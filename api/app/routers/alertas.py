import math
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import WRITE_OPERATIONAL_ROLES
from app.core.audit import record_event
from app.core.alerts import apply_alert_scope
from app.schemas.alerta import AlertaListItem, AlertaAttendRequest

router = APIRouter(prefix="/api/alertas", tags=["alertas"])


def _require_roles(user: dict, *roles: str) -> None:
    if user["role_code"] not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")

# ---------------------------------------------------------------------------
# Severity ordering: CRITICO > ALTO > ATENCION > INFO
# ---------------------------------------------------------------------------

SEVERITY_ORDER = """
    CASE sev.code
        WHEN 'CRITICO'  THEN 1
        WHEN 'ALTO'     THEN 2
        WHEN 'ATENCION' THEN 3
        WHEN 'INFO'     THEN 4
        ELSE 5
    END
"""

# Subject label subquery — resolves human-readable label based on subject_type
SUBJECT_LABEL_SUBQUERY = """
    CASE a.subject_type
        WHEN 'core.ipr' THEN (
            SELECT i.codigo_bip || ' - ' || i.name
            FROM core.ipr i WHERE i.id = a.subject_id
        )
        WHEN 'core.operational_commitment' THEN (
            SELECT oc.code || ': ' || oc.description
            FROM core.operational_commitment oc WHERE oc.id = a.subject_id
        )
        WHEN 'core.ipr_problem' THEN (
            SELECT pr.code || ': ' || pr.description
            FROM core.ipr_problem pr WHERE pr.id = a.subject_id
        )
        WHEN 'core.organization' THEN (
            SELECT org.name FROM core.organization org WHERE org.id = a.subject_id
        )
        ELSE NULL
    END
"""


# ---------------------------------------------------------------------------
# GET /api/alertas — List (paginated, filtered)
# ---------------------------------------------------------------------------

@router.get("")
async def list_alertas(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    alerta_id: UUID | None = None,
    severity: str | None = None,
    active_only: bool = True,
    alert_type: str | None = None,
    subject_type: str | None = None,
    subject_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    params: dict = {}
    conditions = ["a.deleted_at IS NULL"]

    if alerta_id:
        conditions.append("a.id = :alerta_id")
        params["alerta_id"] = str(alerta_id)

    if date_from:
        conditions.append("a.triggered_at::date >= :date_from")
        params["date_from"] = str(date_from)
    if date_to:
        conditions.append("a.triggered_at::date <= :date_to")
        params["date_to"] = str(date_to)

    if active_only:
        conditions.append("a.resolved_at IS NULL")

    if subject_type:
        conditions.append("a.subject_type = :subject_type")
        params["subject_type"] = subject_type
    if subject_id:
        conditions.append("a.subject_id = :subject_id")
        params["subject_id"] = subject_id

    if severity:
        conditions.append("sev.code = :severity")
        params["severity"] = severity

    if alert_type:
        conditions.append("at_cat.code = :alert_type")
        params["alert_type"] = alert_type

    apply_alert_scope(conditions, params, user)

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core.alert a
        JOIN ref.category at_cat ON a.alert_type_id = at_cat.id
        LEFT JOIN ref.category sev ON a.severity_id = sev.id
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
                a.id,
                at_cat.code                 AS alert_type,
                at_cat.label                AS alert_type_label,
                sev.code                    AS severity,
                sev.label                   AS severity_label,
                a.subject_type,
                a.subject_id,
                ({SUBJECT_LABEL_SUBQUERY})  AS subject_label,
                a.message,
                a.triggered_at,
                a.acknowledged_at,
                a.attended_at,
                a.resolved_at
            {base_query}
            ORDER BY
                {SEVERITY_ORDER} ASC,
                a.triggered_at DESC
            LIMIT :limit OFFSET :offset
        """),
        params,
    )
    rows = rows_result.mappings().all()
    items = [AlertaListItem(**dict(r), can_attend=user["role_code"] in WRITE_OPERATIONAL_ROLES and not r["resolved_at"]) for r in rows]
    total_pages = math.ceil(total / page_size) if page_size else 0

    return {
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------------------
# POST /api/alertas/{id}/atender
# ---------------------------------------------------------------------------

@router.post("/{alerta_id}/atender")
async def attend_alerta(
    alerta_id: UUID,
    body: AlertaAttendRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, *WRITE_OPERATIONAL_ROLES)
    conditions = ["a.id = :id", "a.deleted_at IS NULL"]
    params = {"id": str(alerta_id)}
    apply_alert_scope(conditions, params, user)
    check_result = await db.execute(
        text(f"SELECT a.id, a.attended_at, a.resolved_at FROM core.alert a WHERE {' AND '.join(conditions)}"), params,
    )
    row = check_result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerta no encontrada")

    if row["resolved_at"] is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La alerta ya ha sido resuelta",
        )

    await db.execute(
        text("""
            UPDATE core.alert
            SET attended_by_id = :attended_by,
                attended_at    = NOW(),
                action_taken   = :action_taken
            WHERE id = :id AND deleted_at IS NULL
        """),
        {
            "id": str(alerta_id),
            "attended_by": str(user["id"]),
            "action_taken": body.action_taken,
        },
    )
    await record_event(db, "ALERT_ATTENDED", "core.alert", alerta_id, user["id"])
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        error_msg = str(e.orig) if e.orig else str(e)
        if "Transición de estado inválida" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=409, detail="Conflicto de integridad")
    return {"message": "Alerta atendida"}
