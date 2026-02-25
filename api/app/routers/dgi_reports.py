import json
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.schemas.dgi import ReportItem, ReportContent, ReportContentSection, ReportCreate, ReportSectionUpdate

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


# ---------------------------------------------------------------------------
# Helpers: auto-población de secciones desde datos reales
# ---------------------------------------------------------------------------

async def _section_resumen(db: AsyncSession) -> str:
    """Resumen ejecutivo: semáforo + KPIs top-level."""
    # Semáforo desde indicadores
    ind_rows = (await db.execute(text("""
        SELECT dim.code AS dimension, sig.code AS signal, COUNT(*) AS cnt
        FROM core.dgi_indicator i
        JOIN ref.category dim ON dim.id = i.dimension_id
        LEFT JOIN ref.category sig ON sig.id = i.signal_id
        GROUP BY dim.code, sig.code
        ORDER BY dim.code
    """))).mappings().all()

    semaforo_lines = []
    dim_signals: dict[str, list[str]] = {}
    for r in ind_rows:
        dim_signals.setdefault(r["dimension"], []).append(r["signal"] or "VERDE")

    signal_priority = {"ROJO": 3, "AMARILLO": 2, "VERDE": 1}
    for dim in ["PRESUPUESTO", "CARTERA_IPR", "CONVENIOS", "TDE", "RIESGOS"]:
        signals = dim_signals.get(dim, ["VERDE"])
        worst = max(signals, key=lambda s: signal_priority.get(s, 0))
        semaforo_lines.append(f"  {dim}: {worst}")

    # KPIs rápidos
    kpi_row = (await db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM core.ipr WHERE deleted_at IS NULL) AS total_ipr,
            (SELECT ROUND(SUM(paid_amount)::numeric / NULLIF(SUM(current_amount), 0)::numeric * 100, 1)
             FROM core.budget_program WHERE fiscal_year = EXTRACT(YEAR FROM CURRENT_DATE) AND deleted_at IS NULL) AS ejec_ppto,
            (SELECT COUNT(*) FROM core.alert WHERE resolved_at IS NULL AND deleted_at IS NULL) AS alertas_activas,
            (SELECT COUNT(*) FROM core.operational_commitment oc
             JOIN ref.category sc ON sc.id = oc.state_id
             WHERE sc.code NOT IN ('VERIFICADO','CANCELADO') AND oc.due_date < CURRENT_DATE AND oc.deleted_at IS NULL) AS compromisos_vencidos
    """))).mappings().first()

    lines = [
        "SEMÁFORO INSTITUCIONAL:",
        *semaforo_lines,
        "",
        "INDICADORES CLAVE:",
        f"  Cartera IPR: {kpi_row['total_ipr']} proyectos activos",
        f"  Ejecución presupuestaria: {kpi_row['ejec_ppto'] or 0}% del año vigente",
        f"  Alertas activas: {kpi_row['alertas_activas']}",
        f"  Compromisos vencidos: {kpi_row['compromisos_vencidos']}",
    ]
    return "\n".join(lines)


async def _section_tabla_indicadores(db: AsyncSession) -> str:
    """Tabla de indicadores con valor/meta/señal."""
    rows = (await db.execute(text("""
        SELECT dim.code AS dimension, i.name, i.current_value, i.target_value, i.unit,
               sig.code AS signal, i.trend
        FROM core.dgi_indicator i
        JOIN ref.category dim ON dim.id = i.dimension_id
        LEFT JOIN ref.category sig ON sig.id = i.signal_id
        ORDER BY dim.code, i.name
    """))).mappings().all()

    lines = ["INDICADOR | ACTUAL | META | SEÑAL | TENDENCIA"]
    lines.append("-" * 65)
    for r in rows:
        actual = f"{r['current_value']}{r['unit']}" if r['current_value'] is not None else "-"
        meta = f"{r['target_value']}{r['unit']}" if r['target_value'] is not None else "-"
        trend_icon = {"up": "↑", "down": "↓", "flat": "→"}.get(r["trend"] or "", "-")
        lines.append(f"[{r['dimension']}] {r['name']}: {actual} / {meta} | {r['signal'] or '-'} {trend_icon}")
    return "\n".join(lines)


async def _section_alertas(db: AsyncSession) -> str:
    """Alertas activas agrupadas por severidad."""
    rows = (await db.execute(text("""
        SELECT sev.code AS severity, sev.label AS severity_label,
               COUNT(*) AS cnt,
               array_agg(a.message ORDER BY a.triggered_at DESC) FILTER (WHERE sev.code = 'CRITICO') AS critico_msgs
        FROM core.alert a
        JOIN ref.category sev ON sev.id = a.severity_id
        WHERE a.resolved_at IS NULL AND a.deleted_at IS NULL
        GROUP BY sev.code, sev.label
        ORDER BY CASE sev.code WHEN 'CRITICO' THEN 1 WHEN 'ALTO' THEN 2 WHEN 'ATENCION' THEN 3 ELSE 4 END
    """))).mappings().all()

    lines = ["ALERTAS ACTIVAS POR SEVERIDAD:"]
    for r in rows:
        lines.append(f"  {r['severity']}: {r['cnt']} alertas")
        if r["critico_msgs"]:
            for msg in (r["critico_msgs"] or [])[:3]:
                lines.append(f"    → {msg}")
    if not rows:
        lines.append("  Sin alertas activas.")
    return "\n".join(lines)


async def _section_avance_dgi(db: AsyncSession) -> str:
    """Estado de iniciativas DGI."""
    rows = (await db.execute(text("""
        SELECT st.code AS status, COUNT(*) AS cnt,
               array_agg(ini.name ORDER BY ini.progress DESC) AS names
        FROM core.dgi_initiative ini
        JOIN ref.category st ON st.id = ini.status_id
        GROUP BY st.code
        ORDER BY CASE st.code WHEN 'EN_CURSO' THEN 1 WHEN 'REVISION' THEN 2 WHEN 'COMPLETADO' THEN 3 ELSE 4 END
    """))).mappings().all()

    lines = ["INICIATIVAS DGI:"]
    for r in rows:
        lines.append(f"  {r['status']}: {r['cnt']} iniciativa(s)")
        for name in (r["names"] or [])[:3]:
            lines.append(f"    • {name}")
    if not rows:
        lines.append("  Sin iniciativas registradas.")
    return "\n".join(lines)


async def _section_decisiones(db: AsyncSession) -> str:
    """Alertas CRITICO sin acción tomada — requieren decisión del AR."""
    rows = (await db.execute(text("""
        SELECT a.id, a.message, a.triggered_at, a.subject_type
        FROM core.alert a
        JOIN ref.category sev ON sev.id = a.severity_id
        WHERE sev.code = 'CRITICO'
          AND a.action_taken IS NULL
          AND a.resolved_at IS NULL
          AND a.deleted_at IS NULL
        ORDER BY a.triggered_at ASC
        LIMIT 10
    """))).mappings().all()

    lines = ["DECISIONES REQUERIDAS POR ADMIN REGIONAL:"]
    if rows:
        for r in rows:
            lines.append(f"  ❗ {r['message']} (desde {r['triggered_at'].strftime('%d-%b')})")
    else:
        lines.append("  Sin decisiones críticas pendientes.")
    return "\n".join(lines)


async def _section_prioridades(db: AsyncSession) -> str:
    """Prioridades para la próxima semana."""
    # Compromisos vencidos
    comp_rows = (await db.execute(text("""
        SELECT oc.description, org.name AS division, (CURRENT_DATE - oc.due_date) AS dias_vencido
        FROM core.operational_commitment oc
        JOIN ref.category sc ON sc.id = oc.state_id
        LEFT JOIN core.organization org ON org.id = oc.division_id
        WHERE sc.code NOT IN ('VERIFICADO', 'CANCELADO') AND oc.due_date < CURRENT_DATE AND oc.deleted_at IS NULL
        ORDER BY dias_vencido DESC
        LIMIT 5
    """))).mappings().all()

    # Convenios por vencer en 30 días
    conv_rows = (await db.execute(text("""
        SELECT a.agreement_number, org.name AS receiver, EXTRACT(DAY FROM a.valid_to - NOW())::int AS dias
        FROM core.agreement a
        JOIN ref.category st ON st.id = a.state_id
        LEFT JOIN core.organization org ON org.id = a.receiver_id
        WHERE st.code = 'VIGENTE' AND a.valid_to < NOW() + INTERVAL '30 days' AND a.deleted_at IS NULL
        ORDER BY a.valid_to ASC
        LIMIT 5
    """))).mappings().all()

    lines = ["PRIORIDADES PRÓXIMA SEMANA:"]
    if comp_rows:
        lines.append(f"\nCompromisos vencidos ({len(comp_rows)}):")
        for r in comp_rows:
            lines.append(f"  • {r['description']} — {r['division'] or 'Sin división'} ({r['dias_vencido']}d vencido)")
    if conv_rows:
        lines.append(f"\nConvenios por vencer ({len(conv_rows)}):")
        for r in conv_rows:
            lines.append(f"  • {r['agreement_number']} — {r['receiver'] or 'Sin receptor'} (en {r['dias']}d)")
    if not comp_rows and not conv_rows:
        lines.append("  Sin elementos prioritarios identificados.")
    return "\n".join(lines)


SECTION_GENERATORS = {
    "resumen":            ("Resumen ejecutivo",         _section_resumen),
    "tabla_indicadores":  ("Tabla indicadores",         _section_tabla_indicadores),
    "alertas":            ("Alertas activas",            _section_alertas),
    "avance_dgi":         ("Avance iniciativas DGI",    _section_avance_dgi),
    "decisiones":         ("Decisiones requeridas AR",  _section_decisiones),
    "prioridades":        ("Prioridades próxima semana", _section_prioridades),
}


# ---------------------------------------------------------------------------
# POST /api/dgi/reports — Crear nuevo informe
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_report(
    body: ReportCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(text("""
        INSERT INTO core.dgi_report (
            report_type_id, status_id, title, period_start, period_end, recipient,
            generated_by_id, created_at, updated_at
        ) VALUES (
            (SELECT id FROM ref.category WHERE scheme = 'dgi_report_type' AND code = :report_type LIMIT 1),
            (SELECT id FROM ref.category WHERE scheme = 'dgi_report_status' AND code = 'BORRADOR' LIMIT 1),
            :title, :period_start, :period_end, :recipient,
            :generated_by_id, NOW(), NOW()
        )
        RETURNING id
    """), {
        "report_type": body.report_type.upper(),
        "title": body.title,
        "period_start": body.period_start,
        "period_end": body.period_end,
        "recipient": body.recipient,
        "generated_by_id": str(user["id"]),
    })
    await db.commit()
    row = result.mappings().first()
    return {"id": row["id"]}


# ---------------------------------------------------------------------------
# GET /api/dgi/reports/{id}/content — Secciones auto-pobladas
# ---------------------------------------------------------------------------

@router.get("/{report_id}/content", response_model=ReportContent)
async def get_report_content(
    report_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    # Fetch report header
    row = (await db.execute(text("""
        SELECT r.id, r.code, r.title, rt.code AS report_type, st.code AS status,
               r.period_start, r.period_end, r.metadata
        FROM core.dgi_report r
        JOIN ref.category rt ON rt.id = r.report_type_id
        JOIN ref.category st ON st.id = r.status_id
        WHERE r.id = :id AND r.deleted_at IS NULL
    """), {"id": str(report_id)})).mappings().first()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Informe no encontrado")

    # Load any user edits stored in metadata
    metadata = row["metadata"] or {}
    user_edits: dict = metadata.get("section_edits", {}) if isinstance(metadata, dict) else {}

    # Generate all sections
    sections = []
    for section_id, (title, generator_fn) in SECTION_GENERATORS.items():
        if section_id in user_edits:
            # User has edited this section
            edit = user_edits[section_id]
            sections.append(ReportContentSection(
                section_id=section_id,
                title=title,
                content=edit["content"],
                auto_populated=False,
                last_edited_at=edit.get("edited_at"),
            ))
        else:
            # Auto-generate content from real data
            content = await generator_fn(db)
            sections.append(ReportContentSection(
                section_id=section_id,
                title=title,
                content=content,
                auto_populated=True,
                last_edited_at=None,
            ))

    return ReportContent(
        id=row["id"],
        code=row["code"],
        title=row["title"],
        report_type=row["report_type"],
        status=row["status"],
        period_start=row["period_start"],
        period_end=row["period_end"],
        sections=sections,
    )


# ---------------------------------------------------------------------------
# PATCH /api/dgi/reports/{id} — Editar sección (persistida en metadata JSONB)
# ---------------------------------------------------------------------------

@router.patch("/{report_id}")
async def update_report_section(
    report_id: UUID,
    body: ReportSectionUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    # Verify report exists
    row = (await db.execute(text(
        "SELECT id FROM core.dgi_report WHERE id = :id AND deleted_at IS NULL"
    ), {"id": str(report_id)})).mappings().first()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Informe no encontrado")

    from datetime import datetime, timezone
    edit_value = json.dumps({
        "content": body.content,
        "edited_at": datetime.now(timezone.utc).isoformat(),
        "edited_by": str(user["id"]),
    })

    # Atomic JSONB merge: no read-modify-write, prevents lost updates under concurrency
    await db.execute(text("""
        UPDATE core.dgi_report
        SET metadata = jsonb_set(
                jsonb_set(
                    COALESCE(metadata, '{}'),
                    '{section_edits}',
                    COALESCE(metadata->'section_edits', '{}')
                ),
                ARRAY['section_edits', :section_id],
                CAST(:edit_value AS jsonb)
            ),
            updated_at = NOW()
        WHERE id = :id
    """), {"section_id": body.section_id, "edit_value": edit_value, "id": str(report_id)})
    await db.commit()
    return {"message": "Sección actualizada"}


# ---------------------------------------------------------------------------
# GET /api/dgi/reports/{id}/export — JSON estructurado para render/PDF
# ---------------------------------------------------------------------------

@router.get("/{report_id}/export")
async def export_report(
    report_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna el informe completo con todas las secciones auto-pobladas
    en formato JSON estructurado. El frontend puede renderizarlo como
    HTML/PDF (funcionalidad de PDF diferida a Ciclo 3).
    """
    row = (await db.execute(text("""
        SELECT r.id, r.code, r.title, rt.code AS report_type, st.code AS status,
               r.period_start, r.period_end, r.recipient, r.metadata,
               p.names || ' ' || p.paternal_surname AS author
        FROM core.dgi_report r
        JOIN ref.category rt ON rt.id = r.report_type_id
        JOIN ref.category st ON st.id = r.status_id
        LEFT JOIN core."user" u ON u.id = r.generated_by_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE r.id = :id AND r.deleted_at IS NULL
    """), {"id": str(report_id)})).mappings().first()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Informe no encontrado")

    metadata = row["metadata"] or {}
    user_edits: dict = metadata.get("section_edits", {}) if isinstance(metadata, dict) else {}

    sections_export = []
    for section_id, (title, generator_fn) in SECTION_GENERATORS.items():
        if section_id in user_edits:
            content = user_edits[section_id]["content"]
            auto_populated = False
        else:
            content = await generator_fn(db)
            auto_populated = True
        sections_export.append({"section_id": section_id, "title": title, "content": content, "auto_populated": auto_populated})

    return {
        "id": str(row["id"]),
        "code": row["code"],
        "title": row["title"],
        "report_type": row["report_type"],
        "status": row["status"],
        "period_start": row["period_start"].isoformat() if row["period_start"] else None,
        "period_end": row["period_end"].isoformat() if row["period_end"] else None,
        "recipient": row["recipient"],
        "author": row["author"],
        "exported_at": date.today().isoformat(),
        "sections": sections_export,
    }
