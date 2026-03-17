"""
Service Catalog + Requests + SLAs router (Wave B — CI-020..022, POT-019..021).

Public catalog for all users, request management for DGI, SLA definitions
and dashboard metrics.
"""

import math
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import DGI_ROLES
from app.core.audit import record_event

from app.schemas.dgi import (
    ServiceCreate,
    ServiceUpdate,
    ServiceItem,
    ServiceRequestCreate,
    ServiceRequestUpdate,
    ServiceRequestItem,
    SLACreate,
    SLAUpdate,
    SLAItem,
    SLADashboardItem,
    SLADashboardSummary,
)

router = APIRouter(prefix="/api/dgi/services", tags=["dgi"])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_JEFE_DGI_ONLY = {"JEFE_DGI"}
_DGI_MANAGE_ROLES = {"JEFE_DGI", "ESP_CONTROL_GESTION"}


def _require_authenticated(user: dict) -> None:
    """Any authenticated user can access services."""
    if not user.get("id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")


def _require_jefe_dgi(user: dict) -> None:
    if user.get("role_code") not in _JEFE_DGI_ONLY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo JEFE_DGI puede gestionar el catálogo de servicios",
        )


def _require_dgi_manage(user: dict) -> None:
    if user.get("role_code") not in _DGI_MANAGE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo DGI puede gestionar solicitudes",
        )


async def _get_cat_id(db: AsyncSession, scheme: str, code: str) -> str:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = :scheme AND code = :code"),
        {"scheme": scheme, "code": code},
    )).mappings().first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Código inválido para {scheme}: {code}",
        )
    return str(row["id"])


async def _next_service_code(db: AsyncSession, area: str) -> str:
    """Generate SVC-{area}-{seq:03d} with advisory lock."""
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('service_code'))"))
    result = await db.execute(
        text("""
            SELECT MAX(CAST(SUBSTRING(code FROM 8) AS INTEGER)) AS max_seq
            FROM core.dgi_service
            WHERE code ~ :pattern
        """),
        {"pattern": f"^SVC-{area}-[0-9]+$"},
    )
    max_seq = result.scalar() or 0
    return f"SVC-{area}-{max_seq + 1:03d}"


async def _next_request_code(db: AsyncSession) -> str:
    """Generate REQ-{year}-{seq:04d} with advisory lock."""
    year = date.today().year
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('request_code'))"))
    result = await db.execute(
        text("""
            SELECT MAX(CAST(SUBSTRING(code FROM 10) AS INTEGER)) AS max_seq
            FROM core.dgi_service_request
            WHERE code ~ :pattern
        """),
        {"pattern": f"^REQ-{year}-[0-9]+$"},
    )
    max_seq = result.scalar() or 0
    return f"REQ-{year}-{max_seq + 1:04d}"


# ---------------------------------------------------------------------------
# Service SQL fragments
# ---------------------------------------------------------------------------

_SVC_COLS = """
    s.id,
    s.code,
    s.name,
    s.description,
    s.area,
    st.code     AS status,
    st.label    AS status_label,
    s.sla_days,
    s.how_to_request,
    s.deliverables
"""

_SVC_FROM = """
    FROM core.dgi_service s
    JOIN ref.category st ON st.id = s.status_id
"""


def _row_to_service(r: dict) -> ServiceItem:
    return ServiceItem(
        id=r["id"],
        code=r["code"],
        name=r["name"],
        description=r["description"],
        area=r["area"],
        status=r["status"],
        status_label=r["status_label"],
        sla_days=r["sla_days"],
        how_to_request=r["how_to_request"],
        deliverables=r["deliverables"],
    )


# ---------------------------------------------------------------------------
# Request SQL fragments
# ---------------------------------------------------------------------------

