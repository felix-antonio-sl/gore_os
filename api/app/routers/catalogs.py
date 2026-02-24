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
    params = {}
    if division_id:
        query += " AND u.division_id = :div"
        params["div"] = division_id
    query += " ORDER BY p.paternal_surname, p.names"
    result = await db.execute(text(query), params)
    return [dict(r) for r in result.mappings().all()]
