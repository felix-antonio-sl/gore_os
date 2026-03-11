"""
Escalation Protocol router (Wave B — CI-011..015).

4-level escalation with advisory-locked code gen, auto-alert creation,
FSM transitions (DB trigger), and deadline tracking.
"""

import math
from datetime import date, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import DGI_ROLES
from app.core.audit import record_event

from app.schemas.dgi import (
    EscalationCreate,
    EscalationUpdate,
    EscalationItemWaveB,
    EscalationStats,
)

router = APIRouter(prefix="/api/dgi/escalations", tags=["dgi"])

# ---------------------------------------------------------------------------
# FSM & config
# ---------------------------------------------------------------------------
_FSM: dict[str, set[str]] = {
    "ABIERTO":    {"EN_GESTION", "CERRADO"},
    "EN_GESTION": {"RESUELTO", "CERRADO"},
    "RESUELTO":   {"CERRADO"},
    "CERRADO":    set(),
}

_LEVEL_ESCALATED_TO: dict[str, str] = {
    "NIVEL_1": "JEFE_DGI",
    "NIVEL_2": "AR",
    "NIVEL_3": "AR",
    "NIVEL_4": "GOBERNADOR",
}

_LEVEL_DEFAULT_HOURS: dict[str, int] = {
    "NIVEL_1": 4,
    "NIVEL_2": 24,
    "NIVEL_3": 48,
    "NIVEL_4": 72,
}

_FIELD_ALLOWLIST = {"situation", "impact", "recommendation", "resolved_description"}

_WRITE_ROLES = {"JEFE_DGI", "ESP_CONTROL_GESTION"}
_READ_ROLES = {*DGI_ROLES, "ADMIN_REGIONAL", "GOBERNADOR", "ADMIN_SISTEMA"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_read(user: dict) -> None:
    if user.get("role_code") not in _READ_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sin permisos para ver escalamientos",
        )


def _require_dgi(user: dict) -> None:
    if user.get("role_code") not in DGI_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo roles DGI pueden acceder a escalamientos",
        )


def _require_write(user: dict) -> None:
    if user.get("role_code") not in _WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo JEFE_DGI o ESP_CONTROL_GESTION pueden gestionar escalamientos",
        )


async def _get_status_id(db: AsyncSession, code: str) -> str:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'dgi_escalation_status' AND code = :code"),
        {"code": code},
    )).mappings().first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado de escalamiento inválido: {code}",
        )
    return str(row["id"])


async def _get_level_id(db: AsyncSession, code: str) -> str:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'dgi_escalation_level' AND code = :code"),
        {"code": code},
    )).mappings().first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nivel de escalamiento inválido: {code}",
        )
    return str(row["id"])


async def _next_esc_code(db: AsyncSession) -> str:
    """Generate ESC-{year}-{seq:04d} with advisory lock."""
    year = date.today().year
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('escalation_code'))"))
    result = await db.execute(
        text("""
            SELECT MAX(CAST(SUBSTRING(code FROM 10) AS INTEGER)) AS max_seq
            FROM core.dgi_escalation
            WHERE code ~ :pattern
        """),
        {"pattern": f"^ESC-{year}-[0-9]+$"},
    )
    max_seq = result.scalar() or 0
    return f"ESC-{year}-{max_seq + 1:04d}"


async def _create_alert(db: AsyncSession, escalation_id: str, level_code: str,
                        situation: str, user_id: str) -> str | None:
    """Create an auto-alert for the escalation. Returns alert ID."""
    severity_code = "CRITICO" if level_code in ("NIVEL_3", "NIVEL_4") else "ALTO"

    sev_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_severity' AND code = :code"),
        {"code": severity_code},
    )).mappings().first()
    if not sev_row:
        return None

    type_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_type' LIMIT 1"),
    )).mappings().first()
    if not type_row:
        return None

    result = await db.execute(
        text("""
            INSERT INTO core.alert
                (alert_type_id, severity_id, subject_type, subject_id,
                 message, triggered_by_id)
            VALUES
                (:type_id, :sev_id, 'core.dgi_escalation', :subject_id,
                 :message, :triggered_by_id)
            RETURNING id
        """),
        {
            "type_id": str(type_row["id"]),
            "sev_id": str(sev_row["id"]),
            "subject_id": escalation_id,
            "message": f"Escalamiento {level_code}: {situation[:200]}",
            "triggered_by_id": user_id,
        },
    )
    return str(result.scalar())


