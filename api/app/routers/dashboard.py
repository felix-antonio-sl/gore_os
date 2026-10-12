from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.commitments import commitment_actions
from app.core.alerts import apply_alert_scope
from app.core.risks import risk_scope_where
from app.core.security import ALL_ROLES, DGI_ROLES
from app.schemas.dashboard import ActionItem, ActionItemsResponse


router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

_TEMPORAL_MAP = {
    "VENCIDO": 0,
    "HOY": 1,
    "ESTA_SEMANA": 2,
    "FUTURO": 3,
}

_SEVERITY_MAP = {
    "CRITICO": 0,
    "ALTO": 1,
    "MEDIO": 2,
    "BAJO": 3,
}

_PERSONAL_ROLES = ("ANALISTA", "RTF", "ASESOR_JURIDICO")
_DIVISION_ROLES = ("JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD")
_COORDINATION_READ_ROLES = {"JEFE_DGI", "ESP_CONTROL_GESTION", "ESP_PROCESOS", "ESP_TD", "ADMIN_REGIONAL", "GOBERNADOR", "ADMIN_SISTEMA"}


def _compute_temporal(days_remaining: int | None) -> str | None:
    if days_remaining is None:
        return None
    if days_remaining < 0:
        return "VENCIDO"
    if days_remaining == 0:
        return "HOY"
    if days_remaining <= 7:
        return "ESTA_SEMANA"
    return "FUTURO"


def _compute_priority(temporal: str | None, severity: str) -> int:
    sev_val = _SEVERITY_MAP.get(severity, 3)
    temp_val = _TEMPORAL_MAP.get(temporal, 4) if temporal else 4
    return sev_val * 5 + temp_val


def _severity_from_alert(alert_code: str) -> str:
    return {
        "CRITICO": "CRITICO",
        "ALTO": "ALTO",
        "ATENCION": "MEDIO",
        "INFO": "BAJO",
    }.get(alert_code, "BAJO")


def _severity_from_escalation_level(level_code: str) -> str:
    if level_code in ("NIVEL_3", "NIVEL_4"):
        return "CRITICO"
    if level_code == "NIVEL_2":
        return "ALTO"
    return "MEDIO"


def _severity_from_risk_probability(prob_code: str) -> str:
    return {
        "MUY_ALTA": "CRITICO",
        "ALTA": "ALTO",
        "MEDIA": "MEDIO",
        "BAJA": "BAJO",
        "MUY_BAJA": "BAJO",
    }.get(prob_code, "BAJO")

async def _ai_commitments(db: AsyncSession, user: dict) -> list[ActionItem]:
    role = user["role_code"]
    uid = str(user["id"])
    div_id = str(user["division_id"]) if user.get("division_id") else None

    params: dict = {}
    where_scope = ""

    if role in _PERSONAL_ROLES:
        where_scope = "AND oc.responsible_id = :uid"
        params["uid"] = uid
    elif role in _DIVISION_ROLES:
        if not div_id:
            return []
        where_scope = "AND oc.division_id = :div_id"
        params["div_id"] = div_id
    else:
        # Keep institutional attention, plus the user's own future assignments.
        where_scope = "AND (oc.due_date < CURRENT_DATE OR oc.responsible_id = :uid OR sc.code = 'COMPLETADO')"
        params["uid"] = uid

    sql = text(f"""
        SELECT
            oc.id::text AS id,
            oc.ipr_id::text AS ipr_id,
            oc.description,
            ipr.codigo_bip AS ipr_codigo_bip,
            oc.due_date,
            oc.responsible_id,
            oc.division_id,
            sc.code AS state,
            sc.label AS state_label,
            sc.valid_transitions,
            p.names || ' ' || p.paternal_surname AS responsible_name,
            (oc.due_date - CURRENT_DATE) AS days_remaining
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        LEFT JOIN core.ipr ipr ON ipr.id = oc.ipr_id AND ipr.deleted_at IS NULL
        LEFT JOIN core."user" u ON u.id = oc.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE sc.code NOT IN ('VERIFICADO', 'CANCELADO')
          AND oc.deleted_at IS NULL
          {where_scope}
        ORDER BY oc.due_date ASC NULLS LAST
    """)
    rows = (await db.execute(sql, params)).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
        actions = commitment_actions(user, dict(r))
        if r["state"] == "COMPLETADO" and "verificar" not in actions:
            continue  # Waiting on the supervisor, not another task for the executor.
        dr = r["days_remaining"]
        if dr is not None and dr < 0:
            sev = "ALTO"
        elif dr is not None and dr <= 7:
            sev = "MEDIO"
        else:
            sev = "BAJO"
        temporal = _compute_temporal(dr)
        subtitle = r["ipr_codigo_bip"] if r["ipr_codigo_bip"] else None
        items.append(ActionItem(
            id=r["id"],
            category="COMPROMISO",
            title=r["description"] or "Compromiso sin descripción",
            subtitle=subtitle,
            deadline=r["due_date"],
            days_remaining=dr,
            temporal=temporal,
            severity=sev,
            priority=_compute_priority(temporal, sev),
            action_label="Verificar" if "verificar" in actions else "Completar" if "completar" in actions else "Revisar",
            action_route=f"/compromisos?id={r['id']}",
            ipr_id=r.get("ipr_id"),
            ipr_codigo_bip=r.get("ipr_codigo_bip"),
            state=r["state"],
            state_label=r["state_label"],
            responsible_id=str(r["responsible_id"]),
            responsible_name=r["responsible_name"],
        ))
    return items


