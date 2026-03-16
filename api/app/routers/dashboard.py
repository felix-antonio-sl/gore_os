from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.schemas.dashboard import (
    ActionItem,
    ActionItemsResponse,
    DashboardResponse,
    KPICard,
    DashboardCommitment,
    DashboardAlert,
    DashboardProblem,
    TeamMemberLoad,
    MiDivisionResponse,
    CompromisoGroup,
    MisCompromisosResponse,
    DivisionBreakdown,
    DashboardExecutivoResponse,
    SemaforoItem,
    ChartDataPoint,
    BudgetChartPoint,
    ChartDataResponse,
)

# ---------------------------------------------------------------------------
# Semaforo helpers (shared with DGI cockpit)
# ---------------------------------------------------------------------------
_SIGNAL_PRIORITY = {"ROJO": 3, "AMARILLO": 2, "VERDE": 1}
_DIMENSION_LABELS = {
    "PRESUPUESTO": "Presupuesto",
    "CARTERA_IPR": "Cartera IPR",
    "CONVENIOS": "Convenios",
    "TDE": "Transformación Digital",
    "RIESGOS": "Riesgos",
}


def _worst_signal(signals: list[str | None]) -> str:
    best = "VERDE"
    for s in signals:
        if s and _SIGNAL_PRIORITY.get(s, 0) > _SIGNAL_PRIORITY.get(best, 0):
            best = s
    return best

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# ---------------------------------------------------------------------------
# Action-items helpers
# ---------------------------------------------------------------------------
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

# Roles that scope to own items only (no DGI / global views)
_PERSONAL_ROLES = ("ANALISTA", "RTF", "ASESOR_JURIDICO")
_DIVISION_ROLES = ("JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD")


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


# ---------------------------------------------------------------------------
# Action-items: 6 source query functions
# ---------------------------------------------------------------------------
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
        where_scope = (
            "AND oc.ipr_id IN ("
            "  SELECT i.id FROM core.ipr i"
            "  WHERE i.sponsor_division_id = :div_id AND i.deleted_at IS NULL"
            ")"
        )
        params["div_id"] = div_id
    else:
        # Global roles: only overdue
        where_scope = "AND oc.due_date < CURRENT_DATE"

    sql = text(f"""
        SELECT
            oc.id::text AS id,
            oc.ipr_id::text AS ipr_id,
            oc.description,
            ipr.codigo_bip AS ipr_codigo_bip,
            oc.due_date,
            (oc.due_date - CURRENT_DATE) AS days_remaining
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        LEFT JOIN core.ipr ipr ON ipr.id = oc.ipr_id AND ipr.deleted_at IS NULL
        WHERE sc.code NOT IN ('COMPLETADO', 'VERIFICADO', 'CANCELADO')
          AND oc.deleted_at IS NULL
          {where_scope}
        ORDER BY oc.due_date ASC NULLS LAST
        LIMIT 20
    """)
    rows = (await db.execute(sql, params)).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
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
            action_label="Completar",
            action_route=f"/ipr/{r['ipr_id']}?tab=compromisos" if r.get("ipr_id") else "/compromisos",
            ipr_id=r.get("ipr_id"),
            ipr_codigo_bip=r.get("ipr_codigo_bip"),
        ))
    return items