# ---------------------------------------------------------------------------
# SQL fragments
# ---------------------------------------------------------------------------

_LIST_COLS = """
    e.id,
    e.code,
    lv.code         AS level,
    lv.label        AS level_label,
    st.code         AS status,
    st.label        AS status_label,
    e.situation,
    e.impact,
    e.options,
    e.recommendation,
    e.deadline,
    e.subject_type,
    e.subject_id,
    e.escalated_to,
    e.resolved_description,
    e.resolved_at,
    e.alert_id,
    e.created_at,
    p.names || ' ' || p.paternal_surname AS created_by_name
"""

_LIST_FROM = """
    FROM core.dgi_escalation e
    JOIN ref.category lv ON lv.id = e.level_id
    JOIN ref.category st ON st.id = e.status_id
    LEFT JOIN core."user" u ON u.id = e.created_by_id
    LEFT JOIN core.person p ON p.id = u.person_id
"""


def _row_to_item(r: dict) -> EscalationItemWaveB:
    return EscalationItemWaveB(
        id=r["id"],
        code=r["code"],
        level=r["level"],
        level_label=r["level_label"],
        status=r["status"],
        status_label=r["status_label"],
        situation=r["situation"],
        impact=r["impact"],
        options=r["options"] or [],
        recommendation=r["recommendation"],
        deadline=r["deadline"],
        subject_type=r["subject_type"],
        subject_id=r["subject_id"],
        escalated_to=r["escalated_to"],
        resolved_description=r["resolved_description"],
        resolved_at=r["resolved_at"],
        alert_id=r["alert_id"],
        created_at=r["created_at"],
        created_by_name=r.get("created_by_name"),
    )


