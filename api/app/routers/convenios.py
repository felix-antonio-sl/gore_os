import math
from datetime import date as date_type
from fastapi import APIRouter, Depends, Query, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import WRITE_OPERATIONAL_ROLES
from app.core.audit import record_event
from app.schemas.common import PaginatedResponse
from app.schemas.convenio import (
    ConvenioListItem,
    ConvenioDetail,
    ConvenioCreate,
    ConvenioUpdate,
    InstallmentItem,
    InstallmentCreate,
    InstallmentUpdate,
    BulkCuotaRequest,
)

router = APIRouter(prefix="/api/convenios", tags=["convenios"])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _require_roles(user: dict, *roles: str) -> None:
    if user["role_code"] not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")


async def _get_convenio_or_404(convenio_id: UUID, db: AsyncSession) -> dict:
    result = await db.execute(
        text("""
            SELECT
                a.id,
                a.agreement_number,
                a.ipr_id,
                a.total_amount,
                a.signed_at,
                a.valid_from,
                a.valid_to,
                a.created_at,
                at_cat.code   AS agreement_type,
                at_cat.label  AS agreement_type_label,
                st_cat.code   AS state,
                st_cat.label  AS state_label,
                ipr.codigo_bip AS ipr_codigo_bip,
                ipr.name       AS ipr_name,
                org_g.name     AS giver_name,
                org_r.name     AS receiver_name,
                CASE
                    WHEN st_cat.code = 'VIGENTE' AND a.valid_to IS NOT NULL
                    THEN EXTRACT(DAY FROM a.valid_to - NOW())::int
                    ELSE NULL
                END             AS days_to_expiry,
                (p.names || ' ' || p.paternal_surname) AS technical_referent_name,
                cgr_cat.code   AS cgr_outcome,
                cgr_cat.label  AS cgr_outcome_label
            FROM core.agreement a
            JOIN ref.category at_cat ON at_cat.id = a.agreement_type_id
            JOIN ref.category st_cat ON st_cat.id = a.state_id
            LEFT JOIN core.ipr ipr ON ipr.id = a.ipr_id
            LEFT JOIN core.organization org_g ON org_g.id = a.giver_id
            LEFT JOIN core.organization org_r ON org_r.id = a.receiver_id
            LEFT JOIN core.person p ON p.id = a.technical_referent_id
            LEFT JOIN ref.category cgr_cat ON cgr_cat.id = a.cgr_outcome_id
            WHERE a.id = :id AND a.deleted_at IS NULL
        """),
        {"id": str(convenio_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convenio no encontrado")
    return dict(row)


async def _get_agreement_history(convenio_id: UUID, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        text("""
            SELECT ah.id, ah.changed_at, ah.comment,
                   prev.code  AS previous_state,
                   nxt.code   AS new_state,
                   (p.names || ' ' || p.paternal_surname) AS changed_by_name
            FROM core.agreement_history ah
            JOIN ref.category nxt ON ah.new_state_id = nxt.id
            LEFT JOIN ref.category prev ON ah.previous_state_id = prev.id
            LEFT JOIN core."user" cu ON ah.changed_by_id = cu.id
            LEFT JOIN core.person p ON cu.person_id = p.id
            WHERE ah.agreement_id = :aid
            ORDER BY ah.changed_at DESC
        """),
        {"aid": str(convenio_id)},
    )
    return [dict(r) for r in result.mappings().all()]


async def _get_installments(convenio_id: UUID, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        text("""
            SELECT
                ai.id,
                ai.installment_number,
                ai.amount,
                ai.due_date,
                ai.paid_at,
                ai.paid_amount,
                ai.payment_reference,
                ps.code   AS payment_status,
                ps.label  AS payment_status_label
            FROM core.agreement_installment ai
            JOIN ref.category ps ON ps.id = ai.payment_status_id
            WHERE ai.agreement_id = :aid AND ai.deleted_at IS NULL
            ORDER BY ai.installment_number ASC
        """),
        {"aid": str(convenio_id)},
    )
    return [dict(r) for r in result.mappings().all()]


async def _check_pending_renditions(agreement_id: UUID, db: AsyncSession) -> None:
    """Art. 18 Res. 30 CGR: Bloquea si hay rendiciones no-terminales vinculadas."""
    result = await db.execute(
        text("""
            SELECT COUNT(*) AS pending_count,
                   json_agg(json_build_object(
                       'id', LEFT(r.id::text, 8),
                       'status', st.label,
                       'status_code', st.code,
                       'amount', r.amount
                   ) ORDER BY r.created_at) FILTER (WHERE r.id IS NOT NULL) AS details
            FROM core.rendition r
            JOIN ref.category st ON st.id = r.state_id
            WHERE r.deleted_at IS NULL
              AND st.scheme = 'rendition_state'
              AND st.code NOT IN ('APROBADA', 'RECHAZADA')
              AND (
                  r.agreement_id = :agreement_id
                  OR r.ipr_id = (
                      SELECT ipr_id FROM core.agreement
                      WHERE id = :agreement_id AND ipr_id IS NOT NULL
                  )
              )
        """),
        {"agreement_id": str(agreement_id)},
    )
    row = result.mappings().first()
    pending = row["pending_count"]
    if pending > 0:
        details = row["details"] or []
        summary = "; ".join(
            f"{d['id']}… ({d['status']})" for d in details[:5]
        )
        if pending > 5:
            summary += f" … y {pending - 5} más"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Art. 18 Res. 30 CGR: Existen {pending} rendición(es) pendiente(s). Detalle: {summary}",
        )


async def _next_agreement_number(db: AsyncSession) -> str:
    from datetime import date
    year = date.today().year
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('agr_number'))"))
    result = await db.execute(
        text("""
            SELECT MAX(CAST(SUBSTRING(agreement_number FROM 10) AS INTEGER)) AS max_seq
            FROM core.agreement
            WHERE agreement_number ~ :pattern
        """),
        {"pattern": f"^AGR-{year}-[0-9]+$"},
    )
    row = result.mappings().first()
    next_seq = ((row["max_seq"] or 0) + 1) if row else 1
    return f"AGR-{year}-{next_seq:05d}"


# ---------------------------------------------------------------------------
# GET /api/convenios — List (paginated, filtered)
# ---------------------------------------------------------------------------

@router.get("", response_model=PaginatedResponse)
async def list_convenios(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    state: str | None = None,
    agreement_type: str | None = None,
    ipr_id: UUID | None = None,
    orphan: bool | None = Query(None, description="If true, return only conventions without linked IPR"),
    search: str | None = None,
    date_from: date_type | None = None,
    date_to: date_type | None = None,
):
    params: dict = {}
    conditions = ["a.deleted_at IS NULL"]

    if date_from:
        conditions.append("a.valid_to >= :date_from")
        params["date_from"] = str(date_from)
    if date_to:
        conditions.append("a.valid_to <= :date_to")
        params["date_to"] = str(date_to)

    if state:
        conditions.append("st_cat.code = :state")
        params["state"] = state

    if agreement_type:
        conditions.append("at_cat.code = :agreement_type")
        params["agreement_type"] = agreement_type

    if ipr_id:
        conditions.append("a.ipr_id = :ipr_id")
        params["ipr_id"] = str(ipr_id)
    elif orphan is True:
        conditions.append("a.ipr_id IS NULL")

    if search:
        conditions.append("(a.agreement_number ILIKE :search OR ipr.codigo_bip ILIKE :search OR ipr.name ILIKE :search)")
        params["search"] = f"%{search}%"

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core.agreement a
        JOIN ref.category at_cat ON at_cat.id = a.agreement_type_id
        JOIN ref.category st_cat ON st_cat.id = a.state_id
        LEFT JOIN core.ipr ipr ON ipr.id = a.ipr_id
        LEFT JOIN core.organization org_g ON org_g.id = a.giver_id
        LEFT JOIN core.organization org_r ON org_r.id = a.receiver_id
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
                a.id,
                a.agreement_number,
                a.ipr_id,
                a.total_amount,
                a.signed_at,
                a.valid_from,
                a.valid_to,
                at_cat.code   AS agreement_type,
                at_cat.label  AS agreement_type_label,
                st_cat.code   AS state,
                st_cat.label  AS state_label,
                ipr.codigo_bip AS ipr_codigo_bip,
                ipr.name       AS ipr_name,
                org_g.name     AS giver_name,
                org_r.name     AS receiver_name,
                CASE
                    WHEN st_cat.code = 'VIGENTE' AND a.valid_to IS NOT NULL
                    THEN EXTRACT(DAY FROM a.valid_to - NOW())::int
                    ELSE NULL
                END AS days_to_expiry,
                (SELECT COUNT(*) FROM core.agreement_installment ai WHERE ai.agreement_id = a.id AND ai.deleted_at IS NULL) AS installment_count,
                (SELECT COUNT(*) FROM core.agreement_installment ai JOIN ref.category ps ON ps.id = ai.payment_status_id WHERE ai.agreement_id = a.id AND ps.code = 'PAGADO' AND ai.deleted_at IS NULL) AS paid_installments
            {base_query}
            ORDER BY
                CASE st_cat.code
                    WHEN 'VIGENTE' THEN 1
                    WHEN 'EN_MODIFICACION' THEN 2
                    WHEN 'FIRMADO_CONTRAPARTE' THEN 3
                    WHEN 'FIRMADO_GORE' THEN 4
                    ELSE 5
                END ASC,
                a.valid_to ASC NULLS LAST
            LIMIT :limit OFFSET :offset
        """),
        params,
    )
    rows = rows_result.mappings().all()

    items = [
        ConvenioListItem(
            id=r["id"],
            agreement_number=r["agreement_number"],
            agreement_type=r["agreement_type"],
            agreement_type_label=r["agreement_type_label"],
            state=r["state"],
            state_label=r["state_label"],
            ipr_id=r["ipr_id"],
            ipr_codigo_bip=r["ipr_codigo_bip"],
            ipr_name=r["ipr_name"],
            giver_name=r["giver_name"],
            receiver_name=r["receiver_name"],
            total_amount=r["total_amount"],
            signed_at=r["signed_at"],
            valid_from=r["valid_from"],
            valid_to=r["valid_to"],
            days_to_expiry=r["days_to_expiry"],
            installment_count=r["installment_count"] or 0,
            paid_installments=r["paid_installments"] or 0,
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
# GET /api/convenios/{id} — Detail with installments
# ---------------------------------------------------------------------------

@router.get("/{convenio_id}", response_model=ConvenioDetail)
async def get_convenio(
    convenio_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_convenio_or_404(convenio_id, db)
    installments_raw = await _get_installments(convenio_id, db)
    history_raw = await _get_agreement_history(convenio_id, db)

    # Installment counts for list fields
    installments = [InstallmentItem(**r) for r in installments_raw]
    installment_count = len(installments)
    paid_installments = sum(1 for i in installments if i.payment_status == "PAGADO")

    return ConvenioDetail(
        **row,
        installment_count=installment_count,
        paid_installments=paid_installments,
        installments=installments,
        history=history_raw,
    )


# ---------------------------------------------------------------------------
# POST /api/convenios — Create
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_convenio(
    body: ConvenioCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, *WRITE_OPERATIONAL_ROLES)
    agreement_number = body.agreement_number or await _next_agreement_number(db)

    try:
        result = await db.execute(
            text("""
                INSERT INTO core.agreement (
                    agreement_number, agreement_type_id, state_id,
                    ipr_id, giver_id, receiver_id,
                    total_amount, signed_at, valid_from, valid_to,
                    created_by_id, created_at, updated_at
                ) VALUES (
                    :agreement_number, :agreement_type_id, :state_id,
                    :ipr_id, :giver_id, :receiver_id,
                    :total_amount, :signed_at, :valid_from, :valid_to,
                    :created_by_id, NOW(), NOW()
                )
                RETURNING id, agreement_number
            """),
            {
                "agreement_number": agreement_number,
                "agreement_type_id": str(body.agreement_type_id),
                "state_id": str(body.state_id),
                "ipr_id": str(body.ipr_id) if body.ipr_id else None,
                "giver_id": str(body.giver_id) if body.giver_id else None,
                "receiver_id": str(body.receiver_id) if body.receiver_id else None,
                "total_amount": body.total_amount,
                "signed_at": body.signed_at,
                "valid_from": body.valid_from,
                "valid_to": body.valid_to,
                "created_by_id": str(user["id"]),
            },
        )
        row = result.mappings().first()
        await record_event(
            db, "CREACION", "core.agreement", row["id"],
            actor_id=user["id"],
            data={"agreement_number": agreement_number},
        )
        await db.commit()
        return {"id": row["id"], "agreement_number": row["agreement_number"]}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un convenio con ese número")
    except Exception:
        await db.rollback()
        raise


# ---------------------------------------------------------------------------
# PATCH /api/convenios/{id} — Update
# ---------------------------------------------------------------------------

async def _get_utm_value(db: AsyncSession) -> int:
    """Get current UTM value from DB (administrable)."""
    row = (await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'UTM_VALUE' AND is_active = TRUE")
    )).mappings().first()
    if row and row["value_utm"]:
        return int(row["value_utm"])
    return 67_294  # fallback


async def _get_threshold_value(code: str, db: AsyncSession) -> float | None:
    """Get a threshold's UTM value by code."""
    row = (await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = :code AND is_active = TRUE"),
        {"code": code},
    )).mappings().first()
    if row and row["value_utm"]:
        return float(row["value_utm"])
    return None


