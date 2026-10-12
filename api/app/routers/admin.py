import math
from fastapi import APIRouter, Depends, Query, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from pydantic import BaseModel, Field

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import hash_password
from app.core.audit import record_event
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

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_admin(user: dict):
    if user["role_code"] != "ADMIN_SISTEMA":
        raise HTTPException(status_code=403, detail="Solo ADMIN_SISTEMA puede administrar")


class ResetPasswordBody(BaseModel):
    new_password: str = Field(min_length=8)


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
        await record_event(db, "CREACION", "core.user", new_user_id, user["id"], {"email": data.email})
        await db.commit()

        return {"id": str(new_user_id), "email": data.email}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un usuario con ese email")
    except DBAPIError:
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

    await record_event(db, "MODIFICACION", "core.user", user_id, user["id"])
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
    await record_event(db, "MODIFICACION", "core.user", user_id, user["id"], {"is_active": new_status})
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
            text("SELECT id FROM ref.category WHERE scheme = 'org_type' AND code = 'DIVISION'")
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


# ---------------------------------------------------------------------------
# POST /api/admin/financing-tracks — Create a financing track
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# GET /api/admin/financing-tracks/routing — Evaluator routing for an IPR
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# GET /api/admin/financing-tracks/{code}/iprs — IPRs in a track
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# PATCH /api/admin/financing-tracks/{id} — Update a financing track
# ---------------------------------------------------------------------------

_TRACK_FIELDS = {
    "label", "evaluator_code", "evaluator_label",
    "favorable_products", "unfavorable_products", "terminal_negative",
    "required_attrs", "rs_validity_years", "is_active",
}
_TRACK_JSONB_FIELDS = {"thresholds", "sla_days"}


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
    except DBAPIError:
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


# ---------------------------------------------------------------------------
# POST /api/admin/sni-levels — Create a new SNI level
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# PATCH /api/admin/sni-levels/{id} — Update an SNI level
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# POST /api/admin/subv8-funds — Create a subv8 fund
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# PATCH /api/admin/subv8-funds/{fund_id} — Update a subv8 fund
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# GET /api/admin/subv8-funds/{fund_id}/ceilings — List ceilings for a fund
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# POST /api/admin/subv8-funds/{fund_id}/ceilings — Create a ceiling under a fund
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# GET /api/admin/subv8-fund-ceilings — List ALL ceilings flat (with fund info)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# PATCH /api/admin/subv8-fund-ceilings/{ceiling_id} — Update a ceiling
# ---------------------------------------------------------------------------

_SUBV8_CEILING_FIELDS = {"institution_type", "area", "max_amount", "notes"}


# ---------------------------------------------------------------------------
# DELETE /api/admin/subv8-fund-ceilings/{ceiling_id} — Delete a ceiling
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# POST /api/admin/fril-categories — Create a FRIL category
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# PATCH /api/admin/fril-categories/{category_id} — Update a FRIL category
# ---------------------------------------------------------------------------


# ===========================================================================
# BUDGET PROGRAM CODES (DIPRES Level 5) — CRUD on ref.category scheme
# ===========================================================================


_PROGRAM_CODE_FIELDS = {"label", "sort_order"}


# ---------------------------------------------------------------------------
# GET /api/admin/budget-program-codes — List all budget program codes
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# POST /api/admin/budget-program-codes — Create a budget program code
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# PATCH /api/admin/budget-program-codes/{code_id} — Update a budget program code
# ---------------------------------------------------------------------------


# ===========================================================================
# ADMISSIBILITY ITEMS CRUD (Admisibilidad sub-states)
# ===========================================================================


_ADMISSIBILITY_ITEM_FIELDS = {"label", "description", "responsible_role", "sort_order", "is_required"}


# ---------------------------------------------------------------------------
# GET /api/admin/admissibility-items — List admissibility items
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# POST /api/admin/admissibility-items — Create an admissibility item
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# PATCH /api/admin/admissibility-items/{item_id} — Update an admissibility item
# ---------------------------------------------------------------------------


