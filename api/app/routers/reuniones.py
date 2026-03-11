import math
from fastapi import APIRouter, Depends, Query, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.audit import record_event
from app.schemas.common import PaginatedResponse
from app.schemas.reuniones import (
    ReunionListItem,
    ReunionDetail,
    ReunionCreate,
    TopicItem,
    TopicCreate,
    TopicUpdate,
    FinalizarBody,
    AutoSuggestion,
)

router = APIRouter(prefix="/api/reuniones", tags=["reuniones"])

CRISIS_COMMITTEE_CODE = "COMITE-CRISIS"
CRISIS_COMMITTEE_NAME = "Comite de Crisis IPR"
_MANAGER_ROLES = {"ADMIN_SISTEMA", "ADMIN_REGIONAL", "JEFE_DIVISION", "GOBERNADOR", "SECRETARIO_EJECUTIVO", "JEFE_DEPARTAMENTO"}


def _require_manager(user: dict) -> None:
    if user["role_code"] not in _MANAGER_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos suficientes")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _ensure_crisis_committee(db: AsyncSession) -> str:
    """Find or create the crisis committee. Returns its id as string."""
    result = await db.execute(
        text("SELECT id FROM core.committee WHERE code = :code AND deleted_at IS NULL"),
        {"code": CRISIS_COMMITTEE_CODE},
    )
    row = result.mappings().first()
    if row:
        return str(row["id"])

    result = await db.execute(
        text("""
            INSERT INTO core.committee (code, name, is_permanent)
            VALUES (:code, :name, FALSE)
            RETURNING id
        """),
        {"code": CRISIS_COMMITTEE_CODE, "name": CRISIS_COMMITTEE_NAME},
    )
    return str(result.mappings().first()["id"])


async def _next_session_number(committee_id: str, db: AsyncSession) -> int:
    result = await db.execute(
        text("SELECT COALESCE(MAX(session_number), 0) + 1 AS next_num FROM core.session WHERE committee_id = :cid"),
        {"cid": committee_id},
    )
    return result.mappings().first()["next_num"]


