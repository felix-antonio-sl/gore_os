import json
import math
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException, status
from uuid import UUID
from typing import Optional
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import OPERATIONAL_ROLES, DGI_ROLES, WRITE_OPERATIONAL_ROLES
from app.core.audit import record_event
from app.core.scope import check_ipr_access
from app.schemas.ipr import IPRListItem, IPRDetail, IprCreate, IprAssigneeUpdate, IprUpdate, TrackInfo, CurrentActor
from app.schemas.progress_report import ProgressReportCreate, ProgressReportItem
from app.schemas.ipr_party import IprPartyCreate, IprPartyItem
from app.schemas.ipr_territory import IprTerritoryCreate, IprTerritoryItem
from app.schemas.ipr_milestone import IprMilestoneCreate, IprMilestoneUpdate, IprMilestoneItem
from app.schemas.evaluation import EvaluationAssignmentCreate, EvaluationAssignmentUpdate, EvaluationAssignmentItem
from app.schemas.kinship import KinshipDeclarationCreate, KinshipDeclarationItem, KinshipDeclarationValidate
from app.schemas.ipr_modification import IprModificationCreate, IprModificationUpdate, IprModificationItem
from app.schemas.common import PaginatedResponse
from app.routers.presupuesto import check_glosa_rules, check_glosa07_transfer_limits
from app.routers.notifications import create_notification

router = APIRouter(prefix="/api/ipr", tags=["ipr"])

# Roles that have unrestricted access to all IPRs
_ADMIN_ROLES = {
    "ADMIN_REGIONAL", "ADMIN_SISTEMA", "GOBERNADOR", "SECRETARIO_EJECUTIVO",
    "JEFE_DGI", "ESP_CONTROL_GESTION", "ESP_TD", "ESP_PROCESOS",
}

_CREATE_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "ANALISTA"}
_ASSIGN_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "GOBERNADOR", "JEFE_DEPARTAMENTO", "ANALISTA"}

