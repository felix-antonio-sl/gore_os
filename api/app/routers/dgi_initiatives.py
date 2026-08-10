import json
import math
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import DGI_ROLES
from app.core.audit import record_event
from app.schemas.dgi import InitiativeItem, InitiativeCreate, InitiativeUpdate, InitiativeMove, InitiativeReorder, DMAICDetail, DMAICGateResult, DMAICPhaseUpdate, DMAICTransition, LeanMetrics


def _require_dgi(user: dict):
    if user.get("role_code") not in DGI_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo roles DGI pueden gestionar iniciativas")

router = APIRouter(prefix="/api/dgi/initiatives", tags=["dgi"])


# ---------------------------------------------------------------------------
# Helper: fetch a single initiative row by id
# ---------------------------------------------------------------------------
async def _get_initiative_row(initiative_id: str, db: AsyncSession) -> dict | None:
    sql = text("""
        SELECT
            ini.id,
            ini.code,
            ini.name,
            ini.description,
            ini.responsible_id,
            p.names || ' ' || p.paternal_surname AS responsible_name,
            st.code         AS status,
            ph.code         AS dmaic_phase,
            org.name        AS division_name,
            ini.start_date,
            ini.target_date,
            ini.current_day,
            ini.total_days,
            ini.progress,
            ini.wip_column,
            ini.sort_order,
            ini.started_at,
            ini.completed_at
        FROM core.dgi_initiative ini
        JOIN ref.category st ON st.id = ini.status_id
        LEFT JOIN ref.category ph ON ph.id = ini.dmaic_phase_id
        LEFT JOIN core.organization org ON org.id = ini.division_id
        LEFT JOIN core."user" u ON u.id = ini.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE ini.id = :id AND ini.deleted_at IS NULL
    """)
    row = (await db.execute(sql, {"id": initiative_id})).mappings().first()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# GET /api/dgi/initiatives — List all initiatives
# ---------------------------------------------------------------------------
@router.get("")
async def list_initiatives(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
    responsible_id: UUID | None = None,
    page: int | None = Query(None, ge=1, description="Page number (omit for unpaginated array)"),
    page_size: int | None = Query(None, ge=1, le=100, description="Items per page"),
):
    """
    List DGI initiatives.

    Optional filters:
    - status: filter by initiative status code (BACKLOG, EN_CURSO, REVISION, COMPLETADO)
    - responsible_id: filter by responsible user UUID

    Pagination: pass page + page_size for paginated response.
    Omit both for backward-compatible plain array.
    """
    conditions = ["ini.deleted_at IS NULL"]
    params: dict = {}

    if status_filter:
        conditions.append("st.code = :status_filter")
        params["status_filter"] = status_filter

    if responsible_id:
        conditions.append("ini.responsible_id = :responsible_id")
        params["responsible_id"] = str(responsible_id)

    where_clause = " AND ".join(conditions)

    base_from = f"""
        FROM core.dgi_initiative ini
        JOIN ref.category st ON st.id = ini.status_id
        LEFT JOIN ref.category ph ON ph.id = ini.dmaic_phase_id
        LEFT JOIN core.organization org ON org.id = ini.division_id
        LEFT JOIN core."user" u ON u.id = ini.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE {where_clause}
    """

    order_by = """
        ORDER BY
            CASE st.code
                WHEN 'EN_CURSO'   THEN 1
                WHEN 'REVISION'   THEN 2
                WHEN 'BACKLOG'    THEN 3
                WHEN 'COMPLETADO' THEN 4
                ELSE 5
            END,
            ini.sort_order ASC,
            ini.target_date ASC NULLS LAST,
            ini.name
    """

    select_cols = """
            ini.id,
            ini.code,
            ini.name,
            ini.description,
            ini.responsible_id,
            p.names || ' ' || p.paternal_surname AS responsible_name,
            st.code         AS status,
            ph.code         AS dmaic_phase,
            org.name        AS division_name,
            ini.start_date,
            ini.target_date,
            ini.current_day,
            ini.total_days,
            ini.progress,
            ini.wip_column,
            ini.sort_order
    """

    def _to_item(r: dict) -> InitiativeItem:
        return InitiativeItem(
            id=r["id"], code=r["code"], name=r["name"], description=r["description"],
            responsible_id=r["responsible_id"], responsible_name=r["responsible_name"],
            status=r["status"], dmaic_phase=r["dmaic_phase"],
            division_name=r["division_name"], start_date=r["start_date"], target_date=r["target_date"],
            current_day=r["current_day"] or 0, total_days=r["total_days"],
            progress=r["progress"] or 0.0, wip_column=r["wip_column"],
            sort_order=r.get("sort_order", 0),
        )

    # Paginated mode
    if page is not None:
        effective_page_size = page_size or 20
        count_result = await db.execute(text(f"SELECT COUNT(*) {base_from}"), params)
        total = count_result.scalar() or 0
        total_pages = math.ceil(total / effective_page_size) if total > 0 else 0

        offset = (page - 1) * effective_page_size
        params["limit"] = effective_page_size
        params["offset"] = offset

        rows = (await db.execute(
            text(f"SELECT {select_cols} {base_from} {order_by} LIMIT :limit OFFSET :offset"),
            params,
        )).mappings().all()

        items = [_to_item(dict(r)) for r in rows]
        return {
            "items": [i.model_dump() for i in items],
            "total": total,
            "page": page,
            "page_size": effective_page_size,
            "total_pages": total_pages,
        }

    # Unpaginated mode (backward compatible)
    rows = (await db.execute(text(f"SELECT {select_cols} {base_from} {order_by}"), params)).mappings().all()
    return [_to_item(dict(r)) for r in rows]


