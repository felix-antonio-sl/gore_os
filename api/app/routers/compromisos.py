import math
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import WRITE_OPERATIONAL_ROLES, PERSONAL_SCOPE_ROLES
from app.core.audit import record_event
from app.schemas.compromiso import CompromisoCreate, CompromisoListItem, CompromisoDetail, HistoryEntry, StateChangeRequest, CompromisoUpdate

router = APIRouter(prefix="/api/compromisos", tags=["compromisos"])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ADMIN_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"}
MANAGER_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "GOBERNADOR", "JEFE_DEPARTAMENTO"}


def _require_roles(user: dict, *roles: str) -> None:
    if user["role_code"] not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")


async def _get_compromiso_or_404(compromiso_id: UUID, db: AsyncSession) -> dict:
    result = await db.execute(
        text("""
            SELECT oc.id, oc.code, oc.description, oc.ipr_id, oc.problem_id,
                   oc.responsible_id, oc.division_id, oc.due_date, oc.observations,
                   oc.completed_at, oc.verified_by_id, oc.verified_at,
                   oc.created_at, oc.updated_at,
                   state_cat.code      AS state,
                   state_cat.label     AS state_label,
                   type_cat.code       AS commitment_type,
                   type_cat.name       AS commitment_type_label,
                   ipr.codigo_bip      AS ipr_codigo_bip,
                   ipr.name            AS ipr_name,
                   (p.names || ' ' || p.paternal_surname) AS responsible_name,
                   org.name            AS division_name,
                   (vp.names || ' ' || vp.paternal_surname) AS verified_by_name,
                   (oc.due_date - CURRENT_DATE) AS days_remaining
            FROM core.operational_commitment oc
            JOIN ref.category state_cat ON oc.state_id = state_cat.id
            JOIN ref.operational_commitment_type type_cat ON oc.commitment_type_id = type_cat.id
            LEFT JOIN core.ipr ipr ON oc.ipr_id = ipr.id
            LEFT JOIN core."user" ru ON oc.responsible_id = ru.id
            LEFT JOIN core.person p ON ru.person_id = p.id
            LEFT JOIN core.organization org ON oc.division_id = org.id
            LEFT JOIN core."user" vu ON oc.verified_by_id = vu.id
            LEFT JOIN core.person vp ON vu.person_id = vp.id
            WHERE oc.id = :id AND oc.deleted_at IS NULL
        """),
        {"id": str(compromiso_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compromiso no encontrado")
    return dict(row)


async def _get_history(compromiso_id: UUID, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        text("""
            SELECT ch.id, ch.changed_at, ch.comment,
                   prev_cat.code  AS previous_state,
                   new_cat.code   AS new_state,
                   (p.names || ' ' || p.paternal_surname) AS changed_by_name
            FROM core.commitment_history ch
            JOIN ref.category new_cat ON ch.new_state_id = new_cat.id
            LEFT JOIN ref.category prev_cat ON ch.previous_state_id = prev_cat.id
            LEFT JOIN core."user" cu ON ch.changed_by_id = cu.id
            LEFT JOIN core.person p ON cu.person_id = p.id
            WHERE ch.commitment_id = :cid
            ORDER BY ch.changed_at DESC
        """),
        {"cid": str(compromiso_id)},
    )
    return [dict(r) for r in result.mappings().all()]


async def _next_oc_code(db: AsyncSession) -> str:
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('oc_code'))"))
    result = await db.execute(
        text("""
            SELECT MAX(CAST(SUBSTRING(code FROM 4) AS INTEGER)) AS max_seq
            FROM core.operational_commitment
            WHERE code ~ '^OC-[0-9]+$'
        """)
    )
    row = result.mappings().first()
    next_seq = (row["max_seq"] or 0) + 1
    return f"OC-{next_seq:05d}"


# ---------------------------------------------------------------------------
# GET /api/compromisos — List (paginated, filtered)
# ---------------------------------------------------------------------------

@router.get("")
async def list_compromisos(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    state: str | None = None,
    division_id: UUID | None = None,
    responsible_id: UUID | None = None,
    ipr_id: UUID | None = None,
    overdue: bool | None = None,
    mine: bool | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    role = user["role_code"]
    params: dict = {}

    # Role-based defaults
    effective_division_id = division_id
    effective_responsible_id = responsible_id

    if mine:
        effective_responsible_id = user["id"]
    else:
        if role == "JEFE_DIVISION" and not division_id:
            effective_division_id = user.get("division_id")
        if role in PERSONAL_SCOPE_ROLES and not responsible_id:
            effective_responsible_id = user["id"]

    conditions = ["oc.deleted_at IS NULL"]

    if state:
        conditions.append(
            "state_cat.code = :state"
        )
        params["state"] = state

    if effective_division_id:
        conditions.append("oc.division_id = :division_id")
        params["division_id"] = str(effective_division_id)

    if effective_responsible_id:
        conditions.append("oc.responsible_id = :responsible_id")
        params["responsible_id"] = str(effective_responsible_id)

    if ipr_id:
        conditions.append("oc.ipr_id = :ipr_id")
        params["ipr_id"] = str(ipr_id)

    if date_from:
        conditions.append("oc.due_date >= :date_from")
        params["date_from"] = str(date_from)
    if date_to:
        conditions.append("oc.due_date <= :date_to")
        params["date_to"] = str(date_to)

    if overdue is True:
        conditions.append(
            "(oc.due_date < CURRENT_DATE AND state_cat.code NOT IN ('VERIFICADO', 'CANCELADO'))"
        )
    elif overdue is False:
        conditions.append(
            "NOT (oc.due_date < CURRENT_DATE AND state_cat.code NOT IN ('VERIFICADO', 'CANCELADO'))"
        )

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core.operational_commitment oc
        JOIN ref.category state_cat ON oc.state_id = state_cat.id
        JOIN ref.operational_commitment_type type_cat ON oc.commitment_type_id = type_cat.id
        LEFT JOIN core.ipr ipr ON oc.ipr_id = ipr.id
        LEFT JOIN core."user" ru ON oc.responsible_id = ru.id
        LEFT JOIN core.person p ON ru.person_id = p.id
        LEFT JOIN core.organization org ON oc.division_id = org.id
        WHERE {where_clause}
    """

    count_result = await db.execute(
        text(f"SELECT COUNT(*) AS total {base_query}"), params
    )
    total = count_result.scalar() or 0

    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows_result = await db.execute(
        text(f"""
            SELECT
                oc.id,
                oc.code,
                oc.description,
                oc.ipr_id,
                ipr.codigo_bip                              AS ipr_codigo_bip,
                ipr.name                                    AS ipr_name,
                type_cat.name                               AS commitment_type,
                (p.names || ' ' || p.paternal_surname)      AS responsible_name,
                oc.responsible_id,
                org.name                                    AS division_name,
                oc.due_date,
                state_cat.code                              AS state,
                state_cat.label                             AS state_label,
                (oc.due_date - CURRENT_DATE)                AS days_remaining,
                oc.completed_at,
                oc.verified_at
            {base_query}
            ORDER BY
                CASE
                    WHEN oc.due_date < CURRENT_DATE
                         AND state_cat.code NOT IN ('VERIFICADO', 'CANCELADO')
                    THEN 0 ELSE 1
                END ASC,
                oc.due_date ASC
            LIMIT :limit OFFSET :offset
        """),
        params,
    )
    rows = rows_result.mappings().all()
    items = [CompromisoListItem(**dict(r)) for r in rows]
    total_pages = math.ceil(total / page_size) if page_size else 0

    return {
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------------------
# GET /api/compromisos/{id} — Detail with history
# ---------------------------------------------------------------------------

@router.get("/{compromiso_id}")
async def get_compromiso(
    compromiso_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_compromiso_or_404(compromiso_id, db)
    history_rows = await _get_history(compromiso_id, db)
    history = [
        HistoryEntry(
            id=h["id"],
            previous_state=h["previous_state"],
            new_state=h["new_state"],
            changed_by_name=h["changed_by_name"],
            comment=h["comment"],
            changed_at=h["changed_at"],
        )
        for h in history_rows
    ]
    detail = CompromisoDetail(
        id=row["id"],
        code=row["code"],
        description=row["description"],
        ipr_id=row["ipr_id"],
        ipr_codigo_bip=row["ipr_codigo_bip"],
        ipr_name=row["ipr_name"],
        problem_id=row["problem_id"],
        commitment_type=row["commitment_type"],
        commitment_type_label=row["commitment_type_label"],
        responsible_id=row["responsible_id"],
        responsible_name=row["responsible_name"],
        division_id=row["division_id"],
        division_name=row["division_name"],
        due_date=row["due_date"],
        state=row["state"],
        state_label=row["state_label"],
        days_remaining=row["days_remaining"],
        observations=row["observations"],
        completed_at=row["completed_at"],
        verified_by_name=row["verified_by_name"],
        verified_at=row["verified_at"],
        created_at=row["created_at"],
        history=history,
    )
    return detail.model_dump()


# ---------------------------------------------------------------------------
# POST /api/compromisos — Create
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_compromiso(
    data: CompromisoCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION",
                   "JEFE_DEPARTAMENTO", "JEFE_UNIDAD", "ANALISTA")

    code = await _next_oc_code(db)

    # Resolve division_id: if not provided, take from the responsible user's division
    division_id = data.division_id
    if not division_id:
        div_result = await db.execute(
            text("SELECT division_id FROM core.\"user\" WHERE id = :uid AND deleted_at IS NULL"),
            {"uid": str(data.responsible_id)},
        )
        div_row = div_result.mappings().first()
        if div_row:
            division_id = div_row["division_id"]

    try:
        result = await db.execute(
            text("""
                INSERT INTO core.operational_commitment (
                    code, ipr_id, problem_id, commitment_type_id, description,
                    responsible_id, division_id, due_date, observations,
                    state_id, created_by_id, updated_by_id
                ) VALUES (
                    :code, :ipr_id, :problem_id, :commitment_type_id, :description,
                    :responsible_id, :division_id, :due_date, :observations,
                    (SELECT id FROM ref.category WHERE scheme = 'commitment_state' AND code = 'PENDIENTE'),
                    :created_by_id, :created_by_id
                )
                RETURNING id, code
            """),
            {
                "code": code,
                "ipr_id": str(data.ipr_id) if data.ipr_id else None,
                "problem_id": str(data.problem_id) if data.problem_id else None,
                "commitment_type_id": str(data.commitment_type_id),
                "description": data.description,
                "responsible_id": str(data.responsible_id),
                "division_id": str(division_id) if division_id else None,
                "due_date": data.due_date,
                "observations": data.observations,
                "created_by_id": str(user["id"]),
            },
        )
        row = result.mappings().first()
        await record_event(
            db, "COMPROMISO", "core.operational_commitment", row["id"],
            actor_id=user["id"],
            data={"code": row["code"]},
        )
        await db.commit()
        return {"id": str(row["id"]), "code": row["code"]}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un compromiso con datos duplicados")
    except Exception:
        await db.rollback()
        raise


# ---------------------------------------------------------------------------
# PATCH /api/compromisos/{id} — Update fields
# ---------------------------------------------------------------------------

_PATCH_ALLOWLIST = {"observations", "due_date", "description", "responsible_id"}


@router.patch("/{compromiso_id}")
async def update_compromiso(
    compromiso_id: UUID,
    data: CompromisoUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, *WRITE_OPERATIONAL_ROLES)
    await _get_compromiso_or_404(compromiso_id, db)

    updates = {k: v for k, v in data.model_dump(exclude_none=True).items() if k in _PATCH_ALLOWLIST}
    if not updates:
        return {"message": "Sin cambios"}

    # responsible_id changes require MANAGER_ROLES
    if "responsible_id" in updates:
        _require_roles(user, *MANAGER_ROLES)
        # Auto-resolve division_id from new responsible
        div_result = await db.execute(
            text('SELECT division_id FROM core."user" WHERE id = :uid AND deleted_at IS NULL'),
            {"uid": str(updates["responsible_id"])},
        )
        div_row = div_result.mappings().first()
        if div_row and div_row["division_id"]:
            updates["division_id"] = str(div_row["division_id"])

    set_clauses = []
    params: dict = {"id": str(compromiso_id), "updated_by": str(user["id"])}
    for field, value in updates.items():
        set_clauses.append(f"{field} = :{field}")
        params[field] = str(value) if value is not None else None

    set_clauses.append("updated_by_id = :updated_by")
    set_clauses.append("updated_at = NOW()")

    await db.execute(
        text(f"UPDATE core.operational_commitment SET {', '.join(set_clauses)} WHERE id = :id AND deleted_at IS NULL"),
        params,
    )
    await db.commit()

    updated = await _get_compromiso_or_404(compromiso_id, db)
    return CompromisoDetail(
        **{k: updated[k] for k in updated if k != "history"},
        history=[],
    ).model_dump()


# ---------------------------------------------------------------------------
# POST /api/compromisos/{id}/completar
# ---------------------------------------------------------------------------

@router.post("/{compromiso_id}/completar")
async def completar(
    compromiso_id: UUID,
    body: StateChangeRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_compromiso_or_404(compromiso_id, db)

    # Only the responsible user or admins can complete
    is_admin = user["role_code"] in ADMIN_ROLES
    is_responsible = str(user["id"]) == str(row["responsible_id"])
    if not is_admin and not is_responsible:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el responsable o un administrador puede completar este compromiso",
        )

    if row["state"] in ("VERIFICADO", "CANCELADO"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede completar un compromiso en estado {row['state']}",
        )

    await db.execute(
        text("""
            UPDATE core.operational_commitment
            SET state_id = (SELECT id FROM ref.category WHERE scheme = 'commitment_state' AND code = 'COMPLETADO'),
                completed_at = NOW(),
                observations = COALESCE(:observations, observations),
                updated_by_id = :updated_by,
                updated_at = NOW()
            WHERE id = :id AND deleted_at IS NULL
        """),
        {
            "id": str(compromiso_id),
            "observations": body.observations,
            "updated_by": str(user["id"]),
        },
    )
    await record_event(
        db, "STATE_TRANSITION", "core.operational_commitment", compromiso_id,
        actor_id=user["id"],
        data={"from": row["state"], "to": "COMPLETADO"},
    )
    await db.commit()
    return {"message": "Compromiso marcado como completado"}


# ---------------------------------------------------------------------------
# POST /api/compromisos/{id}/verificar
# ---------------------------------------------------------------------------

@router.post("/{compromiso_id}/verificar")
async def verificar(
    compromiso_id: UUID,
    body: StateChangeRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_compromiso_or_404(compromiso_id, db)
    role = user["role_code"]

    # JEFE_DIVISION may only verify commitments in their own division
    if role == "JEFE_DIVISION":
        user_div = str(user.get("division_id") or "")
        comp_div = str(row.get("division_id") or "")
        if not user_div or user_div != comp_div:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puede verificar compromisos de su propia división",
            )
    elif role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sin permisos para verificar compromisos",
        )

    if row["state"] != "COMPLETADO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se puede verificar un compromiso en estado COMPLETADO",
        )

    await db.execute(
        text("""
            UPDATE core.operational_commitment
            SET state_id      = (SELECT id FROM ref.category WHERE scheme = 'commitment_state' AND code = 'VERIFICADO'),
                verified_by_id = :verified_by,
                verified_at    = NOW(),
                updated_by_id  = :updated_by,
                updated_at     = NOW()
            WHERE id = :id AND deleted_at IS NULL
        """),
        {
            "id": str(compromiso_id),
            "verified_by": str(user["id"]),
            "updated_by": str(user["id"]),
        },
    )
    await record_event(
        db, "STATE_TRANSITION", "core.operational_commitment", compromiso_id,
        actor_id=user["id"],
        data={"from": "COMPLETADO", "to": "VERIFICADO"},
    )
    await db.commit()
    return {"message": "Compromiso verificado"}


# ---------------------------------------------------------------------------
# POST /api/compromisos/{id}/devolver
# ---------------------------------------------------------------------------

@router.post("/{compromiso_id}/devolver")
async def devolver(
    compromiso_id: UUID,
    body: StateChangeRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION")

    if not body.observations:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Se requiere el motivo de devolución en el campo 'observations'",
        )

    row = await _get_compromiso_or_404(compromiso_id, db)

    # JEFE_DIVISION may only return commitments in their own division
    if user["role_code"] == "JEFE_DIVISION":
        user_div = str(user.get("division_id") or "")
        comp_div = str(row.get("division_id") or "")
        if not user_div or user_div != comp_div:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puede devolver compromisos de su propia división",
            )

    if row["state"] != "COMPLETADO":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se puede devolver un compromiso en estado COMPLETADO",
        )

    # The trigger trg_commitment_history will capture the state change and
    # use updated_by_id as changed_by_id. We store the motivo in observations.
    await db.execute(
        text("""
            UPDATE core.operational_commitment
            SET state_id      = (SELECT id FROM ref.category WHERE scheme = 'commitment_state' AND code = 'EN_PROGRESO'),
                completed_at  = NULL,
                observations  = :observations,
                updated_by_id = :updated_by,
                updated_at    = NOW()
            WHERE id = :id AND deleted_at IS NULL
        """),
        {
            "id": str(compromiso_id),
            "observations": body.observations,
            "updated_by": str(user["id"]),
        },
    )
    await record_event(
        db, "STATE_TRANSITION", "core.operational_commitment", compromiso_id,
        actor_id=user["id"],
        data={"from": "COMPLETADO", "to": "EN_PROGRESO", "reason": body.observations},
    )
    await db.commit()
    return {"message": "Compromiso devuelto para corrección"}
