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
from app.schemas.threshold import ThresholdListItem, ThresholdCreate, ThresholdUpdate
from app.schemas.parametric import (
    Subv8FundItem, Subv8FundCreate, Subv8FundUpdate,
    Subv8CeilingItem, Subv8CeilingCreate, Subv8CeilingUpdate,
    FrilCategoryItem, FrilCategoryCreate, FrilCategoryUpdate,
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
# GET /api/admin/financing-tracks/routing — Evaluator routing for an IPR
# ---------------------------------------------------------------------------

@router.get("/financing-tracks/routing")
async def get_evaluator_routing(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    ipr_id: UUID | None = None,
):
    """Given an IPR, returns its financing track evaluator info. Informational only."""
    _require_admin(user)
    if not ipr_id:
        raise HTTPException(status_code=422, detail="ipr_id requerido")

    row = (await db.execute(
        text("""
            SELECT ft.code AS track_code, ft.label AS track_label,
                   ft.evaluator_code, ft.evaluator_label,
                   ft.favorable_products, ft.sla_days, ft.rs_validity_years
            FROM core.ipr i
            JOIN core.financing_track ft ON ft.id = i.financing_track_id
            WHERE i.id = :ipr_id AND i.deleted_at IS NULL AND ft.is_active = true
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="IPR no encontrado o sin track de financiamiento asignado",
        )
    return dict(row)


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


# ===========================================================================
# FINANCIAL THRESHOLDS (Compliance engine configuration)
# ===========================================================================


_THRESHOLD_FIELDS = {
    "label", "value_utm", "value_pct", "enforcement_point",
    "source_normativa", "applies_to_track", "is_active",
}


# ---------------------------------------------------------------------------
# GET /api/admin/thresholds — List all financial thresholds
# ---------------------------------------------------------------------------

@router.get("/thresholds", response_model=list[ThresholdListItem])
async def list_thresholds(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    result = await db.execute(
        text("""
            SELECT id, code, label, value_utm, value_pct,
                   enforcement_point, source_normativa, applies_to_track,
                   is_active, created_at, updated_at
            FROM core.financial_threshold
            ORDER BY enforcement_point, code
        """)
    )
    return [ThresholdListItem(**dict(r)) for r in result.mappings().all()]


# ---------------------------------------------------------------------------
# POST /api/admin/thresholds — Create a financial threshold
# ---------------------------------------------------------------------------

@router.post("/thresholds", status_code=status.HTTP_201_CREATED)
async def create_threshold(
    data: ThresholdCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    try:
        result = await db.execute(
            text("""
                INSERT INTO core.financial_threshold (
                    code, label, value_utm, value_pct,
                    enforcement_point, source_normativa, applies_to_track
                ) VALUES (
                    :code, :label, :value_utm, :value_pct,
                    :enforcement_point, :source_normativa, :applies_to_track
                )
                RETURNING id
            """),
            {
                "code": data.code,
                "label": data.label,
                "value_utm": data.value_utm,
                "value_pct": data.value_pct,
                "enforcement_point": data.enforcement_point,
                "source_normativa": data.source_normativa,
                "applies_to_track": data.applies_to_track,
            },
        )
        row = result.mappings().first()
        await db.commit()
        return {"id": str(row["id"]), "code": data.code}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un umbral con ese código")
    except Exception:
        await db.rollback()
        raise


# ---------------------------------------------------------------------------
# PATCH /api/admin/thresholds/{id} — Update a financial threshold
# ---------------------------------------------------------------------------

@router.patch("/thresholds/{threshold_id}")
async def update_threshold(
    threshold_id: UUID,
    data: ThresholdUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    existing = await db.execute(
        text("SELECT id FROM core.financial_threshold WHERE id = :id"),
        {"id": str(threshold_id)},
    )
    if not existing.first():
        raise HTTPException(status_code=404, detail="Umbral no encontrado")

    updates = data.model_dump(exclude_none=True)
    if not updates:
        return {"message": "Sin cambios"}

    # Validate field names against allowlist
    for key in updates:
        if key not in _THRESHOLD_FIELDS:
            raise HTTPException(status_code=422, detail=f"Campo no permitido: {key}")

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(threshold_id)
    await db.execute(
        text(f"UPDATE core.financial_threshold SET {set_clauses}, updated_at = NOW() WHERE id = :id"),
        updates,
    )
    await db.commit()
    return {"message": "Umbral actualizado"}


# ===========================================================================
# SNI LEVEL CONFIG (Proporcionalidad rules — HΩ-11)
# ===========================================================================


_SNI_LEVEL_FIELDS = {
    "label", "min_utm", "max_utm", "evaluator_code",
    "requires_external_eval", "is_active",
}


# ---------------------------------------------------------------------------
# GET /api/admin/sni-levels — List all SNI levels
# ---------------------------------------------------------------------------

@router.get("/sni-levels")
async def list_sni_levels(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    result = await db.execute(
        text("""
            SELECT id, level_number, label, min_utm, max_utm,
                   evaluator_code, requires_external_eval, is_active,
                   created_at, updated_at
            FROM core.sni_level_config
            ORDER BY level_number
        """)
    )
    return [dict(r) for r in result.mappings().all()]


# ---------------------------------------------------------------------------
# POST /api/admin/sni-levels — Create a new SNI level
# ---------------------------------------------------------------------------

@router.post("/sni-levels", status_code=status.HTTP_201_CREATED)
async def create_sni_level(
    data: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    required = {"level_number", "label", "evaluator_code"}
    missing = required - set(data.keys())
    if missing:
        raise HTTPException(status_code=422, detail=f"Campos requeridos faltantes: {missing}")

    try:
        result = await db.execute(
            text("""
                INSERT INTO core.sni_level_config (
                    level_number, label, min_utm, max_utm,
                    evaluator_code, requires_external_eval
                ) VALUES (
                    :level_number, :label, :min_utm, :max_utm,
                    :evaluator_code, :requires_external_eval
                )
                RETURNING id
            """),
            {
                "level_number": data["level_number"],
                "label": data["label"],
                "min_utm": data.get("min_utm", 0),
                "max_utm": data.get("max_utm"),
                "evaluator_code": data["evaluator_code"],
                "requires_external_eval": data.get("requires_external_eval", False),
            },
        )
        row = result.mappings().first()
        await db.commit()
        return {"id": str(row["id"]), "level_number": data["level_number"]}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un nivel con ese número")
    except Exception:
        await db.rollback()
        raise


# ---------------------------------------------------------------------------
# PATCH /api/admin/sni-levels/{id} — Update an SNI level
# ---------------------------------------------------------------------------

@router.patch("/sni-levels/{level_id}")
async def update_sni_level(
    level_id: UUID,
    data: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    existing = await db.execute(
        text("SELECT id FROM core.sni_level_config WHERE id = :id"),
        {"id": str(level_id)},
    )
    if not existing.first():
        raise HTTPException(status_code=404, detail="Nivel SNI no encontrado")

    if not data:
        return {"message": "Sin cambios"}

    # Validate field names against allowlist
    for key in data:
        if key not in _SNI_LEVEL_FIELDS:
            raise HTTPException(status_code=422, detail=f"Campo no permitido: {key}")

    set_clauses = ", ".join(f"{k} = :{k}" for k in data)
    params = {**data, "id": str(level_id)}
    await db.execute(
        text(f"UPDATE core.sni_level_config SET {set_clauses}, updated_at = NOW() WHERE id = :id"),
        params,
    )
    await db.commit()
    return {"message": "Nivel SNI actualizado"}


# ===========================================================================
# SUBVENCIÓN 8% FUNDS (TP-02)
# ===========================================================================


_SUBV8_FUND_FIELDS = {
    "name", "budget_regular", "budget_special", "budget_total",
    "is_exclusive", "sort_order", "is_active",
}


# ---------------------------------------------------------------------------
# GET /api/admin/subv8-funds — List all subv8 funds
# ---------------------------------------------------------------------------

@router.get("/subv8-funds", response_model=list[Subv8FundItem])
async def list_subv8_funds(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    result = await db.execute(
        text("""
            SELECT id, code, name, budget_regular, budget_special,
                   budget_total, is_exclusive, sort_order, is_active
            FROM core.subv8_fund
            ORDER BY sort_order, code
        """)
    )
    return [Subv8FundItem(**dict(r)) for r in result.mappings().all()]


# ---------------------------------------------------------------------------
# POST /api/admin/subv8-funds — Create a subv8 fund
# ---------------------------------------------------------------------------

@router.post("/subv8-funds", status_code=status.HTTP_201_CREATED)
async def create_subv8_fund(
    data: Subv8FundCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    try:
        result = await db.execute(
            text("""
                INSERT INTO core.subv8_fund (
                    code, name, budget_regular, budget_special,
                    budget_total, is_exclusive, sort_order
                ) VALUES (
                    :code, :name, :budget_regular, :budget_special,
                    :budget_total, :is_exclusive, :sort_order
                )
                RETURNING id
            """),
            {
                "code": data.code,
                "name": data.name,
                "budget_regular": data.budget_regular,
                "budget_special": data.budget_special,
                "budget_total": data.budget_total,
                "is_exclusive": data.is_exclusive,
                "sort_order": data.sort_order,
            },
        )
        row = result.mappings().first()
        await db.commit()
        return {"id": str(row["id"]), "code": data.code}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un fondo con ese código")
    except Exception:
        await db.rollback()
        raise


# ---------------------------------------------------------------------------
# PATCH /api/admin/subv8-funds/{fund_id} — Update a subv8 fund
# ---------------------------------------------------------------------------

@router.patch("/subv8-funds/{fund_id}")
async def update_subv8_fund(
    fund_id: UUID,
    data: Subv8FundUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    existing = await db.execute(
        text("SELECT id FROM core.subv8_fund WHERE id = :id"),
        {"id": str(fund_id)},
    )
    if not existing.first():
        raise HTTPException(status_code=404, detail="Fondo no encontrado")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return {"message": "Sin cambios"}

    for key in updates:
        if key not in _SUBV8_FUND_FIELDS:
            raise HTTPException(status_code=422, detail=f"Campo no permitido: {key}")

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(fund_id)
    await db.execute(
        text(f"UPDATE core.subv8_fund SET {set_clauses}, updated_at = NOW() WHERE id = :id"),
        updates,
    )
    await db.commit()
    return {"message": "Fondo actualizado"}


# ---------------------------------------------------------------------------
# GET /api/admin/subv8-funds/{fund_id}/ceilings — List ceilings for a fund
# ---------------------------------------------------------------------------

@router.get("/subv8-funds/{fund_id}/ceilings", response_model=list[Subv8CeilingItem])
async def list_fund_ceilings(
    fund_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    # Verify fund exists
    fund = await db.execute(
        text("SELECT id FROM core.subv8_fund WHERE id = :id"),
        {"id": str(fund_id)},
    )
    if not fund.first():
        raise HTTPException(status_code=404, detail="Fondo no encontrado")

    result = await db.execute(
        text("""
            SELECT c.id, c.fund_id, f.code AS fund_code, f.name AS fund_name,
                   c.institution_type, c.area, c.max_amount, c.notes
            FROM core.subv8_fund_ceiling c
            JOIN core.subv8_fund f ON f.id = c.fund_id
            WHERE c.fund_id = :fund_id
            ORDER BY c.institution_type, c.area
        """),
        {"fund_id": str(fund_id)},
    )
    return [Subv8CeilingItem(**dict(r)) for r in result.mappings().all()]


# ---------------------------------------------------------------------------
# POST /api/admin/subv8-funds/{fund_id}/ceilings — Create a ceiling under a fund
# ---------------------------------------------------------------------------

@router.post("/subv8-funds/{fund_id}/ceilings", status_code=status.HTTP_201_CREATED)
async def create_fund_ceiling(
    fund_id: UUID,
    data: Subv8CeilingCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    # Verify fund exists
    fund = await db.execute(
        text("SELECT id FROM core.subv8_fund WHERE id = :id"),
        {"id": str(fund_id)},
    )
    if not fund.first():
        raise HTTPException(status_code=404, detail="Fondo no encontrado")

    try:
        result = await db.execute(
            text("""
                INSERT INTO core.subv8_fund_ceiling (
                    fund_id, institution_type, area, max_amount, notes
                ) VALUES (
                    :fund_id, :institution_type, :area, :max_amount, :notes
                )
                RETURNING id
            """),
            {
                "fund_id": str(fund_id),
                "institution_type": data.institution_type,
                "area": data.area,
                "max_amount": data.max_amount,
                "notes": data.notes,
            },
        )
        row = result.mappings().first()
        await db.commit()
        return {"id": str(row["id"]), "fund_id": str(fund_id)}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un tope para esa combinación fondo/tipo/área")
    except Exception:
        await db.rollback()
        raise


# ---------------------------------------------------------------------------
# GET /api/admin/subv8-fund-ceilings — List ALL ceilings flat (with fund info)
# ---------------------------------------------------------------------------

@router.get("/subv8-fund-ceilings", response_model=list[Subv8CeilingItem])
async def list_all_ceilings(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    result = await db.execute(
        text("""
            SELECT c.id, c.fund_id, f.code AS fund_code, f.name AS fund_name,
                   c.institution_type, c.area, c.max_amount, c.notes
            FROM core.subv8_fund_ceiling c
            JOIN core.subv8_fund f ON f.id = c.fund_id
            ORDER BY f.sort_order, f.code, c.institution_type, c.area
        """)
    )
    return [Subv8CeilingItem(**dict(r)) for r in result.mappings().all()]


# ---------------------------------------------------------------------------
# PATCH /api/admin/subv8-fund-ceilings/{ceiling_id} — Update a ceiling
# ---------------------------------------------------------------------------

_SUBV8_CEILING_FIELDS = {"institution_type", "area", "max_amount", "notes"}


@router.patch("/subv8-fund-ceilings/{ceiling_id}")
async def update_ceiling(
    ceiling_id: UUID,
    data: Subv8CeilingUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    existing = await db.execute(
        text("SELECT id FROM core.subv8_fund_ceiling WHERE id = :id"),
        {"id": str(ceiling_id)},
    )
    if not existing.first():
        raise HTTPException(status_code=404, detail="Tope no encontrado")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return {"message": "Sin cambios"}

    for key in updates:
        if key not in _SUBV8_CEILING_FIELDS:
            raise HTTPException(status_code=422, detail=f"Campo no permitido: {key}")

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(ceiling_id)
    await db.execute(
        text(f"UPDATE core.subv8_fund_ceiling SET {set_clauses}, updated_at = NOW() WHERE id = :id"),
        updates,
    )
    await db.commit()
    return {"message": "Tope actualizado"}


# ---------------------------------------------------------------------------
# DELETE /api/admin/subv8-fund-ceilings/{ceiling_id} — Delete a ceiling
# ---------------------------------------------------------------------------

@router.delete("/subv8-fund-ceilings/{ceiling_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ceiling(
    ceiling_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    result = await db.execute(
        text("DELETE FROM core.subv8_fund_ceiling WHERE id = :id RETURNING id"),
        {"id": str(ceiling_id)},
    )
    if not result.first():
        raise HTTPException(status_code=404, detail="Tope no encontrado")

    await db.commit()


# ===========================================================================
# FRIL CATEGORIES (TP-04)
# ===========================================================================


_FRIL_CATEGORY_FIELDS = {
    "name", "group_code", "group_name", "description", "examples",
    "max_utm", "is_exempt_commune_limit", "is_active", "sort_order",
}


# ---------------------------------------------------------------------------
# GET /api/admin/fril-categories — List all FRIL categories
# ---------------------------------------------------------------------------

@router.get("/fril-categories", response_model=list[FrilCategoryItem])
async def list_fril_categories(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    result = await db.execute(
        text("""
            SELECT id, code, name, group_code, group_name, description,
                   examples, max_utm, is_exempt_commune_limit, is_active, sort_order
            FROM core.fril_category
            ORDER BY sort_order, code
        """)
    )
    return [FrilCategoryItem(**dict(r)) for r in result.mappings().all()]


# ---------------------------------------------------------------------------
# POST /api/admin/fril-categories — Create a FRIL category
# ---------------------------------------------------------------------------

@router.post("/fril-categories", status_code=status.HTTP_201_CREATED)
async def create_fril_category(
    data: FrilCategoryCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    try:
        result = await db.execute(
            text("""
                INSERT INTO core.fril_category (
                    code, name, group_code, group_name, description,
                    examples, max_utm, is_exempt_commune_limit, sort_order
                ) VALUES (
                    :code, :name, :group_code, :group_name, :description,
                    :examples, :max_utm, :is_exempt_commune_limit, :sort_order
                )
                RETURNING id
            """),
            {
                "code": data.code,
                "name": data.name,
                "group_code": data.group_code,
                "group_name": data.group_name,
                "description": data.description,
                "examples": data.examples,
                "max_utm": data.max_utm,
                "is_exempt_commune_limit": data.is_exempt_commune_limit,
                "sort_order": data.sort_order,
            },
        )
        row = result.mappings().first()
        await db.commit()
        return {"id": str(row["id"]), "code": data.code}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una categoría con ese código")
    except Exception:
        await db.rollback()
        raise


# ---------------------------------------------------------------------------
# PATCH /api/admin/fril-categories/{category_id} — Update a FRIL category
# ---------------------------------------------------------------------------

@router.patch("/fril-categories/{category_id}")
async def update_fril_category(
    category_id: UUID,
    data: FrilCategoryUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    existing = await db.execute(
        text("SELECT id FROM core.fril_category WHERE id = :id"),
        {"id": str(category_id)},
    )
    if not existing.first():
        raise HTTPException(status_code=404, detail="Categoría FRIL no encontrada")

    updates = data.model_dump(exclude_unset=True)
    if not updates:
        return {"message": "Sin cambios"}

    for key in updates:
        if key not in _FRIL_CATEGORY_FIELDS:
            raise HTTPException(status_code=422, detail=f"Campo no permitido: {key}")

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(category_id)
    await db.execute(
        text(f"UPDATE core.fril_category SET {set_clauses}, updated_at = NOW() WHERE id = :id"),
        updates,
    )
    await db.commit()
    return {"message": "Categoría FRIL actualizada"}


# ===========================================================================
# BUDGET PROGRAM CODES (DIPRES Level 5) — CRUD on ref.category scheme
# ===========================================================================


_PROGRAM_CODE_FIELDS = {"label", "sort_order"}


# ---------------------------------------------------------------------------
# GET /api/admin/budget-program-codes — List all budget program codes
# ---------------------------------------------------------------------------

@router.get("/budget-program-codes")
async def list_budget_program_codes(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    result = await db.execute(
        text("""
            SELECT id, code, label, sort_order, created_at, updated_at
            FROM ref.category
            WHERE scheme = 'budget_program_code' AND deleted_at IS NULL
            ORDER BY sort_order, code
        """)
    )
    return [dict(r) for r in result.mappings().all()]


# ---------------------------------------------------------------------------
# POST /api/admin/budget-program-codes — Create a budget program code
# ---------------------------------------------------------------------------

@router.post("/budget-program-codes", status_code=status.HTTP_201_CREATED)
async def create_budget_program_code(
    data: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    required = {"code", "label"}
    missing = required - set(data.keys())
    if missing:
        raise HTTPException(status_code=422, detail=f"Campos requeridos faltantes: {missing}")

    try:
        result = await db.execute(
            text("""
                INSERT INTO ref.category (scheme, code, label, sort_order, created_by_id)
                VALUES ('budget_program_code', :code, :label, :sort_order, :user_id)
                RETURNING id, code
            """),
            {
                "code": data["code"],
                "label": data["label"],
                "sort_order": data.get("sort_order", 0),
                "user_id": str(user["id"]),
            },
        )
        row = result.mappings().first()
        await db.commit()
        return {"id": str(row["id"]), "code": row["code"]}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un código de programa con ese code")


# ---------------------------------------------------------------------------
# PATCH /api/admin/budget-program-codes/{code_id} — Update a budget program code
# ---------------------------------------------------------------------------

@router.patch("/budget-program-codes/{code_id}")
async def update_budget_program_code(
    code_id: UUID,
    data: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)

    existing = await db.execute(
        text("SELECT id FROM ref.category WHERE id = :id AND scheme = 'budget_program_code' AND deleted_at IS NULL"),
        {"id": str(code_id)},
    )
    if not existing.first():
        raise HTTPException(status_code=404, detail="Código de programa no encontrado")

    updates = {k: v for k, v in data.items() if k in _PROGRAM_CODE_FIELDS}
    if not updates:
        return {"message": "Sin cambios"}

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(code_id)
    await db.execute(
        text(f"UPDATE ref.category SET {set_clauses}, updated_at = NOW() WHERE id = :id"),
        updates,
    )
    await db.commit()
    return {"message": "Actualizado"}


# ===========================================================================
# ADMISSIBILITY ITEMS CRUD (Admisibilidad sub-states)
# ===========================================================================


_ADMISSIBILITY_ITEM_FIELDS = {"label", "description", "responsible_role", "sort_order", "is_required"}


# ---------------------------------------------------------------------------
# GET /api/admin/admissibility-items — List admissibility items
# ---------------------------------------------------------------------------

@router.get("/admissibility-items")
async def list_admissibility_items(
    user: CurrentUser,
    track_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    sql = """
        SELECT ai.id, ai.financing_track_id, ai.code, ai.label, ai.description,
               ai.responsible_role, ai.sort_order, ai.is_required,
               ft.code AS track_code
        FROM core.admissibility_item ai
        JOIN core.financing_track ft ON ft.id = ai.financing_track_id
        WHERE ai.deleted_at IS NULL
    """
    params: dict = {}
    if track_id:
        sql += " AND ai.financing_track_id = :track_id"
        params["track_id"] = str(track_id)
    sql += " ORDER BY ai.sort_order, ai.code"
    rows = (await db.execute(text(sql), params)).mappings().all()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# POST /api/admin/admissibility-items — Create an admissibility item
# ---------------------------------------------------------------------------

@router.post("/admissibility-items", status_code=201)
async def create_admissibility_item(
    data: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    required = {"financing_track_id", "code", "label", "responsible_role"}
    missing = required - data.keys()
    if missing:
        raise HTTPException(400, f"Campos requeridos: {missing}")
    try:
        row = (await db.execute(
            text("""
                INSERT INTO core.admissibility_item
                  (financing_track_id, code, label, description, responsible_role, sort_order, is_required)
                VALUES (:financing_track_id, :code, :label, :description, :responsible_role, :sort_order, :is_required)
                RETURNING id, financing_track_id, code, label, description, responsible_role, sort_order, is_required
            """),
            {
                "financing_track_id": str(data["financing_track_id"]),
                "code": data["code"],
                "label": data["label"],
                "description": data.get("description"),
                "responsible_role": data["responsible_role"],
                "sort_order": data.get("sort_order", 0),
                "is_required": data.get("is_required", True),
            },
        )).mappings().first()
        await db.commit()
        return dict(row)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "Ya existe un ítem con ese código para este track")


# ---------------------------------------------------------------------------
# PATCH /api/admin/admissibility-items/{item_id} — Update an admissibility item
# ---------------------------------------------------------------------------

@router.patch("/admissibility-items/{item_id}")
async def update_admissibility_item(
    item_id: UUID,
    data: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    existing = await db.execute(
        text("SELECT id FROM core.admissibility_item WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(item_id)},
    )
    if not existing.first():
        raise HTTPException(404, "Ítem de admisibilidad no encontrado")
    updates = {k: v for k, v in data.items() if k in _ADMISSIBILITY_ITEM_FIELDS}
    if not updates:
        return {"message": "Sin cambios"}
    set_clause = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(item_id)
    row = (await db.execute(
        text(f"""
            UPDATE core.admissibility_item SET {set_clause}, updated_at = NOW()
            WHERE id = :id
            RETURNING id, financing_track_id, code, label, description, responsible_role, sort_order, is_required
        """),
        updates,
    )).mappings().first()
    await db.commit()
    return dict(row)
