from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.deps import get_db, CurrentUser
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

    sql = text("""
        SELECT * FROM (
            SELECT id::text, codigo_bip AS code, name, 'ipr' AS entity_type
            FROM core.ipr
            WHERE deleted_at IS NULL
              AND (codigo_bip ILIKE :term OR name ILIKE :term)
            LIMIT :limit
        ) ipr_results

        UNION ALL

        SELECT * FROM (
            SELECT id::text, code, description AS name, 'compromiso' AS entity_type
            FROM core.operational_commitment
            WHERE deleted_at IS NULL
              AND (code ILIKE :term OR description ILIKE :term)
            LIMIT :limit
        ) compromiso_results

        UNION ALL

        SELECT * FROM (
            SELECT id::text, code, description AS name, 'problema' AS entity_type
            FROM core.ipr_problem
            WHERE deleted_at IS NULL
              AND (code ILIKE :term OR description ILIKE :term)
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

    rows = await db.execute(sql, {"term": term, "limit": limit})
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
