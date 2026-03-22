from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.deps import get_db, CurrentUser
from app.core.scope import GLOBAL_SCOPE_ROLES, DIVISION_SCOPE_ROLES
from app.core.security import PERSONAL_SCOPE_ROLES
from app.schemas.search import SearchResponse, SearchResult

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def global_search(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    q: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(default=5, ge=1, le=20),
):
    """Búsqueda global en IPR, compromisos, problemas y personas."""
    term = f"%{q}%"
    role = user.get("role_code")
    params: dict = {"term": term, "limit": limit}

    # Build scope clauses per entity type
    ipr_scope = ""
    commitment_scope = ""
    problem_scope = ""

    if role not in GLOBAL_SCOPE_ROLES:
        if role in DIVISION_SCOPE_ROLES:
            div_id = user.get("division_id")
            if div_id:
                params["div_id"] = str(div_id)
                ipr_scope = " AND i.sponsor_division_id = CAST(:div_id AS uuid)"
                commitment_scope = (
                    " AND oc.ipr_id IN (SELECT id FROM core.ipr"
                    " WHERE sponsor_division_id = CAST(:div_id AS uuid)"
                    " AND deleted_at IS NULL)"
                )
                problem_scope = (
                    " AND pr.ipr_id IN (SELECT id FROM core.ipr"
                    " WHERE sponsor_division_id = CAST(:div_id AS uuid)"
                    " AND deleted_at IS NULL)"
                )
        elif role in PERSONAL_SCOPE_ROLES:
            params["uid"] = str(user["id"])
            ipr_scope = (
                " AND (i.assignee_id = CAST(:uid AS uuid)"
                " OR i.formulator_id = CAST(:uid AS uuid))"
            )
            commitment_scope = " AND oc.responsible_id = CAST(:uid AS uuid)"
            problem_scope = (
                " AND pr.ipr_id IN (SELECT id FROM core.ipr"
                " WHERE (assignee_id = CAST(:uid AS uuid)"
                " OR formulator_id = CAST(:uid AS uuid))"
                " AND deleted_at IS NULL)"
            )

    sql = text(f"""
        SELECT * FROM (
            SELECT i.id::text, i.codigo_bip AS code, i.name, 'ipr' AS entity_type
            FROM core.ipr i
            WHERE i.deleted_at IS NULL
              AND (i.codigo_bip ILIKE :term OR i.name ILIKE :term)
              {ipr_scope}
            LIMIT :limit
        ) ipr_results

        UNION ALL

        SELECT * FROM (
            SELECT oc.id::text, oc.code, oc.description AS name, 'compromiso' AS entity_type
            FROM core.operational_commitment oc
            WHERE oc.deleted_at IS NULL
              AND (oc.code ILIKE :term OR oc.description ILIKE :term)
              {commitment_scope}
            LIMIT :limit
        ) compromiso_results

        UNION ALL

        SELECT * FROM (
            SELECT pr.id::text, pr.code, pr.description AS name, 'problema' AS entity_type
            FROM core.ipr_problem pr
            WHERE pr.deleted_at IS NULL
              AND (pr.code ILIKE :term OR pr.description ILIKE :term)
              {problem_scope}
            LIMIT :limit
        ) problema_results

        UNION ALL

        SELECT * FROM (
            SELECT p.id::text, NULL AS code,
                   p.names || ' ' || p.paternal_surname AS name,
                   'persona' AS entity_type
            FROM core.person p
            WHERE p.deleted_at IS NULL
              AND (p.names ILIKE :term OR p.paternal_surname ILIKE :term)
            LIMIT :limit
        ) persona_results
    """)

    rows = await db.execute(sql, params)
    results = [
        SearchResult(
            id=str(r["id"]),
            code=r["code"],
            name=r["name"],
            entity_type=r["entity_type"],
        )
        for r in rows.mappings()
    ]

    return SearchResponse(results=results)
