from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import DGI_ROLES
from app.schemas.dgi import InitiativeItem, InitiativeCreate, InitiativeUpdate, InitiativeMove


def _require_dgi(user: dict):
    if user.get("role_code") not in DGI_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo roles DGI pueden gestionar iniciativas")

router = APIRouter(prefix="/api/dgi/initiatives", tags=["dgi"])

# ---------------------------------------------------------------------------
# WIP limits per column
# ---------------------------------------------------------------------------
_WIP_LIMITS: dict[str, int] = {
    "EN_CURSO": 5,
    "REVISION": 2,
}

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
            ini.wip_column
        FROM core.dgi_initiative ini
        JOIN ref.category st ON st.id = ini.status_id
        LEFT JOIN ref.category ph ON ph.id = ini.dmaic_phase_id
        LEFT JOIN core.organization org ON org.id = ini.division_id
        LEFT JOIN core."user" u ON u.id = ini.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE ini.id = :id
    """)
    row = (await db.execute(sql, {"id": initiative_id})).mappings().first()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# GET /api/dgi/initiatives — List all initiatives
# ---------------------------------------------------------------------------
@router.get("", response_model=list[InitiativeItem])
async def list_initiatives(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
    responsible_id: UUID | None = None,
):
    """
    List all DGI initiatives.

    Optional filters:
    - status: filter by initiative status code (BACKLOG, EN_CURSO, REVISION, COMPLETADO)
    - responsible_id: filter by responsible user UUID
    """
    conditions = ["1=1"]
    params: dict = {}

    if status_filter:
        conditions.append("st.code = :status_filter")
        params["status_filter"] = status_filter

    if responsible_id:
        conditions.append("ini.responsible_id = :responsible_id")
        params["responsible_id"] = str(responsible_id)

    where_clause = " AND ".join(conditions)

    sql = text(f"""
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
            ini.wip_column
        FROM core.dgi_initiative ini
        JOIN ref.category st ON st.id = ini.status_id
        LEFT JOIN ref.category ph ON ph.id = ini.dmaic_phase_id
        LEFT JOIN core.organization org ON org.id = ini.division_id
        LEFT JOIN core."user" u ON u.id = ini.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE {where_clause}
        ORDER BY
            CASE st.code
                WHEN 'EN_CURSO'   THEN 1
                WHEN 'REVISION'   THEN 2
                WHEN 'BACKLOG'    THEN 3
                WHEN 'COMPLETADO' THEN 4
                ELSE 5
            END,
            ini.target_date ASC NULLS LAST,
            ini.name
    """)

    rows = (await db.execute(sql, params)).mappings().all()

    return [
        InitiativeItem(
            id=r["id"],
            code=r["code"],
            name=r["name"],
            description=r["description"],
            responsible_id=r["responsible_id"],
            responsible_name=r["responsible_name"],
            status=r["status"],
            dmaic_phase=r["dmaic_phase"],
            division_name=r["division_name"],
            start_date=r["start_date"],
            target_date=r["target_date"],
            current_day=r["current_day"] or 0,
            total_days=r["total_days"],
            progress=r["progress"] or 0.0,
            wip_column=r["wip_column"],
        )
        for r in rows
    ]


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

    # Auto-generate code
    count_row = (await db.execute(text("SELECT COUNT(*) FROM core.dgi_initiative"))).scalar() or 0
    code = f"INI-{count_row + 1:04d}"

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
    await db.commit()

    row = await _get_initiative_row(new_id, db)
    return InitiativeItem(
        id=row["id"], code=row["code"], name=row["name"], description=row["description"],
        responsible_id=row["responsible_id"], responsible_name=row["responsible_name"],
        status=row["status"], dmaic_phase=row["dmaic_phase"],
        division_name=row["division_name"], start_date=row["start_date"], target_date=row["target_date"],
        current_day=row["current_day"] or 0, total_days=row["total_days"],
        progress=row["progress"] or 0.0, wip_column=row["wip_column"],
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

    WIP limits enforced:
    - EN_CURSO: max 5
    - REVISION: max 2

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

    # ── Check WIP limit for target column ────────────────────────────────
    if target_status in _WIP_LIMITS:
        wip_count_result = await db.execute(
            text("""
                SELECT COUNT(*) AS current_wip
                FROM core.dgi_initiative ini
                JOIN ref.category st ON st.id = ini.status_id
                WHERE st.code = :target_status
                  AND ini.id != :initiative_id
            """),
            {"target_status": target_status, "initiative_id": initiative_id_str},
        )
        wip_count = wip_count_result.scalar() or 0
        limit = _WIP_LIMITS[target_status]
        if wip_count >= limit:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Límite WIP alcanzado para '{target_status}': "
                    f"{wip_count}/{limit} iniciativas activas. "
                    "Mueve o completa una iniciativa existente antes de agregar otra."
                ),
            )

    # ── Apply move ────────────────────────────────────────────────────────
    await db.execute(
        text("""
            UPDATE core.dgi_initiative
            SET status_id  = :status_id,
                wip_column = :wip_column
            WHERE id = :id
        """),
        {
            "id": initiative_id_str,
            "status_id": str(target_status_id),
            "wip_column": target_status,
        },
    )
    await db.commit()

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
    )