async def _ai_alerts(db: AsyncSession, user: dict) -> list[ActionItem]:
    role = user["role_code"]
    uid = str(user["id"])
    div_id = str(user["division_id"]) if user.get("division_id") else None

    params: dict = {}
    where_scope = ""

    conditions: list[str] = []
    apply_alert_scope(conditions, params, user)
    if role == "JEFE_DGI":
        conditions.append("al.code = 'CRITICO'")
    elif role in ("ESP_CONTROL_GESTION", "ESP_PROCESOS", "ESP_TD"):
        return []
    elif role not in (*_PERSONAL_ROLES, *_DIVISION_ROLES):
        conditions.append("al.code IN ('CRITICO', 'ALTO')")
    where_scope = "AND " + " AND ".join(conditions) if conditions else ""

    sql = text(f"""
        SELECT a.id::text AS id, al.code AS alert_code, a.message,
               a.subject_type, a.subject_id::text AS subject_id,
               a.triggered_at, a.attended_at
        FROM core.alert a
        JOIN ref.category al ON a.severity_id = al.id
        WHERE a.deleted_at IS NULL AND a.resolved_at IS NULL
          {where_scope}
        ORDER BY a.triggered_at DESC, a.id
        LIMIT 10
    """)
    rows = (await db.execute(sql, params)).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
        sev = _severity_from_alert(r["alert_code"])
        route = f"/alertas?id={r['id']}"
        ipr_id = str(r["subject_id"]) if r["subject_type"] == "core.ipr" else None
        items.append(ActionItem(
            id=r["id"],
            category="ALERTA",
            state="ATENDIDA" if r["attended_at"] else "SIN_RESOLVER",
            state_label="Atendida, sin resolver" if r["attended_at"] else "Sin resolver",
            title=r["message"] or "Alerta",
            subtitle=r["alert_code"],
            deadline=None,
            days_remaining=None,
            temporal=None,
            severity=sev,
            priority=_compute_priority(None, sev),
            action_label="Ver",
            action_route=route,
            ipr_id=ipr_id,
        ))
    return items


