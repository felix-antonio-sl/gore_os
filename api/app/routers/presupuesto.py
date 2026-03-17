import math
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.audit import record_event
from app.schemas.common import PaginatedResponse
from app.schemas.presupuesto import (
    PresupuestoListItem,
    PresupuestoDetail,
    PresupuestoCreate,
    PresupuestoUpdate,
    PresupuestoResumen,
    CarryoverItem,
    BudgetCommitmentItem,
    BudgetCommitmentCreate,
    BudgetCycleMilestoneItem,
    BudgetCycleTrackingItem,
    BudgetCycleTrackingUpdate,
    BudgetCycleSummary,
)

router = APIRouter(prefix="/api/presupuesto", tags=["presupuesto"])

ADMIN_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "ANALISTA"}
MANAGER_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "GOBERNADOR", "JEFE_DEPARTAMENTO"}


def _require_roles(user: dict, *roles: str) -> None:
    if user["role_code"] not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")


def _execution_pct(paid: float | None, current: float | None) -> float:
    if current and current > 0 and paid is not None:
        return round(float(paid) / float(current) * 100, 1)
    return 0.0


async def _get_glosa_thresholds(db: AsyncSession) -> list[dict]:
    """Load all active glosa thresholds from DB."""
    result = await db.execute(
        text("""
            SELECT code, label, value_pct, source_normativa
            FROM core.financial_threshold
            WHERE enforcement_point = 'GLOSA' AND is_active = TRUE
        """)
    )
    return [dict(r) for r in result.mappings().all()]


# Mapping from glosa threshold codes to budget_item scheme codes
_GLOSA_ITEM_MAP = {
    "GLOSA_ADMIN_MAX": {"BIENES_SERVICIOS_CONSUMO"},
    "GLOSA_HONORARIOS_MAX": {"HONORARIOS"},
    "GLOSA_REMUNERACIONES_MAX": {"PERSONAL"},
    "GLOSA_ANF_MAX": {"ACTIVOS_NO_FINANCIEROS"},
    "GLOSA_EQUIPAMIENTO_MAX": {"EQUIPAMIENTO", "EQUIPAMIENTO_INFORMATICO"},
}


async def check_glosa_rules(ipr_id: UUID, db: AsyncSession) -> list[dict]:
    """Evaluate glosa spending rules for an IPR's linked CDPs.
    Returns list of gate dicts for violations found."""
    gates: list[dict] = []

    glosa_thresholds = await _get_glosa_thresholds(db)
    if not glosa_thresholds:
        return gates

    # Get total budget and per-item breakdown from CDPs linked to this IPR
    result = await db.execute(
        text("""
            SELECT
                COALESCE(SUM(bc.amount), 0) AS total_cdp,
                item_cat.code AS item_code,
                COALESCE(SUM(bc.amount), 0) AS item_amount
            FROM core.budget_commitment bc
            JOIN core.budget_program bp ON bp.id = bc.budget_program_id
            LEFT JOIN ref.category item_cat ON item_cat.id = bp.item_id
            WHERE bc.ipr_id = :ipr_id AND bc.deleted_at IS NULL
            GROUP BY item_cat.code
        """),
        {"ipr_id": str(ipr_id)},
    )
    rows = result.mappings().all()
    if not rows:
        return gates

    # Calculate total
    total_cdp = sum(float(r["item_amount"]) for r in rows)
    if total_cdp <= 0:
        return gates

    # Build item breakdown
    item_amounts: dict[str, float] = {}
    for r in rows:
        code = r["item_code"] or "SIN_ITEM"
        item_amounts[code] = float(r["item_amount"])

    # Check each glosa threshold
    for threshold in glosa_thresholds:
        code = threshold["code"]
        max_pct = float(threshold["value_pct"])
        item_codes = _GLOSA_ITEM_MAP.get(code, set())
        if not item_codes:
            continue

        # Sum all matching item amounts
        matching_amount = sum(item_amounts.get(ic, 0) for ic in item_codes)
        actual_pct = (matching_amount / total_cdp * 100) if total_cdp > 0 else 0

        if actual_pct > max_pct:
            gates.append({
                "name": code.lower(),
                "met": False,
                "detail": (
                    f"{threshold['label']}: {actual_pct:.1f}% excede tope de {max_pct:.0f}% "
                    f"(${matching_amount:,.0f} de ${total_cdp:,.0f} total CDPs)"
                ),
            })
        else:
            gates.append({
                "name": code.lower(),
                "met": True,
                "detail": f"{threshold['label']}: {actual_pct:.1f}% dentro del tope {max_pct:.0f}%",
            })

    # Glosa 03 prohibition: FNDR-funded IPRs cannot have PERSONAL expenditure
    glosa03_gates = await _check_glosa03_prohibition(ipr_id, db)
    gates.extend(glosa03_gates)

    return gates


