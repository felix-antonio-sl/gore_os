"""
Bottleneck Detection & Investigation router (CG-019..023).

Provides automated scan for operational bottlenecks (acumulacion, ciclo_tiempo,
presupuesto) and a full CRUD for investigation lifecycle with FSM transitions.
"""

import math
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import DGI_ROLES

from app.schemas.dgi import (
    BottleneckFinding,
    BottleneckInvestigationCreate,
    BottleneckInvestigationUpdate,
    BottleneckInvestigationItem,
    BottleneckInvestigationDetail,
    BottleneckSummary,
)

router = APIRouter(prefix="/api/dgi/data/bottlenecks", tags=["dgi"])

# ---------------------------------------------------------------------------
# FSM: allowed transitions
# ---------------------------------------------------------------------------
_FSM: dict[str, set[str]] = {
    "DETECTADO":    {"VERIFICADO", "CERRADO"},
    "VERIFICADO":   {"ANALIZADO", "CERRADO"},
    "ANALIZADO":    {"PROPUESTO", "CERRADO"},
    "PROPUESTO":    {"IMPLEMENTADO", "CERRADO"},
    "IMPLEMENTADO": {"CERRADO"},
    "CERRADO":      set(),
}

# PATCH field allowlist — must match DB column names exactly
_FIELD_ALLOWLIST = {
    "problem", "verification", "root_cause_analysis",
    "proposal", "communication", "follow_up",
}

# Roles allowed to create/update investigations
_WRITE_ROLES = {"ESP_CONTROL_GESTION", "JEFE_DGI"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_dgi(user: dict) -> None:
    if user.get("role_code") not in DGI_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo roles DGI pueden acceder a cuellos de botella",
        )


def _require_write(user: dict) -> None:
    if user.get("role_code") not in _WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo ESP_CONTROL_GESTION o JEFE_DGI pueden gestionar investigaciones",
        )


async def _next_bn_code(db: AsyncSession) -> str:
    """Generate next BN-{year}-{seq:04d} code with advisory lock."""
    year = date.today().year
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('bottleneck_code'))"))
    result = await db.execute(
        text("""
            SELECT MAX(CAST(SUBSTRING(code FROM 9) AS INTEGER)) AS max_seq
            FROM core.dgi_bottleneck_investigation
            WHERE code ~ :pattern
        """),
        {"pattern": f"^BN-{year}-[0-9]+$"},
    )
    max_seq = result.scalar() or 0
    return f"BN-{year}-{max_seq + 1:04d}"


async def _get_status_id(db: AsyncSession, code: str) -> str:
    """Resolve dgi_bottleneck_status code to UUID. Raises 400 if not found."""
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'dgi_bottleneck_status' AND code = :code"),
        {"code": code},
    )).mappings().first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado de cuello de botella inválido: {code}",
        )
    return str(row["id"])


def _row_to_item(r: dict) -> BottleneckInvestigationItem:
    return BottleneckInvestigationItem(
        id=r["id"],
        code=r["code"],
        status=r["status"],
        status_label=r["status_label"],
        division_id=r["division_id"],
        division_name=r["division_name"],
        detection_type=r["detection_type"],
        detection_value=r["detection_value"],
        detection_threshold=r["detection_threshold"],
        problem=r["problem"],
        detected_at=r["detected_at"],
        closed_at=r["closed_at"],
        created_by_name=r.get("created_by_name"),
        updated_at=r["updated_at"],
    )


def _row_to_detail(r: dict) -> BottleneckInvestigationDetail:
    return BottleneckInvestigationDetail(
        id=r["id"],
        code=r["code"],
        status=r["status"],
        status_label=r["status_label"],
        division_id=r["division_id"],
        division_name=r["division_name"],
        detection_type=r["detection_type"],
        detection_value=r["detection_value"],
        detection_threshold=r["detection_threshold"],
        problem=r["problem"],
        detected_at=r["detected_at"],
        closed_at=r["closed_at"],
        created_by_name=r.get("created_by_name"),
        updated_at=r["updated_at"],
        indicator_id=r.get("indicator_id"),
        process_id=r.get("process_id"),
        verification=r.get("verification"),
        root_cause_analysis=r.get("root_cause_analysis"),
        proposal=r.get("proposal"),
        communication=r.get("communication"),
        follow_up=r.get("follow_up"),
    )


