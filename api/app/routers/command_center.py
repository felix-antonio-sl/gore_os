"""
E-2: Centro de Mando (Command Center)

Consolidated crisis signals for ADMIN_REGIONAL/GOBERNADOR/ADMIN_SISTEMA/JEFE_DGI.
Queries source tables directly (no dependency on txn.event).
"""
import math
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import CurrentUser

router = APIRouter(prefix="/api/command-center", tags=["command-center"])

_ALLOWED_ROLES = {"ADMIN_REGIONAL", "GOBERNADOR", "ADMIN_SISTEMA", "JEFE_DGI"}


def _require_command_center(user: dict) -> None:
    if user.get("role_code") not in _ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Admin Regional, Gobernador, Admin Sistema o Jefe DGI",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 1. GET /api/command-center/summary — aggregated crisis KPIs
# ═══════════════════════════════════════════════════════════════════════════════
@router.get("/summary")
async def command_center_summary(user: CurrentUser, db=Depends(get_db)):
    _require_command_center(user)

    # 1. Escalamientos activos
    esc_active = (await db.execute(text("""
        SELECT COUNT(*) FROM core.dgi_escalation e
        JOIN ref.category es ON es.id = e.status_id
        WHERE e.deleted_at IS NULL AND es.code IN ('ABIERTO', 'EN_GESTION')
    """))).scalar() or 0

    esc_by_level = (await db.execute(text("""
        SELECT lv.code AS level, lv.label, COUNT(*) AS count
        FROM core.dgi_escalation e
        JOIN ref.category lv ON lv.id = e.level_id
        JOIN ref.category es ON es.id = e.status_id
        WHERE e.deleted_at IS NULL AND es.code IN ('ABIERTO', 'EN_GESTION')
        GROUP BY lv.code, lv.label, lv.sort_order
        ORDER BY lv.sort_order
    """))).mappings().all()

    esc_top = (await db.execute(text("""
        SELECT e.id, e.code, e.situation, e.deadline,
               lv.code AS level, lv.label AS level_label
        FROM core.dgi_escalation e
        JOIN ref.category lv ON lv.id = e.level_id
        JOIN ref.category es ON es.id = e.status_id
        WHERE e.deleted_at IS NULL AND es.code IN ('ABIERTO', 'EN_GESTION')
        ORDER BY COALESCE(e.deadline, '2099-12-31'::timestamp) ASC
        LIMIT 5
    """))).mappings().all()

    # 2. Alertas críticas
    alert_critical = (await db.execute(text("""
        SELECT COUNT(*) FROM core.alert a
        JOIN ref.category sv ON sv.id = a.severity_id
        WHERE a.deleted_at IS NULL AND a.resolved_at IS NULL
          AND sv.code = 'CRITICO'
    """))).scalar() or 0

    alert_high = (await db.execute(text("""
        SELECT COUNT(*) FROM core.alert a
        JOIN ref.category sv ON sv.id = a.severity_id
        WHERE a.deleted_at IS NULL AND a.resolved_at IS NULL
          AND sv.code = 'ALTO'
    """))).scalar() or 0

    alert_top = (await db.execute(text("""
        SELECT a.id, LEFT(a.message, 100) AS message,
               sv.code AS severity, sv.label AS severity_label,
               a.triggered_at
        FROM core.alert a
        JOIN ref.category sv ON sv.id = a.severity_id
        WHERE a.deleted_at IS NULL AND a.resolved_at IS NULL
          AND sv.code IN ('CRITICO', 'ALTO')
        ORDER BY a.triggered_at DESC
        LIMIT 5
    """))).mappings().all()

    # 3. Riesgos altos
    risk_high = (await db.execute(text("""
        SELECT COUNT(*) FROM core.risk r
        JOIN ref.category rp ON rp.id = r.probability_id
        JOIN ref.category rs ON rs.id = r.status_id
        WHERE r.deleted_at IS NULL
          AND rp.code IN ('ALTA', 'MUY_ALTA')
          AND rs.code NOT IN ('CERRADO', 'MITIGADO', 'ACEPTADO')
    """))).scalar() or 0

    risk_total_active = (await db.execute(text("""
        SELECT COUNT(*) FROM core.risk r
        JOIN ref.category rs ON rs.id = r.status_id
        WHERE r.deleted_at IS NULL AND rs.code NOT IN ('CERRADO')
    """))).scalar() or 0

    risk_top = (await db.execute(text("""
        SELECT r.id, r.code, r.name,
               rp.code AS probability, rp.label AS probability_label,
               rs.code AS status, rs.label AS status_label
        FROM core.risk r
        JOIN ref.category rp ON rp.id = r.probability_id
        JOIN ref.category rs ON rs.id = r.status_id
        WHERE r.deleted_at IS NULL
          AND rp.code IN ('ALTA', 'MUY_ALTA')
          AND rs.code NOT IN ('CERRADO', 'MITIGADO', 'ACEPTADO')
        ORDER BY rp.sort_order DESC, r.created_at DESC
        LIMIT 5
    """))).mappings().all()

    # 4. Decisiones AR pendientes
    dec_pending = (await db.execute(text("""
        SELECT COUNT(*) FROM core.dgi_ar_decision d
        JOIN ref.category ds ON ds.id = d.status_id
        WHERE d.deleted_at IS NULL AND ds.code IN ('PENDIENTE', 'EN_EJECUCION')
    """))).scalar() or 0

    dec_top = (await db.execute(text("""
        SELECT d.id, d.description, d.due_date,
               dt.code AS decision_type, dt.label AS decision_type_label,
               ds.code AS status, ds.label AS status_label
        FROM core.dgi_ar_decision d
        JOIN ref.category dt ON dt.id = d.decision_type_id
        JOIN ref.category ds ON ds.id = d.status_id
        WHERE d.deleted_at IS NULL AND ds.code IN ('PENDIENTE', 'EN_EJECUCION')
        ORDER BY COALESCE(d.due_date, '2099-12-31'::date) ASC
        LIMIT 5
    """))).mappings().all()

    # 5. Reuniones próximas (7 días)
    now = datetime.now(timezone.utc)
    week_ahead = now + timedelta(days=7)
    meetings_upcoming = (await db.execute(text("""
        SELECT COUNT(*) FROM core.crisis_meeting cm
        JOIN core.session s ON s.id = cm.session_id
        WHERE cm.deleted_at IS NULL
          AND s.scheduled_at BETWEEN :now AND :week_ahead
    """), {"now": now, "week_ahead": week_ahead})).scalar() or 0

    meetings_next = (await db.execute(text("""
        SELECT cm.id, s.scheduled_at, cm.summary,
               p.names || ' ' || p.paternal_surname AS organizer_name
        FROM core.crisis_meeting cm
        JOIN core.session s ON s.id = cm.session_id
        LEFT JOIN core."user" u ON u.id = cm.organizer_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE cm.deleted_at IS NULL
          AND s.scheduled_at BETWEEN :now AND :week_ahead
        ORDER BY s.scheduled_at ASC
        LIMIT 5
    """), {"now": now, "week_ahead": week_ahead})).mappings().all()

    # 6. SLA breaches
    sla_breaches = (await db.execute(text("""
        SELECT COUNT(*) FROM core.dgi_service_request sr
        JOIN ref.category st ON st.id = sr.status_id
        JOIN core.dgi_service sv ON sv.id = sr.service_id
        WHERE sr.deleted_at IS NULL
          AND st.code NOT IN ('COMPLETADA', 'RECHAZADA')
          AND sv.sla_days IS NOT NULL
          AND sr.created_at + (sv.sla_days || ' days')::interval < NOW()
    """))).scalar() or 0

    return {
        "escalations": {
            "active": esc_active,
            "by_level": [dict(r) for r in esc_by_level],
            "top": [dict(r) for r in esc_top],
        },
        "alerts": {
            "critical": alert_critical,
            "high": alert_high,
            "top": [dict(r) for r in alert_top],
        },
        "risks": {
            "high_count": risk_high,
            "total_active": risk_total_active,
            "top": [dict(r) for r in risk_top],
        },
        "decisions": {
            "pending": dec_pending,
            "top": [dict(r) for r in dec_top],
        },
        "meetings": {
            "upcoming": meetings_upcoming,
            "next": [dict(r) for r in meetings_next],
        },
        "sla_breaches": {
            "count": sla_breaches,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. GET /api/command-center/timeline — recent events across domains
# ═══════════════════════════════════════════════════════════════════════════════
@router.get("/timeline")
async def command_center_timeline(
    user: CurrentUser,
    db=Depends(get_db),
    days: int = Query(7, ge=1, le=90),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
):
    _require_command_center(user)

    since = datetime.now(timezone.utc) - timedelta(days=days)
    params: dict = {"since": since, "limit": page_size, "offset": (page - 1) * page_size}

    sources = []

    # Escalations
    sources.append("""
        SELECT 'ESCALATION' AS category, e.code AS ref_code,
               LEFT(e.situation, 100) AS description,
               e.created_at AS event_time,
               lv.label AS detail, e.id AS entity_id
        FROM core.dgi_escalation e
        JOIN ref.category lv ON lv.id = e.level_id
        WHERE e.deleted_at IS NULL AND e.created_at >= :since
    """)

    # Alerts
    sources.append("""
        SELECT 'ALERT' AS category, LEFT(a.id::text, 8) AS ref_code,
               LEFT(a.message, 100) AS description,
               a.triggered_at AS event_time,
               sv.label AS detail, a.id AS entity_id
        FROM core.alert a
        JOIN ref.category sv ON sv.id = a.severity_id
        WHERE a.deleted_at IS NULL AND a.triggered_at >= :since
    """)

    # Risks
    sources.append("""
        SELECT 'RISK' AS category, r.code AS ref_code,
               r.name AS description,
               r.created_at AS event_time,
               rs.label AS detail, r.id AS entity_id
        FROM core.risk r
        JOIN ref.category rs ON rs.id = r.status_id
        WHERE r.deleted_at IS NULL AND r.created_at >= :since
    """)

    # AR Decisions
    sources.append("""
        SELECT 'DECISION' AS category, LEFT(d.id::text, 8) AS ref_code,
               LEFT(d.description, 100) AS description,
               d.created_at AS event_time,
               ds.label AS detail, d.id AS entity_id
        FROM core.dgi_ar_decision d
        JOIN ref.category ds ON ds.id = d.status_id
        WHERE d.deleted_at IS NULL AND d.created_at >= :since
    """)

    # Meetings
    sources.append("""
        SELECT 'MEETING' AS category,
               'REUNION-' || s.session_number AS ref_code,
               COALESCE(cm.summary, 'Reunión de crisis') AS description,
               s.scheduled_at AS event_time,
               NULL AS detail, cm.id AS entity_id
        FROM core.crisis_meeting cm
        JOIN core.session s ON s.id = cm.session_id
        WHERE cm.deleted_at IS NULL AND s.scheduled_at >= :since
    """)

    # Filter by category
    if category:
        cat_upper = category.upper()
        category_map = {
            "ESCALATION": 0, "ALERT": 1, "RISK": 2, "DECISION": 3, "MEETING": 4,
        }
        if cat_upper in category_map:
            sources = [sources[category_map[cat_upper]]]

    if not sources:
        return {"items": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}

    union_query = " UNION ALL ".join(sources)

    # Count
    count_q = f"SELECT COUNT(*) FROM ({union_query}) AS events"
    total = (await db.execute(text(count_q), params)).scalar() or 0
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    # Fetch
    full_query = f"""
        SELECT category, ref_code, description, event_time, detail, entity_id
        FROM ({union_query}) AS events
        ORDER BY event_time DESC
        LIMIT :limit OFFSET :offset
    """
    rows = (await db.execute(text(full_query), params)).mappings().all()

    return {
        "items": [dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