# Mechanisms that use FNDR funding (Glosa 03 applies)
_FNDR_MECHANISMS = {"SNI", "FRIL", "C33"}


async def _check_glosa03_prohibition(ipr_id: UUID, db: AsyncSession) -> list[dict]:
    """Glosa 03: FNDR-funded IPRs cannot allocate budget to PERSONAL.

    Checks if IPR's mechanism is in {SNI, FRIL, C33} or funding_source is FNDR,
    then verifies no CDPs are linked to budget_programs with item = PERSONAL.
    """
    gates: list[dict] = []

    # Check if IPR uses FNDR-related mechanism or funding source
    ipr_row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code, fs.code AS funding_source_code
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            LEFT JOIN ref.category fs ON fs.id = i.funding_source_id
            WHERE i.id = :ipr_id AND i.deleted_at IS NULL
        """),
        {"ipr_id": str(ipr_id)},
    )).mappings().first()

    if not ipr_row:
        return gates

    mechanism = ipr_row["mechanism_code"]
    funding = ipr_row["funding_source_code"]

    # Only applies if FNDR-related
    is_fndr = mechanism in _FNDR_MECHANISMS or funding == "FNDR"
    if not is_fndr:
        return gates

    # Check for CDPs linked to PERSONAL budget items
    personal_count = (await db.execute(
        text("""
            SELECT COUNT(*) FROM core.budget_commitment bc
            JOIN core.budget_program bp ON bp.id = bc.budget_program_id
            JOIN ref.category item_cat ON item_cat.id = bp.item_id
            WHERE bc.ipr_id = :ipr_id AND bc.deleted_at IS NULL
              AND item_cat.code = 'PERSONAL'
        """),
        {"ipr_id": str(ipr_id)},
    )).scalar() or 0

    if personal_count > 0:
        source = mechanism if mechanism in _FNDR_MECHANISMS else f"FNDR ({funding})"
        gates.append({
            "name": "glosa03_prohibition",
            "met": False,
            "detail": (
                f"Glosa 03: Prohibición de gasto en personal con financiamiento {source}. "
                f"Se encontraron {personal_count} CDP(s) vinculados a ítem PERSONAL"
            ),
        })
    else:
        gates.append({
            "name": "glosa03_prohibition",
            "met": True,
            "detail": "Glosa 03: Sin gasto en personal con financiamiento FNDR",
        })

    return gates


# Glosa 07 transfer limits: admin and honorarios caps (parametric from DB)
_GLOSA07_LIMITS_DEFAULT = {
    "glosa07_admin_max": {"items": {"BIENES_SERVICIOS_CONSUMO", "BIENES_SERVICIOS"}, "max_pct": 5.0,
                          "threshold_key": "glosa07_admin_max_pct",
                          "label": "Glosa 07: Gasto administrativo"},
    "glosa07_honorarios_max": {"items": {"HONORARIOS"}, "max_pct": 5.0,
                               "threshold_key": "glosa07_honorarios_max_pct",
                               "label": "Glosa 07: Honorarios"},
}


async def check_glosa07_transfer_limits(ipr_id: UUID, db: AsyncSession) -> list[dict]:
    """Glosa 07: TRANSFER mechanism IPRs have parametric caps on admin and honorarios."""
    gates: list[dict] = []

    # Only applies to TRANSFER mechanism
    mech_row = (await db.execute(
        text("""
            SELECT m.code AS mechanism_code
            FROM core.ipr i
            LEFT JOIN ref.category m ON m.id = i.mechanism_id
            WHERE i.id = :id AND i.deleted_at IS NULL
        """),
        {"id": str(ipr_id)},
    )).mappings().first()

    if not mech_row or mech_row["mechanism_code"] != "TRANSFER":
        return gates

    # Load parametric limits from TRANSFER track thresholds
    track_row = (await db.execute(
        text("SELECT thresholds FROM core.financing_track WHERE code = 'TRANSFER' AND is_active = TRUE"),
    )).mappings().first()
    track_thresholds = dict(track_row["thresholds"] or {}) if track_row else {}

    # Get CDP item breakdown (same query as check_glosa_rules)
    result = await db.execute(
        text("""
            SELECT item_cat.code AS item_code,
                   COALESCE(SUM(bc.amount), 0) AS item_amount
            FROM core.budget_commitment bc
            JOIN core.budget_program bp ON bp.id = bc.budget_program_id
            LEFT JOIN ref.category item_cat ON item_cat.id = bp.item_id
            WHERE bc.ipr_id = :ipr_id AND bc.deleted_at IS NULL
            GROUP BY item_cat.code
        """),
        {"ipr_id": str(ipr_id)},
    )
    rows = result.mappings().all()
    if not rows:
        return gates

    item_amounts: dict[str, float] = {}
    total_cdp = 0.0
    for r in rows:
        code = r["item_code"] or "SIN_ITEM"
        amt = float(r["item_amount"])
        item_amounts[code] = amt
        total_cdp += amt

    if total_cdp <= 0:
        return gates

    for gate_name, rule in _GLOSA07_LIMITS_DEFAULT.items():
        matching = sum(item_amounts.get(ic, 0) for ic in rule["items"])
        actual_pct = (matching / total_cdp * 100)
        max_pct = float(track_thresholds.get(rule["threshold_key"], rule["max_pct"]))

        if actual_pct > max_pct:
            gates.append({
                "name": gate_name,
                "met": False,
                "detail": (
                    f"{rule['label']}: {actual_pct:.1f}% excede tope de {max_pct:.0f}% "
                    f"(${matching:,.0f} de ${total_cdp:,.0f} total CDPs)"
                ),
            })
        else:
            gates.append({
                "name": gate_name,
                "met": True,
                "detail": f"{rule['label']}: {actual_pct:.1f}% dentro del tope {max_pct:.0f}%",
            })

    return gates


async def _get_presupuesto_or_404(presupuesto_id: UUID, db: AsyncSession) -> dict:
    result = await db.execute(
        text("""
            SELECT
                bp.id,
                bp.code,
                bp.name,
                bp.fiscal_year,
                bp.owner_division_id          AS division_id,
                org.name                       AS division_name,
                bp.subtitle_id,
                bp.item_id,
                bp.allocation_id,
                sub.label                      AS subtitle_label,
                pt.label                       AS program_type_label,
                item_cat.label                 AS item_label,
                alloc_cat.label                AS allocation_label,
                pc.label                       AS program_code_label,
                bp.initial_amount,
                bp.current_amount,
                COALESCE(bp.committed_amount, 0) AS committed_amount,
                COALESCE(bp.accrued_amount, 0)   AS accrued_amount,
                COALESCE(bp.paid_amount, 0)      AS paid_amount,
                bp.fndr_amount,
                bp.sectorial_amount,
                bp.created_at
            FROM core.budget_program bp
            LEFT JOIN core.organization org ON org.id = bp.owner_division_id
            LEFT JOIN ref.category sub  ON sub.id  = bp.subtitle_id
            LEFT JOIN ref.category pt   ON pt.id   = bp.program_type_id
            LEFT JOIN ref.category item_cat  ON item_cat.id  = bp.item_id
            LEFT JOIN ref.category alloc_cat ON alloc_cat.id = bp.allocation_id
            LEFT JOIN ref.category pc ON pc.id = bp.program_code_id
            WHERE bp.id = :id AND bp.deleted_at IS NULL
        """),
        {"id": str(presupuesto_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programa presupuestario no encontrado")
    return dict(row)


# ---------------------------------------------------------------------------
# GET /api/presupuesto/resumen  — aggregation (MUST come before /{id})
# ---------------------------------------------------------------------------

@router.get("/resumen", response_model=list[PresupuestoResumen])
async def get_presupuesto_resumen(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    group_by: str = Query("division", pattern="^(division|subtitle)$"),
    fiscal_year: int | None = None,
):
    year_filter = f"AND bp.fiscal_year = :fiscal_year" if fiscal_year else ""
    params: dict = {}
    if fiscal_year:
        params["fiscal_year"] = fiscal_year

    if group_by == "division":
        sql = text(f"""
            SELECT
                COALESCE(org.code, 'SIN_DIVISION')           AS group_key,
                COALESCE(org.name, 'Sin división asignada')  AS group_label,
                COALESCE(SUM(bp.initial_amount), 0)          AS initial_amount,
                COALESCE(SUM(bp.current_amount), 0)          AS current_amount,
                COALESCE(SUM(bp.paid_amount), 0)             AS paid_amount,
                COUNT(*)                                      AS program_count
            FROM core.budget_program bp
            LEFT JOIN core.organization org ON org.id = bp.owner_division_id
            WHERE bp.deleted_at IS NULL {year_filter}
            GROUP BY org.code, org.name
            ORDER BY SUM(bp.initial_amount) DESC NULLS LAST
        """)
    else:
        sql = text(f"""
            SELECT
                COALESCE(sub.code, 'SIN_SUBTITULO')          AS group_key,
                COALESCE(sub.label, 'Sin subtítulo')         AS group_label,
                COALESCE(SUM(bp.initial_amount), 0)          AS initial_amount,
                COALESCE(SUM(bp.current_amount), 0)          AS current_amount,
                COALESCE(SUM(bp.paid_amount), 0)             AS paid_amount,
                COUNT(*)                                      AS program_count
            FROM core.budget_program bp
            LEFT JOIN ref.category sub ON sub.id = bp.subtitle_id
            WHERE bp.deleted_at IS NULL {year_filter}
            GROUP BY sub.code, sub.label
            ORDER BY SUM(bp.initial_amount) DESC NULLS LAST
        """)

    rows = (await db.execute(sql, params)).mappings().all()
    return [
        PresupuestoResumen(
            group_key=r["group_key"],
            group_label=r["group_label"],
            initial_amount=r["initial_amount"],
            current_amount=r["current_amount"],
            paid_amount=r["paid_amount"],
            execution_pct=_execution_pct(r["paid_amount"], r["current_amount"]),
            program_count=r["program_count"],
        )
        for r in rows
    ]


# ---------------------------------------------------------------------------
# GET /api/presupuesto — List (paginated, filtered)
# ---------------------------------------------------------------------------

@router.get("", response_model=PaginatedResponse)
async def list_presupuesto(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    fiscal_year: int | None = None,
    division_id: UUID | None = None,
    subtitle: str | None = None,
    item: str | None = None,
    allocation: str | None = None,
    program_type: str | None = None,
    program_code: str | None = None,
    search: str | None = None,
):
    role = user["role_code"]
    params: dict = {}
    conditions = ["bp.deleted_at IS NULL"]

    # JEFE_DIVISION: only own division
    effective_division_id = division_id
    if role == "JEFE_DIVISION" and not division_id:
        effective_division_id = user.get("division_id")

    if fiscal_year:
        conditions.append("bp.fiscal_year = :fiscal_year")
        params["fiscal_year"] = fiscal_year

    if effective_division_id:
        conditions.append("bp.owner_division_id = :division_id")
        params["division_id"] = str(effective_division_id)

    if subtitle:
        conditions.append("sub.code = :subtitle")
        params["subtitle"] = subtitle

    if item:
        conditions.append("item_cat.code = :item")
        params["item"] = item

    if allocation:
        conditions.append("alloc_cat.code = :allocation")
        params["allocation"] = allocation

    if program_type:
        conditions.append("pt.code = :program_type")
        params["program_type"] = program_type

    if program_code:
        conditions.append("pc.code = :program_code")
        params["program_code"] = program_code

    if search:
        conditions.append("(bp.code ILIKE :search OR bp.name ILIKE :search)")
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core.budget_program bp
        LEFT JOIN core.organization org ON org.id = bp.owner_division_id
        LEFT JOIN ref.category sub  ON sub.id  = bp.subtitle_id
        LEFT JOIN ref.category pt   ON pt.id   = bp.program_type_id
        LEFT JOIN ref.category item_cat  ON item_cat.id  = bp.item_id
        LEFT JOIN ref.category alloc_cat ON alloc_cat.id = bp.allocation_id
        LEFT JOIN ref.category pc ON pc.id = bp.program_code_id
        WHERE {where_clause}
    """

    count_result = await db.execute(text(f"SELECT COUNT(*) AS total {base_query}"), params)
    total = count_result.scalar() or 0

    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows_result = await db.execute(
        text(f"""
            SELECT
                bp.id,
                bp.code,
                bp.name,
                bp.fiscal_year,
                bp.owner_division_id              AS division_id,
                org.name                           AS division_name,
                sub.label                          AS subtitle_label,
                pt.label                           AS program_type_label,
                item_cat.label                     AS item_label,
                alloc_cat.label                    AS allocation_label,
                pc.label                           AS program_code_label,
                bp.initial_amount,
                bp.current_amount,
                COALESCE(bp.committed_amount, 0)   AS committed_amount,
                COALESCE(bp.accrued_amount, 0)     AS accrued_amount,
                COALESCE(bp.paid_amount, 0)        AS paid_amount
            {base_query}
            ORDER BY bp.fiscal_year DESC, bp.initial_amount DESC NULLS LAST
            LIMIT :limit OFFSET :offset
        """),
        params,
    )
    rows = rows_result.mappings().all()

    items = [
        PresupuestoListItem(
            id=r["id"],
            code=r["code"],
            name=r["name"],
            fiscal_year=r["fiscal_year"],
            division_id=r["division_id"],
            division_name=r["division_name"],
            subtitle_label=r["subtitle_label"],
            program_type_label=r["program_type_label"],
            item_label=r["item_label"],
            allocation_label=r["allocation_label"],
            program_code_label=r["program_code_label"],
            initial_amount=r["initial_amount"],
            current_amount=r["current_amount"],
            committed_amount=r["committed_amount"],
            accrued_amount=r["accrued_amount"],
            paid_amount=r["paid_amount"],
            execution_pct=_execution_pct(r["paid_amount"], r["current_amount"]),
        )
        for r in rows
    ]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0,
    )