_REQ_COLS = """
    req.id,
    req.code,
    req.service_id,
    svc.name        AS service_name,
    st.code         AS status,
    st.label        AS status_label,
    rp.names || ' ' || rp.paternal_surname AS requester_name,
    org.name        AS division_name,
    req.description,
    req.urgency,
    ap.names || ' ' || ap.paternal_surname AS assigned_to_name,
    req.started_at,
    req.completed_at,
    req.satisfaction_score,
    EXTRACT(EPOCH FROM (COALESCE(req.completed_at, NOW()) - req.created_at)) / 86400 AS days_elapsed,
    svc.sla_days,
    CASE
        WHEN st.code NOT IN ('COMPLETADA', 'RECHAZADA') AND svc.sla_days IS NOT NULL
        THEN EXTRACT(EPOCH FROM (NOW() - req.created_at)) / 86400 > svc.sla_days
        ELSE FALSE
    END AS is_overdue,
    req.created_at
"""

_REQ_FROM = """
    FROM core.dgi_service_request req
    JOIN core.dgi_service svc ON svc.id = req.service_id
    JOIN ref.category st ON st.id = req.status_id
    JOIN core."user" ru ON ru.id = req.requester_id
    JOIN core.person rp ON rp.id = ru.person_id
    LEFT JOIN core.organization org ON org.id = req.division_id
    LEFT JOIN core."user" au ON au.id = req.assigned_to_id
    LEFT JOIN core.person ap ON ap.id = au.person_id
"""


def _row_to_request(r: dict) -> ServiceRequestItem:
    return ServiceRequestItem(
        id=r["id"],
        code=r["code"],
        service_id=r["service_id"],
        service_name=r["service_name"],
        status=r["status"],
        status_label=r["status_label"],
        requester_name=r["requester_name"],
        division_name=r["division_name"],
        description=r["description"],
        urgency=r["urgency"],
        assigned_to_name=r["assigned_to_name"],
        started_at=r["started_at"],
        completed_at=r["completed_at"],
        satisfaction_score=r["satisfaction_score"],
        days_elapsed=round(float(r["days_elapsed"]), 1) if r["days_elapsed"] else None,
        sla_days=r["sla_days"],
        is_overdue=bool(r["is_overdue"]),
        created_at=r["created_at"],
    )


# ═══════════════════════════════════════════════════════════════════════════
# SERVICE CATALOG
# ═══════════════════════════════════════════════════════════════════════════

# ---------------------------------------------------------------------------
# 1. GET / — List services (all authenticated users)
# ---------------------------------------------------------------------------
@router.get("")
async def list_services(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    area: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
):
    _require_authenticated(user)

    conditions = ["s.deleted_at IS NULL"]
    params: dict = {}

    if area:
        conditions.append("s.area = :area")
        params["area"] = area.upper()

    if status_filter:
        conditions.append("st.code = :status_filter")
        params["status_filter"] = status_filter.upper()

    where = " AND ".join(conditions)

    rows = (await db.execute(text(f"""
        SELECT {_SVC_COLS} {_SVC_FROM}
        WHERE {where}
        ORDER BY s.area, s.name
    """), params)).mappings().all()

    return [_row_to_service(dict(r)).model_dump() for r in rows]