# ===========================================================================
# DATA QUALITY — Completeness metrics
# ===========================================================================


@router.get("/data-quality")
async def get_data_quality(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return data completeness metrics across key entities."""
    _require_admin(user)

    # Person metrics
    person_result = await db.execute(
        text("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE email IS NOT NULL AND email != '') AS with_email,
                COUNT(*) FILTER (WHERE rut IS NOT NULL AND rut != '') AS with_rut,
                COUNT(*) FILTER (WHERE phone IS NOT NULL AND phone != '') AS with_phone
            FROM core.person
        """)
    )
    person = dict(person_result.mappings().first())

    # IPR metrics
    ipr_result = await db.execute(
        text("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE i.executor_id IS NOT NULL) AS with_executor,
                COUNT(*) FILTER (WHERE i.mechanism_id IS NOT NULL) AS with_mechanism,
                COUNT(*) FILTER (WHERE i.ipr_nature IS NOT NULL) AS with_nature,
                COUNT(*) FILTER (WHERE EXISTS (
                    SELECT 1 FROM core.ipr_party ip WHERE ip.ipr_id = i.id
                )) AS with_parties,
                COUNT(*) FILTER (WHERE EXISTS (
                    SELECT 1 FROM core.ipr_territory it WHERE it.ipr_id = i.id
                )) AS with_territory
            FROM core.ipr i
            WHERE i.deleted_at IS NULL
        """)
    )
    ipr = dict(ipr_result.mappings().first())

    # Agreement metrics
    agreement_result = await db.execute(
        text("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE a.cgr_outcome_id IS NOT NULL) AS with_cgr,
                COUNT(*) FILTER (WHERE a.ipr_id IS NOT NULL) AS with_ipr,
                COUNT(*) FILTER (WHERE a.technical_referent_id IS NOT NULL) AS with_referent
            FROM core.agreement a
            WHERE a.deleted_at IS NULL
        """)
    )
    agreement = dict(agreement_result.mappings().first())

    # Document metrics
    document_result = await db.execute(
        text("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE d.document_type_id IS NOT NULL) AS with_type,
                COUNT(*) FILTER (WHERE d.storage_url IS NOT NULL AND d.storage_url != '') AS with_url
            FROM core.document d
        """)
    )
    document = dict(document_result.mappings().first())

    # Organization metrics
    org_result = await db.execute(
        text("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE o.org_type_id IS NOT NULL) AS with_type,
                COUNT(*) FILTER (WHERE o.parent_id IS NOT NULL) AS with_parent
            FROM core.organization o
            WHERE o.deleted_at IS NULL
        """)
    )
    org = dict(org_result.mappings().first())

    def pct(num: int, den: int) -> float:
        return round(num * 100.0 / den, 1) if den > 0 else 0.0

    return {
        "persons": {
            **person,
            "pct_email": pct(person["with_email"], person["total"]),
            "pct_rut": pct(person["with_rut"], person["total"]),
            "pct_phone": pct(person["with_phone"], person["total"]),
        },
        "iprs": {
            **ipr,
            "pct_executor": pct(ipr["with_executor"], ipr["total"]),
            "pct_mechanism": pct(ipr["with_mechanism"], ipr["total"]),
            "pct_nature": pct(ipr["with_nature"], ipr["total"]),
            "pct_parties": pct(ipr["with_parties"], ipr["total"]),
            "pct_territory": pct(ipr["with_territory"], ipr["total"]),
        },
        "agreements": {
            **agreement,
            "pct_cgr": pct(agreement["with_cgr"], agreement["total"]),
            "pct_ipr": pct(agreement["with_ipr"], agreement["total"]),
            "pct_referent": pct(agreement["with_referent"], agreement["total"]),
        },
        "documents": {
            **document,
            "pct_type": pct(document["with_type"], document["total"]),
            "pct_url": pct(document["with_url"], document["total"]),
        },
        "organizations": {
            **org,
            "pct_type": pct(org["with_type"], org["total"]),
            "pct_parent": pct(org["with_parent"], org["total"]),
        },
    }


