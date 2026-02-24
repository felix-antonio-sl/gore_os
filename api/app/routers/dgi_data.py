from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.schemas.dgi import IndicatorItem, DataSourceItem

router = APIRouter(prefix="/api/dgi/data", tags=["dgi"])


# ---------------------------------------------------------------------------
# GET /api/dgi/data/indicators — All indicators (with optional dimension filter)
# ---------------------------------------------------------------------------
@router.get("/indicators", response_model=list[IndicatorItem])
async def list_indicators(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    dimension: str | None = Query(None, description="Filter by dimension code (e.g. PRESUPUESTO, TDE)"),
):
    """
    List all DGI indicators.

    Optional filter:
    - dimension: filter by dgi_indicator_dimension code
    """
    conditions = ["1=1"]
    params: dict = {}

    if dimension:
        conditions.append("dim.code = :dimension")
        params["dimension"] = dimension.upper()

    where_clause = " AND ".join(conditions)

    sql = text(f"""
        SELECT
            i.id,
            i.code,
            i.name,
            dim.code        AS dimension,
            i.current_value,
            i.target_value,
            i.unit,
            sig.code        AS signal,
            i.trend,
            i.description,
            i.last_updated_at
        FROM core.dgi_indicator i
        JOIN ref.category dim ON dim.id = i.dimension_id
        LEFT JOIN ref.category sig ON sig.id = i.signal_id
        WHERE {where_clause}
        ORDER BY
            CASE sig.code
                WHEN 'ROJO'     THEN 1
                WHEN 'AMARILLO' THEN 2
                WHEN 'VERDE'    THEN 3
                ELSE 4
            END,
            dim.code,
            i.name
    """)

    rows = (await db.execute(sql, params)).mappings().all()

    return [
        IndicatorItem(
            id=r["id"],
            code=r["code"],
            name=r["name"],
            dimension=r["dimension"],
            current_value=r["current_value"],
            target_value=r["target_value"],
            unit=r["unit"],
            signal=r["signal"],
            trend=r["trend"],
            description=r["description"],
            last_updated_at=r["last_updated_at"],
        )
        for r in rows
    ]


# ---------------------------------------------------------------------------
# GET /api/dgi/data/indicators/{id} — Single indicator detail
# ---------------------------------------------------------------------------
@router.get("/indicators/{indicator_id}", response_model=IndicatorItem)
async def get_indicator(
    indicator_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a single DGI indicator by UUID.
    """
    sql = text("""
        SELECT
            i.id,
            i.code,
            i.name,
            dim.code        AS dimension,
            i.current_value,
            i.target_value,
            i.unit,
            sig.code        AS signal,
            i.trend,
            i.description,
            i.last_updated_at
        FROM core.dgi_indicator i
        JOIN ref.category dim ON dim.id = i.dimension_id
        LEFT JOIN ref.category sig ON sig.id = i.signal_id
        WHERE i.id = :id
    """)

    row = (await db.execute(sql, {"id": str(indicator_id)})).mappings().first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indicador no encontrado",
        )

    return IndicatorItem(
        id=row["id"],
        code=row["code"],
        name=row["name"],
        dimension=row["dimension"],
        current_value=row["current_value"],
        target_value=row["target_value"],
        unit=row["unit"],
        signal=row["signal"],
        trend=row["trend"],
        description=row["description"],
        last_updated_at=row["last_updated_at"],
    )


# ---------------------------------------------------------------------------
# GET /api/dgi/data/sources — Data source status
# ---------------------------------------------------------------------------
@router.get("/sources", response_model=list[DataSourceItem])
async def list_data_sources(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    source_status: str | None = Query(None, alias="status", description="Filter by status code"),
):
    """
    List all DGI data source statuses.

    Optional filter:
    - status: filter by dgi_source_status code (e.g. ACTUALIZADO, ATRASADO, SIN_DATOS)
    """
    conditions = ["1=1"]
    params: dict = {}

    if source_status:
        conditions.append("st.code = :source_status")
        params["source_status"] = source_status.upper()

    where_clause = " AND ".join(conditions)

    sql = text(f"""
        SELECT
            ds.id,
            org.name        AS division_name,
            ds.source_name,
            st.code         AS status,
            ds.last_data_at,
            ds.days_behind
        FROM core.dgi_data_source_status ds
        LEFT JOIN core.organization org ON org.id = ds.division_id
        JOIN ref.category st ON st.id = ds.status_id
        WHERE {where_clause}
        ORDER BY
            CASE st.code
                WHEN 'SIN_DATOS'   THEN 1
                WHEN 'ATRASADO'    THEN 2
                WHEN 'ACTUALIZADO' THEN 3
                ELSE 4
            END,
            ds.days_behind DESC,
            org.name NULLS LAST
    """)

    rows = (await db.execute(sql, params)).mappings().all()

    return [
        DataSourceItem(
            id=r["id"],
            division_name=r["division_name"],
            source_name=r["source_name"],
            status=r["status"],
            last_data_at=r["last_data_at"],
            days_behind=r["days_behind"] or 0,
        )
        for r in rows
    ]