async def _ai_decisions(db: AsyncSession, user: dict) -> list[ActionItem]:
    role = user["role_code"]
    if role not in _COORDINATION_READ_ROLES:
        return []

    sql = text("""
        SELECT
            d.id::text AS id,
            d.description,
            d.due_date,
            d.responsible_id::text AS responsible_id,
            p.names || ' ' || p.paternal_surname AS responsible_name,
            ss.code AS state, ss.label AS state_label,
            (d.due_date - CURRENT_DATE) AS days_remaining,
            ts.code AS type_code
        FROM core.dgi_ar_decision d
        JOIN ref.category ss ON d.status_id = ss.id
        JOIN ref.category ts ON d.decision_type_id = ts.id
        LEFT JOIN core."user" u ON u.id = d.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE ss.code = 'PENDIENTE'
          AND d.deleted_at IS NULL
        ORDER BY d.due_date ASC NULLS LAST
        LIMIT 10
    """)
    rows = (await db.execute(sql)).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
        dr = r["days_remaining"]
        if dr is not None and dr <= 3:
            sev = "ALTO"
        else:
            sev = "MEDIO"
        temporal = _compute_temporal(dr)
        items.append(ActionItem(
            id=r["id"],
            category="DECISION",
            state=r["state"], state_label=r["state_label"],
            responsible_id=r["responsible_id"], responsible_name=r["responsible_name"],
            title=r["description"] or "Decisión AR",
            subtitle=r["type_code"],
            deadline=r["due_date"],
            days_remaining=dr,
            temporal=temporal,
            severity=sev,
            priority=_compute_priority(temporal, sev),
            action_label="Revisar decisión",
            action_route=f"/coordinacion?id={r['id']}",
        ))
    return items


async def _ai_escalations(db: AsyncSession, user: dict) -> list[ActionItem]:
    role = user["role_code"]
    if role not in _COORDINATION_READ_ROLES:
        return []

    params: dict = {}
    where_scope = ""

    if role in _DIVISION_ROLES:
        where_scope = "AND lc.code IN ('NIVEL_1', 'NIVEL_2')"

    sql = text(f"""
        SELECT
            e.id::text AS id,
            e.code AS ref_code,
            e.situation,
            ss.code AS state, ss.label AS state_label,
            e.deadline::date AS deadline,
            (e.deadline::date - CURRENT_DATE) AS days_remaining,
            lc.code AS level_code
        FROM core.dgi_escalation e
        JOIN ref.category ss ON e.status_id = ss.id
        JOIN ref.category lc ON e.level_id = lc.id
        WHERE ss.code IN ('ABIERTO', 'EN_GESTION')
          AND e.deleted_at IS NULL
          {where_scope}
        ORDER BY e.deadline ASC NULLS LAST
        LIMIT 10
    """)
    rows = (await db.execute(sql, params)).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
        dr = r["days_remaining"]
        sev = _severity_from_escalation_level(r["level_code"])
        temporal = _compute_temporal(dr)
        items.append(ActionItem(
            id=r["id"],
            category="ESCALAMIENTO",
            state=r["state"], state_label=r["state_label"],
            title=r["situation"] or f"Escalamiento {r['ref_code']}",
            subtitle=r["level_code"],
            deadline=r["deadline"],
            days_remaining=dr,
            temporal=temporal,
            severity=sev,
            priority=_compute_priority(temporal, sev),
            action_label="Revisar escalamiento",
            action_route=f"/escalamiento/{r['id']}",
        ))
    return items


async def _ai_sla_breaches(db: AsyncSession, user: dict) -> list[ActionItem]:
    role = user["role_code"]
    # The request API grants institutional reading to DGI; other roles can
    # only open their own requests. Attention must use that same boundary.
    scope = "" if role in DGI_ROLES else "AND sr.requester_id = :uid"
    sql = text(f"""
        SELECT
            sr.id::text AS id,
            s.name AS service_name,
            sr.service_id::text AS service_id,
            rs.code AS state, rs.label AS state_label,
            sr.assigned_to_id::text AS responsible_id,
            p.names || ' ' || p.paternal_surname AS responsible_name,
            EXTRACT(EPOCH FROM (NOW() - sr.created_at)) / 86400 AS elapsed_days,
            s.sla_days AS target_days
        FROM core.dgi_service_request sr
        JOIN core.dgi_service s ON sr.service_id = s.id
        JOIN ref.category rs ON sr.status_id = rs.id
        LEFT JOIN core."user" u ON u.id = sr.assigned_to_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE rs.code NOT IN ('COMPLETADA', 'RECHAZADA')
          AND sr.deleted_at IS NULL
          AND s.deleted_at IS NULL
          AND s.sla_days IS NOT NULL
          {scope}
          AND EXTRACT(EPOCH FROM (NOW() - sr.created_at)) / 86400 > s.sla_days
        ORDER BY (EXTRACT(EPOCH FROM (NOW() - sr.created_at)) / 86400 - s.sla_days) DESC
        LIMIT 10
    """)
    rows = (await db.execute(sql, {"uid": str(user["id"])})).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
        items.append(ActionItem(
            id=r["id"],
            category="SLA",
            state=r["state"], state_label=r["state_label"],
            responsible_id=r["responsible_id"], responsible_name=r["responsible_name"],
            title=f"SLA excedido: {r['service_name']}",
            subtitle=f"{round(float(r['elapsed_days']), 1)}d / {r['target_days']}d",
            deadline=None,
            days_remaining=None,
            temporal=None,
            severity="CRITICO",
            priority=_compute_priority(None, "CRITICO"),
            action_label="Ver",
            action_route=f"/servicios/solicitudes/{r['id']}",
        ))
    return items


