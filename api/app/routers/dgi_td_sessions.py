"""
DGI TD Committee Sessions router (Wave D — CI-016).

Thin wrapper over core.session tables for the Transformación Digital committee.
No voting, no quorum, no formal minutes — operational sessions only.
"""

import math
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.core.security import DGI_ROLES
from app.core.audit import record_event
from app.schemas.common import PaginatedResponse
from app.schemas.dgi import (
    TDSessionCreate,
    TDSessionListItem,
    TDSessionDetail,
    TDTopicItem,
    TDTopicCreate,
    TDTopicUpdate,
)

router = APIRouter(prefix="/api/dgi/td-sessions", tags=["dgi"])

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TD_COMMITTEE_CODE = "COMITE-TD"
TD_COMMITTEE_NAME = "Comité de Transformación Digital"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_dgi(user: dict) -> None:
    if user.get("role_code") not in DGI_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo roles DGI pueden acceder al Comité TD",
        )


async def _ensure_td_committee(db: AsyncSession) -> str:
    """Find or create the TD committee. Returns its id as string."""
    result = await db.execute(
        text("SELECT id FROM core.committee WHERE code = :code AND deleted_at IS NULL"),
        {"code": TD_COMMITTEE_CODE},
    )
    row = result.mappings().first()
    if row:
        return str(row["id"])

    ct_result = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'committee_type' AND code = 'OPERATIVO'"),
    )
    ct_row = ct_result.mappings().first()
    ct_id = str(ct_row["id"]) if ct_row else None

    result = await db.execute(
        text("""
            INSERT INTO core.committee (code, name, committee_type_id, is_permanent)
            VALUES (:code, :name, :ct_id, TRUE)
            RETURNING id
        """),
        {"code": TD_COMMITTEE_CODE, "name": TD_COMMITTEE_NAME, "ct_id": ct_id},
    )
    return str(result.mappings().first()["id"])


async def _next_session_number(committee_id: str, db: AsyncSession) -> int:
    result = await db.execute(
        text("""
            SELECT COALESCE(MAX(session_number), 0) + 1 AS next_num
            FROM core.session WHERE committee_id = :cid
        """),
        {"cid": committee_id},
    )
    return result.mappings().first()["next_num"]


def _compute_status(row: dict) -> str:
    if row.get("ended_at"):
        return "FINALIZADA"
    if row.get("started_at"):
        return "EN_CURSO"
    return "PROGRAMADA"


# ---------------------------------------------------------------------------
# 1. GET /api/dgi/td-sessions — List TD sessions
# ---------------------------------------------------------------------------

