import math
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import DGI_ROLES
from app.schemas.dgi import (
    ProcessItem, ProcessCreate, ProcessUpdate, ProcessDetail,
    ProcessActorItem, ProcessActorCreate,
    ProcessRuleItem, ProcessRuleCreate,
    ProcessMetricItem, ProcessMetricCreate,
    ProcessPainPointItem, ProcessPainPointCreate,
    ImprovementOpportunityItem, ImprovementOpportunityCreate, ImprovementOpportunityUpdate,
    ProcessProgressItem,
    BPMNModelItem,
    MetricComparison, ImpactEffortCell,
)


def _require_dgi(user: dict):
    if user.get("role_code") not in DGI_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo roles DGI pueden gestionar procesos")


router = APIRouter(prefix="/api/dgi/processes", tags=["dgi"])

# ---------------------------------------------------------------------------
# FSM for process status transitions
# ---------------------------------------------------------------------------
_PROCESS_FSM: dict[str, set[str]] = {
    "IDENTIFICADO":     {"EN_LEVANTAMIENTO", "SUSPENDIDO"},
    "EN_LEVANTAMIENTO": {"MODELADO", "IDENTIFICADO", "SUSPENDIDO"},
    "MODELADO":         {"VALIDADO", "EN_LEVANTAMIENTO", "SUSPENDIDO"},
    "VALIDADO":         {"PUBLICADO", "MODELADO", "SUSPENDIDO"},
    "PUBLICADO":        {"SUSPENDIDO"},
    "SUSPENDIDO":       {"IDENTIFICADO"},
}

# ---------------------------------------------------------------------------
# PATCH allowlist
# ---------------------------------------------------------------------------
_PROCESS_FIELD_ALLOWLIST = {"name", "description", "scope", "division_id", "owner_id", "criticality"}


# ---------------------------------------------------------------------------
# Helper: fetch a single process row with JOINs
# ---------------------------------------------------------------------------
async def _get_process_row(process_id: str, db: AsyncSession) -> dict | None:
    sql = text("""
        SELECT
            proc.id,
            proc.code,
            proc.name,
            proc.description,
            proc.scope,
            proc.division_id,
            org.name          AS division_name,
            proc.owner_id,
            p.names || ' ' || p.paternal_surname AS owner_name,
            st.code           AS status,
            proc.criticality,
            proc.created_at,
            proc.updated_at,
            (SELECT COUNT(*) FROM core.dgi_bpmn_model bm
             WHERE bm.process_id = proc.id AND bm.deleted_at IS NULL) AS bpmn_count
        FROM core.dgi_process proc
        JOIN ref.category st ON st.id = proc.status_id
        LEFT JOIN core.organization org ON org.id = proc.division_id
        LEFT JOIN core."user" u ON u.id = proc.owner_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE proc.id = :id AND proc.deleted_at IS NULL
    """)
    row = (await db.execute(sql, {"id": process_id})).mappings().first()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# GET /api/dgi/processes/progress — MP-010 dashboard
