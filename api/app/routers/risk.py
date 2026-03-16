"""
E-1: Risk Management CRUD

Cross-population risk register. DGI + ADMIN roles write, all roles read
(scoped by ANALISTA/RTF/JURIDICO → own IPRs, JEFE_DIVISION → division IPRs).

Route ordering: static paths (summary, matrix, check-alerts) BEFORE /{id}.
"""
import json
import math
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import CurrentUser
from app.core.security import DGI_ROLES
from app.core.audit import record_event

router = APIRouter(prefix="/api/risk", tags=["risk"])

# ---------------------------------------------------------------------------
# Role helpers
# ---------------------------------------------------------------------------
_WRITE_ROLES = {*DGI_ROLES, "ADMIN_REGIONAL", "ADMIN_SISTEMA"}
_ALL_ROLES = {*DGI_ROLES, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR",
              "JEFE_DIVISION", "SECRETARIO_EJECUTIVO",
              "JEFE_DEPARTAMENTO", "JEFE_UNIDAD", "CONSEJERO_REGIONAL",
              "ANALISTA", "RTF", "ASESOR_JURIDICO"}


def _require_read(user: dict) -> None:
    if user.get("role_code") not in _ALL_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Sin permisos para ver riesgos")


def _require_write(user: dict) -> None:
    if user.get("role_code") not in _WRITE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo DGI/Admin pueden gestionar riesgos")


# ---------------------------------------------------------------------------
# FSM (matches DB valid_transitions exactly)
# ---------------------------------------------------------------------------
_FSM: dict[str, set[str]] = {
    "IDENTIFICADO":  {"EN_EVALUACION", "ACEPTADO"},
    "EN_EVALUACION": {"EN_MITIGACION", "ACEPTADO", "CERRADO"},
    "EN_MITIGACION": {"MITIGADO", "CERRADO"},
    "MITIGADO":      {"CERRADO"},
    "ACEPTADO":      {"CERRADO"},
    "CERRADO":       set(),
}

# ---------------------------------------------------------------------------
# PATCH allowlist
# ---------------------------------------------------------------------------
_FIELD_ALLOWLIST = {
    "name", "risk_type_id", "probability_id", "impact_id",
    "mitigation_plan", "identified_at",
}

# ---------------------------------------------------------------------------
# SQL fragments
# ---------------------------------------------------------------------------
_LIST_COLS = """
    r.id, r.code, r.name,
    rt.code AS risk_type, rt.label AS risk_type_label,
    rp.code AS probability, rp.label AS probability_label,
    ri.code AS impact, ri.label AS impact_label,
    rs.code AS status, rs.label AS status_label,
    r.subject_type, r.subject_id,
    CASE r.subject_type
        WHEN 'core.ipr' THEN (SELECT i.codigo_bip || ' - ' || i.name FROM core.ipr i WHERE i.id = r.subject_id)
        WHEN 'core.dgi_process' THEN (SELECT dp.code || ' - ' || dp.name FROM core.dgi_process dp WHERE dp.id = r.subject_id)
        ELSE NULL
    END AS subject_label,
    r.identified_at, r.created_at
"""

_LIST_FROM = """
    FROM core.risk r
    LEFT JOIN ref.category rt ON rt.id = r.risk_type_id
    LEFT JOIN ref.category rp ON rp.id = r.probability_id
    LEFT JOIN ref.category ri ON ri.id = r.impact_id
    LEFT JOIN ref.category rs ON rs.id = r.status_id
"""

_DETAIL_COLS = f"""
    {_LIST_COLS},
    r.mitigation_plan, r.metadata, r.updated_at,
    p.names || ' ' || p.paternal_surname AS created_by_name
"""

_DETAIL_FROM = f"""
    {_LIST_FROM}
    LEFT JOIN core."user" u ON u.id = r.created_by_id
    LEFT JOIN core.person p ON p.id = u.person_id
"""


def _scope_where(user: dict, params: dict) -> str:
    """Return extra WHERE clause based on role scoping."""
    role = user.get("role_code")
    if role in ("ANALISTA", "RTF", "ASESOR_JURIDICO"):
        params["user_id"] = str(user["id"])
        return """
            AND (
                (r.subject_type = 'core.ipr' AND r.subject_id IN (
                    SELECT id FROM core.ipr WHERE assignee_id = :user_id AND deleted_at IS NULL
                ))
            )
        """
    if role in ("JEFE_DIVISION", "JEFE_DEPARTAMENTO", "JEFE_UNIDAD"):
        div_id = user.get("division_id")
        if div_id:
            params["div_id"] = str(div_id)
            return """
                AND (
                    (r.subject_type = 'core.ipr' AND r.subject_id IN (
                        SELECT id FROM core.ipr WHERE sponsor_division_id = :div_id AND deleted_at IS NULL
                    ))
                )
            """
    return ""


