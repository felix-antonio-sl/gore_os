from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.schemas.dashboard import (
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
    ChartDataPoint,
    BudgetChartPoint,
    ChartDataResponse,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

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
# ENCARGADO dashboard
# ---------------------------------------------------------------------------
async def _dashboard_encargado(user: dict, db: AsyncSession) -> DashboardResponse:
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
    - ENCARGADO: personal commitments and alerts on their assigned IPRs
    - JEFE_DIVISION: division-scoped commitments and problems
    - ADMIN_REGIONAL / ADMIN_SISTEMA / JEFE_DGI / ESP_*: global overview
    """
    role_code = user["role_code"]

    if role_code == "ENCARGADO":
        return await _dashboard_encargado(user, db)

    if role_code == "JEFE_DIVISION":
        return await _dashboard_jefe_division(user, db)

    if role_code in (
        "ADMIN_REGIONAL",
        "ADMIN_SISTEMA",
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
# GET /api/dashboard/mis-compromisos — Personal commitments for ENCARGADO
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
        LEFT JOIN core.operational_commitment oc ON oc.division_id = o.id AND oc.deleted_at IS NULL
        LEFT JOIN ref.category sc ON sc.id = oc.state_id
        WHERE o.deleted_at IS NULL
        GROUP BY o.id, o.name
        HAVING COUNT(oc.id) > 0
        ORDER BY o.name
    """)
    div_rows = (await db.execute(div_sql)).mappings().all()
    divisions = [DivisionBreakdown(**dict(r)) for r in div_rows]

    return DashboardExecutivoResponse(
        kpis=base.kpis,
        commitments=base.commitments,
        alerts=base.alerts,
        problems=base.problems,
        divisions=divisions,
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
            o.short_name AS division,
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
        GROUP BY o.id, o.short_name
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
