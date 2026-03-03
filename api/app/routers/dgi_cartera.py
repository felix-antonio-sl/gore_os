"""
DGI Cartera IPR — Portfolio control endpoints.

Aggregates data from IPR, agreements, budget, resolutions, problems,
alerts and commitments into a unified portfolio view for DGI users.
"""
import math
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import DGI_ROLES
from app.schemas.cartera import CarteraIPRItem, CarteraSummary, CuotaVencidaItem

router = APIRouter(prefix="/api/dgi/cartera", tags=["dgi"])


def _require_dgi(user: dict) -> None:
    if user["role_code"] not in DGI_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo roles DGI pueden acceder a la cartera",
        )


# ---------------------------------------------------------------------------
# Health signal computation (shared between list + summary for coherence)
# ---------------------------------------------------------------------------

def _compute_health_signal(row: dict) -> tuple[str, list[str]]:
    """
    Coalgebra observacional: IPR metrics → (signal, reasons).

    ROJO: cuotas vencidas, alertas críticas, desfase >20%, >180d sin update,
          compromisos vencidos.
    AMARILLO: alertas activas, problemas abiertos, >90d sin update,
             ejecución <30% en F4/F5.
    VERDE: todo en orden.
    """
    reasons: list[str] = []

    # --- ROJO conditions ---
    if row["overdue_installments"] > 0:
        reasons.append(f"{row['overdue_installments']} cuota(s) vencida(s)")
    if row["critical_alerts"] > 0:
        reasons.append(f"{row['critical_alerts']} alerta(s) crítica(s)")

    phys = row["physical_progress"]
    fin = row["financial_progress"]
    if phys is not None and fin is not None:
        gap = abs(float(phys) - float(fin))
        if gap > 20:
            reasons.append(f"Desfase físico-financiero {gap:.0f}%")

    if row["days_since_update"] > 180:
        reasons.append(f"{row['days_since_update']}d sin actualización")

    if row["overdue_commitments"] > 0:
        reasons.append(f"{row['overdue_commitments']} compromiso(s) vencido(s)")

    if reasons:
        return "ROJO", reasons

    # --- AMARILLO conditions ---
    amarillo_reasons: list[str] = []

    if row["active_alerts"] > 0:
        amarillo_reasons.append(f"{row['active_alerts']} alerta(s) activa(s)")
    if row["open_problems"] > 0:
        amarillo_reasons.append(f"{row['open_problems']} problema(s) abierto(s)")
    if row["days_since_update"] > 90:
        amarillo_reasons.append(f"{row['days_since_update']}d sin actualización")

    phase = row.get("mcd_phase")
    exec_pct = row.get("budget_execution_pct")
    if phase in ("F4", "F5") and exec_pct is not None and exec_pct < 30:
        amarillo_reasons.append(f"Ejecución {exec_pct:.0f}% en {phase}")

    if amarillo_reasons:
        return "AMARILLO", amarillo_reasons

    return "VERDE", []


# ---------------------------------------------------------------------------
# Base SQL query (reused by list + summary)
# ---------------------------------------------------------------------------