@router.get("", response_model=PaginatedResponse)
async def list_td_sessions(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
):
    _require_dgi(user)
    committee_id = await _ensure_td_committee(db)

    conditions = ["s.committee_id = :cid", "s.deleted_at IS NULL"]
    params: dict = {"cid": committee_id}

    if status_filter:
        if status_filter == "FINALIZADA":
            conditions.append("s.ended_at IS NOT NULL")
        elif status_filter == "EN_CURSO":
            conditions.append("s.started_at IS NOT NULL AND s.ended_at IS NULL")
        elif status_filter == "PROGRAMADA":
            conditions.append("s.started_at IS NULL AND s.ended_at IS NULL")

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core.session s
        LEFT JOIN core.minute m ON m.session_id = s.id
        WHERE {where_clause}
    """

    total = (await db.execute(text(f"SELECT COUNT(*) {base_query}"), params)).scalar() or 0

    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    rows = (await db.execute(text(f"""
        SELECT
            s.id,
            s.session_number,
            s.scheduled_at,
            s.started_at,
            s.ended_at,
            COALESCE(s.metadata->>'description', '') AS description,
            COALESCE(
                (SELECT COUNT(*) FROM core.session_agreement sa WHERE sa.minute_id = m.id),
                0
            ) AS topic_count,
            COALESCE(
                (SELECT COUNT(*) FROM core.session_agreement sa
                 WHERE sa.minute_id = m.id AND (sa.decision IS NULL OR sa.decision = '')),
                0
            ) AS pending_agreements
        {base_query}
        ORDER BY s.scheduled_at DESC
        LIMIT :limit OFFSET :offset
    """), params)).mappings().all()

    items = [
        TDSessionListItem(
            id=r["id"],
            session_number=r["session_number"],
            scheduled_at=r["scheduled_at"],
            started_at=r["started_at"],
            ended_at=r["ended_at"],
            description=r["description"] or None,
            status=_compute_status(dict(r)),
            topic_count=r["topic_count"],
            pending_agreements=r["pending_agreements"],
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
# 2. POST /api/dgi/td-sessions — Create TD session
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_td_session(
    body: TDSessionCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)
    committee_id = await _ensure_td_committee(db)
    session_number = await _next_session_number(committee_id, db)

    # Resolve session_type_id (default ORDINARIA)
    st_result = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'session_type' AND code = 'ORDINARIA'"),
    )
    st_row = st_result.mappings().first()
    session_type_id = str(st_row["id"]) if st_row else None

    metadata = {}
    if body.description:
        metadata["description"] = body.description

    session_result = await db.execute(
        text("""
            INSERT INTO core.session (
                committee_id, session_number, session_type_id,
                scheduled_at, location, created_by_id, metadata
            ) VALUES (
                :committee_id, :session_number, :session_type_id,
                :scheduled_at, :location, :created_by_id,
                CAST(:metadata AS jsonb)
            )
            RETURNING id
        """),
        {
            "committee_id": committee_id,
            "session_number": session_number,
            "session_type_id": session_type_id,
            "scheduled_at": body.scheduled_at,
            "location": body.location,
            "created_by_id": str(user["id"]),
            "metadata": __import__("json").dumps(metadata),
        },
    )
    session_id = str(session_result.mappings().first()["id"])

    # Auto-create minute
    minute_number = f"ACTA-TD-{session_number}"
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

    await record_event(db, "CREACION", "core.session", session_id, user["id"], {"committee": TD_COMMITTEE_CODE, "session_number": session_number})
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        error_msg = str(e.orig) if e.orig else str(e)
        if "Transición de estado inválida" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=409, detail="Conflicto de integridad")
    return {"id": session_id, "session_number": session_number}


# ---------------------------------------------------------------------------
# 3. GET /api/dgi/td-sessions/{id} — Detail with topics
# ---------------------------------------------------------------------------

@router.get("/{session_id}", response_model=TDSessionDetail)
async def get_td_session(
    session_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    result = await db.execute(
        text("""
            SELECT
                s.id, s.session_number, s.scheduled_at,
                s.started_at, s.ended_at, s.location,
                COALESCE(s.metadata->>'description', '') AS description,
                m.id AS minute_id
            FROM core.session s
            LEFT JOIN core.minute m ON m.session_id = s.id
            WHERE s.id = :id AND s.deleted_at IS NULL
        """),
        {"id": str(session_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión TD no encontrada")

    topics: list[TDTopicItem] = []
    if row["minute_id"]:
        topics_result = await db.execute(
            text("""
                SELECT
                    sa.id,
                    sa.agreement_number,
                    sa.subject,
                    sa.decision,
                    sa.created_at
                FROM core.session_agreement sa
                WHERE sa.minute_id = :mid
                ORDER BY sa.agreement_number ASC
            """),
            {"mid": str(row["minute_id"])},
        )
        topics = [
            TDTopicItem(
                id=t["id"],
                topic_number=t["agreement_number"],
                subject=t["subject"],
                agreement=t["decision"],
                created_at=t["created_at"],
            )
            for t in topics_result.mappings().all()
        ]

    return TDSessionDetail(
        id=row["id"],
        session_number=row["session_number"],
        scheduled_at=row["scheduled_at"],
        started_at=row["started_at"],
        ended_at=row["ended_at"],
        description=row["description"] or None,
        status=_compute_status(dict(row)),
        topic_count=len(topics),
        pending_agreements=sum(1 for t in topics if not t.agreement),
        location=row["location"],
        topics=topics,
    )


# ---------------------------------------------------------------------------
# 4. PATCH /api/dgi/td-sessions/{id} — Update session (status transitions)
# ---------------------------------------------------------------------------

@router.patch("/{session_id}")
async def update_td_session(
    session_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    action: str = Query(..., description="iniciar | finalizar"),
    summary: str | None = Query(None),
):
    _require_dgi(user)

    result = await db.execute(
        text("""
            SELECT s.id, s.started_at, s.ended_at
            FROM core.session s
            WHERE s.id = :id AND s.deleted_at IS NULL
        """),
        {"id": str(session_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión TD no encontrada")

    if action == "iniciar":
        if row["started_at"]:
            raise HTTPException(status_code=400, detail="La sesión ya fue iniciada")
        await db.execute(
            text("UPDATE core.session SET started_at = NOW(), updated_at = NOW() WHERE id = :id"),
            {"id": str(session_id)},
        )
        await record_event(db, "STATE_TRANSITION", "core.session", session_id, user["id"], {"from": "PROGRAMADA", "to": "EN_CURSO"})
        await db.commit()
        return {"message": "Sesión iniciada"}

    elif action == "finalizar":
        if not row["started_at"]:
            raise HTTPException(status_code=400, detail="La sesión no ha sido iniciada")
        if row["ended_at"]:
            raise HTTPException(status_code=400, detail="La sesión ya fue finalizada")

        if summary:
            await db.execute(
                text("""
                    UPDATE core.session
                    SET ended_at = NOW(), updated_at = NOW(),
                        metadata = jsonb_set(COALESCE(metadata, '{}'), '{summary}', CAST(:summary AS jsonb))
                    WHERE id = :id
                """),
                {"id": str(session_id), "summary": f'"{summary}"'},
            )
        else:
            await db.execute(
                text("UPDATE core.session SET ended_at = NOW(), updated_at = NOW() WHERE id = :id"),
                {"id": str(session_id)},
            )
        await record_event(db, "STATE_TRANSITION", "core.session", session_id, user["id"], {"from": "EN_CURSO", "to": "FINALIZADA"})
        await db.commit()
        return {"message": "Sesión finalizada"}

    raise HTTPException(status_code=400, detail=f"Acción inválida: {action}")


# ---------------------------------------------------------------------------
# 5. POST /api/dgi/td-sessions/{id}/topics — Add topic
# ---------------------------------------------------------------------------

@router.post("/{session_id}/topics", status_code=status.HTTP_201_CREATED)
async def add_td_topic(
    session_id: UUID,
    body: TDTopicCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    # Get minute_id
    result = await db.execute(
        text("""
            SELECT m.id AS minute_id, s.ended_at
            FROM core.session s
            JOIN core.minute m ON m.session_id = s.id
            WHERE s.id = :id AND s.deleted_at IS NULL
        """),
        {"id": str(session_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión TD no encontrada")
    if row["ended_at"]:
        raise HTTPException(status_code=400, detail="No se pueden agregar temas a una sesión finalizada")

    # Auto-increment topic number
    next_num = (await db.execute(
        text("SELECT COALESCE(MAX(agreement_number), 0) + 1 AS n FROM core.session_agreement WHERE minute_id = :mid"),
        {"mid": str(row["minute_id"])},
    )).mappings().first()["n"]

    sa_result = await db.execute(
        text("""
            INSERT INTO core.session_agreement (
                minute_id, agreement_number, subject, decision, created_by_id
            ) VALUES (:mid, :num, :subject, '', :uid)
            RETURNING id
        """),
        {
            "mid": str(row["minute_id"]),
            "num": next_num,
            "subject": body.subject,
            "uid": str(user["id"]),
        },
    )
    topic_id = str(sa_result.mappings().first()["id"])
    await record_event(db, "CREACION", "core.session_agreement", topic_id, user["id"], {"session_id": str(session_id)})
    await db.commit()
    return {"id": topic_id, "topic_number": next_num}


# ---------------------------------------------------------------------------
# 6. PATCH /api/dgi/td-sessions/{id}/topics/{tid} — Update topic (agreement)
# ---------------------------------------------------------------------------

@router.patch("/{session_id}/topics/{topic_id}")
async def update_td_topic(
    session_id: UUID,
    topic_id: UUID,
    body: TDTopicUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_dgi(user)

    # Verify topic belongs to this session
    check = await db.execute(
        text("""
            SELECT sa.id FROM core.session_agreement sa
            JOIN core.minute m ON m.id = sa.minute_id
            WHERE sa.id = :tid AND m.session_id = :sid
        """),
        {"tid": str(topic_id), "sid": str(session_id)},
    )
    if not check.scalar():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tema no encontrado en esta sesión")

    updates: list[str] = []
    params: dict = {"tid": str(topic_id)}

    if body.subject is not None:
        updates.append("subject = :subject")
        params["subject"] = body.subject
    if body.agreement is not None:
        updates.append("decision = :decision")
        params["decision"] = body.agreement

    if not updates:
        return {"message": "Sin cambios"}

    updates.append("updated_at = NOW()")
    await db.execute(
        text(f"UPDATE core.session_agreement SET {', '.join(updates)} WHERE id = :tid"),
        params,
    )
    await db.commit()
    return {"message": "Tema actualizado"}