async def _check_garantia_threshold(agreement_id: UUID, db: AsyncSession) -> dict | None:
    """Convenios above GARANTIA_CONVENIO threshold require garantia de fiel cumplimiento.
    Returns warning dict if threshold exceeded, None otherwise."""
    threshold_utm = await _get_threshold_value("GARANTIA_CONVENIO", db)
    if threshold_utm is None:
        return None

    utm = await _get_utm_value(db)
    threshold_clp = threshold_utm * utm

    row = (await db.execute(
        text("SELECT total_amount FROM core.agreement WHERE id = :id AND deleted_at IS NULL"),
        {"id": str(agreement_id)},
    )).mappings().first()

    if not row or not row["total_amount"]:
        return None

    total = float(row["total_amount"])
    if total <= threshold_clp:
        return None

    return {
        "warning": "garantia_required",
        "detail": f"Convenio supera {int(threshold_utm):,} UTM (${total:,.0f} CLP) — requiere garantía de fiel cumplimiento",
        "threshold_utm": threshold_utm,
        "total_amount": total,
    }


async def _validate_state_transition(
    convenio_id: UUID,
    new_state_id: str,
    db: AsyncSession,
) -> tuple[str, str]:
    """Validate state transition. Returns (current_code, new_code) or raises HTTP 409."""
    # Get current state code + valid_transitions, and new state code
    result = await db.execute(
        text("""
            SELECT
                cur.code       AS current_code,
                cur.valid_transitions AS valid_transitions,
                nxt.code       AS new_code
            FROM core.agreement a
            JOIN ref.category cur ON cur.id = a.state_id
            JOIN ref.category nxt ON nxt.id = :new_state_id
            WHERE a.id = :id AND a.deleted_at IS NULL
        """),
        {"id": str(convenio_id), "new_state_id": new_state_id},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convenio no encontrado")

    current_code = row["current_code"]
    new_code = row["new_code"]
    valid = row["valid_transitions"] or []

    if new_code not in valid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Transición inválida: {current_code} → {new_code}. Destinos válidos: {', '.join(valid) if valid else '(estado terminal)'}",
        )

    return current_code, new_code


