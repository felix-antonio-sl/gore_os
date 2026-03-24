"""
AR Coordination + Division Interactions router (Wave B).
Consolidated Calendar endpoint (Wave D — CI-019).

Cadena 1: AR prep view, decisions CRUD, escalate to AR.
Cadena 4: Division interaction log + matrix view.
Cadena 5: Calendar — UNION ALL across 5 DGI event sources.
"""

import json
import math
from datetime import date, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from app.core.audit import record_event
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import DGI_ROLES

from app.schemas.dgi import (
    ARDecisionCreate,
    ARDecisionUpdate,
    ARDecisionItem,
    InteractionCreate,
    InteractionUpdate,
    InteractionItem,
    InteractionMatrixRow,
    CalendarEvent,
)

router = APIRouter(prefix="/api/dgi/coordination", tags=["dgi"])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DGI_WRITE_ROLES = {"JEFE_DGI", "ESP_CONTROL_GESTION"}
_READ_ROLES = {*DGI_ROLES, "ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR"}


def _require_dgi_read(user: dict) -> None:
    if user.get("role_code") not in _READ_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso de lectura restringido a roles DGI y ejecutivos",
        )


def _require_dgi_write(user: dict) -> None:
    if user.get("role_code") not in _DGI_WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo JEFE_DGI o ESP_CONTROL_GESTION pueden gestionar coordinación",
        )


async def _get_category_id(db: AsyncSession, scheme: str, code: str) -> str:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = :scheme AND code = :code"),
        {"scheme": scheme, "code": code},
    )).mappings().first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Código inválido para {scheme}: {code}",
        )
    return str(row["id"])


# ---------------------------------------------------------------------------
# AR Decision SQL fragments
# ---------------------------------------------------------------------------

_DEC_COLS = """
    d.id,
    d.description,
    dt.code   AS decision_type,
    dt.label  AS decision_type_label,
    st.code   AS status,
    st.label  AS status_label,
    d.due_date,
    d.context,
    p.names || ' ' || p.paternal_surname AS responsible_name,
    d.resolved_at,
    d.created_at
"""

_DEC_FROM = """
    FROM core.dgi_ar_decision d
    JOIN ref.category dt ON dt.id = d.decision_type_id
    JOIN ref.category st ON st.id = d.status_id
    LEFT JOIN core."user" u ON u.id = d.responsible_id
    LEFT JOIN core.person p ON p.id = u.person_id
"""


def _row_to_decision(r: dict) -> ARDecisionItem:
    return ARDecisionItem(
        id=r["id"],
        description=r["description"],
        decision_type=r["decision_type"],
        decision_type_label=r["decision_type_label"],
        status=r["status"],
        status_label=r["status_label"],
        due_date=r["due_date"],
        context=r["context"],
        responsible_name=r["responsible_name"],
        resolved_at=r["resolved_at"],
        created_at=r["created_at"],
    )


# ═══════════════════════════════════════════════════════════════════════════
# CADENA 1: AR COORDINATION
# ═══════════════════════════════════════════════════════════════════════════

