import math
from datetime import date as date_type
from fastapi import APIRouter, Depends, Query, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import WRITE_OPERATIONAL_ROLES
from app.schemas.common import PaginatedResponse
from app.schemas.acto import ActoListItem, ActoDetail, ActoCreate, ActoUpdate, ActoHistoryEntry

router = APIRouter(prefix="/api/actos", tags=["actos"])

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_ACT_FIELD_ALLOWLIST = {
    "state_id", "subject", "act_number", "issuer_id",
    "requires_cgr", "cgr_outcome_id",
}

_RES_FIELDS = {"ipr_id", "agreement_id", "budget_amount", "resolution_type_id", "resolution_subtype_id"}

# Terminal act states — cannot transition out of these
_TERMINAL_STATES = {"TOMADO_RAZON", "RECHAZADO_CGR", "ANULADO"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _require_roles(user: dict, *roles: str) -> None:
    if user["role_code"] not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")


_BASE_SELECT = """
    SELECT
        a.id,
        a.act_number,
        a.subject,
        a.issued_at,
        a.effective_from,
        a.effective_to,
        a.requires_cgr,
        a.cgr_submitted_at,
        a.cgr_resolved_at,
        a.created_at,
        at_cat.code   AS act_type,
        at_cat.label  AS act_type_label,
        st_cat.code   AS state,
        st_cat.label  AS state_label,
        org.name      AS issuer_name,
        sr.name       AS signer_name,
        cgr_cat.code  AS cgr_outcome,
        cgr_cat.label AS cgr_outcome_label,
        -- Resolution fields (NULL if no resolution)
        rt_cat.code   AS resolution_type,
        rt_cat.label  AS resolution_type_label,
        rst_cat.code  AS resolution_subtype,
        rst_cat.label AS resolution_subtype_label,
        r.ipr_id,
        ipr.codigo_bip AS ipr_codigo_bip,
        r.agreement_id,
        ag.agreement_number,
        r.budget_amount
    FROM core.administrative_act a
    JOIN ref.category at_cat ON at_cat.id = a.act_type_id
    LEFT JOIN ref.category st_cat ON st_cat.id = a.state_id
    LEFT JOIN core.organization org ON org.id = a.issuer_id
    LEFT JOIN meta.role sr ON sr.id = a.signer_id
    LEFT JOIN ref.category cgr_cat ON cgr_cat.id = a.cgr_outcome_id
    LEFT JOIN core.resolution r ON r.administrative_act_id = a.id AND r.deleted_at IS NULL
    LEFT JOIN ref.category rt_cat ON rt_cat.id = r.resolution_type_id
    LEFT JOIN ref.category rst_cat ON rst_cat.id = r.resolution_subtype_id
    LEFT JOIN core.ipr ipr ON ipr.id = r.ipr_id
    LEFT JOIN core.agreement ag ON ag.id = r.agreement_id
"""


async def _get_acto_or_404(acto_id: UUID, db: AsyncSession) -> dict:
    result = await db.execute(
        text(f"{_BASE_SELECT} WHERE a.id = :id AND a.deleted_at IS NULL"),
        {"id": str(acto_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acto administrativo no encontrado")
    return dict(row)


async def _get_act_history(act_id: UUID, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        text("""
            SELECT h.id, h.changed_at, h.comment,
                   prev_cat.code AS previous_state,
                   new_cat.code  AS new_state,
                   (p.names || ' ' || p.paternal_surname) AS changed_by_name
            FROM core.administrative_act_history h
            JOIN ref.category new_cat ON h.new_state_id = new_cat.id
            LEFT JOIN ref.category prev_cat ON h.previous_state_id = prev_cat.id
            LEFT JOIN core."user" cu ON h.changed_by_id = cu.id
            LEFT JOIN core.person p ON cu.person_id = p.id
            WHERE h.act_id = :act_id
            ORDER BY h.changed_at DESC
        """),
        {"act_id": str(act_id)},
    )
    return [dict(r) for r in result.mappings().all()]


async def _next_act_number(db: AsyncSession) -> str:
    from datetime import date
    year = date.today().year
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('act_number'))"))
    result = await db.execute(
        text("""
            SELECT MAX(CAST(SUBSTRING(act_number FROM 10) AS INTEGER)) AS max_seq
            FROM core.administrative_act
            WHERE act_number ~ :pattern
        """),
        {"pattern": f"^ACT-{year}-[0-9]+$"},
    )
    row = result.mappings().first()
    next_seq = ((row["max_seq"] or 0) + 1) if row else 1
    return f"ACT-{year}-{next_seq:05d}"


async def _validate_state_transition(
    acto_id: UUID,
    new_state_id: str,
    db: AsyncSession,
) -> tuple[str, str]:
    """Validate state transition. Returns (current_code, new_code) or raises HTTP 409."""
    result = await db.execute(
        text("""
            SELECT
                cur.code             AS current_code,
                cur.valid_transitions AS valid_transitions,
                nxt.code             AS new_code
            FROM core.administrative_act a
            JOIN ref.category cur ON cur.id = a.state_id
            JOIN ref.category nxt ON nxt.id = :new_state_id
            WHERE a.id = :id AND a.deleted_at IS NULL
        """),
        {"id": str(acto_id), "new_state_id": new_state_id},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acto no encontrado")

    current_code = row["current_code"]
    new_code = row["new_code"]
    valid = row["valid_transitions"] or []

    # ANULADO is cross-cutting: allowed from any non-terminal state
    if new_code == "ANULADO" and current_code not in _TERMINAL_STATES:
        return current_code, new_code

    if new_code not in valid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Transicion invalida: {current_code} -> {new_code}. Destinos validos: {', '.join(valid) if valid else '(estado terminal)'}",
        )

    return current_code, new_code


# ---------------------------------------------------------------------------
# GET /api/actos — List (paginated, filtered)
# ---------------------------------------------------------------------------

@router.get("", response_model=PaginatedResponse)
async def list_actos(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    state: str | None = None,
    act_type: str | None = None,
    search: str | None = None,
    ipr_id: UUID | None = None,
    requires_cgr: bool | None = None,
):
    params: dict = {}
    conditions = ["a.deleted_at IS NULL"]

    if state:
        conditions.append("st_cat.code = :state")
        params["state"] = state

    if act_type:
        conditions.append("at_cat.code = :act_type")
        params["act_type"] = act_type

    if search:
        conditions.append("(a.act_number ILIKE :search OR a.subject ILIKE :search)")
        params["search"] = f"%{search}%"

    if ipr_id:
        conditions.append("r.ipr_id = :ipr_id")
        params["ipr_id"] = str(ipr_id)

    if requires_cgr is not None:
        conditions.append("a.requires_cgr = :requires_cgr")
        params["requires_cgr"] = requires_cgr

    where_clause = " AND ".join(conditions)

    # Count
    count_result = await db.execute(
        text(f"""
            SELECT COUNT(*) AS total
            FROM core.administrative_act a
            JOIN ref.category at_cat ON at_cat.id = a.act_type_id
            LEFT JOIN ref.category st_cat ON st_cat.id = a.state_id
            LEFT JOIN core.resolution r ON r.administrative_act_id = a.id AND r.deleted_at IS NULL
            WHERE {where_clause}
        """),
        params,
    )
    total = count_result.scalar() or 0

    # Rows
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows_result = await db.execute(
        text(f"""
            {_BASE_SELECT}
            WHERE {where_clause}
            ORDER BY a.issued_at DESC NULLS LAST
            LIMIT :limit OFFSET :offset
        """),
        params,
    )
    rows = rows_result.mappings().all()
    items = [ActoListItem(**dict(r)) for r in rows]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0,
    )


# ---------------------------------------------------------------------------
# GET /api/actos/{id} — Detail
# ---------------------------------------------------------------------------

@router.get("/{acto_id}", response_model=ActoDetail)
async def get_acto(
    acto_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_acto_or_404(acto_id, db)
    history = await _get_act_history(acto_id, db)
    return ActoDetail(**row, history=[ActoHistoryEntry(**h) for h in history])


# ---------------------------------------------------------------------------
# POST /api/actos — Create act (+ resolution if RESOLUCION type)
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_acto(
    body: ActoCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, *WRITE_OPERATIONAL_ROLES)

    # Resolve act_type code to check if RESOLUCION
    type_result = await db.execute(
        text("SELECT code FROM ref.category WHERE id = :id AND scheme = 'act_type'"),
        {"id": str(body.act_type_id)},
    )
    type_code = type_result.scalar()
    if not type_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de acto invalido")

    # Get BORRADOR state for default
    borrador_result = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'act_state' AND code = 'BORRADOR'"),
    )
    borrador_id = str(borrador_result.scalar())

    act_number = body.act_number or await _next_act_number(db)

    # Insert administrative_act
    try:
        act_result = await db.execute(
            text("""
                INSERT INTO core.administrative_act (
                    act_number, act_type_id, subject, issuer_id,
                    issued_at, state_id, requires_cgr,
                    created_by_id, created_at, updated_at
                ) VALUES (
                    :act_number, :act_type_id, :subject, :issuer_id,
                    :issued_at, :state_id, :requires_cgr,
                    :created_by_id, NOW(), NOW()
                )
                RETURNING id, act_number
            """),
            {
                "act_number": act_number,
                "act_type_id": str(body.act_type_id),
                "subject": body.subject,
                "issuer_id": str(body.issuer_id) if body.issuer_id else None,
                "issued_at": body.issued_at,
                "state_id": borrador_id,
                "requires_cgr": body.requires_cgr,
                "created_by_id": str(user["id"]),
            },
        )
        act_row = act_result.mappings().first()
        act_id = str(act_row["id"])

        # Auto-create resolution if act_type is RESOLUCION
        resolution_id = None
        if type_code == "RESOLUCION":
            if not body.resolution_type_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="resolution_type_id requerido para actos tipo RESOLUCION",
                )
            res_result = await db.execute(
                text("""
                    INSERT INTO core.resolution (
                        administrative_act_id, resolution_type_id, resolution_subtype_id,
                        ipr_id, agreement_id, budget_amount,
                        created_by_id, created_at, updated_at
                    ) VALUES (
                        :act_id, :resolution_type_id, :resolution_subtype_id,
                        :ipr_id, :agreement_id, :budget_amount,
                        :created_by_id, NOW(), NOW()
                    )
                    RETURNING id
                """),
                {
                    "act_id": act_id,
                    "resolution_type_id": str(body.resolution_type_id),
                    "resolution_subtype_id": str(body.resolution_subtype_id) if body.resolution_subtype_id else None,
                    "ipr_id": str(body.ipr_id) if body.ipr_id else None,
                    "agreement_id": str(body.agreement_id) if body.agreement_id else None,
                    "budget_amount": body.budget_amount,
                    "created_by_id": str(user["id"]),
                },
            )
            resolution_id = str(res_result.mappings().first()["id"])

        await db.commit()
        return {"id": act_id, "act_number": act_row["act_number"], "resolution_id": resolution_id}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un acto con ese número")
        raise


# ---------------------------------------------------------------------------
# PATCH /api/actos/{id} — Update fields + state transitions
# ---------------------------------------------------------------------------

@router.patch("/{acto_id}")
async def update_acto(
    acto_id: UUID,
    body: ActoUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, *WRITE_OPERATIONAL_ROLES)
    await _get_acto_or_404(acto_id, db)

    payload = body.model_dump(exclude_none=True)
    if not payload:
        return {"message": "Sin cambios"}

    # Split into act fields and resolution fields
    act_updates = {k: v for k, v in payload.items() if k in _ACT_FIELD_ALLOWLIST}
    res_updates = {k: v for k, v in payload.items() if k in _RES_FIELDS}

    # Validate state transition if state_id is being changed
    if "state_id" in act_updates:
        new_state_id = str(act_updates["state_id"])
        current_code, new_code = await _validate_state_transition(acto_id, new_state_id, db)

        # CGR tracking: auto-set timestamps on relevant transitions
        if new_code == "TRAMITADO":
            # Check if requires_cgr and set cgr_submitted_at
            check = await db.execute(
                text("SELECT requires_cgr FROM core.administrative_act WHERE id = :id"),
                {"id": str(acto_id)},
            )
            if check.mappings().first()["requires_cgr"]:
                act_updates["cgr_submitted_at"] = date_type.today()
                # Add to allowlist for this request
        elif new_code in ("TOMADO_RAZON", "RECHAZADO_CGR"):
            act_updates["cgr_resolved_at"] = date_type.today()

    # Convert UUIDs to string for act updates
    for k in ("state_id", "issuer_id", "cgr_outcome_id"):
        if k in act_updates:
            act_updates[k] = str(act_updates[k])

    # Update administrative_act
    if act_updates:
        set_clauses = ", ".join(f"{k} = :{k}" for k in act_updates)
        act_updates["id"] = str(acto_id)
        act_updates["updated_by_id"] = str(user["id"])
        await db.execute(
            text(f"UPDATE core.administrative_act SET {set_clauses}, updated_at = NOW(), updated_by_id = :updated_by_id WHERE id = :id"),
            act_updates,
        )

    # Update resolution (if resolution fields present)
    if res_updates:
        # Check resolution exists
        res_check = await db.execute(
            text("SELECT id FROM core.resolution WHERE administrative_act_id = :act_id AND deleted_at IS NULL"),
            {"act_id": str(acto_id)},
        )
        res_row = res_check.mappings().first()
        if res_row:
            # Convert UUIDs
            for k in ("ipr_id", "agreement_id", "resolution_type_id", "resolution_subtype_id"):
                if k in res_updates:
                    res_updates[k] = str(res_updates[k])

            res_set = ", ".join(f"{k} = :{k}" for k in res_updates)
            res_updates["res_id"] = str(res_row["id"])
            res_updates["updated_by_id"] = str(user["id"])
            await db.execute(
                text(f"UPDATE core.resolution SET {res_set}, updated_at = NOW(), updated_by_id = :updated_by_id WHERE id = :res_id"),
                res_updates,
            )

    await db.commit()
    return {"message": "Actualizado correctamente"}


# ---------------------------------------------------------------------------
# GET /api/actos/{id}/transiciones — Valid state transitions
# ---------------------------------------------------------------------------

@router.get("/{acto_id}/transiciones")
async def get_valid_transitions(
    acto_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("""
            SELECT
                cur.code             AS current_code,
                cur.valid_transitions AS valid_transitions
            FROM core.administrative_act a
            JOIN ref.category cur ON cur.id = a.state_id
            WHERE a.id = :id AND a.deleted_at IS NULL
        """),
        {"id": str(acto_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acto no encontrado")

    current_code = row["current_code"]
    valid_codes = list(row["valid_transitions"] or [])

    # ANULADO cross-cutting: add if current state is not terminal
    if current_code not in _TERMINAL_STATES and "ANULADO" not in valid_codes:
        valid_codes.append("ANULADO")

    if not valid_codes:
        return []

    dest_result = await db.execute(
        text("""
            SELECT id, code, label
            FROM ref.category
            WHERE scheme = 'act_state' AND code = ANY(:codes)
            ORDER BY label
        """),
        {"codes": valid_codes},
    )
    return [dict(r) for r in dest_result.mappings().all()]