# ===========================================================================
# SLA DASHBOARD — Consolidated view of all 12 SLA sources
# ===========================================================================


@router.get("/slas/dashboard")
async def get_sla_dashboard(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Aggregate all SLA states into a single response with semáforo."""
    _require_admin(user)

    slas = []

    # 1. SISREC: RTF 7d
    r = (await db.execute(text("""
        SELECT COUNT(*) AS total,
               COUNT(*) FILTER (WHERE EXTRACT(EPOCH FROM (NOW() - COALESCE(r.phase_entered_at, r.updated_at))) / 86400.0 > 7) AS breached
        FROM core.rendition r
        JOIN ref.category st ON st.id = r.state_id AND st.code = 'EN_REVISION_RTF'
        WHERE r.deleted_at IS NULL
    """))).mappings().first()
    slas.append({"name": "SISREC: Revisión RTF", "sla_days": 7, "active": r["total"], "breached": r["breached"]})

    # 2. SISREC: VISADA_RTF 1d
    r = (await db.execute(text("""
        SELECT COUNT(*) AS total,
               COUNT(*) FILTER (WHERE EXTRACT(EPOCH FROM (NOW() - COALESCE(r.phase_entered_at, r.updated_at))) / 86400.0 > 1) AS breached
        FROM core.rendition r
        JOIN ref.category st ON st.id = r.state_id AND st.code = 'VISADA_RTF'
        WHERE r.deleted_at IS NULL
    """))).mappings().first()
    slas.append({"name": "SISREC: Traspaso DAF", "sla_days": 1, "active": r["total"], "breached": r["breached"]})

    # 3. SISREC: UCR 2d
    r = (await db.execute(text("""
        SELECT COUNT(*) AS total,
               COUNT(*) FILTER (WHERE EXTRACT(EPOCH FROM (NOW() - COALESCE(r.phase_entered_at, r.updated_at))) / 86400.0 > 2) AS breached
        FROM core.rendition r
        JOIN ref.category st ON st.id = r.state_id AND st.code = 'EN_REVISION_UCR'
        WHERE r.deleted_at IS NULL
    """))).mappings().first()
    slas.append({"name": "SISREC: Revisión UCR", "sla_days": 2, "active": r["total"], "breached": r["breached"]})

    # 4. SISREC: OBSERVADA 15d
    r = (await db.execute(text("""
        SELECT COUNT(*) AS total,
               COUNT(*) FILTER (WHERE EXTRACT(EPOCH FROM (NOW() - COALESCE(r.phase_entered_at, r.updated_at))) / 86400.0 > 15) AS breached
        FROM core.rendition r
        JOIN ref.category st ON st.id = r.state_id AND st.code = 'OBSERVADA'
        WHERE r.deleted_at IS NULL
    """))).mappings().first()
    slas.append({"name": "SISREC: Observada", "sla_days": 15, "active": r["total"], "breached": r["breached"]})

    # 5. IPR stale (>7d sin transición)
    r = (await db.execute(text("""
        SELECT COUNT(*) AS total,
               COUNT(*) FILTER (WHERE EXTRACT(EPOCH FROM (NOW() - COALESCE(i.phase_entered_at, i.updated_at))) / 86400.0 > 7) AS breached
        FROM core.ipr i
        JOIN ref.category s ON s.id = i.status_id
        WHERE i.deleted_at IS NULL AND s.code NOT IN ('CERRADO', 'ANULADO', 'TERMINADO_ANTICIPADAMENTE')
          AND i.phase_entered_at IS NOT NULL
    """))).mappings().first()
    slas.append({"name": "IPR: Sin movimiento >7d", "sla_days": 7, "active": r["total"], "breached": r["breached"]})

    # 6. Report compliance (periodic reports)
    r = (await db.execute(text("""
        SELECT COUNT(*) AS total
        FROM core.alert a
        WHERE a.subject_type = 'core.ipr' AND a.message LIKE '%informe de avance vencido%'
          AND a.deleted_at IS NULL AND a.resolved_at IS NULL
    """))).mappings().first()
    slas.append({"name": "IPR: Informe periódico", "sla_days": None, "active": None, "breached": r["total"]})

    # 7. Evaluation SLA
    r = (await db.execute(text("""
        SELECT COUNT(*) AS total
        FROM core.alert a
        WHERE a.subject_type = 'core.ipr' AND a.message LIKE '%evaluación excede%'
          AND a.deleted_at IS NULL AND a.resolved_at IS NULL
    """))).mappings().first()
    slas.append({"name": "IPR: Evaluación", "sla_days": None, "active": None, "breached": r["total"]})

    # 8. Pending signatures (actos VISADO)
    r = (await db.execute(text("""
        SELECT COUNT(*) AS total
        FROM core.administrative_act a
        JOIN ref.category st ON st.id = a.state_id AND st.code = 'VISADO'
        WHERE a.deleted_at IS NULL
    """))).mappings().first()
    slas.append({"name": "Actos: Pendientes firma", "sla_days": None, "active": r["total"], "breached": 0})

    # 9. Pending renditions (JEFE_DEPARTAMENTO)
    r = (await db.execute(text("""
        SELECT COUNT(*) AS total
        FROM core.rendition r
        JOIN ref.category st ON st.id = r.state_id
        WHERE r.deleted_at IS NULL AND st.code NOT IN ('APROBADA', 'RECHAZADA')
    """))).mappings().first()
    slas.append({"name": "Rendiciones: Activas", "sla_days": None, "active": r["total"], "breached": 0})

    # 10. Admissibility SLA (NEW)
    r = (await db.execute(text("""
        SELECT COUNT(*) AS total
        FROM core.alert a
        WHERE a.subject_type = 'core.ipr' AND a.message LIKE '%admisibilidad excede%'
          AND a.deleted_at IS NULL AND a.resolved_at IS NULL
    """))).mappings().first()
    slas.append({"name": "IPR: Admisibilidad", "sla_days": 30, "active": None, "breached": r["total"]})

    # 11. Convenio payment SLA (NEW)
    r = (await db.execute(text("""
        SELECT COUNT(*) AS total
        FROM core.alert a
        WHERE a.subject_type = 'core.agreement' AND a.message LIKE '%sin pago de cuota%'
          AND a.deleted_at IS NULL AND a.resolved_at IS NULL
    """))).mappings().first()
    slas.append({"name": "Convenio: Primer pago", "sla_days": 90, "active": None, "breached": r["total"]})

    # 12. Track-phase SLA (NEW)
    r = (await db.execute(text("""
        SELECT COUNT(*) AS total
        FROM core.alert a
        WHERE a.subject_type = 'core.ipr' AND a.message LIKE '%fase excede plazo%'
          AND a.deleted_at IS NULL AND a.resolved_at IS NULL
    """))).mappings().first()
    slas.append({"name": "IPR: Fase por track", "sla_days": None, "active": None, "breached": r["total"]})

    # Compute semáforo
    for sla in slas:
        b = sla["breached"] or 0
        a = sla["active"]
        if a is not None and a > 0:
            pct = (a - b) * 100.0 / a
            sla["compliance_pct"] = round(pct, 1)
            sla["signal"] = "VERDE" if pct >= 90 else "AMARILLO" if pct >= 70 else "ROJO"
        elif b > 0:
            sla["compliance_pct"] = 0.0
            sla["signal"] = "ROJO"
        else:
            sla["compliance_pct"] = 100.0
            sla["signal"] = "VERDE"

    total_monitored = len(slas)
    total_green = sum(1 for s in slas if s["signal"] == "VERDE")
    total_red = sum(1 for s in slas if s["signal"] == "ROJO")

    return {
        "total_monitored": total_monitored,
        "total_green": total_green,
        "total_red": total_red,
        "slas": slas,
    }


# ===========================================================================
# AUDIT TRAIL — txn.event viewer
# ===========================================================================


@router.get("/audit")
async def list_audit_events(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    event_type: str | None = None,
    subject_type: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    search: str | None = None,
):
    """Paginated audit trail from txn.event. ADMIN_SISTEMA only."""
    _require_admin(user)

    conditions = ["1=1"]
    params: dict = {}

    if event_type:
        conditions.append("et.code = :event_type")
        params["event_type"] = event_type
    if subject_type:
        conditions.append("e.subject_type = :subject_type")
        params["subject_type"] = subject_type
    if date_from:
        conditions.append("e.occurred_at >= :date_from::timestamptz")
        params["date_from"] = date_from
    if date_to:
        conditions.append("e.occurred_at < (:date_to::date + 1)::timestamptz")
        params["date_to"] = date_to
    if search:
        conditions.append(
            "(e.data::text ILIKE :search OR e.subject_id::text ILIKE :search)"
        )
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM txn.event e
        JOIN ref.category et ON et.id = e.event_type_id
        LEFT JOIN core."user" u ON u.id = e.actor_id
        LEFT JOIN core.person p ON p.id = u.person_id
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
                e.id::text AS id,
                e.occurred_at,
                et.code AS event_type,
                et.label AS event_type_label,
                e.subject_type,
                e.subject_id::text AS subject_id,
                COALESCE(p.names || ' ' || p.paternal_surname, 'Sistema') AS actor_name,
                e.data
            {base_query}
            ORDER BY e.occurred_at DESC
            LIMIT :limit OFFSET :offset
        """),
        params,
    )
    items = [dict(r) for r in rows_result.mappings().all()]

    # Get distinct event types for filter dropdown
    event_types = (await db.execute(
        text("""
            SELECT DISTINCT et.code, et.label
            FROM txn.event e
            JOIN ref.category et ON et.id = e.event_type_id
            ORDER BY et.code
        """)
    )).mappings().all()

    # Get distinct subject types for filter dropdown
    subject_types = (await db.execute(
        text("SELECT DISTINCT subject_type FROM txn.event ORDER BY subject_type")
    )).mappings().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
        "filters": {
            "event_types": [dict(r) for r in event_types],
            "subject_types": [r["subject_type"] for r in subject_types],
        },
    }


