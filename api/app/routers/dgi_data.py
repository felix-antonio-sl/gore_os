from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.schemas.dgi import IndicatorItem, DataSourceItem

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