_LIST_COLS = """
    b.id,
    b.code,
    st.code         AS status,
    st.label        AS status_label,
    b.division_id,
    org.name        AS division_name,
    b.detection_type,
    b.detection_value,
    b.detection_threshold,
    b.problem,
    b.detected_at,
    b.closed_at,
    b.updated_at,
    p.names || ' ' || p.paternal_surname AS created_by_name
"""

_LIST_FROM = """
    FROM core.dgi_bottleneck_investigation b
    JOIN ref.category st ON st.id = b.status_id
    LEFT JOIN core.organization org ON org.id = b.division_id
    LEFT JOIN core."user" u ON u.id = b.created_by_id
    LEFT JOIN core.person p ON p.id = u.person_id
"""

_DETAIL_COLS = _LIST_COLS + """,
    b.indicator_id,
    b.process_id,
    b.verification,
    b.root_cause_analysis,
    b.proposal,
    b.communication,
    b.follow_up
"""


# ---------------------------------------------------------------------------
# Detection helpers (scan engine)
# ---------------------------------------------------------------------------

async def _detect_acumulacion(
    db: AsyncSession, threshold: int,
) -> list[BottleneckFinding]:
    """
    Detect divisions where PENDIENTE commitments + ABIERTO problems exceed
    the threshold. Commitments are grouped via ipr_id -> core.ipr.sponsor_division_id.
    Problems are grouped via ipr_id -> core.ipr.sponsor_division_id.
    """
    sql = text("""
        WITH division_load AS (
            SELECT
                div.id          AS division_id,
                div.name        AS division_name,
                COALESCE(oc_cnt.pending_commitments, 0) AS pending_commitments,
                COALESCE(pr_cnt.open_problems, 0)       AS open_problems
            FROM core.organization div
            JOIN ref.category ot ON ot.id = div.org_type_id
            LEFT JOIN (
                SELECT ipr.sponsor_division_id AS division_id, COUNT(*) AS pending_commitments
                FROM core.operational_commitment oc
                JOIN ref.category s ON s.id = oc.state_id
                JOIN core.ipr ipr ON ipr.id = oc.ipr_id
                WHERE s.code = 'PENDIENTE' AND oc.deleted_at IS NULL
                GROUP BY ipr.sponsor_division_id
            ) oc_cnt ON oc_cnt.division_id = div.id
            LEFT JOIN (
                SELECT ipr.sponsor_division_id AS division_id, COUNT(*) AS open_problems
                FROM core.ipr_problem pr
                JOIN ref.category s ON s.id = pr.state_id
                JOIN core.ipr ipr ON ipr.id = pr.ipr_id
                WHERE s.code = 'ABIERTO' AND pr.deleted_at IS NULL
                GROUP BY ipr.sponsor_division_id
            ) pr_cnt ON pr_cnt.division_id = div.id
            WHERE ot.code = 'DIVISION' AND div.deleted_at IS NULL
        )
        SELECT *,
               (pending_commitments + open_problems) AS total_load
        FROM division_load
        WHERE (pending_commitments + open_problems) > :threshold
        ORDER BY (pending_commitments + open_problems) DESC
    """)
    rows = (await db.execute(sql, {"threshold": threshold})).mappings().all()

    findings: list[BottleneckFinding] = []
    for r in rows:
        total = int(r["total_load"])
        severity = "ALTO" if total > threshold * 1.5 else "MEDIO"
        findings.append(BottleneckFinding(
            finding_type="ACUMULACION",
            division_id=r["division_id"],
            division_name=r["division_name"],
            description=(
                f"{r['division_name']}: {r['pending_commitments']} compromisos pendientes + "
                f"{r['open_problems']} problemas abiertos = {total} items acumulados"
            ),
            detection_value=float(total),
            detection_threshold=float(threshold),
            severity=severity,
            pending_commitments=int(r["pending_commitments"]),
            open_problems=int(r["open_problems"]),
        ))
    return findings