# ---------------------------------------------------------------------------
# Pullback categórico: Permission = Phase_Boundary ×_Track Role
# Universal defaults per boundary key. Track overrides in financing_track.role_permissions JSONB.
# ---------------------------------------------------------------------------
BOUNDARY_PERMISSIONS: dict[str, set[str]] = {
    "submit_admissibility":      {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "ANALISTA", "JEFE_DIVISION"},
    "admissibility_check":       {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "ANALISTA"},
    "pre_admisible_to_admisible": {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION"},
    "send_evaluation":           {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION", "ANALISTA"},
    "register_eval_result":      {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "ANALISTA"},
    "approve_evaluation":        {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION"},
    "formalization":             {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION"},
    "licitacion_flow":           {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION", "ANALISTA"},
    "intra_F4_transitions":      {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION", "JEFE_DEPARTAMENTO", "ANALISTA"},
    "closure":                   {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"},
    "anulacion":                 {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"},
}


def _get_boundary_key(current_code: str, target_code: str) -> str | None:
    """Map (current_state, target_state) → boundary permission key."""
    if target_code in ("ANULADO", "TERMINADO_ANTICIPADAMENTE"):
        return "anulacion"

    cp = STATUS_PHASE_FIBER.get(current_code)
    tp = STATUS_PHASE_FIBER.get(target_code)
    if not cp or not tp:
        return None

    if cp == "F0" and tp == "F1":
        return "submit_admissibility"
    if cp == "F1" and tp == "F1":
        if current_code == "PRE_ADMISIBLE" and target_code == "ADMISIBLE":
            return "pre_admisible_to_admisible"
        return "admissibility_check"
    if cp == "F1" and tp == "F2":
        return "send_evaluation"
    if cp == "F2" and tp == "F2":
        return "register_eval_result"
    if cp == "F2" and tp == "F3":
        return "approve_evaluation"
    if cp == "F3" and tp == "F4":
        return "formalization"
    if cp == "F4" and tp == "F4":
        if target_code in ("EN_LICITACION", "ADJUDICADO", "CONTRATO_FIRMADO", "EN_OBRA"):
            return "licitacion_flow"
        return "intra_F4_transitions"
    if cp == "F4" and tp == "F5":
        return "intra_F4_transitions"
    if cp == "F5" and tp == "F5":
        return "closure"
    return None


async def _get_transition_roles(
    boundary_key: str, ipr_id: UUID, db: AsyncSession
) -> set[str]:
    """Get allowed roles for a boundary key, applying track overrides if any."""
    universal = BOUNDARY_PERMISSIONS.get(boundary_key)
    if universal is None:
        return set(_ASSIGN_ROLES)  # Fallback for unmapped boundaries

    # Check for track-specific override via financing_track.role_permissions
    row = (await db.execute(
        text("""
            SELECT ft.role_permissions
            FROM core.ipr i
            JOIN ref.category m ON m.id = i.mechanism_id
            JOIN core.financing_track ft ON ft.code = m.code AND ft.is_active = TRUE
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()

    if row and row["role_permissions"]:
        overrides = row["role_permissions"]
        if isinstance(overrides, str):
            overrides = json.loads(overrides)
        if boundary_key in overrides:
            return set(overrides[boundary_key])

    return set(universal)

# ---------------------------------------------------------------------------
# Fibración categórica: ipr_state → mcd_phase
# Cada status pertenece a exactamente una fase MCD.
# ANULADO es terminal cross-cutting — preserva la fase previa.
# ---------------------------------------------------------------------------
STATUS_PHASE_FIBER: dict[str, str] = {
    # F0: Formulación & Ingreso
    "INGRESADO": "F0",
    # F1: Admisibilidad
    "EN_REVISION": "F1", "PRE_ADMISIBLE": "F1", "ADMISIBLE": "F1", "INADMISIBLE": "F1",
    # F2: Evaluación Técnica
    "EN_EVALUACION": "F2",
    "RS": "F2", "FI": "F2", "FC": "F2", "OT": "F2",
    "AD": "F2", "RF": "F2", "ITF": "F2", "AT": "F2",
    # F3: Priorización & Asignación
    "CDP_EMITIDO": "F3",
    # F4: Formalización & Ejecución
    "EN_FORMALIZACION": "F4", "FORMALIZADO": "F4",
    "EN_EJECUCION": "F4", "EN_LICITACION": "F4",
    "ADJUDICADO": "F4", "CONTRATO_FIRMADO": "F4", "EN_OBRA": "F4",
    "RECEPCION_PROVISORIA": "F4", "RECEPCION_DEFINITIVA": "F4",
    "SUSPENDIDO": "F4",
    # F5: Cierre
    "EN_RENDICION": "F5", "RENDICION_APROBADA": "F5",
    "EN_CIERRE_ADMINISTRATIVO": "F5", "CERRADO": "F5",
    "TERMINADO_ANTICIPADAMENTE": "F5",
}

_PHASE_ORDER = {"F0": 0, "F1": 1, "F2": 2, "F3": 3, "F4": 4, "F5": 5}

# Friendly labels for evaluation-result codes used as ipr_state
_EVAL_LABELS: dict[str, str] = {
    "RS": "Rec. Satisfactoria", "FI": "Favorable c/ Indicaciones",
    "FC": "Favorable Condicionado", "OT": "Observado Técnicamente",
    "AD": "Aprobado Directo", "RF": "Rec. Favorable",
    "ITF": "Informe Técnico Favorable", "AT": "Aprobado Técnicamente",
    "NV": "No Viable", "IN": "Inadmisible",
}

# ---------------------------------------------------------------------------
# G15: Actor Actual — (expected_role, user_source, action_label)
# user_source: "assignee" | "division" | "global" | None
# ---------------------------------------------------------------------------
STATUS_ACTOR_MAP: dict[str, tuple[str | None, str | None, str]] = {
    # F0
    "INGRESADO":            ("ANALISTA",        "assignee",  "Completar formulación"),
    # F1
    "EN_REVISION":          ("ANALISTA",        "assignee",  "Completar admisibilidad"),
    "PRE_ADMISIBLE":        ("JEFE_DIVISION",   "division",  "Aprobar admisibilidad"),
    "ADMISIBLE":            ("ANALISTA",        "assignee",  "Enviar a evaluación"),
    "INADMISIBLE":          (None,              None,        "Requiere corrección"),
    # F2
    "EN_EVALUACION":        (None,              None,        "En evaluación externa"),
    "RS":                   ("JEFE_DIVISION",   "division",  "Aprobar resultado"),
    "FI":                   ("JEFE_DIVISION",   "division",  "Aprobar resultado"),
    "FC":                   ("JEFE_DIVISION",   "division",  "Aprobar resultado"),
    "OT":                   ("ANALISTA",        "assignee",  "Subsanar observaciones"),
    "AD":                   ("JEFE_DIVISION",   "division",  "Aprobar resultado"),
    "RF":                   ("JEFE_DIVISION",   "division",  "Aprobar resultado"),
    "ITF":                  ("JEFE_DIVISION",   "division",  "Aprobar resultado"),
    "AT":                   ("JEFE_DIVISION",   "division",  "Aprobar resultado"),
    # F3
    "CDP_EMITIDO":          ("JEFE_DIVISION",   "division",  "Formalizar convenio"),
    # F4
    "EN_FORMALIZACION":     ("ASESOR_JURIDICO", "global",    "V.B. convenio/acto"),
    "FORMALIZADO":          ("ANALISTA",        "assignee",  "Iniciar ejecución"),
    "EN_LICITACION":        ("ANALISTA",        "assignee",  "Gestionar licitación"),
    "ADJUDICADO":           ("ANALISTA",        "assignee",  "Firmar contrato"),
    "CONTRATO_FIRMADO":     ("ANALISTA",        "assignee",  "Iniciar obra"),
    "EN_OBRA":              ("ANALISTA",        "assignee",  "Supervisar ejecución"),
    "EN_EJECUCION":         ("ANALISTA",        "assignee",  "Supervisar ejecución"),
    "RECEPCION_PROVISORIA": ("ANALISTA",        "assignee",  "Recepción definitiva"),
    "RECEPCION_DEFINITIVA": ("ANALISTA",        "assignee",  "Iniciar rendición"),
    "SUSPENDIDO":           ("JEFE_DIVISION",   "division",  "Resolver suspensión"),
    # F5
    "EN_RENDICION":         ("RTF",             "global",    "Revisar rendición"),
    "RENDICION_APROBADA":   ("JEFE_DIVISION",   "division",  "Cierre administrativo"),
    "EN_CIERRE_ADMINISTRATIVO": ("ADMIN_REGIONAL", "global", "Firmar cierre"),
    # Terminales
    "CERRADO":              (None,              None,        "Cerrada"),
    "TERMINADO_ANTICIPADAMENTE": (None,          None,        "Terminada"),
    "ANULADO":              (None,              None,        "Anulada"),
}

_ROLE_LABELS = {
    "ANALISTA": "Analista",
    "JEFE_DIVISION": "Jefe de División",
    "JEFE_DEPARTAMENTO": "Jefe de Departamento",
    "ASESOR_JURIDICO": "Asesor Jurídico",
    "RTF": "RTF",
    "ADMIN_REGIONAL": "Admin. Regional",
    "GOBERNADOR": "Gobernador",
}


async def _resolve_current_actor(
    status_code: str,
    assignee_id: str | None,
    sponsor_division_id: str | None,
    db: AsyncSession,
) -> CurrentActor | None:
    """Resolve the positional role that should act next (e.g. 'Analista DIPIR')."""
    entry = STATUS_ACTOR_MAP.get(status_code)
    if not entry or not entry[0]:
        return None
    role, source, action = entry
    division_abbr = None
    if source == "assignee" and assignee_id:
        row = (await db.execute(text("""
            SELECT o.short_name
            FROM core."user" u
            JOIN core.organization o ON o.id = u.division_id
            WHERE u.id = :uid AND u.deleted_at IS NULL
        """), {"uid": assignee_id})).mappings().first()
        if row:
            division_abbr = row["short_name"]
    elif source == "division" and sponsor_division_id:
        row = (await db.execute(text("""
            SELECT o.short_name
            FROM core.organization o
            WHERE o.id = :div_id AND o.deleted_at IS NULL
        """), {"div_id": sponsor_division_id})).mappings().first()
        if row:
            division_abbr = row["short_name"]
    base_label = _ROLE_LABELS.get(role, role)
    role_label = f"{base_label} {division_abbr}" if division_abbr else base_label
    return CurrentActor(role=role, role_label=role_label, action=action)


# ---------------------------------------------------------------------------
# Universal fallback for IPRs without mechanism (backward compat)
_UNIVERSAL_FAVORABLE = {"RS", "FI", "RF", "ITF", "AT", "AD"}


async def _get_track_config(mechanism_code: str, db: AsyncSession) -> dict | None:
    """Load financing track configuration from DB. Returns None if not found."""
    result = await db.execute(
        text("""
            SELECT code, label, evaluator_code, evaluator_label,
                   favorable_products, unfavorable_products, terminal_negative,
                   thresholds, required_attrs, sla_days, rs_validity_years,
                   role_permissions
            FROM core.financing_track
            WHERE code = :code AND is_active = TRUE
        """),
        {"code": mechanism_code},
    )
    row = result.mappings().first()
    if not row:
        return None
    return {
        "label": row["label"],
        "evaluator": row["evaluator_code"],
        "evaluator_label": row["evaluator_label"],
        "favorable_products": list(row["favorable_products"] or []),
        "unfavorable_products": list(row["unfavorable_products"] or []),
        "terminal_negative": list(row["terminal_negative"] or []),
        "thresholds": dict(row["thresholds"] or {}),
        "required_attrs": list(row["required_attrs"] or []),
        "sla_days": dict(row["sla_days"] or {}),
        "rs_validity_years": row["rs_validity_years"],
        "role_permissions": dict(row["role_permissions"] or {}) if "role_permissions" in row.keys() else {},
    }

# CORE approval constants (fallbacks if DB thresholds unavailable)
_CORE_QUORUM_SIMPLE = 9


async def _get_utm_value(db: AsyncSession) -> int:
    """Get current UTM value from DB (administrable)."""
    row = (await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'UTM_VALUE' AND is_active = TRUE")
    )).mappings().first()
    if row and row["value_utm"]:
        return int(row["value_utm"])
    return 67_294  # fallback


async def _get_threshold(code: str, db: AsyncSession) -> dict | None:
    """Load a universal threshold by code."""
    row = (await db.execute(
        text("""
            SELECT code, label, value_utm, value_pct, enforcement_point, source_normativa
            FROM core.financial_threshold
            WHERE code = :code AND is_active = TRUE
        """),
        {"code": code},
    )).mappings().first()
    if not row:
        return None
    return dict(row)


async def _check_utm_threshold(ipr_id: UUID, threshold_code: str, db: AsyncSession) -> dict | None:
    """Generic gate: check if IPR monto exceeds a UTM threshold.
    Returns {name, met, detail} gate dict or None if below threshold."""
    threshold = await _get_threshold(threshold_code, db)
    if not threshold or not threshold["value_utm"]:
        return None

    utm = await _get_utm_value(db)
    monto = await _get_ipr_monto(ipr_id, db)

    threshold_clp = float(threshold["value_utm"]) * utm
    if monto <= threshold_clp:
        return None
    return {
        "name": threshold_code.lower(),
        "value_utm": float(threshold["value_utm"]),
        "monto": monto,
        "threshold_clp": threshold_clp,
    }


async def _get_ipr_monto(ipr_id: UUID, db: AsyncSession) -> float:
    """Get IPR monto_total from metadata JSONB."""
    row = (await db.execute(
        text("SELECT metadata->>'monto_total' AS monto FROM core.ipr WHERE id = :id"),
        {"id": str(ipr_id)},
    )).mappings().first()
    if row and row["monto"]:
        try:
            return float(row["monto"])
        except (ValueError, TypeError):
            pass
    return 0.0


async def _check_track_amount_gates(
    ipr_id: UUID, mechanism_code: str | None, transition: str, db: AsyncSession,
) -> list[dict]:
    """Evaluate track-specific amount gates for a phase transition.

    Reads thresholds from financing_track.thresholds JSONB and compares
    against IPR monto_total. Returns list of gate dicts.
    """
    gates: list[dict] = []
    if not mechanism_code:
        return gates

    track = await _get_track_config(mechanism_code, db)
    if not track:
        return gates

    thresholds = track.get("thresholds", {})
    if not thresholds:
        return gates

    utm = await _get_utm_value(db)
    monto = await _get_ipr_monto(ipr_id, db)

    if transition == "F2->F3":
        # max_utm: block if IPR amount exceeds track ceiling
        if "max_utm" in thresholds:
            max_clp = float(thresholds["max_utm"]) * utm
            exceeds = monto > max_clp
            gates.append({
                "name": "track_max_utm",
                "met": not exceeds,
                "detail": (
                    f"Tope {mechanism_code}: monto ${monto:,.0f} "
                    f"{'excede' if exceeds else 'dentro de'} "
                    f"máximo {thresholds['max_utm']:,} UTM (${max_clp:,.0f})"
                ),
            })

        # min_clp: block if IPR amount is below track floor
        if "min_clp" in thresholds:
            min_val = float(thresholds["min_clp"])
            below = monto < min_val and monto > 0
            gates.append({
                "name": "track_min_clp",
                "met": not below,
                "detail": (
                    f"Mínimo {mechanism_code}: monto ${monto:,.0f} "
                    f"{'bajo' if below else 'cumple'} "
                    f"mínimo ${min_val:,.0f}"
                ),
            })

        # puntaje_min: check evaluation numeric_score (Wave D)
        if "puntaje_min" in thresholds:
            min_score = float(thresholds["puntaje_min"])
            score_row = (await db.execute(
                text("""
                    SELECT numeric_score FROM core.evaluation_assignment
                    WHERE ipr_id = :ipr_id AND deleted_at IS NULL
                      AND numeric_score IS NOT NULL
                    ORDER BY assigned_at DESC LIMIT 1
                """),
                {"ipr_id": str(ipr_id)},
            )).mappings().first()
            score = float(score_row["numeric_score"]) if score_row else None
            if score is not None:
                meets = score >= min_score
                gates.append({
                    "name": "track_puntaje_min",
                    "met": meets,
                    "detail": (
                        f"Puntaje {mechanism_code}: {score:.2f} "
                        f"{'cumple' if meets else 'bajo'} "
                        f"mínimo {min_score:.2f}"
                    ),
                })
            else:
                gates.append({
                    "name": "track_puntaje_min",
                    "met": False,
                    "detail": f"Puntaje {mechanism_code}: sin puntaje registrado (mínimo requerido: {min_score:.2f})",
                })

    elif transition == "F3->F4":
        # cgr_res30_utm: informational gate (track-specific CGR threshold)
        if "cgr_res30_utm" in thresholds:
            cgr_clp = float(thresholds["cgr_res30_utm"]) * utm
            exceeds = monto > cgr_clp
            gates.append({
                "name": "track_cgr_res30",
                "met": True,  # informational — never blocks
                "type": "informational",
                "detail": (
                    f"CGR Res.30 {mechanism_code}: monto ${monto:,.0f} "
                    f"{'supera' if exceeds else 'bajo'} "
                    f"umbral {thresholds['cgr_res30_utm']:,} UTM (${cgr_clp:,.0f}) — informativo"
                ),
            })

        # licitacion_max_days: block if LICITACION milestone deviation exceeds threshold
        if "licitacion_max_days" in thresholds:
            max_days = int(thresholds["licitacion_max_days"])
            dev_row = (await db.execute(
                text("""
                    SELECT im.deviation_days
                    FROM core.ipr_milestone im
                    JOIN ref.category c ON c.id = im.milestone_type_id
                    WHERE im.ipr_id = :ipr_id AND im.deleted_at IS NULL
                      AND c.code = 'LICITACION' AND im.actual_date IS NOT NULL
                    ORDER BY im.actual_date DESC LIMIT 1
                """),
                {"ipr_id": str(ipr_id)},
            )).mappings().first()
            if dev_row and dev_row["deviation_days"] is not None:
                deviation = int(dev_row["deviation_days"])
                exceeds = deviation > max_days
                gates.append({
                    "name": "track_licitacion_days",
                    "met": not exceeds,
                    "detail": (
                        f"Licitación {mechanism_code}: desviación {deviation} días "
                        f"{'excede' if exceeds else 'dentro de'} "
                        f"máximo {max_days} días"
                    ),
                })

    elif transition == "F4->F5":
        # sisrec_mandatory_utm: require renditions if amount exceeds threshold
        if "sisrec_mandatory_utm" in thresholds:
            sisrec_clp = float(thresholds["sisrec_mandatory_utm"]) * utm
            if monto > sisrec_clp:
                rend_count = (await db.execute(
                    text("""
                        SELECT COUNT(*) FROM core.rendition
                        WHERE ipr_id = :ipr_id AND deleted_at IS NULL
                    """),
                    {"ipr_id": str(ipr_id)},
                )).scalar() or 0
                has_renditions = rend_count > 0
                gates.append({
                    "name": "track_sisrec_mandatory",
                    "met": has_renditions,
                    "detail": (
                        f"SISREC obligatorio {mechanism_code}: monto ${monto:,.0f} "
                        f"supera {thresholds['sisrec_mandatory_utm']:,} UTM — "
                        f"{'tiene' if has_renditions else 'requiere'} "
                        f"rendiciones ({rend_count} encontrada(s))"
                    ),
                })

    return gates


async def _check_core_approval(
    ipr_id: UUID, db: AsyncSession, threshold_utm_override: int | None = None,
) -> dict | None:
    """Check if IPR needs and has CORE approval.

    If threshold_utm_override is provided (from financing_track.thresholds.core_approval),
    it takes precedence over the universal CORE_APPROVAL threshold from DB.
    Returns a gate dict if applicable, or None if threshold not reached.
    """
    if threshold_utm_override is not None:
        utm = await _get_utm_value(db)
        monto = await _get_ipr_monto(ipr_id, db)
        threshold_clp = float(threshold_utm_override) * utm
        if monto <= threshold_clp:
            return None
        threshold_utm = threshold_utm_override
    else:
        check = await _check_utm_threshold(ipr_id, "CORE_APPROVAL", db)
        if check is None:
            return None  # Below threshold — no CORE gate needed
        threshold_utm = int(check["value_utm"])

    # Check for APROBADO vote on session_agreement linked to this IPR
    vote_result = (await db.execute(
        text("""
            SELECT
                COUNT(*) FILTER (WHERE vc.code = 'A_FAVOR') AS favor,
                COUNT(*) FILTER (WHERE vc.code = 'EN_CONTRA') AS contra
            FROM core.session_vote sv
            JOIN core.session_agreement sa ON sa.id = sv.session_agreement_id
            JOIN ref.category vc ON vc.id = sv.vote_option_id
            WHERE sa.ipr_id = :ipr_id
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().first()

    favor = vote_result["favor"] if vote_result else 0
    approved = favor >= _CORE_QUORUM_SIMPLE
    return {
        "name": "core_approval",
        "met": approved,
        "detail": f"Requiere aprobación CORE (monto >{threshold_utm:,} UTM). Votos a favor: {favor}/{_CORE_QUORUM_SIMPLE}",
    }


async def _check_fril_fraccionamiento(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """HΩ-01: Detect artificial fragmentation of FRIL projects.

    Looks for sibling FRIL IPRs with same executor + same territory (comuna) + created
    within ±90 days. If combined monto exceeds FRIL max_utm threshold, blocks.
    Returns gate dict or None if check is not applicable.
    """
    # Load IPR's mechanism, executor, and creation date
    ipr_row = (await db.execute(
        text("""
            SELECT i.id, i.executor_id, i.created_at, i.metadata->>'monto_total' AS monto,
                   m.code AS mechanism_code
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not ipr_row or ipr_row["mechanism_code"] != "FRIL":
        return None
    if not ipr_row["executor_id"]:
        return None  # No executor — can't check siblings

    # Load track config for parametric thresholds
    track = await _get_track_config("FRIL", db)
    sibling_days = int((track or {}).get("thresholds", {}).get("fril_sibling_days", 90))

    # Get territories linked to this IPR
    terr_rows = (await db.execute(
        text("""
            SELECT territory_id FROM core.ipr_territory
            WHERE ipr_id = :id AND deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().all()
    if not terr_rows:
        return None  # No territory — can't check

    territory_ids = [str(r["territory_id"]) for r in terr_rows]

    # Find sibling FRIL IPRs: same executor, overlapping territory, ±90 days
    siblings = (await db.execute(
        text("""
            SELECT i.id, i.metadata->>'monto_total' AS monto
            FROM core.ipr i
            JOIN ref.category m ON m.id = i.mechanism_id
            JOIN core.ipr_territory it ON it.ipr_id = i.id AND it.deleted_at IS NULL
            WHERE m.code = 'FRIL'
              AND i.executor_id = :executor_id
              AND i.id != :ipr_id
              AND i.deleted_at IS NULL
              AND it.territory_id = ANY(:territory_ids)
              AND i.created_at BETWEEN :date_from AND :date_to
        """),
        {
            "executor_id": str(ipr_row["executor_id"]),
            "ipr_id": str(ipr_id),
            "territory_ids": territory_ids,
            "date_from": ipr_row["created_at"] - timedelta(days=sibling_days),
            "date_to": ipr_row["created_at"] + timedelta(days=sibling_days),
        },
    )).mappings().all()

    if not siblings:
        return None  # No siblings found — no fragmentation risk

    # Calculate combined monto
    own_monto = float(ipr_row["monto"]) if ipr_row["monto"] else 0.0
    sibling_montos = sum(float(s["monto"]) for s in siblings if s["monto"])
    combined = own_monto + sibling_montos

    # Check against FRIL max_utm threshold (track already loaded above)
    if not track:
        return None
    max_utm = track.get("thresholds", {}).get("max_utm")
    if not max_utm:
        return None

    utm = await _get_utm_value(db)
    max_clp = float(max_utm) * utm
    exceeds = combined > max_clp

    return {
        "name": "fril_fraccionamiento",
        "met": not exceeds,
        "detail": (
            f"Fraccionamiento FRIL: {len(siblings)} proyecto(s) hermano(s) "
            f"(mismo ejecutor + comuna + ±{sibling_days} días). "
            f"Monto combinado ${combined:,.0f} "
            f"{'excede' if exceeds else 'dentro de'} "
            f"tope {max_utm:,} UTM (${max_clp:,.0f})"
        ),
    }


async def _check_fril_max_per_comuna(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """HΩ-09: Max 5 FRIL projects per territory per fiscal year.

    Exempt: IPRs with fril_category IN ('A2', 'A3') (emergency/reconstruction).
    Returns gate dict or None if not applicable.
    """
    # Load IPR mechanism and year
    ipr_row = (await db.execute(
        text("""
            SELECT i.id, i.created_at, m.code AS mechanism_code,
                   i.metadata->>'fril_category' AS fril_category
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not ipr_row or ipr_row["mechanism_code"] != "FRIL":
        return None

    # Check exemption from core.fril_category table (TP-04)
    fril_cat = ipr_row["fril_category"]
    if fril_cat:
        exempt = (await db.execute(
            text("""
                SELECT is_exempt_commune_limit FROM core.fril_category
                WHERE code = :code AND is_active = true
            """),
            {"code": fril_cat},
        )).scalar()
        if exempt:
            return None

    # Load parametric limit from track config
    track = await _get_track_config("FRIL", db)
    max_per_territory = int((track or {}).get("thresholds", {}).get("fril_max_per_territory", 5))

    # Get territories linked to this IPR
    terr_rows = (await db.execute(
        text("""
            SELECT territory_id FROM core.ipr_territory
            WHERE ipr_id = :id AND deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().all()
    if not terr_rows:
        return None  # No territory — can't check

    fiscal_year = ipr_row["created_at"].year

    # Check each territory
    for terr in terr_rows:
        count_row = (await db.execute(
            text("""
                SELECT COUNT(DISTINCT i.id) AS cnt
                FROM core.ipr i
                JOIN ref.category m ON m.id = i.mechanism_id
                JOIN core.ipr_territory it ON it.ipr_id = i.id AND it.deleted_at IS NULL
                WHERE m.code = 'FRIL'
                  AND it.territory_id = :territory_id
                  AND EXTRACT(YEAR FROM i.created_at) = :fiscal_year
                  AND i.deleted_at IS NULL
                  AND i.id != :ipr_id
                  AND NOT EXISTS (
                       SELECT 1 FROM core.fril_category fc
                       WHERE fc.code = i.metadata->>'fril_category'
                         AND fc.is_exempt_commune_limit = true
                         AND fc.is_active = true
                  )
            """),
            {
                "territory_id": str(terr["territory_id"]),
                "fiscal_year": fiscal_year,
                "ipr_id": str(ipr_id),
            },
        )).mappings().first()

        existing = int(count_row["cnt"]) if count_row else 0
        if existing >= max_per_territory:
            # Get territory name for detail
            terr_name_row = (await db.execute(
                text("SELECT name FROM core.territory WHERE id = :id"),
                {"id": str(terr["territory_id"])},
            )).mappings().first()
            terr_name = terr_name_row["name"] if terr_name_row else "desconocido"
            return {
                "name": "fril_max_comuna",
                "met": False,
                "detail": (
                    f"Máximo {max_per_territory} FRIL por comuna/año: {terr_name} ya tiene "
                    f"{existing} proyecto(s) FRIL en {fiscal_year} (excluye categorías exentas)"
                ),
            }

    return None  # All territories have capacity


async def _check_rs_vigencia(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """HΩ-05: RS evaluation validity check.

    RS (or any favorable product) expires after rs_validity_years without budget assignment.
    Checks at F3→F4: blocks if last favorable evaluation is expired.
    """
    # Load IPR mechanism
    ipr_row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not ipr_row or not ipr_row["mechanism_code"]:
        return None

    track = await _get_track_config(ipr_row["mechanism_code"], db)
    if not track or not track.get("rs_validity_years"):
        return None  # Track doesn't have validity constraint

    validity_years = int(track["rs_validity_years"])
    favorable_products = set(track.get("favorable_products", []))
    if not favorable_products:
        return None

    # Find most recent completed evaluation with favorable result
    eval_row = (await db.execute(
        text("""
            SELECT ea.completed_at, rc.code AS result_code
            FROM core.evaluation_assignment ea
            LEFT JOIN ref.category rc ON rc.id = ea.result_id
            WHERE ea.ipr_id = :ipr_id AND ea.deleted_at IS NULL
              AND ea.completed_at IS NOT NULL
            ORDER BY ea.completed_at DESC LIMIT 1
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().first()

    if not eval_row:
        return {
            "name": "rs_vigencia",
            "met": False,
            "detail": f"Sin evaluación completada — se requiere dictamen favorable ({', '.join(sorted(favorable_products))})",
        }

    result_code = eval_row["result_code"]
    if result_code not in favorable_products:
        return {
            "name": "rs_vigencia",
            "met": False,
            "detail": f"Último dictamen ({result_code}) no es favorable — se requiere: {', '.join(sorted(favorable_products))}",
        }

    # Check expiry
    from datetime import datetime, timezone
    completed_at = eval_row["completed_at"]
    if completed_at.tzinfo is None:
        completed_at = completed_at.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    expiry = completed_at + timedelta(days=validity_years * 365)
    expired = now > expiry

    return {
        "name": "rs_vigencia",
        "met": not expired,
        "detail": (
            f"Dictamen {result_code} completado {completed_at.strftime('%Y-%m-%d')} — "
            f"vigencia {validity_years} años {'(expirado, requiere re-evaluación)' if expired else '(vigente)'}"
        ),
    }


async def _check_evaluation_type_match(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """HΩ-12: Verify evaluation result matches mechanism's expected products.

    Informational gate (never blocks): warns if evaluation result_code doesn't match
    the track's favorable_products or unfavorable_products.
    """
    ipr_row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not ipr_row or not ipr_row["mechanism_code"]:
        return None

    track = await _get_track_config(ipr_row["mechanism_code"], db)
    if not track:
        return None

    # Get all known product codes for this track
    known_products = set(track.get("favorable_products", [])) | set(track.get("unfavorable_products", []))
    if not known_products:
        return None

    # Find completed evaluations with result codes
    evals = (await db.execute(
        text("""
            SELECT rc.code AS result_code
            FROM core.evaluation_assignment ea
            JOIN ref.category rc ON rc.id = ea.result_id
            WHERE ea.ipr_id = :ipr_id AND ea.deleted_at IS NULL
              AND ea.completed_at IS NOT NULL
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().all()

    if not evals:
        return None  # No completed evaluations — nothing to check

    mismatched = [e["result_code"] for e in evals if e["result_code"] not in known_products]
    if not mismatched:
        return None  # All match — no warning needed

    return {
        "name": "eval_type_match",
        "met": True,  # Informational — never blocks
        "type": "informational",
        "detail": (
            f"Advertencia: dictamen(es) {', '.join(mismatched)} no corresponde(n) "
            f"al track {ipr_row['mechanism_code']} "
            f"(productos esperados: {', '.join(sorted(known_products))})"
        ),
    }


async def _check_c33_conservation(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """HΩ-07: C33 conservation cost ratio check.

    If conservation cost > conservation_exempt_pct (default 30%) of replacement cost,
    suggests reclassification to SNI. Informational — never blocks.
    """
    ipr_row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code,
                   i.metadata->>'costo_conservacion' AS costo_conservacion,
                   i.metadata->>'costo_reposicion' AS costo_reposicion
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not ipr_row or ipr_row["mechanism_code"] != "C33":
        return None

    costo_cons = ipr_row["costo_conservacion"]
    costo_repo = ipr_row["costo_reposicion"]

    if not costo_cons or not costo_repo:
        return {
            "name": "c33_conservation",
            "met": True,  # Informational
            "type": "informational",
            "detail": "C33: Ingresar costo_conservacion y costo_reposicion en metadata para evaluar ratio de conservación",
        }

    try:
        cons = float(costo_cons)
        repo = float(costo_repo)
    except (ValueError, TypeError):
        return {
            "name": "c33_conservation",
            "met": True,
            "type": "informational",
            "detail": "C33: Valores de costo inválidos en metadata",
        }

    if repo <= 0:
        return None

    # Load threshold from track config
    track = await _get_track_config("C33", db)
    exempt_pct = 30.0
    if track:
        exempt_pct = float(track.get("thresholds", {}).get("conservation_exempt_pct", 30))

    ratio = (cons / repo) * 100
    exceeds = ratio > exempt_pct

    return {
        "name": "c33_conservation",
        "met": True,  # Informational — never blocks
        "type": "informational",
        "detail": (
            f"C33 conservación: ratio {ratio:.1f}% "
            f"(${cons:,.0f} / ${repo:,.0f}) "
            f"{'excede' if exceeds else 'dentro de'} umbral {exempt_pct:.0f}%"
            f"{' — considerar reclasificación a SNI' if exceeds else ''}"
        ),
    }


async def _check_c33_technical_certification(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """C33 technical certification gate (blocking, F1→F2).

    Routes to SERVIU (edificación) or MOP (vialidad) based on categoria_c33.
    Blocks if certification is missing or unfavorable.
    """
    ipr_row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code,
                   i.metadata->>'categoria_c33' AS categoria_c33,
                   i.metadata->>'informe_tecnico_favorable' AS informe
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()

    if not ipr_row or ipr_row["mechanism_code"] != "C33":
        return None

    categoria = ipr_row["categoria_c33"]
    informe = ipr_row["informe"]

    # Look up certifier org from categoria_c33 scheme
    certifier = None
    if categoria:
        cert_row = (await db.execute(
            text("""
                SELECT metadata->>'certifier_org_code' AS certifier
                FROM ref.category
                WHERE scheme = 'categoria_c33' AND code = :code AND deleted_at IS NULL
            """),
            {"code": categoria},
        )).mappings().first()
        certifier = cert_row["certifier"] if cert_row else None

    if not categoria:
        return {
            "name": "c33_technical_certification",
            "met": False,
            "detail": "Asignar categoría C33 (EDIFICACION/VIALIDAD) antes de continuar",
        }

    if informe is None:
        org_label = certifier or "organismo certificador"
        return {
            "name": "c33_technical_certification",
            "met": False,
            "detail": f"Certificación técnica pendiente — solicitar a {org_label}",
        }

    # metadata stores booleans as JSON strings
    is_favorable = informe == "true" or informe is True
    if not is_favorable:
        org_label = certifier or "organismo certificador"
        return {
            "name": "c33_technical_certification",
            "met": False,
            "detail": f"Certificación técnica desfavorable de {org_label}",
        }

    return {
        "name": "c33_technical_certification",
        "met": True,
        "detail": f"Certificación técnica favorable de {certifier or 'organismo'}",
    }


async def _check_sni_proporcionalidad(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """HΩ-11: SNI proportionality levels by project amount.

    Reads sni_level_config table and determines the evaluation level + expected evaluator.
    Informational — never blocks.
    """
    ipr_row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not ipr_row or ipr_row["mechanism_code"] != "SNI":
        return None

    monto = await _get_ipr_monto(ipr_id, db)
    utm = await _get_utm_value(db)
    monto_utm = monto / utm if utm > 0 else 0

    # Load SNI levels from DB
    levels = (await db.execute(
        text("""
            SELECT level_number, label, min_utm, max_utm, evaluator_code, requires_external_eval
            FROM core.sni_level_config
            WHERE is_active = TRUE
            ORDER BY level_number
        """),
    )).mappings().all()

    if not levels:
        return None  # Table not populated

    # Find matching level
    matched_level = None
    for level in levels:
        min_u = float(level["min_utm"])
        max_u = float(level["max_utm"]) if level["max_utm"] is not None else float('inf')
        if min_u <= monto_utm < max_u or (level["max_utm"] is None and monto_utm >= min_u):
            matched_level = level
            break

    if not matched_level:
        matched_level = levels[-1]  # Fallback to highest level

    ext_label = "evaluación externa obligatoria" if matched_level["requires_external_eval"] else "sin evaluación externa"

    return {
        "name": "sni_proporcionalidad",
        "met": True,  # Informational — never blocks
        "type": "informational",
        "detail": (
            f"SNI {matched_level['label']}: monto {monto_utm:,.0f} UTM "
            f"→ evaluador recomendado: {matched_level['evaluator_code']} ({ext_label})"
        ),
    }


async def _check_fril_tender_deadline(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """HΩ-08: FRIL tender deadline — blocks F3→F4 if tender not started within N days."""
    row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code, i.updated_at
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not row or row["mechanism_code"] != "FRIL":
        return None

    track = await _get_track_config("FRIL", db)
    deadline_days = int((track or {}).get("thresholds", {}).get("tender_deadline_days", 90))
    ipr_updated = row["updated_at"]

    # Check if LICITACION milestone exists with actual_date
    lic_row = (await db.execute(
        text("""
            SELECT actual_date FROM core.ipr_milestone im
            JOIN ref.category mt ON mt.id = im.milestone_type_id
            WHERE im.ipr_id = :id AND mt.code = 'LICITACION'
              AND im.deleted_at IS NULL AND im.actual_date IS NOT NULL
            LIMIT 1
        """),
        {"id": str(ipr_id)},
    )).mappings().first()

    if lic_row:
        return None  # Tender started — gate passes silently

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    if ipr_updated.tzinfo is None:
        from datetime import timezone as tz
        ipr_updated = ipr_updated.replace(tzinfo=tz.utc)
    elapsed = (now - ipr_updated).days

    if elapsed > deadline_days:
        return {
            "name": "fril_tender_deadline",
            "met": False,
            "detail": (
                f"FRIL: {elapsed} días sin licitación desde aprobación técnica "
                f"(máximo {deadline_days} días). Requiere hito LICITACION con fecha real."
            ),
        }

    return {
        "name": "fril_tender_deadline",
        "met": True,
        "detail": (
            f"FRIL: {elapsed}/{deadline_days} días transcurridos sin licitación. "
            f"Plazo vigente."
        ),
    }


async def _check_glosa06_single_purpose(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """HΩ-06: Glosa 06 programs must have exactly 1 MML Purpose."""
    row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code, i.metadata
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not row or row["mechanism_code"] != "GLOSA06":
        return None

    metadata = row["metadata"] or {}
    purpose_count_raw = metadata.get("mml_purpose_count")

    if purpose_count_raw is None:
        return {
            "name": "glosa06_single_purpose",
            "met": False,
            "detail": (
                "Glosa 06: falta metadata 'mml_purpose_count'. "
                "Ingrese el conteo de Propósitos MML para continuar."
            ),
        }

    try:
        purpose_count = int(purpose_count_raw)
    except (ValueError, TypeError):
        return {
            "name": "glosa06_single_purpose",
            "met": False,
            "detail": f"Glosa 06: valor inválido de mml_purpose_count: '{purpose_count_raw}'",
        }

    if purpose_count != 1:
        return {
            "name": "glosa06_single_purpose",
            "met": False,
            "detail": (
                f"Glosa 06: requiere exactamente 1 Propósito MML, "
                f"pero se encontraron {purpose_count}."
            ),
        }

    return None  # Exactly 1 — gate passes silently


async def _check_glosa06_direct_executor(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """Glosa 06: GORE must be the direct executor (no delegation to third parties)."""
    row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not row or row["mechanism_code"] != "GLOSA06":
        return None

    # Check if GORE is registered as EJECUTOR in ipr_party
    gore_executor = (await db.execute(
        text("""
            SELECT COUNT(*) AS cnt
            FROM core.ipr_party ip
            JOIN ref.category role ON role.id = ip.party_role_id
            JOIN core.organization o ON o.id = ip.organization_id
            WHERE ip.ipr_id = :ipr_id
              AND role.code = 'EJECUTOR'
              AND o.code = 'GORE-NUBLE'
              AND ip.deleted_at IS NULL
        """),
        {"ipr_id": str(ipr_id)},
    )).scalar() or 0

    if gore_executor == 0:
        return {
            "name": "glosa06_direct_executor",
            "met": False,
            "detail": (
                "Glosa 06: GORE debe ser ejecutor directo. "
                "Registre GORE-NUBLE como EJECUTOR en Partes del IPR."
            ),
        }

    return None  # GORE is executor — gate passes silently


# SLA constants for moroso check (same as dgi_data.py, defined locally to avoid circular import)
async def _check_pagare_notarial(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """HΩ-03: SUBV8 requires notarial promissory note covering 100% with ≥18m validity."""
    row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code, i.metadata
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not row or row["mechanism_code"] != "SUBV8":
        return None

    metadata = row["metadata"] or {}
    monto_total = await _get_ipr_monto(ipr_id, db)
    pagare_monto_raw = metadata.get("pagare_monto")
    pagare_fecha_raw = metadata.get("pagare_fecha_vencimiento")

    if not pagare_monto_raw or not pagare_fecha_raw:
        return {
            "name": "pagare_notarial",
            "met": False,
            "detail": (
                "SUBV8: requiere pagaré notarial. Ingrese 'pagare_monto' y "
                "'pagare_fecha_vencimiento' en metadata del IPR."
            ),
        }

    try:
        pagare_monto = float(pagare_monto_raw)
    except (ValueError, TypeError):
        return {
            "name": "pagare_notarial",
            "met": False,
            "detail": f"SUBV8: valor inválido de pagare_monto: '{pagare_monto_raw}'",
        }

    # Check coverage and validity against track thresholds
    track = await _get_track_config("SUBV8", db)
    coverage_pct = float((track or {}).get("thresholds", {}).get("pagare_coverage_pct", 100))
    min_required = monto_total * (coverage_pct / 100)

    if pagare_monto < min_required:
        return {
            "name": "pagare_notarial",
            "met": False,
            "detail": (
                f"SUBV8: pagaré (${pagare_monto:,.0f}) no cubre {coverage_pct:.0f}% del monto total "
                f"(${monto_total:,.0f}). Debe ser ≥ ${min_required:,.0f}."
            ),
        }

    validity_months = int((track or {}).get("thresholds", {}).get("pagare_validity_months", 18))

    from datetime import datetime, timezone
    try:
        fecha_venc = datetime.fromisoformat(pagare_fecha_raw)
        if fecha_venc.tzinfo is None:
            fecha_venc = fecha_venc.replace(tzinfo=timezone.utc)
    except ValueError:
        return {
            "name": "pagare_notarial",
            "met": False,
            "detail": f"SUBV8: fecha de vencimiento inválida: '{pagare_fecha_raw}'",
        }

    now = datetime.now(timezone.utc)
    remaining_days = (fecha_venc - now).days
    min_days = validity_months * 30  # Approximate

    if remaining_days < min_days:
        return {
            "name": "pagare_notarial",
            "met": False,
            "detail": (
                f"SUBV8: pagaré vence en {remaining_days} días, "
                f"requiere mínimo {validity_months} meses ({min_days} días) de vigencia."
            ),
        }

    return None  # Passes silently


async def _check_directorio_certificate(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """HΩ-04: SUBV8 requires board certificate issued within N days (default 60)."""
    row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code, i.metadata
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not row or row["mechanism_code"] != "SUBV8":
        return None

    metadata = row["metadata"] or {}
    cert_date_raw = metadata.get("directorio_cert_date")

    if not cert_date_raw:
        return {
            "name": "directorio_certificate",
            "met": False,
            "detail": (
                "SUBV8: requiere certificado de directorio vigente. "
                "Ingrese 'directorio_cert_date' en metadata del IPR."
            ),
        }

    from datetime import datetime, timezone
    try:
        cert_date = datetime.fromisoformat(cert_date_raw)
        if cert_date.tzinfo is None:
            cert_date = cert_date.replace(tzinfo=timezone.utc)
    except ValueError:
        return {
            "name": "directorio_certificate",
            "met": False,
            "detail": f"SUBV8: fecha de certificado inválida: '{cert_date_raw}'",
        }

    track = await _get_track_config("SUBV8", db)
    max_days = int((track or {}).get("thresholds", {}).get("directorio_max_days", 60))

    now = datetime.now(timezone.utc)
    age_days = (now - cert_date).days

    if age_days > max_days:
        return {
            "name": "directorio_certificate",
            "met": False,
            "detail": (
                f"SUBV8: certificado de directorio tiene {age_days} días de antigüedad "
                f"(máximo {max_days} días). Requiere renovación."
            ),
        }

    return None  # Passes silently


async def _check_ranking_persistence(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """HΩ-13: Informational — warn if competitive mechanism lacks ranking data."""
    row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not row or row["mechanism_code"] not in ("SUBV8", "FRPD"):
        return None

    # Check for completed evaluations missing rank_position
    missing = (await db.execute(
        text("""
            SELECT COUNT(*) FROM core.evaluation_assignment
            WHERE ipr_id = :id AND deleted_at IS NULL
              AND completed_at IS NOT NULL AND rank_position IS NULL
        """),
        {"id": str(ipr_id)},
    )).scalar() or 0

    if missing > 0:
        return {
            "name": "ranking_persistence",
            "met": True,  # Informational — never blocks
            "detail": (
                f"Mecanismo competitivo ({row['mechanism_code']}): "
                f"{missing} evaluación(es) completada(s) sin ranking asignado. "
                f"Registre rank_position/rank_total para trazabilidad."
            ),
        }

    return None  # All good — no warning needed


# SLA constants for moroso check (same as dgi_data.py, defined locally to avoid circular import)
_MOROSO_SLA_DAYS = {"EN_REVISION_RTF": 7, "EN_REVISION_UCR": 2}


async def _check_morosos_sisrec(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """HΩ-10: Block SUBV8 funds if executor has overdue renditions on any IPR."""
    row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code, i.executor_id
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not row or row["mechanism_code"] != "SUBV8":
        return None
    if not row["executor_id"]:
        return None  # No executor — skip silently

    executor_id = str(row["executor_id"])

    # Find overdue renditions for this executor across ALL IPRs
    overdue = (await db.execute(
        text("""
            SELECT COUNT(*) FROM core.rendition r
            JOIN ref.category st ON st.id = r.state_id
            JOIN core.ipr i2 ON i2.id = r.ipr_id
            WHERE i2.executor_id = CAST(:executor_id AS uuid)
              AND r.deleted_at IS NULL
              AND st.scheme = 'rendition_state'
              AND (
                  (st.code = 'EN_REVISION_RTF' AND COALESCE(r.phase_entered_at, r.updated_at) < NOW() - INTERVAL '7 days')
                  OR
                  (st.code = 'EN_REVISION_UCR' AND COALESCE(r.phase_entered_at, r.updated_at) < NOW() - INTERVAL '2 days')
              )
        """),
        {"executor_id": executor_id},
    )).scalar() or 0

    if overdue > 0:
        # Get executor name for detail message
        org_row = (await db.execute(
            text("SELECT short_name FROM core.organization WHERE id = CAST(:id AS uuid)"),
            {"id": executor_id},
        )).mappings().first()
        org_name = org_row["short_name"] if org_row else "desconocida"
        return {
            "name": "morosos_sisrec",
            "met": False,
            "detail": (
                f"SUBV8: entidad ejecutora '{org_name}' tiene {overdue} rendición(es) vencida(s) "
                f"(SLA: RTF {_MOROSO_SLA_DAYS['EN_REVISION_RTF']}d, UCR {_MOROSO_SLA_DAYS['EN_REVISION_UCR']}d). "
                f"Bloqueo total de fondos hasta regularización."
            ),
        }

    return None  # No overdue renditions — gate passes silently


async def _check_kinship_declarations(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """HΩ-02: SUBV8 requires kinship declarations from evaluators/legal reps."""
    row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not row or row["mechanism_code"] != "SUBV8":
        return None

    # Check declarations exist and none declare conflict
    decls = (await db.execute(
        text("""
            SELECT declares_no_conflict
            FROM core.kinship_declaration
            WHERE ipr_id = :id AND deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().all()

    if not decls:
        return {
            "name": "kinship_declarations",
            "met": False,
            "detail": (
                "SUBV8: requiere al menos una declaración jurada de parentesco. "
                "Registre las declaraciones de evaluadores y/o representantes legales "
                "en la pestaña Parentesco del IPR."
            ),
        }

    conflicts = [d for d in decls if not d["declares_no_conflict"]]
    if conflicts:
        return {
            "name": "kinship_declarations",
            "met": False,
            "detail": (
                f"SUBV8: {len(conflicts)} declaración(es) de parentesco declara(n) conflicto "
                f"con autoridades GORE. Inhabilidad por consanguinidad/afinidad."
            ),
        }

    return None  # All declarations are clean — silent pass


async def _check_admissibility_checklist(ipr_id: str, db) -> dict:
    """Check if all required admissibility items are verified for this IPR."""
    row = (await db.execute(text("""
        SELECT COUNT(*) FILTER (WHERE ac.id IS NULL AND ai.is_required) AS pending,
               COUNT(*) AS total
        FROM core.admissibility_item ai
        LEFT JOIN core.admissibility_check ac ON ac.item_id = ai.id AND ac.ipr_id = CAST(:ipr_id AS uuid)
        WHERE ai.financing_track_id = (
            SELECT ft.id FROM core.financing_track ft
            JOIN ref.category m ON m.code = ft.code
            JOIN core.ipr i ON i.mechanism_id = m.id
            WHERE i.id = CAST(:ipr_id AS uuid)
        )
          AND ai.deleted_at IS NULL
    """), {"ipr_id": ipr_id})).first()

    pending = row[0] if row else 0
    total = row[1] if row else 0
    # No items configured for this track → pass (admin must create items to enforce checklist)
    if total == 0:
        return {"name": "checklist_complete", "met": True, "detail": "Sin ítems de admisibilidad configurados para este track"}
    if pending > 0:
        return {"name": "checklist_complete", "met": False, "detail": f"Checklist incompleto: {pending} ítem(s) requerido(s) pendiente(s) de verificación"}
    return {"name": "checklist_complete", "met": True, "detail": f"Checklist completo: {total} ítem(s) verificados"}


async def _evaluate_phase_gates(
    ipr_id: UUID, current_phase: str, target_phase: str, db: AsyncSession
) -> list[dict]:
    """Evaluate gates for a fiber boundary crossing."""
    gates: list[dict] = []
    transition = f"{current_phase}->{target_phase}"

    if transition == "F0->F1":
        row = (await db.execute(
            text("SELECT mechanism_id FROM core.ipr WHERE id = :id"),
            {"id": str(ipr_id)},
        )).mappings().first()
        has_mechanism = row and row["mechanism_id"] is not None
        gates.append({
            "name": "mechanism_required",
            "met": has_mechanism,
            "detail": "IPR requiere mecanismo de financiamiento asignado",
        })

        # HΩ-09: Max 5 FRIL per territory per fiscal year
        fril_max = await _check_fril_max_per_comuna(ipr_id, db)
        if fril_max is not None:
            gates.append(fril_max)

    elif transition == "F1->F2":
        # Informational gate: IPRs <=5.000 UTM may be exempt from RATE/SNI evaluation
        rate_check = await _check_utm_threshold(ipr_id, "RATE_EXENCION", db)
        if rate_check is None:
            # Below threshold — informational: could be exempt
            utm = await _get_utm_value(db)
            threshold = await _get_threshold("RATE_EXENCION", db)
            threshold_utm = int(threshold["value_utm"]) if threshold else 5000
            gates.append({
                "name": "rate_exencion",
                "met": True,
                "detail": f"IPR bajo umbral de {threshold_utm:,} UTM — potencialmente exento de evaluación RATE/SNI (informativo)",
            })

        # HΩ-01: FRIL fragmentation detection
        fril_frac = await _check_fril_fraccionamiento(ipr_id, db)
        if fril_frac is not None:
            gates.append(fril_frac)

        # HΩ-07: C33 conservation ratio check
        c33_gate = await _check_c33_conservation(ipr_id, db)
        if c33_gate is not None:
            gates.append(c33_gate)

        # C33 technical certification (blocking)
        c33_cert = await _check_c33_technical_certification(ipr_id, db)
        if c33_cert is not None:
            gates.append(c33_cert)

        # HΩ-11: SNI proporcionalidad levels
        sni_gate = await _check_sni_proporcionalidad(ipr_id, db)
        if sni_gate is not None:
            gates.append(sni_gate)

        # HΩ-06: Glosa 06 single-purpose MML
        glosa06_gate = await _check_glosa06_single_purpose(ipr_id, db)
        if glosa06_gate is not None:
            gates.append(glosa06_gate)

        # Glosa 06: GORE must be direct executor
        glosa06_exec = await _check_glosa06_direct_executor(ipr_id, db)
        if glosa06_exec is not None:
            gates.append(glosa06_exec)

        # HΩ-02: Kinship declarations for SUBV8
        kinship_gate = await _check_kinship_declarations(ipr_id, db)
        if kinship_gate is not None:
            gates.append(kinship_gate)

    elif transition == "F2->F3":
        row = (await db.execute(
            text("""
                SELECT s.code AS status_code, m.code AS mechanism_code
                FROM core.ipr i
                JOIN ref.category s ON s.id = i.status_id
                LEFT JOIN ref.category m ON m.id = i.mechanism_id
                WHERE i.id = :id
            """),
            {"id": str(ipr_id)},
        )).mappings().first()
        current_status = row["status_code"] if row else None
        mechanism_code = row["mechanism_code"] if row else None

        # Track-aware: use mechanism-specific favorable products, or universal fallback
        track = await _get_track_config(mechanism_code, db) if mechanism_code else None
        if track:
            favorable_set = set(track["favorable_products"])
            track_label = track["label"]
        else:
            favorable_set = _UNIVERSAL_FAVORABLE
            track_label = "universal (sin mecanismo)"

        favorable = current_status in favorable_set
        gates.append({
            "name": "favorable_outcome",
            "met": favorable,
            "detail": (
                f"Dictamen debe ser favorable para avanzar a priorización "
                f"(actual: {current_status}, track: {track_label}, "
                f"productos válidos: {', '.join(sorted(favorable_set))})"
            ),
        })

        # Track-specific amount gates for F2→F3
        track_gates = await _check_track_amount_gates(ipr_id, mechanism_code, "F2->F3", db)
        gates.extend(track_gates)

        # Informational: evaluation SLA check
        eval_sla = await _check_evaluation_sla(ipr_id, db)
        if eval_sla is not None:
            gates.append(eval_sla)

        # Informational: Gobernador delegation
        deleg_gate = await _check_gobernador_delegation(ipr_id, db)
        if deleg_gate is not None:
            gates.append(deleg_gate)

        # HΩ-12: Evaluation type match warning
        eval_match = await _check_evaluation_type_match(ipr_id, db)
        if eval_match is not None:
            gates.append(eval_match)

        # HΩ-13: Ranking persistence warning for competitive mechanisms
        ranking_gate = await _check_ranking_persistence(ipr_id, db)
        if ranking_gate is not None:
            gates.append(ranking_gate)

        # HΩ-03: Pagaré notarial for SUBV8
        pagare_gate = await _check_pagare_notarial(ipr_id, db)
        if pagare_gate is not None:
            gates.append(pagare_gate)

        # HΩ-04: Directorio certificate for SUBV8
        dir_gate = await _check_directorio_certificate(ipr_id, db)
        if dir_gate is not None:
            gates.append(dir_gate)

    elif transition == "F3->F4":
        cnt = (await db.execute(
            text("SELECT COUNT(*) FROM core.budget_commitment WHERE ipr_id = :id AND deleted_at IS NULL"),
            {"id": str(ipr_id)},
        )).scalar() or 0
        gates.append({
            "name": "cdp_exists",
            "met": cnt > 0,
            "detail": f"Requiere al menos 1 CDP vinculado ({cnt} encontrado(s))",
        })

        # Load track for CORE approval override + track-specific gates
        mech_row = (await db.execute(
            text("""
                SELECT m.code AS mechanism_code FROM core.ipr i
                LEFT JOIN ref.category m ON m.id = i.mechanism_id
                WHERE i.id = :id
            """),
            {"id": str(ipr_id)},
        )).mappings().first()
        f34_mechanism = mech_row["mechanism_code"] if mech_row else None
        f34_track = await _get_track_config(f34_mechanism, db) if f34_mechanism else None

        # CORE approval gate: use track override if available, else universal threshold
        core_override = None
        if f34_track and "core_approval" in f34_track.get("thresholds", {}):
            core_override = int(f34_track["thresholds"]["core_approval"])
        core_gate = await _check_core_approval(ipr_id, db, threshold_utm_override=core_override)
        if core_gate is not None:
            gates.append(core_gate)

        # Glosa rules: check budget composition limits
        glosa_gates = await check_glosa_rules(ipr_id, db)
        gates.extend(glosa_gates)

        # Glosa 07: TRANSFER mechanism — admin/honorarios 5% caps
        glosa07_gates = await check_glosa07_transfer_limits(ipr_id, db)
        gates.extend(glosa07_gates)

        # Track-specific gates for F3→F4
        track_gates_f34 = await _check_track_amount_gates(ipr_id, f34_mechanism, "F3->F4", db)
        gates.extend(track_gates_f34)

        # HΩ-05: RS evaluation validity check
        rs_gate = await _check_rs_vigencia(ipr_id, db)
        if rs_gate is not None:
            gates.append(rs_gate)

        # HΩ-08: FRIL tender deadline check
        fril_tender = await _check_fril_tender_deadline(ipr_id, db)
        if fril_tender is not None:
            gates.append(fril_tender)

        # HΩ-10: Morosos SISREC — entity-scoped overdue renditions
        morosos_gate = await _check_morosos_sisrec(ipr_id, db)
        if morosos_gate is not None:
            gates.append(morosos_gate)

        # FRIL vigencia 90d (blocking)
        fril_vig = await _check_fril_vigencia_90d(ipr_id, db)
        if fril_vig is not None:
            gates.append(fril_vig)

    elif transition == "F4->F5":
        pending = (await db.execute(
            text("""
                SELECT COUNT(*) FROM core.rendition r
                JOIN ref.category st ON st.id = r.state_id
                WHERE r.ipr_id = :id AND r.deleted_at IS NULL
                  AND st.scheme = 'rendition_state'
                  AND st.code NOT IN ('APROBADA', 'RECHAZADA')
            """),
            {"id": str(ipr_id)},
        )).scalar() or 0
        gates.append({
            "name": "renditions_clear",
            "met": pending == 0,
            "detail": f"Todas las rendiciones deben estar aprobadas/rechazadas ({pending} pendiente(s))",
        })

        open_probs = (await db.execute(
            text("""
                SELECT COUNT(*) FROM core.ipr_problem ip
                JOIN ref.category ps ON ps.id = ip.state_id
                WHERE ip.ipr_id = :id AND ip.deleted_at IS NULL
                  AND ps.code IN ('ABIERTO', 'EN_GESTION')
            """),
            {"id": str(ipr_id)},
        )).scalar() or 0
        gates.append({
            "name": "problems_clear",
            "met": open_probs == 0,
            "detail": f"No debe haber problemas abiertos ({open_probs} encontrado(s))",
        })

        # Track-specific gates for F4→F5
        mech_row_f45 = (await db.execute(
            text("""
                SELECT m.code AS mechanism_code FROM core.ipr i
                LEFT JOIN ref.category m ON m.id = i.mechanism_id
                WHERE i.id = :id
            """),
            {"id": str(ipr_id)},
        )).mappings().first()
        f45_mechanism = mech_row_f45["mechanism_code"] if mech_row_f45 else None
        track_gates_f45 = await _check_track_amount_gates(ipr_id, f45_mechanism, "F4->F5", db)
        gates.extend(track_gates_f45)

        # HΩ-10: Morosos SISREC — entity-scoped overdue renditions (also at F4→F5)
        morosos_gate_f45 = await _check_morosos_sisrec(ipr_id, db)
        if morosos_gate_f45 is not None:
            gates.append(morosos_gate_f45)

        # Informational: pending modifications
        pending_mods = (await db.execute(
            text("""
                SELECT COUNT(*) FROM core.ipr_modification m
                JOIN ref.category ms ON ms.id = m.status_id
                WHERE m.ipr_id = :id AND m.deleted_at IS NULL
                  AND ms.code IN ('SOLICITADA', 'EN_REVISION')
            """),
            {"id": str(ipr_id)},
        )).scalar() or 0
        if pending_mods > 0:
            gates.append({
                "name": "pending_modifications",
                "met": True,
                "detail": f"Advertencia: {pending_mods} modificación(es) pendiente(s) de resolución (informativo)",
            })

        # Informational: report periodicity compliance
        report_gate = await _check_report_periodicity(ipr_id, db)
        if report_gate is not None:
            gates.append(report_gate)

        # Informational: supervisor GORE assigned (PROYECTO only)
        sup_gate = await _check_supervisor_gore_assigned(ipr_id, db)
        if sup_gate is not None:
            gates.append(sup_gate)

    return gates


async def _check_report_periodicity(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """Check if progress reports are overdue per financing track SLA."""
    row = (await db.execute(
        text("""
            SELECT ft.sla_days, ft.label AS track_label
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            LEFT JOIN core.financing_track ft ON ft.code = m.code AND ft.is_active = TRUE
            WHERE i.id = :id
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not row or not row["sla_days"]:
        return None
    sla_days = row["sla_days"]
    freq = sla_days.get("report_frequency_days")
    if not freq:
        return None

    # Get last report date
    last_report = (await db.execute(
        text("""
            SELECT MAX(report_date) AS last_date
            FROM core.progress_report
            WHERE ipr_id = :id AND deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    last_date = last_report["last_date"] if last_report else None

    if last_date is None:
        return {
            "name": "report_periodicity",
            "met": True,
            "detail": f"Advertencia: sin informes de avance registrados. Periodicidad requerida: cada {freq} días ({row['track_label']}) (informativo)",
        }

    from datetime import date as dt_date
    today = dt_date.today()
    days_since = (today - last_date).days if isinstance(last_date, dt_date) else 0
    overdue = days_since > freq
    return {
        "name": "report_periodicity",
        "met": True,
        "detail": (
            f"{'Advertencia: informe de avance vencido' if overdue else 'Periodicidad OK'}: "
            f"último informe hace {days_since} días, frecuencia {freq}d ({row['track_label']}) (informativo)"
        ),
    }


async def _check_evaluation_sla(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """Informational: check if IPR evaluation duration exceeds track SLA."""
    row = (await db.execute(
        text("""
            SELECT i.phase_entered_at, ft.sla_days, ft.label AS track_label,
                   s.code AS status_code
            FROM core.ipr i
            JOIN ref.category s ON s.id = i.status_id
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            LEFT JOIN core.financing_track ft ON ft.code = m.code AND ft.is_active = TRUE
            WHERE i.id = :id
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not row or not row["sla_days"] or not row["phase_entered_at"]:
        return None
    max_days = row["sla_days"].get("evaluation_max_days")
    if not max_days:
        return None
    # Only relevant if currently in evaluation phase
    if row["status_code"] not in ("EN_EVALUACION", "RS", "FI", "FC", "OT", "AD", "RF", "ITF", "AT"):
        return None
    from datetime import datetime, timezone
    entered = row["phase_entered_at"]
    if entered.tzinfo is None:
        entered = entered.replace(tzinfo=timezone.utc)
    days_in = (datetime.now(timezone.utc) - entered).days
    overdue = days_in > max_days
    return {
        "name": "evaluation_sla",
        "met": True,
        "detail": (
            f"{'Advertencia: evaluación excede plazo SLA' if overdue else 'SLA evaluación OK'}: "
            f"{days_in} días (máx {max_days}d, track: {row['track_label']}) (informativo)"
        ),
    }


async def _check_gobernador_delegation(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """Informational: check if IPR amount triggers CORE approval or Gobernador delegation."""
    row = (await db.execute(
        text("""
            SELECT i.metadata->>'monto_total' AS monto
            FROM core.ipr i WHERE i.id = :id
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not row or not row["monto"]:
        return None
    try:
        monto = float(row["monto"])
    except (ValueError, TypeError):
        return None
    utm = await _get_utm_value(db)
    threshold = await _get_threshold("CORE_UTM", db)
    core_utm = int(threshold["value_utm"]) if threshold else 7000
    monto_utm = monto / utm if utm > 0 else 0
    if monto_utm > core_utm:
        return {
            "name": "gobernador_delegation",
            "met": True,
            "detail": f"Monto {monto_utm:,.0f} UTM > {core_utm:,} UTM: requiere sesión CORE (informativo)",
        }
    return {
        "name": "gobernador_delegation",
        "met": True,
        "detail": f"Monto {monto_utm:,.0f} UTM ≤ {core_utm:,} UTM: aprobación delegada al Gobernador (informativo)",
    }


async def _check_fril_vigencia_90d(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """FRIL vigencia: evaluation result valid for 90 days (per FRIL guide).

    Only fires for FRIL mechanism. Reads rs_validity_days from sla_days.
    Blocking at F3→F4.
    """
    row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code, ft.sla_days
            FROM core.ipr i
            JOIN ref.category m ON m.id = i.mechanism_id
            JOIN core.financing_track ft ON ft.code = m.code AND ft.is_active = TRUE
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not row or row["mechanism_code"] != "FRIL":
        return None

    sla = row["sla_days"] or {}
    validity_days = sla.get("rs_validity_days")
    if not validity_days:
        return None

    # Find most recent completed evaluation
    eval_row = (await db.execute(
        text("""
            SELECT ea.completed_at
            FROM core.evaluation_assignment ea
            WHERE ea.ipr_id = :ipr_id AND ea.deleted_at IS NULL
              AND ea.completed_at IS NOT NULL
            ORDER BY ea.completed_at DESC LIMIT 1
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().first()

    if not eval_row:
        return {
            "name": "fril_vigencia_90d",
            "met": False,
            "detail": "FRIL: sin evaluación completada — se requiere dictamen antes de formalizar",
        }

    from datetime import datetime, timezone
    completed_at = eval_row["completed_at"]
    if completed_at.tzinfo is None:
        completed_at = completed_at.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    expiry = completed_at + timedelta(days=int(validity_days))
    expired = now > expiry
    days_left = (expiry - now).days if not expired else 0

    return {
        "name": "fril_vigencia_90d",
        "met": not expired,
        "detail": (
            f"FRIL: dictamen completado {completed_at.strftime('%Y-%m-%d')} — "
            f"vigencia {validity_days}d {'(expirado, requiere re-evaluación)' if expired else f'({days_left}d restantes)'}"
        ),
    }


async def _check_supervisor_gore_assigned(ipr_id: UUID, db: AsyncSession) -> dict | None:
    """Informational: check if SUPERVISOR_GORE party is assigned during F4 execution."""
    nature = (await db.execute(
        text("SELECT ipr_nature FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(ipr_id)},
    )).scalar()
    if nature != "PROYECTO":
        return None

    count = (await db.execute(
        text("""
            SELECT COUNT(*) FROM core.ipr_party ip
            JOIN ref.category r ON r.id = ip.party_role_id
            WHERE ip.ipr_id = :id AND r.code = 'SUPERVISOR_GORE' AND ip.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).scalar() or 0

    return {
        "name": "supervisor_gore_assigned",
        "met": True,  # informational — never blocks
        "detail": (
            "Supervisor GORE asignado" if count > 0
            else "Advertencia: no se ha asignado Supervisor GORE para seguimiento de ejecución (informativo)"
        ),
    }


def _require_roles(user: dict, *roles: str) -> None:
    if user["role_code"] not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")


@router.get("", response_model=PaginatedResponse)
async def list_iprs(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    ipr_type: Optional[str] = Query(None, description="Filter by ipr_type category code"),
    status: Optional[str] = Query(None, description="Filter by ipr_state category code"),
    sector: Optional[str] = Query(None, description="Filter by investment_sector category code"),
    alert_level: Optional[str] = Query(None, description="Filter by alert_level category code"),
    mechanism: Optional[str] = Query(None, description="Filter by mechanism category code"),
    mcd_phase: Optional[str] = Query(None, description="Filter by mcd_phase category code"),
    search: Optional[str] = Query(None, description="ILIKE search on codigo_bip or name"),
    assignee_id: Optional[UUID] = Query(None, description="Filter by assignee user UUID"),
    sponsor_division_id: Optional[UUID] = Query(None, description="Filter by sponsor division UUID"),
):
    """
    List IPRs with server-side pagination and role-aware filtering.

    - JEFE_DIVISION: restricted to IPRs where sponsor_division_id = user.division_id
    - ANALISTA/RTF/ASESOR_JURIDICO/JEFE_UNIDAD: restricted to IPRs where assignee_id = user.id
    - Admin roles: unrestricted access
    - assignee_id: explicit filter by assigned user (any role)
    - sponsor_division_id: explicit filter by sponsor division (any role)
    """
    role_code = user["role_code"]
    user_id = str(user["id"])
    division_id = str(user["division_id"]) if user.get("division_id") else None

    # Build WHERE conditions
    conditions = ["i.deleted_at IS NULL"]
    params: dict = {}

    # Role-based scope restriction
    if role_code in ("ANALISTA", "RTF", "ASESOR_JURIDICO", "JEFE_UNIDAD"):
        conditions.append("i.assignee_id = :assignee_id")
        params["assignee_id"] = user_id
    elif role_code in ("JEFE_DIVISION", "JEFE_DEPARTAMENTO") and division_id:
        conditions.append("i.sponsor_division_id = :division_id")
        params["division_id"] = division_id

    # Explicit assignee filter (available for all roles, overrides role-based if both set)
    if assignee_id:
        conditions.append("i.assignee_id = :filter_assignee_id")
        params["filter_assignee_id"] = str(assignee_id)

    # Explicit sponsor division filter
    if sponsor_division_id:
        conditions.append("i.sponsor_division_id = :filter_sponsor_division_id")
        params["filter_sponsor_division_id"] = str(sponsor_division_id)

    # Optional category code filters
    if ipr_type:
        conditions.append(
            "i.ipr_type_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_type' AND code = :ipr_type LIMIT 1)"
        )
        params["ipr_type"] = ipr_type

    if status:
        conditions.append(
            "i.status_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_state' AND code = :status LIMIT 1)"
        )
        params["status"] = status

    if sector:
        conditions.append(
            "i.investment_sector_id = (SELECT id FROM ref.category WHERE scheme = 'investment_sector' AND code = :sector LIMIT 1)"
        )
        params["sector"] = sector

    if alert_level:
        conditions.append(
            "i.alert_level_id = (SELECT id FROM ref.category WHERE scheme = 'alert_level' AND code = :alert_level LIMIT 1)"
        )
        params["alert_level"] = alert_level

    if mechanism:
        conditions.append(
            "i.mechanism_id = (SELECT id FROM ref.category WHERE scheme = 'mechanism' AND code = :mechanism LIMIT 1)"
        )
        params["mechanism"] = mechanism

    if mcd_phase:
        conditions.append(
            "i.mcd_phase_id = (SELECT id FROM ref.category WHERE scheme = 'mcd_phase' AND code = :mcd_phase LIMIT 1)"
        )
        params["mcd_phase"] = mcd_phase

    if search:
        conditions.append(
            "(i.codigo_bip ILIKE :search OR i.name ILIKE :search)"
        )
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions)

    # Count query
    count_sql = text(f"""
        SELECT COUNT(*) AS total
        FROM core.ipr i
        WHERE {where_clause}
    """)

    count_result = await db.execute(count_sql, params)
    total = count_result.scalar() or 0

    total_pages = math.ceil(total / page_size) if total > 0 else 0
    offset = (page - 1) * page_size

    # Data query
    data_sql = text(f"""
        SELECT
            i.id,
            i.codigo_bip,
            i.name,
            ct.code        AS ipr_type,
            st.code        AS status,
            sec.code       AS investment_sector,
            fs.code        AS funding_source,
            mech.code      AS mechanism,
            mcd.code       AS mcd_phase,
            al.code        AS alert_level,
            i.has_open_problems,
            exc.name       AS executor_name,
            COALESCE(
                CASE
                    WHEN i.metadata IS NOT NULL AND i.metadata->>'monto_total' IS NOT NULL
                         AND i.metadata->>'monto_total' != ''
                    THEN (i.metadata->>'monto_total')::float
                END,
                (SELECT SUM(bc.amount)::float FROM core.budget_commitment bc
                 WHERE bc.ipr_id = i.id AND bc.deleted_at IS NULL)
            )              AS total_budget,
            assignee_div.short_name AS assignee_division_abbr,
            sponsor_div.short_name  AS sponsor_division_abbr,
            i.phase_entered_at
        FROM core.ipr i
        LEFT JOIN ref.category  ct   ON ct.id   = i.ipr_type_id
        LEFT JOIN ref.category  st   ON st.id   = i.status_id
        LEFT JOIN ref.category  sec  ON sec.id  = i.investment_sector_id
        LEFT JOIN ref.category  fs   ON fs.id   = i.funding_source_id
        LEFT JOIN ref.category  mech ON mech.id = i.mechanism_id
        LEFT JOIN ref.category  mcd  ON mcd.id  = i.mcd_phase_id
        LEFT JOIN ref.category  al   ON al.id   = i.alert_level_id
        LEFT JOIN core.organization exc ON exc.id = i.executor_id
        LEFT JOIN core."user" assignee_u ON assignee_u.id = i.assignee_id
        LEFT JOIN core.organization assignee_div ON assignee_div.id = assignee_u.division_id
        LEFT JOIN core.organization sponsor_div ON sponsor_div.id = i.sponsor_division_id
        WHERE {where_clause}
        ORDER BY
            i.alert_level_id DESC NULLS LAST,
            i.codigo_bip ASC
        LIMIT :limit OFFSET :offset
    """)

    params["limit"] = page_size
    params["offset"] = offset

    data_result = await db.execute(data_sql, params)
    rows = data_result.mappings().all()

    items = []
    for row in rows:
        actor_entry = STATUS_ACTOR_MAP.get(row["status"] or "")
        actor_role = None
        actor_action = None
        if actor_entry and actor_entry[0]:
            role_code, source, action = actor_entry
            base_label = _ROLE_LABELS.get(role_code, role_code)
            div_abbr = row["assignee_division_abbr"] if source == "assignee" else (
                row["sponsor_division_abbr"] if source == "division" else None
            )
            actor_role = f"{base_label} {div_abbr}" if div_abbr else base_label
            actor_action = action
        elif actor_entry:
            actor_action = actor_entry[2]
        items.append(IPRListItem(
            id=row["id"],
            codigo_bip=row["codigo_bip"],
            name=row["name"],
            ipr_type=row["ipr_type"],
            status=row["status"],
            investment_sector=row["investment_sector"],
            funding_source=row["funding_source"],
            mechanism=row["mechanism"],
            mcd_phase=row["mcd_phase"],
            alert_level=row["alert_level"],
            has_open_problems=row["has_open_problems"] or False,
            executor_name=row["executor_name"],
            total_budget=row["total_budget"],
            actor_role=actor_role,
            actor_action=actor_action,
            phase_entered_at=row["phase_entered_at"],
        ))

    return PaginatedResponse(
        items=[item.model_dump() for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


# ---------------------------------------------------------------------------
# GET /api/ipr/mis-formulaciones — ANALISTA pipeline F0-F2
# ---------------------------------------------------------------------------

@router.get("/mis-formulaciones")
async def get_mis_formulaciones(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """IPRs assigned to current user in F0-F2 with satellite completeness."""
    from app.schemas.ipr import FormulacionIPR, MisFormulacionesResponse

    user_id = str(user["id"])

    sql = text("""
        SELECT i.id, i.codigo_bip, i.name,
               mcd.code AS phase,
               COALESCE(EXTRACT(DAY FROM NOW() - i.phase_entered_at)::int, 0) AS days_in_phase,
               i.mechanism_id IS NOT NULL AS has_mechanism,
               (SELECT COUNT(*) FROM core.ipr_party WHERE ipr_id = i.id AND deleted_at IS NULL) AS partes_count,
               (SELECT COUNT(*) FROM core.ipr_territory WHERE ipr_id = i.id AND deleted_at IS NULL) AS territorio_count,
               (SELECT COUNT(*) FROM core.ipr_milestone WHERE ipr_id = i.id AND deleted_at IS NULL) AS hitos_count,
               (SELECT COUNT(*) FROM core.evaluation_assignment WHERE ipr_id = i.id AND deleted_at IS NULL) AS evaluaciones_count,
               (SELECT COUNT(*) FROM core.evaluation_assignment WHERE ipr_id = i.id AND deleted_at IS NULL AND result_id IS NOT NULL) AS eval_with_result,
               (SELECT COUNT(*) FROM core.admissibility_check WHERE ipr_id = i.id) AS admisibilidad_total,
               (SELECT COUNT(*) FROM core.admissibility_check WHERE ipr_id = i.id AND verified_at IS NOT NULL) AS admisibilidad_verified
        FROM core.ipr i
        JOIN ref.category sc ON sc.id = i.status_id
        LEFT JOIN ref.category mcd ON mcd.id = i.mcd_phase_id
        WHERE i.assignee_id = :uid
          AND i.deleted_at IS NULL
          AND mcd.code IN ('F0', 'F1', 'F2')
          AND sc.code NOT IN ('ANULADO', 'TERMINADO_ANTICIPADAMENTE', 'INADMISIBLE')
        ORDER BY mcd.code, i.phase_entered_at ASC
    """)
    rows = (await db.execute(sql, {"uid": user_id})).mappings().all()

    by_phase: dict[str, list[FormulacionIPR]] = {"F0": [], "F1": [], "F2": []}
    for r in rows:
        phase = r["phase"] or "F0"
        if phase == "F0":
            missing = []
            if not r["has_mechanism"]:
                missing.append("mecanismo")
            if r["partes_count"] == 0:
                missing.append("partes")
            if r["territorio_count"] == 0:
                missing.append("territorio")
            if r["hitos_count"] == 0:
                missing.append("hitos")
            if missing:
                action = f"Completar {', '.join(missing)} para avanzar a F1"
                tab = missing[0]
            else:
                action = "Lista para avanzar a F1"
                tab = "compromisos"
        elif phase == "F1":
            total_adm = r["admisibilidad_total"]
            verified = r["admisibilidad_verified"]
            if total_adm > 0 and verified < total_adm:
                action = f"Verificar {total_adm - verified} items de admisibilidad pendientes"
                tab = "admisibilidad"
            elif total_adm == 0:
                action = "Sin items de admisibilidad configurados"
                tab = "admisibilidad"
            else:
                action = "Admisibilidad completa — lista para avanzar a F2"
                tab = "compromisos"
        else:
            if r["evaluaciones_count"] == 0:
                action = "Asignar evaluador según mecanismo"
                tab = "evaluaciones"
            elif r["eval_with_result"] == 0:
                action = "Esperando resultado de evaluación externa"
                tab = "evaluaciones"
            else:
                action = "Evaluación registrada — lista para avanzar a F3"
                tab = "evaluaciones"

        by_phase[phase].append(FormulacionIPR(
            id=str(r["id"]),
            codigo_bip=r["codigo_bip"] or "",
            name=r["name"] or "",
            phase=phase,
            days_in_phase=r["days_in_phase"],
            has_mechanism=bool(r["has_mechanism"]),
            partes_count=r["partes_count"],
            territorio_count=r["territorio_count"],
            hitos_count=r["hitos_count"],
            evaluaciones_count=r["evaluaciones_count"],
            admisibilidad_total=r["admisibilidad_total"],
            admisibilidad_verified=r["admisibilidad_verified"],
            eval_assigned=r["evaluaciones_count"] > 0,
            eval_result=None,
            suggested_action=action,
            suggested_tab=tab,
        ))

    total = sum(len(v) for v in by_phase.values())
    return MisFormulacionesResponse(total=total, by_phase=by_phase)


# ---------------------------------------------------------------------------
# GET /api/ipr/cartera-por-division — Division portfolio with health signals
# ---------------------------------------------------------------------------

@router.get("/cartera-por-division")
async def get_cartera_por_division(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Division portfolio summary with health signals."""
    from app.schemas.ipr import DivisionCarteraItem

    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DGI")

    sql = text("""
        SELECT
            o.id AS division_id,
            o.name AS division_name,
            o.short_name AS abbreviation,
            COUNT(i.id) AS total_iprs,
            COUNT(*) FILTER (WHERE mp.code = 'F0') AS f0,
            COUNT(*) FILTER (WHERE mp.code = 'F1') AS f1,
            COUNT(*) FILTER (WHERE mp.code = 'F2') AS f2,
            COUNT(*) FILTER (WHERE mp.code = 'F3') AS f3,
            COUNT(*) FILTER (WHERE mp.code = 'F4') AS f4,
            COUNT(*) FILTER (WHERE mp.code = 'F5') AS f5,
            COALESCE(
                (SELECT COUNT(*) FROM core.alert a
                 JOIN ref.category sev ON sev.id = a.severity_id
                 WHERE a.subject_type = 'core.ipr'
                 AND a.subject_id IN (SELECT id FROM core.ipr WHERE sponsor_division_id = o.id AND deleted_at IS NULL)
                 AND sev.code = 'CRITICO'
                 AND a.resolved_at IS NULL AND a.deleted_at IS NULL), 0
            ) AS critical_alerts,
            COALESCE(
                (SELECT COUNT(*) FROM core.ipr_problem p
                 JOIN ref.category ps ON ps.id = p.state_id
                 WHERE p.ipr_id IN (SELECT id FROM core.ipr WHERE sponsor_division_id = o.id AND deleted_at IS NULL)
                 AND ps.code = 'ABIERTO'
                 AND p.deleted_at IS NULL), 0
            ) AS open_problems,
            COALESCE(
                (SELECT COUNT(*) FROM core.operational_commitment oc
                 JOIN ref.category cs ON cs.id = oc.state_id
                 WHERE oc.ipr_id IN (SELECT id FROM core.ipr WHERE sponsor_division_id = o.id AND deleted_at IS NULL)
                 AND cs.code NOT IN ('COMPLETADO', 'VERIFICADO', 'CANCELADO')
                 AND oc.due_date < CURRENT_DATE
                 AND oc.deleted_at IS NULL), 0
            ) AS overdue_commitments
        FROM core.organization o
        JOIN ref.category ot ON ot.id = o.org_type_id
        LEFT JOIN core.ipr i ON i.sponsor_division_id = o.id AND i.deleted_at IS NULL
        LEFT JOIN ref.category mp ON mp.id = i.mcd_phase_id
        WHERE ot.code IN ('DIVISION', 'GORE')
        AND o.deleted_at IS NULL
        GROUP BY o.id, o.name, o.short_name
        HAVING COUNT(i.id) > 0
        ORDER BY o.name
    """)

    rows = (await db.execute(sql)).mappings().all()

    results = []
    for r in rows:
        by_phase = {
            "F0": r["f0"], "F1": r["f1"], "F2": r["f2"],
            "F3": r["f3"], "F4": r["f4"], "F5": r["f5"],
        }

        # Health signal
        reasons = []
        signal = "VERDE"

        if r["critical_alerts"] > 0:
            signal = "ROJO"
            reasons.append(f"{r['critical_alerts']} alerta(s) critica(s)")

        total = r["total_iprs"] or 1
        overdue_pct = (r["overdue_commitments"] / total) * 100 if total > 0 else 0
        if overdue_pct > 30:
            signal = "ROJO"
            reasons.append(f"{r['overdue_commitments']} compromisos vencidos ({overdue_pct:.0f}%)")

        if signal == "VERDE" and r["open_problems"] > 5:
            signal = "AMARILLO"
            reasons.append(f"{r['open_problems']} problemas abiertos")

        if not reasons:
            reasons.append("Sin alertas ni problemas criticos")

        results.append(DivisionCarteraItem(
            division_id=str(r["division_id"]),
            division_name=r["division_name"],
            abbreviation=r["abbreviation"],
            total_iprs=r["total_iprs"],
            by_phase=by_phase,
            critical_alerts=r["critical_alerts"],
            open_problems=r["open_problems"],
            overdue_commitments=r["overdue_commitments"],
            health_signal=signal,
            health_reasons=reasons,
        ))

    return results


# ---------------------------------------------------------------------------
# GET /api/ipr/track-summary — Aggregate IPR statistics by financing track
# ---------------------------------------------------------------------------

@router.get("/track-summary")
async def get_track_summary(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Aggregate IPR statistics grouped by financing track (mechanism)."""
    result = await db.execute(
        text("""
            SELECT
                ft.code AS track_code,
                ft.label AS track_label,
                COUNT(i.id) AS total_iprs,
                COUNT(i.id) FILTER (WHERE mcd.code = 'F0') AS f0,
                COUNT(i.id) FILTER (WHERE mcd.code = 'F1') AS f1,
                COUNT(i.id) FILTER (WHERE mcd.code = 'F2') AS f2,
                COUNT(i.id) FILTER (WHERE mcd.code = 'F3') AS f3,
                COUNT(i.id) FILTER (WHERE mcd.code = 'F4') AS f4,
                COUNT(i.id) FILTER (WHERE mcd.code = 'F5') AS f5,
                COUNT(i.id) FILTER (WHERE al.code IN ('CRITICO', 'ALTO')) AS critical_alerts
            FROM core.financing_track ft
            LEFT JOIN ref.category mech ON mech.scheme = 'mechanism' AND mech.code = ft.code
            LEFT JOIN core.ipr i ON i.mechanism_id = mech.id AND i.deleted_at IS NULL
            LEFT JOIN ref.category mcd ON mcd.id = i.mcd_phase_id
            LEFT JOIN ref.category al ON al.id = i.alert_level_id
            WHERE ft.is_active = TRUE
            GROUP BY ft.code, ft.label
            ORDER BY total_iprs DESC
        """)
    )
    rows = result.mappings().all()
    return [
        {
            "track_code": r["track_code"],
            "track_label": r["track_label"],
            "total_iprs": r["total_iprs"],
            "by_phase": {
                "F0": r["f0"], "F1": r["f1"], "F2": r["f2"],
                "F3": r["f3"], "F4": r["f4"], "F5": r["f5"],
            },
            "critical_alerts": r["critical_alerts"],
        }
        for r in rows
    ]


@router.get("/{ipr_id}/track-info", response_model=TrackInfo)
async def get_track_info(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return poly-switch track info for an IPR based on its mechanism."""
    await check_ipr_access(db, user, ipr_id)
    row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code, m.label AS mechanism_label
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="IPR no encontrada")

    mechanism_code = row["mechanism_code"]
    track = await _get_track_config(mechanism_code, db) if mechanism_code else None

    # Fetch mechanism-specific attributes from core.ipr_mechanism
    mechanism_attrs: dict = {}
    if mechanism_code and track:
        mech_row = (await db.execute(
            text("SELECT * FROM core.ipr_mechanism WHERE ipr_id = :id AND deleted_at IS NULL"),
            {"id": str(ipr_id)},
        )).mappings().first()
        if mech_row:
            for attr in track.get("required_attrs", []):
                val = mech_row.get(attr)
                if val is not None:
                    mechanism_attrs[attr] = val

    # Fetch evaluation assignments (table may not exist yet — Wave B migration)
    evaluations: list[dict] = []
    if track:
        try:
            eval_rows = (await db.execute(
                text("""
                    SELECT ea.id, et.code AS evaluator_type, o.short_name AS evaluator_org_name,
                           ea.evaluator_name, ea.assigned_at, ea.deadline_at,
                           ea.completed_at, ea.result_code, r.label AS result_label,
                           ea.observations, ea.numeric_score
                    FROM core.evaluation_assignment ea
                    JOIN ref.category et ON et.id = ea.evaluator_type_id
                    LEFT JOIN core.organization o ON o.id = ea.evaluator_organization_id
                    LEFT JOIN ref.category r ON r.id = ea.result_id
                    WHERE ea.ipr_id = :id AND ea.deleted_at IS NULL
                    ORDER BY ea.assigned_at DESC
                """),
                {"id": str(ipr_id)},
            )).mappings().all()
            evaluations = [dict(e) for e in eval_rows]
        except Exception:
            await db.rollback()
            evaluations = []

    if track:
        return TrackInfo(
            mechanism=mechanism_code,
            mechanism_label=track["label"],
            evaluator=track["evaluator"],
            evaluator_label=track["evaluator_label"],
            favorable_products=track["favorable_products"],
            unfavorable_products=track.get("unfavorable_products", []),
            terminal_negative=track.get("terminal_negative", []),
            thresholds=track.get("thresholds", {}),
            sla_days=track.get("sla_days", {}),
            required_attrs=track.get("required_attrs", []),
            mechanism_attrs=mechanism_attrs,
            evaluations=evaluations,
        )

    return TrackInfo(mechanism=mechanism_code, mechanism_label=row["mechanism_label"])


@router.get("/{ipr_id}", response_model=IPRDetail)
async def get_ipr(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve full IPR detail with all category labels resolved and
    aggregated counts for commitments, problems, and alerts.
    """
    await check_ipr_access(db, user, ipr_id)
    sql = text("""
        SELECT
            i.id,
            i.codigo_bip,
            i.name,
            ct.code         AS ipr_type,
            ct.label        AS ipr_type_label,
            st.code         AS status,
            st.label        AS status_label,
            sec.code        AS investment_sector,
            fs.code         AS funding_source,
            fc.code         AS fund_category,
            fc.label        AS fund_category_label,
            mech.code       AS mechanism,
            mech.label      AS mechanism_label,
            mcd.code        AS mcd_phase,
            mcd.label       AS mcd_phase_label,
            al.code         AS alert_level,
            i.has_open_problems,
            exc.name        AS executor_name,
            frm.name        AS formulator_name,
            i.max_execution_months,
            i.intended_outcome,
            COALESCE(i.requires_cgr, false)    AS requires_cgr,
            COALESCE(i.requires_dipres, false) AS requires_dipres,
            i.created_at,
            i.phase_entered_at,
            i.assignee_id,
            i.sponsor_division_id,
            -- commitment count
            (
                SELECT COUNT(*)
                FROM core.operational_commitment oc
                WHERE oc.ipr_id = i.id AND oc.deleted_at IS NULL
            ) AS commitment_count,
            -- problem count
            (
                SELECT COUNT(*)
                FROM core.ipr_problem ip
                WHERE ip.ipr_id = i.id AND ip.deleted_at IS NULL
            ) AS problem_count,
            -- alert count
            (
                SELECT COUNT(*)
                FROM core.alert a
                WHERE a.subject_type = 'core.ipr'
                  AND a.subject_id = i.id
                  AND a.deleted_at IS NULL
            ) AS alert_count,
            -- agreement count
            (
                SELECT COUNT(*)
                FROM core.agreement ag
                WHERE ag.ipr_id = i.id
                  AND ag.deleted_at IS NULL
            ) AS agreement_count
        FROM core.ipr i
        LEFT JOIN ref.category  ct   ON ct.id   = i.ipr_type_id
        LEFT JOIN ref.category  st   ON st.id   = i.status_id
        LEFT JOIN ref.category  sec  ON sec.id  = i.investment_sector_id
        LEFT JOIN ref.category  fs   ON fs.id   = i.funding_source_id
        LEFT JOIN ref.category  fc   ON fc.id   = i.fund_category_id
        LEFT JOIN ref.category  mech ON mech.id = i.mechanism_id
        LEFT JOIN ref.category  mcd  ON mcd.id  = i.mcd_phase_id
        LEFT JOIN ref.category  al   ON al.id   = i.alert_level_id
        LEFT JOIN core.organization exc ON exc.id = i.executor_id
        LEFT JOIN core.organization frm ON frm.id = i.formulator_id
        WHERE i.id = :ipr_id
          AND i.deleted_at IS NULL
    """)

    result = await db.execute(sql, {"ipr_id": str(ipr_id)})
    row = result.mappings().first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IPR {ipr_id} no encontrado",
        )

    # G15: Resolve current actor
    current_actor = await _resolve_current_actor(
        row["status"] or "",
        str(row["assignee_id"]) if row.get("assignee_id") else None,
        str(row["sponsor_division_id"]) if row.get("sponsor_division_id") else None,
        db,
    )

    return IPRDetail(
        id=row["id"],
        codigo_bip=row["codigo_bip"],
        name=row["name"],
        ipr_type=row["ipr_type"],
        ipr_type_label=row["ipr_type_label"],
        status=row["status"],
        status_label=row["status_label"],
        investment_sector=row["investment_sector"],
        funding_source=row["funding_source"],
        fund_category=row["fund_category"],
        fund_category_label=row["fund_category_label"],
        mechanism=row["mechanism"],
        mechanism_label=row["mechanism_label"],
        mcd_phase=STATUS_PHASE_FIBER.get(row["status"], row["mcd_phase"]),
        mcd_phase_label=row["mcd_phase_label"],
        alert_level=row["alert_level"],
        has_open_problems=row["has_open_problems"] or False,
        executor_name=row["executor_name"],
        formulator_name=row["formulator_name"],
        max_execution_months=row["max_execution_months"],
        intended_outcome=row["intended_outcome"],
        requires_cgr=row["requires_cgr"],
        requires_dipres=row["requires_dipres"],
        commitment_count=row["commitment_count"] or 0,
        problem_count=row["problem_count"] or 0,
        alert_count=row["alert_count"] or 0,
        agreement_count=row["agreement_count"] or 0,
        phase_entered_at=row["phase_entered_at"],
        current_actor=current_actor,
        created_at=row["created_at"],
    )


# ---------------------------------------------------------------------------
# POST /api/ipr — Create IPR
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_ipr(
    body: IprCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a new IPR. Only ADMIN_SISTEMA and ADMIN_REGIONAL."""
    _require_roles(user, *_CREATE_ROLES)

    codigo_bip = body.codigo_bip.strip()
    if not codigo_bip:
        # Auto-generate next BIP code
        await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('ipr_code'))"))
        seq = await db.execute(
            text("SELECT COALESCE(MAX(CAST(SUBSTRING(codigo_bip FROM '[0-9]+$') AS INT)), 0) + 1 FROM core.ipr")
        )
        next_num = seq.scalar() or 1
        codigo_bip = f"IPR-{next_num:05d}"

    # Check uniqueness
    dup = await db.execute(
        text("SELECT id FROM core.ipr WHERE codigo_bip = :code AND deleted_at IS NULL"),
        {"code": codigo_bip},
    )
    if dup.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una IPR con código {codigo_bip}",
        )

    import json as _json
    metadata = _json.dumps({"descripcion": body.description}) if body.description else "{}"

    sql = text("""
        INSERT INTO core.ipr (
            codigo_bip, name, ipr_nature, ipr_type_id, status_id,
            sponsor_division_id, mechanism_id, funding_source_id, mcd_phase_id,
            created_by_id, updated_by_id, metadata
        ) VALUES (
            :codigo_bip, :name, 'PROYECTO', :ipr_type_id, :status_id,
            :sponsor_division_id, :mechanism_id, :funding_source_id, :mcd_phase_id,
            :user_id, :user_id, CAST(:metadata AS jsonb)
        )
        RETURNING id, codigo_bip
    """)

    result = await db.execute(sql, {
        "codigo_bip": codigo_bip,
        "name": body.name,
        "ipr_type_id": str(body.ipr_type_id) if body.ipr_type_id else None,
        "status_id": str(body.status_id) if body.status_id else None,
        "sponsor_division_id": str(body.sponsor_division_id) if body.sponsor_division_id else None,
        "mechanism_id": str(body.mechanism_id) if body.mechanism_id else None,
        "funding_source_id": str(body.funding_source_id) if body.funding_source_id else None,
        "mcd_phase_id": str(body.mcd_phase_id) if body.mcd_phase_id else None,
        "user_id": str(user["id"]),
        "metadata": metadata,
    })
    row = result.mappings().first()
    await record_event(db, "CREACION", "core.ipr", row["id"], user["id"], {"codigo_bip": codigo_bip})
    await db.commit()

    return {"id": str(row["id"]), "codigo_bip": row["codigo_bip"]}


# ---------------------------------------------------------------------------
# PATCH /api/ipr/{id} — Update IPR fields (general edit)
# ---------------------------------------------------------------------------

_IPR_FIELD_ALLOWLIST = {
    "name": "name",
    "ipr_type_id": "ipr_type_id",
    "status_id": "status_id",
    "investment_sector_id": "investment_sector_id",
    "funding_source_id": "funding_source_id",
    "mechanism_id": "mechanism_id",
    "mcd_phase_id": "mcd_phase_id",
    "fund_category_id": "fund_category_id",
    "sponsor_division_id": "sponsor_division_id",
    "assignee_id": "assignee_id",
}

@router.patch("/{ipr_id}")
async def update_ipr(
    ipr_id: UUID,
    body: IprUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update IPR fields. ADMIN_SISTEMA, ADMIN_REGIONAL can edit all fields.
    JEFE_DIVISION can only update assignee_id."""
    _require_roles(user, *_ASSIGN_ROLES)
    await check_ipr_access(db, user, ipr_id)

    # Verify IPR exists
    check = await db.execute(
        text("SELECT id, assignee_id, codigo_bip FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(ipr_id)},
    )
    _ipr_row = check.mappings().first()
    if not _ipr_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IPR no encontrado")

    updates = body.model_dump(exclude_none=True)
    if not updates:
        return {"message": "Sin cambios"}

    # JEFE_DIVISION/JEFE_DEPARTAMENTO: can update assignee_id + status_id
    # (status_id changes are further restricted by boundary permissions below)
    role = user.get("role_code", "")
    if role in ("JEFE_DIVISION", "JEFE_DEPARTAMENTO"):
        _allowed_fields = {"assignee_id", "status_id"}
        updates = {k: v for k, v in updates.items() if k in _allowed_fields}
        if not updates:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permisos para editar estos campos")

    # --- Fiber derivation: auto-compute mcd_phase on status change ---
    _old_status_id = None  # Track for audit event
    _target_status_code = None  # Track for notification
    if "status_id" in updates and updates["status_id"] is not None:
        new_status_id = str(updates["status_id"])

        codes = (await db.execute(
            text("""
                SELECT
                    cur.code AS current_code,
                    nxt.code AS target_code,
                    i.status_id::text AS old_status_id
                FROM core.ipr i
                JOIN ref.category cur ON cur.id = i.status_id
                JOIN ref.category nxt ON nxt.id = CAST(:new_status_id AS uuid)
                WHERE i.id = :id
            """),
            {"id": str(ipr_id), "new_status_id": new_status_id},
        )).mappings().first()

        if codes:
            current_code = codes["current_code"]
            target_code = codes["target_code"]
            _old_status_id = codes["old_status_id"]
            _target_status_code = target_code

            # --- Boundary permission check ---
            boundary_key = _get_boundary_key(current_code, target_code)
            if boundary_key:
                allowed_roles = await _get_transition_roles(boundary_key, ipr_id, db)
                if role not in allowed_roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Rol {role} no tiene permiso para la transición {current_code}→{target_code}",
                    )

            current_phase = STATUS_PHASE_FIBER.get(current_code)
            target_phase = STATUS_PHASE_FIBER.get(target_code)

            # ANULADO / TERMINADO_ANTICIPADAMENTE: preserve current phase, no gates
            if target_code not in ("ANULADO", "TERMINADO_ANTICIPADAMENTE") and current_phase and target_phase and current_phase != target_phase:
                gates = await _evaluate_phase_gates(ipr_id, current_phase, target_phase, db)
                failed = [g for g in gates if not g["met"]]
                if failed:
                    details = "; ".join(g["detail"] for g in failed)
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Gates no cumplidos para {current_phase}\u2192{target_phase}: {details}",
                    )

                # Auto-derive mcd_phase_id
                phase_id = (await db.execute(
                    text("SELECT id FROM ref.category WHERE scheme = 'mcd_phase' AND code = :code"),
                    {"code": target_phase},
                )).scalar()
                if phase_id:
                    updates["mcd_phase_id"] = str(phase_id)

            # Custom gate: PRE_ADMISIBLE → ADMISIBLE (same-phase, not caught by phase gates)
            if current_code == "PRE_ADMISIBLE" and target_code == "ADMISIBLE":
                gate = await _check_admissibility_checklist(str(ipr_id), db)
                if not gate["met"]:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=gate["detail"])

            # Nature-aware gates: bifurcación F4
            if current_code == "EN_FORMALIZACION" and target_code == "EN_LICITACION":
                nature = (await db.execute(
                    text("SELECT ipr_nature FROM core.ipr WHERE id = :id"),
                    {"id": str(ipr_id)},
                )).scalar()
                if nature != "PROYECTO":
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Solo proyectos pueden avanzar a En Licitación",
                    )

            if current_code == "FORMALIZADO" and target_code == "EN_EJECUCION":
                nature = (await db.execute(
                    text("SELECT ipr_nature FROM core.ipr WHERE id = :id"),
                    {"id": str(ipr_id)},
                )).scalar()
                if nature == "PROYECTO":
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Proyectos deben ir a En Licitación, no directamente a Ejecución",
                    )

            # Custom gate: EN_LICITACION → ADJUDICADO requires ITO for PROYECTO
            if current_code == "EN_LICITACION" and target_code == "ADJUDICADO":
                nature = (await db.execute(
                    text("SELECT ipr_nature FROM core.ipr WHERE id = :id"),
                    {"id": str(ipr_id)},
                )).scalar()
                if nature == "PROYECTO":
                    ito_count = (await db.execute(
                        text("""
                            SELECT COUNT(*) FROM core.ipr_party ip
                            JOIN ref.category r ON r.id = ip.party_role_id
                            WHERE ip.ipr_id = :id AND r.code = 'ITO' AND ip.deleted_at IS NULL
                        """),
                        {"id": str(ipr_id)},
                    )).scalar() or 0
                    if ito_count == 0:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="Proyecto requiere ITO (Inspector Técnico de Obra) asignado antes de adjudicar",
                        )

            # Custom gate: EN_CIERRE_ADMINISTRATIVO → CERRADO requires signed closure
            if current_code == "EN_CIERRE_ADMINISTRATIVO" and target_code == "CERRADO":
                closure = (await db.execute(
                    text("""
                        SELECT signed_by_id, signed_at
                        FROM core.ipr_closure
                        WHERE ipr_id = :id
                    """),
                    {"id": str(ipr_id)},
                )).mappings().first()
                if not closure or not closure["signed_by_id"] or not closure["signed_at"]:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Cierre administrativo requiere acta de cierre firmada",
                    )

    set_clauses = []
    params: dict = {"id": str(ipr_id), "user_id": str(user["id"])}
    for field, value in updates.items():
        col = _IPR_FIELD_ALLOWLIST.get(field)
        if col is None:
            continue
        set_clauses.append(f"{col} = :{field}")
        params[field] = str(value) if value is not None else None

    if not set_clauses:
        return {"message": "Sin cambios válidos"}

    set_clauses.append("updated_by_id = :user_id")
    set_clauses.append("updated_at = NOW()")

    sql = text(f"UPDATE core.ipr SET {', '.join(set_clauses)} WHERE id = :id")
    try:
        await db.execute(sql, params)
        # Record audit event for status transitions
        if _old_status_id and "status_id" in updates:
            await record_event(
                db,
                "STATE_TRANSITION",
                "core.ipr",
                ipr_id,
                user["id"],
                {"old_status_id": _old_status_id, "new_status_id": str(updates["status_id"])},
            )
        if _old_status_id is None:
            await record_event(db, "MODIFICACION", "core.ipr", ipr_id, user["id"])
        # --- Notify assignee on status change ---
        if _old_status_id and "status_id" in updates and _ipr_row["assignee_id"]:
            try:
                _codigo = _ipr_row["codigo_bip"] or str(ipr_id)[:8]
                await create_notification(
                    db=db,
                    user_id=_ipr_row["assignee_id"],
                    title=f"IPR {_codigo}: cambio de estado",
                    body=f"Nuevo estado: {_target_status_code}" if _target_status_code else None,
                    category="sistema",
                    entity_type="core.ipr",
                    entity_id=ipr_id,
                    link=f"/ipr/{ipr_id}",
                )
            except Exception:
                pass  # Never break main flow
        await db.commit()
    except DBAPIError as e:
        await db.rollback()
        if "Transición de estado inválida" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e.orig))
        raise

    return {"message": "IPR actualizado exitosamente"}


# ---------------------------------------------------------------------------
# Transition effects helper
# ---------------------------------------------------------------------------

def _compute_transition_effects(current_code: str, target_code: str) -> list[str]:
    """Compute informational effects that will happen after a transition."""
    effects = []

    _EFFECTS_MAP = {
        "EN_RENDICION": "Se habilitará el tab Cierre al completar rendición",
        "EN_CIERRE_ADMINISTRATIVO": "Se habilitará el formulario de cierre administrativo",
        "CERRADO": "La IPR quedará en estado terminal — no se podrán realizar más transiciones",
        "EN_FORMALIZACION": "Se requerirá Convenio Marco para formalizar",
        "EN_LICITACION": "Se requerirá ITO asignado (Partes) para avanzar a Adjudicado",
        "EN_EJECUCION": "Se activará el seguimiento de avances periódicos",
        "EN_OBRA": "Se activará el monitoreo de plazos de obra",
        "ADJUDICADO": "Se habilitará la firma de contrato",
        "CONTRATO_FIRMADO": "Se habilitará el inicio de ejecución/obra",
        "ANULADO": "La IPR quedará anulada permanentemente",
        "TERMINADO_ANTICIPADAMENTE": "La IPR se cerrará anticipadamente",
        "CDP_EMITIDO": "Se habilitará la formalización del proyecto",
        "EN_EVALUACION": "Se asignarán evaluadores según mecanismo de financiamiento",
    }

    if target_code in _EFFECTS_MAP:
        effects.append(_EFFECTS_MAP[target_code])

    # Phase boundary notifications
    _PHASE_MAP = {
        "F0": ["INGRESADO"],
        "F1": ["EN_REVISION", "PRE_ADMISIBLE", "ADMISIBLE", "INADMISIBLE"],
        "F2": ["EN_EVALUACION", "RS", "FI", "FC", "OT", "AD", "RF", "ITF", "AT"],
        "F3": ["CDP_EMITIDO"],
        "F4": ["EN_FORMALIZACION", "FORMALIZADO", "EN_LICITACION", "ADJUDICADO", "CONTRATO_FIRMADO", "EN_EJECUCION", "EN_OBRA", "RECEPCION_PROVISORIA", "RECEPCION_DEFINITIVA", "SUSPENDIDO"],
        "F5": ["EN_RENDICION", "RENDICION_APROBADA", "EN_CIERRE_ADMINISTRATIVO", "CERRADO"],
    }

    current_phase = None
    target_phase = None
    for phase, codes in _PHASE_MAP.items():
        if current_code in codes:
            current_phase = phase
        if target_code in codes:
            target_phase = phase

    if current_phase and target_phase and current_phase != target_phase:
        effects.append(f"Cambio de fase: {current_phase} → {target_phase}")

    return effects


# ---------------------------------------------------------------------------
# GET /api/ipr/{id}/readiness — Satellite counts + gate precheck
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/readiness")
async def get_ipr_readiness(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Satellite counts + gate precheck for next transitions."""
    await check_ipr_access(db, user, ipr_id)
    from app.schemas.ipr import SatelliteStatus, TransitionReadiness, IprReadiness

    # 1. Verify IPR exists
    check = await db.execute(
        text("SELECT id, status_id FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": ipr_id},
    )
    row = check.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="IPR no encontrada")

    # 2. Count satellites via single CTE query
    sat_sql = text("""
        WITH sat AS (
            SELECT
                (SELECT COUNT(*) FROM core.ipr_party WHERE ipr_id = :id AND deleted_at IS NULL) AS partes,
                (SELECT COUNT(*) FROM core.ipr_party WHERE ipr_id = :id AND deleted_at IS NULL
                    AND party_role_id IN (SELECT id FROM ref.category WHERE scheme = 'party_role' AND code = 'ITO')) AS has_ito,
                (SELECT COUNT(*) FROM core.ipr_territory WHERE ipr_id = :id AND deleted_at IS NULL) AS territorio,
                (SELECT COUNT(*) FROM core.ipr_milestone WHERE ipr_id = :id AND deleted_at IS NULL) AS hitos_total,
                (SELECT COUNT(*) FROM core.ipr_milestone WHERE ipr_id = :id AND deleted_at IS NULL AND actual_date IS NOT NULL) AS hitos_completados,
                (SELECT COUNT(*) FROM core.evaluation_assignment WHERE ipr_id = :id AND deleted_at IS NULL) AS evaluaciones,
                (SELECT COUNT(*) FROM core.evaluation_assignment WHERE ipr_id = :id AND deleted_at IS NULL AND result_id IS NOT NULL) AS eval_con_resultado,
                (SELECT COUNT(*) FROM core.operational_commitment WHERE ipr_id = :id AND deleted_at IS NULL) AS compromisos,
                (SELECT COUNT(*) FROM core.operational_commitment oc
                    JOIN ref.category sc ON sc.id = oc.state_id
                    WHERE oc.ipr_id = :id AND oc.deleted_at IS NULL AND sc.code IN ('COMPLETADO', 'VERIFICADO')) AS compromisos_completados,
                (SELECT COUNT(*) FROM core.agreement WHERE ipr_id = :id AND deleted_at IS NULL) AS convenios,
                (SELECT COUNT(*) FROM core.budget_commitment WHERE ipr_id = :id AND deleted_at IS NULL) AS cdps,
                (SELECT COUNT(*) FROM core.progress_report WHERE ipr_id = :id AND deleted_at IS NULL) AS avances,
                (SELECT COUNT(*) FROM core.admissibility_check WHERE ipr_id = :id) AS admisibilidad_total,
                (SELECT COUNT(*) FROM core.admissibility_check WHERE ipr_id = :id AND verified_at IS NOT NULL) AS admisibilidad_verificados
        )
        SELECT * FROM sat
    """)
    sat_row = (await db.execute(sat_sql, {"id": ipr_id})).mappings().first()

    satellites = [
        SatelliteStatus(name="partes", label="Partes", count=sat_row["partes"],
                       detail={"has_ito": sat_row["has_ito"] > 0}),
        SatelliteStatus(name="territorio", label="Territorio", count=sat_row["territorio"]),
        SatelliteStatus(name="hitos", label="Hitos", count=sat_row["hitos_total"],
                       detail={"completados": sat_row["hitos_completados"]}),
        SatelliteStatus(name="evaluaciones", label="Evaluaciones", count=sat_row["evaluaciones"],
                       detail={"con_resultado": sat_row["eval_con_resultado"]}),
        SatelliteStatus(name="compromisos", label="Compromisos", count=sat_row["compromisos"],
                       detail={"completados": sat_row["compromisos_completados"]}),
        SatelliteStatus(name="convenios", label="Convenios", count=sat_row["convenios"]),
        SatelliteStatus(name="cdps", label="CDPs", count=sat_row["cdps"]),
        SatelliteStatus(name="avances", label="Avances", count=sat_row["avances"]),
        SatelliteStatus(name="admisibilidad", label="Admisibilidad", count=sat_row["admisibilidad_total"],
                       detail={"verificados": sat_row["admisibilidad_verificados"]}),
    ]

    # 3. Gate precheck for next transitions
    status_sql = text("""
        SELECT sc.code AS current_code, sc.valid_transitions,
               mcd.code AS current_phase, i.ipr_nature
        FROM core.ipr i
        JOIN ref.category sc ON sc.id = i.status_id
        LEFT JOIN ref.category mcd ON mcd.id = i.mcd_phase_id
        WHERE i.id = :id
    """)
    status_row = (await db.execute(status_sql, {"id": ipr_id})).mappings().first()

    next_transitions = []
    if status_row and status_row["valid_transitions"]:
        valid = status_row["valid_transitions"]
        current_code = status_row["current_code"]
        current_phase = status_row["current_phase"]
        ipr_nature = status_row["ipr_nature"]

        dest_sql = text("""
            SELECT id, code, label
            FROM ref.category
            WHERE scheme = 'ipr_state' AND code = ANY(:codes)
            ORDER BY sort_order
        """)
        dest_rows = (await db.execute(dest_sql, {"codes": valid})).mappings().all()

        for dest in dest_rows:
            target_phase = STATUS_PHASE_FIBER.get(dest["code"])
            phase_change = (
                dest["code"] not in ("ANULADO", "TERMINADO_ANTICIPADAMENTE")
                and current_phase is not None
                and target_phase is not None
                and target_phase != current_phase
            )

            gates: list[dict] = []
            if phase_change:
                gates = await _evaluate_phase_gates(ipr_id, current_phase, target_phase, db)

            # Same-phase custom gates
            if current_code == "PRE_ADMISIBLE" and dest["code"] == "ADMISIBLE":
                gates.append(await _check_admissibility_checklist(str(ipr_id), db))

            if current_code == "EN_LICITACION" and dest["code"] == "ADJUDICADO" and ipr_nature == "PROYECTO":
                ito_count = (await db.execute(
                    text("""
                        SELECT COUNT(*) FROM core.ipr_party ip
                        JOIN ref.category r ON r.id = ip.party_role_id
                        WHERE ip.ipr_id = :id AND r.code = 'ITO' AND ip.deleted_at IS NULL
                    """),
                    {"id": str(ipr_id)},
                )).scalar() or 0
                gates.append({"name": "ito_assigned", "met": ito_count > 0,
                              "detail": "Proyecto requiere ITO asignado" if ito_count == 0 else "ITO asignado"})

            if current_code == "EN_CIERRE_ADMINISTRATIVO" and dest["code"] == "CERRADO":
                closure = (await db.execute(
                    text("SELECT signed_by_id, signed_at FROM core.ipr_closure WHERE ipr_id = :id"),
                    {"id": str(ipr_id)},
                )).mappings().first()
                signed = bool(closure and closure["signed_by_id"] and closure["signed_at"])
                gates.append({"name": "closure_signed", "met": signed,
                              "detail": "Acta de cierre debe estar firmada" if not signed else "Acta de cierre firmada"})

            gates_met = sum(1 for g in gates if g["met"])
            label = _EVAL_LABELS.get(dest["code"], dest["label"])

            next_transitions.append(
                TransitionReadiness(
                    code=dest["code"],
                    label=label,
                    target_phase=target_phase,
                    gates_met=gates_met,
                    gates_total=len(gates),
                    blocking_gates=[g["detail"] for g in gates if not g["met"]],
                )
            )

    return IprReadiness(satellites=satellites, next_transitions=next_transitions)


# ---------------------------------------------------------------------------
# GET /api/ipr/{id}/historial — Transition history from txn.event
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/historial")
async def get_ipr_historial(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Transition history for an IPR from txn.event."""
    await check_ipr_access(db, user, ipr_id)
    # Verify IPR exists
    check = await db.execute(
        text("SELECT id FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": ipr_id},
    )
    if not check.mappings().first():
        raise HTTPException(status_code=404, detail="IPR no encontrada")

    sql = text("""
        SELECT
            e.id::text AS id,
            old_cat.code AS previous_state,
            new_cat.code AS new_state,
            COALESCE(p.names || ' ' || p.paternal_surname, 'Sistema') AS changed_by_name,
            e.data->>'comment' AS comment,
            e.occurred_at AS changed_at
        FROM txn.event e
        LEFT JOIN ref.category old_cat ON old_cat.id = (e.data->>'old_status_id')::uuid
        LEFT JOIN ref.category new_cat ON new_cat.id = (e.data->>'new_status_id')::uuid
        LEFT JOIN core."user" u ON u.id = e.actor_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE e.subject_type = 'core.ipr'
            AND e.subject_id = :ipr_id
            AND e.event_type_id IN (
                SELECT id FROM ref.category WHERE scheme = 'event_type' AND code = 'STATE_TRANSITION'
            )
        ORDER BY e.occurred_at DESC
        LIMIT 50
    """)

    rows = (await db.execute(sql, {"ipr_id": ipr_id})).mappings().all()

    return [
        {
            "id": r["id"],
            "previous_state": r["previous_state"],
            "new_state": r["new_state"],
            "changed_by_name": r["changed_by_name"],
            "comment": r["comment"],
            "changed_at": r["changed_at"].isoformat() if r["changed_at"] else None,
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# GET /api/ipr/{id}/transiciones — Valid next states with gate status
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/transiciones")
async def get_ipr_transitions(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return valid next states for this IPR with gate status per phase boundary."""
    await check_ipr_access(db, user, ipr_id)
    row = (await db.execute(
        text("""
            SELECT st.code AS current_code, st.valid_transitions,
                   mcd.code AS current_phase, i.ipr_nature
            FROM core.ipr i
            JOIN ref.category st ON st.id = i.status_id
            LEFT JOIN ref.category mcd ON mcd.id = i.mcd_phase_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="IPR no encontrado")

    valid_codes = row["valid_transitions"] or []
    current_phase = row["current_phase"]

    if not valid_codes:
        return []

    # Fetch destination state details
    dests = (await db.execute(
        text("""
            SELECT id, code, label FROM ref.category
            WHERE scheme = 'ipr_state' AND code = ANY(:codes)
            ORDER BY sort_order
        """),
        {"codes": valid_codes},
    )).mappings().all()

    current_code = row["current_code"]
    ipr_nature = row["ipr_nature"]

    # Nature-aware transition filter: hide inapplicable transitions
    _NATURE_FILTER = {
        # EN_FORMALIZACION: PROYECTO → EN_LICITACION, no-PROYECTO → FORMALIZADO
        ("EN_FORMALIZACION", "EN_LICITACION"): lambda n: n == "PROYECTO",
        ("EN_FORMALIZACION", "FORMALIZADO"): lambda n: n != "PROYECTO",
        # FORMALIZADO → EN_EJECUCION: solo no-PROYECTO (PROYECTO va por licitación)
        ("FORMALIZADO", "EN_EJECUCION"): lambda n: n != "PROYECTO",
    }

    result = []
    for d in dests:
        # Skip transitions not applicable to this IPR's nature
        nature_check = _NATURE_FILTER.get((current_code, d["code"]))
        if nature_check and not nature_check(ipr_nature):
            continue

        target_phase = STATUS_PHASE_FIBER.get(d["code"])
        phase_change = (
            d["code"] not in ("ANULADO", "TERMINADO_ANTICIPADAMENTE")
            and current_phase is not None
            and target_phase is not None
            and target_phase != current_phase
        )
        gates = []
        if phase_change:
            gates = await _evaluate_phase_gates(ipr_id, current_phase, target_phase, db)

        # Custom gate: PRE_ADMISIBLE → ADMISIBLE (same-phase, not caught by phase gates)
        if current_code == "PRE_ADMISIBLE" and d["code"] == "ADMISIBLE":
            adm_gate = await _check_admissibility_checklist(str(ipr_id), db)
            gates.append(adm_gate)

        # Custom gate: EN_LICITACION → ADJUDICADO requires ITO for PROYECTO
        if current_code == "EN_LICITACION" and d["code"] == "ADJUDICADO":
            if ipr_nature == "PROYECTO":
                ito_count = (await db.execute(
                    text("""
                        SELECT COUNT(*) FROM core.ipr_party ip
                        JOIN ref.category r ON r.id = ip.party_role_id
                        WHERE ip.ipr_id = :id AND r.code = 'ITO' AND ip.deleted_at IS NULL
                    """),
                    {"id": str(ipr_id)},
                )).scalar() or 0
                gates.append({
                    "name": "ito_assigned",
                    "met": ito_count > 0,
                    "detail": "Proyecto requiere ITO asignado" if ito_count == 0 else "ITO asignado",
                })

        # Custom gate: EN_CIERRE_ADMINISTRATIVO → CERRADO requires signed closure
        if current_code == "EN_CIERRE_ADMINISTRATIVO" and d["code"] == "CERRADO":
            closure = (await db.execute(
                text("SELECT signed_by_id, signed_at FROM core.ipr_closure WHERE ipr_id = :id"),
                {"id": str(ipr_id)},
            )).mappings().first()
            signed = bool(closure and closure["signed_by_id"] and closure["signed_at"])
            gates.append({
                "name": "closure_signed",
                "met": signed,
                "detail": "Acta de cierre debe estar firmada" if not signed else "Acta de cierre firmada",
            })

        blocked = any(not g["met"] for g in gates)

        # Role-based permission: check if current user can execute this transition
        user_role = user.get("role_code", "")
        bk = _get_boundary_key(current_code, d["code"])
        if bk:
            allowed_roles = await _get_transition_roles(bk, ipr_id, db)
            role_allowed = user_role in allowed_roles
        else:
            role_allowed = user_role in _ASSIGN_ROLES

        result.append({
            "id": str(d["id"]),
            "code": d["code"],
            "label": _EVAL_LABELS.get(d["code"], d["label"]),
            "target_phase": target_phase,
            "phase_change": phase_change,
            "gates": gates,
            "blocked": blocked,
            "allowed": role_allowed,
            "effects": _compute_transition_effects(current_code, d["code"]),
        })

    return result


# ---------------------------------------------------------------------------
# POST /api/ipr/{id}/avances — Create progress report
# ---------------------------------------------------------------------------

@router.post("/{ipr_id}/avances", status_code=status.HTTP_201_CREATED)
async def create_progress_report(
    ipr_id: UUID,
    body: ProgressReportCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a new progress report for an IPR."""
    _require_roles(user, *WRITE_OPERATIONAL_ROLES)
    await check_ipr_access(db, user, ipr_id)
    # Verify IPR exists
    check = await db.execute(
        text("SELECT id FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(ipr_id)},
    )
    if not check.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IPR no encontrado")

    # Auto-increment report_number
    seq = await db.execute(
        text("SELECT COALESCE(MAX(report_number), 0) + 1 FROM core.progress_report WHERE ipr_id = :ipr_id"),
        {"ipr_id": str(ipr_id)},
    )
    next_number = seq.scalar() or 1

    sql = text("""
        INSERT INTO core.progress_report (
            ipr_id, report_number, report_date,
            physical_progress, financial_progress,
            description, issues_detected,
            reported_by_id, created_by_id, updated_by_id
        ) VALUES (
            :ipr_id, :report_number, :report_date,
            :physical_progress, :financial_progress,
            :description, :issues_detected,
            :user_id, :user_id, :user_id
        )
        RETURNING id, report_number
    """)

    result = await db.execute(sql, {
        "ipr_id": str(ipr_id),
        "report_number": next_number,
        "report_date": body.report_date,
        "physical_progress": body.physical_progress,
        "financial_progress": body.financial_progress,
        "description": body.description,
        "issues_detected": body.issues_detected,
        "user_id": str(user["id"]),
    })
    row = result.mappings().first()
    await record_event(db, "CREACION", "core.progress_report", row["id"], user["id"], {"ipr_id": str(ipr_id)})
    await db.commit()

    return {"id": str(row["id"]), "report_number": row["report_number"]}


# ---------------------------------------------------------------------------
# GET /api/ipr/{id}/avances — List progress reports
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/avances", response_model=list[ProgressReportItem])
async def list_progress_reports(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all progress reports for an IPR, ordered by report_number DESC."""
    await check_ipr_access(db, user, ipr_id)
    sql = text("""
        SELECT
            pr.id,
            pr.report_number,
            pr.report_date,
            pr.physical_progress,
            pr.financial_progress,
            pr.description,
            pr.issues_detected,
            CONCAT(p.names, ' ', p.paternal_surname) AS reported_by_name,
            pr.created_at
        FROM core.progress_report pr
        LEFT JOIN core."user" u ON u.id = pr.reported_by_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE pr.ipr_id = :ipr_id AND pr.deleted_at IS NULL
        ORDER BY pr.report_number DESC
    """)

    result = await db.execute(sql, {"ipr_id": str(ipr_id)})
    rows = result.mappings().all()

    return [
        ProgressReportItem(
            id=row["id"],
            report_number=row["report_number"],
            report_date=row["report_date"],
            physical_progress=float(row["physical_progress"]) if row["physical_progress"] is not None else None,
            financial_progress=float(row["financial_progress"]) if row["financial_progress"] is not None else None,
            description=row["description"],
            issues_detected=row["issues_detected"],
            reported_by_name=row["reported_by_name"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


# ---------------------------------------------------------------------------
# GET /api/ipr/{id}/partes — List parties for an IPR
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/partes", response_model=list[IprPartyItem])
async def list_ipr_parties(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all parties (organizations with roles) for an IPR."""
    await check_ipr_access(db, user, ipr_id)
    sql = text("""
        SELECT ip.id, o.name AS organization_name, o.code AS organization_code,
               c.code AS role_code, c.label AS role_label,
               ip.is_primary, ip.valid_from, ip.valid_to,
               ip.contact_person, ip.contact_email, ip.responsibility_description,
               a.agreement_number
        FROM core.ipr_party ip
        JOIN core.organization o ON o.id = ip.organization_id
        JOIN ref.category c ON c.id = ip.party_role_id
        LEFT JOIN core.agreement a ON a.id = ip.agreement_id
        WHERE ip.ipr_id = :ipr_id AND ip.deleted_at IS NULL
        ORDER BY ip.is_primary DESC, c.label
    """)
    result = await db.execute(sql, {"ipr_id": str(ipr_id)})
    rows = result.mappings().all()
    return [
        IprPartyItem(
            id=row["id"],
            organization_name=row["organization_name"],
            organization_code=row["organization_code"],
            role_code=row["role_code"],
            role_label=row["role_label"],
            is_primary=row["is_primary"] or False,
            valid_from=row["valid_from"],
            valid_to=row["valid_to"],
            contact_person=row["contact_person"],
            contact_email=row["contact_email"],
            responsibility_description=row["responsibility_description"],
            agreement_number=row["agreement_number"],
        )
        for row in rows
    ]


# ---------------------------------------------------------------------------
# POST /api/ipr/{id}/partes — Add a party to an IPR
# ---------------------------------------------------------------------------

@router.post("/{ipr_id}/partes", status_code=status.HTTP_201_CREATED)
async def create_ipr_party(
    ipr_id: UUID,
    body: IprPartyCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Add an organization-role pair to an IPR."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "ANALISTA",
                   "JEFE_DIVISION", "JEFE_DEPARTAMENTO")
    await check_ipr_access(db, user, ipr_id)

    # Verify IPR exists
    check = await db.execute(
        text("SELECT id FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(ipr_id)},
    )
    if not check.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IPR no encontrado")

    sql = text("""
        INSERT INTO core.ipr_party (
            ipr_id, organization_id, party_role_id, agreement_id,
            is_primary, valid_from, valid_to,
            responsibility_description, contact_person, contact_email,
            created_by_id, updated_by_id
        ) VALUES (
            :ipr_id, :organization_id, :party_role_id, :agreement_id,
            :is_primary, :valid_from, :valid_to,
            :responsibility_description, :contact_person, :contact_email,
            :user_id, :user_id
        )
        RETURNING id
    """)
    try:
        result = await db.execute(sql, {
            "ipr_id": str(ipr_id),
            "organization_id": str(body.organization_id),
            "party_role_id": str(body.party_role_id),
            "agreement_id": str(body.agreement_id) if body.agreement_id else None,
            "is_primary": body.is_primary,
            "valid_from": body.valid_from,
            "valid_to": body.valid_to,
            "responsibility_description": body.responsibility_description,
            "contact_person": body.contact_person,
            "contact_email": body.contact_email,
            "user_id": str(user["id"]),
        })
        row = result.mappings().first()
        await record_event(db, "CREACION", "core.ipr_party", row["id"], user["id"], {"ipr_id": str(ipr_id)})
        await db.commit()
        return {"id": str(row["id"])}
    except Exception as e:
        await db.rollback()
        err_str = str(e)
        if "uq_ipr_party_role" in err_str or "ipr_party" in err_str and "unique" in err_str.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta organizacion ya tiene ese rol en este IPR",
            )
        raise


# ---------------------------------------------------------------------------
# DELETE /api/ipr/{id}/partes/{party_id} — Soft-delete a party
# ---------------------------------------------------------------------------

@router.delete("/{ipr_id}/partes/{party_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ipr_party(
    ipr_id: UUID,
    party_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete an IPR party."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "ANALISTA",
                   "JEFE_DIVISION", "JEFE_DEPARTAMENTO")
    await check_ipr_access(db, user, ipr_id)

    result = await db.execute(
        text("""
            UPDATE core.ipr_party
            SET deleted_at = NOW(), updated_by_id = :user_id
            WHERE id = :id AND ipr_id = :ipr_id AND deleted_at IS NULL
        """),
        {"id": str(party_id), "ipr_id": str(ipr_id), "user_id": str(user["id"])},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parte no encontrada")
    await record_event(db, "ELIMINACION", "core.ipr_party", party_id, user["id"], {"ipr_id": str(ipr_id)})
    await db.commit()


# ---------------------------------------------------------------------------
# GET /api/ipr/{id}/territorio — List territories for an IPR
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/territorio", response_model=list[IprTerritoryItem])
async def list_ipr_territories(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all territory associations for an IPR."""
    await check_ipr_access(db, user, ipr_id)
    sql = text("""
        SELECT it.id, t.name AS territory_name, t.code AS territory_code,
               c.code AS impact_type_code, c.label AS impact_type_label,
               it.is_primary, it.notes
        FROM core.ipr_territory it
        JOIN core.territory t ON t.id = it.territory_id
        JOIN ref.category c ON c.id = it.impact_type_id
        WHERE it.ipr_id = :ipr_id AND it.deleted_at IS NULL
        ORDER BY it.is_primary DESC, t.name
    """)
    result = await db.execute(sql, {"ipr_id": str(ipr_id)})
    rows = result.mappings().all()
    return [
        IprTerritoryItem(
            id=row["id"],
            territory_name=row["territory_name"],
            territory_code=row["territory_code"],
            impact_type_code=row["impact_type_code"],
            impact_type_label=row["impact_type_label"],
            is_primary=row["is_primary"] or False,
            notes=row["notes"],
        )
        for row in rows
    ]


# ---------------------------------------------------------------------------
# POST /api/ipr/{id}/territorio — Add a territory to an IPR
# ---------------------------------------------------------------------------

@router.post("/{ipr_id}/territorio", status_code=status.HTTP_201_CREATED)
async def create_ipr_territory(
    ipr_id: UUID,
    body: IprTerritoryCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Associate a territory with an IPR."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "ANALISTA",
                   "JEFE_DIVISION", "JEFE_DEPARTAMENTO")
    await check_ipr_access(db, user, ipr_id)

    check = await db.execute(
        text("SELECT id FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(ipr_id)},
    )
    if not check.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IPR no encontrado")

    sql = text("""
        INSERT INTO core.ipr_territory (
            ipr_id, territory_id, impact_type_id, is_primary, notes,
            created_by_id, updated_by_id
        ) VALUES (
            :ipr_id, :territory_id, :impact_type_id, :is_primary, :notes,
            :user_id, :user_id
        )
        RETURNING id
    """)
    try:
        result = await db.execute(sql, {
            "ipr_id": str(ipr_id),
            "territory_id": str(body.territory_id),
            "impact_type_id": str(body.impact_type_id),
            "is_primary": body.is_primary,
            "notes": body.notes,
            "user_id": str(user["id"]),
        })
        row = result.mappings().first()
        await record_event(db, "CREACION", "core.ipr_territory", row["id"], user["id"], {"ipr_id": str(ipr_id)})
        await db.commit()
        return {"id": str(row["id"])}
    except Exception as e:
        await db.rollback()
        err_str = str(e)
        if "uq_ipr_territory_impact" in err_str or "ipr_territory" in err_str and "unique" in err_str.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este territorio ya tiene ese tipo de impacto en este IPR",
            )
        raise


# ---------------------------------------------------------------------------
# DELETE /api/ipr/{id}/territorio/{record_id} — Soft-delete territory
# ---------------------------------------------------------------------------

@router.delete("/{ipr_id}/territorio/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ipr_territory(
    ipr_id: UUID,
    record_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete an IPR territory association."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "ANALISTA",
                   "JEFE_DIVISION", "JEFE_DEPARTAMENTO")
    await check_ipr_access(db, user, ipr_id)

    result = await db.execute(
        text("""
            UPDATE core.ipr_territory
            SET deleted_at = NOW(), updated_by_id = :user_id
            WHERE id = :id AND ipr_id = :ipr_id AND deleted_at IS NULL
        """),
        {"id": str(record_id), "ipr_id": str(ipr_id), "user_id": str(user["id"])},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Territorio no encontrado")
    await record_event(db, "ELIMINACION", "core.ipr_territory", record_id, user["id"], {"ipr_id": str(ipr_id)})
    await db.commit()


# ---------------------------------------------------------------------------
# GET /api/ipr/{id}/hitos — List milestones for an IPR
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/hitos", response_model=list[IprMilestoneItem])
async def list_ipr_milestones(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all milestones for an IPR, ordered by planned_date."""
    await check_ipr_access(db, user, ipr_id)
    sql = text("""
        SELECT im.id, c.code AS milestone_type_code, c.label AS milestone_type_label,
               im.description, im.planned_date, im.actual_date, im.deviation_days,
               CONCAT(p.names, ' ', p.paternal_surname) AS completed_by_name,
               im.verification_notes, im.created_at
        FROM core.ipr_milestone im
        JOIN ref.category c ON c.id = im.milestone_type_id
        LEFT JOIN core."user" u ON u.id = im.completed_by_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE im.ipr_id = :ipr_id AND im.deleted_at IS NULL
        ORDER BY im.planned_date ASC
    """)
    result = await db.execute(sql, {"ipr_id": str(ipr_id)})
    rows = result.mappings().all()
    return [
        IprMilestoneItem(
            id=row["id"],
            milestone_type_code=row["milestone_type_code"],
            milestone_type_label=row["milestone_type_label"],
            description=row["description"],
            planned_date=row["planned_date"],
            actual_date=row["actual_date"],
            deviation_days=row["deviation_days"],
            completed_by_name=row["completed_by_name"],
            verification_notes=row["verification_notes"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


# ---------------------------------------------------------------------------
# POST /api/ipr/{id}/hitos — Create a milestone
# ---------------------------------------------------------------------------

@router.post("/{ipr_id}/hitos", status_code=status.HTTP_201_CREATED)
async def create_ipr_milestone(
    ipr_id: UUID,
    body: IprMilestoneCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a new milestone for an IPR."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "ANALISTA",
                   "JEFE_DIVISION", "JEFE_DEPARTAMENTO")
    await check_ipr_access(db, user, ipr_id)

    check = await db.execute(
        text("SELECT id FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(ipr_id)},
    )
    if not check.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IPR no encontrado")

    sql = text("""
        INSERT INTO core.ipr_milestone (
            ipr_id, milestone_type_id, description, planned_date,
            created_by_id, updated_by_id
        ) VALUES (
            :ipr_id, :milestone_type_id, :description, :planned_date,
            :user_id, :user_id
        )
        RETURNING id
    """)
    result = await db.execute(sql, {
        "ipr_id": str(ipr_id),
        "milestone_type_id": str(body.milestone_type_id),
        "description": body.description,
        "planned_date": body.planned_date,
        "user_id": str(user["id"]),
    })
    row = result.mappings().first()
    await record_event(db, "CREACION", "core.ipr_milestone", row["id"], user["id"], {"ipr_id": str(ipr_id)})
    await db.commit()
    return {"id": str(row["id"])}


# ---------------------------------------------------------------------------
# PATCH /api/ipr/{id}/hitos/{hito_id} — Mark milestone completed
# ---------------------------------------------------------------------------

@router.patch("/{ipr_id}/hitos/{hito_id}")
async def update_ipr_milestone(
    ipr_id: UUID,
    hito_id: UUID,
    body: IprMilestoneUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update milestone (mark as completed with actual_date). Admin roles only."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "ANALISTA")
    await check_ipr_access(db, user, ipr_id)

    updates = body.model_dump(exclude_none=True)
    if not updates:
        return {"message": "Sin cambios"}

    set_clauses = ["updated_by_id = :user_id", "updated_at = NOW()"]
    params: dict = {
        "id": str(hito_id),
        "ipr_id": str(ipr_id),
        "user_id": str(user["id"]),
    }

    if "actual_date" in updates:
        set_clauses.append("actual_date = :actual_date")
        set_clauses.append("completed_by_id = :user_id")
        params["actual_date"] = updates["actual_date"]

    if "verification_notes" in updates:
        set_clauses.append("verification_notes = :verification_notes")
        params["verification_notes"] = updates["verification_notes"]

    sql = text(f"""
        UPDATE core.ipr_milestone
        SET {', '.join(set_clauses)}
        WHERE id = :id AND ipr_id = :ipr_id AND deleted_at IS NULL
    """)
    result = await db.execute(sql, params)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hito no encontrado")
    await record_event(db, "MODIFICACION", "core.ipr_milestone", hito_id, user["id"], {"ipr_id": str(ipr_id)})
    await db.commit()
    return {"message": "Hito actualizado"}


# ---------------------------------------------------------------------------
# Evaluation Assignments (Poly-Switch Wave B)
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/evaluaciones", response_model=list[EvaluationAssignmentItem])
async def list_evaluations(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List evaluation assignments for an IPR."""
    await check_ipr_access(db, user, ipr_id)
    rows = (await db.execute(
        text("""
            SELECT ea.id, ea.ipr_id,
                   et.code AS evaluator_type, et.label AS evaluator_type_label,
                   o.short_name AS evaluator_org_name,
                   ea.evaluator_name, ea.assigned_at, ea.deadline_at,
                   ea.completed_at, ea.result_code,
                   r.label AS result_label, ea.observations,
                   ea.numeric_score,
                   ea.rank_position, ea.rank_total, ea.convocatoria_code
            FROM core.evaluation_assignment ea
            JOIN ref.category et ON et.id = ea.evaluator_type_id
            LEFT JOIN core.organization o ON o.id = ea.evaluator_organization_id
            LEFT JOIN ref.category r ON r.id = ea.result_id
            WHERE ea.ipr_id = :ipr_id AND ea.deleted_at IS NULL
            ORDER BY ea.assigned_at DESC
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().all()
    return [EvaluationAssignmentItem(**dict(r)) for r in rows]


@router.post("/{ipr_id}/evaluaciones", status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    ipr_id: UUID,
    body: EvaluationAssignmentCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create an evaluation assignment. Auto-assigns evaluator_type from financing_track DB if omitted."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "ANALISTA",
                   "JEFE_DIVISION", "JEFE_DEPARTAMENTO")
    await check_ipr_access(db, user, ipr_id)

    # Verify IPR exists
    ipr_row = (await db.execute(
        text("""
            SELECT i.id, m.code AS mechanism_code
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not ipr_row:
        raise HTTPException(status_code=404, detail="IPR no encontrada")

    # Auto-assign evaluator_type from financing_track DB if not provided
    evaluator_type_id = body.evaluator_type_id
    if not evaluator_type_id:
        mechanism_code = ipr_row["mechanism_code"]
        evaluator_code = None

        # SNI override: determine evaluator from sni_level_config based on monto
        if mechanism_code == "SNI":
            monto = await _get_ipr_monto(ipr_id, db)
            utm = await _get_utm_value(db)
            monto_utm = monto / utm if utm > 0 else 0
            level_row = (await db.execute(
                text("""
                    SELECT evaluator_code FROM core.sni_level_config
                    WHERE is_active = TRUE
                      AND min_utm <= :monto_utm
                      AND (max_utm IS NULL OR max_utm > :monto_utm)
                    ORDER BY level_number LIMIT 1
                """),
                {"monto_utm": monto_utm},
            )).mappings().first()
            if level_row:
                evaluator_code = level_row["evaluator_code"]

        # Fallback to track default evaluator
        if not evaluator_code:
            track = await _get_track_config(mechanism_code, db) if mechanism_code else None
            if track:
                evaluator_code = track["evaluator"]

        if evaluator_code:
            et_row = (await db.execute(
                text("SELECT id FROM ref.category WHERE scheme = 'evaluator_type' AND code = :code"),
                {"code": evaluator_code},
            )).mappings().first()
            if et_row:
                evaluator_type_id = et_row["id"]

    if not evaluator_type_id:
        raise HTTPException(status_code=400, detail="evaluator_type_id requerido (no se pudo auto-asignar)")

    row = (await db.execute(
        text("""
            INSERT INTO core.evaluation_assignment (
                ipr_id, evaluator_type_id, evaluator_organization_id,
                evaluator_name, deadline_at, created_by_id,
                rank_position, rank_total, convocatoria_code
            ) VALUES (
                CAST(:ipr_id AS uuid), CAST(:evaluator_type_id AS uuid),
                CAST(:evaluator_org_id AS uuid), :evaluator_name,
                :deadline_at, CAST(:user_id AS uuid),
                :rank_position, :rank_total, :convocatoria_code
            )
            RETURNING id
        """),
        {
            "ipr_id": str(ipr_id),
            "evaluator_type_id": str(evaluator_type_id),
            "evaluator_org_id": str(body.evaluator_organization_id) if body.evaluator_organization_id else None,
            "evaluator_name": body.evaluator_name,
            "deadline_at": body.deadline_at,
            "user_id": str(user["id"]),
            "rank_position": body.rank_position,
            "rank_total": body.rank_total,
            "convocatoria_code": body.convocatoria_code,
        },
    )).mappings().first()
    await record_event(db, "CREACION", "core.evaluation_assignment", row["id"], user["id"], {"ipr_id": str(ipr_id)})
    await db.commit()
    return {"id": str(row["id"]), "message": "Evaluación asignada"}


@router.patch("/{ipr_id}/evaluaciones/{eval_id}")
async def update_evaluation(
    ipr_id: UUID,
    eval_id: UUID,
    body: EvaluationAssignmentUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update an evaluation assignment (result, observations, completion)."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "ANALISTA")
    await check_ipr_access(db, user, ipr_id)

    set_clauses = ["updated_at = NOW()", "updated_by_id = CAST(:user_id AS uuid)"]
    params: dict = {"id": str(eval_id), "ipr_id": str(ipr_id), "user_id": str(user["id"])}

    updates = body.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    if "result_id" in updates and updates["result_id"] is not None:
        set_clauses.append("result_id = CAST(:result_id AS uuid)")
        params["result_id"] = str(updates["result_id"])
        # Denormalize result_code
        rc_row = (await db.execute(
            text("SELECT code FROM ref.category WHERE id = CAST(:rid AS uuid)"),
            {"rid": str(updates["result_id"])},
        )).mappings().first()
        if rc_row:
            set_clauses.append("result_code = :result_code")
            params["result_code"] = rc_row["code"]

    if "observations" in updates:
        set_clauses.append("observations = :observations")
        params["observations"] = updates["observations"]

    if "completed_at" in updates:
        set_clauses.append("completed_at = :completed_at")
        params["completed_at"] = updates["completed_at"]

    if "deadline_at" in updates:
        set_clauses.append("deadline_at = :deadline_at")
        params["deadline_at"] = updates["deadline_at"]

    if "numeric_score" in updates:
        set_clauses.append("numeric_score = :numeric_score")
        params["numeric_score"] = updates["numeric_score"]

    if "rank_position" in updates:
        set_clauses.append("rank_position = :rank_position")
        params["rank_position"] = updates["rank_position"]

    if "rank_total" in updates:
        set_clauses.append("rank_total = :rank_total")
        params["rank_total"] = updates["rank_total"]

    if "convocatoria_code" in updates:
        set_clauses.append("convocatoria_code = :convocatoria_code")
        params["convocatoria_code"] = updates["convocatoria_code"]

    sql = text(f"""
        UPDATE core.evaluation_assignment
        SET {', '.join(set_clauses)}
        WHERE id = CAST(:id AS uuid) AND ipr_id = CAST(:ipr_id AS uuid)
          AND deleted_at IS NULL
    """)
    result = await db.execute(sql, params)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    await record_event(db, "MODIFICACION", "core.evaluation_assignment", eval_id, user["id"], {"ipr_id": str(ipr_id)})
    await db.commit()
    return {"message": "Evaluación actualizada"}


# ---------------------------------------------------------------------------
# HΩ-02: Kinship declarations (parentesco)
# ---------------------------------------------------------------------------

_KINSHIP_WRITE_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL"}


async def _get_kinship_declaration(decl_id, db: AsyncSession) -> dict:
    """Fetch a single kinship declaration with joined person names."""
    row = (await db.execute(
        text("""
            SELECT kd.id, kd.ipr_id, kd.person_id,
                   (p.names || ' ' || p.paternal_surname) AS person_name,
                   p.rut AS person_rut,
                   kd.declaration_type, kd.declares_no_conflict,
                   kd.related_authority_id,
                   CASE WHEN kd.related_authority_id IS NOT NULL
                        THEN (SELECT pa.names || ' ' || pa.paternal_surname
                              FROM core.person pa WHERE pa.id = kd.related_authority_id)
                   END AS related_authority_name,
                   kd.relationship_type, kd.relationship_degree,
                   kd.declared_at, kd.validated_by_id, kd.validated_at
            FROM core.kinship_declaration kd
            JOIN core.person p ON p.id = kd.person_id
            WHERE kd.id = CAST(:id AS uuid) AND kd.deleted_at IS NULL
        """),
        {"id": str(decl_id)},
    )).mappings().first()
    return dict(row)


@router.get("/{ipr_id}/parentesco", response_model=list[KinshipDeclarationItem])
async def list_kinship_declarations(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all kinship declarations for an IPR."""
    await check_ipr_access(db, user, ipr_id)
    result = await db.execute(
        text("""
            SELECT kd.id, kd.ipr_id, kd.person_id,
                   (p.names || ' ' || p.paternal_surname) AS person_name,
                   p.rut AS person_rut,
                   kd.declaration_type, kd.declares_no_conflict,
                   kd.related_authority_id,
                   CASE WHEN kd.related_authority_id IS NOT NULL
                        THEN (SELECT pa.names || ' ' || pa.paternal_surname
                              FROM core.person pa WHERE pa.id = kd.related_authority_id)
                   END AS related_authority_name,
                   kd.relationship_type, kd.relationship_degree,
                   kd.declared_at, kd.validated_by_id, kd.validated_at
            FROM core.kinship_declaration kd
            JOIN core.person p ON p.id = kd.person_id
            WHERE kd.ipr_id = :ipr_id AND kd.deleted_at IS NULL
            ORDER BY kd.declared_at DESC
        """),
        {"ipr_id": str(ipr_id)},
    )
    return [dict(r) for r in result.mappings().all()]


@router.post("/{ipr_id}/parentesco", response_model=KinshipDeclarationItem, status_code=201)
async def create_kinship_declaration(
    ipr_id: UUID,
    body: KinshipDeclarationCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a kinship declaration for an IPR."""
    _require_roles(user, *_KINSHIP_WRITE_ROLES)
    await check_ipr_access(db, user, ipr_id)

    # Validate declaration_type
    if body.declaration_type not in ("EVALUADOR", "REPRESENTANTE_LEGAL", "PERSONAL_CONTRATADO"):
        raise HTTPException(status_code=422, detail="declaration_type inválido")

    # If declares conflict, require authority details
    if not body.declares_no_conflict:
        if not body.related_authority_id or not body.relationship_type or body.relationship_degree is None:
            raise HTTPException(
                status_code=422,
                detail="Si declara conflicto, debe indicar autoridad relacionada, tipo y grado de parentesco",
            )

    # Verify person exists
    person = (await db.execute(
        text("SELECT id FROM core.person WHERE id = CAST(:pid AS uuid) AND is_active = true"),
        {"pid": str(body.person_id)},
    )).mappings().first()
    if not person:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    # Verify related authority is actually a GORE authority (if provided)
    if body.related_authority_id:
        authority_check = (await db.execute(
            text("""
                SELECT u.id FROM core."user" u
                JOIN ref.category r ON u.system_role_id = r.id
                WHERE u.person_id = CAST(:pid AS uuid) AND u.is_active = true
                  AND r.code IN ('GOBERNADOR', 'CONSEJERO_REGIONAL', 'SECRETARIO_EJECUTIVO',
                                 'ADMIN_REGIONAL', 'JEFE_DIVISION')
            """),
            {"pid": str(body.related_authority_id)},
        )).mappings().first()
        if not authority_check:
            raise HTTPException(
                status_code=422,
                detail="La persona indicada como autoridad no tiene un rol de autoridad GORE",
            )

    try:
        row = (await db.execute(
            text("""
                INSERT INTO core.kinship_declaration (
                    ipr_id, person_id, declaration_type, declares_no_conflict,
                    related_authority_id, relationship_type, relationship_degree
                ) VALUES (
                    CAST(:ipr_id AS uuid), CAST(:person_id AS uuid), :declaration_type,
                    :declares_no_conflict, CAST(:related_authority_id AS uuid),
                    :relationship_type, :relationship_degree
                )
                RETURNING id, declared_at, created_at
            """),
            {
                "ipr_id": str(ipr_id),
                "person_id": str(body.person_id),
                "declaration_type": body.declaration_type,
                "declares_no_conflict": body.declares_no_conflict,
                "related_authority_id": str(body.related_authority_id) if body.related_authority_id else None,
                "relationship_type": body.relationship_type,
                "relationship_degree": body.relationship_degree,
            },
        )).mappings().first()
        await db.commit()
    except Exception as exc:
        await db.rollback()
        if "uq_kinship_decl" in str(exc):
            raise HTTPException(
                status_code=409,
                detail="Ya existe una declaración de esta persona con este tipo para este IPR",
            )
        raise

    # Re-fetch full item
    return await _get_kinship_declaration(row["id"], db)


@router.patch("/{ipr_id}/parentesco/{decl_id}", response_model=KinshipDeclarationItem)
async def validate_kinship_declaration(
    ipr_id: UUID,
    decl_id: UUID,
    body: KinshipDeclarationValidate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Validate (or invalidate) a kinship declaration. Admin only."""
    _require_roles(user, "ADMIN_SISTEMA")
    await check_ipr_access(db, user, ipr_id)

    existing = (await db.execute(
        text("""
            SELECT id FROM core.kinship_declaration
            WHERE id = CAST(:id AS uuid) AND ipr_id = CAST(:ipr_id AS uuid) AND deleted_at IS NULL
        """),
        {"id": str(decl_id), "ipr_id": str(ipr_id)},
    )).mappings().first()
    if not existing:
        raise HTTPException(status_code=404, detail="Declaración no encontrada")

    if body.validated:
        await db.execute(
            text("""
                UPDATE core.kinship_declaration
                SET validated_by_id = CAST(:uid AS uuid), validated_at = now(), updated_at = now()
                WHERE id = CAST(:id AS uuid)
            """),
            {"id": str(decl_id), "uid": str(user["id"])},
        )
    else:
        await db.execute(
            text("""
                UPDATE core.kinship_declaration
                SET validated_by_id = NULL, validated_at = NULL, updated_at = now()
                WHERE id = CAST(:id AS uuid)
            """),
            {"id": str(decl_id)},
        )
    await db.commit()
    return await _get_kinship_declaration(decl_id, db)


@router.delete("/{ipr_id}/parentesco/{decl_id}", status_code=204)
async def delete_kinship_declaration(
    ipr_id: UUID,
    decl_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a kinship declaration. Admin only."""
    _require_roles(user, "ADMIN_SISTEMA")
    await check_ipr_access(db, user, ipr_id)
    result = await db.execute(
        text("""
            UPDATE core.kinship_declaration SET deleted_at = now(), updated_at = now()
            WHERE id = CAST(:id AS uuid) AND ipr_id = CAST(:ipr_id AS uuid) AND deleted_at IS NULL
        """),
        {"id": str(decl_id), "ipr_id": str(ipr_id)},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Declaración no encontrada")
    await db.commit()


# ---------------------------------------------------------------------------
# Admissibility checklist (PRE_ADMISIBLE → ADMISIBLE)
# ---------------------------------------------------------------------------


@router.get("/{ipr_id}/admisibilidad")
async def get_admissibility_checklist(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await check_ipr_access(db, user, ipr_id)
    ipr = (await db.execute(text("""
        SELECT i.id, i.mechanism_id,
               m.code AS mechanism_code,
               ft.id AS track_id, ft.code AS track_code
        FROM core.ipr i
        LEFT JOIN ref.category m ON m.id = i.mechanism_id
        LEFT JOIN core.financing_track ft ON ft.code = m.code
        WHERE i.id = :ipr_id
    """), {"ipr_id": str(ipr_id)})).mappings().first()
    if not ipr:
        raise HTTPException(404, "IPR no encontrado")
    if not ipr["track_id"]:
        return {"track_code": None, "total_items": 0, "verified_count": 0, "pending_count": 0, "items": []}

    rows = (await db.execute(text("""
        SELECT ai.id AS item_id, ai.code, ai.label, ai.description,
               ai.responsible_role, ai.is_required, ai.sort_order,
               ac.verified_at, ac.notes,
               COALESCE(p.names || ' ' || p.paternal_surname, '') AS verified_by
        FROM core.admissibility_item ai
        LEFT JOIN core.admissibility_check ac ON ac.item_id = ai.id AND ac.ipr_id = :ipr_id
        LEFT JOIN core."user" u ON u.id = ac.verified_by_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE ai.financing_track_id = :track_id AND ai.deleted_at IS NULL
        ORDER BY ai.sort_order, ai.code
    """), {"ipr_id": str(ipr_id), "track_id": str(ipr["track_id"])})).mappings().all()

    items = []
    verified_count = 0
    for r in rows:
        verified = r["verified_at"] is not None
        if verified:
            verified_count += 1
        items.append({
            "item_id": str(r["item_id"]),
            "code": r["code"],
            "label": r["label"],
            "description": r["description"],
            "responsible_role": r["responsible_role"],
            "is_required": r["is_required"],
            "verified": verified,
            "verified_by": r["verified_by"] if verified else None,
            "verified_at": r["verified_at"].isoformat() if verified else None,
            "notes": r["notes"],
        })

    total = len(items)
    required_pending = sum(1 for i in items if i["is_required"] and not i["verified"])
    return {
        "track_code": ipr["track_code"],
        "total_items": total,
        "verified_count": verified_count,
        "pending_count": required_pending,
        "items": items,
    }


@router.post("/{ipr_id}/admisibilidad/{item_id}/verificar")
async def verify_admissibility_item(
    ipr_id: UUID,
    item_id: UUID,
    user: CurrentUser,
    data: dict | None = None,
    db: AsyncSession = Depends(get_db),
):
    if data is None:
        data = {}
    await check_ipr_access(db, user, ipr_id)

    # Validate IPR exists and is in PRE_ADMISIBLE state
    ipr_state = (await db.execute(text("""
        SELECT c.code FROM core.ipr i
        JOIN ref.category c ON c.id = i.status_id
        WHERE i.id = CAST(:ipr_id AS uuid) AND i.deleted_at IS NULL
    """), {"ipr_id": str(ipr_id)})).scalar()
    if not ipr_state:
        raise HTTPException(404, "IPR no encontrado")
    if ipr_state != "PRE_ADMISIBLE":
        raise HTTPException(409, "Solo se puede verificar ítems en estado PRE_ADMISIBLE")

    item = (await db.execute(text(
        "SELECT id, responsible_role FROM core.admissibility_item WHERE id = :id AND deleted_at IS NULL"
    ), {"id": str(item_id)})).mappings().first()
    if not item:
        raise HTTPException(404, "Ítem de admisibilidad no encontrado")

    user_role = user.get("role_code", "")
    if user_role != "ADMIN_SISTEMA" and user_role != item["responsible_role"]:
        raise HTTPException(403, f"Solo {item['responsible_role']} puede verificar este ítem")

    try:
        row = (await db.execute(text("""
            INSERT INTO core.admissibility_check (ipr_id, item_id, verified_by_id, notes)
            VALUES (:ipr_id, :item_id, :user_id, :notes)
            RETURNING id, verified_at
        """), {
            "ipr_id": str(ipr_id),
            "item_id": str(item_id),
            "user_id": user["id"],
            "notes": data.get("notes"),
        })).mappings().first()
        await db.commit()
        return {"message": "Ítem verificado", "verified_at": row["verified_at"].isoformat()}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "Este ítem ya fue verificado para este IPR")


@router.delete("/{ipr_id}/admisibilidad/{item_id}/verificar")
async def unverify_admissibility_item(
    ipr_id: UUID,
    item_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await check_ipr_access(db, user, ipr_id)
    # Validate IPR exists and is in PRE_ADMISIBLE state
    ipr_state = (await db.execute(text("""
        SELECT c.code FROM core.ipr i
        JOIN ref.category c ON c.id = i.status_id
        WHERE i.id = CAST(:ipr_id AS uuid) AND i.deleted_at IS NULL
    """), {"ipr_id": str(ipr_id)})).scalar()
    if not ipr_state:
        raise HTTPException(404, "IPR no encontrado")
    if ipr_state != "PRE_ADMISIBLE":
        raise HTTPException(409, "Solo se puede modificar verificación en estado PRE_ADMISIBLE")

    item = (await db.execute(text(
        "SELECT responsible_role FROM core.admissibility_item WHERE id = :id AND deleted_at IS NULL"
    ), {"id": str(item_id)})).mappings().first()
    if not item:
        raise HTTPException(404, "Ítem no encontrado")

    user_role = user.get("role_code", "")
    if user_role != "ADMIN_SISTEMA" and user_role != item["responsible_role"]:
        raise HTTPException(403, f"Solo {item['responsible_role']} puede desmarcar este ítem")

    result = await db.execute(text(
        "DELETE FROM core.admissibility_check WHERE ipr_id = :ipr_id AND item_id = :item_id"
    ), {"ipr_id": str(ipr_id), "item_id": str(item_id)})
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(404, "Verificación no encontrada")
    return {"message": "Verificación desmarcada"}


# ---------------------------------------------------------------------------
# C33 Technical Certification
# ---------------------------------------------------------------------------

_CERT_REQUEST_ROLES = {"JEFE_DIVISION", "ADMIN_REGIONAL", "ADMIN_SISTEMA", "JEFE_DGI", "GOBERNADOR"}
_CERT_RESOLVE_ROLES = {"ADMIN_REGIONAL", "ADMIN_SISTEMA"}


@router.get("/{ipr_id}/certificacion-tecnica")
async def get_certification_status(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get C33 technical certification status for an IPR."""
    await check_ipr_access(db, user, ipr_id)
    row = (await db.execute(text("""
        SELECT m.code AS mechanism_code,
               i.metadata->>'categoria_c33' AS categoria_c33,
               i.metadata->>'informe_tecnico_favorable' AS informe,
               i.metadata->>'cert_requested_at' AS requested_at,
               i.metadata->>'cert_requested_by_name' AS requested_by,
               i.metadata->>'cert_certifier_org' AS certifier_org,
               i.metadata->>'cert_resolved_at' AS resolved_at,
               i.metadata->>'cert_resolved_by_name' AS resolved_by,
               i.metadata->>'cert_document_reference' AS document_reference,
               i.metadata->>'cert_notes' AS notes
        FROM core.ipr i
        LEFT JOIN ref.category m ON m.id = i.mechanism_id
        WHERE i.id = CAST(:id AS uuid) AND i.deleted_at IS NULL
    """), {"id": str(ipr_id)})).mappings().first()

    if not row:
        raise HTTPException(404, "IPR no encontrado")
    if row["mechanism_code"] != "C33":
        raise HTTPException(409, "Este IPR no es del track C33")

    categoria = row["categoria_c33"]
    certifier = row["certifier_org"]
    if categoria and not certifier:
        cert_row = (await db.execute(text("""
            SELECT metadata->>'certifier_org_code' AS certifier
            FROM ref.category
            WHERE scheme = 'categoria_c33' AND code = :code AND deleted_at IS NULL
        """), {"code": categoria})).mappings().first()
        certifier = cert_row["certifier"] if cert_row else None

    informe_raw = row["informe"]
    informe_val = None
    if informe_raw is not None:
        informe_val = informe_raw == "true" or informe_raw is True

    return {
        "categoria_c33": categoria,
        "certifier_org": certifier,
        "requested": row["requested_at"] is not None,
        "requested_at": row["requested_at"],
        "requested_by": row["requested_by"],
        "resolved": informe_raw is not None,
        "informe_tecnico_favorable": informe_val,
        "resolved_at": row["resolved_at"],
        "resolved_by": row["resolved_by"],
        "document_reference": row["document_reference"],
        "notes": row["notes"],
    }


@router.post("/{ipr_id}/certificacion-tecnica/solicitar")
async def solicitar_certification(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Request C33 technical certification from SERVIU/MOP."""
    _require_roles(user, *_CERT_REQUEST_ROLES)
    await check_ipr_access(db, user, ipr_id)

    row = (await db.execute(text("""
        SELECT m.code AS mechanism_code,
               i.metadata->>'categoria_c33' AS categoria_c33,
               i.metadata->>'cert_requested_at' AS already_requested,
               i.metadata->>'informe_tecnico_favorable' AS already_resolved
        FROM core.ipr i
        LEFT JOIN ref.category m ON m.id = i.mechanism_id
        WHERE i.id = CAST(:id AS uuid) AND i.deleted_at IS NULL
    """), {"id": str(ipr_id)})).mappings().first()

    if not row:
        raise HTTPException(404, "IPR no encontrado")
    if row["mechanism_code"] != "C33":
        raise HTTPException(409, "Este IPR no es del track C33")
    if not row["categoria_c33"]:
        raise HTTPException(409, "Asignar categoría C33 antes de solicitar certificación")
    if row["already_resolved"] is not None:
        raise HTTPException(409, "Certificación ya tiene resultado registrado")

    cert_row = (await db.execute(text("""
        SELECT metadata->>'certifier_org_code' AS certifier
        FROM ref.category
        WHERE scheme = 'categoria_c33' AND code = :code AND deleted_at IS NULL
    """), {"code": row["categoria_c33"]})).mappings().first()
    certifier = cert_row["certifier"] if cert_row else "Organismo"

    person_row = (await db.execute(text("""
        SELECT p.names, p.paternal_surname
        FROM core."user" u JOIN core.person p ON p.id = u.person_id
        WHERE u.id = CAST(:uid AS uuid)
    """), {"uid": user["id"]})).mappings().first()
    requester_name = f"{person_row['names']} {person_row['paternal_surname']}" if person_row else "Unknown"

    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat()

    await db.execute(text("""
        UPDATE core.ipr
        SET metadata = jsonb_set(
                jsonb_set(
                    jsonb_set(
                        jsonb_set(
                            COALESCE(metadata, '{}'),
                            '{cert_requested_at}', CAST(:ts AS jsonb)
                        ),
                        '{cert_requested_by_id}', CAST(:uid AS jsonb)
                    ),
                    '{cert_requested_by_name}', CAST(:uname AS jsonb)
                ),
                '{cert_certifier_org}', CAST(:org AS jsonb)
            ),
            updated_at = NOW()
        WHERE id = CAST(:id AS uuid)
    """), {
        "id": str(ipr_id),
        "ts": json.dumps(now_iso),
        "uid": json.dumps(str(user["id"])),
        "uname": json.dumps(requester_name),
        "org": json.dumps(certifier),
    })
    await db.commit()

    return {
        "message": f"Certificación técnica solicitada a {certifier}",
        "certifier_org": certifier,
        "requested_at": now_iso,
        "requested_by": requester_name,
    }


@router.patch("/{ipr_id}/certificacion-tecnica")
async def resolver_certification(
    ipr_id: UUID,
    data: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Register C33 technical certification result."""
    _require_roles(user, *_CERT_RESOLVE_ROLES)
    await check_ipr_access(db, user, ipr_id)

    row = (await db.execute(text("""
        SELECT m.code AS mechanism_code,
               i.metadata->>'cert_requested_at' AS requested,
               i.metadata->>'informe_tecnico_favorable' AS already_resolved
        FROM core.ipr i
        LEFT JOIN ref.category m ON m.id = i.mechanism_id
        WHERE i.id = CAST(:id AS uuid) AND i.deleted_at IS NULL
    """), {"id": str(ipr_id)})).mappings().first()

    if not row:
        raise HTTPException(404, "IPR no encontrado")
    if row["mechanism_code"] != "C33":
        raise HTTPException(409, "Este IPR no es del track C33")
    if not row["requested"]:
        raise HTTPException(409, "No existe solicitud de certificación previa")
    if row["already_resolved"] is not None:
        raise HTTPException(409, "Certificación ya tiene resultado registrado")

    favorable = data.get("favorable")
    if favorable is None:
        raise HTTPException(422, "Campo 'favorable' es requerido (true/false)")

    person_row = (await db.execute(text("""
        SELECT p.names, p.paternal_surname
        FROM core."user" u JOIN core.person p ON p.id = u.person_id
        WHERE u.id = CAST(:uid AS uuid)
    """), {"uid": user["id"]})).mappings().first()
    resolver_name = f"{person_row['names']} {person_row['paternal_surname']}" if person_row else "Unknown"

    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat()

    doc_ref = data.get("document_reference", "")
    notes = data.get("notes", "")

    await db.execute(text("""
        UPDATE core.ipr
        SET metadata = jsonb_set(
                jsonb_set(
                    jsonb_set(
                        jsonb_set(
                            jsonb_set(
                                COALESCE(metadata, '{}'),
                                '{informe_tecnico_favorable}', CAST(:favorable AS jsonb)
                            ),
                            '{cert_resolved_at}', CAST(:ts AS jsonb)
                        ),
                        '{cert_resolved_by_id}', CAST(:uid AS jsonb)
                    ),
                    '{cert_resolved_by_name}', CAST(:uname AS jsonb)
                ),
                '{cert_document_reference}', CAST(:doc AS jsonb)
            ),
            updated_at = NOW()
        WHERE id = CAST(:id AS uuid)
    """), {
        "id": str(ipr_id),
        "favorable": json.dumps(favorable),
        "ts": json.dumps(now_iso),
        "uid": json.dumps(str(user["id"])),
        "uname": json.dumps(resolver_name),
        "doc": json.dumps(doc_ref),
    })

    if notes:
        await db.execute(text("""
            UPDATE core.ipr
            SET metadata = jsonb_set(COALESCE(metadata, '{}'), '{cert_notes}', CAST(:notes AS jsonb))
            WHERE id = CAST(:id AS uuid)
        """), {"id": str(ipr_id), "notes": json.dumps(notes)})

    await db.commit()

    return {
        "message": "Resultado de certificación registrado",
        "informe_tecnico_favorable": favorable,
        "resolved_at": now_iso,
        "resolved_by": resolver_name,
        "document_reference": doc_ref,
    }


# ---------------------------------------------------------------------------
# GET /api/ipr/{id}/modificaciones — List modifications
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/modificaciones")
async def list_modifications(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all formal modifications for an IPR."""
    _require_roles(user, *OPERATIONAL_ROLES, *DGI_ROLES)
    await check_ipr_access(db, user, ipr_id)

    rows = (await db.execute(
        text("""
            SELECT m.id, m.code,
                   mt.code AS modification_type_code, mt.label AS modification_type_label,
                   ms.code AS status_code, ms.label AS status_label,
                   m.description, m.justification,
                   m.field_changed, m.old_value, m.new_value, m.amount_delta,
                   CONCAT(req.names, ' ', req.paternal_surname) AS requested_by_name,
                   CASE WHEN m.approved_by_id IS NOT NULL
                        THEN CONCAT(appr.names, ' ', appr.paternal_surname)
                        ELSE NULL END AS approved_by_name,
                   m.approved_at, m.created_at
            FROM core.ipr_modification m
            JOIN ref.category mt ON mt.id = m.modification_type_id
            JOIN ref.category ms ON ms.id = m.status_id
            JOIN core."user" req_u ON req_u.id = m.requested_by_id
            JOIN core.person req ON req.id = req_u.person_id
            LEFT JOIN core."user" appr_u ON appr_u.id = m.approved_by_id
            LEFT JOIN core.person appr ON appr.id = appr_u.person_id
            WHERE m.ipr_id = :ipr_id AND m.deleted_at IS NULL
            ORDER BY m.created_at DESC
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().all()

    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# POST /api/ipr/{id}/modificaciones — Create modification
# ---------------------------------------------------------------------------

@router.post("/{ipr_id}/modificaciones", status_code=status.HTTP_201_CREATED)
async def create_modification(
    ipr_id: UUID,
    body: IprModificationCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a formal modification request for an IPR."""
    _require_roles(user, *WRITE_OPERATIONAL_ROLES)
    await check_ipr_access(db, user, ipr_id)

    check = await db.execute(
        text("SELECT id FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(ipr_id)},
    )
    if not check.first():
        raise HTTPException(status_code=404, detail="IPR no encontrado")

    # Get initial status (SOLICITADA)
    status_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'modification_status' AND code = 'SOLICITADA'"),
    )).scalar()
    if not status_id:
        raise HTTPException(status_code=500, detail="modification_status SOLICITADA no encontrado")

    # Advisory-locked code generation
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('mod_code'))"))
    from datetime import date as dt_date
    year = dt_date.today().year
    seq = (await db.execute(
        text("""
            SELECT COALESCE(MAX(CAST(SUBSTRING(code FROM '[0-9]+$') AS INT)), 0) + 1
            FROM core.ipr_modification
            WHERE code LIKE :prefix
        """),
        {"prefix": f"MOD-{year}-%"},
    )).scalar() or 1
    code = f"MOD-{year}-{seq:04d}"

    row = (await db.execute(
        text("""
            INSERT INTO core.ipr_modification (
                ipr_id, code, modification_type_id, status_id,
                description, justification, field_changed,
                old_value, new_value, amount_delta,
                requested_by_id, created_at, updated_at
            ) VALUES (
                CAST(:ipr_id AS uuid), :code,
                CAST(:type_id AS uuid), CAST(:status_id AS uuid),
                :description, :justification, :field_changed,
                :old_value, :new_value, :amount_delta,
                CAST(:user_id AS uuid), NOW(), NOW()
            )
            RETURNING id, code
        """),
        {
            "ipr_id": str(ipr_id), "code": code,
            "type_id": str(body.modification_type_id),
            "status_id": str(status_id),
            "description": body.description,
            "justification": body.justification,
            "field_changed": body.field_changed,
            "old_value": body.old_value,
            "new_value": body.new_value,
            "amount_delta": body.amount_delta,
            "user_id": str(user["id"]),
        },
    )).mappings().first()
    await record_event(db, "CREACION", "core.ipr_modification", row["id"], user["id"], {"ipr_id": str(ipr_id)})
    await db.commit()

    return {"id": str(row["id"]), "code": row["code"]}


# ---------------------------------------------------------------------------
# PATCH /api/ipr/{id}/modificaciones/{mod_id} — Update modification status
# ---------------------------------------------------------------------------

_MOD_FIELD_ALLOWLIST = {"status_id": "status_id", "description": "description", "justification": "justification"}

@router.patch("/{ipr_id}/modificaciones/{mod_id}")
async def update_modification(
    ipr_id: UUID,
    mod_id: UUID,
    body: IprModificationUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update a modification (status transitions, description edits)."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR")
    await check_ipr_access(db, user, ipr_id)

    check = (await db.execute(
        text("SELECT id FROM core.ipr_modification WHERE id = :id AND ipr_id = :ipr_id AND deleted_at IS NULL"),
        {"id": str(mod_id), "ipr_id": str(ipr_id)},
    )).first()
    if not check:
        raise HTTPException(status_code=404, detail="Modificación no encontrada")

    updates = body.model_dump(exclude_none=True)
    if not updates:
        return {"message": "Sin cambios"}

    set_clauses = []
    params: dict = {"id": str(mod_id)}
    for field, value in updates.items():
        col = _MOD_FIELD_ALLOWLIST.get(field)
        if col is None:
            continue
        set_clauses.append(f"{col} = :{field}")
        params[field] = str(value) if value is not None else None

    # If status changes to APROBADA/RECHAZADA, record approver
    if "status_id" in updates:
        new_status_code = (await db.execute(
            text("SELECT code FROM ref.category WHERE id = CAST(:sid AS uuid)"),
            {"sid": str(updates["status_id"])},
        )).scalar()
        if new_status_code in ("APROBADA", "RECHAZADA"):
            set_clauses.append("approved_by_id = CAST(:approver AS uuid)")
            set_clauses.append("approved_at = NOW()")
            params["approver"] = str(user["id"])

    if not set_clauses:
        return {"message": "Sin cambios válidos"}

    set_clauses.append("updated_at = NOW()")
    sql = text(f"UPDATE core.ipr_modification SET {', '.join(set_clauses)} WHERE id = CAST(:id AS uuid)")
    try:
        await db.execute(sql, params)
        await record_event(db, "MODIFICACION", "core.ipr_modification", mod_id, user["id"], {"ipr_id": str(ipr_id)})
        await db.commit()
    except DBAPIError as e:
        await db.rollback()
        if "Transición de estado inválida" in str(e):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e.orig))
        raise

    return {"message": "Modificación actualizada"}


# ---------------------------------------------------------------------------
# POST /api/ipr/check-report-compliance — Batch check report periodicity
# ---------------------------------------------------------------------------

@router.post("/check-report-compliance")
async def check_report_compliance(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Scan IPRs in F4 execution states and create alerts for overdue reports."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DGI", "ESP_CONTROL_GESTION")

    # IPRs in execution states
    iprs = (await db.execute(
        text("""
            SELECT i.id, i.codigo_bip, i.name, s.code AS status_code,
                   ft.sla_days, ft.label AS track_label,
                   (SELECT MAX(pr.report_date) FROM core.progress_report pr
                    WHERE pr.ipr_id = i.id AND pr.deleted_at IS NULL) AS last_report
            FROM core.ipr i
            JOIN ref.category s ON s.id = i.status_id
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            LEFT JOIN core.financing_track ft ON ft.code = m.code AND ft.is_active = TRUE
            WHERE i.deleted_at IS NULL
              AND s.code IN ('EN_EJECUCION', 'EN_OBRA', 'CONTRATO_FIRMADO')
              AND ft.sla_days IS NOT NULL
        """),
    )).mappings().all()

    from datetime import date as dt_date
    today = dt_date.today()
    alert_severity_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_level' AND code = 'ATENCION'"),
    )).scalar()
    alert_type_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_type' AND code = 'PLAZO_LEGAL'"),
    )).scalar()
    created = 0

    for ipr in iprs:
        sla = ipr["sla_days"] or {}
        freq = sla.get("report_frequency_days")
        if not freq:
            continue

        last_report = ipr["last_report"]
        if last_report is None:
            overdue = True
        else:
            days_since = (today - last_report).days if isinstance(last_report, dt_date) else 0
            overdue = days_since > freq

        if overdue:
            # Check if alert already exists for this IPR today
            existing = (await db.execute(
                text("""
                    SELECT id FROM core.alert
                    WHERE subject_type = 'core.ipr' AND subject_id = CAST(:ipr_id AS uuid)
                      AND message LIKE '%informe de avance vencido%'
                      AND created_at::date = CURRENT_DATE
                """),
                {"ipr_id": str(ipr["id"])},
            )).first()
            if existing:
                continue

            await db.execute(
                text("""
                    INSERT INTO core.alert (
                        alert_type_id, subject_type, subject_id, severity_id,
                        message, created_by_id, created_at, updated_at
                    ) VALUES (
                        CAST(:alert_type AS uuid),
                        'core.ipr', CAST(:ipr_id AS uuid), CAST(:sev AS uuid),
                        :msg, CAST(:uid AS uuid), NOW(), NOW()
                    )
                """),
                {
                    "alert_type": str(alert_type_id),
                    "ipr_id": str(ipr["id"]),
                    "sev": str(alert_severity_id),
                    "msg": f"Informe de avance vencido para {ipr['codigo_bip']} ({ipr['track_label']}). Periodicidad: cada {freq} días.",
                    "uid": str(user["id"]),
                },
            )
            created += 1

    await db.commit()
    return {"checked": len(iprs), "alerts_created": created}


# ---------------------------------------------------------------------------
# GET /api/ipr/{id}/cierre — Get closure record
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/cierre")
async def get_closure(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get the closure record for an IPR."""
    _require_roles(user, *OPERATIONAL_ROLES, *DGI_ROLES)
    await check_ipr_access(db, user, ipr_id)
    row = (await db.execute(
        text("""
            SELECT c.id, c.closure_date, c.closure_report,
                   c.physical_completion, c.financial_completion,
                   c.final_amount, c.signed_at, c.closure_act_id,
                   CONCAT(sp.names, ' ', sp.paternal_surname) AS signed_by_name,
                   CONCAT(cp.names, ' ', cp.paternal_surname) AS created_by_name,
                   c.created_at
            FROM core.ipr_closure c
            LEFT JOIN core."user" su ON su.id = c.signed_by_id
            LEFT JOIN core.person sp ON sp.id = su.person_id
            JOIN core."user" cu ON cu.id = c.created_by_id
            JOIN core.person cp ON cp.id = cu.person_id
            WHERE c.ipr_id = :ipr_id
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().first()
    if not row:
        return None
    return dict(row)


# ---------------------------------------------------------------------------
# POST /api/ipr/{id}/cierre — Create closure record
# ---------------------------------------------------------------------------

@router.post("/{ipr_id}/cierre", status_code=status.HTTP_201_CREATED)
async def create_closure(
    ipr_id: UUID,
    body: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create a closure record for an IPR."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR")
    await check_ipr_access(db, user, ipr_id)

    check = await db.execute(
        text("SELECT id FROM core.ipr WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(ipr_id)},
    )
    if not check.first():
        raise HTTPException(status_code=404, detail="IPR no encontrado")

    # Check if closure already exists
    existing = (await db.execute(
        text("SELECT id FROM core.ipr_closure WHERE ipr_id = :id"),
        {"id": str(ipr_id)},
    )).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ya existe un registro de cierre para este IPR")

    closure_date_raw = body.get("closure_date")
    closure_date_val = date.fromisoformat(closure_date_raw) if isinstance(closure_date_raw, str) else closure_date_raw

    row = (await db.execute(
        text("""
            INSERT INTO core.ipr_closure (
                ipr_id, closure_date, closure_report,
                physical_completion, financial_completion, final_amount,
                created_by_id
            ) VALUES (
                CAST(:ipr_id AS uuid), :closure_date, :closure_report,
                :physical, :financial, :amount,
                CAST(:uid AS uuid)
            )
            RETURNING id
        """),
        {
            "ipr_id": str(ipr_id),
            "closure_date": closure_date_val,
            "closure_report": body.get("closure_report"),
            "physical": body.get("physical_completion"),
            "financial": body.get("financial_completion"),
            "amount": body.get("final_amount"),
            "uid": str(user["id"]),
        },
    )).mappings().first()
    await record_event(db, "CIERRE", "core.ipr_closure", row["id"], user["id"], {"ipr_id": str(ipr_id)})
    await db.commit()
    return {"id": str(row["id"]), "message": "Registro de cierre creado"}


# ---------------------------------------------------------------------------
# PATCH /api/ipr/{id}/cierre — Update closure (sign)
# ---------------------------------------------------------------------------

@router.patch("/{ipr_id}/cierre")
async def update_closure(
    ipr_id: UUID,
    body: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update closure record — sign, update completion percentages."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR")
    await check_ipr_access(db, user, ipr_id)

    check = (await db.execute(
        text("SELECT id FROM core.ipr_closure WHERE ipr_id = :id"),
        {"id": str(ipr_id)},
    )).first()
    if not check:
        raise HTTPException(status_code=404, detail="Registro de cierre no encontrado")

    set_clauses = ["updated_at = NOW()"]
    params: dict = {"ipr_id": str(ipr_id)}

    allowed = {"closure_date", "closure_report", "physical_completion", "financial_completion", "final_amount", "closure_act_id"}
    for key in allowed:
        if key in body:
            set_clauses.append(f"{key} = :{key}")
            params[key] = str(body[key]) if body[key] is not None else None

    # Handle signing
    if body.get("sign"):
        set_clauses.append("signed_by_id = CAST(:signer AS uuid)")
        set_clauses.append("signed_at = NOW()")
        params["signer"] = str(user["id"])

    sql = text(f"UPDATE core.ipr_closure SET {', '.join(set_clauses)} WHERE ipr_id = CAST(:ipr_id AS uuid)")
    await db.execute(sql, params)
    await record_event(db, "MODIFICACION", "core.ipr_closure", ipr_id, user["id"])
    await db.commit()
    return {"message": "Registro de cierre actualizado"}


# ---------------------------------------------------------------------------
# GET /api/ipr/{id}/evaluacion-expost — List ex-post evaluations
# ---------------------------------------------------------------------------

@router.get("/{ipr_id}/evaluacion-expost")
async def list_expost_evaluations(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List ex-post evaluations for an IPR."""
    _require_roles(user, *OPERATIONAL_ROLES, *DGI_ROLES)
    await check_ipr_access(db, user, ipr_id)

    rows = (await db.execute(
        text("""
            SELECT e.id, e.evaluation_date,
                   CONCAT(ep.names, ' ', ep.paternal_surname) AS evaluator_name,
                   et.code AS eval_type_code, et.label AS eval_type_label,
                   e.impact_score, e.sustainability_score,
                   e.efficiency_score, e.effectiveness_score,
                   r.code AS rating_code, r.label AS rating_label,
                   e.findings, e.recommendations, e.lessons_learned,
                   e.created_at
            FROM core.ipr_expost_evaluation e
            JOIN core."user" eu ON eu.id = e.evaluator_id
            JOIN core.person ep ON ep.id = eu.person_id
            JOIN ref.category et ON et.id = e.evaluation_type_id
            LEFT JOIN ref.category r ON r.id = e.overall_rating_id
            WHERE e.ipr_id = :ipr_id
            ORDER BY e.evaluation_date DESC
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().all()

    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# POST /api/ipr/{id}/evaluacion-expost — Create ex-post evaluation
# ---------------------------------------------------------------------------

@router.post("/{ipr_id}/evaluacion-expost", status_code=status.HTTP_201_CREATED)
async def create_expost_evaluation(
    ipr_id: UUID,
    body: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Create an ex-post evaluation for an IPR (only for CERRADO IPRs)."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DGI", "ESP_CONTROL_GESTION")
    await check_ipr_access(db, user, ipr_id)

    # Verify IPR exists and is CERRADO
    ipr_row = (await db.execute(
        text("""
            SELECT s.code FROM core.ipr i
            JOIN ref.category s ON s.id = i.status_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()
    if not ipr_row:
        raise HTTPException(status_code=404, detail="IPR no encontrado")
    if ipr_row["code"] != "CERRADO":
        raise HTTPException(status_code=409, detail="Evaluación ex-post solo disponible para IPRs cerrados")

    eval_date_raw = body.get("evaluation_date")
    eval_date_val = date.fromisoformat(eval_date_raw) if isinstance(eval_date_raw, str) else eval_date_raw

    row = (await db.execute(
        text("""
            INSERT INTO core.ipr_expost_evaluation (
                ipr_id, evaluation_date, evaluator_id,
                evaluation_type_id,
                impact_score, sustainability_score,
                efficiency_score, effectiveness_score,
                overall_rating_id,
                findings, recommendations, lessons_learned
            ) VALUES (
                CAST(:ipr_id AS uuid), :eval_date, CAST(:uid AS uuid),
                CAST(:type_id AS uuid),
                :impact, :sustainability, :efficiency, :effectiveness,
                CAST(:rating_id AS uuid),
                :findings, :recommendations, :lessons
            )
            RETURNING id
        """),
        {
            "ipr_id": str(ipr_id),
            "eval_date": eval_date_val,
            "uid": str(user["id"]),
            "type_id": body.get("evaluation_type_id"),
            "impact": body.get("impact_score"),
            "sustainability": body.get("sustainability_score"),
            "efficiency": body.get("efficiency_score"),
            "effectiveness": body.get("effectiveness_score"),
            "rating_id": body.get("overall_rating_id"),
            "findings": body.get("findings"),
            "recommendations": body.get("recommendations"),
            "lessons": body.get("lessons_learned"),
        },
    )).mappings().first()
    await record_event(db, "CREACION", "core.ipr_expost_evaluation", row["id"], user["id"], {"ipr_id": str(ipr_id)})
    await db.commit()
    return {"id": str(row["id"]), "message": "Evaluación ex-post creada"}


# ---------------------------------------------------------------------------
# PATCH /api/ipr/{id}/evaluacion-expost/{eval_id} — Update ex-post evaluation
# ---------------------------------------------------------------------------

@router.patch("/{ipr_id}/evaluacion-expost/{eval_id}")
async def update_expost_evaluation(
    ipr_id: UUID,
    eval_id: UUID,
    body: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update an ex-post evaluation."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DGI", "ESP_CONTROL_GESTION")
    await check_ipr_access(db, user, ipr_id)

    check = (await db.execute(
        text("SELECT id FROM core.ipr_expost_evaluation WHERE id = :id AND ipr_id = :ipr_id"),
        {"id": str(eval_id), "ipr_id": str(ipr_id)},
    )).first()
    if not check:
        raise HTTPException(status_code=404, detail="Evaluación ex-post no encontrada")

    allowed = {
        "evaluation_date", "impact_score", "sustainability_score",
        "efficiency_score", "effectiveness_score", "overall_rating_id",
        "findings", "recommendations", "lessons_learned",
    }
    set_clauses = ["updated_at = NOW()"]
    params: dict = {"id": str(eval_id)}
    for key in allowed:
        if key in body:
            if key == "overall_rating_id":
                set_clauses.append(f"{key} = CAST(:{key} AS uuid)")
            else:
                set_clauses.append(f"{key} = :{key}")
            params[key] = body[key]

    sql = text(f"UPDATE core.ipr_expost_evaluation SET {', '.join(set_clauses)} WHERE id = CAST(:id AS uuid)")
    await db.execute(sql, params)
    await record_event(db, "MODIFICACION", "core.ipr_expost_evaluation", eval_id, user["id"], {"ipr_id": str(ipr_id)})
    await db.commit()
    return {"message": "Evaluación ex-post actualizada"}


# ---------------------------------------------------------------------------
# POST /api/ipr/check-evaluation-slas — Batch check evaluation SLA compliance
# ---------------------------------------------------------------------------

@router.post("/check-evaluation-slas")
async def check_evaluation_slas(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Scan IPRs in evaluation states and create alerts for overdue evaluations."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DGI", "ESP_CONTROL_GESTION")

    iprs = (await db.execute(
        text("""
            SELECT i.id, i.codigo_bip, i.name, i.phase_entered_at,
                   i.assignee_id,
                   s.code AS status_code, ft.sla_days, ft.label AS track_label
            FROM core.ipr i
            JOIN ref.category s ON s.id = i.status_id
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            LEFT JOIN core.financing_track ft ON ft.code = m.code AND ft.is_active = TRUE
            WHERE i.deleted_at IS NULL
              AND s.code IN ('EN_EVALUACION', 'RS', 'FI', 'FC', 'OT', 'AD', 'RF', 'ITF', 'AT')
              AND i.phase_entered_at IS NOT NULL
              AND ft.sla_days IS NOT NULL
        """),
    )).mappings().all()

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    alert_severity_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_level' AND code = 'ATENCION'"),
    )).scalar()
    alert_type_id_eval = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_type' AND code = 'PLAZO_LEGAL'"),
    )).scalar()
    created = 0

    for ipr in iprs:
        sla = ipr["sla_days"] or {}
        max_days = sla.get("evaluation_max_days")
        if not max_days:
            continue

        entered = ipr["phase_entered_at"]
        if entered.tzinfo is None:
            entered = entered.replace(tzinfo=timezone.utc)
        days_in = (now - entered).days
        if days_in <= max_days:
            continue

        existing = (await db.execute(
            text("""
                SELECT id FROM core.alert
                WHERE subject_type = 'core.ipr' AND subject_id = CAST(:ipr_id AS uuid)
                  AND message LIKE '%evaluación excede plazo%'
                  AND created_at::date = CURRENT_DATE
            """),
            {"ipr_id": str(ipr["id"])},
        )).first()
        if existing:
            continue

        await db.execute(
            text("""
                INSERT INTO core.alert (
                    alert_type_id, subject_type, subject_id, severity_id,
                    message, created_by_id, created_at, updated_at
                ) VALUES (
                    CAST(:alert_type AS uuid),
                    'core.ipr', CAST(:ipr_id AS uuid), CAST(:sev AS uuid),
                    :msg, CAST(:uid AS uuid), NOW(), NOW()
                )
            """),
            {
                "alert_type": str(alert_type_id_eval),
                "ipr_id": str(ipr["id"]),
                "sev": str(alert_severity_id),
                "msg": f"Evaluación excede plazo SLA para {ipr['codigo_bip']} ({ipr['track_label']}): {days_in} días (máx {max_days}d)",
                "uid": str(user["id"]),
            },
        )
        created += 1
        if ipr["assignee_id"]:
            try:
                await create_notification(
                    db=db,
                    user_id=ipr["assignee_id"],
                    title=f"Evaluación pendiente: {ipr['codigo_bip']}",
                    body=f"Evaluación excede plazo SLA: {days_in} días (máx {max_days}d)",
                    category="sla",
                    entity_type="core.ipr",
                    entity_id=ipr["id"],
                    link=f"/ipr/{ipr['id']}?tab=evaluaciones",
                )
            except Exception:
                pass

    await db.commit()
    return {"checked": len(iprs), "alerts_created": created}


# ---------------------------------------------------------------------------
# POST /api/ipr/check-admissibility-slas — Batch check admissibility timing
# ---------------------------------------------------------------------------

@router.post("/check-admissibility-slas")
async def check_admissibility_slas(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Detect IPRs stuck in PRE_ADMISIBLE exceeding the admissibility SLA."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DGI", "ESP_CONTROL_GESTION")

    iprs = (await db.execute(
        text("""
            SELECT i.id, i.codigo_bip, i.name, i.phase_entered_at,
                   i.assignee_id,
                   ft.sla_days, ft.label AS track_label
            FROM core.ipr i
            JOIN ref.category s ON s.id = i.status_id
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            LEFT JOIN core.financing_track ft ON ft.code = m.code AND ft.is_active = TRUE
            WHERE i.deleted_at IS NULL
              AND s.code = 'PRE_ADMISIBLE'
              AND i.phase_entered_at IS NOT NULL
        """),
    )).mappings().all()

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    default_sla = 30

    alert_severity_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_level' AND code = 'ATENCION'"),
    )).scalar()
    alert_type_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_type' AND code = 'PLAZO_LEGAL'"),
    )).scalar()
    created = 0

    for ipr in iprs:
        sla = ipr["sla_days"] or {}
        max_days = sla.get("admisibilidad", default_sla)

        entered = ipr["phase_entered_at"]
        if entered.tzinfo is None:
            entered = entered.replace(tzinfo=timezone.utc)
        days_in = (now - entered).days
        if days_in <= max_days:
            continue

        existing = (await db.execute(
            text("""
                SELECT id FROM core.alert
                WHERE subject_type = 'core.ipr' AND subject_id = CAST(:ipr_id AS uuid)
                  AND message LIKE '%admisibilidad excede%'
                  AND created_at::date = CURRENT_DATE
            """),
            {"ipr_id": str(ipr["id"])},
        )).first()
        if existing:
            continue

        track_label = ipr["track_label"] or "sin track"
        await db.execute(
            text("""
                INSERT INTO core.alert (
                    alert_type_id, subject_type, subject_id, severity_id,
                    message, created_by_id, created_at, updated_at
                ) VALUES (
                    CAST(:alert_type AS uuid),
                    'core.ipr', CAST(:ipr_id AS uuid), CAST(:sev AS uuid),
                    :msg, CAST(:uid AS uuid), NOW(), NOW()
                )
            """),
            {
                "alert_type": str(alert_type_id),
                "ipr_id": str(ipr["id"]),
                "sev": str(alert_severity_id),
                "msg": f"Admisibilidad excede plazo SLA para {ipr['codigo_bip']} ({track_label}): {days_in} días (máx {max_days}d)",
                "uid": str(user["id"]),
            },
        )
        created += 1
        if ipr["assignee_id"]:
            try:
                await create_notification(
                    db=db,
                    user_id=ipr["assignee_id"],
                    title=f"Admisibilidad pendiente: {ipr['codigo_bip']}",
                    body=f"Admisibilidad excede plazo SLA: {days_in} días (máx {max_days}d)",
                    category="sla",
                    entity_type="core.ipr",
                    entity_id=ipr["id"],
                    link=f"/ipr/{ipr['id']}?tab=admisibilidad",
                )
            except Exception:
                pass

    await db.commit()
    return {"checked": len(iprs), "alerts_created": created}


# ---------------------------------------------------------------------------
# POST /api/ipr/check-track-phase-slas — Batch check phase timing per track
# ---------------------------------------------------------------------------

@router.post("/check-track-phase-slas")
async def check_track_phase_slas(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Compare phase_entered_at vs financing_track.sla_days per phase."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DGI", "ESP_CONTROL_GESTION")

    iprs = (await db.execute(
        text("""
            SELECT i.id, i.codigo_bip, i.name, i.phase_entered_at,
                   i.assignee_id,
                   s.code AS status_code, mcd.code AS mcd_phase,
                   ft.sla_days, ft.label AS track_label
            FROM core.ipr i
            JOIN ref.category s ON s.id = i.status_id
            LEFT JOIN ref.category mcd ON mcd.id = i.mcd_phase_id
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            LEFT JOIN core.financing_track ft ON ft.code = m.code AND ft.is_active = TRUE
            WHERE i.deleted_at IS NULL
              AND i.phase_entered_at IS NOT NULL
              AND ft.sla_days IS NOT NULL
              AND s.code NOT IN ('CERRADO', 'ANULADO', 'TERMINADO_ANTICIPADAMENTE')
        """),
    )).mappings().all()

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    alert_severity_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_level' AND code = 'ATENCION'"),
    )).scalar()
    alert_type_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_type' AND code = 'PLAZO_LEGAL'"),
    )).scalar()
    created = 0

    for ipr in iprs:
        sla = ipr["sla_days"] or {}
        phase = ipr["mcd_phase"] or ""
        phase_key = f"{phase}_max_days"
        max_days = sla.get(phase_key)
        if not max_days:
            max_days = sla.get(f"{ipr['status_code']}_max_days")
        if not max_days:
            continue

        entered = ipr["phase_entered_at"]
        if entered.tzinfo is None:
            entered = entered.replace(tzinfo=timezone.utc)
        days_in = (now - entered).days
        if days_in <= max_days:
            continue

        existing = (await db.execute(
            text("""
                SELECT id FROM core.alert
                WHERE subject_type = 'core.ipr' AND subject_id = CAST(:ipr_id AS uuid)
                  AND message LIKE '%fase excede plazo%'
                  AND created_at::date = CURRENT_DATE
            """),
            {"ipr_id": str(ipr["id"])},
        )).first()
        if existing:
            continue

        track_label = ipr["track_label"] or "sin track"
        await db.execute(
            text("""
                INSERT INTO core.alert (
                    alert_type_id, subject_type, subject_id, severity_id,
                    message, created_by_id, created_at, updated_at
                ) VALUES (
                    CAST(:alert_type AS uuid),
                    'core.ipr', CAST(:ipr_id AS uuid), CAST(:sev AS uuid),
                    :msg, CAST(:uid AS uuid), NOW(), NOW()
                )
            """),
            {
                "alert_type": str(alert_type_id),
                "ipr_id": str(ipr["id"]),
                "sev": str(alert_severity_id),
                "msg": f"Fase {phase} excede plazo SLA para {ipr['codigo_bip']} ({track_label}): {days_in} días (máx {max_days}d)",
                "uid": str(user["id"]),
            },
        )
        created += 1
        if ipr["assignee_id"]:
            try:
                await create_notification(
                    db=db,
                    user_id=ipr["assignee_id"],
                    title=f"Fase excedida: {ipr['codigo_bip']}",
                    body=f"Fase {phase} excede plazo SLA: {days_in} días (máx {max_days}d)",
                    category="sla",
                    entity_type="core.ipr",
                    entity_id=ipr["id"],
                    link=f"/ipr/{ipr['id']}",
                )
            except Exception:
                pass

    await db.commit()
    return {"checked": len(iprs), "alerts_created": created}