# ---------------------------------------------------------------------------
# POST /api/dgi/initiatives — Create initiative
# ---------------------------------------------------------------------------
@router.post("", status_code=status.HTTP_201_CREATED, response_model=InitiativeItem)
async def create_initiative(
    body: InitiativeCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    # Resolve status_id (default BACKLOG)
    status_code = body.status.upper() if body.status else "BACKLOG"
    st_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'dgi_initiative_status' AND code = :code"),
        {"code": status_code},
    )).mappings().first()
    if not st_row:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Estado inválido: {status_code}")
    status_id = str(st_row["id"])

    # Resolve dmaic_phase_id (optional)
    dmaic_phase_id = None
    if body.dmaic_phase:
        ph_row = (await db.execute(
            text("SELECT id FROM ref.category WHERE scheme = 'dgi_dmaic_phase' AND code = :code"),
            {"code": body.dmaic_phase.upper()},
        )).mappings().first()
        if ph_row:
            dmaic_phase_id = str(ph_row["id"])

    # Auto-generate code (advisory lock + MAX pattern)
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('initiative_code'))"))
    max_seq = (await db.execute(text(
        "SELECT COALESCE(MAX(CAST(SUBSTRING(code FROM 5) AS INTEGER)), 0) FROM core.dgi_initiative WHERE code ~ '^INI-[0-9]+$'"
    ))).scalar() or 0
    code = f"INI-{max_seq + 1:04d}"

    result = await db.execute(
        text("""
            INSERT INTO core.dgi_initiative (code, name, description, responsible_id, status_id, dmaic_phase_id, target_date, total_days, wip_column, created_by_id)
            VALUES (:code, :name, :description, :responsible_id, :status_id, :dmaic_phase_id, :target_date, :total_days, :wip_column, :created_by_id)
            RETURNING id
        """),
        {
            "code": code,
            "name": body.name,
            "description": body.description,
            "responsible_id": str(user["id"]),
            "status_id": status_id,
            "dmaic_phase_id": dmaic_phase_id,
            "target_date": body.target_date,
            "total_days": body.total_days,
            "wip_column": status_code,
            "created_by_id": str(user["id"]),
        },
    )
    new_id = str(result.scalar())
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        error_msg = str(e.orig) if e.orig else str(e)
        if "Transición de estado inválida" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=409, detail="Conflicto de integridad")

    row = await _get_initiative_row(new_id, db)
    return InitiativeItem(
        id=row["id"], code=row["code"], name=row["name"], description=row["description"],
        responsible_id=row["responsible_id"], responsible_name=row["responsible_name"],
        status=row["status"], dmaic_phase=row["dmaic_phase"],
        division_name=row["division_name"], start_date=row["start_date"], target_date=row["target_date"],
        current_day=row["current_day"] or 0, total_days=row["total_days"],
        progress=row["progress"] or 0.0, wip_column=row["wip_column"],
        sort_order=row.get("sort_order", 0),
    )


