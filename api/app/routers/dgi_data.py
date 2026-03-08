from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
import math
from datetime import datetime, timedelta, timezone
from app.schemas.dgi import (
    IndicatorItem, DataSourceItem,
    OrganizacionItem, PersonaItem, TerritorioItem, EventoItem,
    RendicionItem, RendicionDetail, RendicionCreate, RendicionUpdate,
    RendicionHistoryEntry, RendicionPhaseEntry,
)
from app.core.security import DGI_ROLES, WRITE_OPERATIONAL_ROLES

_RENDICION_WRITE_ROLES = WRITE_OPERATIONAL_ROLES | DGI_ROLES

router = APIRouter(prefix="/api/dgi/data", tags=["dgi"])


# ---------------------------------------------------------------------------
# Helpers: computar aggregates reales por dimensión
# ---------------------------------------------------------------------------

async def _compute_presupuesto(db: AsyncSession) -> dict:
    """Ejecución presupuestaria: paid/current del año fiscal actual."""
    row = (await db.execute(text("""
        SELECT
            COALESCE(ROUND(SUM(paid_amount)::numeric / NULLIF(SUM(current_amount), 0)::numeric * 100, 1), 0) AS exec_pct,
            COALESCE(SUM(initial_amount), 0) AS total_initial,
            COALESCE(SUM(paid_amount), 0)    AS total_paid
        FROM core.budget_program
        WHERE fiscal_year = EXTRACT(YEAR FROM CURRENT_DATE) AND deleted_at IS NULL
    """))).mappings().first()
    pct = float(row["exec_pct"] or 0)
    signal = "VERDE" if pct >= 70 else ("AMARILLO" if pct >= 40 else "ROJO")
    return {"value": pct, "signal": signal, "unit": "PERCENT"}


async def _compute_cartera_ipr(db: AsyncSession) -> dict:
    """% IPRs con alerta CRITICO activa."""
    row = (await db.execute(text("""
        SELECT
            COUNT(DISTINCT i.id)                                              AS total_ipr,
            COUNT(DISTINCT a.subject_id)
                FILTER (WHERE sev.code = 'CRITICO' AND a.resolved_at IS NULL) AS critical_ipr
        FROM core.ipr i
        LEFT JOIN core.alert a ON a.subject_type = 'core.ipr' AND a.subject_id = i.id AND a.deleted_at IS NULL
        LEFT JOIN ref.category sev ON sev.id = a.severity_id
        WHERE i.deleted_at IS NULL
    """))).mappings().first()
    total = int(row["total_ipr"] or 0)
    critical = int(row["critical_ipr"] or 0)
    pct = round(critical / total * 100, 1) if total > 0 else 0.0
    signal = "VERDE" if pct < 5 else ("AMARILLO" if pct < 15 else "ROJO")
    return {"value": pct, "signal": signal, "unit": "PERCENT", "total": total, "critical": critical}


async def _compute_convenios(db: AsyncSession) -> dict:
    """% convenios vencidos sobre el total activo."""
    row = (await db.execute(text("""
        SELECT
            SUM(CASE WHEN st.code = 'VIGENTE'  THEN 1 ELSE 0 END) AS vigentes,
            SUM(CASE WHEN st.code = 'VENCIDO'  THEN 1 ELSE 0 END) AS vencidos,
            SUM(CASE WHEN st.code = 'VIGENTE' AND a.valid_to < NOW() + INTERVAL '30 days' THEN 1 ELSE 0 END) AS por_vencer
        FROM core.agreement a
        JOIN ref.category st ON st.id = a.state_id
        WHERE a.deleted_at IS NULL
    """))).mappings().first()
    vigentes = int(row["vigentes"] or 0)
    vencidos = int(row["vencidos"] or 0)
    total = vigentes + vencidos
    pct = round(vencidos / total * 100, 1) if total > 0 else 0.0
    signal = "VERDE" if pct < 5 else ("AMARILLO" if pct < 20 else "ROJO")
    return {"value": pct, "signal": signal, "unit": "PERCENT", "vigentes": vigentes, "vencidos": vencidos}


