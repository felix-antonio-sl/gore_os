from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.schemas.dgi import ReportItem

router = APIRouter(prefix="/api/dgi/reports", tags=["dgi"])


# ---------------------------------------------------------------------------
# GET /api/dgi/reports — List reports (with optional type and status filters)
# ---------------------------------------------------------------------------
@router.get("", response_model=list[ReportItem])
async def list_reports(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    report_type: str | None = Query(None, description="Filter by report type code (e.g. SEMANAL, MENSUAL, COMITE)"),
    report_status: str | None = Query(None, alias="status", description="Filter by report status code (e.g. BORRADOR, ENVIADO, ARCHIVADO)"),
):
    """
    List DGI reports.

    Optional filters:
    - report_type: filter by dgi_report_type code
    - status: filter by dgi_report_status code
    """
    conditions = ["1=1"]
    params: dict = {}

    if report_type:
        conditions.append("rt.code = :report_type")
        params["report_type"] = report_type.upper()

    if report_status:
        conditions.append("st.code = :report_status")
        params["report_status"] = report_status.upper()

    where_clause = " AND ".join(conditions)

    sql = text(f"""
        SELECT
            r.id,
            r.code,
            rt.code         AS report_type,
            st.code         AS status,
            r.title,
            r.period_start,
            r.period_end,
            r.recipient,
            p.names || ' ' || p.paternal_surname AS generated_by_name,
            r.sent_at,
            r.created_at
        FROM core.dgi_report r
        JOIN ref.category rt ON rt.id = r.report_type_id
        JOIN ref.category st ON st.id = r.status_id
        LEFT JOIN core."user" u ON u.id = r.generated_by_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE {where_clause}
        ORDER BY
            CASE st.code
                WHEN 'BORRADOR'  THEN 1
                WHEN 'ENVIADO'   THEN 2
                WHEN 'ARCHIVADO' THEN 3
                ELSE 4
            END,
            r.created_at DESC
    """)

    rows = (await db.execute(sql, params)).mappings().all()

    return [
        ReportItem(
            id=r["id"],
            code=r["code"],
            report_type=r["report_type"],
            status=r["status"],
            title=r["title"],
            period_start=r["period_start"],
            period_end=r["period_end"],
            recipient=r["recipient"],
            generated_by_name=r["generated_by_name"],
            sent_at=r["sent_at"],
            created_at=r["created_at"],
        )
        for r in rows
    ]