# ---------------------------------------------------------------------------
# Category lookup helper
# ---------------------------------------------------------------------------
async def _cat_id(db, scheme: str, code: str) -> str:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = :s AND code = :c"),
        {"s": scheme, "c": code},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=400, detail=f"Código inválido para {scheme}: {code}")
    return str(row["id"])


# ---------------------------------------------------------------------------
# Alert creation helper (E-4)
# ---------------------------------------------------------------------------
async def _create_risk_alert(db, risk_id: str, risk_code: str, risk_name: str,
                             probability_code: str, user_id: str) -> str | None:
    severity_code = "CRITICO" if probability_code == "MUY_ALTA" else "ALTO"
    sev_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_level' AND code = :c"),
        {"c": severity_code},
    )).mappings().first()
    type_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'alert_type' AND code = 'RIESGO_ALTO'"),
    )).mappings().first()
    if not type_row:
        # Fallback to any alert_type if RIESGO_ALTO not yet seeded
        type_row = (await db.execute(
            text("SELECT id FROM ref.category WHERE scheme = 'alert_type' LIMIT 1"),
        )).mappings().first()
    if not sev_row or not type_row:
        return None
    result = await db.execute(
        text("""
            INSERT INTO core.alert
                (alert_type_id, severity_id, subject_type, subject_id, message, created_by_id)
            VALUES (:type_id, :sev_id, 'core.risk', :subject_id,
                    :message, :created_by_id)
            RETURNING id
        """),
        {
            "type_id": str(type_row["id"]),
            "sev_id": str(sev_row["id"]),
            "subject_id": risk_id,
            "message": f"Riesgo {severity_code}: {risk_code} — {risk_name[:200]}",
            "created_by_id": user_id,
        },
    )
    alert_id = result.scalar()
    if alert_id:
        await record_event(db, "ALERT_CREATED", "core.alert", alert_id, user_id,
                           {"source": "risk_check_alerts", "risk_code": risk_code})
    return str(alert_id) if alert_id else None