# ---------------------------------------------------------------------------
# 1. GET /ar/prep — AR Preparation view
# ---------------------------------------------------------------------------
@router.get("/ar/prep")
async def get_ar_prep(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Preparation view for AR meeting: active initiatives, top alerts,
    pending decisions.
    """
    _require_dgi_read(user)

    # Active initiatives (EN_CURSO + REVISION)
    ini_rows = (await db.execute(text("""
        SELECT COUNT(*) AS cnt
        FROM core.dgi_initiative i
        JOIN ref.category st ON st.id = i.status_id
        WHERE st.code IN ('EN_CURSO', 'REVISION') AND i.deleted_at IS NULL
    """))).mappings().first()
    active_initiatives = int(ini_rows["cnt"]) if ini_rows else 0

    top_initiatives = (await db.execute(text("""
        SELECT i.id, i.code, i.name, st.code AS status
        FROM core.dgi_initiative i
        JOIN ref.category st ON st.id = i.status_id
        WHERE st.code IN ('EN_CURSO', 'REVISION') AND i.deleted_at IS NULL
        ORDER BY i.target_date ASC NULLS LAST
        LIMIT 3
    """))).mappings().all()

    # Top alerts (CRITICO + ALTO, unresolved)
    alert_rows = (await db.execute(text("""
        SELECT COUNT(*) AS cnt
        FROM core.alert a
        JOIN ref.category sev ON sev.id = a.severity_id
        WHERE sev.code IN ('CRITICO', 'ALTO')
          AND a.resolved_at IS NULL AND a.deleted_at IS NULL
    """))).mappings().first()
    pending_alerts = int(alert_rows["cnt"]) if alert_rows else 0

    top_alerts = (await db.execute(text("""
        SELECT a.id, a.message, sev.code AS severity
        FROM core.alert a
        JOIN ref.category sev ON sev.id = a.severity_id
        WHERE sev.code IN ('CRITICO', 'ALTO')
          AND a.resolved_at IS NULL AND a.deleted_at IS NULL
        ORDER BY a.triggered_at DESC
        LIMIT 3
    """))).mappings().all()

    # Pending decisions
    dec_rows = (await db.execute(text("""
        SELECT COUNT(*) AS cnt
        FROM core.dgi_ar_decision d
        JOIN ref.category st ON st.id = d.status_id
        WHERE st.code IN ('PENDIENTE', 'EN_EJECUCION') AND d.deleted_at IS NULL
    """))).mappings().first()
    pending_decisions = int(dec_rows["cnt"]) if dec_rows else 0

    top_decisions = (await db.execute(text(f"""
        SELECT {_DEC_COLS} {_DEC_FROM}
        WHERE st.code IN ('PENDIENTE', 'EN_EJECUCION') AND d.deleted_at IS NULL
        ORDER BY d.due_date ASC NULLS LAST
        LIMIT 3
    """))).mappings().all()

    return {
        "initiatives": {
            "count": active_initiatives,
            "top": [dict(r) for r in top_initiatives],
        },
        "alerts": {
            "count": pending_alerts,
            "top": [dict(r) for r in top_alerts],
        },
        "decisions": {
            "count": pending_decisions,
            "top": [_row_to_decision(dict(r)).model_dump() for r in top_decisions],
        },
    }


# ---------------------------------------------------------------------------
# 2. GET /ar/decisions — List AR decisions
# ---------------------------------------------------------------------------
@router.get("/ar/decisions")
async def list_ar_decisions(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
    type_filter: str | None = Query(None, alias="type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    _require_dgi_read(user)

    conditions = ["d.deleted_at IS NULL"]
    params: dict = {}

    if status_filter:
        conditions.append("st.code = :status_filter")
        params["status_filter"] = status_filter.upper()

    if type_filter:
        conditions.append("dt.code = :type_filter")
        params["type_filter"] = type_filter.upper()

    where = " AND ".join(conditions)

    count_result = await db.execute(
        text(f"SELECT COUNT(*) {_DEC_FROM} WHERE {where}"), params,
    )
    total = count_result.scalar() or 0
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(text(f"""
        SELECT {_DEC_COLS} {_DEC_FROM}
        WHERE {where}
        ORDER BY d.created_at DESC
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    items = [_row_to_decision(dict(r)).model_dump() for r in rows]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------------------
# 3. POST /ar/decisions — Create AR decision
# ---------------------------------------------------------------------------
@router.post("/ar/decisions", status_code=status.HTTP_201_CREATED,
             response_model=ARDecisionItem)
async def create_ar_decision(
    body: ARDecisionCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi_write(user)

    type_id = await _get_category_id(db, "dgi_ar_decision_type", body.decision_type.upper())
    status_id = await _get_category_id(db, "dgi_ar_decision_status", "PENDIENTE")

    result = await db.execute(
        text("""
            INSERT INTO core.dgi_ar_decision
                (description, decision_type_id, status_id, due_date, context,
                 responsible_id, created_by_id)
            VALUES
                (:description, :type_id, :status_id, :due_date, :context,
                 :responsible_id, :created_by_id)
            RETURNING id
        """),
        {
            "description": body.description,
            "type_id": type_id,
            "status_id": status_id,
            "due_date": body.due_date,
            "context": body.context,
            "responsible_id": str(body.responsible_id) if body.responsible_id else None,
            "created_by_id": str(user["id"]),
        },
    )
    new_id = str(result.scalar())
    await record_event(db, "DECISION_CREATED", "core.dgi_ar_decision", new_id, user["id"],
                       {"decision_type": body.decision_type})
    await db.commit()

    row = (await db.execute(
        text(f"SELECT {_DEC_COLS} {_DEC_FROM} WHERE d.id = :id"),
        {"id": new_id},
    )).mappings().first()
    return _row_to_decision(dict(row))


# ---------------------------------------------------------------------------
# 4. PATCH /ar/decisions/{id} — Update AR decision
# ---------------------------------------------------------------------------
@router.patch("/ar/decisions/{decision_id}", response_model=ARDecisionItem)
async def update_ar_decision(
    decision_id: UUID,
    body: ARDecisionUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi_write(user)

    decision_id_str = str(decision_id)

    existing = (await db.execute(
        text(f"SELECT d.id, st.code AS current_status {_DEC_FROM} WHERE d.id = :id AND d.deleted_at IS NULL"),
        {"id": decision_id_str},
    )).mappings().first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decisión no encontrada")

    updates: list[str] = []
    params: dict = {"id": decision_id_str}

    body_data = body.model_dump(exclude_none=True)

    # Field updates
    for field in ("description", "due_date", "context"):
        if field in body_data:
            updates.append(f"{field} = :{field}")
            params[field] = body_data[field]

    if "responsible_id" in body_data:
        updates.append("responsible_id = :responsible_id")
        params["responsible_id"] = str(body_data["responsible_id"])

    # Status transition (DB trigger validates)
    if body.status is not None:
        new_status_id = await _get_category_id(db, "dgi_ar_decision_status", body.status.upper())
        updates.append("status_id = :new_status_id")
        params["new_status_id"] = new_status_id

    if not updates:
        row = (await db.execute(
            text(f"SELECT {_DEC_COLS} {_DEC_FROM} WHERE d.id = :id"),
            {"id": decision_id_str},
        )).mappings().first()
        return _row_to_decision(dict(row))

    updates.append("updated_at = NOW()")
    set_clause = ", ".join(updates)

    try:
        await db.execute(
            text(f"UPDATE core.dgi_ar_decision SET {set_clause} WHERE id = :id"),
            params,
        )
        if body.status is not None:
            await record_event(db, "DECISION_STATUS_CHANGE", "core.dgi_ar_decision",
                               decision_id, user["id"],
                               {"old_status": existing["current_status"], "new_status": body.status.upper()})
        await db.commit()
    except (IntegrityError, DBAPIError) as e:
        await db.rollback()
        err = str(e)
        if "Transición inválida" in err:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)
        raise

    row = (await db.execute(
        text(f"SELECT {_DEC_COLS} {_DEC_FROM} WHERE d.id = :id"),
        {"id": decision_id_str},
    )).mappings().first()
    return _row_to_decision(dict(row))


# ---------------------------------------------------------------------------
# 5. DELETE /ar/decisions/{id} — Soft-delete
# ---------------------------------------------------------------------------
@router.delete("/ar/decisions/{decision_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ar_decision(
    decision_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi_write(user)

    result = await db.execute(
        text("""
            UPDATE core.dgi_ar_decision
            SET deleted_at = NOW(), updated_at = NOW()
            WHERE id = :id AND deleted_at IS NULL
        """),
        {"id": str(decision_id)},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decisión no encontrada")
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════════════════════
# CADENA 4: DIVISION INTERACTIONS
# ═══════════════════════════════════════════════════════════════════════════

_INT_COLS = """
    i.id,
    i.division_id,
    org.name        AS division_name,
    it.code         AS interaction_type,
    it.label        AS interaction_type_label,
    i.interaction_date,
    i.participants,
    i.topics,
    i.agreements,
    i.next_date,
    i.notes,
    i.created_at
"""

_INT_FROM = """
    FROM core.dgi_division_interaction i
    JOIN core.organization org ON org.id = i.division_id
    JOIN ref.category it ON it.id = i.interaction_type_id
"""


def _row_to_interaction(r: dict) -> InteractionItem:
    return InteractionItem(
        id=r["id"],
        division_id=r["division_id"],
        division_name=r["division_name"],
        interaction_type=r["interaction_type"],
        interaction_type_label=r["interaction_type_label"],
        interaction_date=r["interaction_date"],
        participants=r["participants"] or [],
        topics=r["topics"] or [],
        agreements=r["agreements"] or [],
        next_date=r["next_date"],
        notes=r["notes"],
        created_at=r["created_at"],
    )


# ---------------------------------------------------------------------------
# 6. GET /interactions — List interactions
# ---------------------------------------------------------------------------
@router.get("/interactions")
async def list_interactions(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    division_id: UUID | None = None,
    type_filter: str | None = Query(None, alias="type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    _require_dgi_read(user)

    conditions = ["i.deleted_at IS NULL"]
    params: dict = {}

    if division_id:
        conditions.append("i.division_id = :division_id")
        params["division_id"] = str(division_id)

    if type_filter:
        conditions.append("it.code = :type_filter")
        params["type_filter"] = type_filter.upper()

    where = " AND ".join(conditions)

    count_result = await db.execute(
        text(f"SELECT COUNT(*) {_INT_FROM} WHERE {where}"), params,
    )
    total = count_result.scalar() or 0
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(text(f"""
        SELECT {_INT_COLS} {_INT_FROM}
        WHERE {where}
        ORDER BY i.interaction_date DESC
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    items = [_row_to_interaction(dict(r)).model_dump() for r in rows]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------------------
# 7. POST /interactions — Create interaction
# ---------------------------------------------------------------------------
@router.post("/interactions", status_code=status.HTTP_201_CREATED,
             response_model=InteractionItem)
async def create_interaction(
    body: InteractionCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi_write(user)

    type_id = await _get_category_id(db, "dgi_interaction_type", body.interaction_type.upper())

    result = await db.execute(
        text("""
            INSERT INTO core.dgi_division_interaction
                (division_id, interaction_type_id, interaction_date,
                 participants, topics, agreements, next_date, notes, created_by_id)
            VALUES
                (:division_id, :type_id, :interaction_date,
                 CAST(:participants AS jsonb), CAST(:topics AS jsonb),
                 CAST(:agreements AS jsonb), :next_date, :notes, :created_by_id)
            RETURNING id
        """),
        {
            "division_id": str(body.division_id),
            "type_id": type_id,
            "interaction_date": body.interaction_date or date.today(),
            "participants": json.dumps(body.participants or []),
            "topics": json.dumps(body.topics or []),
            "agreements": json.dumps(body.agreements or []),
            "next_date": body.next_date,
            "notes": body.notes,
            "created_by_id": str(user["id"]),
        },
    )
    new_id = str(result.scalar())
    await db.commit()

    row = (await db.execute(
        text(f"SELECT {_INT_COLS} {_INT_FROM} WHERE i.id = :id"),
        {"id": new_id},
    )).mappings().first()
    return _row_to_interaction(dict(row))


# ---------------------------------------------------------------------------
# 8. PATCH /interactions/{id} — Update interaction
# ---------------------------------------------------------------------------
@router.patch("/interactions/{interaction_id}", response_model=InteractionItem)
async def update_interaction(
    interaction_id: UUID,
    body: InteractionUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi_write(user)

    iid = str(interaction_id)

    existing = (await db.execute(
        text(f"SELECT i.id {_INT_FROM} WHERE i.id = :id AND i.deleted_at IS NULL"),
        {"id": iid},
    )).mappings().first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interacción no encontrada")

    updates: list[str] = []
    params: dict = {"id": iid}

    body_data = body.model_dump(exclude_none=True)

    for field in ("interaction_date", "next_date", "notes"):
        if field in body_data:
            updates.append(f"{field} = :{field}")
            params[field] = body_data[field]

    if "interaction_type" in body_data:
        type_id = await _get_category_id(db, "dgi_interaction_type", body_data["interaction_type"].upper())
        updates.append("interaction_type_id = :type_id")
        params["type_id"] = type_id

    for json_field in ("participants", "topics", "agreements"):
        if json_field in body_data:
            updates.append(f"{json_field} = CAST(:{json_field} AS jsonb)")
            params[json_field] = json.dumps(body_data[json_field])

    if not updates:
        row = (await db.execute(
            text(f"SELECT {_INT_COLS} {_INT_FROM} WHERE i.id = :id"),
            {"id": iid},
        )).mappings().first()
        return _row_to_interaction(dict(row))

    updates.append("updated_at = NOW()")
    set_clause = ", ".join(updates)

    await db.execute(
        text(f"UPDATE core.dgi_division_interaction SET {set_clause} WHERE id = :id"),
        params,
    )
    await db.commit()

    row = (await db.execute(
        text(f"SELECT {_INT_COLS} {_INT_FROM} WHERE i.id = :id"),
        {"id": iid},
    )).mappings().first()
    return _row_to_interaction(dict(row))


# ---------------------------------------------------------------------------
# 9. DELETE /interactions/{id} — Soft-delete
# ---------------------------------------------------------------------------
@router.delete("/interactions/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interaction(
    interaction_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi_write(user)

    result = await db.execute(
        text("""
            UPDATE core.dgi_division_interaction
            SET deleted_at = NOW(), updated_at = NOW()
            WHERE id = :id AND deleted_at IS NULL
        """),
        {"id": str(interaction_id)},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interacción no encontrada")
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# 10. GET /interactions/matrix — Division × interaction matrix
# ---------------------------------------------------------------------------
@router.get("/interactions/matrix", response_model=list[InteractionMatrixRow])
async def get_interaction_matrix(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Matrix view: divisions × last interaction × next planned × counts.
    """
    _require_dgi_read(user)

    rows = (await db.execute(text("""
        WITH division_stats AS (
            SELECT
                org.id          AS division_id,
                org.name        AS division_name,
                MAX(i.interaction_date)  AS last_interaction,
                MIN(i.next_date)         AS next_planned,
                COUNT(i.id)              AS interaction_count,
                (
                    SELECT COUNT(*)
                    FROM core.dgi_division_interaction ix,
                         jsonb_array_elements(ix.agreements) AS ag
                    WHERE ix.division_id = org.id
                      AND ix.deleted_at IS NULL
                      AND (ag->>'status') IS DISTINCT FROM 'COMPLETADO'
                ) AS pending_agreements,
                (
                    SELECT it2.code
                    FROM core.dgi_division_interaction ix2
                    JOIN ref.category it2 ON it2.id = ix2.interaction_type_id
                    WHERE ix2.division_id = org.id AND ix2.deleted_at IS NULL
                    GROUP BY it2.code
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                ) AS dominant_type
            FROM core.organization org
            JOIN ref.category ot ON ot.id = org.org_type_id
            LEFT JOIN core.dgi_division_interaction i
                ON i.division_id = org.id AND i.deleted_at IS NULL
            WHERE ot.code = 'DIVISION' AND org.deleted_at IS NULL
            GROUP BY org.id, org.name
        )
        SELECT * FROM division_stats
        ORDER BY division_name
    """))).mappings().all()

    return [
        InteractionMatrixRow(
            division_id=r["division_id"],
            division_name=r["division_name"],
            last_interaction=r["last_interaction"],
            next_planned=r["next_planned"],
            interaction_count=r["interaction_count"],
            pending_agreements=r["pending_agreements"] or 0,
            dominant_type=r["dominant_type"],
        )
        for r in rows
    ]


# ═══════════════════════════════════════════════════════════════════════════
# CADENA 5: CONSOLIDATED CALENDAR (Wave D — CI-019)
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/calendar", response_model=list[CalendarEvent])
async def get_consolidated_calendar(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    event_type: str | None = Query(None, alias="type"),
):
    """
    Consolidated DGI calendar: sessions, interactions, decision deadlines,
    escalation deadlines, SLA breach estimates.
    """
    _require_dgi_read(user)

    if not from_date:
        from_date = date.today()
    if not to_date:
        to_date = from_date + timedelta(days=30)

    params: dict = {"from_date": from_date, "to_date": to_date}

    # Build UNION ALL query across 5 event sources
    sources = []

    # 1. TD Committee sessions
    sources.append("""
        SELECT
            s.scheduled_at AS event_date,
            'SESSION' AS event_type,
            'Sesión TD #' || s.session_number AS title,
            COALESCE(s.metadata->>'description', s.location, '') AS description,
            s.id AS entity_id
        FROM core.session s
        JOIN core.committee c ON c.id = s.committee_id
        WHERE c.code IN ('COMITE-TD', 'COMITE-CRISIS')
          AND s.deleted_at IS NULL
          AND s.scheduled_at::date BETWEEN :from_date AND :to_date
    """)

    # 2. Division interactions (next_date)
    sources.append("""
        SELECT
            di.next_date::timestamp AS event_date,
            'INTERACTION' AS event_type,
            'Interacción: ' || org.name AS title,
            COALESCE(di.notes, '') AS description,
            di.id AS entity_id
        FROM core.dgi_division_interaction di
        JOIN core.organization org ON org.id = di.division_id
        WHERE di.deleted_at IS NULL
          AND di.next_date IS NOT NULL
          AND di.next_date BETWEEN :from_date AND :to_date
    """)

    # 3. AR decision deadlines (pending/in progress)
    sources.append("""
        SELECT
            d.due_date::timestamp AS event_date,
            'DECISION' AS event_type,
            d.description AS title,
            dt.label AS description,
            d.id AS entity_id
        FROM core.dgi_ar_decision d
        JOIN ref.category st ON st.id = d.status_id
        JOIN ref.category dt ON dt.id = d.decision_type_id
        WHERE d.deleted_at IS NULL
          AND st.code IN ('PENDIENTE', 'EN_EJECUCION')
          AND d.due_date IS NOT NULL
          AND d.due_date BETWEEN :from_date AND :to_date
    """)

    # 4. Escalation deadlines (active)
    sources.append("""
        SELECT
            e.deadline AS event_date,
            'ESCALATION' AS event_type,
            e.code || ': ' || LEFT(e.situation, 60) AS title,
            lv.label AS description,
            e.id AS entity_id
        FROM core.dgi_escalation e
        JOIN ref.category st ON st.id = e.status_id
        JOIN ref.category lv ON lv.id = e.level_id
        WHERE e.deleted_at IS NULL
          AND st.code IN ('ABIERTO', 'EN_GESTION')
          AND e.deadline IS NOT NULL
          AND e.deadline::date BETWEEN :from_date AND :to_date
    """)

    # 5. SLA breach estimates (open requests)
    sources.append("""
        SELECT
            (sr.created_at + (COALESCE(svc.sla_days, 5) || ' days')::interval) AS event_date,
            'SLA' AS event_type,
            'SLA: ' || svc.name || ' — ' || sr.code AS title,
            sr.description AS description,
            sr.id AS entity_id
        FROM core.dgi_service_request sr
        JOIN core.dgi_service svc ON svc.id = sr.service_id
        JOIN ref.category rst ON rst.id = sr.status_id
        WHERE rst.code NOT IN ('COMPLETADA', 'RECHAZADA')
          AND (sr.created_at + (COALESCE(svc.sla_days, 5) || ' days')::interval)::date
              BETWEEN :from_date AND :to_date
    """)

    # Filter by event type
    if event_type:
        event_type_upper = event_type.upper()
        sources = [s for i, s in enumerate(sources)
                   if (i == 0 and event_type_upper == "SESSION")
                   or (i == 1 and event_type_upper == "INTERACTION")
                   or (i == 2 and event_type_upper == "DECISION")
                   or (i == 3 and event_type_upper == "ESCALATION")
                   or (i == 4 and event_type_upper == "SLA")]

    if not sources:
        return []

    union_query = " UNION ALL ".join(sources)
    full_query = f"""
        SELECT event_date, event_type, title, description, entity_id
        FROM ({union_query}) AS events
        ORDER BY event_date ASC
        LIMIT 200
    """

    rows = (await db.execute(text(full_query), params)).mappings().all()

    today = datetime.now()
    events = []
    for r in rows:
        ed = r["event_date"]
        if ed is None:
            continue
        # Compute severity by proximity
        if isinstance(ed, date) and not isinstance(ed, datetime):
            ed = datetime.combine(ed, datetime.min.time())
        delta_days = (ed - today).days
        if delta_days < 0:
            severity = "rojo"
        elif delta_days <= 3:
            severity = "amber"
        else:
            severity = "verde"

        events.append(CalendarEvent(
            event_date=ed,
            event_type=r["event_type"],
            title=r["title"] or "",
            description=r["description"],
            entity_id=r["entity_id"],
            severity=severity,
        ))

    return events
