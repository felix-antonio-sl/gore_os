import math
from fastapi import APIRouter, Depends, Query, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.presupuesto import (
    PresupuestoListItem,
    PresupuestoDetail,
    PresupuestoCreate,
    PresupuestoUpdate,
    PresupuestoResumen,
    CarryoverItem,
    BudgetCommitmentItem,
)

router = APIRouter(prefix="/api/presupuesto", tags=["presupuesto"])

ADMIN_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"}
MANAGER_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "GOBERNADOR", "JEFE_DEPARTAMENTO"}


def _require_roles(user: dict, *roles: str) -> None:
    if user["role_code"] not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")


def _execution_pct(paid: float | None, current: float | None) -> float:
    if current and current > 0 and paid is not None:
        return round(float(paid) / float(current) * 100, 1)
    return 0.0


async def _get_presupuesto_or_404(presupuesto_id: UUID, db: AsyncSession) -> dict:
    result = await db.execute(
        text("""
            SELECT
                bp.id,
                bp.code,
                bp.name,
                bp.fiscal_year,
                bp.owner_division_id          AS division_id,
                org.name                       AS division_name,
                sub.label                      AS subtitle_label,
                pt.label                       AS program_type_label,
                item_cat.label                 AS item_label,
                alloc_cat.label                AS allocation_label,
                bp.initial_amount,
                bp.current_amount,
                COALESCE(bp.committed_amount, 0) AS committed_amount,
                COALESCE(bp.accrued_amount, 0)   AS accrued_amount,
                COALESCE(bp.paid_amount, 0)      AS paid_amount,
                bp.fndr_amount,
                bp.sectorial_amount,
                bp.created_at
            FROM core.budget_program bp
            LEFT JOIN core.organization org ON org.id = bp.owner_division_id
            LEFT JOIN ref.category sub  ON sub.id  = bp.subtitle_id
            LEFT JOIN ref.category pt   ON pt.id   = bp.program_type_id
            LEFT JOIN ref.category item_cat  ON item_cat.id  = bp.item_id
            LEFT JOIN ref.category alloc_cat ON alloc_cat.id = bp.allocation_id
            WHERE bp.id = :id AND bp.deleted_at IS NULL
        """),
        {"id": str(presupuesto_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programa presupuestario no encontrado")
    return dict(row)


# ---------------------------------------------------------------------------
# GET /api/presupuesto/resumen  — aggregation (MUST come before /{id})
# ---------------------------------------------------------------------------

@router.get("/resumen", response_model=list[PresupuestoResumen])
async def get_presupuesto_resumen(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    group_by: str = Query("division", pattern="^(division|subtitle)$"),
    fiscal_year: int | None = None,
):
    year_filter = f"AND bp.fiscal_year = :fiscal_year" if fiscal_year else ""
    params: dict = {}
    if fiscal_year:
        params["fiscal_year"] = fiscal_year

    if group_by == "division":
        sql = text(f"""
            SELECT
                COALESCE(org.code, 'SIN_DIVISION')           AS group_key,
                COALESCE(org.name, 'Sin división asignada')  AS group_label,
                COALESCE(SUM(bp.initial_amount), 0)          AS initial_amount,
                COALESCE(SUM(bp.current_amount), 0)          AS current_amount,
                COALESCE(SUM(bp.paid_amount), 0)             AS paid_amount,
                COUNT(*)                                      AS program_count
            FROM core.budget_program bp
            LEFT JOIN core.organization org ON org.id = bp.owner_division_id
            WHERE bp.deleted_at IS NULL {year_filter}
            GROUP BY org.code, org.name
            ORDER BY SUM(bp.initial_amount) DESC NULLS LAST
        """)
    else:
        sql = text(f"""
            SELECT
                COALESCE(sub.code, 'SIN_SUBTITULO')          AS group_key,
                COALESCE(sub.label, 'Sin subtítulo')         AS group_label,
                COALESCE(SUM(bp.initial_amount), 0)          AS initial_amount,
                COALESCE(SUM(bp.current_amount), 0)          AS current_amount,
                COALESCE(SUM(bp.paid_amount), 0)             AS paid_amount,
                COUNT(*)                                      AS program_count
            FROM core.budget_program bp
            LEFT JOIN ref.category sub ON sub.id = bp.subtitle_id
            WHERE bp.deleted_at IS NULL {year_filter}
            GROUP BY sub.code, sub.label
            ORDER BY SUM(bp.initial_amount) DESC NULLS LAST
        """)

    rows = (await db.execute(sql, params)).mappings().all()
    return [
        PresupuestoResumen(
            group_key=r["group_key"],
            group_label=r["group_label"],
            initial_amount=r["initial_amount"],
            current_amount=r["current_amount"],
            paid_amount=r["paid_amount"],
            execution_pct=_execution_pct(r["paid_amount"], r["current_amount"]),
            program_count=r["program_count"],
        )
        for r in rows
    ]


# ---------------------------------------------------------------------------
# GET /api/presupuesto — List (paginated, filtered)
# ---------------------------------------------------------------------------

@router.get("", response_model=PaginatedResponse)
async def list_presupuesto(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    fiscal_year: int | None = None,
    division_id: UUID | None = None,
    subtitle: str | None = None,
    search: str | None = None,
):
    role = user["role_code"]
    params: dict = {}
    conditions = ["bp.deleted_at IS NULL"]

    # JEFE_DIVISION: only own division
    effective_division_id = division_id
    if role == "JEFE_DIVISION" and not division_id:
        effective_division_id = user.get("division_id")

    if fiscal_year:
        conditions.append("bp.fiscal_year = :fiscal_year")
        params["fiscal_year"] = fiscal_year

    if effective_division_id:
        conditions.append("bp.owner_division_id = :division_id")
        params["division_id"] = str(effective_division_id)

    if subtitle:
        conditions.append("sub.code = :subtitle")
        params["subtitle"] = subtitle

    if search:
        conditions.append("(bp.code ILIKE :search OR bp.name ILIKE :search)")
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core.budget_program bp
        LEFT JOIN core.organization org ON org.id = bp.owner_division_id
        LEFT JOIN ref.category sub  ON sub.id  = bp.subtitle_id
        LEFT JOIN ref.category pt   ON pt.id   = bp.program_type_id
        WHERE {where_clause}
    """

    count_result = await db.execute(text(f"SELECT COUNT(*) AS total {base_query}"), params)
    total = count_result.scalar() or 0

    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows_result = await db.execute(
        text(f"""
            SELECT
                bp.id,
                bp.code,
                bp.name,
                bp.fiscal_year,
                bp.owner_division_id              AS division_id,
                org.name                           AS division_name,
                sub.label                          AS subtitle_label,
                pt.label                           AS program_type_label,
                bp.initial_amount,
                bp.current_amount,
                COALESCE(bp.committed_amount, 0)   AS committed_amount,
                COALESCE(bp.accrued_amount, 0)     AS accrued_amount,
                COALESCE(bp.paid_amount, 0)        AS paid_amount
            {base_query}
            ORDER BY bp.fiscal_year DESC, bp.initial_amount DESC NULLS LAST
            LIMIT :limit OFFSET :offset
        """),
        params,
    )
    rows = rows_result.mappings().all()

    items = [
        PresupuestoListItem(
            id=r["id"],
            code=r["code"],
            name=r["name"],
            fiscal_year=r["fiscal_year"],
            division_id=r["division_id"],
            division_name=r["division_name"],
            subtitle_label=r["subtitle_label"],
            program_type_label=r["program_type_label"],
            initial_amount=r["initial_amount"],
            current_amount=r["current_amount"],
            committed_amount=r["committed_amount"],
            accrued_amount=r["accrued_amount"],
            paid_amount=r["paid_amount"],
            execution_pct=_execution_pct(r["paid_amount"], r["current_amount"]),
        )
        for r in rows
    ]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0,
    )


# ---------------------------------------------------------------------------
# GET /api/presupuesto/cdps-por-ipr/{ipr_id} — CDPs linked to an IPR
# ---------------------------------------------------------------------------

@router.get("/cdps-por-ipr/{ipr_id}", response_model=list[BudgetCommitmentItem])
async def list_cdps_by_ipr(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all budget commitments (CDPs) linked to a specific IPR."""
    result = await db.execute(
        text("""
            SELECT
                bc.id,
                bc.commitment_number,
                bc.amount,
                bc.issued_at,
                bc.expires_at,
                st.label  AS status_label,
                bc.ipr_id,
                ipr.codigo_bip AS ipr_codigo_bip
            FROM core.budget_commitment bc
            LEFT JOIN ref.category st ON st.id = bc.status_id
            LEFT JOIN core.ipr ipr ON ipr.id = bc.ipr_id
            WHERE bc.ipr_id = :ipr_id AND bc.deleted_at IS NULL
            ORDER BY bc.issued_at DESC
        """),
        {"ipr_id": str(ipr_id)},
    )
    return [BudgetCommitmentItem(**dict(r)) for r in result.mappings().all()]


# ---------------------------------------------------------------------------
# GET /api/presupuesto/{id} — Detail
# ---------------------------------------------------------------------------

@router.get("/{presupuesto_id}", response_model=PresupuestoDetail)
async def get_presupuesto(
    presupuesto_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_presupuesto_or_404(presupuesto_id, db)

    # Carryovers
    co_result = await db.execute(
        text("""
            SELECT id, fiscal_year, amount
            FROM core.budget_carryover
            WHERE budget_program_id = :pid
            ORDER BY fiscal_year DESC
        """),
        {"pid": str(presupuesto_id)},
    )
    carryovers = [CarryoverItem(**dict(r)) for r in co_result.mappings().all()]

    # Budget commitments
    bc_result = await db.execute(
        text("""
            SELECT
                bc.id,
                bc.commitment_number,
                bc.amount,
                bc.issued_at,
                bc.expires_at,
                st.label  AS status_label,
                bc.ipr_id,
                ipr.codigo_bip AS ipr_codigo_bip
            FROM core.budget_commitment bc
            LEFT JOIN ref.category st ON st.id = bc.status_id
            LEFT JOIN core.ipr ipr ON ipr.id = bc.ipr_id
            WHERE bc.budget_program_id = :pid AND bc.deleted_at IS NULL
            ORDER BY bc.issued_at DESC
        """),
        {"pid": str(presupuesto_id)},
    )
    budget_commitments = [BudgetCommitmentItem(**dict(r)) for r in bc_result.mappings().all()]

    return PresupuestoDetail(
        **row,
        execution_pct=_execution_pct(row.get("paid_amount"), row.get("current_amount")),
        carryovers=carryovers,
        budget_commitments=budget_commitments,
    )


# ---------------------------------------------------------------------------
# POST /api/presupuesto — Create
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_presupuesto(
    body: PresupuestoCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, *ADMIN_ROLES)

    # Check unique code+fiscal_year
    dup = await db.execute(
        text("SELECT 1 FROM core.budget_program WHERE code = :code AND fiscal_year = :year AND deleted_at IS NULL"),
        {"code": body.code, "year": body.fiscal_year},
    )
    if dup.scalar():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un programa con ese código para el año fiscal indicado")

    result = await db.execute(
        text("""
            INSERT INTO core.budget_program (
                code, name, fiscal_year,
                program_type_id, subtitle_id, item_id, allocation_id, owner_division_id,
                initial_amount, current_amount,
                committed_amount, accrued_amount, paid_amount,
                created_by_id, created_at, updated_at
            ) VALUES (
                :code, :name, :fiscal_year,
                :program_type_id, :subtitle_id, :item_id, :allocation_id, :owner_division_id,
                :initial_amount, :current_amount,
                0, 0, 0,
                :created_by_id, NOW(), NOW()
            )
            RETURNING id, code
        """),
        {
            "code": body.code,
            "name": body.name,
            "fiscal_year": body.fiscal_year,
            "program_type_id": str(body.program_type_id) if body.program_type_id else None,
            "subtitle_id": str(body.subtitle_id) if body.subtitle_id else None,
            "item_id": str(body.item_id) if body.item_id else None,
            "allocation_id": str(body.allocation_id) if body.allocation_id else None,
            "owner_division_id": str(body.owner_division_id) if body.owner_division_id else None,
            "initial_amount": body.initial_amount,
            "current_amount": body.current_amount if body.current_amount is not None else body.initial_amount,
            "created_by_id": str(user["id"]),
        },
    )
    await db.commit()
    row = result.mappings().first()
    return {"id": row["id"], "code": row["code"]}


# ---------------------------------------------------------------------------
# PATCH /api/presupuesto/{id} — Update amounts
# ---------------------------------------------------------------------------

@router.patch("/{presupuesto_id}")
async def update_presupuesto(
    presupuesto_id: UUID,
    body: PresupuestoUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_presupuesto_or_404(presupuesto_id, db)

    # JEFE_DIVISION only own division
    role = user["role_code"]
    if role == "JEFE_DIVISION":
        if str(row.get("division_id")) != str(user.get("division_id")):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puede modificar programas de su división")
    elif role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")

    # Allowlist: solo estas columnas son actualizables via PATCH
    UPDATABLE_COLUMNS = {"initial_amount", "current_amount", "committed_amount", "accrued_amount", "paid_amount"}

    updates = {k: v for k, v in body.model_dump(exclude_none=True).items() if k in UPDATABLE_COLUMNS}
    if not updates:
        return {"message": "Sin cambios"}

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(presupuesto_id)
    updates["updated_by_id"] = str(user["id"])

    await db.execute(
        text(f"UPDATE core.budget_program SET {set_clauses}, updated_at = NOW(), updated_by_id = :updated_by_id WHERE id = :id"),
        updates,
    )
    await db.commit()
    return {"message": "Actualizado correctamente"}