async def _detect_ciclo_tiempo(db: AsyncSession) -> list[BottleneckFinding]:
    """
    Detect divisions where the average days-in-PENDIENTE for commitments
    exceeds the 90-day historical average by more than 50%.
    """
    sql = text("""
        WITH division_avg AS (
            SELECT
                ipr.sponsor_division_id AS division_id,
                div.name                AS division_name,
                AVG(EXTRACT(EPOCH FROM (NOW() - oc.created_at)) / 86400) AS current_avg_days
            FROM core.operational_commitment oc
            JOIN ref.category s ON s.id = oc.state_id
            JOIN core.ipr ipr ON ipr.id = oc.ipr_id
            JOIN core.organization div ON div.id = ipr.sponsor_division_id
            WHERE s.code = 'PENDIENTE' AND oc.deleted_at IS NULL
            GROUP BY ipr.sponsor_division_id, div.name
        ),
        historical AS (
            SELECT
                AVG(EXTRACT(EPOCH FROM (COALESCE(oc.completed_at, NOW()) - oc.created_at)) / 86400) AS hist_avg_days
            FROM core.operational_commitment oc
            JOIN ref.category s ON s.id = oc.state_id
            WHERE oc.deleted_at IS NULL
              AND oc.created_at >= NOW() - INTERVAL '90 days'
        )
        SELECT
            da.division_id,
            da.division_name,
            da.current_avg_days,
            COALESCE(h.hist_avg_days, da.current_avg_days) AS historical_avg_days,
            CASE
                WHEN COALESCE(h.hist_avg_days, 0) > 0
                THEN ((da.current_avg_days - h.hist_avg_days) / h.hist_avg_days) * 100
                ELSE 0
            END AS delta_pct
        FROM division_avg da
        CROSS JOIN historical h
        WHERE COALESCE(h.hist_avg_days, 0) > 0
          AND ((da.current_avg_days - h.hist_avg_days) / h.hist_avg_days) > 0.5
        ORDER BY delta_pct DESC
    """)
    rows = (await db.execute(sql)).mappings().all()

    findings: list[BottleneckFinding] = []
    for r in rows:
        delta = float(r["delta_pct"])
        severity = "ALTO" if delta > 75 else "MEDIO"
        findings.append(BottleneckFinding(
            finding_type="CICLO_TIEMPO",
            division_id=r["division_id"],
            division_name=r["division_name"],
            description=(
                f"{r['division_name']}: promedio actual {r['current_avg_days']:.0f}d vs "
                f"histórico {r['historical_avg_days']:.0f}d (+{delta:.0f}%)"
            ),
            detection_value=round(float(r["current_avg_days"]), 2),
            detection_threshold=round(float(r["historical_avg_days"]), 2),
            severity=severity,
            current_avg_days=round(float(r["current_avg_days"]), 2),
            historical_avg_days=round(float(r["historical_avg_days"]), 2),
            delta_pct=round(delta, 2),
        ))
    return findings


