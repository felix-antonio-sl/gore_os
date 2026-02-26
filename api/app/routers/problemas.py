import math
from fastapi import APIRouter, Depends, Query, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import WRITE_OPERATIONAL_ROLES
from app.schemas.problema import ProblemaCreate, ProblemaDetail, ProblemaListItem, ProblemaUpdate

router = APIRouter(prefix="/api/problemas", tags=["problemas"])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

OPEN_STATES = ("ABIERTO", "EN_GESTION")


def _require_roles(user: dict, *roles: str) -> None:
    if user["role_code"] not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")


async def _get_problema_or_404(problema_id: UUID, db: AsyncSession) -> dict:
    result = await db.execute(
        text("""
            SELECT
                p.id, p.code, p.ipr_id, p.description, p.impact_description,
                p.proposed_solution, p.solution_applied,
                p.detected_at, p.resolved_at, p.created_at,
                ipr.codigo_bip                              AS ipr_codigo_bip,
                ipr.name                                    AS ipr_name,
                pt.code                                     AS problem_type,
                pt.label                                    AS problem_type_label,
                imp.code                                    AS impact,
                imp.label                                   AS impact_label,
                st.code                                     AS state,
                st.label                                    AS state_label,
                (CURRENT_DATE - p.detected_at::date)        AS days_open,
                (dp.names || ' ' || dp.paternal_surname)    AS detected_by_name,
                (rp.names || ' ' || rp.paternal_surname)    AS resolved_by_name
            FROM core.ipr_problem p
            JOIN core.ipr ipr ON p.ipr_id = ipr.id
            JOIN ref.category pt ON p.problem_type_id = pt.id
            JOIN ref.category st ON p.state_id = st.id
            LEFT JOIN ref.category imp ON p.impact_id = imp.id
            LEFT JOIN core."user" du ON p.detected_by_id = du.id
            LEFT JOIN core.person dp ON du.person_id = dp.id
            LEFT JOIN core."user" ru ON p.resolved_by_id = ru.id
            LEFT JOIN core.person rp ON ru.person_id = rp.id
            WHERE p.id = :id AND p.deleted_at IS NULL
        """),
        {"id": str(problema_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problema no encontrado")
    return dict(row)


async def _next_pr_code(db: AsyncSession) -> str:
    result = await db.execute(
        text("""
            SELECT MAX(CAST(SUBSTRING(code FROM 4) AS INTEGER)) AS max_seq
            FROM core.ipr_problem
            WHERE code ~ '^PR-[0-9]+$'
        """)
    )
    row = result.mappings().first()
    next_seq = (row["max_seq"] or 0) + 1
    return f"PR-{next_seq:05d}"


# ---------------------------------------------------------------------------
# GET /api/problemas — List (paginated, filtered)
# ---------------------------------------------------------------------------

@router.get("")
async def list_problemas(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    state: str | None = None,
    problem_type: str | None = None,
    ipr_id: UUID | None = None,
    search: str | None = None,
):
    role = user["role_code"]
    params: dict = {}
    conditions = ["p.deleted_at IS NULL"]

    if state:
        conditions.append("st.code = :state")
        params["state"] = state

    if problem_type:
        conditions.append("pt.code = :problem_type")
        params["problem_type"] = problem_type

    if ipr_id:
        conditions.append("p.ipr_id = :ipr_id")
        params["ipr_id"] = str(ipr_id)

    if search:
        conditions.append("p.description ILIKE :search")
        params["search"] = f"%{search}%"

    # JEFE_DIVISION: filter problems of IPRs whose responsible division matches user's division
    if role == "JEFE_DIVISION" and user.get("division_id"):
        conditions.append("""
            p.ipr_id IN (
                SELECT i.id FROM core.ipr i
                JOIN core.ipr_party ip2 ON ip2.ipr_id = i.id
                JOIN core."user" u2 ON ip2.party_id = u2.id
                    AND ip2.party_role_id = (
                        SELECT id FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'EJECUTOR'
                    )
                WHERE u2.division_id = :jefe_division_id
            )
        """)
        params["jefe_division_id"] = str(user["division_id"])

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core.ipr_problem p
        JOIN core.ipr ipr ON p.ipr_id = ipr.id
        JOIN ref.category pt ON p.problem_type_id = pt.id
        JOIN ref.category st ON p.state_id = st.id
        LEFT JOIN ref.category imp ON p.impact_id = imp.id
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
                p.id, p.code, p.ipr_id, p.description,
                ipr.codigo_bip                          AS ipr_codigo_bip,
                ipr.name                                AS ipr_name,
                pt.code                                 AS problem_type,
                pt.label                                AS problem_type_label,
                imp.code                                AS impact,
                imp.label                               AS impact_label,
                st.code                                 AS state,
                st.label                                AS state_label,
                (CURRENT_DATE - p.detected_at::date)    AS days_open,
                p.detected_at
            {base_query}
            ORDER BY
                CASE WHEN st.code IN ('ABIERTO', 'EN_GESTION') THEN 0 ELSE 1 END ASC,
                p.detected_at DESC
            LIMIT :limit OFFSET :offset
        """),
        params,
    )
    rows = rows_result.mappings().all()
    items = [ProblemaListItem(**dict(r)) for r in rows]
    total_pages = math.ceil(total / page_size) if page_size else 0

    return {
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------------------
# GET /api/problemas/{id} — Detail
# ---------------------------------------------------------------------------

@router.get("/{problema_id}")
async def get_problema(
    problema_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_problema_or_404(problema_id, db)
    detail = ProblemaDetail(**row)
    return detail.model_dump()


# ---------------------------------------------------------------------------
# POST /api/problemas — Create
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_problema(
    data: ProblemaCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, *WRITE_OPERATIONAL_ROLES)
    code = await _next_pr_code(db)

    result = await db.execute(
        text("""
            INSERT INTO core.ipr_problem (
                code, ipr_id, problem_type_id, impact_id, description,
                impact_description, proposed_solution,
                detected_by_id, detected_at,
                state_id, created_by_id
            ) VALUES (
                :code, :ipr_id, :problem_type_id, :impact_id, :description,
                :impact_description, :proposed_solution,
                :detected_by_id, NOW(),
                (SELECT id FROM ref.category WHERE scheme = 'problem_state' AND code = 'ABIERTO'),
                :created_by_id
            )
            RETURNING id, code
        """),
        {
            "code": code,
            "ipr_id": str(data.ipr_id),
            "problem_type_id": str(data.problem_type_id),
            "impact_id": str(data.impact_id) if data.impact_id else None,
            "description": data.description,
            "impact_description": data.impact_description,
            "proposed_solution": data.proposed_solution,
            "detected_by_id": str(user["id"]),
            "created_by_id": str(user["id"]),
        },
    )
    await db.commit()
    row = result.mappings().first()
    return {"id": str(row["id"]), "code": row["code"]}


# ---------------------------------------------------------------------------
# PATCH /api/problemas/{id} — Update
# ---------------------------------------------------------------------------

@router.patch("/{problema_id}")
async def update_problema(
    problema_id: UUID,
    data: ProblemaUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, *WRITE_OPERATIONAL_ROLES)
    # Verify the problem exists
    current = await _get_problema_or_404(problema_id, db)

    # Build SET clauses dynamically based on provided fields
    set_parts = ["updated_at = NOW()"]
    params: dict = {"id": str(problema_id)}

    if data.proposed_solution is not None:
        set_parts.append("proposed_solution = :proposed_solution")
        params["proposed_solution"] = data.proposed_solution

    if data.solution_applied is not None:
        set_parts.append("solution_applied = :solution_applied")
        params["solution_applied"] = data.solution_applied

    if data.state_id is not None:
        # Verify the category id exists and belongs to problem_state scheme
        cat_result = await db.execute(
            text("""
                SELECT code FROM ref.category
                WHERE id = :cat_id AND scheme = 'problem_state'
            """),
            {"cat_id": str(data.state_id)},
        )
        cat_row = cat_result.mappings().first()
        if not cat_row:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="state_id inválido: debe pertenecer al esquema 'problem_state'",
            )
        set_parts.append("state_id = :state_id")
        params["state_id"] = str(data.state_id)

        if cat_row["code"] == "RESUELTO":
            set_parts.append("resolved_by_id = :resolved_by")
            set_parts.append("resolved_at = NOW()")
            params["resolved_by"] = str(user["id"])

    if len(set_parts) == 1:
        # Only updated_at — nothing meaningful was sent
        return await _get_problema_or_404(problema_id, db)

    set_clause = ", ".join(set_parts)
    await db.execute(
        text(f"""
            UPDATE core.ipr_problem
            SET {set_clause}
            WHERE id = :id AND deleted_at IS NULL
        """),
        params,
    )
    await db.commit()

    updated = await _get_problema_or_404(problema_id, db)
    return ProblemaDetail(**updated).model_dump()