async def _validate_amount_thresholds(
    convenio_id: UUID,
    current_code: str,
    new_code: str,
    db: AsyncSession,
) -> None:
    """Validate UTM-based thresholds for sensitive transitions (reads from DB)."""
    result = await db.execute(
        text("SELECT total_amount FROM core.agreement WHERE id = :id"),
        {"id": str(convenio_id)},
    )
    row = result.mappings().first()
    total_amount = float(row["total_amount"]) if row and row["total_amount"] else 0

    utm = await _get_utm_value(db)

    # GARANTIA_CONVENIO threshold: >1.000 UTM → requiere VISADO_INTERNO antes de FIRMADO_GORE
    garantia_utm = await _get_threshold_value("GARANTIA_CONVENIO", db) or 1000
    if new_code == "FIRMADO_GORE" and current_code != "VISADO_INTERNO" and total_amount > garantia_utm * utm:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Convenios >{int(garantia_utm):,} UTM requieren Visado Interno del AR antes de pasar a Firmado GORE",
        )

    # CGR_TOMA_RAZON threshold: >2.500 UTM → requiere TDR_PENDIENTE antes de VIGENTE
    cgr_utm = await _get_threshold_value("CGR_TOMA_RAZON", db) or 2500
    if new_code == "VIGENTE" and current_code != "TDR_PENDIENTE" and total_amount > cgr_utm * utm:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Convenios >{int(cgr_utm):,} UTM requieren Toma de Razón CGR (TdR Pendiente) antes de pasar a Vigente",
        )