async def _detect_presupuesto(db: AsyncSession) -> list[BottleneckFinding]:
    """
    Detect budget programs with paid execution < 40% in Q3+ of the fiscal year.
    Only flags programs from the current fiscal year and only if we are in Q3 or Q4.
    """
    today = date.today()
    current_quarter = (today.month - 1) // 3 + 1
    if current_quarter < 3:
        return []  # Only flag in Q3+

    sql = text("""
        SELECT
            bp.id,
            bp.code,
            bp.name                AS program_name,
            org.id                 AS division_id,
            org.name               AS division_name,
            bp.current_amount,
            bp.paid_amount,
            CASE
                WHEN COALESCE(bp.current_amount, 0) > 0
                THEN (COALESCE(bp.paid_amount, 0) / bp.current_amount) * 100
                ELSE 0
            END                    AS execution_pct
        FROM core.budget_program bp
        LEFT JOIN core.organization org ON org.id = bp.owner_division_id
        WHERE bp.fiscal_year = :year
          AND bp.deleted_at IS NULL
          AND COALESCE(bp.current_amount, 0) > 0
          AND (COALESCE(bp.paid_amount, 0) / bp.current_amount) < 0.40
        ORDER BY (COALESCE(bp.paid_amount, 0) / bp.current_amount) ASC
        LIMIT 20
    """)
    rows = (await db.execute(sql, {"year": today.year})).mappings().all()

    findings: list[BottleneckFinding] = []
    for r in rows:
        pct = float(r["execution_pct"])
        severity = "ALTO" if pct < 20 else "MEDIO"
        findings.append(BottleneckFinding(
            finding_type="PRESUPUESTO",
            division_id=r["division_id"],
            division_name=r["division_name"],
            description=(
                f"Programa {r['code']} ({r['program_name']}): "
                f"ejecución {pct:.1f}% en Q{current_quarter}"
            ),
            detection_value=round(pct, 2),
            detection_threshold=40.0,
            severity=severity,
            execution_pct=round(pct, 2),
            program_name=r["program_name"],
        ))
    return findings


# ---------------------------------------------------------------------------
# Public helper: reusable from cockpit without circular imports
# ---------------------------------------------------------------------------

async def fetch_bottleneck_summary(db: AsyncSession) -> BottleneckSummary:
    """Build BottleneckSummary from DB. Callable from cockpit or router."""
    # Count active (not CERRADO)
    total_row = (await db.execute(text("""
        SELECT COUNT(*) AS cnt
        FROM core.dgi_bottleneck_investigation b
        JOIN ref.category st ON st.id = b.status_id
        WHERE st.code != 'CERRADO' AND b.deleted_at IS NULL
    """))).mappings().first()
    total_active = int(total_row["cnt"]) if total_row else 0

    # By status
    status_rows = (await db.execute(text("""
        SELECT st.code, st.label, COUNT(*) AS cnt
        FROM core.dgi_bottleneck_investigation b
        JOIN ref.category st ON st.id = b.status_id
        WHERE b.deleted_at IS NULL
        GROUP BY st.code, st.label
        ORDER BY st.code
    """))).mappings().all()
    by_status = [{"code": r["code"], "label": r["label"], "count": r["cnt"]} for r in status_rows]

    # By division
    division_rows = (await db.execute(text("""
        SELECT org.name AS division_name, COUNT(*) AS cnt
        FROM core.dgi_bottleneck_investigation b
        JOIN ref.category st ON st.id = b.status_id
        LEFT JOIN core.organization org ON org.id = b.division_id
        WHERE st.code != 'CERRADO' AND b.deleted_at IS NULL
        GROUP BY org.name
        ORDER BY cnt DESC
    """))).mappings().all()
    by_division = [{"division_name": r["division_name"], "count": r["cnt"]} for r in division_rows]

    # Critical count: DETECTADO + VERIFICADO
    critical_row = (await db.execute(text("""
        SELECT COUNT(*) AS cnt
        FROM core.dgi_bottleneck_investigation b
        JOIN ref.category st ON st.id = b.status_id
        WHERE st.code IN ('DETECTADO', 'VERIFICADO') AND b.deleted_at IS NULL
    """))).mappings().first()
    critical_count = int(critical_row["cnt"]) if critical_row else 0

    return BottleneckSummary(
        total_active=total_active,
        by_status=by_status,
        by_division=by_division,
        critical_count=critical_count,
    )