async def _compute_riesgos(db: AsyncSession) -> dict:
    """Alertas no resueltas + problemas abiertos."""
    row = (await db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM core.alert WHERE resolved_at IS NULL AND deleted_at IS NULL)        AS alertas,
            (SELECT COUNT(*) FROM core.ipr_problem ip
             JOIN ref.category ps ON ps.id = ip.state_id
             WHERE ps.code IN ('ABIERTO', 'EN_GESTION') AND ip.deleted_at IS NULL)                   AS problemas
    """))).mappings().first()
    alertas = int(row["alertas"] or 0)
    problemas = int(row["problemas"] or 0)
    total = alertas + problemas
    signal = "VERDE" if total < 5 else ("AMARILLO" if total < 15 else "ROJO")
    return {"value": float(total), "signal": signal, "unit": "COUNT", "alertas": alertas, "problemas": problemas}


async def _update_dimension_indicators(db: AsyncSession, dimension_code: str, new_value: float, signal_code: str) -> int:
    """UPDATE todos los indicadores de una dimensión con el nuevo valor y señal."""
    result = await db.execute(text("""
        UPDATE core.dgi_indicator
        SET
            current_value    = :val,
            signal_id        = (SELECT id FROM ref.category WHERE scheme = 'dgi_signal' AND code = :signal LIMIT 1),
            last_updated_at  = NOW(),
            updated_at       = NOW()
        WHERE dimension_id = (
            SELECT id FROM ref.category WHERE scheme = 'dgi_indicator_dimension' AND code = :dim LIMIT 1
        )
          AND deleted_at IS NULL
        RETURNING id
    """), {"val": new_value, "signal": signal_code, "dim": dimension_code})
    return len(result.fetchall())


# ---------------------------------------------------------------------------
# POST /api/dgi/data/indicators/refresh — Recalcular indicadores desde BD real
# ---------------------------------------------------------------------------

@router.post("/indicators/refresh")
async def refresh_indicators(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Recalcula y persiste los valores reales de los indicadores DGI desde la BD.
    Dimensiones actualizadas: PRESUPUESTO, CARTERA_IPR, CONVENIOS, RIESGOS.
    TDE se mantiene estático (sin fuente de datos real aún).
    Idempotente: ejecutar N veces produce el mismo resultado.
    """
    try:
        # Capture snapshots of current values BEFORE updating
        await db.execute(text("""
            INSERT INTO core.dgi_indicator_snapshot (indicator_id, value, signal_id, recorded_at)
            SELECT i.id, i.current_value, i.signal_id, NOW()
            FROM core.dgi_indicator i
            WHERE i.deleted_at IS NULL AND i.current_value IS NOT NULL
        """))

        results = {}

        # PRESUPUESTO
        ppto = await _compute_presupuesto(db)
        n = await _update_dimension_indicators(db, "PRESUPUESTO", ppto["value"], ppto["signal"])
        results["PRESUPUESTO"] = {**ppto, "updated_rows": n}

        # CARTERA_IPR
        ipr = await _compute_cartera_ipr(db)
        n = await _update_dimension_indicators(db, "CARTERA_IPR", ipr["value"], ipr["signal"])
        results["CARTERA_IPR"] = {**ipr, "updated_rows": n}

        # CONVENIOS
        conv = await _compute_convenios(db)
        n = await _update_dimension_indicators(db, "CONVENIOS", conv["value"], conv["signal"])
        results["CONVENIOS"] = {**conv, "updated_rows": n}

        # RIESGOS
        riesgos = await _compute_riesgos(db)
        n = await _update_dimension_indicators(db, "RIESGOS", riesgos["value"], riesgos["signal"])
        results["RIESGOS"] = {**riesgos, "updated_rows": n}

        # TDE: no update (mantiene valores del seed)
        results["TDE"] = {"note": "Sin fuente de datos real. Valores del seed se mantienen."}

        await db.commit()
        return {"status": "ok", "dimensions": results}
    except Exception:
        await db.rollback()
        raise


# ---------------------------------------------------------------------------
# GET /api/dgi/data/indicators — All indicators (with optional dimension filter)
# ---------------------------------------------------------------------------
@router.get("/indicators", response_model=list[IndicatorItem])
async def list_indicators(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    dimension: str | None = Query(None, description="Filter by dimension code (e.g. PRESUPUESTO, TDE)"),
):
    """
    List all DGI indicators.

    Optional filter:
    - dimension: filter by dgi_indicator_dimension code
    """
    conditions = ["1=1"]
    params: dict = {}

    if dimension:
        conditions.append("dim.code = :dimension")
        params["dimension"] = dimension.upper()

    where_clause = " AND ".join(conditions)

    sql = text(f"""
        SELECT
            i.id,
            i.code,
            i.name,
            dim.code        AS dimension,
            i.current_value,
            i.target_value,
            i.unit,
            sig.code        AS signal,
            i.trend,
            i.description,
            i.last_updated_at
        FROM core.dgi_indicator i
        JOIN ref.category dim ON dim.id = i.dimension_id
        LEFT JOIN ref.category sig ON sig.id = i.signal_id
        WHERE {where_clause}
        ORDER BY
            CASE sig.code
                WHEN 'ROJO'     THEN 1
                WHEN 'AMARILLO' THEN 2
                WHEN 'VERDE'    THEN 3
                ELSE 4
            END,
            dim.code,
            i.name
    """)

    rows = (await db.execute(sql, params)).mappings().all()

    return [
        IndicatorItem(
            id=r["id"],
            code=r["code"],
            name=r["name"],
            dimension=r["dimension"],
            current_value=r["current_value"],
            target_value=r["target_value"],
            unit=r["unit"],
            signal=r["signal"],
            trend=r["trend"],
            description=r["description"],
            last_updated_at=r["last_updated_at"],
        )
        for r in rows
    ]