# ===========================================================================
# DOCUMENT QUALITY — core.document statistics
# ===========================================================================


@router.get("/data-quality/documents")
async def get_document_quality(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Document completeness statistics for TDE foundation."""
    _require_admin(user)

    result = await db.execute(
        text("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE d.document_type_id IS NOT NULL) AS with_type,
                COUNT(*) FILTER (WHERE d.storage_url IS NOT NULL AND d.storage_url != '') AS with_url,
                COUNT(*) FILTER (WHERE d.ipr_id IS NOT NULL) AS with_ipr,
                COUNT(*) FILTER (WHERE d.agreement_id IS NOT NULL) AS with_agreement,
                COUNT(*) FILTER (WHERE d.folio_number IS NOT NULL) AS with_folio,
                COUNT(*) FILTER (WHERE d.metadata != '{}' AND d.metadata IS NOT NULL) AS with_metadata
            FROM core.document d
            WHERE d.deleted_at IS NULL
        """)
    )
    doc = dict(result.mappings().first())

    # Breakdown by type
    type_result = await db.execute(
        text("""
            SELECT COALESCE(dt.label, 'Sin tipo') AS type_label, COUNT(*) AS count
            FROM core.document d
            LEFT JOIN ref.category dt ON dt.id = d.document_type_id
            WHERE d.deleted_at IS NULL
            GROUP BY dt.label
            ORDER BY count DESC
        """)
    )
    by_type = [dict(r) for r in type_result.mappings().all()]

    def pct(num: int, den: int) -> float:
        return round(num * 100.0 / den, 1) if den > 0 else 0.0

    return {
        **doc,
        "pct_type": pct(doc["with_type"], doc["total"]),
        "pct_url": pct(doc["with_url"], doc["total"]),
        "pct_ipr": pct(doc["with_ipr"], doc["total"]),
        "pct_agreement": pct(doc["with_agreement"], doc["total"]),
        "pct_folio": pct(doc["with_folio"], doc["total"]),
        "pct_metadata": pct(doc["with_metadata"], doc["total"]),
        "by_type": by_type,
    }