# ---------------------------------------------------------------------------
# 1. GET /scan — Automated bottleneck detection
# ---------------------------------------------------------------------------
@router.get("/scan", response_model=list[BottleneckFinding])
async def scan_bottlenecks(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    threshold_acumulacion: int = Query(10, ge=1, description="Umbral de acumulación por división"),
):
    """
    Run automated bottleneck detection queries.

    Three detection types:
    - ACUMULACION: divisions with PENDIENTE commitments + ABIERTO problems > threshold
    - CICLO_TIEMPO: divisions where avg days-in-state exceeds 90d historical by > 50%
    - PRESUPUESTO: budget programs with execution < 40% in Q3+
    """
    _require_dgi(user)

    findings: list[BottleneckFinding] = []
    findings.extend(await _detect_acumulacion(db, threshold_acumulacion))
    findings.extend(await _detect_ciclo_tiempo(db))
    findings.extend(await _detect_presupuesto(db))
    return findings


# ---------------------------------------------------------------------------
# 2. GET /summary — Aggregated summary for cockpit
# ---------------------------------------------------------------------------
@router.get("/summary", response_model=BottleneckSummary)
async def get_summary(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Summary of active bottleneck investigations for the cockpit widget.
    """
    _require_dgi(user)
    return await fetch_bottleneck_summary(db)


# ---------------------------------------------------------------------------
# 3. GET / — Paginated list
# ---------------------------------------------------------------------------
@router.get("")
async def list_investigations(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    division_id: UUID | None = None,
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    Paginated list of bottleneck investigations with optional filters.
    """
    _require_dgi(user)

    conditions = ["b.deleted_at IS NULL"]
    params: dict = {}

    if division_id:
        conditions.append("b.division_id = :division_id")
        params["division_id"] = str(division_id)

    if status_filter:
        conditions.append("st.code = :status_filter")
        params["status_filter"] = status_filter.upper()

    where_clause = " AND ".join(conditions)

    # Count
    count_result = await db.execute(
        text(f"SELECT COUNT(*) {_LIST_FROM} WHERE {where_clause}"),
        params,
    )
    total = count_result.scalar() or 0
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    # Fetch page
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(
        text(f"""
            SELECT {_LIST_COLS}
            {_LIST_FROM}
            WHERE {where_clause}
            ORDER BY b.detected_at DESC
            LIMIT :limit OFFSET :offset
        """),
        params,
    )).mappings().all()

    items = [_row_to_item(dict(r)) for r in rows]

    return {
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------------------
# 4. POST / — Create investigation
# ---------------------------------------------------------------------------
@router.post("", status_code=status.HTTP_201_CREATED, response_model=BottleneckInvestigationDetail)
async def create_investigation(
    body: BottleneckInvestigationCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new bottleneck investigation. Initial status: DETECTADO.
    """
    _require_write(user)

    status_id = await _get_status_id(db, "DETECTADO")
    code = await _next_bn_code(db)

    result = await db.execute(
        text("""
            INSERT INTO core.dgi_bottleneck_investigation
                (code, status_id, division_id, indicator_id, process_id,
                 detection_type, detection_value, detection_threshold,
                 problem, created_by_id)
            VALUES
                (:code, :status_id, :division_id, :indicator_id, :process_id,
                 :detection_type, :detection_value, :detection_threshold,
                 :problem, :created_by_id)
            RETURNING id
        """),
        {
            "code": code,
            "status_id": status_id,
            "division_id": str(body.division_id) if body.division_id else None,
            "indicator_id": str(body.indicator_id) if body.indicator_id else None,
            "process_id": str(body.process_id) if body.process_id else None,
            "detection_type": body.detection_type,
            "detection_value": body.detection_value,
            "detection_threshold": body.detection_threshold,
            "problem": body.problem,
            "created_by_id": str(user["id"]),
        },
    )
    new_id = str(result.scalar())
    await db.commit()

    # Fetch full detail
    row = (await db.execute(
        text(f"SELECT {_DETAIL_COLS} {_LIST_FROM} WHERE b.id = :id"),
        {"id": new_id},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al recuperar investigación creada")
    return _row_to_detail(dict(row))


# ---------------------------------------------------------------------------
# 5. GET /{id} — Detail
# ---------------------------------------------------------------------------
@router.get("/{investigation_id}", response_model=BottleneckInvestigationDetail)
async def get_investigation(
    investigation_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Full detail of a bottleneck investigation.
    """
    _require_dgi(user)

    row = (await db.execute(
        text(f"SELECT {_DETAIL_COLS} {_LIST_FROM} WHERE b.id = :id AND b.deleted_at IS NULL"),
        {"id": str(investigation_id)},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigación no encontrada")
    return _row_to_detail(dict(row))


# ---------------------------------------------------------------------------
# 6. PATCH /{id} — Update with FSM validation
# ---------------------------------------------------------------------------
@router.patch("/{investigation_id}", response_model=BottleneckInvestigationDetail)
async def update_investigation(
    investigation_id: UUID,
    body: BottleneckInvestigationUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Update investigation fields and/or transition status via FSM.

    Allowlisted fields: problem, verification, root_cause_analysis,
    proposal, communication, follow_up.

    Status transitions follow the FSM: DETECTADO -> VERIFICADO -> ANALIZADO
    -> PROPUESTO -> IMPLEMENTADO -> CERRADO (any state can jump to CERRADO).
    """
    _require_write(user)

    investigation_id_str = str(investigation_id)

    # Fetch current record
    existing = (await db.execute(
        text(f"""
            SELECT b.id, st.code AS current_status
            {_LIST_FROM}
            WHERE b.id = :id AND b.deleted_at IS NULL
        """),
        {"id": investigation_id_str},
    )).mappings().first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigación no encontrada")

    current_status = existing["current_status"]

    # Build update sets
    updates: dict = {}
    params: dict = {"id": investigation_id_str}

    # Field updates from allowlist
    body_data = body.model_dump(exclude_none=True)
    for field in _FIELD_ALLOWLIST:
        if field in body_data:
            updates[field] = body_data[field]

    # Status transition
    if body.status is not None:
        target = body.status.upper()
        allowed = _FSM.get(current_status, set())
        if target not in allowed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Transición inválida: {current_status} -> {target}. "
                    f"Transiciones permitidas: {', '.join(sorted(allowed)) if allowed else 'ninguna'}"
                ),
            )
        new_status_id = await _get_status_id(db, target)
        updates["status_id"] = new_status_id

        # If closing, set closed_at
        if target == "CERRADO":
            updates["closed_at"] = "NOW()"

    if not updates:
        # No changes — return current state
        row = (await db.execute(
            text(f"SELECT {_DETAIL_COLS} {_LIST_FROM} WHERE b.id = :id AND b.deleted_at IS NULL"),
            {"id": investigation_id_str},
        )).mappings().first()
        return _row_to_detail(dict(row))

    # Build SET clause — special handling for closed_at = NOW()
    set_parts = []
    for k, v in updates.items():
        if k == "closed_at" and v == "NOW()":
            set_parts.append("closed_at = NOW()")
        else:
            set_parts.append(f"{k} = :{k}")
            params[k] = v

    set_parts.append("updated_at = NOW()")
    set_clause = ", ".join(set_parts)

    await db.execute(
        text(f"UPDATE core.dgi_bottleneck_investigation SET {set_clause} WHERE id = :id"),
        params,
    )
    await db.commit()

    # Return updated detail
    row = (await db.execute(
        text(f"SELECT {_DETAIL_COLS} {_LIST_FROM} WHERE b.id = :id"),
        {"id": investigation_id_str},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al recuperar investigación actualizada")
    return _row_to_detail(dict(row))


# ---------------------------------------------------------------------------
# 7. DELETE /{id} — Soft delete
# ---------------------------------------------------------------------------
@router.delete("/{investigation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investigation(
    investigation_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Soft-delete a bottleneck investigation.
    """
    _require_write(user)

    result = await db.execute(
        text("""
            UPDATE core.dgi_bottleneck_investigation
            SET deleted_at = NOW(), updated_at = NOW()
            WHERE id = :id AND deleted_at IS NULL
        """),
        {"id": str(investigation_id)},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigación no encontrada")
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