# ---------------------------------------------------------------------------
# PATCH /api/dgi/initiatives/{id} — Update initiative
# ---------------------------------------------------------------------------
@router.patch("/{initiative_id}", response_model=InitiativeItem)
async def update_initiative(
    initiative_id: UUID,
    body: InitiativeUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    initiative_id_str = str(initiative_id)
    existing = await _get_initiative_row(initiative_id_str, db)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Iniciativa no encontrada")

    UPDATABLE = {"name", "description", "target_date", "total_days", "responsible_id", "division_id"}
    updates = {k: v for k, v in body.model_dump(exclude_none=True).items() if k in UPDATABLE}

    # Handle dmaic_phase → resolve to FK
    if body.dmaic_phase is not None:
        ph_row = (await db.execute(
            text("SELECT id FROM ref.category WHERE scheme = 'dgi_dmaic_phase' AND code = :code"),
            {"code": body.dmaic_phase.upper()},
        )).mappings().first()
        if ph_row:
            updates["dmaic_phase_id"] = str(ph_row["id"])

    if not updates:
        return InitiativeItem(
            id=existing["id"], code=existing["code"], name=existing["name"], description=existing["description"],
            responsible_id=existing["responsible_id"], responsible_name=existing["responsible_name"],
            status=existing["status"], dmaic_phase=existing["dmaic_phase"],
            division_name=existing["division_name"], start_date=existing["start_date"], target_date=existing["target_date"],
            current_day=existing["current_day"] or 0, total_days=existing["total_days"],
            progress=existing["progress"] or 0.0, wip_column=existing["wip_column"],
        sort_order=existing.get("sort_order", 0),
        )

    # Convert UUID fields to str for SQL
    for k in ("responsible_id", "division_id", "dmaic_phase_id"):
        if k in updates and updates[k] is not None:
            updates[k] = str(updates[k])

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = initiative_id_str
    updates["updated_by_id"] = str(user["id"])

    await db.execute(
        text(f"UPDATE core.dgi_initiative SET {set_clauses}, updated_at = NOW(), updated_by_id = :updated_by_id WHERE id = :id"),
        updates,
    )
    await db.commit()

    row = await _get_initiative_row(initiative_id_str, db)
    return InitiativeItem(
        id=row["id"], code=row["code"], name=row["name"], description=row["description"],
        responsible_id=row["responsible_id"], responsible_name=row["responsible_name"],
        status=row["status"], dmaic_phase=row["dmaic_phase"],
        division_name=row["division_name"], start_date=row["start_date"], target_date=row["target_date"],
        current_day=row["current_day"] or 0, total_days=row["total_days"],
        progress=row["progress"] or 0.0, wip_column=row["wip_column"],
        sort_order=row.get("sort_order", 0),
    )


# ---------------------------------------------------------------------------
# POST /api/dgi/initiatives/{id}/move — Move initiative to Kanban column
# ---------------------------------------------------------------------------
@router.post("/{initiative_id}/move", response_model=InitiativeItem)
async def move_initiative(
    initiative_id: UUID,
    body: InitiativeMove,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Move a DGI initiative to a new Kanban column (status).

    Allowed status values: BACKLOG, EN_CURSO, REVISION, COMPLETADO
    """
    initiative_id_str = str(initiative_id)
    target_status = body.status.upper()

    # ── Validate target status exists in scheme ───────────────────────────
    status_check = await db.execute(
        text("""
            SELECT id FROM ref.category
            WHERE scheme = 'dgi_initiative_status' AND code = :code
        """),
        {"code": target_status},
    )
    status_row = status_check.mappings().first()
    if not status_row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido: '{target_status}'. Use BACKLOG, EN_CURSO, REVISION o COMPLETADO.",
        )
    target_status_id = status_row["id"]

    # ── Verify initiative exists ──────────────────────────────────────────
    existing = await _get_initiative_row(initiative_id_str, db)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Iniciativa no encontrada",
        )

    # No-op: already in target column
    if existing["status"] == target_status:
        return InitiativeItem(
            id=existing["id"],
            code=existing["code"],
            name=existing["name"],
            description=existing["description"],
            responsible_id=existing["responsible_id"],
            responsible_name=existing["responsible_name"],
            status=existing["status"],
            dmaic_phase=existing["dmaic_phase"],
            division_name=existing["division_name"],
            start_date=existing["start_date"],
            target_date=existing["target_date"],
            current_day=existing["current_day"] or 0,
            total_days=existing["total_days"],
            progress=existing["progress"] or 0.0,
            wip_column=existing["wip_column"],
        )

    # ── Assign sort_order = max+1 in target column ──────────────────────
    max_order = (await db.execute(
        text("""
            SELECT COALESCE(MAX(sort_order), -1) FROM core.dgi_initiative
            WHERE wip_column = :col AND deleted_at IS NULL
        """),
        {"col": target_status},
    )).scalar()

    # ── Apply move ────────────────────────────────────────────────────────
    await db.execute(
        text("""
            UPDATE core.dgi_initiative
            SET status_id  = :status_id,
                wip_column = :wip_column,
                sort_order = :sort_order
            WHERE id = :id
        """),
        {
            "id": initiative_id_str,
            "status_id": str(target_status_id),
            "wip_column": target_status,
            "sort_order": max_order + 1,
        },
    )
    await record_event(db, "STATE_TRANSITION", "core.dgi_initiative", initiative_id, user["id"], {"from": existing["status"], "to": target_status})
    try:
        await db.commit()
    except (IntegrityError, DBAPIError) as e:
        await db.rollback()
        error_msg = str(e.orig) if e.orig else str(e)
        if "Transición de estado inválida" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=409, detail="Conflicto de integridad")

    # ── Return updated initiative ─────────────────────────────────────────
    updated = await _get_initiative_row(initiative_id_str, db)
    if not updated:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al recuperar iniciativa actualizada")

    return InitiativeItem(
        id=updated["id"],
        code=updated["code"],
        name=updated["name"],
        description=updated["description"],
        responsible_id=updated["responsible_id"],
        responsible_name=updated["responsible_name"],
        status=updated["status"],
        dmaic_phase=updated["dmaic_phase"],
        division_name=updated["division_name"],
        start_date=updated["start_date"],
        target_date=updated["target_date"],
        current_day=updated["current_day"] or 0,
        total_days=updated["total_days"],
        progress=updated["progress"] or 0.0,
        wip_column=updated["wip_column"],
        sort_order=updated.get("sort_order", 0),
    )


# ---------------------------------------------------------------------------
# POST /api/dgi/initiatives/reorder — Reorder initiatives within a column
# ---------------------------------------------------------------------------
@router.post("/reorder")
async def reorder_initiatives(
    body: InitiativeReorder,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Persist new vertical order for initiatives within a single column.
    Receives an ordered list of initiative UUIDs.
    Updates sort_order = 0, 1, 2, ... in the given order.
    """
    _require_dgi(user)

    if not body.initiative_ids:
        return {"updated": 0}

    for idx, ini_id in enumerate(body.initiative_ids):
        await db.execute(
            text("UPDATE core.dgi_initiative SET sort_order = :order WHERE id = :id"),
            {"order": idx, "id": str(ini_id)},
        )

    await db.commit()
    return {"updated": len(body.initiative_ids)}


# ---------------------------------------------------------------------------
# DMAIC gate validation (informational, not blocking)
# ---------------------------------------------------------------------------
_DMAIC_PHASE_ORDER = ["DEFINE", "MEASURE", "ANALYZE", "IMPROVE", "VERIFY"]

_DMAIC_GATE_CRITERIA: dict[str, list[tuple[str, str]]] = {
    "DEFINE": [("problem", "Problema definido"), ("scope", "Alcance definido")],
    "MEASURE": [("baseline_summary", "Línea base documentada")],
    "ANALYZE": [("root_causes", "Causas raíz identificadas")],
    "IMPROVE": [("solution_design", "Diseño de solución"), ("pilot_result", "Resultado del piloto")],
    "VERIFY": [("verification_plan", "Plan de verificación definido")],
}


def _evaluate_dmaic_gates(phases: dict) -> list[DMAICGateResult]:
    results = []
    phase_key_map = {
        "DEFINE": "define",
        "MEASURE": "measure",
        "ANALYZE": "analyze",
        "IMPROVE": "improve",
        "VERIFY": "verify",
    }
    for phase_code, criteria in _DMAIC_GATE_CRITERIA.items():
        phase_data = phases.get(phase_key_map[phase_code], {})
        all_met = True
        missing = []
        for field_key, field_label in criteria:
            if not phase_data.get(field_key, "").strip():
                all_met = False
                missing.append(field_label)

        detail = "Completo" if all_met else f"Pendiente: {', '.join(missing)}"
        results.append(DMAICGateResult(phase=phase_code, met=all_met, detail=detail))
    return results


# ---------------------------------------------------------------------------
# GET /api/dgi/initiatives/lean-metrics — Lean metrics dashboard
# ---------------------------------------------------------------------------
@router.get("/lean-metrics", response_model=LeanMetrics)
async def get_lean_metrics(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Computes Lean/Kanban metrics: throughput, lead time, cycle time, WIP, aging."""
    _require_dgi(user)

    # Throughput: completed initiatives per period
    throughput_sql = text("""
        SELECT
            COUNT(*) FILTER (WHERE completed_at >= NOW() - INTERVAL '30 days') AS t30,
            COUNT(*) FILTER (WHERE completed_at >= NOW() - INTERVAL '60 days') AS t60,
            COUNT(*) FILTER (WHERE completed_at >= NOW() - INTERVAL '90 days') AS t90
        FROM core.dgi_initiative ini
        JOIN ref.category st ON st.id = ini.status_id
        WHERE st.code = 'COMPLETADO'
          AND ini.deleted_at IS NULL
          AND ini.completed_at IS NOT NULL
    """)
    t_row = (await db.execute(throughput_sql)).mappings().first()

    # Lead time: avg days from created_at to completed_at
    lead_time_sql = text("""
        SELECT AVG(EXTRACT(EPOCH FROM (completed_at - created_at)) / 86400) AS avg_days
        FROM core.dgi_initiative
        WHERE completed_at IS NOT NULL AND deleted_at IS NULL
    """)
    lt_row = (await db.execute(lead_time_sql)).mappings().first()

    # Cycle time: avg days from started_at to completed_at
    cycle_time_sql = text("""
        SELECT AVG(EXTRACT(EPOCH FROM (completed_at - started_at)) / 86400) AS avg_days
        FROM core.dgi_initiative
        WHERE completed_at IS NOT NULL AND started_at IS NOT NULL AND deleted_at IS NULL
    """)
    ct_row = (await db.execute(cycle_time_sql)).mappings().first()

    # WIP: active initiatives (EN_CURSO + REVISION)
    wip_sql = text("""
        SELECT COUNT(*) AS wip
        FROM core.dgi_initiative ini
        JOIN ref.category st ON st.id = ini.status_id
        WHERE st.code IN ('EN_CURSO', 'REVISION')
          AND ini.deleted_at IS NULL
    """)
    wip_row = (await db.execute(wip_sql)).mappings().first()

    # Aging: days since last status change for active initiatives
    aging_sql = text("""
        SELECT
            ini.id,
            ini.name,
            st.code AS column,
            EXTRACT(EPOCH FROM (NOW() - ini.updated_at)) / 86400 AS days
        FROM core.dgi_initiative ini
        JOIN ref.category st ON st.id = ini.status_id
        WHERE st.code IN ('BACKLOG', 'EN_CURSO', 'REVISION')
          AND ini.deleted_at IS NULL
        ORDER BY days DESC
    """)
    aging_rows = (await db.execute(aging_sql)).mappings().all()

    return LeanMetrics(
        throughput_30d=t_row["t30"] if t_row else 0,
        throughput_60d=t_row["t60"] if t_row else 0,
        throughput_90d=t_row["t90"] if t_row else 0,
        lead_time_avg=round(float(lt_row["avg_days"]), 1) if lt_row and lt_row["avg_days"] else None,
        cycle_time_avg=round(float(ct_row["avg_days"]), 1) if ct_row and ct_row["avg_days"] else None,
        wip_count=wip_row["wip"] if wip_row else 0,
        aging=[
            {
                "id": str(r["id"]),
                "name": r["name"],
                "days": round(float(r["days"]), 1),
                "column": r["column"],
            }
            for r in aging_rows
        ],
    )


# ---------------------------------------------------------------------------
# GET /api/dgi/initiatives/{id}/dmaic — DMAIC detail
# ---------------------------------------------------------------------------
@router.get("/{initiative_id}/dmaic", response_model=DMAICDetail)
async def get_dmaic_detail(
    initiative_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Returns DMAIC content, current phase, and gate validation status."""
    _require_dgi(user)

    sql = text("""
        SELECT
            ini.id,
            ini.metadata,
            ph.code AS dmaic_phase
        FROM core.dgi_initiative ini
        LEFT JOIN ref.category ph ON ph.id = ini.dmaic_phase_id
        WHERE ini.id = :id AND ini.deleted_at IS NULL
    """)
    row = (await db.execute(sql, {"id": str(initiative_id)})).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Iniciativa no encontrada")

    metadata = row["metadata"] or {}
    current_phase = row["dmaic_phase"]

    # Extract DMAIC phase content from metadata
    phases = {
        "define": metadata.get("define", {}),
        "measure": metadata.get("measure", {}),
        "analyze": metadata.get("analyze", {}),
        "improve": metadata.get("improve", {}),
        "verify": metadata.get("verify", {}),
    }

    # Gate validation (informational)
    gates = _evaluate_dmaic_gates(phases)

    return DMAICDetail(
        initiative_id=row["id"],
        current_phase=current_phase,
        phases=phases,
        gates=gates,
    )


# ---------------------------------------------------------------------------
# POST /api/dgi/initiatives/{id}/dmaic/transition — Advance DMAIC phase
# ---------------------------------------------------------------------------
@router.post("/{initiative_id}/dmaic/transition")
async def transition_dmaic_phase(
    initiative_id: UUID,
    body: DMAICTransition,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Advance DMAIC phase with gate validation (informational, not blocking)."""
    _require_dgi(user)

    target_phase = body.target_phase.upper()
    if target_phase not in _DMAIC_PHASE_ORDER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fase DMAIC inválida: {target_phase}. Use: {', '.join(_DMAIC_PHASE_ORDER)}",
        )

    initiative_id_str = str(initiative_id)

    # Get current state
    sql = text("""
        SELECT ini.id,
               ini.metadata,
               ph.code AS current_phase,
               COALESCE(ph.valid_transitions, '[]'::jsonb) AS valid_transitions
        FROM core.dgi_initiative ini
        LEFT JOIN ref.category ph ON ph.id = ini.dmaic_phase_id
        WHERE ini.id = :id AND ini.deleted_at IS NULL
    """)
    row = (await db.execute(sql, {"id": initiative_id_str})).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Iniciativa no encontrada")

    current_phase = row["current_phase"]
    metadata = row["metadata"] or {}

    # La DB define el avance desde una fase persistida; una iniciativa sin fase
    # conserva el comportamiento de inicio existente.
    allowed_phases = set(
        _DMAIC_PHASE_ORDER if current_phase is None else row["valid_transitions"] or []
    )
    if target_phase not in allowed_phases:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede retroceder de {current_phase} a {target_phase}",
        )

    # Resolve target phase category id
    phase_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'dgi_dmaic_phase' AND code = :code"),
        {"code": target_phase},
    )).mappings().first()
    if not phase_row:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Fase DMAIC no encontrada en catálogo: {target_phase}")

    try:
        await db.execute(
            text("""
                UPDATE core.dgi_initiative
                SET dmaic_phase_id = :phase_id,
                    updated_at = NOW(),
                    updated_by_id = :user_id
                WHERE id = :id
            """),
            {"id": initiative_id_str, "phase_id": str(phase_row["id"]), "user_id": str(user["id"])},
        )
        await record_event(
            db,
            "STATE_TRANSITION",
            "core.dgi_initiative",
            initiative_id,
            user["id"],
            {"dmaic_phase": target_phase, "from": current_phase, "to": target_phase},
        )
        await db.commit()
    except DBAPIError as exc:
        await db.rollback()
        if "Transición de estado inválida" in str(exc.orig):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc.orig))
        raise

    # Evaluate gates for the result
    phases = {
        "define": metadata.get("define", {}),
        "measure": metadata.get("measure", {}),
        "analyze": metadata.get("analyze", {}),
        "improve": metadata.get("improve", {}),
        "verify": metadata.get("verify", {}),
    }
    gates = _evaluate_dmaic_gates(phases)

    return {
        "status": "ok",
        "previous_phase": current_phase,
        "new_phase": target_phase,
        "gates": [g.model_dump() for g in gates],
    }


# ---------------------------------------------------------------------------
# GET /api/dgi/initiatives/{id}/dmaic/history — DMAIC phase audit log
# ---------------------------------------------------------------------------
@router.get("/{initiative_id}/dmaic/history")
async def get_dmaic_history(
    initiative_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Returns DMAIC phase transition audit log from the initiative history trigger."""
    _require_dgi(user)

    initiative_id_str = str(initiative_id)

    # Verify exists
    existing = (await db.execute(
        text("SELECT id FROM core.dgi_initiative WHERE id = :id AND deleted_at IS NULL"),
        {"id": initiative_id_str},
    )).mappings().first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Iniciativa no encontrada")

    # Check if history table exists
    table_check = (await db.execute(
        text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'core' AND table_name = 'dgi_initiative_history'
            )
        """)
    )).scalar()

    if not table_check:
        return []

    sql = text("""
        SELECT
            h.id,
            prev.code AS previous_phase,
            new.code AS new_phase,
            p.names || ' ' || p.paternal_surname AS changed_by_name,
            h.changed_at
        FROM core.dgi_initiative_history h
        LEFT JOIN ref.category prev ON prev.id = h.previous_dmaic_phase_id
        LEFT JOIN ref.category new ON new.id = h.new_dmaic_phase_id
        LEFT JOIN core."user" u ON u.id = h.changed_by_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE h.initiative_id = :id
          AND h.previous_dmaic_phase_id IS DISTINCT FROM h.new_dmaic_phase_id
        ORDER BY h.changed_at DESC
    """)
    rows = (await db.execute(sql, {"id": initiative_id_str})).mappings().all()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# PATCH /api/dgi/initiatives/{id}/dmaic/{phase} — Update DMAIC phase content
# ---------------------------------------------------------------------------
@router.patch("/{initiative_id}/dmaic/{phase}")
async def update_dmaic_phase(
    initiative_id: UUID,
    phase: str,
    body: DMAICPhaseUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Atomic jsonb_set update for one DMAIC phase section."""
    _require_dgi(user)

    phase_lower = phase.lower()
    if phase_lower not in ("define", "measure", "analyze", "improve", "verify"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Fase DMAIC inválida: {phase}")

    initiative_id_str = str(initiative_id)

    # Verify initiative exists
    existing = (await db.execute(
        text("SELECT id FROM core.dgi_initiative WHERE id = :id AND deleted_at IS NULL"),
        {"id": initiative_id_str},
    )).mappings().first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Iniciativa no encontrada")

    # Build phase content from non-None fields
    phase_content = {k: v for k, v in body.model_dump().items() if v is not None}

    # Atomic jsonb_set: merge into existing phase data
    # Use ARRAY[...] instead of CAST for asyncpg text[] compatibility
    await db.execute(
        text("""
            UPDATE core.dgi_initiative
            SET metadata = jsonb_set(
                COALESCE(metadata, '{}'),
                ARRAY[:phase_key],
                COALESCE(metadata->:phase_key, '{}') || CAST(:content AS jsonb)
            ),
            updated_at = NOW(),
            updated_by_id = :user_id
            WHERE id = :id
        """),
        {
            "id": initiative_id_str,
            "phase_key": phase_lower,
            "content": json.dumps(phase_content),
            "user_id": str(user["id"]),
        },
    )
    await db.commit()

    return {"status": "ok", "phase": phase_lower, "updated_fields": list(phase_content.keys())}
