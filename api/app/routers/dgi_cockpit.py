from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from datetime import date, timedelta

from app.schemas.dgi import (
    CockpitJefeDGI,
    CockpitControlGestion,
    CockpitProcesos,
    CockpitTD,
    DimensionSummary,
    RenditionSummary,
    IndicatorItem,
    InitiativeItem,
    BPMNModelItem,
    DataSourceItem,
    CommitteeSessionItem,
    DecreeItem,
    NormativeAlertItem,
    VelocityStats,
    KBStats,
    AgendaItem,
    PortfolioStats,
)

router = APIRouter(prefix="/api/dgi/cockpit", tags=["dgi"])

# ---------------------------------------------------------------------------
# Signal priority helper: ROJO > AMARILLO > VERDE
# ---------------------------------------------------------------------------
_SIGNAL_PRIORITY = {"ROJO": 3, "AMARILLO": 2, "VERDE": 1}

# Named constant: target number of active DGI initiatives (portfolio goal)
_DGI_PORTFOLIO_TARGET = 5

# Ley 21.180 compliance start date (for velocity computation)
_LEY_21180_START = date(2024, 1, 1)
_LEY_21180_DEADLINE = date(2027, 12, 31)

DIMENSION_LABELS = {
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


# ---------------------------------------------------------------------------
# JEFE_DGI cockpit
# ---------------------------------------------------------------------------
async def _cockpit_jefe_dgi(user: dict, db: AsyncSession) -> CockpitJefeDGI:

    # ── Semaforo: all indicators grouped by dimension ─────────────────────
    ind_sql = text("""
        SELECT
            dim.code   AS dimension,
            sig.code   AS signal
        FROM core.dgi_indicator i
        JOIN ref.category dim ON dim.id = i.dimension_id
        LEFT JOIN ref.category sig ON sig.id = i.signal_id
        ORDER BY dim.code
    """)
    ind_rows = (await db.execute(ind_sql)).mappings().all()

    # Group signals by dimension
    dim_signals: dict[str, list[str | None]] = {}
    for r in ind_rows:
        dim_signals.setdefault(r["dimension"], []).append(r["signal"])

    # Build semaforo for the 5 canonical dimensions
    semaforo = []
    for dim_code in ["PRESUPUESTO", "CARTERA_IPR", "CONVENIOS", "TDE", "RIESGOS"]:
        signals = dim_signals.get(dim_code, [])
        semaforo.append(
            DimensionSummary(
                dimension=dim_code,
                label=DIMENSION_LABELS.get(dim_code, dim_code),
                signal=_worst_signal(signals) if signals else "VERDE",
                indicator_count=len(signals),
            )
        )

    # ── Decisions pending: critical unresolved alerts without action taken ─
    decisions_sql = text("""
        SELECT COUNT(*) AS total
        FROM core.alert a
        JOIN ref.category sev ON sev.id = a.severity_id
        WHERE sev.code = 'CRITICO'
          AND a.resolved_at IS NULL
          AND a.action_taken IS NULL
          AND a.deleted_at IS NULL
    """)
    decisions_row = (await db.execute(decisions_sql)).mappings().first()
    decisions_pending = decisions_row["total"] if decisions_row else 0

    # ── Decision items: top 5 actionable items across sources ─────────────
    decision_items_sql = text("""
        (
            SELECT 'alert' AS source, a.id::text AS id, a.message AS title,
                   sev.code AS severity
            FROM core.alert a
            JOIN ref.category sev ON sev.id = a.severity_id
            WHERE sev.code IN ('CRITICO', 'ALTO')
              AND a.resolved_at IS NULL
              AND a.action_taken IS NULL
              AND a.deleted_at IS NULL
            ORDER BY a.created_at DESC
            LIMIT 3
        )
        UNION ALL
        (
            SELECT 'rendition' AS source, r.id::text AS id,
                   'Rendición ' || LEFT(r.id::text, 8) || ' — ' || COALESCE(org.name, 'Sin ejecutor') AS title,
                   CASE WHEN EXTRACT(EPOCH FROM NOW() - COALESCE(r.phase_entered_at, r.updated_at)) / 86400 > 7 THEN 'VENCIDA' ELSE 'PENDIENTE' END AS severity
            FROM core.rendition r
            LEFT JOIN core.organization org ON org.id = r.renderer_id
            JOIN ref.category st ON st.id = r.state_id
            WHERE st.code IN ('PENDIENTE', 'EN_REVISION_RTF')
              AND r.deleted_at IS NULL
            ORDER BY r.created_at ASC
            LIMIT 2
        )
    """)
    decision_rows = (await db.execute(decision_items_sql)).mappings().all()
    decision_items = [
        {"source": r["source"], "id": str(r["id"]), "title": r["title"], "severity": r["severity"]}
        for r in decision_rows
    ]

    # ── Team status: DGI specialists (hardcoded roles, dynamic users) ─────
    team_sql = text("""
        SELECT
            u.id,
            p.names || ' ' || p.paternal_surname AS full_name,
            c.code AS role_code,
            c.label AS role_label
        FROM core."user" u
        JOIN ref.category c ON u.system_role_id = c.id
        JOIN core.person p ON u.person_id = p.id
        WHERE c.code IN ('ESP_CONTROL_GESTION', 'ESP_TD', 'ESP_PROCESOS')
          AND u.is_active = TRUE
          AND u.deleted_at IS NULL
        ORDER BY c.code
    """)
    team_rows = (await db.execute(team_sql)).mappings().all()

    # Real activity: count active initiatives + last report per user
    team_status = []
    for r in team_rows:
        uid = str(r["id"])
        # Count active initiatives assigned to this user
        ini_row = (await db.execute(text("""
            SELECT COUNT(*) AS cnt
            FROM core.dgi_initiative i
            JOIN ref.category st ON st.id = i.status_id
            WHERE i.responsible_id = :uid AND st.code IN ('EN_CURSO', 'REVISION')
        """), {"uid": uid})).mappings().first()
        ini_count = ini_row["cnt"] if ini_row else 0

        # Last report edited by this user
        rep_row = (await db.execute(text("""
            SELECT r.title, r.updated_at
            FROM core.dgi_report r
            WHERE r.generated_by_id = :uid AND r.deleted_at IS NULL
            ORDER BY r.updated_at DESC LIMIT 1
        """), {"uid": uid})).mappings().first()

        if ini_count > 0 and rep_row:
            activity = f"{ini_count} iniciativa(s) activa(s) · Último informe: {rep_row['title']}"
        elif ini_count > 0:
            activity = f"{ini_count} iniciativa(s) activa(s)"
        elif rep_row:
            activity = f"Último informe: {rep_row['title']}"
        else:
            activity = "Sin actividad reciente"

        team_status.append({
            "id": uid,
            "name": r["full_name"],
            "role": r["role_label"],
            "activity": activity,
        })

    # ── Critical alerts: top 3 CRITICO ────────────────────────────────────
    alerts_sql = text("""
        SELECT
            a.id,
            sev.code    AS severity,
            a.message,
            a.subject_type,
            a.triggered_at
        FROM core.alert a
        JOIN ref.category sev ON sev.id = a.severity_id
        WHERE sev.code = 'CRITICO'
          AND a.resolved_at IS NULL
          AND a.deleted_at IS NULL
        ORDER BY a.triggered_at DESC
        LIMIT 3
    """)
    alert_rows = (await db.execute(alerts_sql)).mappings().all()
    critical_alerts = [
        {
            "id": str(r["id"]),
            "severity": r["severity"],
            "message": r["message"],
            "subject_type": r["subject_type"],
            "triggered_at": r["triggered_at"].isoformat() if r["triggered_at"] else None,
        }
        for r in alert_rows
    ]

    # ── Report status: current week's BORRADOR report ─────────────────────
    report_sql = text("""
        SELECT
            r.id,
            r.code,
            r.title,
            st.code AS status,
            rt.code AS report_type,
            r.period_start,
            r.period_end
        FROM core.dgi_report r
        JOIN ref.category st ON st.id = r.status_id
        JOIN ref.category rt ON rt.id = r.report_type_id
        WHERE st.code = 'BORRADOR'
          AND r.period_start >= date_trunc('week', CURRENT_DATE)
        ORDER BY r.created_at DESC
        LIMIT 1
    """)
    report_row = (await db.execute(report_sql)).mappings().first()
    report_status = None
    if report_row:
        report_status = {
            "title": report_row["title"],
            "status": report_row["status"],
            "due": report_row["period_end"].isoformat() if report_row["period_end"] else None,
        }

    # ── Rendition summary: count by state + amount at risk ────────────────
    rend_rows = (await db.execute(text("""
        SELECT st.code, st.label, COUNT(*) AS cnt
        FROM core.rendition r
        JOIN ref.category st ON st.id = r.state_id
        WHERE r.deleted_at IS NULL AND st.scheme = 'rendition_state'
        GROUP BY st.code, st.label, st.sort_order
        ORDER BY st.sort_order
    """))).mappings().all()

    risk_row = (await db.execute(text("""
        SELECT COALESCE(SUM(DISTINCT a.total_amount), 0) AS total_risk
        FROM core.rendition r
        JOIN ref.category st ON st.id = r.state_id
        LEFT JOIN core.agreement a ON a.id = r.agreement_id
        WHERE r.deleted_at IS NULL AND st.code NOT IN ('APROBADA', 'RECHAZADA')
    """))).mappings().first()

    rendition_summary = RenditionSummary(
        total=sum(r["cnt"] for r in rend_rows),
        by_state=[{"code": r["code"], "label": r["label"], "count": r["cnt"]} for r in rend_rows],
        amount_at_risk=float(risk_row["total_risk"]) if risk_row and float(risk_row["total_risk"]) > 0 else None,
    )

    return CockpitJefeDGI(
        semaforo=semaforo,
        decisions_pending=int(decisions_pending),
        decision_items=decision_items,
        team_status=team_status,
        critical_alerts=critical_alerts,
        report_status=report_status,
        rendition_summary=rendition_summary,
    )


# ---------------------------------------------------------------------------
# ESP_CONTROL_GESTION cockpit
# ---------------------------------------------------------------------------
async def _cockpit_control_gestion(user: dict, db: AsyncSession) -> CockpitControlGestion:

    # ── Data sources ──────────────────────────────────────────────────────
    sources_sql = text("""
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
        ORDER BY ds.days_behind DESC, org.name
    """)
    source_rows = (await db.execute(sources_sql)).mappings().all()
    data_sources = [
        DataSourceItem(
            id=r["id"],
            division_name=r["division_name"],
            source_name=r["source_name"],
            status=r["status"],
            last_data_at=r["last_data_at"],
            days_behind=r["days_behind"] or 0,
        )
        for r in source_rows
    ]

    # ── Indicators in alert: ROJO or AMARILLO ─────────────────────────────
    alert_ind_sql = text("""
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
        JOIN ref.category sig ON sig.id = i.signal_id
        WHERE sig.code IN ('ROJO', 'AMARILLO')
        ORDER BY
            CASE sig.code WHEN 'ROJO' THEN 1 WHEN 'AMARILLO' THEN 2 ELSE 3 END,
            i.name
    """)
    alert_ind_rows = (await db.execute(alert_ind_sql)).mappings().all()
    indicators_alert = [
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
        for r in alert_ind_rows
    ]

    # ── Trends: all indicators ────────────────────────────────────────────
    trends_sql = text("""
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
        ORDER BY dim.code, i.name
    """)
    trends_rows = (await db.execute(trends_sql)).mappings().all()
    trends = [
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
        for r in trends_rows
    ]

    # ── Work queue: derivado de fuentes atrasadas + indicadores en alerta ──
    _today = date.today()
    _days_to_friday = (4 - _today.weekday()) % 7
    _next_friday = _today + timedelta(days=_days_to_friday) if _days_to_friday > 0 else _today
    _end_of_week = _today + timedelta(days=6 - _today.weekday())

    work_queue = []

    # Fuentes de datos atrasadas → tarea ALTA
    overdue_sources = [s for s in data_sources if s.status in ("ATRASADO", "SIN_DATOS")]
    if overdue_sources:
        names = ", ".join(s.source_name for s in overdue_sources[:3])
        work_queue.append({
            "priority": "ALTA",
            "task": f"Validar {len(overdue_sources)} fuente(s) con datos atrasados: {names}",
            "status": "Pendiente",
            "deadline": f"Hoy ({_today.strftime('%d/%m')})",
        })

    # Indicadores ROJO → tarea ALTA
    rojo_inds = [i for i in indicators_alert if i.signal == "ROJO"]
    if rojo_inds:
        names_ind = ", ".join(i.name for i in rojo_inds[:3])
        work_queue.append({
            "priority": "ALTA",
            "task": f"Investigar {len(rojo_inds)} indicador(es) en ROJO: {names_ind}",
            "status": "Pendiente",
            "deadline": f"Hoy ({_today.strftime('%d/%m')})",
        })

    # Indicadores AMARILLO → tarea MEDIA
    amarillo_inds = [i for i in indicators_alert if i.signal == "AMARILLO"]
    if amarillo_inds:
        work_queue.append({
            "priority": "MEDIA",
            "task": f"Monitorear {len(amarillo_inds)} indicador(es) en AMARILLO",
            "status": "En seguimiento",
            "deadline": f"Semana ({_end_of_week.strftime('%d/%m')})",
        })

    # Informe semanal pendiente → tarea MEDIA
    report_check_sql = text("""
        SELECT COUNT(*) AS pending
        FROM core.dgi_report r
        JOIN ref.category st ON st.id = r.status_id
        JOIN ref.category rt ON rt.id = r.report_type_id
        WHERE st.code = 'BORRADOR' AND rt.code = 'SEMANAL'
    """)
    report_check = (await db.execute(report_check_sql)).scalar() or 0
    if report_check == 0:
        work_queue.append({
            "priority": "MEDIA",
            "task": "Generar borrador Informe Semanal",
            "status": "Pendiente",
            "deadline": f"Vie {_next_friday.strftime('%d/%m')}",
        })

    # Si no hay nada urgente, agregar tarea base
    if not work_queue:
        work_queue.append({
            "priority": "BAJA",
            "task": "Revisar tablero de indicadores y preparar reporte diario",
            "status": "Pendiente",
            "deadline": f"Hoy 17:00",
        })

    return CockpitControlGestion(
        data_sources=data_sources,
        indicators_alert=indicators_alert,
        trends=trends,
        work_queue=work_queue,
    )


# ---------------------------------------------------------------------------
# ESP_PROCESOS cockpit
# ---------------------------------------------------------------------------
async def _cockpit_procesos(user: dict, db: AsyncSession) -> CockpitProcesos:

    # ── Initiatives: EN_CURSO first ───────────────────────────────────────
    init_sql = text("""
        SELECT
            ini.id,
            ini.code,
            ini.name,
            ini.description,
            ini.responsible_id,
            p.names || ' ' || p.paternal_surname AS responsible_name,
            st.code         AS status,
            ph.code         AS dmaic_phase,
            org.name        AS division_name,
            ini.start_date,
            ini.target_date,
            ini.current_day,
            ini.total_days,
            ini.progress,
            ini.wip_column
        FROM core.dgi_initiative ini
        JOIN ref.category st ON st.id = ini.status_id
        LEFT JOIN ref.category ph ON ph.id = ini.dmaic_phase_id
        LEFT JOIN core.organization org ON org.id = ini.division_id
        LEFT JOIN core."user" u ON u.id = ini.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        ORDER BY
            CASE st.code
                WHEN 'EN_CURSO' THEN 1
                WHEN 'REVISION' THEN 2
                WHEN 'BACKLOG'  THEN 3
                WHEN 'COMPLETADO' THEN 4
                ELSE 5
            END,
            ini.target_date ASC NULLS LAST
    """)
    init_rows = (await db.execute(init_sql)).mappings().all()
    initiatives = [
        InitiativeItem(
            id=r["id"],
            code=r["code"],
            name=r["name"],
            description=r["description"],
            responsible_id=r["responsible_id"],
            responsible_name=r["responsible_name"],
            status=r["status"],
            dmaic_phase=r["dmaic_phase"],
            division_name=r["division_name"],
            start_date=r["start_date"],
            target_date=r["target_date"],
            current_day=r["current_day"] or 0,
            total_days=r["total_days"],
            progress=r["progress"] or 0.0,
            wip_column=r["wip_column"],
        )
        for r in init_rows
    ]

    # ── BPMN models ───────────────────────────────────────────────────────
    bpmn_sql = text("""
        SELECT
            b.id,
            b.code,
            b.process_name,
            b.version,
            st.code         AS status,
            b.description
        FROM core.dgi_bpmn_model b
        JOIN ref.category st ON st.id = b.status_id
        ORDER BY b.process_name
    """)
    bpmn_rows = (await db.execute(bpmn_sql)).mappings().all()
    bpmn_models = [
        BPMNModelItem(
            id=r["id"],
            code=r["code"],
            process_name=r["process_name"],
            version=r["version"],
            status=r["status"],
            description=r["description"],
        )
        for r in bpmn_rows
    ]

    # ── Today agenda: derived from DB + recurring items ──────────────────
    today_agenda: list[AgendaItem] = [
        AgendaItem(time="09:00", activity="Stand-up DGI (15 min)", process="Gestión DGI"),
    ]

    # Committee sessions scheduled for today
    sessions_sql = text("""
        SELECT cs.session_date
        FROM core.dgi_committee_session cs
        JOIN ref.category st ON st.id = cs.status_id
        WHERE DATE(cs.session_date) = CURRENT_DATE AND st.code != 'CANCELADA'
        ORDER BY cs.session_date
    """)
    session_rows = (await db.execute(sessions_sql)).mappings().all()
    for s in session_rows:
        t = s["session_date"].strftime("%H:%M") if s["session_date"] else "10:00"
        today_agenda.append(AgendaItem(time=t, activity="Sesión Comité DGI", process="Gestión DGI"))

    # BPMN models in REVISION → suggest review task
    bpmn_review_count = (await db.execute(text("""
        SELECT COUNT(*) FROM core.dgi_bpmn_model b
        JOIN ref.category st ON st.id = b.status_id
        WHERE st.code = 'REVISION'
    """))).scalar() or 0
    if bpmn_review_count > 0:
        today_agenda.append(AgendaItem(
            time="12:00",
            activity=f"Revisión {bpmn_review_count} modelo(s) BPMN en revisión",
            process="Modelamiento",
        ))

    # Recurring: update Kanban board
    today_agenda.append(AgendaItem(time="16:30", activity="Actualizar tablero Kanban iniciativas", process="Portfolio DGI"))

    # ── Portfolio stats ───────────────────────────────────────────────────
    stats_sql = text("""
        SELECT
            SUM(CASE WHEN st.code IN ('EN_CURSO', 'REVISION') THEN 1 ELSE 0 END) AS active,
            SUM(CASE WHEN st.code = 'COMPLETADO'               THEN 1 ELSE 0 END) AS completed
        FROM core.dgi_initiative ini
        JOIN ref.category st ON st.id = ini.status_id
    """)
    stats_row = (await db.execute(stats_sql)).mappings().first()
    portfolio_stats = PortfolioStats(
        active=int(stats_row["active"] or 0),
        completed=int(stats_row["completed"] or 0),
        target=_DGI_PORTFOLIO_TARGET,
    )

    return CockpitProcesos(
        initiatives=initiatives,
        bpmn_models=bpmn_models,
        today_agenda=today_agenda,
        portfolio_stats=portfolio_stats,
    )


# ---------------------------------------------------------------------------
# ESP_TD cockpit
# ---------------------------------------------------------------------------
async def _cockpit_td(user: dict, db: AsyncSession) -> CockpitTD:

    # ── Compliance bars: indicators in TDE dimension ──────────────────────
    tde_sql = text("""
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
        WHERE dim.code = 'TDE'
        ORDER BY i.name
    """)
    tde_rows = (await db.execute(tde_sql)).mappings().all()
    compliance_bars = [
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
        for r in tde_rows
    ]

    # ── Velocity: derived from TDE indicators + Ley 21.180 deadline ──────
    today = date.today()
    months_elapsed = max((today.year - _LEY_21180_START.year) * 12 + today.month - _LEY_21180_START.month, 1)
    months_remaining = max((_LEY_21180_DEADLINE.year - today.year) * 12 + _LEY_21180_DEADLINE.month - today.month, 1)

    avg_current = 0.0
    avg_target = 100.0
    if compliance_bars:
        vals = [b.current_value for b in compliance_bars if b.current_value is not None]
        tgts = [b.target_value for b in compliance_bars if b.target_value is not None]
        avg_current = sum(vals) / len(vals) if vals else 0.0
        avg_target = sum(tgts) / len(tgts) if tgts else 100.0

    current_rate = round(avg_current / months_elapsed, 1)
    required_rate = round(max(avg_target - avg_current, 0) / months_remaining, 1)

    velocity = VelocityStats(
        current=current_rate,
        required=required_rate,
        months_remaining=months_remaining,
    )

    # ── Decrees checklist (DS7–DS12): from core.dgi_decree ────────────────
    decree_sql = text("""
        SELECT d.id, d.code, d.name, d.description, st.code AS status, d.deadline
        FROM core.dgi_decree d
        JOIN ref.category st ON st.id = d.status_id
        WHERE d.deleted_at IS NULL
        ORDER BY d.code
    """)
    decree_rows = (await db.execute(decree_sql)).mappings().all()
    decrees = [
        DecreeItem(
            id=r["id"],
            code=r["code"],
            name=r["name"],
            description=r["description"],
            status=r["status"],
            deadline=r["deadline"],
            days_until=(r["deadline"] - today).days if r["deadline"] else None,
        )
        for r in decree_rows
    ]

    # ── KB stats: placeholder (module pending implementation) ─────────────
    kb_stats = KBStats(
        module_status="pending",
        message="Módulo pendiente de implementación",
    )

    # ── Committee: next upcoming session ──────────────────────────────────
    committee_sql = text("""
        SELECT
            cs.id,
            cs.session_date,
            st.code         AS status,
            cs.agenda,
            cs.agreements,
            cs.notes
        FROM core.dgi_committee_session cs
        JOIN ref.category st ON st.id = cs.status_id
        WHERE cs.session_date >= NOW()
          AND st.code != 'CANCELADA'
        ORDER BY cs.session_date ASC
        LIMIT 1
    """)
    committee_row = (await db.execute(committee_sql)).mappings().first()
    committee = None
    if committee_row:
        committee = CommitteeSessionItem(
            id=committee_row["id"],
            session_date=committee_row["session_date"],
            status=committee_row["status"],
            agenda=committee_row["agenda"] if committee_row["agenda"] else [],
            agreements=committee_row["agreements"] if committee_row["agreements"] else [],
            notes=committee_row["notes"],
        )

    # ── Normative alerts: derived from non-VIGENTE decrees with deadline ──
    normative_alerts = []
    for d in decrees:
        if d.status == "VIGENTE" or d.days_until is None:
            continue
        if d.days_until < 0:
            msg = f"{d.code} {d.name} venció hace {abs(d.days_until)} día(s)"
        else:
            msg = f"{d.code} {d.name} vence en {d.days_until} día(s)"
        normative_alerts.append(NormativeAlertItem(
            message=msg, days_until=d.days_until, decree_code=d.code,
        ))
    normative_alerts.sort(key=lambda a: a.days_until)

    return CockpitTD(
        compliance_bars=compliance_bars,
        velocity=velocity,
        decrees=decrees,
        kb_stats=kb_stats,
        committee=committee,
        normative_alerts=normative_alerts,
    )


# ---------------------------------------------------------------------------
# Main endpoint: GET /api/dgi/cockpit
# ---------------------------------------------------------------------------
@router.get("")
async def get_cockpit(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Role-specific DGI cockpit.

    Returns a cockpit tailored to the authenticated user's role:
    - JEFE_DGI: semaforo, decisions_pending, team_status, critical_alerts, report_status
    - ESP_CONTROL_GESTION: data_sources, indicators_alert, trends, work_queue
    - ESP_PROCESOS: initiatives, bpmn_models, today_agenda, portfolio_stats
    - ESP_TD: compliance_bars, velocity, decrees, kb_stats, committee, normative_alerts
    """
    role = user["role_code"]

    if role == "JEFE_DGI":
        return await _cockpit_jefe_dgi(user, db)

    if role == "ESP_CONTROL_GESTION":
        return await _cockpit_control_gestion(user, db)

    if role == "ESP_PROCESOS":
        return await _cockpit_procesos(user, db)

    if role == "ESP_TD":
        return await _cockpit_td(user, db)

    # Fallback for other DGI-adjacent roles: return Jefe DGI view
    return await _cockpit_jefe_dgi(user, db)