@router.patch("/{convenio_id}")
async def update_convenio(
    convenio_id: UUID,
    body: ConvenioUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, *WRITE_OPERATIONAL_ROLES)
    await _get_convenio_or_404(convenio_id, db)

    # Allowlist: solo estas columnas son actualizables via PATCH
    UPDATABLE_COLUMNS = {"state_id", "ipr_id", "total_amount", "valid_to", "cgr_outcome_id"}

    updates = {k: v for k, v in body.model_dump(exclude_none=True).items() if k in UPDATABLE_COLUMNS}
    if not updates:
        return {"message": "Sin cambios"}

    # Validate state transition if state_id is being changed
    warnings = []
    if "state_id" in updates:
        new_state_id = str(updates["state_id"])
        current_code, new_code = await _validate_state_transition(convenio_id, new_state_id, db)
        await _validate_amount_thresholds(convenio_id, current_code, new_code, db)
        # Check garantía threshold (informational warning)
        if new_code in ("FIRMADO_GORE", "FIRMADO_CONTRAPARTE", "VIGENTE"):
            garantia = await _check_garantia_threshold(convenio_id, db)
            if garantia:
                warnings.append(garantia)

    # Convert UUIDs to string
    for k in ["state_id", "ipr_id", "cgr_outcome_id"]:
        if k in updates:
            updates[k] = str(updates[k])

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(convenio_id)
    updates["updated_by_id"] = str(user["id"])

    await db.execute(
        text(f"UPDATE core.agreement SET {set_clauses}, updated_at = NOW(), updated_by_id = :updated_by_id WHERE id = :id"),
        updates,
    )
    if "state_id" in updates:
        await record_event(
            db, "STATE_TRANSITION", "core.agreement", convenio_id,
            actor_id=user["id"],
            data={"from": current_code, "to": new_code},
        )
    else:
        await record_event(
            db, "MODIFICACION", "core.agreement", convenio_id,
            actor_id=user["id"],
            data={"fields": [k for k in updates if k not in ("id", "updated_by_id")]},
        )
    await db.commit()
    result = {"message": "Actualizado correctamente"}
    if warnings:
        result["warnings"] = warnings
    return result