# ---------------------------------------------------------------------------
# GET /api/presupuesto/cdps-por-ipr/{ipr_id} — CDPs linked to an IPR
# ---------------------------------------------------------------------------

@router.get("/cdps-por-ipr/{ipr_id}", response_model=list[BudgetCommitmentItem])
async def list_cdps_by_ipr(
    ipr_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all budget commitments (CDPs) linked to a specific IPR."""
    result = await db.execute(
        text("""
            SELECT
                bc.id,
                bc.commitment_number,
                bc.amount,
                bc.issued_at,
                bc.expires_at,
                st.label  AS status_label,
                bc.ipr_id,
                ipr.codigo_bip AS ipr_codigo_bip
            FROM core.budget_commitment bc
            LEFT JOIN ref.category st ON st.id = bc.status_id
            LEFT JOIN core.ipr ipr ON ipr.id = bc.ipr_id
            WHERE bc.ipr_id = :ipr_id AND bc.deleted_at IS NULL
            ORDER BY bc.issued_at DESC
        """),
        {"ipr_id": str(ipr_id)},
    )
    return [BudgetCommitmentItem(**dict(r)) for r in result.mappings().all()]


# ---------------------------------------------------------------------------
# POST /api/presupuesto/{id}/cdps — Create CDP
# ---------------------------------------------------------------------------

@router.post("/{presupuesto_id}/cdps", status_code=status.HTTP_201_CREATED)
async def create_cdp(
    presupuesto_id: UUID,
    body: BudgetCommitmentCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, *ADMIN_ROLES)

    # Verify program exists and get fiscal year + available balance
    prog = await _get_presupuesto_or_404(presupuesto_id, db)
    current = float(prog.get("current_amount") or prog.get("initial_amount") or 0)
    committed = float(prog.get("committed_amount") or 0)
    available = current - committed

    if body.amount > available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Monto ({body.amount:,}) excede saldo disponible ({available:,.0f} CLP)",
        )

    fiscal_year = prog["fiscal_year"]

    # Generate sequential commitment_number with advisory lock
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('cdp_number'))"))
    seq_result = await db.execute(
        text("""
            SELECT MAX(CAST(SUBSTRING(commitment_number FROM 10) AS INTEGER)) AS max_seq
            FROM core.budget_commitment
            WHERE commitment_number ~ :pattern AND deleted_at IS NULL
        """),
        {"pattern": f"^CDP-{fiscal_year}-[0-9]+$"},
    )
    seq_row = seq_result.mappings().first()
    next_seq = ((seq_row["max_seq"] or 0) + 1) if seq_row else 1
    commitment_number = f"CDP-{fiscal_year}-{next_seq:04d}"

    # Get EMITIDO status
    emitido_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'budget_commitment_status' AND code = 'EMITIDO'")
    )).scalar()

    result = await db.execute(
        text("""
            INSERT INTO core.budget_commitment (
                commitment_number, budget_program_id, amount, issued_at,
                ipr_id, agreement_id, status_id,
                created_by_id, created_at, updated_at
            ) VALUES (
                :commitment_number, :budget_program_id, :amount, CURRENT_DATE,
                :ipr_id, :agreement_id, :status_id,
                :created_by_id, NOW(), NOW()
            )
            RETURNING id, commitment_number
        """),
        {
            "commitment_number": commitment_number,
            "budget_program_id": str(presupuesto_id),
            "amount": body.amount,
            "ipr_id": str(body.ipr_id) if body.ipr_id else None,
            "agreement_id": str(body.agreement_id) if body.agreement_id else None,
            "status_id": str(emitido_id) if emitido_id else None,
            "created_by_id": str(user["id"]),
        },
    )

    # Update committed_amount on the program
    await db.execute(
        text("""
            UPDATE core.budget_program
            SET committed_amount = COALESCE(committed_amount, 0) + :amount,
                updated_at = NOW()
            WHERE id = :pid
        """),
        {"amount": body.amount, "pid": str(presupuesto_id)},
    )

    row = result.mappings().first()
    await record_event(
        db, "CDP", "core.budget_commitment", row["id"],
        actor_id=user["id"],
        data={"commitment_number": commitment_number, "amount": float(body.amount)},
    )
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        error_msg = str(e.orig) if e.orig else str(e)
        if "Transición de estado inválida" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=409, detail="Conflicto de integridad")
    return {"id": row["id"], "commitment_number": row["commitment_number"]}


# ---------------------------------------------------------------------------
# Budget Cycle Timeline (TP-05 / HΩ-15)
# ---------------------------------------------------------------------------

_VALID_CYCLE_STATUSES = {"PENDIENTE", "EN_CURSO", "COMPLETADO", "OMITIDO"}


@router.get("/ciclo/hitos", response_model=list[BudgetCycleMilestoneItem])
async def list_cycle_milestones(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """List all 17 standard budget cycle milestones (parametric TP-05)."""
    result = await db.execute(
        text("""
            SELECT id, phase, quarter, ordinal, month_label, name, responsible, deliverable
            FROM core.budget_cycle_milestone
            ORDER BY ordinal
        """)
    )
    return [BudgetCycleMilestoneItem(**dict(r)) for r in result.mappings().all()]


@router.post("/ciclo/{fiscal_year}", status_code=201)
async def initialize_cycle(
    fiscal_year: int,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Initialize tracking rows for all milestones in a fiscal year. Idempotent."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR")

    if fiscal_year < 2020 or fiscal_year > 2040:
        raise HTTPException(status_code=422, detail="Año fiscal fuera de rango (2020-2040)")

    # Check if already initialized
    existing = (await db.execute(
        text("SELECT COUNT(*) FROM core.budget_cycle_tracking WHERE fiscal_year = :fy"),
        {"fy": fiscal_year},
    )).scalar()

    if existing and existing > 0:
        summary = await _cycle_summary(db, fiscal_year)
        return JSONResponse(content=summary, status_code=200)

    # Insert tracking row for each milestone
    await db.execute(
        text("""
            INSERT INTO core.budget_cycle_tracking (milestone_id, fiscal_year)
            SELECT id, :fy FROM core.budget_cycle_milestone
            ORDER BY ordinal
            ON CONFLICT (milestone_id, fiscal_year) DO NOTHING
        """),
        {"fy": fiscal_year},
    )
    await record_event(db, "CREACION", "core.budget_cycle_tracking", user["id"], user["id"],
                       {"fiscal_year": fiscal_year})
    await db.commit()

    return await _cycle_summary(db, fiscal_year)


@router.get("/ciclo/{fiscal_year}", response_model=list[BudgetCycleTrackingItem])
async def get_cycle_timeline(
    fiscal_year: int,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get the full timeline for a fiscal year with tracking status."""
    result = await db.execute(
        text("""
            SELECT t.id, t.milestone_id, m.ordinal, m.phase, m.quarter,
                   m.month_label, m.name, m.responsible, m.deliverable,
                   t.fiscal_year, t.status, t.planned_date, t.completed_at,
                   t.notes,
                   CASE WHEN p.id IS NOT NULL
                        THEN p.names || ' ' || p.paternal_surname
                        ELSE NULL END AS completed_by_name
            FROM core.budget_cycle_tracking t
            JOIN core.budget_cycle_milestone m ON m.id = t.milestone_id
            LEFT JOIN core."user" u ON u.id = t.completed_by_id
            LEFT JOIN core.person p ON p.id = u.person_id
            WHERE t.fiscal_year = :fy
            ORDER BY m.ordinal
        """),
        {"fy": fiscal_year},
    )
    rows = result.mappings().all()
    if not rows:
        raise HTTPException(status_code=404, detail=f"Ciclo {fiscal_year} no inicializado")
    return [BudgetCycleTrackingItem(**dict(r)) for r in rows]


@router.get("/ciclo/{fiscal_year}/resumen", response_model=BudgetCycleSummary)
async def get_cycle_summary(
    fiscal_year: int,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get completion summary for a fiscal year cycle."""
    summary = await _cycle_summary(db, fiscal_year)
    return summary


@router.patch("/ciclo/tracking/{tracking_id}")
async def update_cycle_tracking(
    tracking_id: UUID,
    body: BudgetCycleTrackingUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Update a milestone tracking entry (status, planned_date, notes)."""
    _require_roles(user, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION")

    # Validate status if provided
    if body.status and body.status not in _VALID_CYCLE_STATUSES:
        raise HTTPException(status_code=422, detail=f"Status inválido. Valores: {_VALID_CYCLE_STATUSES}")

    # Build dynamic SET clause
    sets = []
    params: dict = {"tid": str(tracking_id)}

    if body.status is not None:
        sets.append("status = :status")
        params["status"] = body.status
        if body.status == "COMPLETADO":
            sets.append("completed_at = NOW()")
            sets.append("completed_by_id = :uid")
            params["uid"] = str(user["id"])
        elif body.status in ("PENDIENTE", "EN_CURSO"):
            sets.append("completed_at = NULL")
            sets.append("completed_by_id = NULL")

    if body.planned_date is not None:
        sets.append("planned_date = :planned_date")
        params["planned_date"] = str(body.planned_date)

    if body.notes is not None:
        sets.append("notes = :notes")
        params["notes"] = body.notes

    if not sets:
        raise HTTPException(status_code=422, detail="Sin campos para actualizar")

    sets.append("updated_at = NOW()")
    set_clause = ", ".join(sets)

    result = await db.execute(
        text(f"""
            UPDATE core.budget_cycle_tracking SET {set_clause}
            WHERE id = :tid
            RETURNING id, milestone_id, fiscal_year, status, planned_date,
                      completed_at, notes
        """),
        params,
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Tracking entry not found")

    await db.commit()
    return dict(row)


async def _cycle_summary(db: AsyncSession, fiscal_year: int) -> dict:
    """Build cycle summary response."""
    result = await db.execute(
        text("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE status = 'COMPLETADO') AS completed,
                COUNT(*) FILTER (WHERE status = 'EN_CURSO') AS en_curso,
                COUNT(*) FILTER (WHERE status = 'PENDIENTE') AS pendiente,
                COUNT(*) FILTER (WHERE status = 'OMITIDO') AS omitido
            FROM core.budget_cycle_tracking
            WHERE fiscal_year = :fy
        """),
        {"fy": fiscal_year},
    )
    row = result.mappings().first()
    if not row or row["total"] == 0:
        raise HTTPException(status_code=404, detail=f"Ciclo {fiscal_year} no inicializado")

    total = row["total"]
    completed = row["completed"]
    return {
        "fiscal_year": fiscal_year,
        "total_milestones": total,
        "completed": completed,
        "en_curso": row["en_curso"],
        "pendiente": row["pendiente"],
        "omitido": row["omitido"],
        "completion_pct": round(completed / total * 100, 1) if total > 0 else 0.0,
    }


# ---------------------------------------------------------------------------
# GET /api/presupuesto/{id} — Detail
# ---------------------------------------------------------------------------

@router.get("/{presupuesto_id}", response_model=PresupuestoDetail)
async def get_presupuesto(
    presupuesto_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_presupuesto_or_404(presupuesto_id, db)

    # Carryovers
    co_result = await db.execute(
        text("""
            SELECT id, fiscal_year, amount
            FROM core.budget_carryover
            WHERE budget_program_id = :pid
            ORDER BY fiscal_year DESC
        """),
        {"pid": str(presupuesto_id)},
    )
    carryovers = [CarryoverItem(**dict(r)) for r in co_result.mappings().all()]

    # Budget commitments
    bc_result = await db.execute(
        text("""
            SELECT
                bc.id,
                bc.commitment_number,
                bc.amount,
                bc.issued_at,
                bc.expires_at,
                st.label  AS status_label,
                bc.ipr_id,
                ipr.codigo_bip AS ipr_codigo_bip
            FROM core.budget_commitment bc
            LEFT JOIN ref.category st ON st.id = bc.status_id
            LEFT JOIN core.ipr ipr ON ipr.id = bc.ipr_id
            WHERE bc.budget_program_id = :pid AND bc.deleted_at IS NULL
            ORDER BY bc.issued_at DESC
        """),
        {"pid": str(presupuesto_id)},
    )
    budget_commitments = [BudgetCommitmentItem(**dict(r)) for r in bc_result.mappings().all()]

    return PresupuestoDetail(
        **row,
        execution_pct=_execution_pct(row.get("paid_amount"), row.get("current_amount")),
        carryovers=carryovers,
        budget_commitments=budget_commitments,
    )


# ---------------------------------------------------------------------------
# POST /api/presupuesto — Create
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_presupuesto(
    body: PresupuestoCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, *ADMIN_ROLES)

    # Check unique code+fiscal_year
    dup = await db.execute(
        text("SELECT 1 FROM core.budget_program WHERE code = :code AND fiscal_year = :year AND deleted_at IS NULL"),
        {"code": body.code, "year": body.fiscal_year},
    )
    if dup.scalar():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un programa con ese código para el año fiscal indicado")

    result = await db.execute(
        text("""
            INSERT INTO core.budget_program (
                code, name, fiscal_year,
                program_type_id, subtitle_id, item_id, allocation_id, program_code_id, owner_division_id,
                initial_amount, current_amount,
                committed_amount, accrued_amount, paid_amount,
                created_by_id, created_at, updated_at
            ) VALUES (
                :code, :name, :fiscal_year,
                :program_type_id, :subtitle_id, :item_id, :allocation_id, :program_code_id, :owner_division_id,
                :initial_amount, :current_amount,
                0, 0, 0,
                :created_by_id, NOW(), NOW()
            )
            RETURNING id, code
        """),
        {
            "code": body.code,
            "name": body.name,
            "fiscal_year": body.fiscal_year,
            "program_type_id": str(body.program_type_id) if body.program_type_id else None,
            "subtitle_id": str(body.subtitle_id) if body.subtitle_id else None,
            "item_id": str(body.item_id) if body.item_id else None,
            "allocation_id": str(body.allocation_id) if body.allocation_id else None,
            "program_code_id": str(body.program_code_id) if body.program_code_id else None,
            "owner_division_id": str(body.owner_division_id) if body.owner_division_id else None,
            "initial_amount": body.initial_amount,
            "current_amount": body.current_amount if body.current_amount is not None else body.initial_amount,
            "created_by_id": str(user["id"]),
        },
    )
    row = result.mappings().first()
    await record_event(db, "CREACION", "core.budget_program", row["id"], user["id"],
                       {"code": body.code, "fiscal_year": body.fiscal_year})
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        error_msg = str(e.orig) if e.orig else str(e)
        if "Transición de estado inválida" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=409, detail="Conflicto de integridad")
    return {"id": row["id"], "code": row["code"]}


# ---------------------------------------------------------------------------
# PATCH /api/presupuesto/{id} — Update amounts
# ---------------------------------------------------------------------------

@router.patch("/{presupuesto_id}")
async def update_presupuesto(
    presupuesto_id: UUID,
    body: PresupuestoUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_presupuesto_or_404(presupuesto_id, db)

    # JEFE_DIVISION only own division
    role = user["role_code"]
    if role == "JEFE_DIVISION":
        if str(row.get("division_id")) != str(user.get("division_id")):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo puede modificar programas de su división")
    elif role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")

    # Allowlist: solo estas columnas son actualizables via PATCH
    UPDATABLE_COLUMNS = {"initial_amount", "current_amount", "committed_amount", "accrued_amount", "paid_amount", "program_code_id", "subtitle_id", "item_id", "allocation_id"}

    updates = {k: v for k, v in body.model_dump(exclude_none=True).items() if k in UPDATABLE_COLUMNS}
    if not updates:
        return {"message": "Sin cambios"}

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(presupuesto_id)
    updates["updated_by_id"] = str(user["id"])

    await db.execute(
        text(f"UPDATE core.budget_program SET {set_clauses}, updated_at = NOW(), updated_by_id = :updated_by_id WHERE id = :id"),
        updates,
    )
    await record_event(db, "MODIFICACION", "core.budget_program", presupuesto_id, user["id"],
                       {"fields": list(updates.keys())})
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        error_msg = str(e.orig) if e.orig else str(e)
        if "Transición de estado inválida" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=409, detail="Conflicto de integridad")
    return {"message": "Actualizado correctamente"}