# ---------------------------------------------------------------------------
# 1. GET /active — Active escalations with deadline semaphore
#    (registered BEFORE /{escalation_id} to avoid path conflict)
# ---------------------------------------------------------------------------
@router.get("/active")
async def get_active_escalations(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_read(user)

    rows = (await db.execute(text(f"""
        SELECT {_LIST_COLS} {_LIST_FROM}
        WHERE st.code IN ('ABIERTO', 'EN_GESTION') AND e.deleted_at IS NULL
        ORDER BY e.deadline ASC NULLS LAST
    """))).mappings().all()

    now = datetime.utcnow()
    items = []
    for r in rows:
        item = _row_to_item(dict(r)).model_dump()
        # Compute deadline semaphore
        if r["deadline"]:
            dl = r["deadline"]
            if dl.tzinfo:
                from datetime import timezone
                now_aware = datetime.now(timezone.utc)
                hours_left = (dl - now_aware).total_seconds() / 3600
            else:
                hours_left = (dl - now).total_seconds() / 3600
            if hours_left < 0:
                item["deadline_signal"] = "VENCIDO"
            elif hours_left < 4:
                item["deadline_signal"] = "ROJO"
            elif hours_left < 24:
                item["deadline_signal"] = "AMARILLO"
            else:
                item["deadline_signal"] = "VERDE"
            item["hours_remaining"] = round(hours_left, 1)
        else:
            item["deadline_signal"] = None
            item["hours_remaining"] = None
        items.append(item)

    return items


# ---------------------------------------------------------------------------
# 2. GET /stats — Escalation statistics
#    (registered BEFORE /{escalation_id} to avoid path conflict)
# ---------------------------------------------------------------------------
@router.get("/stats", response_model=EscalationStats)
async def get_escalation_stats(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_read(user)

    # Active count
    active_row = (await db.execute(text("""
        SELECT COUNT(*) AS cnt
        FROM core.dgi_escalation e
        JOIN ref.category st ON st.id = e.status_id
        WHERE st.code IN ('ABIERTO', 'EN_GESTION') AND e.deleted_at IS NULL
    """))).mappings().first()
    total_active = int(active_row["cnt"]) if active_row else 0

    # By level
    level_rows = (await db.execute(text("""
        SELECT lv.code AS level, lv.label, COUNT(*) AS cnt
        FROM core.dgi_escalation e
        JOIN ref.category lv ON lv.id = e.level_id
        JOIN ref.category st ON st.id = e.status_id
        WHERE st.code IN ('ABIERTO', 'EN_GESTION') AND e.deleted_at IS NULL
        GROUP BY lv.code, lv.label
        ORDER BY lv.code
    """))).mappings().all()
    by_level = [{"level": r["level"], "label": r["label"], "count": r["cnt"]} for r in level_rows]

    # Avg resolution time (hours) for resolved escalations
    avg_row = (await db.execute(text("""
        SELECT AVG(EXTRACT(EPOCH FROM (e.resolved_at - e.created_at)) / 3600) AS avg_hours,
               COUNT(*) AS resolved_count
        FROM core.dgi_escalation e
        JOIN ref.category st ON st.id = e.status_id
        WHERE st.code IN ('RESUELTO', 'CERRADO') AND e.resolved_at IS NOT NULL
          AND e.deleted_at IS NULL
    """))).mappings().first()

    return EscalationStats(
        total_active=total_active,
        by_level=by_level,
        avg_resolution_hours=round(float(avg_row["avg_hours"]), 1) if avg_row and avg_row["avg_hours"] else None,
        resolved_count=int(avg_row["resolved_count"]) if avg_row else 0,
    )


# ---------------------------------------------------------------------------
# 3. GET / — Paginated list
# ---------------------------------------------------------------------------
@router.get("")
async def list_escalations(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    level_filter: str | None = Query(None, alias="level"),
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    _require_read(user)

    conditions = ["e.deleted_at IS NULL"]
    params: dict = {}

    if level_filter:
        conditions.append("lv.code = :level_filter")
        params["level_filter"] = level_filter.upper()

    if status_filter:
        conditions.append("st.code = :status_filter")
        params["status_filter"] = status_filter.upper()

    where = " AND ".join(conditions)

    total = (await db.execute(
        text(f"SELECT COUNT(*) {_LIST_FROM} WHERE {where}"), params,
    )).scalar() or 0
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(text(f"""
        SELECT {_LIST_COLS} {_LIST_FROM}
        WHERE {where}
        ORDER BY e.created_at DESC
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    items = [_row_to_item(dict(r)).model_dump() for r in rows]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------------------
# 4. POST / — Create escalation
# ---------------------------------------------------------------------------
@router.post("", status_code=status.HTTP_201_CREATED, response_model=EscalationItemWaveB)
async def create_escalation(
    body: EscalationCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_write(user)

    level_code = body.level.upper()
    level_id = await _get_level_id(db, level_code)
    status_id = await _get_status_id(db, "ABIERTO")
    code = await _next_esc_code(db)
    escalated_to = _LEVEL_ESCALATED_TO.get(level_code, "JEFE_DGI")

    # Default deadline based on level
    deadline = body.deadline
    if not deadline:
        hours = _LEVEL_DEFAULT_HOURS.get(level_code, 24)
        deadline = datetime.utcnow() + timedelta(hours=hours)

    import json as _json
    options_json = _json.dumps(body.options) if body.options else "[]"

    result = await db.execute(
        text("""
            INSERT INTO core.dgi_escalation
                (code, level_id, status_id, situation, impact,
                 options, recommendation, deadline, subject_type, subject_id,
                 escalated_to, created_by_id)
            VALUES
                (:code, :level_id, :status_id, :situation, :impact,
                 CAST(:options AS jsonb), :recommendation, :deadline,
                 :subject_type, :subject_id, :escalated_to, :created_by_id)
            RETURNING id
        """),
        {
            "code": code,
            "level_id": level_id,
            "status_id": status_id,
            "situation": body.situation,
            "impact": body.impact,
            "options": options_json,
            "recommendation": body.recommendation,
            "deadline": deadline,
            "subject_type": body.subject_type,
            "subject_id": str(body.subject_id) if body.subject_id else None,
            "escalated_to": escalated_to,
            "created_by_id": str(user["id"]),
        },
    )
    new_id = str(result.scalar())

    # Auto-create alert
    alert_id = await _create_alert(db, new_id, level_code, body.situation, str(user["id"]))
    if alert_id:
        await db.execute(
            text("UPDATE core.dgi_escalation SET alert_id = :alert_id WHERE id = :id"),
            {"alert_id": alert_id, "id": new_id},
        )

    await record_event(db, "ESCALATION_CREATED", "core.dgi_escalation", new_id, user["id"],
                       {"code": code, "level": level_code})
    await db.commit()

    row = (await db.execute(
        text(f"SELECT {_LIST_COLS} {_LIST_FROM} WHERE e.id = :id"),
        {"id": new_id},
    )).mappings().first()
    return _row_to_item(dict(row))


# ---------------------------------------------------------------------------
# 5. GET /{escalation_id} — Detail
# ---------------------------------------------------------------------------
@router.get("/{escalation_id}", response_model=EscalationItemWaveB)
async def get_escalation(
    escalation_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_read(user)

    row = (await db.execute(
        text(f"SELECT {_LIST_COLS} {_LIST_FROM} WHERE e.id = :id AND e.deleted_at IS NULL"),
        {"id": str(escalation_id)},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escalamiento no encontrado")
    return _row_to_item(dict(row))


# ---------------------------------------------------------------------------
# 6. PATCH /{escalation_id} — Update + FSM transition
# ---------------------------------------------------------------------------
@router.patch("/{escalation_id}", response_model=EscalationItemWaveB)
async def update_escalation(
    escalation_id: UUID,
    body: EscalationUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_write(user)

    eid = str(escalation_id)

    existing = (await db.execute(
        text(f"SELECT e.id, st.code AS current_status {_LIST_FROM} WHERE e.id = :id AND e.deleted_at IS NULL"),
        {"id": eid},
    )).mappings().first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escalamiento no encontrado")

    current_status = existing["current_status"]

    updates: list[str] = []
    params: dict = {"id": eid}

    body_data = body.model_dump(exclude_none=True)

    # Field updates from allowlist
    for field in _FIELD_ALLOWLIST:
        if field in body_data:
            updates.append(f"{field} = :{field}")
            params[field] = body_data[field]

    # Options as JSONB
    if "options" in body_data:
        import json as _json
        updates.append("options = CAST(:options AS jsonb)")
        params["options"] = _json.dumps(body_data["options"])

    # Status transition
    if body.status is not None:
        target = body.status.upper()
        allowed = _FSM.get(current_status, set())
        if target not in allowed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Transición inválida: {current_status} → {target}. "
                       f"Permitidas: {', '.join(sorted(allowed)) if allowed else 'ninguna'}",
            )
        new_status_id = await _get_status_id(db, target)
        updates.append("status_id = :new_status_id")
        params["new_status_id"] = new_status_id

        if target in ("RESUELTO", "CERRADO"):
            updates.append("resolved_at = NOW()")

    if not updates:
        row = (await db.execute(
            text(f"SELECT {_LIST_COLS} {_LIST_FROM} WHERE e.id = :id"),
            {"id": eid},
        )).mappings().first()
        return _row_to_item(dict(row))

    updates.append("updated_at = NOW()")
    set_clause = ", ".join(updates)

    await db.execute(
        text(f"UPDATE core.dgi_escalation SET {set_clause} WHERE id = :id"),
        params,
    )

    if body.status is not None:
        await record_event(db, "ESCALATION_STATUS_CHANGE", "core.dgi_escalation",
                           escalation_id, user["id"],
                           {"old_status": current_status, "new_status": body.status.upper()})

    await db.commit()

    row = (await db.execute(
        text(f"SELECT {_LIST_COLS} {_LIST_FROM} WHERE e.id = :id"),
        {"id": eid},
    )).mappings().first()
    return _row_to_item(dict(row))


# ---------------------------------------------------------------------------
# 7. DELETE /{escalation_id} — Soft-delete
# ---------------------------------------------------------------------------
@router.delete("/{escalation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_escalation(
    escalation_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_write(user)

    result = await db.execute(
        text("""
            UPDATE core.dgi_escalation
            SET deleted_at = NOW(), updated_at = NOW()
            WHERE id = :id AND deleted_at IS NULL
        """),
        {"id": str(escalation_id)},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escalamiento no encontrado")
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