async def _ai_risks(db: AsyncSession, user: dict) -> list[ActionItem]:
    params: dict = {}
    scope = risk_scope_where(user, params)
    sql = text(f"""
        SELECT
            r.id::text AS id,
            r.code AS ref_code,
            r.name,
            ss.code AS state, ss.label AS state_label,
            pc.code AS prob_code
        FROM core.risk r
        JOIN ref.category ss ON r.status_id = ss.id
        JOIN ref.category pc ON r.probability_id = pc.id
        WHERE ss.code IN ('IDENTIFICADO', 'EN_EVALUACION', 'EN_MITIGACION')
          AND pc.code IN ('ALTA', 'MUY_ALTA')
          AND r.deleted_at IS NULL
          {scope}
        ORDER BY
            CASE pc.code WHEN 'MUY_ALTA' THEN 0 ELSE 1 END ASC
        LIMIT 10
    """)
    rows = (await db.execute(sql, params)).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
        sev = _severity_from_risk_probability(r["prob_code"])
        items.append(ActionItem(
            id=r["id"],
            category="RIESGO",
            state=r["state"], state_label=r["state_label"],
            title=r["name"] or f"Riesgo {r['ref_code']}",
            subtitle=r["ref_code"],
            deadline=None,
            days_remaining=None,
            temporal=None,
            severity=sev,
            priority=_compute_priority(None, sev),
            action_label="Revisar riesgo",
            action_route=f"/riesgos/{r['id']}",
        ))
    return items


_SIGNATURE_ROLES = ("GOBERNADOR", "ADMIN_REGIONAL", "ADMIN_SISTEMA")


async def _ai_pending_signatures(db: AsyncSession, user: dict) -> list[ActionItem]:
    role = user["role_code"]
    if role not in _SIGNATURE_ROLES:
        return []

    sql = text("""
        SELECT aa.id::text, aa.act_number AS ref_code, aa.subject, 'acto' AS item_type,
               ss.code AS state, ss.label AS state_label
        FROM core.administrative_act aa
        JOIN ref.category ss ON ss.id = aa.state_id
        WHERE ss.valid_transitions ? 'FIRMADO' AND ss.scheme = 'act_state'
          AND aa.deleted_at IS NULL
        UNION ALL
        SELECT a.id::text, a.agreement_number AS ref_code,
               COALESCE(at.label, a.agreement_number) AS subject, 'convenio' AS item_type,
               ss.code AS state, ss.label AS state_label
        FROM core.agreement a
        LEFT JOIN ref.category at ON at.id = a.agreement_type_id
        JOIN ref.category ss ON ss.id = a.state_id
        WHERE ss.valid_transitions ? 'FIRMADO_GORE' AND ss.scheme = 'agreement_state'
          AND a.deleted_at IS NULL
        ORDER BY item_type
        LIMIT 15
    """)
    rows = (await db.execute(sql)).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
        route = f"/actos?id={r['id']}" if r["item_type"] == "acto" else f"/convenios?id={r['id']}"
        items.append(ActionItem(
            id=r["id"],
            category="FIRMA",
            state=r["state"], state_label=r["state_label"],
            title=f"{r['ref_code'] or 'S/N'} — {r['subject'] or 'Sin materia'}",
            subtitle=r["item_type"].capitalize(),
            deadline=None,
            days_remaining=None,
            temporal=None,
            severity="ALTO",
            priority=_compute_priority(None, "ALTO"),
            action_label="Firmar",
            action_route=route,
        ))
    return items

