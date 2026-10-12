"""Decision context and authorized follow-up for the work inbox."""

import json
import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from app.core.audit import record_event
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import DGI_ROLES

from app.schemas.dgi import ARDecisionCreate, ARDecisionUpdate, ARDecisionItem

router = APIRouter(prefix="/api/dgi/coordination", tags=["dgi"])


_DGI_WRITE_ROLES = {"JEFE_DGI", "ESP_CONTROL_GESTION"}
_READ_ROLES = {*DGI_ROLES, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"}


def _require_dgi_read(user: dict) -> None:
    if user.get("role_code") not in _READ_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de lectura restringido a roles DGI y ejecutivos",
        )


def _require_dgi_write(user: dict) -> None:
    if user.get("role_code") not in _DGI_WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo JEFE_DGI o ESP_CONTROL_GESTION pueden gestionar coordinación",
        )


async def _get_category_id(db: AsyncSession, scheme: str, code: str) -> str:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = :scheme AND code = :code"),
        {"scheme": scheme, "code": code},
    )).mappings().first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Código inválido para {scheme}: {code}",
        )
    return str(row["id"])


_DEC_COLS = """
    d.id,
    d.description,
    dt.code   AS decision_type,
    dt.label  AS decision_type_label,
    st.code   AS status,
    st.label  AS status_label,
    COALESCE(st.valid_transitions, '[]'::jsonb) AS valid_transitions,
    d.due_date,
    d.context,
    d.responsible_id,
    p.names || ' ' || p.paternal_surname AS responsible_name,
    d.resolved_at,
    d.created_at
"""

_DEC_FROM = """
    FROM core.dgi_ar_decision d
    JOIN ref.category dt ON dt.id = d.decision_type_id
    JOIN ref.category st ON st.id = d.status_id
    LEFT JOIN core."user" u ON u.id = d.responsible_id
    LEFT JOIN core.person p ON p.id = u.person_id
"""


def _row_to_decision(r: dict, user: dict) -> ARDecisionItem:
    return ARDecisionItem(
        id=r["id"],
        description=r["description"],
        decision_type=r["decision_type"],
        decision_type_label=r["decision_type_label"],
        status=r["status"],
        status_label=r["status_label"],
        due_date=r["due_date"],
        context=r["context"],
        responsible_name=r["responsible_name"],
        resolved_at=r["resolved_at"],
        created_at=r["created_at"],
        responsible_id=r["responsible_id"],
        allowed_statuses=r["valid_transitions"] if user["role_code"] in _DGI_WRITE_ROLES else [],
        can_edit=user["role_code"] in _DGI_WRITE_ROLES,
    )

