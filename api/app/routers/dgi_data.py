from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
import math
from datetime import datetime, timezone
from app.schemas.dgi import RendicionItem, RendicionDetail, RendicionCreate, RendicionUpdate, RendicionHistoryEntry, RenditionPhaseDefinition, EscalationItem, EscalationCheckResult, CicloPhaseStatus
from app.core.security import DGI_ROLES, WRITE_OPERATIONAL_ROLES
from app.core.audit import record_event

_RENDICION_WRITE_ROLES = WRITE_OPERATIONAL_ROLES | DGI_ROLES

router = APIRouter(prefix="/api/dgi/data", tags=["dgi"])


@router.get("/rendiciones")
async def list_rendiciones(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    state: str | None = None,
    search: str | None = None,
    ipr_id: str | None = None,
):
    conditions = ["r.deleted_at IS NULL"]
    params: dict = {}

    if ipr_id:
        conditions.append("r.ipr_id = CAST(:ipr_id AS uuid)")
        params["ipr_id"] = ipr_id

    if state:
        conditions.append("st.code = :state")
        params["state"] = state

    if search:
        conditions.append(
            "(a.agreement_number ILIKE :search OR org.name ILIKE :search OR ipr.codigo_bip ILIKE :search)"
        )
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core.rendition r
        LEFT JOIN core.agreement a ON a.id = r.agreement_id
        LEFT JOIN core.ipr ipr ON ipr.id = r.ipr_id
        LEFT JOIN core.organization org ON org.id = r.renderer_id
        LEFT JOIN core."user" ru ON ru.id = r.responsible_id
        LEFT JOIN core.person rp ON rp.id = ru.person_id
        LEFT JOIN ref.category st ON st.id = r.state_id
        WHERE {where_clause}
    """

    total = (await db.execute(text(f"SELECT COUNT(*) {base_query}"), params)).scalar() or 0
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(text(f"""
        SELECT r.id, r.period_start, r.period_end, r.submitted_at, r.amount,
               a.agreement_number, a.total_amount AS agreement_total_amount,
               ipr.codigo_bip AS ipr_codigo_bip, r.ipr_id,
               org.name AS renderer_name,
               (rp.names || ' ' || rp.paternal_surname) AS responsible_name,
               st.code AS state_code, st.label AS state_label,
               EXTRACT(EPOCH FROM (NOW() - COALESCE(r.phase_entered_at, r.updated_at))) / 86400.0 AS days_in_state
        {base_query}
        ORDER BY r.submitted_at DESC NULLS LAST
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    items = [RendicionItem(
        id=r["id"], agreement_number=r["agreement_number"],
        ipr_codigo_bip=r["ipr_codigo_bip"], ipr_id=r["ipr_id"],
        renderer_name=r["renderer_name"], responsible_name=r["responsible_name"],
        state_code=r["state_code"], state_label=r["state_label"],
        period_start=r["period_start"], period_end=r["period_end"],
        submitted_at=r["submitted_at"],
        agreement_total_amount=float(r["agreement_total_amount"]) if r["agreement_total_amount"] else None,
        amount=float(r["amount"]) if r["amount"] else None,
        days_in_state=round(float(r["days_in_state"]), 1) if r["days_in_state"] else None,
        is_overdue=(
            r["state_code"] in _RENDICION_SLA_DAYS
            and r["days_in_state"] is not None
            and float(r["days_in_state"]) > _RENDICION_SLA_DAYS[r["state_code"]]
        ),
    ) for r in rows]

    return {
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }

@router.get("/rendiciones/resumen")
async def get_rendiciones_resumen(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Aggregate rendition statistics for KPI strip and reporting."""
    result = await db.execute(
        text("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE st.code NOT IN ('APROBADA', 'RECHAZADA')) AS active,
                COUNT(*) FILTER (WHERE st.code = 'APROBADA') AS aprobadas,
                COUNT(*) FILTER (WHERE st.code = 'RECHAZADA') AS rechazadas,
                COUNT(*) FILTER (WHERE st.code = 'OBSERVADA') AS observadas,
                COUNT(*) FILTER (WHERE st.code = 'EN_REVISION_RTF') AS en_revision_rtf,
                COUNT(*) FILTER (WHERE st.code = 'EN_REVISION_UCR') AS en_revision_ucr,
                COUNT(*) FILTER (
                    WHERE st.code NOT IN ('APROBADA', 'RECHAZADA')
                    AND EXTRACT(EPOCH FROM (NOW() - COALESCE(r.phase_entered_at, r.updated_at))) / 86400.0 > rp.sla_days
                ) AS sla_breached,
                SUM(r.amount) FILTER (WHERE st.code = 'APROBADA') AS total_approved_amount
            FROM core.rendition r
            JOIN ref.category st ON st.id = r.state_id
            LEFT JOIN core.rendition_phase rp ON rp.code = st.code
            WHERE r.deleted_at IS NULL
        """)
    )
    row = result.mappings().first()

    by_state = await db.execute(
        text("""
            SELECT st.code, st.label, COUNT(*) AS count
            FROM core.rendition r
            JOIN ref.category st ON st.id = r.state_id
            WHERE r.deleted_at IS NULL
            GROUP BY st.code, st.label
            ORDER BY count DESC
        """)
    )
    by_state_list = [dict(r) for r in by_state.mappings().all()]

    # SLA compliance rate
    total_active = row["active"] or 0
    sla_breached = row["sla_breached"] or 0
    sla_compliance_pct = round((total_active - sla_breached) * 100.0 / total_active, 1) if total_active > 0 else 100.0

    return {
        "total": row["total"],
        "active": total_active,
        "aprobadas": row["aprobadas"],
        "rechazadas": row["rechazadas"],
        "observadas": row["observadas"],
        "en_revision_rtf": row["en_revision_rtf"],
        "en_revision_ucr": row["en_revision_ucr"],
        "sla_breached": sla_breached,
        "sla_compliance_pct": sla_compliance_pct,
        "total_approved_amount": row["total_approved_amount"],
        "by_state": by_state_list,
    }

@router.get("/rendiciones/fases")
async def list_rendition_phases(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all 8 CGR rendition phase definitions (TP-06 parametric table)."""
    rows = (await db.execute(
        text("""
            SELECT id, ordinal, code, name, responsible_role,
                   sla_days, escalation_action, is_internal
            FROM core.rendition_phase
            ORDER BY ordinal
        """)
    )).mappings().all()
    return [RenditionPhaseDefinition(**dict(r)) for r in rows]

@router.post("/rendiciones/check-escalations")
async def check_escalations(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Detect overdue renditions and create escalation + alert entries."""
    if user["role_code"] not in _RENDICION_WRITE_ROLES:
        raise HTTPException(status_code=403, detail="Rol sin permiso")

    rows = (await db.execute(
        text("""
            SELECT r.id, st.code AS state_code,
                   EXTRACT(EPOCH FROM (NOW() - COALESCE(r.phase_entered_at, r.updated_at))) / 86400.0 AS days_in_state,
                   a.agreement_number, ipr.codigo_bip
            FROM core.rendition r
            LEFT JOIN ref.category st ON st.id = r.state_id
            LEFT JOIN core.agreement a ON a.id = r.agreement_id
            LEFT JOIN core.ipr ipr ON ipr.id = r.ipr_id
            WHERE r.deleted_at IS NULL
              AND st.code IN ('EN_REVISION_RTF', 'VISADA_RTF', 'EN_REVISION_UCR')
        """)
    )).mappings().all()

    phase_rows = (await db.execute(
        text("SELECT id, code, sla_days FROM core.rendition_phase")
    )).mappings().all()
    phase_map = {p["code"]: {"id": str(p["id"]), "sla_days": p["sla_days"]} for p in phase_rows}

    severity_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_level' AND code = 'ALTO'")
    )).scalar()

    alert_type_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_type' AND code = 'PLAZO_LEGAL'")
    )).scalar()
    if not alert_type_id:
        alert_type_id = (await db.execute(
            text("SELECT id FROM ref.category WHERE scheme = 'alert_type' LIMIT 1")
        )).scalar()

    checked = 0
    new_escalations = 0
    details = []

    for r in rows:
        checked += 1
        phase_code = _STATE_TO_PHASE_CODE.get(r["state_code"])
        if not phase_code or phase_code not in phase_map:
            continue

        phase_info = phase_map[phase_code]
        sla = phase_info["sla_days"]
        days = float(r["days_in_state"])

        for level, multiplier in _ESCALATION_MULTIPLIERS.items():
            threshold = sla * multiplier
            if days <= threshold:
                continue

            escalation_id = (await db.execute(
                text("""
                    INSERT INTO core.rendition_escalation (
                        rendition_id, phase_id, escalation_level
                    ) VALUES (:rid, :pid, :level)
                    ON CONFLICT (rendition_id, phase_id, escalation_level)
                        WHERE resolved_at IS NULL
                    DO NOTHING
                    RETURNING id
                """),
                {"rid": str(r["id"]), "pid": phase_info["id"], "level": level},
            )).scalar()

            if escalation_id is None:
                continue

            if severity_id and alert_type_id:
                alert_row = (await db.execute(
                    text("""
                        INSERT INTO core.alert (
                            alert_type_id, severity_id, subject_type, subject_id,
                            message
                        ) VALUES (
                            :type_id, :sev, 'core.rendition', :sid,
                            :message
                        ) RETURNING id
                    """),
                    {
                        "type_id": str(alert_type_id),
                        "sev": str(severity_id),
                        "sid": str(r["id"]),
                        "message": f"Escalamiento N{level}: rendición "
                                   f"{r.get('agreement_number') or str(r['id'])[:8]} "
                                   f"lleva {round(days, 1)}d en {r['state_code']} "
                                   f"(SLA: {sla}d, umbral N{level}: {threshold}d)",
                    },
                )).mappings().first()
                if alert_row:
                    await db.execute(
                        text("""
                            UPDATE core.rendition_escalation
                            SET alert_id = :alert_id
                            WHERE id = :escalation_id
                        """),
                        {
                            "alert_id": str(alert_row["id"]),
                            "escalation_id": str(escalation_id),
                        },
                    )
            new_escalations += 1
            details.append({
                "rendition_id": str(r["id"]),
                "phase_code": phase_code,
                "level": level,
                "days_in_state": round(days, 1),
                "threshold": threshold,
            })

    await db.commit()
    return EscalationCheckResult(checked=checked, new_escalations=new_escalations, details=details)