async def _ai_pending_renditions(db: AsyncSession, user: dict) -> list[ActionItem]:
    role = user["role_code"]
    if role not in ("JEFE_DIVISION", "JEFE_DEPARTAMENTO"):
        return []
    if not user.get("division_id"):
        return []

    sql = text("""
        SELECT r.id::text, LEFT(r.id::text, 8) AS ref_code,
               a.agreement_number, r.amount,
               rs.code AS state, rs.label AS state_label,
               r.responsible_id::text AS responsible_id,
               p.names || ' ' || p.paternal_surname AS responsible_name,
               COALESCE(r.phase_entered_at, r.updated_at) AS entered_at,
               EXTRACT(DAY FROM NOW() - COALESCE(r.phase_entered_at, r.updated_at))::int AS days_waiting
        FROM core.rendition r
        JOIN ref.category rs ON rs.id = r.state_id
        LEFT JOIN core.agreement a ON a.id = r.agreement_id
        JOIN core.ipr ipr ON ipr.id = COALESCE(r.ipr_id, a.ipr_id) AND ipr.deleted_at IS NULL
        LEFT JOIN core."user" u ON u.id = r.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE rs.code = 'VISADA_RTF'
          AND r.deleted_at IS NULL
          AND ipr.sponsor_division_id = :div_id
        ORDER BY r.phase_entered_at ASC
        LIMIT 10
    """)
    rows = (await db.execute(sql, {"div_id": str(user["division_id"])})).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
        days = r["days_waiting"] or 0
        sev = "CRITICO" if days > 3 else "ALTO" if days > 1 else "MEDIO"
        items.append(ActionItem(
            id=r["id"],
            category="RENDICION",
            state=r["state"], state_label=r["state_label"],
            responsible_id=r["responsible_id"], responsible_name=r["responsible_name"],
            title=f"Rendición {r['ref_code']} — {r['agreement_number'] or 'S/N'}",
            subtitle=f"{days}d esperando aprobación",
            deadline=None,
            days_remaining=None,
            temporal="VENCIDO" if days > 3 else "HOY" if days > 1 else None,
            severity=sev,
            priority=_compute_priority("VENCIDO" if days > 3 else None, sev),
            action_label="Revisar rendición",
            action_route=f"/rendiciones?id={r['id']}",
        ))
    return items

async def _ai_ipr_stale(db: AsyncSession, user: dict) -> list[ActionItem]:
    role = user["role_code"]
    user_id = str(user["id"])
    division_id = user.get("division_id")

    # Scope filter by role
    if role in ("ANALISTA", "RTF", "ASESOR_JURIDICO"):
        scope = "AND i.assignee_id = :uid"
    elif role in _DIVISION_ROLES:
        if not division_id:
            return []
        scope = "AND i.sponsor_division_id = :div_id"
    elif role in ("ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"):
        scope = ""  # global
    else:
        return []

    sql = text(f"""
        SELECT i.id::text, i.codigo_bip, i.name,
               i.assignee_id::text AS responsible_id,
               p.names || ' ' || p.paternal_surname AS responsible_name,
               sc.code AS status_code, sc.label AS status_label,
               mcd.code AS phase,
               EXTRACT(DAY FROM NOW() - i.phase_entered_at)::int AS days_in_phase
        FROM core.ipr i
        JOIN ref.category sc ON sc.id = i.status_id
        LEFT JOIN ref.category mcd ON mcd.id = i.mcd_phase_id
        LEFT JOIN core."user" u ON u.id = i.assignee_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE i.deleted_at IS NULL
          AND i.phase_entered_at IS NOT NULL
          AND EXTRACT(DAY FROM NOW() - i.phase_entered_at) > 7
          AND sc.code NOT IN ('CERRADO', 'ANULADO', 'TERMINADO_ANTICIPADAMENTE')
          {scope}
        ORDER BY i.phase_entered_at ASC
        LIMIT 5
    """)
    params: dict = {"uid": user_id}
    if division_id:
        params["div_id"] = str(division_id)
    rows = (await db.execute(sql, params)).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
        days = r["days_in_phase"] or 0
        sev = "ALTO" if days > 30 else "MEDIO"
        items.append(ActionItem(
            id=r["id"],
            category="IPR",
            state=r["status_code"], state_label=r["status_label"],
            responsible_id=r["responsible_id"], responsible_name=r["responsible_name"],
            title=f"{r['codigo_bip']} — {r['status_label'] or r['status_code']}",
            subtitle=f"{days}d en {r['phase'] or '?'}",
            deadline=None,
            days_remaining=None,
            temporal=None,
            severity=sev,
            priority=_compute_priority(None, sev),
            action_label="Ver",
            action_route=f"/ipr/{r['id']}",
            ipr_id=r["id"],
            ipr_codigo_bip=r["codigo_bip"],
        ))
    return items