# ---------------------------------------------------------------------------
# GET /api/dgi/data/indicators/{id} — Single indicator detail
# ---------------------------------------------------------------------------
@router.get("/indicators/{indicator_id}", response_model=IndicatorItem)
async def get_indicator(
    indicator_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a single DGI indicator by UUID.
    """
    sql = text("""
        SELECT
            i.id,
            i.code,
            i.name,
            dim.code        AS dimension,
            i.current_value,
            i.target_value,
            i.unit,
            sig.code        AS signal,
            i.trend,
            i.description,
            i.last_updated_at
        FROM core.dgi_indicator i
        JOIN ref.category dim ON dim.id = i.dimension_id
        LEFT JOIN ref.category sig ON sig.id = i.signal_id
        WHERE i.id = :id
    """)

    row = (await db.execute(sql, {"id": str(indicator_id)})).mappings().first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indicador no encontrado",
        )

    return IndicatorItem(
        id=row["id"],
        code=row["code"],
        name=row["name"],
        dimension=row["dimension"],
        current_value=row["current_value"],
        target_value=row["target_value"],
        unit=row["unit"],
        signal=row["signal"],
        trend=row["trend"],
        description=row["description"],
        last_updated_at=row["last_updated_at"],
    )


# ---------------------------------------------------------------------------
# GET /api/dgi/data/indicators/{id}/history — Snapshot time series
# ---------------------------------------------------------------------------
@router.get("/indicators/{indicator_id}/history")
async def get_indicator_history(
    indicator_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    days: int = Query(90, ge=1, le=365),
):
    """Return snapshot time series for an indicator over the last N days."""
    sql = text("""
        SELECT s.value, sig.code AS signal, s.recorded_at
        FROM core.dgi_indicator_snapshot s
        LEFT JOIN ref.category sig ON sig.id = s.signal_id
        WHERE s.indicator_id = :id
          AND s.recorded_at >= NOW() - MAKE_INTERVAL(days => :days)
        ORDER BY s.recorded_at ASC
    """)
    rows = (await db.execute(sql, {"id": str(indicator_id), "days": days})).mappings().all()
    return [
        {
            "value": float(r["value"]) if r["value"] is not None else None,
            "signal": r["signal"],
            "recorded_at": r["recorded_at"].isoformat(),
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# GET /api/dgi/data/sources — Data source status
# ---------------------------------------------------------------------------
@router.get("/sources", response_model=list[DataSourceItem])
async def list_data_sources(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    source_status: str | None = Query(None, alias="status", description="Filter by status code"),
):
    """
    List all DGI data source statuses.

    Optional filter:
    - status: filter by dgi_source_status code (e.g. ACTUALIZADO, ATRASADO, SIN_DATOS)
    """
    conditions = ["1=1"]
    params: dict = {}

    if source_status:
        conditions.append("st.code = :source_status")
        params["source_status"] = source_status.upper()

    where_clause = " AND ".join(conditions)

    sql = text(f"""
        SELECT
            ds.id,
            org.name        AS division_name,
            ds.source_name,
            st.code         AS status,
            ds.last_data_at,
            ds.days_behind
        FROM core.dgi_data_source_status ds
        LEFT JOIN core.organization org ON org.id = ds.division_id
        JOIN ref.category st ON st.id = ds.status_id
        WHERE {where_clause}
        ORDER BY
            CASE st.code
                WHEN 'SIN_DATOS'   THEN 1
                WHEN 'ATRASADO'    THEN 2
                WHEN 'ACTUALIZADO' THEN 3
                ELSE 4
            END,
            ds.days_behind DESC,
            org.name NULLS LAST
    """)

    rows = (await db.execute(sql, params)).mappings().all()

    return [
        DataSourceItem(
            id=r["id"],
            division_name=r["division_name"],
            source_name=r["source_name"],
            status=r["status"],
            last_data_at=r["last_data_at"],
            days_behind=r["days_behind"] or 0,
        )
        for r in rows
    ]


# ---------------------------------------------------------------------------
# GET /api/dgi/data/organizaciones
# ---------------------------------------------------------------------------

@router.get("/organizaciones")
async def list_organizaciones(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    org_type: str | None = None,
    search: str | None = None,
):
    conditions = ["o.deleted_at IS NULL"]
    params: dict = {}

    if org_type:
        conditions.append("ot.code = :org_type")
        params["org_type"] = org_type

    if search:
        conditions.append("(o.name ILIKE :search OR o.code ILIKE :search)")
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core.organization o
        LEFT JOIN ref.category ot ON ot.id = o.org_type_id
        LEFT JOIN core.organization parent ON parent.id = o.parent_id
        WHERE {where_clause}
    """

    total = (await db.execute(text(f"SELECT COUNT(*) {base_query}"), params)).scalar() or 0
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(text(f"""
        SELECT o.id, o.code, o.name, o.short_name, o.rut,
               ot.label AS org_type, parent.name AS parent_name,
               (SELECT COUNT(*) FROM core."user" u
                WHERE u.division_id = o.id AND u.deleted_at IS NULL) AS user_count
        {base_query}
        ORDER BY o.name
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    items = [OrganizacionItem(
        id=r["id"], code=r["code"], name=r["name"],
        short_name=r["short_name"], org_type=r["org_type"],
        parent_name=r["parent_name"], rut=r["rut"],
        user_count=r["user_count"] or 0,
    ) for r in rows]

    return {
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


# ---------------------------------------------------------------------------
# GET /api/dgi/data/personas
# ---------------------------------------------------------------------------

@router.get("/personas")
async def list_personas(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    organization_id: str | None = None,
    search: str | None = None,
):
    conditions = ["p.deleted_at IS NULL"]
    params: dict = {}

    if organization_id:
        conditions.append("p.organization_id = :organization_id")
        params["organization_id"] = organization_id

    if search:
        conditions.append(
            "(p.names ILIKE :search OR p.paternal_surname ILIKE :search OR p.email ILIKE :search)"
        )
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core.person p
        LEFT JOIN core.organization org ON org.id = p.organization_id
        LEFT JOIN ref.category est ON est.id = p.estamento_id
        LEFT JOIN core."position" pos ON pos.id = p.position_id
        WHERE {where_clause}
    """

    total = (await db.execute(text(f"SELECT COUNT(*) {base_query}"), params)).scalar() or 0
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(text(f"""
        SELECT p.id, p.names, p.paternal_surname, p.maternal_surname,
               p.email, p.phone, p.is_active,
               org.name AS organization_name,
               est.label AS estamento, pos.name AS position_name
        {base_query}
        ORDER BY p.paternal_surname, p.names
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    items = [PersonaItem(
        id=r["id"], names=r["names"], paternal_surname=r["paternal_surname"],
        maternal_surname=r["maternal_surname"], email=r["email"], phone=r["phone"],
        is_active=r["is_active"] if r["is_active"] is not None else True,
        organization_name=r["organization_name"],
        estamento=r["estamento"], position_name=r["position_name"],
    ) for r in rows]

    return {
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


# ---------------------------------------------------------------------------
# GET /api/dgi/data/territorio
# ---------------------------------------------------------------------------

@router.get("/territorio")
async def list_territorio(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    territory_type: str | None = None,
    search: str | None = None,
):
    conditions = ["t.deleted_at IS NULL"]
    params: dict = {}

    if territory_type:
        conditions.append("tt.code = :territory_type")
        params["territory_type"] = territory_type

    if search:
        conditions.append("(t.name ILIKE :search OR t.code ILIKE :search)")
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core.territory t
        JOIN ref.category tt ON tt.id = t.territory_type_id
        LEFT JOIN core.territory parent ON parent.id = t.parent_id
        WHERE {where_clause}
    """

    total = (await db.execute(text(f"SELECT COUNT(*) {base_query}"), params)).scalar() or 0
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(text(f"""
        SELECT t.id, t.code, t.name, t.population, t.area_km2,
               tt.label AS territory_type, parent.name AS parent_name
        {base_query}
        ORDER BY t.code
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    items = [TerritorioItem(
        id=r["id"], code=r["code"], name=r["name"],
        territory_type=r["territory_type"], parent_name=r["parent_name"],
        population=r["population"], area_km2=float(r["area_km2"]) if r["area_km2"] else None,
    ) for r in rows]

    return {
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


# ---------------------------------------------------------------------------
# GET /api/dgi/data/eventos  (partitioned table — REQUIRES date range)
# ---------------------------------------------------------------------------

@router.get("/eventos")
async def list_eventos(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    subject_type: str | None = None,
    event_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    search: str | None = None,
):
    # Default date range: last 30 days (required for partition pruning)
    now = datetime.now(timezone.utc)
    df = datetime.fromisoformat(date_from) if date_from else (now - timedelta(days=30))
    dt = datetime.fromisoformat(date_to) if date_to else now

    conditions = ["e.occurred_at >= :date_from", "e.occurred_at < :date_to"]
    params: dict = {"date_from": df, "date_to": dt}

    if subject_type:
        conditions.append("e.subject_type = :subject_type")
        params["subject_type"] = subject_type

    if event_type:
        conditions.append("et.code = :event_type")
        params["event_type"] = event_type

    if search:
        conditions.append("e.subject_type ILIKE :search")
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM txn.event e
        JOIN ref.category et ON et.id = e.event_type_id
        LEFT JOIN core."user" u ON u.id = e.actor_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE {where_clause}
    """

    total = (await db.execute(text(f"SELECT COUNT(*) {base_query}"), params)).scalar() or 0
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(text(f"""
        SELECT e.id, e.occurred_at, et.code AS event_type, et.label AS event_type_label,
               e.subject_type, e.subject_id,
               (p.names || ' ' || p.paternal_surname) AS actor_name,
               e.data->>'summary' AS summary
        {base_query}
        ORDER BY e.occurred_at DESC
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    items = [EventoItem(
        id=r["id"], occurred_at=r["occurred_at"],
        event_type=r["event_type"], event_type_label=r["event_type_label"],
        subject_type=r["subject_type"], subject_id=r["subject_id"],
        actor_name=r["actor_name"], summary=r["summary"],
    ) for r in rows]

    return {
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


# ---------------------------------------------------------------------------
# GET /api/dgi/data/rendiciones
# ---------------------------------------------------------------------------

@router.get("/rendiciones")
async def list_rendiciones(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    state: str | None = None,
    search: str | None = None,
):
    conditions = ["r.deleted_at IS NULL"]
    params: dict = {}

    if state:
        conditions.append("st.code = :state")
        params["state"] = state

    if search:
        conditions.append(
            "(a.agreement_number ILIKE :search OR org.name ILIKE :search OR ipr.codigo_bip ILIKE :search)"
        )
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core.rendition r
        LEFT JOIN core.agreement a ON a.id = r.agreement_id
        LEFT JOIN core.ipr ipr ON ipr.id = r.ipr_id
        LEFT JOIN core.organization org ON org.id = r.renderer_id
        LEFT JOIN ref.category st ON st.id = r.state_id
        WHERE {where_clause}
    """

    total = (await db.execute(text(f"SELECT COUNT(*) {base_query}"), params)).scalar() or 0
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(text(f"""
        SELECT r.id, r.period_start, r.period_end, r.submitted_at, r.amount,
               a.agreement_number, a.total_amount AS agreement_total_amount,
               ipr.codigo_bip AS ipr_codigo_bip, r.ipr_id,
               org.name AS renderer_name, st.code AS state_code, st.label AS state_label,
               EXTRACT(EPOCH FROM (NOW() - r.updated_at)) / 86400.0 AS days_in_state
        {base_query}
        ORDER BY r.submitted_at DESC NULLS LAST
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    items = [RendicionItem(
        id=r["id"], agreement_number=r["agreement_number"],
        ipr_codigo_bip=r["ipr_codigo_bip"], ipr_id=r["ipr_id"],
        renderer_name=r["renderer_name"], state_code=r["state_code"], state_label=r["state_label"],
        period_start=r["period_start"], period_end=r["period_end"],
        submitted_at=r["submitted_at"],
        agreement_total_amount=float(r["agreement_total_amount"]) if r["agreement_total_amount"] else None,
        amount=float(r["amount"]) if r["amount"] else None,
        days_in_state=round(float(r["days_in_state"]), 1) if r["days_in_state"] else None,
        is_overdue=(
            r["state_code"] in _RENDICION_SLA_DAYS
            and r["days_in_state"] is not None
            and float(r["days_in_state"]) > _RENDICION_SLA_DAYS[r["state_code"]]
        ),
    ) for r in rows]

    return {
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


# ---------------------------------------------------------------------------
# GET /api/dgi/data/rendiciones/vencidas — Overdue renditions (SLA breach)
# ---------------------------------------------------------------------------

@router.get("/rendiciones/vencidas")
async def list_rendiciones_vencidas(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    """Rendiciones that have exceeded their SLA time in a reviewable state."""
    # Build CASE expression for SLA thresholds
    sla_conditions = " OR ".join(
        f"(st.code = '{code}' AND EXTRACT(EPOCH FROM (NOW() - r.updated_at)) / 86400.0 > {days})"
        for code, days in _RENDICION_SLA_DAYS.items()
    )

    base_query = f"""
        FROM core.rendition r
        LEFT JOIN core.agreement a ON a.id = r.agreement_id
        LEFT JOIN core.ipr ipr ON ipr.id = r.ipr_id
        LEFT JOIN core.organization org ON org.id = r.renderer_id
        LEFT JOIN ref.category st ON st.id = r.state_id
        WHERE r.deleted_at IS NULL AND ({sla_conditions})
    """

    params: dict = {}
    total = (await db.execute(text(f"SELECT COUNT(*) {base_query}"), params)).scalar() or 0
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(text(f"""
        SELECT r.id, r.period_start, r.period_end, r.submitted_at, r.amount,
               a.agreement_number, a.total_amount AS agreement_total_amount,
               ipr.codigo_bip AS ipr_codigo_bip, r.ipr_id,
               org.name AS renderer_name, st.code AS state_code, st.label AS state_label,
               EXTRACT(EPOCH FROM (NOW() - r.updated_at)) / 86400.0 AS days_in_state
        {base_query}
        ORDER BY days_in_state DESC
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    items = [RendicionItem(
        id=r["id"], agreement_number=r["agreement_number"],
        ipr_codigo_bip=r["ipr_codigo_bip"], ipr_id=r["ipr_id"],
        renderer_name=r["renderer_name"], state_code=r["state_code"], state_label=r["state_label"],
        period_start=r["period_start"], period_end=r["period_end"],
        submitted_at=r["submitted_at"],
        agreement_total_amount=float(r["agreement_total_amount"]) if r["agreement_total_amount"] else None,
        amount=float(r["amount"]) if r["amount"] else None,
        days_in_state=round(float(r["days_in_state"]), 1) if r["days_in_state"] else None,
        is_overdue=True,
    ) for r in rows]

    return {
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


# ---------------------------------------------------------------------------
# GET /api/dgi/data/rendiciones/{rendicion_id}/ciclo — Phase timeline
# ---------------------------------------------------------------------------

@router.get("/rendiciones/{rendicion_id}/ciclo")
async def get_rendicion_ciclo(
    rendicion_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db),
):
    """Phase-by-phase cycle view of a rendition's lifecycle with SLA tracking."""
    row = (await db.execute(
        text("""
            SELECT r.id, r.created_at, st.code AS state_code
            FROM core.rendition r
            LEFT JOIN ref.category st ON st.id = r.state_id
            WHERE r.id = :id AND r.deleted_at IS NULL
        """),
        {"id": str(rendicion_id)},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Rendición no encontrada")

    history_rows = (await db.execute(
        text("""
            SELECT h.changed_at,
                   new_cat.code  AS new_state,
                   new_cat.label AS new_state_label
            FROM core.rendition_history h
            JOIN ref.category new_cat ON h.new_state_id = new_cat.id
            WHERE h.rendition_id = :rid
            ORDER BY h.changed_at ASC
        """),
        {"rid": str(rendicion_id)},
    )).mappings().all()

    now = datetime.now(timezone.utc)
    phases: list[dict] = []

    if history_rows:
        # Phase 0: PENDIENTE from creation to first transition
        first_ts = history_rows[0]["changed_at"]
        d0 = (first_ts - row["created_at"]).total_seconds() / 86400.0
        sla0 = _RENDICION_SLA_DAYS.get("PENDIENTE")
        phases.append({
            "phase_code": "PENDIENTE",
            "phase_label": "Pendiente",
            "entered_at": row["created_at"],
            "exited_at": first_ts,
            "duration_days": round(d0, 1),
            "sla_days": sla0,
            "is_overdue": sla0 is not None and d0 > sla0,
        })

        for i, h in enumerate(history_rows):
            entered = h["changed_at"]
            if i + 1 < len(history_rows):
                exited = history_rows[i + 1]["changed_at"]
                dur = (exited - entered).total_seconds() / 86400.0
            else:
                exited = None
                dur = (now - entered).total_seconds() / 86400.0
            sla = _RENDICION_SLA_DAYS.get(h["new_state"])
            phases.append({
                "phase_code": h["new_state"],
                "phase_label": h["new_state_label"],
                "entered_at": entered,
                "exited_at": exited,
                "duration_days": round(dur, 1),
                "sla_days": sla,
                "is_overdue": sla is not None and dur > sla,
            })
    else:
        # No transitions yet — still in PENDIENTE
        dur = (now - row["created_at"]).total_seconds() / 86400.0
        sla0 = _RENDICION_SLA_DAYS.get("PENDIENTE")
        phases.append({
            "phase_code": "PENDIENTE",
            "phase_label": "Pendiente",
            "entered_at": row["created_at"],
            "exited_at": None,
            "duration_days": round(dur, 1),
            "sla_days": sla0,
            "is_overdue": sla0 is not None and dur > sla0,
        })

    total_elapsed = (now - row["created_at"]).total_seconds() / 86400.0
    overdue_count = sum(1 for p in phases if p["is_overdue"])

    return {
        "rendicion_id": rendicion_id,
        "current_state": row["state_code"],
        "total_elapsed_days": round(total_elapsed, 1),
        "phases": phases,
        "overdue_count": overdue_count,
    }


# ---------------------------------------------------------------------------
# GET /api/dgi/data/rendiciones/{rendicion_id} — Detail
# ---------------------------------------------------------------------------

@router.get("/rendiciones/{rendicion_id}", response_model=RendicionDetail)
async def get_rendicion(rendicion_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    row = (await db.execute(
        text("""
            SELECT r.id, r.agreement_id, r.ipr_id, r.renderer_id,
                   r.period_start, r.period_end, r.submitted_at, r.amount,
                   r.metadata, r.created_at,
                   a.agreement_number, a.total_amount AS agreement_total_amount,
                   ipr.codigo_bip AS ipr_codigo_bip,
                   org.name AS renderer_name,
                   st.code AS state_code, st.label AS state_label,
                   EXTRACT(EPOCH FROM (NOW() - r.updated_at)) / 86400.0 AS days_in_state
            FROM core.rendition r
            LEFT JOIN core.agreement a ON a.id = r.agreement_id
            LEFT JOIN core.ipr ipr ON ipr.id = r.ipr_id
            LEFT JOIN core.organization org ON org.id = r.renderer_id
            LEFT JOIN ref.category st ON st.id = r.state_id
            WHERE r.id = :id AND r.deleted_at IS NULL
        """),
        {"id": str(rendicion_id)},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Rendición no encontrada")
    history = await _get_rendition_history(rendicion_id, db)
    return RendicionDetail(
        id=row["id"], agreement_id=row["agreement_id"], ipr_id=row["ipr_id"],
        renderer_id=row["renderer_id"], agreement_number=row["agreement_number"],
        ipr_codigo_bip=row["ipr_codigo_bip"], renderer_name=row["renderer_name"],
        state_code=row["state_code"], state_label=row["state_label"],
        period_start=row["period_start"], period_end=row["period_end"],
        submitted_at=row["submitted_at"],
        agreement_total_amount=float(row["agreement_total_amount"]) if row["agreement_total_amount"] else None,
        amount=float(row["amount"]) if row["amount"] else None,
        days_in_state=round(float(row["days_in_state"]), 1) if row["days_in_state"] else None,
        is_overdue=(
            row["state_code"] in _RENDICION_SLA_DAYS
            and row["days_in_state"] is not None
            and float(row["days_in_state"]) > _RENDICION_SLA_DAYS[row["state_code"]]
        ),
        sla_days=_RENDICION_SLA_DAYS.get(row["state_code"]),
        metadata=dict(row["metadata"]) if row["metadata"] else None,
        created_at=row["created_at"],
        history=[RendicionHistoryEntry(**h) for h in history],
    )


# ---------------------------------------------------------------------------
# POST /api/dgi/data/rendiciones — Create rendicion (SISREC MVP)
# ---------------------------------------------------------------------------

@router.post("/rendiciones", status_code=status.HTTP_201_CREATED)
async def create_rendicion(body: RendicionCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if user["role_code"] not in _RENDICION_WRITE_ROLES:
        raise HTTPException(status_code=403, detail="Rol sin permiso para crear rendiciones")
    if not body.agreement_id and not body.ipr_id:
        raise HTTPException(status_code=422, detail="Se requiere agreement_id o ipr_id (al menos uno)")

    pendiente_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'PENDIENTE'"),
    )).scalar()

    row = (await db.execute(
        text("""
            INSERT INTO core.rendition (
                agreement_id, ipr_id, renderer_id, state_id,
                period_start, period_end, submitted_at, amount,
                created_by_id, created_at, updated_at
            ) VALUES (
                :agreement_id, :ipr_id, :renderer_id, :state_id,
                :period_start, :period_end, COALESCE(:submitted_at, NOW()), :amount,
                :created_by_id, NOW(), NOW()
            ) RETURNING id
        """),
        {
            "agreement_id": str(body.agreement_id) if body.agreement_id else None,
            "ipr_id": str(body.ipr_id) if body.ipr_id else None,
            "renderer_id": str(body.renderer_id) if body.renderer_id else None,
            "state_id": str(pendiente_id),
            "period_start": body.period_start,
            "period_end": body.period_end,
            "submitted_at": body.submitted_at,
            "amount": body.amount,
            "created_by_id": str(user["id"]),
        },
    )).mappings().first()
    await db.commit()
    return {"id": str(row["id"])}


# ---------------------------------------------------------------------------
# PATCH /api/dgi/data/rendiciones/{rendicion_id}
# ---------------------------------------------------------------------------

# Rendition state machine (code → allowed target codes)
_RENDICION_TRANSITIONS = {
    "PENDIENTE":       {"EN_REVISION_RTF"},
    "EN_REVISION_RTF": {"OBSERVADA", "VISADA_RTF"},
    "VISADA_RTF":      {"EN_REVISION_UCR"},
    "EN_REVISION_UCR": {"OBSERVADA", "APROBADA", "RECHAZADA"},
    "OBSERVADA":       {"EN_REVISION_RTF"},
    # APROBADA and RECHAZADA are terminal — no transitions
}

# Role-based transition authorization: (from, to) → allowed role set
_RENDICION_TRANSITION_ROLES: dict[tuple[str, str], set[str]] = {
    ("PENDIENTE", "EN_REVISION_RTF"):       _RENDICION_WRITE_ROLES,
    ("EN_REVISION_RTF", "OBSERVADA"):       DGI_ROLES,
    ("EN_REVISION_RTF", "VISADA_RTF"):      DGI_ROLES,
    ("VISADA_RTF", "EN_REVISION_UCR"):      DGI_ROLES,
    ("EN_REVISION_UCR", "OBSERVADA"):       DGI_ROLES,
    ("EN_REVISION_UCR", "APROBADA"):        DGI_ROLES,
    ("EN_REVISION_UCR", "RECHAZADA"):       DGI_ROLES,
    ("OBSERVADA", "EN_REVISION_RTF"):       _RENDICION_WRITE_ROLES,
}

# SLA days per reviewable state (CGR normative)
_RENDICION_SLA_DAYS: dict[str, int] = {
    "EN_REVISION_RTF": 7,
    "VISADA_RTF": 1,
    "EN_REVISION_UCR": 2,
    "OBSERVADA": 15,
}

RENDICION_UPDATABLE = {"state_id", "period_start", "period_end", "submitted_at", "amount"}


async def _get_rendition_history(rendition_id: UUID, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        text("""
            SELECT h.id, h.changed_at, h.comment,
                   prev_cat.code AS previous_state,
                   new_cat.code  AS new_state,
                   (p.names || ' ' || p.paternal_surname) AS changed_by_name
            FROM core.rendition_history h
            JOIN ref.category new_cat ON h.new_state_id = new_cat.id
            LEFT JOIN ref.category prev_cat ON h.previous_state_id = prev_cat.id
            LEFT JOIN core."user" cu ON h.changed_by_id = cu.id
            LEFT JOIN core.person p ON cu.person_id = p.id
            WHERE h.rendition_id = :rendition_id
            ORDER BY h.changed_at DESC
        """),
        {"rendition_id": str(rendition_id)},
    )
    return [dict(r) for r in result.mappings().all()]


@router.patch("/rendiciones/{rendicion_id}")
async def patch_rendicion(
    rendicion_id: UUID,
    body: RendicionUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a rendición. Multi-role state machine:
    PENDIENTE → EN_REVISION_RTF → VISADA_RTF → EN_REVISION_UCR → APROBADA/RECHAZADA.
    OBSERVADA loops back to EN_REVISION_RTF.
    Role authorization checked per-transition.
    """
    # Verify rendicion exists
    row = (await db.execute(
        text("SELECT id, state_id FROM core.rendition WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(rendicion_id)},
    )).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Rendición no encontrada")

    # Build update fields from non-None values, excluding comment (handled separately)
    updates = body.model_dump(exclude_none=True)
    comment = updates.pop("comment", None)

    if not updates:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    # Validate all fields are in allowlist
    invalid = set(updates.keys()) - RENDICION_UPDATABLE
    if invalid:
        raise HTTPException(status_code=400, detail=f"Campos no permitidos: {invalid}")

    # Validate state transition if state_id is changing
    if "state_id" in updates:
        # Get current state code
        current_state = (await db.execute(
            text("SELECT code FROM ref.category WHERE id = :id"),
            {"id": str(row["state_id"])},
        )).scalar()

        # Get target state code
        new_state = (await db.execute(
            text("SELECT code FROM ref.category WHERE id = :id"),
            {"id": str(updates["state_id"])},
        )).scalar()

        if not new_state:
            raise HTTPException(status_code=400, detail="state_id inválido")

        allowed = _RENDICION_TRANSITIONS.get(current_state, set())
        if new_state not in allowed:
            raise HTTPException(
                status_code=409,
                detail=f"Transición inválida: {current_state} → {new_state}. "
                       f"Permitidas: {sorted(allowed) if allowed else 'ninguna (estado terminal)'}",
            )

        # Role-based authorization for this specific transition
        allowed_roles = _RENDICION_TRANSITION_ROLES.get((current_state, new_state))
        if allowed_roles and user["role_code"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol {user['role_code']} no puede ejecutar {current_state} → {new_state}",
            )
    else:
        # Non-transition updates: require write roles
        if user["role_code"] not in _RENDICION_WRITE_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rol sin permiso para modificar rendiciones",
            )

    # Build SET clause
    set_parts = []
    params: dict = {"id": str(rendicion_id), "user_id": user["id"]}

    for col, val in updates.items():
        param_name = f"v_{col}"
        set_parts.append(f"{col} = :{param_name}")
        params[param_name] = str(val) if isinstance(val, UUID) else val

    set_parts.append("updated_at = NOW()")
    set_parts.append("updated_by_id = :user_id")

    sql = text(f"""
        UPDATE core.rendition
        SET {', '.join(set_parts)}
        WHERE id = :id AND deleted_at IS NULL
    """)

    await db.execute(sql, params)

    # If state changed and comment provided, update the most recent history row
    if "state_id" in updates and comment:
        await db.execute(
            text("""
                UPDATE core.rendition_history
                SET comment = :comment
                WHERE id = (
                    SELECT id FROM core.rendition_history
                    WHERE rendition_id = :rendition_id
                    ORDER BY changed_at DESC LIMIT 1
                )
            """),
            {"comment": comment, "rendition_id": str(rendicion_id)},
        )

    await db.commit()

    return {"message": "Rendición actualizada"}