# REGISTERED BEFORE /{process_id} to avoid path conflict
# ---------------------------------------------------------------------------
@router.get("/progress", response_model=list[ProcessProgressItem])
async def get_process_progress(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    MP-010: Process progress dashboard.
    Returns process counts grouped by division and status.
    """
    _require_dgi(user)

    sql = text("""
        SELECT
            COALESCE(org.name, 'Sin División') AS division_name,
            st.code AS status_code,
            COUNT(*) AS cnt
        FROM core.dgi_process proc
        JOIN ref.category st ON st.id = proc.status_id
        LEFT JOIN core.organization org ON org.id = proc.division_id
        WHERE proc.deleted_at IS NULL
        GROUP BY org.name, st.code
        ORDER BY org.name
    """)
    rows = (await db.execute(sql)).mappings().all()

    # Pivot into ProcessProgressItem per division
    divisions: dict[str, dict] = {}
    for r in rows:
        div = r["division_name"]
        if div not in divisions:
            divisions[div] = {
                "division_name": div,
                "total": 0,
                "identificado": 0,
                "en_levantamiento": 0,
                "modelado": 0,
                "validado": 0,
                "publicado": 0,
                "suspendido": 0,
            }
        code_lower = r["status_code"].lower()
        count = r["cnt"]
        divisions[div]["total"] += count
        if code_lower in divisions[div]:
            divisions[div][code_lower] = count

    return [ProcessProgressItem(**v) for v in divisions.values()]


# ---------------------------------------------------------------------------
# GET /api/dgi/processes/impact-effort — Impact/Effort matrix
# REGISTERED BEFORE /{process_id} to avoid path conflict
# ---------------------------------------------------------------------------
@router.get("/impact-effort", response_model=list[ImpactEffortCell])
async def get_impact_effort_matrix(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Aggregated impact/effort matrix from all active opportunities.
    Returns cells with counts and opportunity details.
    """
    _require_dgi(user)

    sql = text("""
        SELECT
            opp.impact,
            opp.effort,
            opp.id,
            opp.description
        FROM core.dgi_improvement_opportunity opp
        JOIN core.dgi_process proc ON proc.id = opp.process_id
        WHERE opp.deleted_at IS NULL
          AND proc.deleted_at IS NULL
          AND opp.impact IS NOT NULL
          AND opp.effort IS NOT NULL
        ORDER BY opp.impact, opp.effort
    """)
    rows = (await db.execute(sql)).mappings().all()

    # Group by impact x effort
    cells: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        key = (r["impact"], r["effort"])
        if key not in cells:
            cells[key] = []
        cells[key].append({"id": str(r["id"]), "description": r["description"]})

    # Build all possible cells (3x3 grid)
    result = []
    for impact in ["ALTO", "MEDIO", "BAJO"]:
        for effort in ["BAJO", "MEDIO", "ALTO"]:
            key = (impact, effort)
            opps = cells.get(key, [])
            result.append(ImpactEffortCell(
                impact=impact,
                effort=effort,
                count=len(opps),
                opportunities=opps,
            ))

    return result


# ---------------------------------------------------------------------------
# GET /api/dgi/processes — List processes (paginated)
# ---------------------------------------------------------------------------
@router.get("")
async def list_processes(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    division_id: UUID | None = None,
    status_filter: str | None = Query(None, alias="status"),
    criticality: str | None = None,
    search: str | None = Query(None, description="ILIKE search on name/code"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List DGI processes with optional filters. Always paginated."""
    _require_dgi(user)

    conditions = ["proc.deleted_at IS NULL"]
    params: dict = {}

    if division_id:
        conditions.append("proc.division_id = :division_id")
        params["division_id"] = str(division_id)

    if status_filter:
        conditions.append("st.code = :status_filter")
        params["status_filter"] = status_filter.upper()

    if criticality:
        conditions.append("proc.criticality = :criticality")
        params["criticality"] = criticality.upper()

    if search:
        conditions.append("(proc.name ILIKE :search OR proc.code ILIKE :search)")
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions)

    base_from = f"""
        FROM core.dgi_process proc
        JOIN ref.category st ON st.id = proc.status_id
        LEFT JOIN core.organization org ON org.id = proc.division_id
        LEFT JOIN core."user" u ON u.id = proc.owner_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE {where_clause}
    """

    # Count
    count_result = await db.execute(text(f"SELECT COUNT(*) {base_from}"), params)
    total = count_result.scalar() or 0
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    select_cols = """
            proc.id,
            proc.code,
            proc.name,
            proc.description,
            proc.scope,
            proc.division_id,
            org.name          AS division_name,
            proc.owner_id,
            p.names || ' ' || p.paternal_surname AS owner_name,
            st.code           AS status,
            proc.criticality,
            (SELECT COUNT(*) FROM core.dgi_bpmn_model bm
             WHERE bm.process_id = proc.id AND bm.deleted_at IS NULL) AS bpmn_count
    """

    rows = (await db.execute(
        text(f"SELECT {select_cols} {base_from} ORDER BY proc.name LIMIT :limit OFFSET :offset"),
        params,
    )).mappings().all()

    items = [
        ProcessItem(
            id=r["id"], code=r["code"], name=r["name"], description=r["description"],
            scope=r["scope"], division_id=r["division_id"], division_name=r["division_name"],
            owner_id=r["owner_id"], owner_name=r["owner_name"],
            status=r["status"], criticality=r["criticality"],
            bpmn_count=r["bpmn_count"],
        ).model_dump()
        for r in rows
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------------------
# POST /api/dgi/processes — Create process
# ---------------------------------------------------------------------------
@router.post("", status_code=status.HTTP_201_CREATED, response_model=ProcessItem)
async def create_process(
    body: ProcessCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    # Resolve status_id
    status_code = body.status.upper() if body.status else "IDENTIFICADO"
    st_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'dgi_process_status' AND code = :code"),
        {"code": status_code},
    )).mappings().first()
    if not st_row:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Estado inválido: {status_code}")
    status_id = str(st_row["id"])

    # Advisory lock for code generation
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('proc_code'))"))
    seq = (await db.execute(
        text("SELECT COALESCE(MAX(SUBSTRING(code, 6)::int), 0) FROM core.dgi_process WHERE code LIKE 'PROC-%'")
    )).scalar() or 0
    code = f"PROC-{seq + 1:04d}"

    result = await db.execute(
        text("""
            INSERT INTO core.dgi_process
                (code, name, description, scope, division_id, owner_id, status_id, criticality, created_by_id)
            VALUES
                (:code, :name, :description, :scope, :division_id, :owner_id, :status_id, :criticality, :created_by_id)
            RETURNING id
        """),
        {
            "code": code,
            "name": body.name,
            "description": body.description,
            "scope": body.scope,
            "division_id": str(body.division_id) if body.division_id else None,
            "owner_id": str(body.owner_id) if body.owner_id else None,
            "status_id": status_id,
            "criticality": body.criticality.upper() if body.criticality else "MEDIA",
            "created_by_id": str(user["id"]),
        },
    )
    new_id = str(result.scalar())
    await db.commit()

    row = await _get_process_row(new_id, db)
    return ProcessItem(
        id=row["id"], code=row["code"], name=row["name"], description=row["description"],
        scope=row["scope"], division_id=row["division_id"], division_name=row["division_name"],
        owner_id=row["owner_id"], owner_name=row["owner_name"],
        status=row["status"], criticality=row["criticality"],
        bpmn_count=row["bpmn_count"],
    )


# ---------------------------------------------------------------------------
# GET /api/dgi/processes/{process_id} — Process detail
# ---------------------------------------------------------------------------
@router.get("/{process_id}", response_model=ProcessDetail)
async def get_process(
    process_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    row = await _get_process_row(str(process_id), db)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso no encontrado")

    # Fetch BPMN models for this process
    bpmn_rows = (await db.execute(
        text("""
            SELECT
                bm.id,
                bm.code,
                proc.name AS process_name,
                bm.version,
                st.code   AS status,
                bm.description
            FROM core.dgi_bpmn_model bm
            JOIN ref.category st ON st.id = bm.status_id
            LEFT JOIN core.dgi_process proc ON proc.id = bm.process_id
            WHERE bm.process_id = :process_id AND bm.deleted_at IS NULL
            ORDER BY bm.created_at DESC
        """),
        {"process_id": str(process_id)},
    )).mappings().all()

    bpmn_models = [
        BPMNModelItem(
            id=b["id"], code=b["code"], process_name=b["process_name"],
            version=b["version"], status=b["status"], description=b["description"],
        )
        for b in bpmn_rows
    ]

    return ProcessDetail(
        id=row["id"], code=row["code"], name=row["name"], description=row["description"],
        scope=row["scope"], division_id=row["division_id"], division_name=row["division_name"],
        owner_id=row["owner_id"], owner_name=row["owner_name"],
        status=row["status"], criticality=row["criticality"],
        bpmn_count=row["bpmn_count"],
        created_at=row["created_at"], updated_at=row["updated_at"],
        bpmn_models=bpmn_models,
    )


# ---------------------------------------------------------------------------
# PATCH /api/dgi/processes/{process_id} — Update process
# ---------------------------------------------------------------------------
@router.patch("/{process_id}", response_model=ProcessItem)
async def update_process(
    process_id: UUID,
    body: ProcessUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    process_id_str = str(process_id)
    existing = await _get_process_row(process_id_str, db)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso no encontrado")

    updates: dict = {}

    # --- Status transition (FSM-validated, handled separately) ---
    if body.status is not None:
        target_status = body.status.upper()
        current_status = existing["status"]

        if target_status != current_status:
            allowed = _PROCESS_FSM.get(current_status, set())
            if target_status not in allowed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Transición inválida: {current_status} → {target_status}. "
                           f"Transiciones permitidas: {', '.join(sorted(allowed)) if allowed else 'ninguna'}",
                )
            # Resolve new status_id
            st_row = (await db.execute(
                text("SELECT id FROM ref.category WHERE scheme = 'dgi_process_status' AND code = :code"),
                {"code": target_status},
            )).mappings().first()
            if not st_row:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Estado inválido: {target_status}")
            updates["status_id"] = str(st_row["id"])

    # --- Regular field updates ---
    payload = body.model_dump(exclude_none=True)
    for k, v in payload.items():
        if k in _PROCESS_FIELD_ALLOWLIST:
            updates[k] = v

    if not updates:
        return ProcessItem(
            id=existing["id"], code=existing["code"], name=existing["name"],
            description=existing["description"], scope=existing["scope"],
            division_id=existing["division_id"], division_name=existing["division_name"],
            owner_id=existing["owner_id"], owner_name=existing["owner_name"],
            status=existing["status"], criticality=existing["criticality"],
            bpmn_count=existing["bpmn_count"],
        )

    # Convert UUID fields to str for SQL
    for k in ("division_id", "owner_id"):
        if k in updates and updates[k] is not None:
            updates[k] = str(updates[k])

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = process_id_str
    updates["updated_by_id"] = str(user["id"])

    await db.execute(
        text(f"UPDATE core.dgi_process SET {set_clauses}, updated_at = NOW(), updated_by_id = :updated_by_id WHERE id = :id"),
        updates,
    )
    await db.commit()

    row = await _get_process_row(process_id_str, db)
    return ProcessItem(
        id=row["id"], code=row["code"], name=row["name"], description=row["description"],
        scope=row["scope"], division_id=row["division_id"], division_name=row["division_name"],
        owner_id=row["owner_id"], owner_name=row["owner_name"],
        status=row["status"], criticality=row["criticality"],
        bpmn_count=row["bpmn_count"],
    )


# ---------------------------------------------------------------------------
# DELETE /api/dgi/processes/{process_id} — Soft delete
# ---------------------------------------------------------------------------
@router.delete("/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_process(
    process_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    process_id_str = str(process_id)
    existing = await _get_process_row(process_id_str, db)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso no encontrado")

    await db.execute(
        text("""
            UPDATE core.dgi_process
            SET deleted_at = NOW(), deleted_by_id = :deleted_by_id
            WHERE id = :id
        """),
        {"id": process_id_str, "deleted_by_id": str(user["id"])},
    )
    await db.commit()


# ===========================================================================
# SATELLITE: Actors
# ===========================================================================

@router.get("/{process_id}/actors", response_model=list[ProcessActorItem])
async def list_actors(
    process_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    # Verify process exists
    existing = await _get_process_row(str(process_id), db)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso no encontrado")

    rows = (await db.execute(
        text("""
            SELECT id, actor_type, actor_name, lane_label, description, created_at
            FROM core.dgi_process_actor
            WHERE process_id = :process_id
            ORDER BY actor_name
        """),
        {"process_id": str(process_id)},
    )).mappings().all()

    return [
        ProcessActorItem(
            id=r["id"], actor_type=r["actor_type"], actor_name=r["actor_name"],
            lane_label=r["lane_label"], description=r["description"], created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{process_id}/actors", status_code=status.HTTP_201_CREATED, response_model=ProcessActorItem)
async def create_actor(
    process_id: UUID,
    body: ProcessActorCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    existing = await _get_process_row(str(process_id), db)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso no encontrado")

    result = await db.execute(
        text("""
            INSERT INTO core.dgi_process_actor (process_id, actor_type, actor_name, lane_label, description)
            VALUES (:process_id, :actor_type, :actor_name, :lane_label, :description)
            RETURNING id, actor_type, actor_name, lane_label, description, created_at
        """),
        {
            "process_id": str(process_id),
            "actor_type": body.actor_type.upper(),
            "actor_name": body.actor_name,
            "lane_label": body.lane_label,
            "description": body.description,
        },
    )
    r = result.mappings().first()
    await db.commit()

    return ProcessActorItem(
        id=r["id"], actor_type=r["actor_type"], actor_name=r["actor_name"],
        lane_label=r["lane_label"], description=r["description"], created_at=r["created_at"],
    )


@router.delete("/{process_id}/actors/{actor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_actor(
    process_id: UUID,
    actor_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    result = await db.execute(
        text("DELETE FROM core.dgi_process_actor WHERE id = :actor_id AND process_id = :process_id"),
        {"actor_id": str(actor_id), "process_id": str(process_id)},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Actor no encontrado")
    await db.commit()


# ===========================================================================
# SATELLITE: Rules
# ===========================================================================

@router.get("/{process_id}/rules", response_model=list[ProcessRuleItem])
async def list_rules(
    process_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    existing = await _get_process_row(str(process_id), db)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso no encontrado")

    rows = (await db.execute(
        text("""
            SELECT id, code, description, rule_type, created_at
            FROM core.dgi_process_rule
            WHERE process_id = :process_id
            ORDER BY code
        """),
        {"process_id": str(process_id)},
    )).mappings().all()

    return [
        ProcessRuleItem(
            id=r["id"], code=r["code"], description=r["description"],
            rule_type=r["rule_type"], created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{process_id}/rules", status_code=status.HTTP_201_CREATED, response_model=ProcessRuleItem)
async def create_rule(
    process_id: UUID,
    body: ProcessRuleCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    existing = await _get_process_row(str(process_id), db)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso no encontrado")

    try:
        result = await db.execute(
            text("""
                INSERT INTO core.dgi_process_rule (process_id, code, description, rule_type)
                VALUES (:process_id, :code, :description, :rule_type)
                RETURNING id, code, description, rule_type, created_at
            """),
            {
                "process_id": str(process_id),
                "code": body.code,
                "description": body.description,
                "rule_type": body.rule_type.upper(),
            },
        )
        r = result.mappings().first()
        await db.commit()
    except Exception as e:
        await db.rollback()
        error_str = str(e)
        if "unique" in error_str.lower() or "duplicate" in error_str.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una regla con código '{body.code}' en este proceso",
            )
        raise

    return ProcessRuleItem(
        id=r["id"], code=r["code"], description=r["description"],
        rule_type=r["rule_type"], created_at=r["created_at"],
    )


@router.delete("/{process_id}/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    process_id: UUID,
    rule_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    result = await db.execute(
        text("DELETE FROM core.dgi_process_rule WHERE id = :rule_id AND process_id = :process_id"),
        {"rule_id": str(rule_id), "process_id": str(process_id)},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regla no encontrada")
    await db.commit()


# ===========================================================================
# SATELLITE: Metrics
# ===========================================================================

@router.get("/{process_id}/metrics", response_model=list[ProcessMetricItem])
async def list_metrics(
    process_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    existing = await _get_process_row(str(process_id), db)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso no encontrado")

    rows = (await db.execute(
        text("""
            SELECT id, name, value, unit, measured_at, measurement_type, source, created_at
            FROM core.dgi_process_metric
            WHERE process_id = :process_id
            ORDER BY measured_at DESC, name
        """),
        {"process_id": str(process_id)},
    )).mappings().all()

    return [
        ProcessMetricItem(
            id=r["id"], name=r["name"], value=float(r["value"]) if r["value"] is not None else None,
            unit=r["unit"], measured_at=r["measured_at"],
            measurement_type=r["measurement_type"], source=r["source"],
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{process_id}/metrics", status_code=status.HTTP_201_CREATED, response_model=ProcessMetricItem)
async def create_metric(
    process_id: UUID,
    body: ProcessMetricCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    existing = await _get_process_row(str(process_id), db)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso no encontrado")

    result = await db.execute(
        text("""
            INSERT INTO core.dgi_process_metric
                (process_id, name, value, unit, measured_at, measurement_type, source, created_by_id)
            VALUES
                (:process_id, :name, :value, :unit, COALESCE(:measured_at, CURRENT_DATE), :measurement_type, :source, :created_by_id)
            RETURNING id, name, value, unit, measured_at, measurement_type, source, created_at
        """),
        {
            "process_id": str(process_id),
            "name": body.name,
            "value": body.value,
            "unit": body.unit,
            "measured_at": body.measured_at,
            "measurement_type": body.measurement_type.upper() if body.measurement_type else "BASELINE",
            "source": body.source,
            "created_by_id": str(user["id"]),
        },
    )
    r = result.mappings().first()
    await db.commit()

    return ProcessMetricItem(
        id=r["id"], name=r["name"], value=float(r["value"]) if r["value"] is not None else None,
        unit=r["unit"], measured_at=r["measured_at"],
        measurement_type=r["measurement_type"], source=r["source"],
        created_at=r["created_at"],
    )


@router.delete("/{process_id}/metrics/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_metric(
    process_id: UUID,
    metric_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    result = await db.execute(
        text("DELETE FROM core.dgi_process_metric WHERE id = :metric_id AND process_id = :process_id"),
        {"metric_id": str(metric_id), "process_id": str(process_id)},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Métrica no encontrada")
    await db.commit()


# ---------------------------------------------------------------------------
# GET /api/dgi/processes/{process_id}/metrics/comparison — Before/After
# ---------------------------------------------------------------------------
@router.get("/{process_id}/metrics/comparison", response_model=list[MetricComparison])
async def get_metrics_comparison(
    process_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    MP-018: Before/after metric comparison.
    Groups metrics by name, showing BASELINE vs POST_MEJORA values side by side.
    """
    _require_dgi(user)

    process_id_str = str(process_id)

    # Verify process exists
    existing = (await db.execute(
        text("SELECT id FROM core.dgi_process WHERE id = :id AND deleted_at IS NULL"),
        {"id": process_id_str},
    )).mappings().first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso no encontrado")

    sql = text("""
        SELECT
            m.name,
            m.value,
            m.unit,
            m.measurement_type
        FROM core.dgi_process_metric m
        WHERE m.process_id = :process_id
          AND m.deleted_at IS NULL
          AND m.measurement_type IN ('BASELINE', 'POST_MEJORA')
        ORDER BY m.name, m.measurement_type
    """)
    rows = (await db.execute(sql, {"process_id": process_id_str})).mappings().all()

    # Group by metric name
    grouped: dict[str, dict] = {}
    for r in rows:
        name = r["name"]
        if name not in grouped:
            grouped[name] = {"name": name, "baseline_value": None, "post_mejora_value": None, "unit": r["unit"]}
        if r["measurement_type"] == "BASELINE":
            grouped[name]["baseline_value"] = float(r["value"]) if r["value"] is not None else None
        elif r["measurement_type"] == "POST_MEJORA":
            grouped[name]["post_mejora_value"] = float(r["value"]) if r["value"] is not None else None

    # Compute deltas
    result = []
    for data in grouped.values():
        baseline = data["baseline_value"]
        post = data["post_mejora_value"]
        delta = None
        improved = False
        if baseline is not None and post is not None:
            delta = round(post - baseline, 2)
            improved = post > baseline  # Higher is better by default
        result.append(MetricComparison(
            name=data["name"],
            baseline_value=baseline,
            post_mejora_value=post,
            unit=data["unit"],
            delta=delta,
            improved=improved,
        ))

    return result


# ===========================================================================
# SATELLITE: Pain Points
# ===========================================================================

@router.get("/{process_id}/pain-points", response_model=list[ProcessPainPointItem])
async def list_pain_points(
    process_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    existing = await _get_process_row(str(process_id), db)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso no encontrado")

    rows = (await db.execute(
        text("""
            SELECT
                pp.id, pp.description, pp.impact, pp.bpmn_stage,
                p.names || ' ' || p.paternal_surname AS reported_by_name,
                pp.created_at
            FROM core.dgi_process_pain_point pp
            LEFT JOIN core."user" u ON u.id = pp.reported_by_id
            LEFT JOIN core.person p ON p.id = u.person_id
            WHERE pp.process_id = :process_id
            ORDER BY pp.created_at DESC
        """),
        {"process_id": str(process_id)},
    )).mappings().all()

    return [
        ProcessPainPointItem(
            id=r["id"], description=r["description"], impact=r["impact"],
            bpmn_stage=r["bpmn_stage"], reported_by_name=r["reported_by_name"],
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{process_id}/pain-points", status_code=status.HTTP_201_CREATED, response_model=ProcessPainPointItem)
async def create_pain_point(
    process_id: UUID,
    body: ProcessPainPointCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    existing = await _get_process_row(str(process_id), db)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso no encontrado")

    result = await db.execute(
        text("""
            INSERT INTO core.dgi_process_pain_point
                (process_id, description, impact, bpmn_stage, reported_by_id)
            VALUES
                (:process_id, :description, :impact, :bpmn_stage, :reported_by_id)
            RETURNING id, description, impact, bpmn_stage, created_at
        """),
        {
            "process_id": str(process_id),
            "description": body.description,
            "impact": body.impact.upper(),
            "bpmn_stage": body.bpmn_stage,
            "reported_by_id": str(user["id"]),
        },
    )
    r = result.mappings().first()
    await db.commit()

    # Re-fetch to get reported_by_name via JOIN
    pp_row = (await db.execute(
        text("""
            SELECT
                pp.id, pp.description, pp.impact, pp.bpmn_stage,
                p.names || ' ' || p.paternal_surname AS reported_by_name,
                pp.created_at
            FROM core.dgi_process_pain_point pp
            LEFT JOIN core."user" u ON u.id = pp.reported_by_id
            LEFT JOIN core.person p ON p.id = u.person_id
            WHERE pp.id = :id
        """),
        {"id": str(r["id"])},
    )).mappings().first()

    return ProcessPainPointItem(
        id=pp_row["id"], description=pp_row["description"], impact=pp_row["impact"],
        bpmn_stage=pp_row["bpmn_stage"], reported_by_name=pp_row["reported_by_name"],
        created_at=pp_row["created_at"],
    )


@router.delete("/{process_id}/pain-points/{pain_point_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pain_point(
    process_id: UUID,
    pain_point_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    result = await db.execute(
        text("DELETE FROM core.dgi_process_pain_point WHERE id = :pain_point_id AND process_id = :process_id"),
        {"pain_point_id": str(pain_point_id), "process_id": str(process_id)},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Punto de dolor no encontrado")
    await db.commit()


# ===========================================================================
# SATELLITE: Improvement Opportunities
# ===========================================================================

@router.get("/{process_id}/opportunities", response_model=list[ImprovementOpportunityItem])
async def list_opportunities(
    process_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    existing = await _get_process_row(str(process_id), db)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso no encontrado")

    rows = (await db.execute(
        text("""
            SELECT
                opp.id, opp.dimension, opp.description, opp.impact, opp.effort,
                opp.status, opp.initiative_id,
                ini.code AS initiative_code,
                opp.created_at
            FROM core.dgi_improvement_opportunity opp
            LEFT JOIN core.dgi_initiative ini ON ini.id = opp.initiative_id
            WHERE opp.process_id = :process_id AND opp.deleted_at IS NULL
            ORDER BY opp.created_at DESC
        """),
        {"process_id": str(process_id)},
    )).mappings().all()

    return [
        ImprovementOpportunityItem(
            id=r["id"], dimension=r["dimension"], description=r["description"],
            impact=r["impact"], effort=r["effort"], status=r["status"],
            initiative_id=r["initiative_id"], initiative_code=r["initiative_code"],
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{process_id}/opportunities", status_code=status.HTTP_201_CREATED, response_model=ImprovementOpportunityItem)
async def create_opportunity(
    process_id: UUID,
    body: ImprovementOpportunityCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    existing = await _get_process_row(str(process_id), db)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proceso no encontrado")

    result = await db.execute(
        text("""
            INSERT INTO core.dgi_improvement_opportunity
                (process_id, dimension, description, impact, effort, status, created_by_id)
            VALUES
                (:process_id, :dimension, :description, :impact, :effort, :status, :created_by_id)
            RETURNING id, dimension, description, impact, effort, status, created_at
        """),
        {
            "process_id": str(process_id),
            "dimension": body.dimension.upper(),
            "description": body.description,
            "impact": body.impact.upper(),
            "effort": body.effort.upper(),
            "status": body.status.upper() if body.status else "PROPUESTA",
            "created_by_id": str(user["id"]),
        },
    )
    r = result.mappings().first()
    await db.commit()

    return ImprovementOpportunityItem(
        id=r["id"], dimension=r["dimension"], description=r["description"],
        impact=r["impact"], effort=r["effort"], status=r["status"],
        initiative_id=None, initiative_code=None,
        created_at=r["created_at"],
    )


@router.patch("/{process_id}/opportunities/{opportunity_id}", response_model=ImprovementOpportunityItem)
async def update_opportunity(
    process_id: UUID,
    opportunity_id: UUID,
    body: ImprovementOpportunityUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update opportunity status and/or link to initiative (MP-013 bridge)."""
    _require_dgi(user)

    # Verify opportunity exists and belongs to process
    opp_row = (await db.execute(
        text("""
            SELECT id FROM core.dgi_improvement_opportunity
            WHERE id = :opp_id AND process_id = :process_id AND deleted_at IS NULL
        """),
        {"opp_id": str(opportunity_id), "process_id": str(process_id)},
    )).mappings().first()
    if not opp_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oportunidad de mejora no encontrada")

    updates: dict = {}
    if body.status is not None:
        updates["status"] = body.status.upper()
    if body.initiative_id is not None:
        updates["initiative_id"] = str(body.initiative_id)

    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se proporcionaron campos para actualizar")

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["opp_id"] = str(opportunity_id)

    await db.execute(
        text(f"UPDATE core.dgi_improvement_opportunity SET {set_clauses}, updated_at = NOW() WHERE id = :opp_id"),
        updates,
    )
    await db.commit()

    # Re-fetch with JOIN
    r = (await db.execute(
        text("""
            SELECT
                opp.id, opp.dimension, opp.description, opp.impact, opp.effort,
                opp.status, opp.initiative_id,
                ini.code AS initiative_code,
                opp.created_at
            FROM core.dgi_improvement_opportunity opp
            LEFT JOIN core.dgi_initiative ini ON ini.id = opp.initiative_id
            WHERE opp.id = :opp_id
        """),
        {"opp_id": str(opportunity_id)},
    )).mappings().first()

    return ImprovementOpportunityItem(
        id=r["id"], dimension=r["dimension"], description=r["description"],
        impact=r["impact"], effort=r["effort"], status=r["status"],
        initiative_id=r["initiative_id"], initiative_code=r["initiative_code"],
        created_at=r["created_at"],
    )


@router.delete("/{process_id}/opportunities/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    process_id: UUID,
    opportunity_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete an improvement opportunity."""
    _require_dgi(user)

    result = await db.execute(
        text("""
            UPDATE core.dgi_improvement_opportunity
            SET deleted_at = NOW()
            WHERE id = :opp_id AND process_id = :process_id AND deleted_at IS NULL
        """),
        {"opp_id": str(opportunity_id), "process_id": str(process_id)},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Oportunidad de mejora no encontrada")
    await db.commit()
