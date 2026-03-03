import math
from fastapi import APIRouter, Depends, Query, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import hash_password
from app.schemas.admin import (
    UserListItem,
    UserDetail,
    UserCreate,
    UserUpdate,
    DivisionListItem,
    DivisionCreate,
    DivisionUpdate,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_admin(user: dict):
    if user["role_code"] != "ADMIN_SISTEMA":
        raise HTTPException(status_code=403, detail="Solo ADMIN_SISTEMA puede administrar")


class ResetPasswordBody(BaseModel):
    new_password: str


# ---------------------------------------------------------------------------
# GET /api/admin/usuarios — List users (paginated, filtered)
# ---------------------------------------------------------------------------

@router.get("/usuarios")
async def list_usuarios(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    role_code: str | None = None,
    is_active: bool | None = None,
):
    _require_admin(user)

    conditions = ["u.deleted_at IS NULL"]
    params: dict = {}

    if search:
        conditions.append(
            "(p.names ILIKE :search OR p.paternal_surname ILIKE :search OR u.email ILIKE :search)"
        )
        params["search"] = f"%{search}%"

    if role_code:
        conditions.append("c.code = :role_code")
        params["role_code"] = role_code

    if is_active is not None:
        conditions.append("u.is_active = :is_active")
        params["is_active"] = is_active

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core."user" u
        JOIN core.person p ON u.person_id = p.id
        JOIN ref.category c ON u.system_role_id = c.id
        LEFT JOIN core.organization o ON u.division_id = o.id
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
                u.id,
                u.email,
                p.names,
                p.paternal_surname,
                p.maternal_surname,
                c.code AS role_code,
                c.label AS role_label,
                o.name AS division_name,
                u.is_active,
                u.created_at
            {base_query}
            ORDER BY p.paternal_surname, p.names
            LIMIT :limit OFFSET :offset
        """),
        params,
    )
    rows = rows_result.mappings().all()
    items = [UserListItem(**dict(r)).model_dump() for r in rows]
    total_pages = math.ceil(total / page_size) if page_size else 0

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------------------
# GET /api/admin/usuarios/{id} — User detail
# ---------------------------------------------------------------------------

@router.get("/usuarios/{user_id}")
async def get_usuario(
    user_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    result = await db.execute(
        text("""
            SELECT
                u.id,
                u.email,
                p.names,
                p.paternal_surname,
                p.maternal_surname,
                c.code AS role_code,
                c.label AS role_label,
                o.name AS division_name,
                u.is_active,
                u.created_at,
                u.division_id,
                u.system_role_id,
                p.phone,
                p.rut
            FROM core."user" u
            JOIN core.person p ON u.person_id = p.id
            JOIN ref.category c ON u.system_role_id = c.id
            LEFT JOIN core.organization o ON u.division_id = o.id
            WHERE u.id = :uid AND u.deleted_at IS NULL
        """),
        {"uid": str(user_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return UserDetail(**dict(row)).model_dump()


# ---------------------------------------------------------------------------
# POST /api/admin/usuarios — Create user
# ---------------------------------------------------------------------------

@router.post("/usuarios", status_code=status.HTTP_201_CREATED)
async def create_usuario(
    data: UserCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    # Check if email already exists
    existing = await db.execute(
        text("SELECT id FROM core.\"user\" WHERE email = :email AND deleted_at IS NULL"),
        {"email": data.email},
    )
    if existing.first():
        raise HTTPException(status_code=409, detail="Ya existe un usuario con ese email")

    try:
        # Create person first
        person_result = await db.execute(
            text("""
                INSERT INTO core.person (names, paternal_surname, maternal_surname, email, rut, phone)
                VALUES (:names, :paternal_surname, :maternal_surname, :email, :rut, :phone)
                RETURNING id
            """),
            {
                "names": data.names,
                "paternal_surname": data.paternal_surname,
                "maternal_surname": data.maternal_surname,
                "email": data.email,
                "rut": data.rut,
                "phone": data.phone,
            },
        )
        person_id = person_result.scalar()

        # Create user linked to person
        pw_hash = hash_password(data.password)
        user_result = await db.execute(
            text("""
                INSERT INTO core."user" (person_id, email, password_hash, system_role_id, division_id)
                VALUES (:person_id, :email, :password_hash, :system_role_id, :division_id)
                RETURNING id
            """),
            {
                "person_id": str(person_id),
                "email": data.email,
                "password_hash": pw_hash,
                "system_role_id": str(data.system_role_id),
                "division_id": str(data.division_id) if data.division_id else None,
            },
        )
        new_user_id = user_result.scalar()
        await db.commit()

        return {"id": str(new_user_id), "email": data.email}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un usuario con ese email")
    except Exception:
        await db.rollback()
        raise


# ---------------------------------------------------------------------------
# PATCH /api/admin/usuarios/{id} — Update user
# ---------------------------------------------------------------------------

PERSON_FIELDS = {"names", "paternal_surname", "maternal_surname", "phone"}
USER_FIELDS = {"email", "system_role_id", "division_id"}


@router.patch("/usuarios/{user_id}")
async def update_usuario(
    user_id: UUID,
    data: UserUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    # Verify user exists
    existing = await db.execute(
        text("SELECT u.id, u.person_id FROM core.\"user\" u WHERE u.id = :uid AND u.deleted_at IS NULL"),
        {"uid": str(user_id)},
    )
    row = existing.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    person_id = row["person_id"]
    updates = data.model_dump(exclude_unset=True)

    # Separate person vs user fields
    person_updates = {k: v for k, v in updates.items() if k in PERSON_FIELDS}
    user_updates = {k: v for k, v in updates.items() if k in USER_FIELDS}

    if person_updates:
        set_clauses = ", ".join(f"{k} = :{k}" for k in person_updates)
        person_updates["pid"] = str(person_id)
        await db.execute(
            text(f"UPDATE core.person SET {set_clauses}, updated_at = NOW() WHERE id = :pid"),
            person_updates,
        )

    if user_updates:
        # Convert UUIDs to strings for the query
        params = {}
        for k, v in user_updates.items():
            params[k] = str(v) if v is not None and k in ("system_role_id", "division_id") else v
        set_clauses = ", ".join(f"{k} = :{k}" for k in user_updates)
        params["uid"] = str(user_id)
        await db.execute(
            text(f"UPDATE core.\"user\" SET {set_clauses}, updated_at = NOW() WHERE id = :uid"),
            params,
        )

    await db.commit()
    return {"message": "Usuario actualizado"}


# ---------------------------------------------------------------------------
# POST /api/admin/usuarios/{id}/toggle-activo — Toggle active status
# ---------------------------------------------------------------------------

@router.post("/usuarios/{user_id}/toggle-activo")
async def toggle_activo(
    user_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    result = await db.execute(
        text("SELECT is_active FROM core.\"user\" WHERE id = :uid AND deleted_at IS NULL"),
        {"uid": str(user_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    new_status = not row["is_active"]
    await db.execute(
        text("UPDATE core.\"user\" SET is_active = :active, updated_at = NOW() WHERE id = :uid"),
        {"active": new_status, "uid": str(user_id)},
    )
    await db.commit()

    label = "activado" if new_status else "desactivado"
    return {"is_active": new_status, "message": f"Usuario {label}"}


# ---------------------------------------------------------------------------
# POST /api/admin/usuarios/{id}/reset-password — Reset password
# ---------------------------------------------------------------------------

@router.post("/usuarios/{user_id}/reset-password")
async def reset_password(
    user_id: UUID,
    body: ResetPasswordBody,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    result = await db.execute(
        text("SELECT id FROM core.\"user\" WHERE id = :uid AND deleted_at IS NULL"),
        {"uid": str(user_id)},
    )
    if not result.first():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    pw_hash = hash_password(body.new_password)
    await db.execute(
        text("UPDATE core.\"user\" SET password_hash = :pw, updated_at = NOW() WHERE id = :uid"),
        {"pw": pw_hash, "uid": str(user_id)},
    )
    await db.commit()

    return {"message": "Contraseña actualizada"}


# ===========================================================================
# DIVISIONES
# ===========================================================================


# ---------------------------------------------------------------------------
# GET /api/admin/divisiones — List organizations with user count
# ---------------------------------------------------------------------------

@router.get("/divisiones")
async def list_divisiones(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    result = await db.execute(
        text("""
            SELECT
                o.id,
                o.code,
                o.name,
                c.label AS organization_type,
                (o.deleted_at IS NULL) AS is_active,
                COALESCE(uc.user_count, 0) AS user_count
            FROM core.organization o
            LEFT JOIN ref.category c ON o.org_type_id = c.id
            LEFT JOIN (
                SELECT division_id, COUNT(*) AS user_count
                FROM core."user"
                WHERE deleted_at IS NULL
                GROUP BY division_id
            ) uc ON uc.division_id = o.id
            WHERE o.deleted_at IS NULL
              AND c.code IN ('DIVISION', 'GORE')
            ORDER BY o.name
        """)
    )
    rows = result.mappings().all()
    return [DivisionListItem(**dict(r)).model_dump() for r in rows]


# ---------------------------------------------------------------------------
# POST /api/admin/divisiones — Create organization
# ---------------------------------------------------------------------------

@router.post("/divisiones", status_code=status.HTTP_201_CREATED)
async def create_division(
    data: DivisionCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    # Resolve organization_type_id
    org_type_id = data.organization_type_id
    if not org_type_id:
        type_result = await db.execute(
            text("SELECT id FROM ref.category WHERE scheme = 'organization_type' AND code = 'DIVISION'")
        )
        type_row = type_result.scalar()
        if not type_row:
            raise HTTPException(status_code=500, detail="No se encontró tipo DIVISION en ref.category")
        org_type_id = type_row

    result = await db.execute(
        text("""
            INSERT INTO core.organization (code, name, org_type_id)
            VALUES (:code, :name, :org_type_id)
            RETURNING id
        """),
        {
            "code": data.code,
            "name": data.name,
            "org_type_id": str(org_type_id),
        },
    )
    new_id = result.scalar()
    await db.commit()

    return {"id": str(new_id), "code": data.code}


# ---------------------------------------------------------------------------
# PATCH /api/admin/divisiones/{id} — Update organization
# ---------------------------------------------------------------------------

DIVISION_FIELDS = {"name", "code"}


@router.patch("/divisiones/{division_id}")
async def update_division(
    division_id: UUID,
    data: DivisionUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    existing = await db.execute(
        text("SELECT id FROM core.organization WHERE id = :did AND deleted_at IS NULL"),
        {"did": str(division_id)},
    )
    if not existing.first():
        raise HTTPException(status_code=404, detail="División no encontrada")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return {"message": "Sin cambios"}

    # Validate field names against allowlist
    for key in updates:
        if key not in DIVISION_FIELDS:
            raise HTTPException(status_code=422, detail=f"Campo no permitido: {key}")

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["did"] = str(division_id)
    await db.execute(
        text(f"UPDATE core.organization SET {set_clauses}, updated_at = NOW() WHERE id = :did"),
        updates,
    )
    await db.commit()

    return {"message": "División actualizada"}


# ===========================================================================
# FINANCING TRACKS (Poly-Switch configuration)
# ===========================================================================


# ---------------------------------------------------------------------------
# GET /api/admin/financing-tracks — List all financing tracks
# ---------------------------------------------------------------------------

@router.get("/financing-tracks")
async def list_financing_tracks(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    result = await db.execute(
        text("""
            SELECT id, code, label, evaluator_code, evaluator_label,
                   favorable_products, unfavorable_products, terminal_negative,
                   thresholds, required_attrs, sla_days, rs_validity_years, is_active
            FROM core.financing_track
            ORDER BY code
        """)
    )
    return [dict(r) for r in result.mappings().all()]


# ---------------------------------------------------------------------------
# POST /api/admin/financing-tracks — Create a financing track
# ---------------------------------------------------------------------------

@router.post("/financing-tracks", status_code=status.HTTP_201_CREATED)
async def create_financing_track(
    data: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    required = {"code", "label", "evaluator_code", "evaluator_label"}
    missing = required - set(data.keys())
    if missing:
        raise HTTPException(status_code=422, detail=f"Campos requeridos faltantes: {missing}")

    try:
        result = await db.execute(
            text("""
                INSERT INTO core.financing_track (
                    code, label, evaluator_code, evaluator_label,
                    favorable_products, unfavorable_products, terminal_negative,
                    thresholds, required_attrs, sla_days, rs_validity_years
                ) VALUES (
                    :code, :label, :evaluator_code, :evaluator_label,
                    :favorable_products, :unfavorable_products, :terminal_negative,
                    CAST(:thresholds AS jsonb), :required_attrs,
                    CAST(:sla_days AS jsonb), :rs_validity_years
                )
                RETURNING id
            """),
            {
                "code": data["code"],
                "label": data["label"],
                "evaluator_code": data["evaluator_code"],
                "evaluator_label": data["evaluator_label"],
                "favorable_products": data.get("favorable_products", []),
                "unfavorable_products": data.get("unfavorable_products", []),
                "terminal_negative": data.get("terminal_negative", []),
                "thresholds": str(data.get("thresholds", {})).replace("'", '"'),
                "required_attrs": data.get("required_attrs", []),
                "sla_days": str(data.get("sla_days", {})).replace("'", '"'),
                "rs_validity_years": data.get("rs_validity_years"),
            },
        )
        row = result.mappings().first()
        await db.commit()
        return {"id": str(row["id"]), "code": data["code"]}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un track con ese código")
    except Exception:
        await db.rollback()
        raise


# ---------------------------------------------------------------------------
# PATCH /api/admin/financing-tracks/{id} — Update a financing track
# ---------------------------------------------------------------------------

_TRACK_FIELDS = {
    "label", "evaluator_code", "evaluator_label",
    "favorable_products", "unfavorable_products", "terminal_negative",
    "required_attrs", "rs_validity_years", "is_active",
}
_TRACK_JSONB_FIELDS = {"thresholds", "sla_days"}


@router.patch("/financing-tracks/{track_id}")
async def update_financing_track(
    track_id: UUID,
    data: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    existing = await db.execute(
        text("SELECT id FROM core.financing_track WHERE id = :id"),
        {"id": str(track_id)},
    )
    if not existing.first():
        raise HTTPException(status_code=404, detail="Track no encontrado")

    if not data:
        return {"message": "Sin cambios"}

    set_parts = []
    params: dict = {"id": str(track_id)}

    for key, val in data.items():
        if key in _TRACK_FIELDS:
            param = f"v_{key}"
            set_parts.append(f"{key} = :{param}")
            params[param] = val
        elif key in _TRACK_JSONB_FIELDS:
            import json
            param = f"v_{key}"
            set_parts.append(f"{key} = CAST(:{param} AS jsonb)")
            params[param] = json.dumps(val) if isinstance(val, dict) else val

    if not set_parts:
        return {"message": "Sin campos válidos para actualizar"}

    set_parts.append("updated_at = NOW()")
    sql = text(f"UPDATE core.financing_track SET {', '.join(set_parts)} WHERE id = :id")
    await db.execute(sql, params)
    await db.commit()
    return {"message": "Track actualizado"}