@router.get("/rendiciones/vencidas")
async def list_rendiciones_vencidas(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
):
    """Rendiciones that have exceeded their SLA time in a reviewable state."""
    # Build CASE expression for SLA thresholds (uses phase_entered_at for accuracy)
    sla_conditions = " OR ".join(
        f"(st.code = '{code}' AND EXTRACT(EPOCH FROM (NOW() - COALESCE(r.phase_entered_at, r.updated_at))) / 86400.0 > {days})"
        for code, days in _RENDICION_SLA_DAYS.items()
    )

    base_query = f"""
        FROM core.rendition r
        LEFT JOIN core.agreement a ON a.id = r.agreement_id
        LEFT JOIN core.ipr ipr ON ipr.id = r.ipr_id
        LEFT JOIN core.organization org ON org.id = r.renderer_id
        LEFT JOIN core."user" ru ON ru.id = r.responsible_id
        LEFT JOIN core.person rp ON rp.id = ru.person_id
        LEFT JOIN ref.category st ON st.id = r.state_id
        WHERE r.deleted_at IS NULL AND ({sla_conditions})
    """

    params: dict = {}
    total = (await db.execute(text(f"SELECT COUNT(*) {base_query}"), params)).scalar() or 0
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(text(f"""
        SELECT r.id, r.period_start, r.period_end, r.submitted_at, r.amount,
               a.agreement_number, a.total_amount AS agreement_total_amount,
               ipr.codigo_bip AS ipr_codigo_bip, r.ipr_id,
               org.name AS renderer_name,
               (rp.names || ' ' || rp.paternal_surname) AS responsible_name,
               st.code AS state_code, st.label AS state_label,
               EXTRACT(EPOCH FROM (NOW() - COALESCE(r.phase_entered_at, r.updated_at))) / 86400.0 AS days_in_state
        {base_query}
        ORDER BY days_in_state DESC
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    items = [RendicionItem(
        id=r["id"], agreement_number=r["agreement_number"],
        ipr_codigo_bip=r["ipr_codigo_bip"], ipr_id=r["ipr_id"],
        renderer_name=r["renderer_name"], responsible_name=r["responsible_name"],
        state_code=r["state_code"], state_label=r["state_label"],
        period_start=r["period_start"], period_end=r["period_end"],
        submitted_at=r["submitted_at"],
        agreement_total_amount=float(r["agreement_total_amount"]) if r["agreement_total_amount"] else None,
        amount=float(r["amount"]) if r["amount"] else None,
        days_in_state=round(float(r["days_in_state"]), 1) if r["days_in_state"] else None,
        is_overdue=True,
    ) for r in rows]

    return {
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }

@router.get("/rendiciones/{rendicion_id}/ciclo")
async def get_rendicion_ciclo(
    rendicion_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db),
):
    """Enhanced phase-by-phase cycle view with TP-06 phase definitions.

    Maps state history to 8 CGR phases. Internal phases (4-7) derive from
    rendition_history. External phases (1-3) from metadata timestamps.
    Phase 8 from archived_at.
    """
    row = (await db.execute(
        text("""
            SELECT r.id, r.created_at, r.archived_at, r.metadata,
                   st.code AS state_code
            FROM core.rendition r
            LEFT JOIN ref.category st ON st.id = r.state_id
            WHERE r.id = :id AND r.deleted_at IS NULL
        """),
        {"id": str(rendicion_id)},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Rendición no encontrada")

    phase_defs = (await db.execute(
        text("SELECT id, ordinal, code, name, responsible_role, sla_days FROM core.rendition_phase ORDER BY ordinal")
    )).mappings().all()
    phase_by_code = {p["code"]: dict(p) for p in phase_defs}

    history_rows = (await db.execute(
        text("""
            SELECT h.changed_at,
                   new_cat.code  AS new_state,
                   new_cat.label AS new_state_label
            FROM core.rendition_history h
            JOIN ref.category new_cat ON h.new_state_id = new_cat.id
            WHERE h.rendition_id = :rid
            ORDER BY h.changed_at ASC
        """),
        {"rid": str(rendicion_id)},
    )).mappings().all()

    now = datetime.now(timezone.utc)
    metadata = row["metadata"] or {}
    current_state = row["state_code"]

    state_to_phase = {
        "PENDIENTE": "RECEPCION_GORE",
        "EN_REVISION_RTF": "REVISION_RTF",
        "VISADA_RTF": "APROBACION_DAF",
        "EN_REVISION_UCR": "CONTABILIZACION_UCR",
    }

    phases: list[dict] = []

    # --- External phases (1-3): from metadata timestamps ---
    external_keys = [
        ("PREPARACION_EJECUTOR", "fase1_preparacion_at"),
        ("CERTIFICACION", "fase2_certificacion_at"),
        ("FIRMA_ENCARGADO", "fase3_firma_at"),
    ]
    for phase_code, meta_key in external_keys:
        pdef = phase_by_code.get(phase_code, {})
        ts_str = metadata.get(meta_key)
        if ts_str:
            entered = datetime.fromisoformat(ts_str) if isinstance(ts_str, str) else ts_str
            phases.append(CicloPhaseStatus(
                ordinal=pdef.get("ordinal", 0), code=phase_code, name=pdef.get("name", ""),
                responsible_role=pdef.get("responsible_role", ""), sla_days=pdef.get("sla_days", 0),
                status="completada", entered_at=entered, duration_days=None, is_overdue=False,
            ).model_dump())
        else:
            phases.append(CicloPhaseStatus(
                ordinal=pdef.get("ordinal", 0), code=phase_code, name=pdef.get("name", ""),
                responsible_role=pdef.get("responsible_role", ""), sla_days=pdef.get("sla_days", 0),
                status="no_aplica",
            ).model_dump())

    # --- Internal phases (4-7): from state history ---
    state_entries: list[dict] = []
    if history_rows:
        first_ts = history_rows[0]["changed_at"]
        state_entries.append({
            "state": "PENDIENTE", "entered": row["created_at"], "exited": first_ts,
        })
        for i, h in enumerate(history_rows):
            exited = history_rows[i + 1]["changed_at"] if i + 1 < len(history_rows) else None
            state_entries.append({
                "state": h["new_state"], "entered": h["changed_at"], "exited": exited,
            })
    else:
        state_entries.append({
            "state": "PENDIENTE", "entered": row["created_at"], "exited": None,
        })

    internal_phase_codes = ["RECEPCION_GORE", "REVISION_RTF", "APROBACION_DAF", "CONTABILIZACION_UCR"]
    for phase_code in internal_phase_codes:
        pdef = phase_by_code.get(phase_code, {})
        matching_states = [s for s in state_entries if state_to_phase.get(s["state"]) == phase_code]

        if matching_states:
            entered = matching_states[0]["entered"]
            last = matching_states[-1]
            exited = last["exited"]
            if exited:
                dur = (exited - entered).total_seconds() / 86400.0
                p_status = "completada"
            else:
                dur = (now - entered).total_seconds() / 86400.0
                p_status = "en_curso"
            sla = pdef.get("sla_days", 0)
            phases.append(CicloPhaseStatus(
                ordinal=pdef.get("ordinal", 0), code=phase_code, name=pdef.get("name", ""),
                responsible_role=pdef.get("responsible_role", ""), sla_days=sla,
                status=p_status, entered_at=entered, exited_at=exited,
                duration_days=round(dur, 1),
                is_overdue=sla > 0 and dur > sla,
            ).model_dump())
        else:
            current_phase_code = state_to_phase.get(current_state)
            current_ordinal = phase_by_code.get(current_phase_code, {}).get("ordinal", 0) if current_phase_code else 99
            phase_ordinal = pdef.get("ordinal", 0)
            if current_state in ("APROBADA", "RECHAZADA"):
                p_status = "completada" if phase_ordinal <= 7 else "pendiente"
            elif current_ordinal > phase_ordinal:
                p_status = "completada"
            else:
                p_status = "pendiente"
            phases.append(CicloPhaseStatus(
                ordinal=pdef.get("ordinal", 0), code=phase_code, name=pdef.get("name", ""),
                responsible_role=pdef.get("responsible_role", ""), sla_days=pdef.get("sla_days", 0),
                status=p_status,
            ).model_dump())

    # --- Phase 8 (ARCHIVO_CIERRE): from archived_at ---
    pdef8 = phase_by_code.get("ARCHIVO_CIERRE", {})
    if row["archived_at"]:
        phases.append(CicloPhaseStatus(
            ordinal=8, code="ARCHIVO_CIERRE", name=pdef8.get("name", "Archivo y Cierre"),
            responsible_role=pdef8.get("responsible_role", "ARCHIVO"), sla_days=pdef8.get("sla_days", 1),
            status="completada", entered_at=row["archived_at"],
        ).model_dump())
    elif current_state == "APROBADA":
        phases.append(CicloPhaseStatus(
            ordinal=8, code="ARCHIVO_CIERRE", name=pdef8.get("name", "Archivo y Cierre"),
            responsible_role=pdef8.get("responsible_role", "ARCHIVO"), sla_days=pdef8.get("sla_days", 1),
            status="en_curso",
        ).model_dump())
    else:
        phases.append(CicloPhaseStatus(
            ordinal=8, code="ARCHIVO_CIERRE", name=pdef8.get("name", "Archivo y Cierre"),
            responsible_role=pdef8.get("responsible_role", "ARCHIVO"), sla_days=pdef8.get("sla_days", 1),
            status="pendiente",
        ).model_dump())

    phases.sort(key=lambda p: p["ordinal"])

    total_elapsed = (now - row["created_at"]).total_seconds() / 86400.0
    overdue_count = sum(1 for p in phases if p.get("is_overdue"))

    return {
        "rendicion_id": rendicion_id,
        "current_state": current_state,
        "total_elapsed_days": round(total_elapsed, 1),
        "cycle_target_days": _RENDICION_CYCLE_TARGET_DAYS,
        "cycle_overdue": total_elapsed > _RENDICION_CYCLE_TARGET_DAYS,
        "archived_at": row["archived_at"],
        "phases": phases,
        "overdue_count": overdue_count,
    }

@router.get("/rendiciones/{rendicion_id}", response_model=RendicionDetail)
async def get_rendicion(rendicion_id: UUID, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    row = (await db.execute(
        text("""
            SELECT r.id, r.agreement_id, r.ipr_id, r.renderer_id, r.responsible_id,
                   r.period_start, r.period_end, r.submitted_at, r.amount,
                   r.phase_entered_at, r.metadata, r.created_at,
                   a.agreement_number, a.total_amount AS agreement_total_amount,
                   ipr.codigo_bip AS ipr_codigo_bip,
                   org.name AS renderer_name,
                   (rp.names || ' ' || rp.paternal_surname) AS responsible_name,
                   st.code AS state_code, st.label AS state_label,
                   COALESCE(st.valid_transitions, '[]'::jsonb) AS valid_transitions,
                   EXTRACT(EPOCH FROM (NOW() - COALESCE(r.phase_entered_at, r.updated_at))) / 86400.0 AS days_in_state,
                   EXTRACT(EPOCH FROM (NOW() - r.created_at)) / 86400.0 AS total_cycle_days
            FROM core.rendition r
            LEFT JOIN core.agreement a ON a.id = r.agreement_id
            LEFT JOIN core.ipr ipr ON ipr.id = r.ipr_id
            LEFT JOIN core.organization org ON org.id = r.renderer_id
            LEFT JOIN core."user" ru ON ru.id = r.responsible_id
            LEFT JOIN core.person rp ON rp.id = ru.person_id
            LEFT JOIN ref.category st ON st.id = r.state_id
            WHERE r.id = :id AND r.deleted_at IS NULL
        """),
        {"id": str(rendicion_id)},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Rendición no encontrada")
    history = await _get_rendition_history(rendicion_id, db)
    destinations = (await db.execute(text("""
        SELECT id, code, label FROM ref.category
        WHERE scheme = 'rendition_state' AND code = ANY(:codes)
        ORDER BY label
    """), {"codes": list(row["valid_transitions"])})).mappings().all()
    allowed_transitions = [dict(destination) for destination in destinations
        if user["role_code"] in _RENDICION_TRANSITION_ROLES.get(
            (row["state_code"], destination["code"]), _RENDICION_WRITE_ROLES
        )]
    total_cycle = round(float(row["total_cycle_days"]), 1) if row["total_cycle_days"] else None
    return RendicionDetail(
        id=row["id"], agreement_id=row["agreement_id"], ipr_id=row["ipr_id"],
        renderer_id=row["renderer_id"], responsible_id=row["responsible_id"],
        agreement_number=row["agreement_number"],
        ipr_codigo_bip=row["ipr_codigo_bip"], renderer_name=row["renderer_name"],
        responsible_name=row["responsible_name"],
        state_code=row["state_code"], state_label=row["state_label"],
        period_start=row["period_start"], period_end=row["period_end"],
        submitted_at=row["submitted_at"],
        agreement_total_amount=float(row["agreement_total_amount"]) if row["agreement_total_amount"] else None,
        amount=float(row["amount"]) if row["amount"] else None,
        days_in_state=round(float(row["days_in_state"]), 1) if row["days_in_state"] else None,
        is_overdue=(
            row["state_code"] in _RENDICION_SLA_DAYS
            and row["days_in_state"] is not None
            and float(row["days_in_state"]) > _RENDICION_SLA_DAYS[row["state_code"]]
        ),
        sla_days=_RENDICION_SLA_DAYS.get(row["state_code"]),
        phase_entered_at=row["phase_entered_at"],
        total_cycle_days=total_cycle,
        cycle_overdue=total_cycle is not None and total_cycle > _RENDICION_CYCLE_TARGET_DAYS,
        metadata=dict(row["metadata"]) if row["metadata"] else None,
        created_at=row["created_at"],
        history=[RendicionHistoryEntry(**h) for h in history],
        allowed_transitions=allowed_transitions,
    )

@router.patch("/rendiciones/{rendicion_id}/archivar")
async def archive_rendicion(
    rendicion_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Set archived_at on an APROBADA rendition (phase 8 closure)."""
    if user["role_code"] not in _RENDICION_WRITE_ROLES:
        raise HTTPException(status_code=403, detail="Rol sin permiso para archivar")

    row = (await db.execute(
        text("""
            SELECT r.id, r.archived_at, st.code AS state_code
            FROM core.rendition r
            LEFT JOIN ref.category st ON st.id = r.state_id
            WHERE r.id = :id AND r.deleted_at IS NULL
        """),
        {"id": str(rendicion_id)},
    )).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Rendición no encontrada")
    if row["state_code"] != "APROBADA":
        raise HTTPException(status_code=409, detail="Solo rendiciones APROBADA pueden archivarse")
    if row["archived_at"]:
        raise HTTPException(status_code=409, detail="Rendición ya archivada")

    await db.execute(
        text("UPDATE core.rendition SET archived_at = NOW() WHERE id = :id"),
        {"id": str(rendicion_id)},
    )
    await record_event(db, "STATE_TRANSITION", "core.rendition", rendicion_id, user["id"], {
        "from": "APROBADA",
        "to": "ARCHIVADA",
    })
    await db.commit()
    return {"archived": True, "rendicion_id": str(rendicion_id)}

@router.get("/rendiciones/{rendicion_id}/escalamientos")
async def list_rendicion_escalations(
    rendicion_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List escalation records for a rendition."""
    exists = (await db.execute(
        text("SELECT 1 FROM core.rendition WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(rendicion_id)},
    )).scalar()
    if not exists:
        raise HTTPException(status_code=404, detail="Rendición no encontrada")

    rows = (await db.execute(
        text("""
            SELECT e.id, e.rendition_id, e.phase_id, e.escalation_level,
                   e.detected_at, e.alert_id, e.resolved_at,
                   rp.code AS phase_code, rp.name AS phase_name
            FROM core.rendition_escalation e
            JOIN core.rendition_phase rp ON rp.id = e.phase_id
            WHERE e.rendition_id = :rid
            ORDER BY e.detected_at DESC
        """),
        {"rid": str(rendicion_id)},
    )).mappings().all()
    return [EscalationItem(**dict(r)) for r in rows]

@router.post("/rendiciones", status_code=status.HTTP_201_CREATED)
async def create_rendicion(body: RendicionCreate, user: CurrentUser, db: AsyncSession = Depends(get_db)):
    if user["role_code"] not in _RENDICION_WRITE_ROLES:
        raise HTTPException(status_code=403, detail="Rol sin permiso para crear rendiciones")
    if not body.agreement_id and not body.ipr_id:
        raise HTTPException(status_code=422, detail="Se requiere agreement_id o ipr_id (al menos uno)")

    pendiente_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'PENDIENTE'"),
    )).scalar()

    row = (await db.execute(
        text("""
            INSERT INTO core.rendition (
                agreement_id, ipr_id, renderer_id, state_id,
                period_start, period_end, submitted_at, amount,
                phase_entered_at, created_by_id, created_at, updated_at
            ) VALUES (
                :agreement_id, :ipr_id, :renderer_id, :state_id,
                :period_start, :period_end, COALESCE(:submitted_at, NOW()), :amount,
                NOW(), :created_by_id, NOW(), NOW()
            ) RETURNING id
        """),
        {
            "agreement_id": str(body.agreement_id) if body.agreement_id else None,
            "ipr_id": str(body.ipr_id) if body.ipr_id else None,
            "renderer_id": str(body.renderer_id) if body.renderer_id else None,
            "state_id": str(pendiente_id),
            "period_start": body.period_start,
            "period_end": body.period_end,
            "submitted_at": body.submitted_at,
            "amount": body.amount,
            "created_by_id": str(user["id"]),
        },
    )).mappings().first()

    await record_event(db, "CREACION", "core.rendition", row["id"], user["id"], {
        "agreement_id": str(body.agreement_id) if body.agreement_id else None,
        "ipr_id": str(body.ipr_id) if body.ipr_id else None,
        "amount": float(body.amount) if body.amount else None,
    })
    await db.commit()
    return {"id": str(row["id"])}



_RTF_REVIEW_ROLES = DGI_ROLES | {"RTF"}

_RENDICION_TRANSITION_ROLES: dict[tuple[str, str], set[str]] = {
    ("PENDIENTE", "EN_REVISION_RTF"):              _RENDICION_WRITE_ROLES,
    ("EN_REVISION_RTF", "OBSERVADA"):              _RTF_REVIEW_ROLES,
    ("EN_REVISION_RTF", "VISADA_RTF"):             _RTF_REVIEW_ROLES,
    ("VISADA_RTF", "EN_REVISION_UCR"):             DGI_ROLES,
    ("EN_REVISION_UCR", "OBSERVADA"):              DGI_ROLES,
    ("EN_REVISION_UCR", "APROBADA"):               DGI_ROLES,
    ("EN_REVISION_UCR", "APROBADA_PARCIALMENTE"):  DGI_ROLES,
    ("EN_REVISION_UCR", "RECHAZADA"):              DGI_ROLES,
    ("APROBADA_PARCIALMENTE", "EN_REVISION_RTF"):  _RENDICION_WRITE_ROLES,
    ("OBSERVADA", "EN_REVISION_RTF"):              _RENDICION_WRITE_ROLES,
}

_RENDICION_SLA_DAYS: dict[str, int] = {
    "EN_REVISION_RTF": 7,
    "VISADA_RTF": 1,
    "EN_REVISION_UCR": 2,
    "OBSERVADA": 15,
}

RENDICION_UPDATABLE = {"state_id", "responsible_id", "period_start", "period_end", "submitted_at", "amount", "metadata"}

_RENDICION_CYCLE_TARGET_DAYS = 14

_STATE_TO_PHASE_CODE: dict[str, str] = {
    "EN_REVISION_RTF": "REVISION_RTF",
    "VISADA_RTF": "APROBACION_DAF",
    "EN_REVISION_UCR": "CONTABILIZACION_UCR",
}

_ESCALATION_MULTIPLIERS = {1: 1.0, 2: 1.5, 3: 2.0}


async def _get_rendition_history(rendition_id: UUID, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        text("""
            SELECT h.id, h.changed_at, h.comment,
                   prev_cat.code AS previous_state,
                   new_cat.code  AS new_state,
                   (p.names || ' ' || p.paternal_surname) AS changed_by_name
            FROM core.rendition_history h
            JOIN ref.category new_cat ON h.new_state_id = new_cat.id
            LEFT JOIN ref.category prev_cat ON h.previous_state_id = prev_cat.id
            LEFT JOIN core."user" cu ON h.changed_by_id = cu.id
            LEFT JOIN core.person p ON cu.person_id = p.id
            WHERE h.rendition_id = :rendition_id
            ORDER BY h.changed_at DESC
        """),
        {"rendition_id": str(rendition_id)},
    )
    return [dict(r) for r in result.mappings().all()]


@router.patch("/rendiciones/{rendicion_id}")
async def patch_rendicion(
    rendicion_id: UUID,
    body: RendicionUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a rendición. Multi-role state machine:
    PENDIENTE → EN_REVISION_RTF → VISADA_RTF → EN_REVISION_UCR → APROBADA/RECHAZADA.
    OBSERVADA loops back to EN_REVISION_RTF.
    Role authorization checked per-transition.
    """
    # Verify rendicion exists
    row = (await db.execute(
        text("SELECT id, state_id FROM core.rendition WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(rendicion_id)},
    )).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Rendición no encontrada")

    # Build update fields from non-None values, excluding comment (handled separately)
    updates = body.model_dump(exclude_none=True)
    comment = updates.pop("comment", None)

    if not updates:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    # Validate all fields are in allowlist
    invalid = set(updates.keys()) - RENDICION_UPDATABLE
    if invalid:
        raise HTTPException(status_code=400, detail=f"Campos no permitidos: {invalid}")

    # Validate state transition if state_id is changing
    if "state_id" in updates:
        # Get current state code
        current_state = (await db.execute(
            text("SELECT code, valid_transitions FROM ref.category WHERE id = :id"),
            {"id": str(row["state_id"])},
        )).mappings().first()

        # Get target state code
        current_category = current_state
        current_state = current_category["code"]
        new_state = (await db.execute(
            text("SELECT code FROM ref.category WHERE id = :id"),
            {"id": str(updates["state_id"])},
        )).scalar()

        if not new_state:
            raise HTTPException(status_code=400, detail="state_id inválido")

        allowed = set(current_category["valid_transitions"] or [])
        if new_state not in allowed:
            raise HTTPException(
                status_code=409,
                detail=f"Transición inválida: {current_state} → {new_state}. "
                       f"Permitidas: {sorted(allowed) if allowed else 'ninguna (estado terminal)'}",
            )

        # Role-based authorization for this specific transition
        allowed_roles = _RENDICION_TRANSITION_ROLES.get((current_state, new_state))
        if allowed_roles and user["role_code"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol {user['role_code']} no puede ejecutar {current_state} → {new_state}",
            )
    else:
        # Non-transition updates: require write roles
        if user["role_code"] not in _RENDICION_WRITE_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rol sin permiso para modificar rendiciones",
            )

    # Build SET clause
    set_parts = []
    params: dict = {"id": str(rendicion_id), "user_id": user["id"]}

    # Handle metadata as JSONB (asyncpg can't use ::jsonb syntax)
    metadata_val = updates.pop("metadata", None)
    if metadata_val is not None:
        import json as _json
        set_parts.append("metadata = CAST(:v_metadata AS jsonb)")
        params["v_metadata"] = _json.dumps(metadata_val)

    for col, val in updates.items():
        param_name = f"v_{col}"
        set_parts.append(f"{col} = :{param_name}")
        params[param_name] = str(val) if isinstance(val, UUID) else val

    set_parts.append("updated_at = NOW()")
    set_parts.append("updated_by_id = :user_id")

    # Track phase entry time accurately (only reset on state transitions)
    if "state_id" in updates:
        set_parts.append("phase_entered_at = NOW()")

    sql = text(f"""
        UPDATE core.rendition
        SET {', '.join(set_parts)}
        WHERE id = :id AND deleted_at IS NULL
    """)

    await db.execute(sql, params)

    # If state changed and comment provided, update the most recent history row
    if "state_id" in updates and comment:
        await db.execute(
            text("""
                UPDATE core.rendition_history
                SET comment = :comment
                WHERE id = (
                    SELECT id FROM core.rendition_history
                    WHERE rendition_id = :rendition_id
                    ORDER BY changed_at DESC LIMIT 1
                )
            """),
            {"comment": comment, "rendition_id": str(rendicion_id)},
        )

    # Audit trail
    if "state_id" in updates:
        await record_event(db, "STATE_TRANSITION", "core.rendition", rendicion_id, user["id"], {
            "from": current_state,
            "to": new_state,
        })

    await db.commit()

    return {"message": "Rendición actualizada"}
