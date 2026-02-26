from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import CurrentUser

router = APIRouter(prefix="/api/catalogs", tags=["catalogs"])


@router.get("/categories/{scheme}")
async def get_categories(scheme: str, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT id, code, label, description FROM ref.category WHERE scheme = :s ORDER BY sort_order"),
        {"s": scheme},
    )
    return [dict(r) for r in result.mappings().all()]


@router.get("/commitment-types")
async def get_commitment_types(user: CurrentUser, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT id, code, name, description, default_days FROM ref.operational_commitment_type WHERE is_active = true ORDER BY sort_order")
    )
    return [dict(r) for r in result.mappings().all()]


@router.get("/users")
async def get_users_list(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    division_id: str | None = None,
    search: str | None = None,
):
    query = """
        SELECT u.id, u.email, u.division_id, p.names as nombre, p.paternal_surname as apellido_paterno,
               c.code as role_code, o.name as division_name
        FROM core."user" u
        JOIN core.person p ON u.person_id = p.id
        JOIN ref.category c ON u.system_role_id = c.id
        LEFT JOIN core.organization o ON u.division_id = o.id
        WHERE u.is_active = true AND u.deleted_at IS NULL
    """
    params: dict = {}
    if division_id:
        query += " AND u.division_id = :div"
        params["div"] = division_id
    if search:
        query += " AND (p.names ILIKE :s OR p.paternal_surname ILIKE :s OR u.email ILIKE :s)"
        params["s"] = f"%{search}%"
    query += " ORDER BY p.paternal_surname, p.names LIMIT 50"
    result = await db.execute(text(query), params)
    return [dict(r) for r in result.mappings().all()]


@router.get("/iprs")
async def get_iprs_list(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    search: str | None = None,
):
    query = """
        SELECT i.id, i.codigo_bip, i.name
        FROM core.ipr i
        WHERE i.deleted_at IS NULL
    """
    params: dict = {}
    if search:
        query += " AND (i.codigo_bip ILIKE :search OR i.name ILIKE :search)"
        params["search"] = f"%{search}%"
    query += " ORDER BY i.codigo_bip LIMIT 200"
    result = await db.execute(text(query), params)
    return [dict(r) for r in result.mappings().all()]


@router.get("/organizations")
async def get_organizations_list(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    search: str | None = None,
):
    query = """
        SELECT o.id, o.code, o.name, COALESCE(o.short_name, o.name) AS short_name,
               c.code AS org_type, o.rut
        FROM core.organization o
        JOIN ref.category c ON o.org_type_id = c.id
        WHERE o.deleted_at IS NULL
    """
    params: dict = {}
    if search:
        query += " AND (o.name ILIKE :s OR o.code ILIKE :s OR o.rut ILIKE :s)"
        params["s"] = f"%{search}%"
    query += " ORDER BY o.name LIMIT 50"
    result = await db.execute(text(query), params)
    return [dict(r) for r in result.mappings().all()]


@router.get("/territories")
async def get_territories_list(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("""
            SELECT t.id, t.code, t.name, c.code AS territory_type
            FROM core.territory t
            JOIN ref.category c ON c.id = t.territory_type_id
            WHERE t.deleted_at IS NULL
            ORDER BY c.code, t.name
        """)
    )
    return [dict(r) for r in result.mappings().all()]


@router.get("/divisions")
async def get_divisions_list(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("""
            SELECT o.id, o.code, o.name
            FROM core.organization o
            JOIN ref.category c ON o.org_type_id = c.id
            WHERE o.deleted_at IS NULL
              AND c.code IN ('DIVISION', 'GORE')
            ORDER BY o.name
        """)
    )
    return [dict(r) for r in result.mappings().all()]