# ---------------------------------------------------------------------------
# GET /api/convenios/{id}/transiciones — Valid state transitions
# ---------------------------------------------------------------------------

@router.get("/{convenio_id}/transiciones")
async def get_valid_transitions(
    convenio_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return the valid destination states for this agreement's current state."""
    result = await db.execute(
        text("""
            SELECT
                cur.code AS current_code,
                cur.valid_transitions AS valid_transitions
            FROM core.agreement a
            JOIN ref.category cur ON cur.id = a.state_id
            WHERE a.id = :id AND a.deleted_at IS NULL
        """),
        {"id": str(convenio_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Convenio no encontrado")

    valid_codes = row["valid_transitions"] or []
    if not valid_codes:
        return []

    # Fetch id, code, label for each valid destination
    dest_result = await db.execute(
        text("""
            SELECT id, code, label
            FROM ref.category
            WHERE scheme = 'agreement_state' AND code = ANY(:codes)
            ORDER BY label
        """),
        {"codes": valid_codes},
    )
    return [dict(r) for r in dest_result.mappings().all()]


# ---------------------------------------------------------------------------
# GET /api/convenios/{id}/cuotas — List installments
# ---------------------------------------------------------------------------

@router.get("/{convenio_id}/cuotas", response_model=list[InstallmentItem])
async def list_cuotas(
    convenio_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await _get_convenio_or_404(convenio_id, db)
    installments_raw = await _get_installments(convenio_id, db)
    return [InstallmentItem(**r) for r in installments_raw]


# ---------------------------------------------------------------------------
# POST /api/convenios/{id}/cuotas/bulk — Bulk generate installments
# ---------------------------------------------------------------------------

def _add_months(d: date_type, months: int) -> date_type:
    """Add months to a date, clamping to last day of target month."""
    import calendar
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return d.replace(year=year, month=month, day=day)


@router.post("/{convenio_id}/cuotas/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_create_cuotas(
    convenio_id: UUID,
    body: BulkCuotaRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, *WRITE_OPERATIONAL_ROLES)
    await _get_convenio_or_404(convenio_id, db)

    if body.num_installments < 1 or body.num_installments > 60:
        raise HTTPException(status_code=422, detail="num_installments debe estar entre 1 y 60")
    if body.total_amount <= 0:
        raise HTTPException(status_code=422, detail="total_amount debe ser mayor a 0")

    # Get max existing installment_number
    max_row = (await db.execute(
        text("SELECT COALESCE(MAX(installment_number), 0) AS max_num FROM core.agreement_installment WHERE agreement_id = :aid AND deleted_at IS NULL"),
        {"aid": str(convenio_id)},
    )).mappings().first()
    start_num = (max_row["max_num"] if max_row else 0) + 1

    # Lookup PENDIENTE payment status
    pendiente_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'payment_status' AND code = 'PENDIENTE'")
    )).scalar()
    if not pendiente_id:
        raise HTTPException(status_code=500, detail="payment_status PENDIENTE no encontrado")

    # Distribute amounts
    amount_per = body.total_amount // body.num_installments
    remainder = body.total_amount % body.num_installments

    created = []
    for i in range(body.num_installments):
        num = start_num + i
        amount = amount_per + (remainder if i == 0 else 0)
        due = _add_months(body.start_date, i * body.frequency_months)

        row = (await db.execute(
            text("""
                INSERT INTO core.agreement_installment (
                    agreement_id, installment_number, amount, due_date, payment_status_id,
                    created_at, updated_at
                ) VALUES (
                    :agreement_id, :num, :amount, :due_date, :payment_status_id,
                    NOW(), NOW()
                )
                RETURNING id, installment_number, amount, due_date
            """),
            {
                "agreement_id": str(convenio_id),
                "num": num,
                "amount": amount,
                "due_date": due,
                "payment_status_id": str(pendiente_id),
            },
        )).mappings().first()
        created.append(dict(row))

    await record_event(
        db, "CREACION", "core.agreement_installment", str(convenio_id),
        actor_id=user["id"],
        data={"count": len(created), "total_amount": float(body.total_amount), "bulk": True},
    )
    await db.commit()
    return created


# ---------------------------------------------------------------------------
# POST /api/convenios/{id}/cuotas — Add installment
# ---------------------------------------------------------------------------

@router.post("/{convenio_id}/cuotas", status_code=status.HTTP_201_CREATED)
async def add_cuota(
    convenio_id: UUID,
    body: InstallmentCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, *WRITE_OPERATIONAL_ROLES)
    await _get_convenio_or_404(convenio_id, db)

    # Art. 18 Res. 30 CGR: bloquear si hay rendiciones pendientes
    await _check_pending_renditions(convenio_id, db)

    # Check unique installment_number
    dup = await db.execute(
        text("SELECT 1 FROM core.agreement_installment WHERE agreement_id = :aid AND installment_number = :num AND deleted_at IS NULL"),
        {"aid": str(convenio_id), "num": body.installment_number},
    )
    if dup.scalar():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una cuota con ese número")

    result = await db.execute(
        text("""
            INSERT INTO core.agreement_installment (
                agreement_id, installment_number, amount, due_date, payment_status_id,
                created_at, updated_at
            ) VALUES (
                :agreement_id, :installment_number, :amount, :due_date, :payment_status_id,
                NOW(), NOW()
            )
            RETURNING id
        """),
        {
            "agreement_id": str(convenio_id),
            "installment_number": body.installment_number,
            "amount": body.amount,
            "due_date": body.due_date,
            "payment_status_id": str(body.payment_status_id),
        },
    )
    row = result.mappings().first()
    await record_event(
        db, "CREACION", "core.agreement_installment", row["id"],
        actor_id=user["id"],
        data={"agreement_id": str(convenio_id), "installment_number": body.installment_number},
    )
    await db.commit()
    return {"id": row["id"]}


# ---------------------------------------------------------------------------
# PATCH /api/convenios/{id}/cuotas/{cuota_id} — Update installment
# ---------------------------------------------------------------------------

@router.patch("/{convenio_id}/cuotas/{cuota_id}")
async def update_cuota(
    convenio_id: UUID,
    cuota_id: UUID,
    body: InstallmentUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_roles(user, *WRITE_OPERATIONAL_ROLES)
    # Verify cuota belongs to convenio
    check = await db.execute(
        text("SELECT 1 FROM core.agreement_installment WHERE id = :id AND agreement_id = :aid AND deleted_at IS NULL"),
        {"id": str(cuota_id), "aid": str(convenio_id)},
    )
    if not check.scalar():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuota no encontrada")

    updates = body.model_dump(exclude_none=True)
    if not updates:
        return {"message": "Sin cambios"}

    # Art. 18 Res. 30 CGR: bloquear pago efectivo si hay rendiciones pendientes
    needs_rendition_check = False
    if "payment_status_id" in updates:
        target_code = (await db.execute(
            text("SELECT code FROM ref.category WHERE id = :id AND scheme = 'payment_status'"),
            {"id": str(updates["payment_status_id"])},
        )).scalar()
        if target_code in ("PAGADO", "EN_PROCESO"):
            needs_rendition_check = True
    if "paid_amount" in updates or "paid_at" in updates:
        needs_rendition_check = True
    if needs_rendition_check:
        await _check_pending_renditions(convenio_id, db)

    if "payment_status_id" in updates:
        updates["payment_status_id"] = str(updates["payment_status_id"])

    set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = str(cuota_id)

    await db.execute(
        text(f"UPDATE core.agreement_installment SET {set_clauses}, updated_at = NOW() WHERE id = :id"),
        updates,
    )
    await record_event(
        db, "MODIFICACION", "core.agreement_installment", cuota_id,
        actor_id=user["id"],
        data={"agreement_id": str(convenio_id), "fields": [k for k in updates if k != "id"]},
    )
    await db.commit()
    return {"message": "Cuota actualizada"}