_BASE_SQL = """
SELECT
    i.id,
    i.codigo_bip,
    i.name,
    mech.code                   AS mechanism,
    ph.code                     AS mcd_phase,
    div.name                    AS division_name,
    div.id                      AS division_id,
    CAST(i.metadata->>'monto_total' AS numeric) AS monto_total,
    EXTRACT(DAY FROM CURRENT_TIMESTAMP - i.updated_at)::int AS days_since_update,

    -- Latest progress report
    pr.physical_progress,
    pr.financial_progress,

    -- Budget (CDPs)
    COALESCE(bc.cdp_total, 0)   AS cdp_total,
    COALESCE(bc.cdp_paid, 0)    AS cdp_paid,
    CASE
        WHEN CAST(i.metadata->>'monto_total' AS numeric) > 0
        THEN ROUND(COALESCE(bc.cdp_paid, 0)::numeric
             / CAST(i.metadata->>'monto_total' AS numeric) * 100, 1)
        ELSE NULL
    END                         AS budget_execution_pct,

    -- Agreements
    COALESCE(ag.agreement_count, 0)      AS agreement_count,
    ag.agreement_latest_state,
    COALESCE(ag.overdue_installments, 0) AS overdue_installments,

    -- Resolutions
    COALESCE(res.resolution_count, 0) AS resolution_count,
    COALESCE(res.pending_cgr, 0)      AS pending_cgr,

    -- Problems
    COALESCE(prob.open_problems, 0)   AS open_problems,

    -- Alerts
    COALESCE(al.active_alerts, 0)     AS active_alerts,
    COALESCE(al.critical_alerts, 0)   AS critical_alerts,

    -- Commitments
    COALESCE(com.overdue_commitments, 0) AS overdue_commitments

FROM core.ipr i
LEFT JOIN ref.category mech ON mech.id = i.mechanism_id
LEFT JOIN ref.category ph   ON ph.id = i.mcd_phase_id
LEFT JOIN core.organization div ON div.id = i.sponsor_division_id

-- Latest progress report
LEFT JOIN LATERAL (
    SELECT pr2.physical_progress, pr2.financial_progress
    FROM core.progress_report pr2
    WHERE pr2.ipr_id = i.id AND pr2.deleted_at IS NULL
    ORDER BY pr2.report_date DESC
    LIMIT 1
) pr ON TRUE

-- Budget commitments
LEFT JOIN LATERAL (
    SELECT
        SUM(bc2.amount) AS cdp_total,
        SUM(bc2.amount) FILTER (WHERE ps.code = 'PAGADO') AS cdp_paid
    FROM core.budget_commitment bc2
    LEFT JOIN ref.category ps ON ps.id = bc2.status_id
    WHERE bc2.ipr_id = i.id AND bc2.deleted_at IS NULL
) bc ON TRUE

-- Agreements + installments
LEFT JOIN LATERAL (
    SELECT
        COUNT(DISTINCT a2.id) AS agreement_count,
        (
            SELECT st.code
            FROM core.agreement a3
            JOIN ref.category st ON st.id = a3.state_id
            WHERE a3.ipr_id = i.id AND a3.deleted_at IS NULL
            ORDER BY a3.updated_at DESC
            LIMIT 1
        ) AS agreement_latest_state,
        COUNT(ai2.id) FILTER (
            WHERE ai2.due_date < CURRENT_DATE
              AND pst.code != 'PAGADA'
        ) AS overdue_installments
    FROM core.agreement a2
    LEFT JOIN core.agreement_installment ai2 ON ai2.agreement_id = a2.id
    LEFT JOIN ref.category pst ON pst.id = ai2.payment_status_id
    WHERE a2.ipr_id = i.id AND a2.deleted_at IS NULL
) ag ON TRUE

-- Resolutions
LEFT JOIN LATERAL (
    SELECT
        COUNT(*) AS resolution_count,
        COUNT(*) FILTER (WHERE ast.code = 'ENVIADO_CGR') AS pending_cgr
    FROM core.resolution r2
    JOIN core.administrative_act aa ON aa.id = r2.administrative_act_id
    JOIN ref.category ast ON ast.id = aa.state_id
    WHERE r2.ipr_id = i.id AND r2.deleted_at IS NULL AND aa.deleted_at IS NULL
) res ON TRUE

-- Open problems
LEFT JOIN LATERAL (
    SELECT COUNT(*) AS open_problems
    FROM core.ipr_problem p2
    JOIN ref.category pst ON pst.id = p2.state_id
    WHERE p2.ipr_id = i.id
      AND pst.code IN ('ABIERTO', 'EN_GESTION')
      AND p2.deleted_at IS NULL
) prob ON TRUE

-- Active alerts
LEFT JOIN LATERAL (
    SELECT
        COUNT(*) AS active_alerts,
        COUNT(*) FILTER (WHERE sev.code = 'CRITICO') AS critical_alerts
    FROM core.alert al2
    JOIN ref.category sev ON sev.id = al2.severity_id
    WHERE al2.subject_type = 'core.ipr'
      AND al2.subject_id = i.id
      AND al2.resolved_at IS NULL
      AND al2.deleted_at IS NULL
) al ON TRUE

-- Overdue commitments
LEFT JOIN LATERAL (
    SELECT COUNT(*) AS overdue_commitments
    FROM core.operational_commitment oc2
    JOIN ref.category cst ON cst.id = oc2.state_id
    WHERE oc2.ipr_id = i.id
      AND cst.code IN ('PENDIENTE', 'EN_PROGRESO')
      AND oc2.due_date < CURRENT_DATE
      AND oc2.deleted_at IS NULL
) com ON TRUE

WHERE i.deleted_at IS NULL
"""