async def _ai_alerts(db: AsyncSession, user: dict) -> list[ActionItem]:
    role = user["role_code"]
    uid = str(user["id"])
    div_id = str(user["division_id"]) if user.get("division_id") else None

    params: dict = {}
    where_scope = ""

    if role in _PERSONAL_ROLES:
        where_scope = (
            "AND a.subject_id IN ("
            "  SELECT i.id FROM core.ipr i"
            "  WHERE i.assignee_id = :uid AND i.deleted_at IS NULL"
            ")"
        )
        params["uid"] = uid
    elif role in _DIVISION_ROLES:
        if not div_id:
            return []
        where_scope = (
            "AND a.subject_id IN ("
            "  SELECT i.id FROM core.ipr i"
            "  WHERE i.sponsor_division_id = :div_id AND i.deleted_at IS NULL"
            ")"
        )
        params["div_id"] = div_id
    elif role == "JEFE_DGI":
        where_scope = "AND al.code = 'CRITICO'"
    elif role in ("ESP_CONTROL_GESTION", "ESP_PROCESOS", "ESP_TD"):
        # ESP_* roles see SLA items via _ai_sla_breaches, not general alerts
        return []
    else:
        # Global roles: CRITICO + ALTO
        where_scope = "AND al.code IN ('CRITICO', 'ALTO')"

    sql = text(f"""
        SELECT
            a.id::text AS id,
            al.code AS alert_code,
            a.message,
            a.subject_type,
            a.subject_id::text AS subject_id
        FROM core.alert a
        JOIN ref.category al ON a.severity_id = al.id
        WHERE a.deleted_at IS NULL
          AND a.resolved_at IS NULL
          {where_scope}
        ORDER BY a.triggered_at DESC
        LIMIT 10
    """)
    rows = (await db.execute(sql, params)).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
        sev = _severity_from_alert(r["alert_code"])
        if r["subject_type"] == "core.ipr":
            route = f"/ipr/{r['subject_id']}?tab=alertas"
        else:
            route = "/alertas"
        ipr_id = str(r["subject_id"]) if r["subject_type"] == "core.ipr" else None
        items.append(ActionItem(
            id=r["id"],
            category="ALERTA",
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
    if role in (*_PERSONAL_ROLES, *_DIVISION_ROLES):
        return []

    sql = text("""
        SELECT
            d.id::text AS id,
            d.description,
            d.due_date,
            (d.due_date - CURRENT_DATE) AS days_remaining,
            ts.code AS type_code
        FROM core.dgi_ar_decision d
        JOIN ref.category ss ON d.status_id = ss.id
        JOIN ref.category ts ON d.decision_type_id = ts.id
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
            title=r["description"] or "Decisión AR",
            subtitle=r["type_code"],
            deadline=r["due_date"],
            days_remaining=dr,
            temporal=temporal,
            severity=sev,
            priority=_compute_priority(temporal, sev),
            action_label="Decidir",
            action_route="/coordinacion",
        ))
    return items


async def _ai_escalations(db: AsyncSession, user: dict) -> list[ActionItem]:
    role = user["role_code"]
    if role in _PERSONAL_ROLES:
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
            e.deadline,
            (e.deadline - CURRENT_DATE) AS days_remaining,
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
            title=r["situation"] or f"Escalamiento {r['ref_code']}",
            subtitle=r["level_code"],
            deadline=r["deadline"],
            days_remaining=dr,
            temporal=temporal,
            severity=sev,
            priority=_compute_priority(temporal, sev),
            action_label="Gestionar",
            action_route=f"/escalamiento/{r['id']}",
        ))
    return items


async def _ai_sla_breaches(db: AsyncSession, user: dict) -> list[ActionItem]:
    role = user["role_code"]
    if role in (*_PERSONAL_ROLES, *_DIVISION_ROLES):
        return []

    sql = text("""
        SELECT
            sr.id::text AS id,
            s.name AS service_name,
            sr.service_id::text AS service_id,
            EXTRACT(DAY FROM (NOW() - sr.created_at))::int AS elapsed_days,
            sla.target_days
        FROM core.dgi_service_request sr
        JOIN core.dgi_service s ON sr.service_id = s.id
        JOIN core.dgi_sla sla ON sla.service_id = s.id
        JOIN ref.category rs ON sr.status_id = rs.id
        WHERE rs.code NOT IN ('COMPLETADA', 'RECHAZADA')
          AND sr.deleted_at IS NULL
          AND s.deleted_at IS NULL
          AND EXTRACT(DAY FROM (NOW() - sr.created_at))::int > sla.target_days
        ORDER BY (EXTRACT(DAY FROM (NOW() - sr.created_at))::int - sla.target_days) DESC
        LIMIT 10
    """)
    rows = (await db.execute(sql)).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
        items.append(ActionItem(
            id=r["id"],
            category="SLA",
            title=f"SLA excedido: {r['service_name']}",
            subtitle=f"{r['elapsed_days']}d / {r['target_days']}d",
            deadline=None,
            days_remaining=None,
            temporal=None,
            severity="CRITICO",
            priority=_compute_priority(None, "CRITICO"),
            action_label="Ver",
            action_route=f"/servicios/{r['service_id']}",
        ))
    return items


async def _ai_risks(db: AsyncSession, user: dict) -> list[ActionItem]:
    role = user["role_code"]
    if role in (*_PERSONAL_ROLES, *_DIVISION_ROLES):
        return []

    sql = text("""
        SELECT
            r.id::text AS id,
            r.code AS ref_code,
            r.name,
            pc.code AS prob_code
        FROM core.risk r
        JOIN ref.category ss ON r.status_id = ss.id
        JOIN ref.category pc ON r.probability_id = pc.id
        WHERE ss.code IN ('IDENTIFICADO', 'EN_EVALUACION', 'EN_MITIGACION')
          AND pc.code IN ('ALTA', 'MUY_ALTA')
          AND r.deleted_at IS NULL
        ORDER BY
            CASE pc.code WHEN 'MUY_ALTA' THEN 0 ELSE 1 END ASC
        LIMIT 10
    """)
    rows = (await db.execute(sql)).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
        sev = _severity_from_risk_probability(r["prob_code"])
        items.append(ActionItem(
            id=r["id"],
            category="RIESGO",
            title=r["name"] or f"Riesgo {r['ref_code']}",
            subtitle=r["ref_code"],
            deadline=None,
            days_remaining=None,
            temporal=None,
            severity=sev,
            priority=_compute_priority(None, sev),
            action_label="Gestionar",
            action_route=f"/riesgos/{r['id']}",
        ))
    return items


# ---------------------------------------------------------------------------
# Source 7: Pending signatures — actos VISADO + convenios VISADO_INTERNAMENTE
# For: GOBERNADOR, ADMIN_REGIONAL, ADMIN_SISTEMA (G9+G12)
# ---------------------------------------------------------------------------

_SIGNATURE_ROLES = ("GOBERNADOR", "ADMIN_REGIONAL", "ADMIN_SISTEMA")


async def _ai_pending_signatures(db: AsyncSession, user: dict) -> list[ActionItem]:
    role = user["role_code"]
    if role not in _SIGNATURE_ROLES:
        return []

    sql = text("""
        SELECT id::text, act_number AS ref_code, subject, 'acto' AS item_type
        FROM core.administrative_act
        WHERE state_id IN (SELECT id FROM ref.category WHERE scheme = 'administrative_act_step' AND code = 'VISADO')
          AND deleted_at IS NULL
        UNION ALL
        SELECT a.id::text, a.agreement_number AS ref_code,
               COALESCE(at.label, a.agreement_number) AS subject, 'convenio' AS item_type
        FROM core.agreement a
        LEFT JOIN ref.category at ON at.id = a.agreement_type_id
        WHERE a.state_id IN (SELECT id FROM ref.category WHERE scheme = 'agreement_state' AND code = 'VISADO_INTERNAMENTE')
          AND a.deleted_at IS NULL
        ORDER BY item_type
        LIMIT 15
    """)
    rows = (await db.execute(sql)).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
        route = f"/actos/{r['id']}" if r["item_type"] == "acto" else f"/convenios/{r['id']}"
        items.append(ActionItem(
            id=r["id"],
            category="FIRMA",
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


# ---------------------------------------------------------------------------
# Source 8: Pending rendition approvals — VISADA_RTF waiting Jefe DAF
# For: JEFE_DIVISION, JEFE_DEPARTAMENTO in DAF (G11)
# ---------------------------------------------------------------------------

async def _ai_pending_renditions(db: AsyncSession, user: dict) -> list[ActionItem]:
    role = user["role_code"]
    if role not in ("JEFE_DIVISION", "JEFE_DEPARTAMENTO"):
        return []

    sql = text("""
        SELECT r.id::text, LEFT(r.id::text, 8) AS ref_code,
               a.agreement_number, r.amount,
               COALESCE(r.phase_entered_at, r.updated_at) AS entered_at,
               EXTRACT(DAY FROM NOW() - COALESCE(r.phase_entered_at, r.updated_at))::int AS days_waiting
        FROM core.rendition r
        JOIN ref.category rs ON rs.id = r.state_id
        LEFT JOIN core.agreement a ON a.id = r.agreement_id
        WHERE rs.code = 'VISADA_RTF'
          AND r.deleted_at IS NULL
        ORDER BY r.phase_entered_at ASC
        LIMIT 10
    """)
    rows = (await db.execute(sql)).mappings().all()

    items: list[ActionItem] = []
    for r in rows:
        days = r["days_waiting"] or 0
        sev = "CRITICO" if days > 3 else "ALTO" if days > 1 else "MEDIO"
        items.append(ActionItem(
            id=r["id"],
            category="RENDICION",
            title=f"Rendición {r['ref_code']} — {r['agreement_number'] or 'S/N'}",
            subtitle=f"{days}d esperando aprobación",
            deadline=None,
            days_remaining=None,
            temporal="VENCIDO" if days > 3 else "HOY" if days > 1 else None,
            severity=sev,
            priority=_compute_priority("VENCIDO" if days > 3 else None, sev),
            action_label="Aprobar",
            action_route="/datos?dominio=rendiciones&state=VISADA_RTF",
        ))
    return items


# ---------------------------------------------------------------------------
# Source 9: IPRs stale — in user's scope, user can transition, >7d in state
# For: TRANSITION_ROLES (G15)
# ---------------------------------------------------------------------------

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
               sc.code AS status_code, sc.label AS status_label,
               mcd.code AS phase,
               EXTRACT(DAY FROM NOW() - i.phase_entered_at)::int AS days_in_phase
        FROM core.ipr i
        JOIN ref.category sc ON sc.id = i.status_id
        LEFT JOIN ref.category mcd ON mcd.id = i.mcd_phase_id
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


# ---------------------------------------------------------------------------
# Helper: overdue predicate (state NOT IN verified/cancelled AND past due_date)
# ---------------------------------------------------------------------------
_OVERDUE_STATES_EXCLUDED = ("'VERIFICADO'", "'CANCELADO'")
_OVERDUE_PRED = (
    "AND sc.code NOT IN ('VERIFICADO', 'CANCELADO') "
    "AND oc.due_date < CURRENT_DATE "
    "AND oc.deleted_at IS NULL"
)


# ---------------------------------------------------------------------------
# Personal scope dashboard (ANALISTA, RTF, ASESOR_JURIDICO, JEFE_UNIDAD)
# ---------------------------------------------------------------------------
async def _dashboard_personal(user: dict, db: AsyncSession) -> DashboardResponse:
    user_id = str(user["id"])

    # ── KPIs ──────────────────────────────────────────────────────────────
    kpi_sql = text("""
        SELECT
            SUM(CASE WHEN sc.code = 'PENDIENTE'   THEN 1 ELSE 0 END) AS pendientes,
            SUM(CASE WHEN sc.code = 'EN_PROGRESO'  THEN 1 ELSE 0 END) AS en_progreso,
            SUM(CASE WHEN sc.code = 'COMPLETADO'   THEN 1 ELSE 0 END) AS completados
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        WHERE oc.responsible_id = :uid
          AND oc.deleted_at IS NULL
    """)
    kpi_row = (await db.execute(kpi_sql, {"uid": user_id})).mappings().first()

    # Mis Alertas: alerts where subject_id in IPRs assigned to me
    alerts_kpi_sql = text("""
        SELECT COUNT(*) AS mis_alertas
        FROM core.alert a
        WHERE a.subject_type = 'core.ipr'
          AND a.subject_id IN (
              SELECT id FROM core.ipr
              WHERE assignee_id = :uid AND deleted_at IS NULL
          )
          AND a.resolved_at IS NULL
          AND a.deleted_at IS NULL
    """)
    alerts_kpi_row = (await db.execute(alerts_kpi_sql, {"uid": user_id})).mappings().first()

    kpis = [
        KPICard(label="Pendientes",    value=kpi_row["pendientes"]  or 0, sublabel="Mis compromisos",   color="amber"),
        KPICard(label="En Progreso",   value=kpi_row["en_progreso"] or 0, sublabel="En ejecución",      color="blue"),
        KPICard(label="Completados",   value=kpi_row["completados"] or 0, sublabel="Este período",      color="green"),
        KPICard(label="Mis Alertas",   value=alerts_kpi_row["mis_alertas"] or 0, sublabel="Sin resolver", color="red"),
    ]

    # ── Commitments (overdue first, then by due_date ASC, limit 10) ───────
    comm_sql = text("""
        SELECT
            oc.id,
            oc.description,
            ipr.codigo_bip  AS ipr_codigo_bip,
            p.names || ' ' || p.paternal_surname AS responsible_name,
            oc.due_date,
            sc.code         AS state,
            (oc.due_date - CURRENT_DATE) AS days_remaining
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        LEFT JOIN core.ipr ipr ON ipr.id = oc.ipr_id AND ipr.deleted_at IS NULL
        LEFT JOIN core."user" u ON u.id = oc.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE oc.responsible_id = :uid
          AND oc.deleted_at IS NULL
          AND sc.code NOT IN ('VERIFICADO', 'CANCELADO')
        ORDER BY
            CASE WHEN oc.due_date < CURRENT_DATE THEN 0 ELSE 1 END ASC,
            oc.due_date ASC
        LIMIT 10
    """)
    comm_rows = (await db.execute(comm_sql, {"uid": user_id})).mappings().all()

    commitments = [
        DashboardCommitment(
            id=r["id"],
            description=r["description"],
            ipr_codigo_bip=r["ipr_codigo_bip"],
            responsible_name=r["responsible_name"],
            due_date=r["due_date"],
            state=r["state"],
            days_remaining=r["days_remaining"],
        )
        for r in comm_rows
    ]

    # ── Alerts (my IPRs, limit 5) ─────────────────────────────────────────
    alert_sql = text("""
        SELECT
            a.id,
            sev.code        AS severity,
            a.message,
            a.subject_type,
            a.subject_id,
            a.triggered_at
        FROM core.alert a
        LEFT JOIN ref.category sev ON sev.id = a.severity_id
        WHERE a.subject_type = 'core.ipr'
          AND a.subject_id IN (
              SELECT id FROM core.ipr
              WHERE assignee_id = :uid AND deleted_at IS NULL
          )
          AND a.resolved_at IS NULL
          AND a.deleted_at IS NULL
        ORDER BY a.triggered_at DESC
        LIMIT 5
    """)
    alert_rows = (await db.execute(alert_sql, {"uid": user_id})).mappings().all()

    alerts = [
        DashboardAlert(
            id=r["id"],
            severity=r["severity"],
            message=r["message"],
            subject_type=r["subject_type"],
            subject_id=r["subject_id"],
            triggered_at=r["triggered_at"],
        )
        for r in alert_rows
    ]

    return DashboardResponse(kpis=kpis, commitments=commitments, alerts=alerts, problems=[])


# ---------------------------------------------------------------------------
# JEFE_DIVISION dashboard
# ---------------------------------------------------------------------------
async def _dashboard_jefe_division(user: dict, db: AsyncSession) -> DashboardResponse:
    division_id = str(user["division_id"]) if user.get("division_id") else None

    if not division_id:
        return DashboardResponse(kpis=[], commitments=[], alerts=[], problems=[])

    # ── KPIs ──────────────────────────────────────────────────────────────
    kpi_sql = text("""
        SELECT
            -- Vencidos en mi división
            SUM(
                CASE WHEN sc.code NOT IN ('VERIFICADO','CANCELADO')
                          AND oc.due_date < CURRENT_DATE
                     THEN 1 ELSE 0 END
            ) AS vencidos,
            -- Por Verificar (COMPLETADO sin verificar)
            SUM(
                CASE WHEN sc.code = 'COMPLETADO' THEN 1 ELSE 0 END
            ) AS por_verificar
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        WHERE oc.division_id = :div_id
          AND oc.deleted_at IS NULL
    """)
    kpi_row = (await db.execute(kpi_sql, {"div_id": division_id})).mappings().first()

    # Problemas abiertos en mi división
    prob_kpi_sql = text("""
        SELECT COUNT(*) AS problemas_abiertos
        FROM core.ipr_problem ip
        JOIN ref.category ps ON ps.id = ip.state_id
        JOIN core.ipr i ON i.id = ip.ipr_id
        WHERE ps.code IN ('ABIERTO', 'EN_GESTION')
          AND i.sponsor_division_id = :div_id
          AND i.deleted_at IS NULL
          AND ip.deleted_at IS NULL
    """)
    prob_kpi_row = (await db.execute(prob_kpi_sql, {"div_id": division_id})).mappings().first()

    # Alertas en mi división
    alert_kpi_sql = text("""
        SELECT COUNT(*) AS alertas_div
        FROM core.alert a
        WHERE a.subject_type = 'core.ipr'
          AND a.subject_id IN (
              SELECT id FROM core.ipr
              WHERE sponsor_division_id = :div_id AND deleted_at IS NULL
          )
          AND a.resolved_at IS NULL
          AND a.deleted_at IS NULL
    """)
    alert_kpi_row = (await db.execute(alert_kpi_sql, {"div_id": division_id})).mappings().first()

    # Ejecución presupuestaria de mi división
    ppto_div_sql = text("""
        SELECT
            ROUND(SUM(paid_amount)::numeric / NULLIF(SUM(current_amount), 0)::numeric * 100, 1) AS ejecucion_pct
        FROM core.budget_program
        WHERE owner_division_id = :div_id
          AND fiscal_year = EXTRACT(YEAR FROM CURRENT_DATE)
          AND deleted_at IS NULL
    """)
    ppto_div_row = (await db.execute(ppto_div_sql, {"div_id": division_id})).mappings().first()
    ppto_div_pct = int(ppto_div_row["ejecucion_pct"] or 0) if ppto_div_row else 0
    ppto_div_color = "green" if ppto_div_pct >= 70 else ("amber" if ppto_div_pct >= 40 else "gray")

    kpis = [
        KPICard(label="Vencidos mi div",    value=kpi_row["vencidos"]              or 0, sublabel="Compromisos vencidos",     color="red"),
        KPICard(label="Por Verificar",       value=kpi_row["por_verificar"]         or 0, sublabel="Completados sin verificar", color="amber"),
        KPICard(label="Problemas abiertos",  value=prob_kpi_row["problemas_abiertos"] or 0, sublabel="En mi división",         color="orange"),
        KPICard(label="Ejec. Presupuestaria", value=ppto_div_pct,                         sublabel="Mi división",              color=ppto_div_color),
    ]

    # ── Commitments: COMPLETADO in division (pending verification), limit 10
    comm_sql = text("""
        SELECT
            oc.id,
            oc.description,
            ipr.codigo_bip  AS ipr_codigo_bip,
            p.names || ' ' || p.paternal_surname AS responsible_name,
            oc.due_date,
            sc.code         AS state,
            (oc.due_date - CURRENT_DATE) AS days_remaining
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        LEFT JOIN core.ipr ipr ON ipr.id = oc.ipr_id AND ipr.deleted_at IS NULL
        LEFT JOIN core."user" u ON u.id = oc.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE oc.division_id = :div_id
          AND sc.code = 'COMPLETADO'
          AND oc.deleted_at IS NULL
        ORDER BY oc.completed_at ASC
        LIMIT 10
    """)
    comm_rows = (await db.execute(comm_sql, {"div_id": division_id})).mappings().all()

    commitments = [
        DashboardCommitment(
            id=r["id"],
            description=r["description"],
            ipr_codigo_bip=r["ipr_codigo_bip"],
            responsible_name=r["responsible_name"],
            due_date=r["due_date"],
            state=r["state"],
            days_remaining=r["days_remaining"],
        )
        for r in comm_rows
    ]

    # ── Problems: open in my division, limit 5 ───────────────────────────
    prob_sql = text("""
        SELECT
            ip.id,
            ipr.codigo_bip  AS ipr_codigo_bip,
            pt.code         AS problem_type,
            EXTRACT(DAY FROM (NOW() - ip.detected_at))::int AS days_open,
            ps.code         AS state
        FROM core.ipr_problem ip
        JOIN ref.category ps ON ps.id = ip.state_id
        JOIN ref.category pt ON pt.id = ip.problem_type_id
        JOIN core.ipr ipr ON ipr.id = ip.ipr_id
        WHERE ps.code IN ('ABIERTO', 'EN_GESTION')
          AND ipr.sponsor_division_id = :div_id
          AND ipr.deleted_at IS NULL
          AND ip.deleted_at IS NULL
        ORDER BY ip.detected_at ASC
        LIMIT 5
    """)
    prob_rows = (await db.execute(prob_sql, {"div_id": division_id})).mappings().all()

    problems = [
        DashboardProblem(
            id=r["id"],
            ipr_codigo_bip=r["ipr_codigo_bip"],
            problem_type=r["problem_type"],
            days_open=r["days_open"] or 0,
            state=r["state"],
        )
        for r in prob_rows
    ]

    return DashboardResponse(kpis=kpis, commitments=commitments, alerts=[], problems=problems)


# ---------------------------------------------------------------------------
# ADMIN_REGIONAL dashboard
# ---------------------------------------------------------------------------
async def _dashboard_admin_regional(user: dict, db: AsyncSession) -> DashboardResponse:

    # ── KPIs ──────────────────────────────────────────────────────────────
    # IPRs críticas (with CRITICO alert)
    criticas_sql = text("""
        SELECT COUNT(DISTINCT i.id) AS iprs_criticas
        FROM core.ipr i
        JOIN core.alert a ON a.subject_type = 'core.ipr' AND a.subject_id = i.id
        JOIN ref.category sev ON sev.id = a.severity_id
        WHERE sev.code = 'CRITICO'
          AND a.resolved_at IS NULL
          AND a.deleted_at IS NULL
          AND i.deleted_at IS NULL
    """)
    criticas_row = (await db.execute(criticas_sql)).mappings().first()

    # Compromisos vencidos global
    vencidos_sql = text("""
        SELECT COUNT(*) AS vencidos_global
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        WHERE sc.code NOT IN ('VERIFICADO', 'CANCELADO')
          AND oc.due_date < CURRENT_DATE
          AND oc.deleted_at IS NULL
    """)
    vencidos_row = (await db.execute(vencidos_sql)).mappings().first()

    # Problemas > 7 días (abiertos/en gestión, detectados hace más de 7 días)
    prob7_sql = text("""
        SELECT COUNT(*) AS problemas_7d
        FROM core.ipr_problem ip
        JOIN ref.category ps ON ps.id = ip.state_id
        WHERE ps.code IN ('ABIERTO', 'EN_GESTION')
          AND ip.detected_at < NOW() - INTERVAL '7 days'
          AND ip.deleted_at IS NULL
    """)
    prob7_row = (await db.execute(prob7_sql)).mappings().first()

    # Alertas sin atender
    alertas_sql = text("""
        SELECT COUNT(*) AS alertas_sin_atender
        FROM core.alert a
        WHERE a.attended_at IS NULL
          AND a.resolved_at IS NULL
          AND a.deleted_at IS NULL
    """)
    alertas_row = (await db.execute(alertas_sql)).mappings().first()

    # Ejecución presupuestaria global
    ppto_sql = text("""
        SELECT
            ROUND(SUM(paid_amount)::numeric / NULLIF(SUM(current_amount), 0)::numeric * 100, 1) AS ejecucion_pct,
            COUNT(*) AS program_count
        FROM core.budget_program
        WHERE fiscal_year = EXTRACT(YEAR FROM CURRENT_DATE) AND deleted_at IS NULL
    """)
    ppto_row = (await db.execute(ppto_sql)).mappings().first()
    ppto_pct = int(ppto_row["ejecucion_pct"] or 0)
    ppto_count = int(ppto_row["program_count"] or 0)
    ppto_color = "green" if ppto_pct >= 70 else ("amber" if ppto_pct >= 40 else "red")

    # Convenios por vencer en 30 días
    conv_sql = text("""
        SELECT COUNT(*) AS conv_por_vencer
        FROM core.agreement a
        JOIN ref.category st ON st.id = a.state_id
        WHERE st.code = 'VIGENTE'
          AND a.valid_to IS NOT NULL
          AND a.valid_to < NOW() + INTERVAL '30 days'
          AND a.deleted_at IS NULL
    """)
    conv_row = (await db.execute(conv_sql)).mappings().first()
    conv_count = int(conv_row["conv_por_vencer"] or 0)

    kpis = [
        KPICard(label="IPRs críticas",          value=criticas_row["iprs_criticas"]       or 0, sublabel="Con alerta CRÍTICO",      color="red"),
        KPICard(label="Compromisos vencidos",    value=vencidos_row["vencidos_global"]     or 0, sublabel="Global",                  color="red"),
        KPICard(label="Ejec. Presupuestaria",    value=ppto_pct,                               sublabel=f"{ppto_count} programas",   color=ppto_color),
        KPICard(label="Convenios por vencer",    value=conv_count,                             sublabel="Próximos 30 días",          color="amber" if conv_count > 0 else "green"),
    ]

    # ── Commitments: all overdue, limit 15 ────────────────────────────────
    comm_sql = text("""
        SELECT
            oc.id,
            oc.description,
            ipr.codigo_bip  AS ipr_codigo_bip,
            p.names || ' ' || p.paternal_surname AS responsible_name,
            oc.due_date,
            sc.code         AS state,
            (oc.due_date - CURRENT_DATE) AS days_remaining
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        LEFT JOIN core.ipr ipr ON ipr.id = oc.ipr_id AND ipr.deleted_at IS NULL
        LEFT JOIN core."user" u ON u.id = oc.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE sc.code NOT IN ('VERIFICADO', 'CANCELADO')
          AND oc.due_date < CURRENT_DATE
          AND oc.deleted_at IS NULL
        ORDER BY oc.due_date ASC
        LIMIT 15
    """)
    comm_rows = (await db.execute(comm_sql)).mappings().all()

    commitments = [
        DashboardCommitment(
            id=r["id"],
            description=r["description"],
            ipr_codigo_bip=r["ipr_codigo_bip"],
            responsible_name=r["responsible_name"],
            due_date=r["due_date"],
            state=r["state"],
            days_remaining=r["days_remaining"],
        )
        for r in comm_rows
    ]

    # ── Alerts: unattended, sorted by severity, limit 10 ─────────────────
    alert_sql = text("""
        SELECT
            a.id,
            sev.code        AS severity,
            a.message,
            a.subject_type,
            a.subject_id,
            a.triggered_at
        FROM core.alert a
        LEFT JOIN ref.category sev ON sev.id = a.severity_id
        WHERE a.attended_at IS NULL
          AND a.resolved_at IS NULL
          AND a.deleted_at IS NULL
        ORDER BY
            CASE sev.code
                WHEN 'CRITICO'  THEN 1
                WHEN 'ALTO'     THEN 2
                WHEN 'ATENCION' THEN 3
                WHEN 'INFO'     THEN 4
                ELSE 5
            END ASC,
            a.triggered_at ASC
        LIMIT 10
    """)
    alert_rows = (await db.execute(alert_sql)).mappings().all()

    alerts = [
        DashboardAlert(
            id=r["id"],
            severity=r["severity"],
            message=r["message"],
            subject_type=r["subject_type"],
            subject_id=r["subject_id"],
            triggered_at=r["triggered_at"],
        )
        for r in alert_rows
    ]

    return DashboardResponse(kpis=kpis, commitments=commitments, alerts=alerts, problems=[])


# ---------------------------------------------------------------------------
# Generic admin-level dashboard (ADMIN_SISTEMA, JEFE_DGI, ESP_* roles)
# ---------------------------------------------------------------------------
async def _dashboard_generic_admin(user: dict, db: AsyncSession) -> DashboardResponse:
    """Minimal dashboard for admin-like roles not covered by specific handlers."""
    return await _dashboard_admin_regional(user, db)


# ---------------------------------------------------------------------------
# Main router endpoint
# ---------------------------------------------------------------------------
@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Role-aware dashboard endpoint.

    Returns KPIs, commitments, alerts, and problems scoped to the user's role:
    - ANALISTA/RTF/ASESOR_JURIDICO/JEFE_UNIDAD: personal commitments and alerts on assigned IPRs
    - JEFE_DIVISION: division-scoped commitments and problems
    - ADMIN_REGIONAL / ADMIN_SISTEMA / JEFE_DGI / ESP_*: global overview
    """
    role_code = user["role_code"]

    if role_code in ("ANALISTA", "RTF", "ASESOR_JURIDICO", "JEFE_UNIDAD"):
        return await _dashboard_personal(user, db)

    if role_code in ("JEFE_DIVISION", "JEFE_DEPARTAMENTO"):
        return await _dashboard_jefe_division(user, db)

    if role_code in (
        "ADMIN_REGIONAL",
        "ADMIN_SISTEMA",
        "GOBERNADOR",
        "SECRETARIO_EJECUTIVO",
        "CONSEJERO_REGIONAL",
        "JEFE_DGI",
        "ESP_CONTROL_GESTION",
        "ESP_TD",
        "ESP_PROCESOS",
    ):
        return await _dashboard_admin_regional(user, db)

    # Fallback: same as admin regional
    return await _dashboard_admin_regional(user, db)


# ---------------------------------------------------------------------------
# GET /api/dashboard/mi-division — Team stats for JEFE_DIVISION
# ---------------------------------------------------------------------------

@router.get("/mi-division", response_model=MiDivisionResponse)
async def get_mi_division(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    division_id = str(user["division_id"]) if user.get("division_id") else None
    if not division_id:
        return MiDivisionResponse(kpis=[], team=[], commitments=[])

    # KPIs de la división
    kpi_sql = text("""
        SELECT
            SUM(CASE WHEN sc.code NOT IN ('VERIFICADO','CANCELADO') AND oc.due_date < CURRENT_DATE THEN 1 ELSE 0 END) AS vencidos,
            SUM(CASE WHEN sc.code = 'PENDIENTE' THEN 1 ELSE 0 END) AS pendientes,
            SUM(CASE WHEN sc.code = 'COMPLETADO' THEN 1 ELSE 0 END) AS por_verificar,
            COUNT(*) FILTER (WHERE sc.code NOT IN ('VERIFICADO','CANCELADO')) AS activos
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        WHERE oc.division_id = :div_id AND oc.deleted_at IS NULL
    """)
    kpi_row = (await db.execute(kpi_sql, {"div_id": division_id})).mappings().first()

    kpis = [
        KPICard(label="Vencidos", value=kpi_row["vencidos"] or 0, sublabel="Compromisos vencidos", color="red"),
        KPICard(label="Pendientes", value=kpi_row["pendientes"] or 0, sublabel="Sin iniciar", color="amber"),
        KPICard(label="Por Verificar", value=kpi_row["por_verificar"] or 0, sublabel="Completados", color="blue"),
        KPICard(label="Activos", value=kpi_row["activos"] or 0, sublabel="Total en curso", color="green"),
    ]

    # Carga por persona del equipo
    team_sql = text("""
        SELECT
            u.id AS user_id,
            p.names || ' ' || p.paternal_surname AS name,
            SUM(CASE WHEN sc.code = 'PENDIENTE' THEN 1 ELSE 0 END) AS pendientes,
            SUM(CASE WHEN sc.code = 'EN_PROGRESO' THEN 1 ELSE 0 END) AS en_progreso,
            SUM(CASE WHEN sc.code = 'COMPLETADO' THEN 1 ELSE 0 END) AS completados,
            SUM(CASE WHEN sc.code NOT IN ('VERIFICADO','CANCELADO') AND oc.due_date < CURRENT_DATE THEN 1 ELSE 0 END) AS vencidos,
            COUNT(*) AS total
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        JOIN core."user" u ON u.id = oc.responsible_id
        JOIN core.person p ON p.id = u.person_id
        WHERE oc.division_id = :div_id
          AND oc.deleted_at IS NULL
          AND sc.code NOT IN ('VERIFICADO', 'CANCELADO')
        GROUP BY u.id, p.names, p.paternal_surname
        ORDER BY SUM(CASE WHEN sc.code NOT IN ('VERIFICADO','CANCELADO') AND oc.due_date < CURRENT_DATE THEN 1 ELSE 0 END) DESC
    """)
    team_rows = (await db.execute(team_sql, {"div_id": division_id})).mappings().all()
    team = [TeamMemberLoad(**dict(r)) for r in team_rows]

    # Compromisos vencidos de la división
    comm_sql = text("""
        SELECT
            oc.id, oc.description,
            ipr.codigo_bip AS ipr_codigo_bip,
            p.names || ' ' || p.paternal_surname AS responsible_name,
            oc.due_date, sc.code AS state,
            (oc.due_date - CURRENT_DATE) AS days_remaining
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        LEFT JOIN core.ipr ipr ON ipr.id = oc.ipr_id AND ipr.deleted_at IS NULL
        LEFT JOIN core."user" u ON u.id = oc.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE oc.division_id = :div_id
          AND sc.code NOT IN ('VERIFICADO', 'CANCELADO')
          AND oc.due_date < CURRENT_DATE
          AND oc.deleted_at IS NULL
        ORDER BY oc.due_date ASC
        LIMIT 20
    """)
    comm_rows = (await db.execute(comm_sql, {"div_id": division_id})).mappings().all()
    commitments = [DashboardCommitment(**dict(r)) for r in comm_rows]

    return MiDivisionResponse(kpis=kpis, team=team, commitments=commitments)


# ---------------------------------------------------------------------------
# GET /api/dashboard/mis-compromisos — Personal commitments for personal-scope roles
# ---------------------------------------------------------------------------

@router.get("/mis-compromisos", response_model=MisCompromisosResponse)
async def get_mis_compromisos(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    user_id = str(user["id"])

    # KPIs personales
    kpi_sql = text("""
        SELECT
            SUM(CASE WHEN sc.code NOT IN ('VERIFICADO','CANCELADO') AND oc.due_date < CURRENT_DATE THEN 1 ELSE 0 END) AS vencidos,
            SUM(CASE WHEN sc.code = 'PENDIENTE' THEN 1 ELSE 0 END) AS pendientes,
            SUM(CASE WHEN sc.code = 'EN_PROGRESO' THEN 1 ELSE 0 END) AS en_progreso,
            SUM(CASE WHEN sc.code = 'COMPLETADO' AND oc.completed_at >= date_trunc('month', CURRENT_DATE) THEN 1 ELSE 0 END) AS completados_mes
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        WHERE oc.responsible_id = :uid AND oc.deleted_at IS NULL
    """)
    kpi_row = (await db.execute(kpi_sql, {"uid": user_id})).mappings().first()

    kpis = [
        KPICard(label="Vencidos", value=kpi_row["vencidos"] or 0, sublabel="Requieren atencion", color="red"),
        KPICard(label="Pendientes", value=kpi_row["pendientes"] or 0, sublabel="Sin iniciar", color="amber"),
        KPICard(label="En Progreso", value=kpi_row["en_progreso"] or 0, sublabel="En ejecucion", color="blue"),
        KPICard(label="Completados", value=kpi_row["completados_mes"] or 0, sublabel="Este mes", color="green"),
    ]

    # Vencidos
    vencidos_sql = text("""
        SELECT oc.id, oc.description, ipr.codigo_bip AS ipr_codigo_bip,
               p.names || ' ' || p.paternal_surname AS responsible_name,
               oc.due_date, sc.code AS state, (oc.due_date - CURRENT_DATE) AS days_remaining
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        LEFT JOIN core.ipr ipr ON ipr.id = oc.ipr_id AND ipr.deleted_at IS NULL
        LEFT JOIN core."user" u ON u.id = oc.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE oc.responsible_id = :uid AND oc.deleted_at IS NULL
          AND sc.code NOT IN ('VERIFICADO','CANCELADO') AND oc.due_date < CURRENT_DATE
        ORDER BY oc.due_date ASC LIMIT 20
    """)
    vencidos_rows = (await db.execute(vencidos_sql, {"uid": user_id})).mappings().all()

    # Esta semana
    semana_sql = text("""
        SELECT oc.id, oc.description, ipr.codigo_bip AS ipr_codigo_bip,
               p.names || ' ' || p.paternal_surname AS responsible_name,
               oc.due_date, sc.code AS state, (oc.due_date - CURRENT_DATE) AS days_remaining
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        LEFT JOIN core.ipr ipr ON ipr.id = oc.ipr_id AND ipr.deleted_at IS NULL
        LEFT JOIN core."user" u ON u.id = oc.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE oc.responsible_id = :uid AND oc.deleted_at IS NULL
          AND sc.code NOT IN ('VERIFICADO','CANCELADO')
          AND oc.due_date >= CURRENT_DATE AND oc.due_date <= CURRENT_DATE + INTERVAL '7 days'
        ORDER BY oc.due_date ASC LIMIT 20
    """)
    semana_rows = (await db.execute(semana_sql, {"uid": user_id})).mappings().all()

    # Pendientes (no vencidos, no esta semana)
    pendientes_sql = text("""
        SELECT oc.id, oc.description, ipr.codigo_bip AS ipr_codigo_bip,
               p.names || ' ' || p.paternal_surname AS responsible_name,
               oc.due_date, sc.code AS state, (oc.due_date - CURRENT_DATE) AS days_remaining
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        LEFT JOIN core.ipr ipr ON ipr.id = oc.ipr_id AND ipr.deleted_at IS NULL
        LEFT JOIN core."user" u ON u.id = oc.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE oc.responsible_id = :uid AND oc.deleted_at IS NULL
          AND sc.code IN ('PENDIENTE', 'EN_PROGRESO')
          AND oc.due_date > CURRENT_DATE + INTERVAL '7 days'
        ORDER BY oc.due_date ASC LIMIT 20
    """)
    pendientes_rows = (await db.execute(pendientes_sql, {"uid": user_id})).mappings().all()

    groups = [
        CompromisoGroup(
            label="Vencidos",
            count=len(vencidos_rows),
            items=[DashboardCommitment(**dict(r)) for r in vencidos_rows],
        ),
        CompromisoGroup(
            label="Esta Semana",
            count=len(semana_rows),
            items=[DashboardCommitment(**dict(r)) for r in semana_rows],
        ),
        CompromisoGroup(
            label="Pendientes",
            count=len(pendientes_rows),
            items=[DashboardCommitment(**dict(r)) for r in pendientes_rows],
        ),
    ]

    return MisCompromisosResponse(kpis=kpis, groups=groups)


# ---------------------------------------------------------------------------
# GET /api/dashboard/ejecutivo — Enhanced executive dashboard
# ---------------------------------------------------------------------------

@router.get("/ejecutivo", response_model=DashboardExecutivoResponse)
async def get_dashboard_ejecutivo(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    # Base dashboard data
    base = await _dashboard_admin_regional(user, db)

    # Division breakdown
    div_sql = text("""
        SELECT
            o.name AS division_name,
            COALESCE(SUM(CASE WHEN sc.code NOT IN ('VERIFICADO','CANCELADO') AND oc.due_date < CURRENT_DATE THEN 1 ELSE 0 END), 0) AS vencidos,
            COALESCE(COUNT(oc.id), 0) AS total_compromisos,
            COALESCE((
                SELECT COUNT(*)
                FROM core.ipr_problem ip
                JOIN ref.category ps ON ps.id = ip.state_id
                JOIN core.ipr i ON i.id = ip.ipr_id
                WHERE ps.code IN ('ABIERTO', 'EN_GESTION')
                  AND i.sponsor_division_id = o.id
                  AND i.deleted_at IS NULL AND ip.deleted_at IS NULL
            ), 0) AS problemas_abiertos,
            COALESCE((
                SELECT ROUND(SUM(bp.paid_amount)::numeric / NULLIF(SUM(bp.current_amount), 0)::numeric * 100, 1)
                FROM core.budget_program bp
                WHERE bp.owner_division_id = o.id
                  AND bp.fiscal_year = EXTRACT(YEAR FROM CURRENT_DATE)
                  AND bp.deleted_at IS NULL
            ), 0) AS ejecucion_pct
        FROM core.organization o
        JOIN ref.category ot ON ot.id = o.org_type_id
        LEFT JOIN core.operational_commitment oc ON oc.division_id = o.id AND oc.deleted_at IS NULL
        LEFT JOIN ref.category sc ON sc.id = oc.state_id
        WHERE o.deleted_at IS NULL
          AND ot.code IN ('DIVISION', 'GORE')
        GROUP BY o.id, o.name
        HAVING COUNT(oc.id) > 0
        ORDER BY o.name
    """)
    div_rows = (await db.execute(div_sql)).mappings().all()
    divisions = [DivisionBreakdown(**dict(r)) for r in div_rows]

    # ── Semaforo DGI ───────────────────────────────────────────────────────
    ind_sql = text("""
        SELECT
            dim.code   AS dimension,
            sig.code   AS signal
        FROM core.dgi_indicator i
        JOIN ref.category dim ON dim.id = i.dimension_id
        LEFT JOIN ref.category sig ON sig.id = i.signal_id
        WHERE i.deleted_at IS NULL
        ORDER BY dim.code
    """)
    ind_rows = (await db.execute(ind_sql)).mappings().all()

    dim_signals: dict[str, list[str | None]] = {}
    for r in ind_rows:
        dim_signals.setdefault(r["dimension"], []).append(r["signal"])

    semaforo = []
    for dim_code in ["PRESUPUESTO", "CARTERA_IPR", "CONVENIOS", "TDE", "RIESGOS"]:
        signals = dim_signals.get(dim_code, [])
        semaforo.append(
            SemaforoItem(
                dimension=dim_code,
                label=_DIMENSION_LABELS.get(dim_code, dim_code),
                signal=_worst_signal(signals) if signals else "VERDE",
                indicator_count=len(signals),
            )
        )

    return DashboardExecutivoResponse(
        kpis=base.kpis,
        commitments=base.commitments,
        alerts=base.alerts,
        problems=base.problems,
        divisions=divisions,
        semaforo=semaforo,
    )


# ---------------------------------------------------------------------------
# Chart data endpoint
# ---------------------------------------------------------------------------
@router.get("/chart-data", response_model=ChartDataResponse)
async def get_chart_data(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Datos para charts del dashboard: compromisos por estado, alertas por severidad,
    ejecución presupuestaria por división."""

    # ── Compromisos por estado ──────────────────────────────────────────────
    comm_sql = text("""
        SELECT sc.code AS state, COUNT(*) AS cnt
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        WHERE oc.deleted_at IS NULL
        GROUP BY sc.code
    """)
    comm_rows = (await db.execute(comm_sql)).mappings().all()

    STATE_COLORS = {
        "PENDIENTE": "#f59e0b",
        "EN_PROGRESO": "#3b82f6",
        "COMPLETADO": "#10b981",
        "VERIFICADO": "#6366f1",
        "CANCELADO": "#9ca3af",
        "VENCIDO": "#ef4444",
    }
    commitments_by_state = [
        ChartDataPoint(
            name=r["state"],
            value=r["cnt"],
            color=STATE_COLORS.get(r["state"], "#9ca3af"),
        )
        for r in comm_rows
    ]

    # ── Alertas por severidad ───────────────────────────────────────────────
    alert_sql = text("""
        SELECT COALESCE(sev.code, 'SIN_CLASIFICAR') AS severity, COUNT(*) AS cnt
        FROM core.alert a
        LEFT JOIN ref.category sev ON sev.id = a.severity_id
        WHERE a.deleted_at IS NULL
          AND a.resolved_at IS NULL
        GROUP BY sev.code
    """)
    alert_rows = (await db.execute(alert_sql)).mappings().all()

    SEVERITY_COLORS = {
        "CRITICO": "#ef4444",
        "ALTO": "#f97316",
        "ATENCION": "#f59e0b",
        "INFO": "#3b82f6",
    }
    alerts_by_severity = [
        ChartDataPoint(
            name=r["severity"],
            value=r["cnt"],
            color=SEVERITY_COLORS.get(r["severity"], "#9ca3af"),
        )
        for r in alert_rows
    ]

    # ── Presupuesto por división ────────────────────────────────────────────
    budget_sql = text("""
        SELECT
            COALESCE(o.short_name, o.name, 'Sin nombre') AS division,
            COALESCE(SUM(bp.paid_amount), 0)    AS pagado,
            COALESCE(SUM(bp.current_amount), 0) AS vigente,
            CASE
                WHEN COALESCE(SUM(bp.current_amount), 0) = 0 THEN 0
                ELSE ROUND(
                    SUM(bp.paid_amount)::numeric
                    / SUM(bp.current_amount)::numeric * 100, 1
                )
            END AS ejecucion_pct
        FROM core.organization o
        JOIN core.budget_program bp ON bp.owner_division_id = o.id
        WHERE bp.fiscal_year = EXTRACT(YEAR FROM CURRENT_DATE)
          AND bp.deleted_at IS NULL
          AND o.deleted_at IS NULL
        GROUP BY o.id, o.short_name, o.name
        ORDER BY ejecucion_pct DESC
        LIMIT 10
    """)
    budget_rows = (await db.execute(budget_sql)).mappings().all()

    budget_by_division = [
        BudgetChartPoint(
            division=r["division"],
            ejecucion_pct=float(r["ejecucion_pct"]),
            pagado=float(r["pagado"]),
            vigente=float(r["vigente"]),
        )
        for r in budget_rows
    ]

    return ChartDataResponse(
        commitments_by_state=commitments_by_state,
        alerts_by_severity=alerts_by_severity,
        budget_by_division=budget_by_division,
    )


# ---------------------------------------------------------------------------
# GET /api/dashboard/action-items — 6-source coproduct with role scoping
# ---------------------------------------------------------------------------
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
        summary = "Todo al día"

    # Greeting
    nombre = user.get("nombre", "") or ""
    first_name = nombre.split()[0] if nombre.strip() else "Usuario"

    return ActionItemsResponse(
        greeting_name=first_name,
        today=date.today(),
        summary=summary,
        items=all_items,
        counts=counts,
    )


# ---------------------------------------------------------------------------
# Pending V.B. for Asesor Jurídico
# ---------------------------------------------------------------------------
def _require_roles(user: dict, *roles: str) -> None:
    if user["role_code"] not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sin permisos suficientes",
        )


@router.get("/pending-vb")
async def get_pending_vb(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Pending Visto Bueno items for Asesor Jurídico."""
    _require_roles(user, "ASESOR_JURIDICO", "ADMIN_SISTEMA")

    # Actos administrativos en revisión legal
    actos_sql = text("""
        SELECT
            aa.id::text AS id,
            aa.act_number,
            aa.subject,
            'acto' AS item_type,
            st.code AS state,
            st.label AS state_label,
            aa.ipr_id::text AS ipr_id,
            ipr.codigo_bip AS ipr_codigo_bip,
            aa.created_at
        FROM core.administrative_act aa
        JOIN ref.category st ON st.id = aa.state_id
        LEFT JOIN core.ipr ipr ON ipr.id = aa.ipr_id
        WHERE st.code = 'EN_REVISION'
            AND aa.deleted_at IS NULL
        ORDER BY aa.created_at ASC
        LIMIT 20
    """)
    actos = (await db.execute(actos_sql)).mappings().all()

    # Convenios en revisión jurídica
    convenios_sql = text("""
        SELECT
            ag.id::text AS id,
            ag.agreement_number AS act_number,
            COALESCE(ag.agreement_number, 'Convenio sin número') AS subject,
            'convenio' AS item_type,
            st.code AS state,
            st.label AS state_label,
            ag.ipr_id::text AS ipr_id,
            ipr.codigo_bip AS ipr_codigo_bip,
            ag.created_at
        FROM core.agreement ag
        JOIN ref.category st ON st.id = ag.state_id
        LEFT JOIN core.ipr ipr ON ipr.id = ag.ipr_id
        WHERE st.code = 'EN_REVISION_JURIDICA'
            AND ag.deleted_at IS NULL
        ORDER BY ag.created_at ASC
        LIMIT 20
    """)
    convenios = (await db.execute(convenios_sql)).mappings().all()

    items = []
    for r in [*actos, *convenios]:
        items.append({
            "id": r["id"],
            "act_number": r["act_number"],
            "subject": r["subject"],
            "item_type": r["item_type"],
            "state": r["state"],
            "state_label": r["state_label"],
            "ipr_id": r["ipr_id"],
            "ipr_codigo_bip": r["ipr_codigo_bip"],
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
        })

    return {"items": items, "total": len(items)}