async def _get_reunion_or_404(reunion_id: UUID, db: AsyncSession) -> dict:
    result = await db.execute(
        text("""
            SELECT
                cm.id,
                cm.session_id,
                s.session_number,
                s.scheduled_at,
                s.location,
                cm.started_at,
                cm.finished_at,
                cm.summary,
                cm.organizer_id,
                (p.names || ' ' || p.paternal_surname) AS organizer_name,
                m.id AS minute_id
            FROM core.crisis_meeting cm
            JOIN core.session s ON s.id = cm.session_id
            LEFT JOIN core."user" u ON u.id = cm.organizer_id
            LEFT JOIN core.person p ON p.id = u.person_id
            LEFT JOIN core.minute m ON m.session_id = s.id
            WHERE cm.id = :id AND cm.deleted_at IS NULL
        """),
        {"id": str(reunion_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reunion no encontrada")
    return dict(row)


def _compute_status(row: dict) -> str:
    if row.get("finished_at"):
        return "FINALIZADA"
    if row.get("started_at"):
        return "EN_CURSO"
    return "PROGRAMADA"


# ---------------------------------------------------------------------------
# GET /api/reuniones — List reuniones (paginated)
# ---------------------------------------------------------------------------

@router.get("", response_model=PaginatedResponse)
async def list_reuniones(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
):
    params: dict = {}
    conditions = ["cm.deleted_at IS NULL"]

    if status_filter:
        if status_filter == "FINALIZADA":
            conditions.append("cm.finished_at IS NOT NULL")
        elif status_filter == "EN_CURSO":
            conditions.append("cm.started_at IS NOT NULL AND cm.finished_at IS NULL")
        elif status_filter == "PROGRAMADA":
            conditions.append("cm.started_at IS NULL AND cm.finished_at IS NULL")

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core.crisis_meeting cm
        JOIN core.session s ON s.id = cm.session_id
        LEFT JOIN core."user" u ON u.id = cm.organizer_id
        LEFT JOIN core.person p ON p.id = u.person_id
        LEFT JOIN core.minute m ON m.session_id = s.id
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
                cm.id,
                cm.session_id,
                s.session_number,
                s.scheduled_at,
                cm.started_at,
                cm.finished_at,
                cm.summary,
                (p.names || ' ' || p.paternal_surname) AS organizer_name,
                COALESCE(
                    (SELECT COUNT(*) FROM core.session_agreement sa WHERE sa.minute_id = m.id),
                    0
                ) AS topic_count
            {base_query}
            ORDER BY s.scheduled_at DESC
            LIMIT :limit OFFSET :offset
        """),
        params,
    )
    rows = rows_result.mappings().all()

    items = [
        ReunionListItem(
            id=r["id"],
            session_id=r["session_id"],
            session_number=r["session_number"],
            scheduled_at=r["scheduled_at"],
            started_at=r["started_at"],
            finished_at=r["finished_at"],
            summary=r["summary"],
            organizer_name=r["organizer_name"],
            status=_compute_status(dict(r)),
            topic_count=r["topic_count"],
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
# POST /api/reuniones — Create reunion
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_reunion(
    body: ReunionCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_manager(user)
    committee_id = await _ensure_crisis_committee(db)
    session_number = await _next_session_number(committee_id, db)

    try:
        # 1. Create session
        session_result = await db.execute(
            text("""
                INSERT INTO core.session (committee_id, session_number, scheduled_at, location, created_by_id)
                VALUES (:committee_id, :session_number, :scheduled_at, :location, :created_by_id)
                RETURNING id
            """),
            {
                "committee_id": committee_id,
                "session_number": session_number,
                "scheduled_at": body.scheduled_at,
                "location": body.location,
                "created_by_id": str(user["id"]),
            },
        )
        session_id = str(session_result.mappings().first()["id"])

        # 2. Create crisis_meeting
        cm_result = await db.execute(
            text("""
                INSERT INTO core.crisis_meeting (session_id, summary, organizer_id, created_by_id)
                VALUES (:session_id, :summary, :organizer_id, :created_by_id)
                RETURNING id
            """),
            {
                "session_id": session_id,
                "summary": body.summary,
                "organizer_id": str(user["id"]),
                "created_by_id": str(user["id"]),
            },
        )
        cm_id = str(cm_result.mappings().first()["id"])

        # 3. Auto-create minute
        minute_number = f"ACT-{session_number}"
        await db.execute(
            text("""
                INSERT INTO core.minute (session_id, minute_number, created_by_id)
                VALUES (:session_id, :minute_number, :created_by_id)
            """),
            {
                "session_id": session_id,
                "minute_number": minute_number,
                "created_by_id": str(user["id"]),
            },
        )

        await db.commit()
        return {"id": cm_id, "session_id": session_id}
    except Exception:
        await db.rollback()
        raise


# ---------------------------------------------------------------------------
# GET /api/reuniones/{id} — Detail with topics
# ---------------------------------------------------------------------------

@router.get("/{reunion_id}", response_model=ReunionDetail)
async def get_reunion(
    reunion_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_reunion_or_404(reunion_id, db)
    minute_id = row.get("minute_id")

    topics: list[TopicItem] = []
    if minute_id:
        topics_result = await db.execute(
            text("""
                SELECT
                    sa.id,
                    sa.agreement_number,
                    sa.subject,
                    sa.decision,
                    sa.due_date,
                    (rp.names || ' ' || rp.paternal_surname) AS responsible_name,
                    sc.code AS status,
                    sa.ipr_id,
                    ipr.codigo_bip AS ipr_codigo_bip,
                    aic.target_type AS context_type
                FROM core.session_agreement sa
                LEFT JOIN core.person rp ON rp.id = sa.responsible_id
                LEFT JOIN ref.category sc ON sc.id = sa.status_id
                LEFT JOIN core.ipr ipr ON ipr.id = sa.ipr_id
                LEFT JOIN core.agenda_item_context aic ON aic.session_agreement_id = sa.id
                WHERE sa.minute_id = :minute_id
                ORDER BY sa.agreement_number ASC
            """),
            {"minute_id": str(minute_id)},
        )
        for t in topics_result.mappings().all():
            topics.append(TopicItem(
                id=t["id"],
                agreement_number=t["agreement_number"],
                subject=t["subject"],
                decision=t["decision"],
                responsible_name=t["responsible_name"],
                due_date=t["due_date"],
                status=t["status"],
                ipr_id=t["ipr_id"],
                ipr_codigo_bip=t["ipr_codigo_bip"],
                context_type=t["context_type"],
            ))

    # Count topics for list fields
    return ReunionDetail(
        id=row["id"],
        session_id=row["session_id"],
        session_number=row["session_number"],
        scheduled_at=row["scheduled_at"],
        started_at=row["started_at"],
        finished_at=row["finished_at"],
        summary=row["summary"],
        organizer_name=row["organizer_name"],
        status=_compute_status(row),
        topic_count=len(topics),
        location=row["location"],
        topics=topics,
    )


# ---------------------------------------------------------------------------
# GET /api/reuniones/{id}/preparar — Auto-suggestions
# ---------------------------------------------------------------------------

@router.get("/{reunion_id}/preparar", response_model=list[AutoSuggestion])
async def preparar_reunion(
    reunion_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await _get_reunion_or_404(reunion_id, db)

    suggestions: list[AutoSuggestion] = []

    # 1. Alertas CRITICO sin resolver
    alertas_result = await db.execute(
        text("""
            SELECT
                a.id,
                a.message,
                sev.label AS severity_label,
                a.subject_id,
                ipr.codigo_bip AS ipr_codigo_bip
            FROM core.alert a
            JOIN ref.category sev ON sev.id = a.severity_id
            LEFT JOIN core.ipr ipr ON ipr.id = a.subject_id AND a.subject_type = 'core.ipr'
            WHERE sev.code = 'CRITICO'
              AND a.resolved_at IS NULL
              AND a.deleted_at IS NULL
            ORDER BY a.triggered_at DESC
            LIMIT 5
        """),
    )
    for r in alertas_result.mappings().all():
        suggestions.append(AutoSuggestion(
            type="alerta_critica",
            subject=f"Alerta critica: {r['message'][:80]}",
            detail=r["message"],
            target_id=r["id"],
            ipr_codigo_bip=r["ipr_codigo_bip"],
        ))

    # 2. Compromisos vencidos mas antiguos
    compromisos_result = await db.execute(
        text("""
            SELECT
                oc.id,
                oc.description,
                oc.due_date,
                ipr.codigo_bip AS ipr_codigo_bip
            FROM core.operational_commitment oc
            JOIN ref.category st ON st.id = oc.state_id
            LEFT JOIN core.ipr ipr ON ipr.id = oc.ipr_id
            WHERE st.code IN ('PENDIENTE', 'EN_PROGRESO')
              AND oc.due_date < CURRENT_DATE
              AND oc.deleted_at IS NULL
            ORDER BY oc.due_date ASC
            LIMIT 5
        """),
    )
    for r in compromisos_result.mappings().all():
        suggestions.append(AutoSuggestion(
            type="compromiso_vencido",
            subject=f"Compromiso vencido: {r['description'][:80]}",
            detail=r["description"],
            target_id=r["id"],
            ipr_codigo_bip=r["ipr_codigo_bip"],
        ))

    # 3. Problemas abiertos > 7 dias
    problemas_result = await db.execute(
        text("""
            SELECT
                ip.id,
                ip.description,
                ip.detected_at,
                ipr.codigo_bip AS ipr_codigo_bip
            FROM core.ipr_problem ip
            JOIN ref.category st ON st.id = ip.state_id
            LEFT JOIN core.ipr ipr ON ipr.id = ip.ipr_id
            WHERE st.code = 'ABIERTO'
              AND ip.detected_at < (CURRENT_DATE - INTERVAL '7 days')
              AND ip.deleted_at IS NULL
            ORDER BY ip.detected_at ASC
            LIMIT 5
        """),
    )
    for r in problemas_result.mappings().all():
        suggestions.append(AutoSuggestion(
            type="problema_abierto",
            subject=f"Problema abierto: {r['description'][:80]}",
            detail=r["description"],
            target_id=r["id"],
            ipr_codigo_bip=r["ipr_codigo_bip"],
        ))

    return suggestions


# ---------------------------------------------------------------------------
# POST /api/reuniones/{id}/temas — Add topic
# ---------------------------------------------------------------------------

@router.post("/{reunion_id}/temas", status_code=status.HTTP_201_CREATED)
async def add_topic(
    reunion_id: UUID,
    body: TopicCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_reunion_or_404(reunion_id, db)
    minute_id = row.get("minute_id")
    if not minute_id:
        raise HTTPException(status_code=400, detail="No hay acta asociada a esta reunion")

    # Get next agreement_number
    next_num_result = await db.execute(
        text("SELECT COALESCE(MAX(agreement_number), 0) + 1 AS next_num FROM core.session_agreement WHERE minute_id = :mid"),
        {"mid": str(minute_id)},
    )
    next_num = next_num_result.mappings().first()["next_num"]

    # Resolve responsible person_id from user table if responsible_id is a user_id
    responsible_person_id = None
    if body.responsible_id:
        person_result = await db.execute(
            text('SELECT person_id FROM core."user" WHERE id = :uid'),
            {"uid": str(body.responsible_id)},
        )
        person_row = person_result.mappings().first()
        if person_row:
            responsible_person_id = str(person_row["person_id"])

    sa_result = await db.execute(
        text("""
            INSERT INTO core.session_agreement (
                minute_id, agreement_number, subject, decision,
                responsible_id, due_date, ipr_id, created_by_id
            ) VALUES (
                :minute_id, :agreement_number, :subject, '',
                :responsible_id, :due_date, :ipr_id, :created_by_id
            )
            RETURNING id
        """),
        {
            "minute_id": str(minute_id),
            "agreement_number": next_num,
            "subject": body.subject,
            "responsible_id": responsible_person_id,
            "due_date": body.due_date,
            "ipr_id": str(body.ipr_id) if body.ipr_id else None,
            "created_by_id": str(user["id"]),
        },
    )
    sa_id = str(sa_result.mappings().first()["id"])

    # Optionally create agenda_item_context if ipr_id provided
    if body.ipr_id:
        await db.execute(
            text("""
                INSERT INTO core.agenda_item_context (session_agreement_id, target_type, target_id, ipr_id)
                VALUES (:sa_id, 'ipr', :target_id, :ipr_id)
            """),
            {
                "sa_id": sa_id,
                "target_id": str(body.ipr_id),
                "ipr_id": str(body.ipr_id),
            },
        )

    await db.commit()
    return {"id": sa_id, "agreement_number": next_num}


# ---------------------------------------------------------------------------
# POST /api/reuniones/{id}/temas/{tema_id}/revisar — Mark topic as reviewed
# ---------------------------------------------------------------------------

@router.post("/{reunion_id}/temas/{tema_id}/revisar")
async def review_topic(
    reunion_id: UUID,
    tema_id: UUID,
    body: TopicUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await _get_reunion_or_404(reunion_id, db)

    # Verify the topic exists
    check = await db.execute(
        text("SELECT 1 FROM core.session_agreement WHERE id = :id"),
        {"id": str(tema_id)},
    )
    if not check.scalar():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tema no encontrado")

    updates = {}
    params: dict = {"id": str(tema_id)}

    if body.decision is not None:
        updates["decision"] = ":decision"
        params["decision"] = body.decision

    if body.status is not None:
        # Look up or create the status category
        status_result = await db.execute(
            text("SELECT id FROM ref.category WHERE scheme = 'session_agreement_status' AND code = :code"),
            {"code": body.status},
        )
        status_row = status_result.mappings().first()
        if status_row:
            updates["status_id"] = ":status_id"
            params["status_id"] = str(status_row["id"])

    if not updates:
        return {"message": "Sin cambios"}

    set_clauses = ", ".join(f"{k} = {v}" for k, v in updates.items())
    await db.execute(
        text(f"UPDATE core.session_agreement SET {set_clauses}, updated_at = NOW() WHERE id = :id"),
        params,
    )
    await db.commit()
    return {"message": "Tema revisado"}


# ---------------------------------------------------------------------------
# POST /api/reuniones/{id}/iniciar — Start reunion
# ---------------------------------------------------------------------------

@router.post("/{reunion_id}/iniciar")
async def start_reunion(
    reunion_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_manager(user)
    row = await _get_reunion_or_404(reunion_id, db)
    if row.get("started_at"):
        raise HTTPException(status_code=400, detail="La reunion ya fue iniciada")

    await db.execute(
        text("UPDATE core.crisis_meeting SET started_at = NOW(), updated_at = NOW() WHERE id = :id"),
        {"id": str(reunion_id)},
    )
    await db.execute(
        text("UPDATE core.session SET started_at = NOW(), updated_at = NOW() WHERE id = :sid"),
        {"sid": str(row["session_id"])},
    )
    await record_event(db, "MEETING_STARTED", "core.crisis_meeting", reunion_id, user["id"])
    await db.commit()
    return {"message": "Reunion iniciada"}


# ---------------------------------------------------------------------------
# POST /api/reuniones/{id}/finalizar — Finish reunion
# ---------------------------------------------------------------------------

@router.post("/{reunion_id}/finalizar")
async def finish_reunion(
    reunion_id: UUID,
    body: FinalizarBody,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_manager(user)
    row = await _get_reunion_or_404(reunion_id, db)
    if not row.get("started_at"):
        raise HTTPException(status_code=400, detail="La reunion no ha sido iniciada")
    if row.get("finished_at"):
        raise HTTPException(status_code=400, detail="La reunion ya fue finalizada")

    params: dict = {"id": str(reunion_id)}
    summary_clause = ""
    if body.summary:
        summary_clause = ", summary = :summary"
        params["summary"] = body.summary

    await db.execute(
        text(f"UPDATE core.crisis_meeting SET finished_at = NOW(), updated_at = NOW(){summary_clause} WHERE id = :id"),
        params,
    )
    await db.execute(
        text("UPDATE core.session SET ended_at = NOW(), updated_at = NOW() WHERE id = :sid"),
        {"sid": str(row["session_id"])},
    )
    await record_event(db, "MEETING_ENDED", "core.crisis_meeting", reunion_id, user["id"])
    await db.commit()
    return {"message": "Reunion finalizada"}


# ---------------------------------------------------------------------------
# E-3: POST /api/reuniones/{id}/decisiones — Create AR decision from meeting
# ---------------------------------------------------------------------------

@router.post("/{reunion_id}/decisiones", status_code=status.HTTP_201_CREATED)
async def create_meeting_decision(
    reunion_id: UUID,
    body: dict,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_manager(user)
    row = await _get_reunion_or_404(reunion_id, db)
    meeting_status = _compute_status(row)
    if meeting_status not in ("EN_CURSO", "FINALIZADA"):
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden crear decisiones en reuniones EN_CURSO o FINALIZADAS",
        )

    session_id = row["session_id"]

    # Resolve decision type
    dt_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'dgi_ar_decision_type' AND code = :code"),
        {"code": body.get("decision_type", "PRIORIDAD")},
    )).mappings().first()
    if not dt_row:
        raise HTTPException(status_code=400, detail="Tipo de decisión inválido")

    # Get PENDIENTE status
    ds_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'dgi_ar_decision_status' AND code = 'PENDIENTE'"),
    )).mappings().first()
    if not ds_row:
        raise HTTPException(status_code=400, detail="Estado PENDIENTE no encontrado")

    result = await db.execute(
        text("""
            INSERT INTO core.dgi_ar_decision
                (description, decision_type_id, status_id, due_date,
                 responsible_id, context, source_session_id, created_by_id)
            VALUES
                (:description, :dt_id, :ds_id, :due_date,
                 :responsible_id, :context, :source_session_id, :created_by_id)
            RETURNING id
        """),
        {
            "description": body["description"],
            "dt_id": str(dt_row["id"]),
            "ds_id": str(ds_row["id"]),
            "due_date": body.get("due_date"),
            "responsible_id": body.get("responsible_id"),
            "context": body.get("context"),
            "source_session_id": str(session_id),
            "created_by_id": str(user["id"]),
        },
    )
    decision_id = str(result.scalar())
    await record_event(db, "DECISION_CREATED", "core.dgi_ar_decision", decision_id, user["id"],
                       {"source": "crisis_meeting", "reunion_id": str(reunion_id)})
    await db.commit()
    return {"id": decision_id, "source_session_id": str(session_id)}


# ---------------------------------------------------------------------------
# E-3: GET /api/reuniones/{id}/decisiones — List decisions from meeting
# ---------------------------------------------------------------------------

@router.get("/{reunion_id}/decisiones")
async def list_meeting_decisions(
    reunion_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_reunion_or_404(reunion_id, db)
    session_id = row["session_id"]

    rows = (await db.execute(text("""
        SELECT d.id, d.description,
               dt.code AS decision_type, dt.label AS decision_type_label,
               ds.code AS status, ds.label AS status_label,
               d.due_date, d.context,
               p.names || ' ' || p.paternal_surname AS responsible_name,
               d.created_at
        FROM core.dgi_ar_decision d
        JOIN ref.category dt ON dt.id = d.decision_type_id
        JOIN ref.category ds ON ds.id = d.status_id
        LEFT JOIN core."user" u ON u.id = d.responsible_id
        LEFT JOIN core.person p ON p.id = u.person_id
        WHERE d.source_session_id = :session_id
          AND d.deleted_at IS NULL
        ORDER BY d.created_at ASC
    """), {"session_id": str(session_id)})).mappings().all()

    return [dict(r) for r in rows]