def _build_filters(
    division_id: UUID | None,
    mechanism: str | None,
    mcd_phase: str | None,
    search: str | None,
    has_overdue_installments: bool | None,
) -> tuple[str, dict]:
    """Build WHERE clauses and params dict from filter args."""
    clauses: list[str] = []
    params: dict = {}

    if division_id:
        clauses.append("div.id = :division_id")
        params["division_id"] = str(division_id)

    if mechanism:
        clauses.append("mech.code = :mechanism")
        params["mechanism"] = mechanism.upper()

    if mcd_phase:
        clauses.append("ph.code = :mcd_phase")
        params["mcd_phase"] = mcd_phase.upper()

    if search:
        clauses.append("(i.codigo_bip ILIKE :search OR i.name ILIKE :search)")
        params["search"] = f"%{search}%"

    if has_overdue_installments:
        clauses.append("COALESCE(ag.overdue_installments, 0) > 0")

    where = (" AND " + " AND ".join(clauses)) if clauses else ""
    return where, params


def _build_order(sort_by: str | None, sort_order: str) -> str:
    """Build ORDER BY clause from sort params."""
    allowed = {
        "codigo_bip": "i.codigo_bip",
        "name": "i.name",
        "mcd_phase": "ph.code",
        "days_since_update": "days_since_update",
        "physical_progress": "pr.physical_progress",
        "overdue_installments": "COALESCE(ag.overdue_installments, 0)",
        "critical_alerts": "COALESCE(al.critical_alerts, 0)",
        "monto_total": "CAST(i.metadata->>'monto_total' AS numeric)",
    }
    col = allowed.get(sort_by or "", "i.codigo_bip")
    direction = "DESC" if sort_order.upper() == "DESC" else "ASC"
    return f"ORDER BY {col} {direction} NULLS LAST"


# ---------------------------------------------------------------------------
# GET /api/dgi/cartera — Paginated IPR portfolio
# ---------------------------------------------------------------------------

@router.get("")
async def list_cartera(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    division_id: UUID | None = Query(None),
    mechanism: str | None = Query(None),
    mcd_phase: str | None = Query(None),
    search: str | None = Query(None),
    has_overdue_installments: bool | None = Query(None),
    health_signal: str | None = Query(None, description="Post-filter: VERDE, AMARILLO, ROJO"),
    sort_by: str | None = Query(None),
    sort_order: str = Query("ASC"),
):
    _require_dgi(user)

    where_extra, params = _build_filters(
        division_id, mechanism, mcd_phase, search, has_overdue_installments
    )
    order = _build_order(sort_by, sort_order)

    # When health_signal filter is active, we fetch all rows and post-filter
    if health_signal:
        sql = text(f"{_BASE_SQL}{where_extra} {order}")
        rows = (await db.execute(sql, params)).mappings().all()
        items = []
        for r in rows:
            sig, reasons = _compute_health_signal(dict(r))
            if sig != health_signal.upper():
                continue
            items.append(CarteraIPRItem(
                **_row_to_item(r, sig, reasons),
            ))
        total = len(items)
        start = (page - 1) * page_size
        paged = items[start : start + page_size]
        return {
            "items": paged,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 1,
        }

    # Normal path: SQL pagination
    count_sql = text(f"SELECT COUNT(*) FROM ({_BASE_SQL}{where_extra}) sub")
    total = (await db.execute(count_sql, params)).scalar() or 0

    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset
    data_sql = text(f"{_BASE_SQL}{where_extra} {order} LIMIT :limit OFFSET :offset")
    rows = (await db.execute(data_sql, params)).mappings().all()

    items = []
    for r in rows:
        sig, reasons = _compute_health_signal(dict(r))
        items.append(CarteraIPRItem(**_row_to_item(r, sig, reasons)))

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 1,
    }


def _row_to_item(r: dict, signal: str, reasons: list[str]) -> dict:
    return {
        "id": r["id"],
        "codigo_bip": r["codigo_bip"],
        "name": r["name"],
        "mechanism": r["mechanism"],
        "mcd_phase": r["mcd_phase"],
        "division_name": r["division_name"],
        "division_id": r["division_id"],
        "monto_total": float(r["monto_total"]) if r["monto_total"] else None,
        "health_signal": signal,
        "health_reasons": reasons,
        "days_since_update": r["days_since_update"] or 0,
        "physical_progress": float(r["physical_progress"]) if r["physical_progress"] is not None else None,
        "financial_progress": float(r["financial_progress"]) if r["financial_progress"] is not None else None,
        "cdp_total": float(r["cdp_total"]),
        "cdp_paid": float(r["cdp_paid"]),
        "budget_execution_pct": float(r["budget_execution_pct"]) if r["budget_execution_pct"] is not None else None,
        "agreement_count": r["agreement_count"],
        "agreement_latest_state": r["agreement_latest_state"],
        "overdue_installments": r["overdue_installments"],
        "resolution_count": r["resolution_count"],
        "pending_cgr": r["pending_cgr"],
        "open_problems": r["open_problems"],
        "active_alerts": r["active_alerts"],
        "critical_alerts": r["critical_alerts"],
        "overdue_commitments": r["overdue_commitments"],
    }