@router.get("/action-items", response_model=ActionItemsResponse)
async def get_action_items(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Unified action-items feed: commitments, alerts, decisions, escalations,
    SLA breaches, and risks — scoped by the user's role and division.
    Sorted by priority (lower = more urgent).
    """
    _require_roles(user, *ALL_ROLES)
    # Gather all 9 sources
    commitments = await _ai_commitments(db, user)
    alerts = await _ai_alerts(db, user)
    decisions = await _ai_decisions(db, user)
    escalations = await _ai_escalations(db, user)
    sla_breaches = await _ai_sla_breaches(db, user)
    risks = await _ai_risks(db, user)
    signatures = await _ai_pending_signatures(db, user)
    renditions = await _ai_pending_renditions(db, user)
    stale_iprs = await _ai_ipr_stale(db, user)

    all_items = commitments + alerts + decisions + escalations + sla_breaches + risks + signatures + renditions + stale_iprs
    all_items.sort(key=lambda x: x.priority)

    # Count by severity (always include all 4 keys)
    counts: dict[str, int] = {"CRITICO": 0, "ALTO": 0, "MEDIO": 0, "BAJO": 0}
    for item in all_items:
        counts[item.severity] = counts.get(item.severity, 0) + 1

    # Summary
    vencidas = sum(1 for i in all_items if i.temporal == "VENCIDO")
    hoy = sum(1 for i in all_items if i.temporal == "HOY")
    if vencidas > 0 or hoy > 0:
        parts = []
        if vencidas > 0:
            parts.append(f"{vencidas} tarea{'s' if vencidas != 1 else ''} vencida{'s' if vencidas != 1 else ''}")
        if hoy > 0:
            parts.append(f"{hoy} para hoy")
        summary = "Tienes " + " y ".join(parts)
    else:
        summary = f"{len(all_items)} pendientes en tu ámbito" if all_items else "Sin pendientes en tu ámbito"

    # Greeting
    nombre = user.get("nombre", "") or ""
    first_name = nombre.split()[0] if nombre.strip() else "Usuario"

    return ActionItemsResponse(
        greeting_name=first_name,
        today=date.today(),
        summary=summary,
        items=all_items,
        counts=counts,
        scope_label="Mis asignaciones" if user["role_code"] in _PERSONAL_ROLES else "Mi división" if user["role_code"] in _DIVISION_ROLES else "Atención institucional y mis asignaciones",
        limited_sources=[name for name, source, limit in (
            ("Alertas", alerts, 10), ("Decisiones", decisions, 10),
            ("Escalamientos", escalations, 10), ("Servicios", sla_breaches, 10),
            ("Riesgos", risks, 10), ("Firmas", signatures, 15),
            ("Rendiciones", renditions, 10), ("IPR", stale_iprs, 5),
        ) if len(source) == limit],
    )

def _require_roles(user: dict, *roles: str) -> None:
    if user["role_code"] not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sin permisos suficientes",
        )