# ═══════════════════════════════════════════════════════════════════════════════
# 1. GET /api/risk/summary — static path BEFORE /{id}
# ═══════════════════════════════════════════════════════════════════════════════
@router.get("/summary")
async def risk_summary(user: CurrentUser, db=Depends(get_db)):
    _require_read(user)
    params: dict = {}
    scope = _scope_where(user, params)

    by_status = (await db.execute(text(f"""
        SELECT rs.code, rs.label, COUNT(*) AS count
        FROM core.risk r
        JOIN ref.category rs ON rs.id = r.status_id
        WHERE r.deleted_at IS NULL {scope}
        GROUP BY rs.code, rs.label, rs.sort_order
        ORDER BY rs.sort_order
    """), params)).mappings().all()

    by_type = (await db.execute(text(f"""
        SELECT rt.code, rt.label, COUNT(*) AS count
        FROM core.risk r
        JOIN ref.category rt ON rt.id = r.risk_type_id
        WHERE r.deleted_at IS NULL {scope}
        GROUP BY rt.code, rt.label, rt.sort_order
        ORDER BY rt.sort_order
    """), params)).mappings().all()

    by_prob = (await db.execute(text(f"""
        SELECT rp.code, rp.label, COUNT(*) AS count
        FROM core.risk r
        JOIN ref.category rp ON rp.id = r.probability_id
        WHERE r.deleted_at IS NULL {scope}
        GROUP BY rp.code, rp.label, rp.sort_order
        ORDER BY rp.sort_order
    """), params)).mappings().all()

    total = (await db.execute(text(f"""
        SELECT COUNT(*) FROM core.risk r WHERE r.deleted_at IS NULL {scope}
    """), params)).scalar() or 0

    high_risk = (await db.execute(text(f"""
        SELECT COUNT(*) FROM core.risk r
        JOIN ref.category rp ON rp.id = r.probability_id
        JOIN ref.category rs ON rs.id = r.status_id
        WHERE r.deleted_at IS NULL
          AND rp.code IN ('ALTA', 'MUY_ALTA')
          AND rs.code NOT IN ('CERRADO', 'MITIGADO', 'ACEPTADO')
          {scope}
    """), params)).scalar() or 0

    return {
        "total": total,
        "by_status": [dict(r) for r in by_status],
        "by_type": [dict(r) for r in by_type],
        "by_probability": [dict(r) for r in by_prob],
        "high_risk_count": high_risk,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. GET /api/risk/matrix — probability × impact grid
# ═══════════════════════════════════════════════════════════════════════════════
@router.get("/matrix")
async def risk_matrix(user: CurrentUser, db=Depends(get_db)):
    _require_read(user)
    params: dict = {}
    scope = _scope_where(user, params)

    rows = (await db.execute(text(f"""
        SELECT rp.code AS probability, rp.label AS probability_label,
               ri.code AS impact, ri.label AS impact_label,
               COUNT(*) AS count
        FROM core.risk r
        JOIN ref.category rp ON rp.id = r.probability_id
        JOIN ref.category ri ON ri.id = r.impact_id
        WHERE r.deleted_at IS NULL {scope}
        GROUP BY rp.code, rp.label, rp.sort_order, ri.code, ri.label, ri.sort_order
        ORDER BY rp.sort_order, ri.sort_order
    """), params)).mappings().all()

    return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════════════════════════
# 3. POST /api/risk/check-alerts — batch scan high risks → create alerts (E-4)
# ═══════════════════════════════════════════════════════════════════════════════
@router.post("/check-alerts")
async def check_risk_alerts(user: CurrentUser, db=Depends(get_db)):
    _require_write(user)

    rows = (await db.execute(text("""
        SELECT r.id, r.code, r.name, rp.code AS probability_code
        FROM core.risk r
        JOIN ref.category rp ON rp.id = r.probability_id
        JOIN ref.category rs ON rs.id = r.status_id
        WHERE r.deleted_at IS NULL
          AND rp.code IN ('ALTA', 'MUY_ALTA')
          AND rs.code NOT IN ('CERRADO', 'MITIGADO', 'ACEPTADO')
          AND NOT EXISTS (
              SELECT 1 FROM core.alert a
              WHERE a.subject_type = 'core.risk'
                AND a.subject_id = r.id
                AND a.deleted_at IS NULL
                AND a.resolved_at IS NULL
          )
    """))).mappings().all()

    new_alerts = 0
    skipped = 0
    for r in rows:
        alert_id = await _create_risk_alert(
            db, str(r["id"]), r["code"], r["name"],
            r["probability_code"], str(user["id"]),
        )
        if alert_id:
            new_alerts += 1
        else:
            skipped += 1

    await db.commit()
    return {"new_alerts": new_alerts, "skipped": skipped}


# ═══════════════════════════════════════════════════════════════════════════════
# 4. GET /api/risk — paginated list
# ═══════════════════════════════════════════════════════════════════════════════
@router.get("")
async def list_risks(
    user: CurrentUser,
    db=Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    risk_type: str | None = Query(None),
    probability: str | None = Query(None),
    search: str | None = Query(None),
):
    _require_read(user)
    params: dict = {}
    conditions = ["r.deleted_at IS NULL"]
    scope = _scope_where(user, params)
    if scope:
        conditions.append(scope.strip().lstrip("AND").strip())

    if status_filter:
        conditions.append("rs.code = :status_filter")
        params["status_filter"] = status_filter.upper()
    if risk_type:
        conditions.append("rt.code = :risk_type")
        params["risk_type"] = risk_type.upper()
    if probability:
        conditions.append("rp.code = :probability")
        params["probability"] = probability.upper()
    if search:
        conditions.append("(r.name ILIKE :search OR r.code ILIKE :search)")
        params["search"] = f"%{search}%"

    where = " AND ".join(conditions)

    total = (await db.execute(
        text(f"SELECT COUNT(*) {_LIST_FROM} WHERE {where}"), params
    )).scalar() or 0
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    params["limit"] = page_size
    params["offset"] = (page - 1) * page_size
    rows = (await db.execute(text(f"""
        SELECT {_LIST_COLS} {_LIST_FROM}
        WHERE {where}
        ORDER BY r.created_at DESC
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    return {
        "items": [dict(r) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 5. POST /api/risk — create
# ═══════════════════════════════════════════════════════════════════════════════
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_risk(body: dict, user: CurrentUser, db=Depends(get_db)):
    _require_write(user)

    # Advisory lock + code generation
    await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('risk_code'))"))
    max_seq = (await db.execute(text(
        "SELECT COALESCE(MAX(CAST(SUBSTRING(code FROM 5) AS INTEGER)), 0) "
        "FROM core.risk WHERE code ~ '^RSK-[0-9]+$'"
    ))).scalar() or 0
    code = f"RSK-{max_seq + 1:04d}"

    # Resolve category IDs
    status_id = await _cat_id(db, "risk_status", "IDENTIFICADO")
    risk_type_id = None
    if body.get("risk_type_id"):
        risk_type_id = body["risk_type_id"]
    probability_id = body.get("probability_id")
    impact_id = body.get("impact_id")

    result = await db.execute(
        text("""
            INSERT INTO core.risk
                (code, name, risk_type_id, probability_id, impact_id,
                 subject_type, subject_id, mitigation_plan, status_id,
                 identified_at, created_by_id)
            VALUES
                (:code, :name, :risk_type_id, :probability_id, :impact_id,
                 :subject_type, :subject_id, :mitigation_plan, :status_id,
                 :identified_at, :created_by_id)
            RETURNING id
        """),
        {
            "code": code,
            "name": body["name"],
            "risk_type_id": risk_type_id,
            "probability_id": probability_id,
            "impact_id": impact_id,
            "subject_type": body["subject_type"],
            "subject_id": body["subject_id"],
            "mitigation_plan": body.get("mitigation_plan"),
            "status_id": status_id,
            "identified_at": body.get("identified_at"),
            "created_by_id": str(user["id"]),
        },
    )
    risk_id = str(result.scalar())

    await record_event(db, "RISK_CREATED", "core.risk", risk_id, user["id"],
                       {"code": code, "name": body["name"]})
    await db.commit()

    # Fetch and return detail
    row = (await db.execute(
        text(f"SELECT {_DETAIL_COLS} {_DETAIL_FROM} WHERE r.id = :id"),
        {"id": risk_id},
    )).mappings().first()
    return dict(row)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. GET /api/risk/{id} — detail
# ═══════════════════════════════════════════════════════════════════════════════
@router.get("/{risk_id}")
async def get_risk(risk_id: UUID, user: CurrentUser, db=Depends(get_db)):
    _require_read(user)
    row = (await db.execute(
        text(f"SELECT {_DETAIL_COLS} {_DETAIL_FROM} WHERE r.id = :id AND r.deleted_at IS NULL"),
        {"id": str(risk_id)},
    )).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Riesgo no encontrado")
    return dict(row)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. PATCH /api/risk/{id} — update + FSM transition
# ═══════════════════════════════════════════════════════════════════════════════
@router.patch("/{risk_id}")
async def update_risk(risk_id: UUID, body: dict, user: CurrentUser, db=Depends(get_db)):
    _require_write(user)

    existing = (await db.execute(text("""
        SELECT r.id, rs.code AS current_status
        FROM core.risk r
        JOIN ref.category rs ON rs.id = r.status_id
        WHERE r.id = :id AND r.deleted_at IS NULL
    """), {"id": str(risk_id)})).mappings().first()
    if not existing:
        raise HTTPException(status_code=404, detail="Riesgo no encontrado")

    updates = ["updated_at = NOW()", "updated_by_id = :updated_by_id"]
    params: dict = {"id": str(risk_id), "updated_by_id": str(user["id"])}

    # FSM transition
    old_status = None
    if "status_id" in body:
        new_status_code = body.pop("status_id").upper() if isinstance(body.get("status_id"), str) else None
        if new_status_code:
            # Resolve code to UUID
            target_row = (await db.execute(
                text("SELECT id, code FROM ref.category WHERE scheme = 'risk_status' AND code = :c"),
                {"c": new_status_code},
            )).mappings().first()
            if not target_row:
                raise HTTPException(status_code=400, detail=f"Estado inválido: {new_status_code}")

            current = existing["current_status"]
            allowed = _FSM.get(current, set())
            if new_status_code not in allowed:
                raise HTTPException(
                    status_code=422,
                    detail=f"Transición inválida: {current} → {new_status_code}. "
                           f"Permitidas: {', '.join(sorted(allowed)) if allowed else 'ninguna'}",
                )
            updates.append("status_id = :new_status_id")
            params["new_status_id"] = str(target_row["id"])
            old_status = current

    # Regular fields
    for field in _FIELD_ALLOWLIST:
        if field in body and body[field] is not None:
            updates.append(f"{field} = :{field}")
            params[field] = body[field]

    await db.execute(
        text(f"UPDATE core.risk SET {', '.join(updates)} WHERE id = :id"),
        params,
    )

    if old_status:
        await record_event(db, "RISK_STATUS_CHANGE", "core.risk", risk_id, user["id"],
                           {"old_status": old_status, "new_status": params.get("new_status_id")})

    await db.commit()

    row = (await db.execute(
        text(f"SELECT {_DETAIL_COLS} {_DETAIL_FROM} WHERE r.id = :id"),
        {"id": str(risk_id)},
    )).mappings().first()
    return dict(row)


# ═══════════════════════════════════════════════════════════════════════════════
# 8. DELETE /api/risk/{id} — soft-delete
# ═══════════════════════════════════════════════════════════════════════════════
@router.delete("/{risk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_risk(risk_id: UUID, user: CurrentUser, db=Depends(get_db)):
    _require_write(user)
    result = await db.execute(
        text("""
            UPDATE core.risk
            SET deleted_at = NOW(), updated_at = NOW(),
                deleted_by_id = :uid, updated_by_id = :uid
            WHERE id = :id AND deleted_at IS NULL
        """),
        {"id": str(risk_id), "uid": str(user["id"])},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Riesgo no encontrado")
    await db.commit()
    return Response(status_code=204)