# ---------------------------------------------------------------------------
# GET /api/dgi/cartera/resumen — Portfolio summary
# ---------------------------------------------------------------------------

@router.get("/resumen")
async def cartera_resumen(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    division_id: UUID | None = Query(None),
    mechanism: str | None = Query(None),
    mcd_phase: str | None = Query(None),
    search: str | None = Query(None),
):
    _require_dgi(user)

    where_extra, params = _build_filters(division_id, mechanism, mcd_phase, search, None)
    sql = text(f"{_BASE_SQL}{where_extra}")
    rows = (await db.execute(sql, params)).mappings().all()

    verde = amarillo = rojo = 0
    overdue_total = 0
    cgr_total = 0
    monto_sum = 0.0
    paid_sum = 0.0

    for r in rows:
        sig, _ = _compute_health_signal(dict(r))
        if sig == "VERDE":
            verde += 1
        elif sig == "AMARILLO":
            amarillo += 1
        else:
            rojo += 1
        overdue_total += r["overdue_installments"]
        cgr_total += r["pending_cgr"]
        monto_sum += float(r["monto_total"]) if r["monto_total"] else 0
        paid_sum += float(r["cdp_paid"])

    return CarteraSummary(
        total=len(rows),
        verde=verde,
        amarillo=amarillo,
        rojo=rojo,
        overdue_installments_total=overdue_total,
        pending_cgr_total=cgr_total,
        monto_total=monto_sum,
        total_paid=paid_sum,
    )


# ---------------------------------------------------------------------------
# GET /api/dgi/cartera/cuotas-vencidas — Overdue installments cross-portfolio
# ---------------------------------------------------------------------------

@router.get("/cuotas-vencidas")
async def cuotas_vencidas(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    division_id: UUID | None = Query(None),
):
    _require_dgi(user)

    where_div = ""
    params: dict = {}
    if division_id:
        where_div = "AND div.id = :division_id"
        params["division_id"] = str(division_id)

    count_sql = text(f"""
        SELECT COUNT(*)
        FROM core.agreement_installment ai
        JOIN core.agreement a ON a.id = ai.agreement_id AND a.deleted_at IS NULL
        JOIN ref.category pst ON pst.id = ai.payment_status_id
        LEFT JOIN core.ipr i ON i.id = a.ipr_id
        LEFT JOIN core.organization div ON div.id = i.sponsor_division_id
        WHERE ai.due_date < CURRENT_DATE
          AND pst.code != 'PAGADA'
          {where_div}
    """)
    total = (await db.execute(count_sql, params)).scalar() or 0

    params["limit"] = page_size
    params["offset"] = (page - 1) * page_size

    data_sql = text(f"""
        SELECT
            ai.id,
            i.id            AS ipr_id,
            i.codigo_bip    AS ipr_codigo_bip,
            a.id            AS agreement_id,
            a.agreement_number,
            recv.name       AS counterpart_name,
            ai.installment_number,
            ai.amount,
            ai.due_date,
            (CURRENT_DATE - ai.due_date)::int AS days_overdue
        FROM core.agreement_installment ai
        JOIN core.agreement a ON a.id = ai.agreement_id AND a.deleted_at IS NULL
        JOIN ref.category pst ON pst.id = ai.payment_status_id
        LEFT JOIN core.ipr i ON i.id = a.ipr_id
        LEFT JOIN core.organization div ON div.id = i.sponsor_division_id
        LEFT JOIN core.organization recv ON recv.id = a.receiver_id
        WHERE ai.due_date < CURRENT_DATE
          AND pst.code != 'PAGADA'
          {where_div}
        ORDER BY ai.due_date ASC
        LIMIT :limit OFFSET :offset
    """)
    rows = (await db.execute(data_sql, params)).mappings().all()

    items = [
        CuotaVencidaItem(
            id=r["id"],
            ipr_id=r["ipr_id"],
            ipr_codigo_bip=r["ipr_codigo_bip"],
            agreement_id=r["agreement_id"],
            agreement_number=r["agreement_number"],
            counterpart_name=r["counterpart_name"],
            installment_number=r["installment_number"],
            amount=float(r["amount"]) if r["amount"] else 0,
            due_date=r["due_date"].isoformat() if r["due_date"] else "",
            days_overdue=r["days_overdue"] or 0,
        )
        for r in rows
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 1,
    }