# ---------------------------------------------------------------------------
# 2. POST / — Create service (JEFE_DGI only)
# ---------------------------------------------------------------------------
@router.post("", status_code=status.HTTP_201_CREATED, response_model=ServiceItem)
async def create_service(
    body: ServiceCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_jefe_dgi(user)

    area = body.area.upper()
    if area not in ("CG", "MP", "TD", "KC"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Área debe ser CG, MP, TD o KC",
        )

    status_id = await _get_cat_id(db, "dgi_service_status", "ACTIVO")
    code = await _next_service_code(db, area)

    result = await db.execute(
        text("""
            INSERT INTO core.dgi_service
                (code, name, description, area, status_id, sla_days,
                 how_to_request, deliverables, created_by_id)
            VALUES
                (:code, :name, :description, :area, :status_id, :sla_days,
                 :how_to_request, :deliverables, :created_by_id)
            RETURNING id
        """),
        {
            "code": code,
            "name": body.name,
            "description": body.description,
            "area": area,
            "status_id": status_id,
            "sla_days": body.sla_days,
            "how_to_request": body.how_to_request,
            "deliverables": body.deliverables,
            "created_by_id": str(user["id"]),
        },
    )
    new_id = str(result.scalar())
    await record_event(db, "CREACION", "core.dgi_service", new_id, user["id"], {"code": code})
    await db.commit()

    row = (await db.execute(
        text(f"SELECT {_SVC_COLS} {_SVC_FROM} WHERE s.id = :id"),
        {"id": new_id},
    )).mappings().first()
    return _row_to_service(dict(row))


# ═══════════════════════════════════════════════════════════════════════════
# SERVICE REQUESTS
# ═══════════════════════════════════════════════════════════════════════════

# ---------------------------------------------------------------------------
# 8. GET /requests — List requests
# ---------------------------------------------------------------------------
@router.get("/requests")
async def list_requests(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
    service_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    _require_authenticated(user)

    conditions = ["req.deleted_at IS NULL"]
    params: dict = {}

    # Non-DGI users see only their own requests
    if user.get("role_code") not in DGI_ROLES:
        conditions.append("req.requester_id = :requester_id")
        params["requester_id"] = str(user["id"])

    if status_filter:
        conditions.append("st.code = :status_filter")
        params["status_filter"] = status_filter.upper()

    if service_id:
        conditions.append("req.service_id = :service_id")
        params["service_id"] = str(service_id)

    where = " AND ".join(conditions)

    total = (await db.execute(
        text(f"SELECT COUNT(*) {_REQ_FROM} WHERE {where}"), params,
    )).scalar() or 0
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(text(f"""
        SELECT {_REQ_COLS} {_REQ_FROM}
        WHERE {where}
        ORDER BY req.created_at DESC
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    items = [_row_to_request(dict(r)).model_dump() for r in rows]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------------------
# 9. POST /requests — Create request (any authenticated user)
# ---------------------------------------------------------------------------
@router.post("/requests", status_code=status.HTTP_201_CREATED, response_model=ServiceRequestItem)
async def create_request(
    body: ServiceRequestCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_authenticated(user)

    # Validate service exists and is active
    svc = (await db.execute(text(f"""
        SELECT s.id {_SVC_FROM}
        WHERE s.id = :id AND s.deleted_at IS NULL AND st.code = 'ACTIVO'
    """), {"id": str(body.service_id)})).mappings().first()
    if not svc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Servicio no encontrado o no activo",
        )

    urgency = body.urgency.upper() if body.urgency else "NORMAL"
    if urgency not in ("BAJA", "NORMAL", "ALTA", "CRITICA"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Urgencia inválida")

    status_id = await _get_cat_id(db, "dgi_request_status", "RECIBIDA")
    code = await _next_request_code(db)

    result = await db.execute(
        text("""
            INSERT INTO core.dgi_service_request
                (code, service_id, status_id, requester_id, division_id,
                 description, urgency, created_by_id)
            VALUES
                (:code, :service_id, :status_id, :requester_id, :division_id,
                 :description, :urgency, :created_by_id)
            RETURNING id
        """),
        {
            "code": code,
            "service_id": str(body.service_id),
            "status_id": status_id,
            "requester_id": str(user["id"]),
            "division_id": user.get("division_id"),
            "description": body.description,
            "urgency": urgency,
            "created_by_id": str(user["id"]),
        },
    )
    new_id = str(result.scalar())
    await record_event(db, "CREACION", "core.dgi_service_request", new_id, user["id"], {"code": code, "service_id": str(body.service_id)})
    await db.commit()

    row = (await db.execute(
        text(f"SELECT {_REQ_COLS} {_REQ_FROM} WHERE req.id = :id"),
        {"id": new_id},
    )).mappings().first()
    return _row_to_request(dict(row))


# ---------------------------------------------------------------------------
# 10. GET /requests/{id} — Request detail
# ---------------------------------------------------------------------------
@router.get("/requests/{request_id}", response_model=ServiceRequestItem)
async def get_request(
    request_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_authenticated(user)

    row = (await db.execute(
        text(f"SELECT {_REQ_COLS} {_REQ_FROM} WHERE req.id = :id AND req.deleted_at IS NULL"),
        {"id": str(request_id)},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

    # Non-DGI users can only see their own requests
    if user.get("role_code") not in DGI_ROLES and str(row["requester_name"]) != "self":
        # Check by requester_id
        check = (await db.execute(
            text("SELECT requester_id FROM core.dgi_service_request WHERE id = :id"),
            {"id": str(request_id)},
        )).mappings().first()
        if check and str(check["requester_id"]) != str(user["id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puede ver sus propias solicitudes")

    return _row_to_request(dict(row))


# ---------------------------------------------------------------------------
# 11. PATCH /requests/{id} — Update request (assign, transition, feedback)
# ---------------------------------------------------------------------------
@router.patch("/requests/{request_id}", response_model=ServiceRequestItem)
async def update_request(
    request_id: UUID,
    body: ServiceRequestUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    rid = str(request_id)

    existing = (await db.execute(
        text("SELECT req.id, st.code AS current_status, req.requester_id FROM core.dgi_service_request req JOIN ref.category st ON st.id = req.status_id WHERE req.id = :id AND req.deleted_at IS NULL"),
        {"id": rid},
    )).mappings().first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

    updates: list[str] = []
    params: dict = {"id": rid}

    body_data = body.model_dump(exclude_none=True)

    # Feedback fields: only requester can submit when COMPLETADA
    if "satisfaction_score" in body_data or "feedback_text" in body_data:
        if str(existing["requester_id"]) != str(user["id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el solicitante puede dar feedback",
            )
        if existing["current_status"] != "COMPLETADA":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Solo se puede dar feedback a solicitudes completadas",
            )
        if "satisfaction_score" in body_data:
            updates.append("satisfaction_score = :satisfaction_score")
            params["satisfaction_score"] = body_data["satisfaction_score"]
        if "feedback_text" in body_data:
            updates.append("feedback_text = :feedback_text")
            params["feedback_text"] = body_data["feedback_text"]
    else:
        # DGI manages status and assignment
        _require_dgi_manage(user)

        if "assigned_to_id" in body_data:
            updates.append("assigned_to_id = :assigned_to_id")
            params["assigned_to_id"] = str(body_data["assigned_to_id"])

        # Status transition (DB trigger validates)
        if "status" in body_data:
            new_status_id = await _get_cat_id(db, "dgi_request_status", body_data["status"].upper())
            updates.append("status_id = :new_status_id")
            params["new_status_id"] = new_status_id

    if not updates:
        row = (await db.execute(
            text(f"SELECT {_REQ_COLS} {_REQ_FROM} WHERE req.id = :id"),
            {"id": rid},
        )).mappings().first()
        return _row_to_request(dict(row))

    updates.append("updated_at = NOW()")
    set_clause = ", ".join(updates)

    try:
        await db.execute(
            text(f"UPDATE core.dgi_service_request SET {set_clause} WHERE id = :id"), params,
        )
        if "status" in body_data:
            await record_event(db, "STATE_TRANSITION", "core.dgi_service_request", request_id, user["id"], {"from": existing["current_status"], "to": body_data["status"].upper()})
        await db.commit()
    except Exception as e:
        await db.rollback()
        err = str(e)
        if "Transición inválida" in err:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
        raise

    row = (await db.execute(
        text(f"SELECT {_REQ_COLS} {_REQ_FROM} WHERE req.id = :id"),
        {"id": rid},
    )).mappings().first()
    return _row_to_request(dict(row))


# ═══════════════════════════════════════════════════════════════════════════
# SLA DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

# ---------------------------------------------------------------------------
# 12. GET /sla-dashboard — SLA compliance dashboard
# ---------------------------------------------------------------------------
@router.get("/sla-dashboard", response_model=SLADashboardSummary)
async def get_sla_dashboard(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    if user.get("role_code") not in DGI_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo DGI")

    rows = (await db.execute(text("""
        SELECT
            svc.id              AS service_id,
            svc.name            AS service_name,
            svc.area,
            COUNT(req.id)       AS total_requests,
            COUNT(req.id) FILTER (WHERE rst.code = 'COMPLETADA') AS completed,
            AVG(EXTRACT(EPOCH FROM (req.completed_at - req.created_at)) / 86400)
                FILTER (WHERE rst.code = 'COMPLETADA') AS avg_days,
            COUNT(req.id) FILTER (
                WHERE rst.code = 'COMPLETADA'
                  AND svc.sla_days IS NOT NULL
                  AND EXTRACT(EPOCH FROM (req.completed_at - req.created_at)) / 86400 > svc.sla_days
            ) AS breaches
        FROM core.dgi_service svc
        LEFT JOIN core.dgi_service_request req ON req.service_id = svc.id AND req.deleted_at IS NULL
        LEFT JOIN ref.category rst ON rst.id = req.status_id
        WHERE svc.deleted_at IS NULL
        GROUP BY svc.id, svc.name, svc.area
        ORDER BY svc.area, svc.name
    """))).mappings().all()

    by_service = []
    total_completed = 0
    total_requests = 0
    total_days_sum = 0.0
    total_days_count = 0
    total_breaches = 0

    for r in rows:
        tot = int(r["total_requests"])
        comp = int(r["completed"])
        rate = round(comp / tot * 100, 1) if tot > 0 else 0.0
        avg = round(float(r["avg_days"]), 1) if r["avg_days"] else None
        br = int(r["breaches"])

        by_service.append(SLADashboardItem(
            service_id=r["service_id"],
            service_name=r["service_name"],
            area=r["area"],
            total_requests=tot,
            completed=comp,
            completion_rate=rate,
            avg_days=avg,
            breaches=br,
        ))

        total_requests += tot
        total_completed += comp
        total_breaches += br
        if avg is not None:
            total_days_sum += avg
            total_days_count += 1

    global_rate = round(total_completed / total_requests * 100, 1) if total_requests > 0 else 0.0
    avg_resolution = round(total_days_sum / total_days_count, 1) if total_days_count > 0 else None

    # Active requests count
    active_row = (await db.execute(text("""
        SELECT COUNT(*) AS cnt
        FROM core.dgi_service_request req
        JOIN ref.category st ON st.id = req.status_id
        WHERE st.code NOT IN ('COMPLETADA', 'RECHAZADA') AND req.deleted_at IS NULL
    """))).mappings().first()
    active_requests = int(active_row["cnt"]) if active_row else 0

    # Average satisfaction
    sat_row = (await db.execute(text("""
        SELECT AVG(satisfaction_score) AS avg_sat
        FROM core.dgi_service_request
        WHERE satisfaction_score IS NOT NULL AND deleted_at IS NULL
    """))).mappings().first()
    avg_satisfaction = round(float(sat_row["avg_sat"]), 1) if sat_row and sat_row["avg_sat"] else None

    return SLADashboardSummary(
        global_completion_rate=global_rate,
        active_requests=active_requests,
        avg_resolution_days=avg_resolution,
        avg_satisfaction=avg_satisfaction,
        by_service=by_service,
    )


# ---------------------------------------------------------------------------
# 3. GET /{id} — Service detail + SLAs
# ---------------------------------------------------------------------------
@router.get("/{service_id}")
async def get_service(
    service_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_authenticated(user)

    row = (await db.execute(
        text(f"SELECT {_SVC_COLS} {_SVC_FROM} WHERE s.id = :id AND s.deleted_at IS NULL"),
        {"id": str(service_id)},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")

    service = _row_to_service(dict(row)).model_dump()

    # Attach SLAs
    sla_rows = (await db.execute(text("""
        SELECT sl.id, sl.service_id, pt.code AS product_type, pt.label AS product_type_label,
               sl.description, sl.target_days, sl.target_hour::text AS target_hour, sl.priority
        FROM core.dgi_sla sl
        JOIN ref.category pt ON pt.id = sl.product_type_id
        WHERE sl.service_id = :service_id AND sl.deleted_at IS NULL
        ORDER BY sl.priority DESC, pt.sort_order
    """), {"service_id": str(service_id)})).mappings().all()

    service["slas"] = [dict(r) for r in sla_rows]

    return service


# ---------------------------------------------------------------------------
# 4. PATCH /{id} — Update service
# ---------------------------------------------------------------------------
@router.patch("/{service_id}", response_model=ServiceItem)
async def update_service(
    service_id: UUID,
    body: ServiceUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_jefe_dgi(user)

    sid = str(service_id)
    existing = (await db.execute(
        text(f"SELECT s.id {_SVC_FROM} WHERE s.id = :id AND s.deleted_at IS NULL"),
        {"id": sid},
    )).mappings().first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")

    updates: list[str] = []
    params: dict = {"id": sid}

    body_data = body.model_dump(exclude_none=True)

    for field in ("name", "description", "area", "sla_days", "how_to_request", "deliverables"):
        if field in body_data:
            updates.append(f"{field} = :{field}")
            params[field] = body_data[field]

    if "status" in body_data:
        new_status_id = await _get_cat_id(db, "dgi_service_status", body_data["status"].upper())
        updates.append("status_id = :new_status_id")
        params["new_status_id"] = new_status_id

    if not updates:
        row = (await db.execute(
            text(f"SELECT {_SVC_COLS} {_SVC_FROM} WHERE s.id = :id"),
            {"id": sid},
        )).mappings().first()
        return _row_to_service(dict(row))

    updates.append("updated_at = NOW()")
    set_clause = ", ".join(updates)

    await db.execute(
        text(f"UPDATE core.dgi_service SET {set_clause} WHERE id = :id"), params,
    )
    await record_event(db, "MODIFICACION", "core.dgi_service", service_id, user["id"])
    await db.commit()

    row = (await db.execute(
        text(f"SELECT {_SVC_COLS} {_SVC_FROM} WHERE s.id = :id"),
        {"id": sid},
    )).mappings().first()
    return _row_to_service(dict(row))


# ═══════════════════════════════════════════════════════════════════════════
# SLAs
# ═══════════════════════════════════════════════════════════════════════════

# ---------------------------------------------------------------------------
# 5. GET /{id}/slas — List SLAs for service
# ---------------------------------------------------------------------------
@router.get("/{service_id}/slas", response_model=list[SLAItem])
async def list_slas(
    service_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_authenticated(user)

    rows = (await db.execute(text("""
        SELECT sl.id, sl.service_id, pt.code AS product_type, pt.label AS product_type_label,
               sl.description, sl.target_days, sl.target_hour::text AS target_hour, sl.priority
        FROM core.dgi_sla sl
        JOIN ref.category pt ON pt.id = sl.product_type_id
        WHERE sl.service_id = :service_id AND sl.deleted_at IS NULL
        ORDER BY sl.priority DESC, pt.sort_order
    """), {"service_id": str(service_id)})).mappings().all()

    return [
        SLAItem(
            id=r["id"], service_id=r["service_id"], product_type=r["product_type"],
            product_type_label=r["product_type_label"], description=r["description"],
            target_days=r["target_days"], target_hour=r["target_hour"], priority=r["priority"],
        )
        for r in rows
    ]


# ---------------------------------------------------------------------------
# 6. POST /{id}/slas — Create SLA
# ---------------------------------------------------------------------------
@router.post("/{service_id}/slas", status_code=status.HTTP_201_CREATED, response_model=SLAItem)
async def create_sla(
    service_id: UUID,
    body: SLACreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_jefe_dgi(user)

    sid = str(service_id)
    product_type_id = await _get_cat_id(db, "dgi_sla_product_type", body.product_type.upper())

    try:
        result = await db.execute(
            text("""
                INSERT INTO core.dgi_sla
                    (service_id, product_type_id, description, target_days,
                     target_hour, priority)
                VALUES
                    (:service_id, :product_type_id, :description, :target_days,
                     :target_hour, :priority)
                RETURNING id
            """),
            {
                "service_id": sid,
                "product_type_id": product_type_id,
                "description": body.description,
                "target_days": body.target_days,
                "target_hour": body.target_hour,
                "priority": body.priority,
            },
        )
        new_id = str(result.scalar())
        await record_event(db, "CREACION", "core.dgi_sla", new_id, user["id"], {"service_id": str(service_id)})
        await db.commit()
    except Exception as e:
        await db.rollback()
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un SLA para este servicio y tipo de producto",
            )
        raise

    row = (await db.execute(text("""
        SELECT sl.id, sl.service_id, pt.code AS product_type, pt.label AS product_type_label,
               sl.description, sl.target_days, sl.target_hour::text AS target_hour, sl.priority
        FROM core.dgi_sla sl
        JOIN ref.category pt ON pt.id = sl.product_type_id
        WHERE sl.id = :id
    """), {"id": new_id})).mappings().first()

    return SLAItem(
        id=row["id"], service_id=row["service_id"], product_type=row["product_type"],
        product_type_label=row["product_type_label"], description=row["description"],
        target_days=row["target_days"], target_hour=row["target_hour"], priority=row["priority"],
    )


# ---------------------------------------------------------------------------
# 7. PATCH /{id}/slas/{sla_id} — Update SLA
# ---------------------------------------------------------------------------
@router.patch("/{service_id}/slas/{sla_id}", response_model=SLAItem)
async def update_sla(
    service_id: UUID,
    sla_id: UUID,
    body: SLAUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_jefe_dgi(user)

    sid = str(sla_id)
    existing = (await db.execute(
        text("SELECT id FROM core.dgi_sla WHERE id = :id AND service_id = :service_id AND deleted_at IS NULL"),
        {"id": sid, "service_id": str(service_id)},
    )).mappings().first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SLA no encontrado")

    updates: list[str] = []
    params: dict = {"id": sid}

    body_data = body.model_dump(exclude_none=True)
    for field in ("description", "target_days", "target_hour", "priority"):
        if field in body_data:
            updates.append(f"{field} = :{field}")
            params[field] = body_data[field]

    if not updates:
        row = (await db.execute(text("""
            SELECT sl.id, sl.service_id, pt.code AS product_type, pt.label AS product_type_label,
                   sl.description, sl.target_days, sl.target_hour::text AS target_hour, sl.priority
            FROM core.dgi_sla sl
            JOIN ref.category pt ON pt.id = sl.product_type_id
            WHERE sl.id = :id
        """), {"id": sid})).mappings().first()
        return SLAItem(
            id=row["id"], service_id=row["service_id"], product_type=row["product_type"],
            product_type_label=row["product_type_label"], description=row["description"],
            target_days=row["target_days"], target_hour=row["target_hour"], priority=row["priority"],
        )

    updates.append("updated_at = NOW()")
    set_clause = ", ".join(updates)

    await db.execute(
        text(f"UPDATE core.dgi_sla SET {set_clause} WHERE id = :id"), params,
    )
    await db.commit()

    row = (await db.execute(text("""
        SELECT sl.id, sl.service_id, pt.code AS product_type, pt.label AS product_type_label,
               sl.description, sl.target_days, sl.target_hour::text AS target_hour, sl.priority
        FROM core.dgi_sla sl
        JOIN ref.category pt ON pt.id = sl.product_type_id
        WHERE sl.id = :id
    """), {"id": sid})).mappings().first()
    return SLAItem(
        id=row["id"], service_id=row["service_id"], product_type=row["product_type"],
        product_type_label=row["product_type_label"], description=row["description"],
        target_days=row["target_days"], target_hour=row["target_hour"], priority=row["priority"],
    )