@router.get("/ar/decisions")
async def list_ar_decisions(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
    type_filter: str | None = Query(None, alias="type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    _require_dgi_read(user)

    conditions = ["d.deleted_at IS NULL"]
    params: dict = {}

    if status_filter:
        conditions.append("st.code = :status_filter")
        params["status_filter"] = status_filter.upper()

    if type_filter:
        conditions.append("dt.code = :type_filter")
        params["type_filter"] = type_filter.upper()

    where = " AND ".join(conditions)

    count_result = await db.execute(
        text(f"SELECT COUNT(*) {_DEC_FROM} WHERE {where}"), params,
    )
    total = count_result.scalar() or 0
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(text(f"""
        SELECT {_DEC_COLS} {_DEC_FROM}
        WHERE {where}
        ORDER BY d.created_at DESC
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    items = [_row_to_decision(dict(r), user).model_dump() for r in rows]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }

@router.get("/ar/decisions/{decision_id}", response_model=ARDecisionItem)
async def get_ar_decision(decision_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    _require_dgi_read(user)
    row = (await db.execute(
        text(f"SELECT {_DEC_COLS} {_DEC_FROM} WHERE d.id = :id AND d.deleted_at IS NULL"),
        {"id": str(decision_id)},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Decisión no encontrada")
    return _row_to_decision(dict(row), user)


@router.post("/ar/decisions", status_code=status.HTTP_201_CREATED,
             response_model=ARDecisionItem)
async def create_ar_decision(
    body: ARDecisionCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi_write(user)

    type_id = await _get_category_id(db, "dgi_ar_decision_type", body.decision_type.upper())
    status_id = await _get_category_id(db, "dgi_ar_decision_status", "PENDIENTE")

    result = await db.execute(
        text("""
            INSERT INTO core.dgi_ar_decision
                (description, decision_type_id, status_id, due_date, context,
                 responsible_id, created_by_id)
            VALUES
                (:description, :type_id, :status_id, :due_date, :context,
                 :responsible_id, :created_by_id)
            RETURNING id
        """),
        {
            "description": body.description,
            "type_id": type_id,
            "status_id": status_id,
            "due_date": body.due_date,
            "context": body.context,
            "responsible_id": str(body.responsible_id) if body.responsible_id else None,
            "created_by_id": str(user["id"]),
        },
    )
    new_id = str(result.scalar())
    await record_event(db, "DECISION_CREATED", "core.dgi_ar_decision", new_id, user["id"],
                       {"decision_type": body.decision_type})
    await db.commit()

    row = (await db.execute(
        text(f"SELECT {_DEC_COLS} {_DEC_FROM} WHERE d.id = :id"),
        {"id": new_id},
    )).mappings().first()
    return _row_to_decision(dict(row), user)

@router.patch("/ar/decisions/{decision_id}", response_model=ARDecisionItem)
async def update_ar_decision(
    decision_id: UUID,
    body: ARDecisionUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi_write(user)

    decision_id_str = str(decision_id)

    existing = (await db.execute(
        text(f"SELECT d.id, st.code AS current_status {_DEC_FROM} WHERE d.id = :id AND d.deleted_at IS NULL"),
        {"id": decision_id_str},
    )).mappings().first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decisión no encontrada")

    updates: list[str] = []
    params: dict = {"id": decision_id_str}

    body_data = body.model_dump(exclude_none=True)

    # Field updates
    for field in ("description", "due_date", "context"):
        if field in body_data:
            updates.append(f"{field} = :{field}")
            params[field] = body_data[field]

    if "responsible_id" in body_data:
        updates.append("responsible_id = :responsible_id")
        params["responsible_id"] = str(body_data["responsible_id"])

    # Status transition (DB trigger validates)
    if body.status is not None:
        new_status_id = await _get_category_id(db, "dgi_ar_decision_status", body.status.upper())
        updates.append("status_id = :new_status_id")
        params["new_status_id"] = new_status_id

    if not updates:
        row = (await db.execute(
            text(f"SELECT {_DEC_COLS} {_DEC_FROM} WHERE d.id = :id"),
            {"id": decision_id_str},
        )).mappings().first()
        return _row_to_decision(dict(row), user)

    updates.append("updated_at = NOW()")
    set_clause = ", ".join(updates)

    try:
        await db.execute(
            text(f"UPDATE core.dgi_ar_decision SET {set_clause} WHERE id = :id"),
            params,
        )
        if body.status is not None:
            await record_event(db, "DECISION_STATUS_CHANGE", "core.dgi_ar_decision",
                               decision_id, user["id"],
                               {"old_status": existing["current_status"], "new_status": body.status.upper()})
        await db.commit()
    except (IntegrityError, DBAPIError) as e:
        await db.rollback()
        err = str(e)
        if "Transición inválida" in err:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
        raise

    row = (await db.execute(
        text(f"SELECT {_DEC_COLS} {_DEC_FROM} WHERE d.id = :id"),
        {"id": decision_id_str},
    )).mappings().first()
    return _row_to_decision(dict(row), user)

@router.delete("/ar/decisions/{decision_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ar_decision(
    decision_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi_write(user)

    result = await db.execute(
        text("""
            UPDATE core.dgi_ar_decision
            SET deleted_at = NOW(), updated_at = NOW()
            WHERE id = :id AND deleted_at IS NULL
        """),
        {"id": str(decision_id)},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decisión no encontrada")
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
