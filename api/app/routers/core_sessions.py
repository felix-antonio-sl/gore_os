import math
from fastapi import APIRouter, Depends, Query, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.deps import CurrentUser
from app.core.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.core_session import (
    CoreSessionCreate,
    CoreSessionListItem,
    CoreSessionDetail,
    TopicCreate,
    TopicWithVotes,
    VoteCreate,
    MemberAttendance,
    FinalizarBody,
)

router = APIRouter(prefix="/api/core-sessions", tags=["core-sessions"])

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CORE_COMMITTEE_CODE = "CONSEJO-REGIONAL"
CORE_COMMITTEE_NAME = "Consejo Regional de Ñuble"
CORE_MEMBER_COUNT = 16
QUORUM_SIMPLE = 9       # >50%
QUORUM_CALIFICADA = 11  # ≥2/3
UTM_VALUE = 67_294       # UTM feb 2026
CORE_THRESHOLD_UTM = 7_000

_MANAGER_ROLES = {
    "ADMIN_SISTEMA", "ADMIN_REGIONAL", "SECRETARIO_EJECUTIVO", "GOBERNADOR",
}
_ALL_CORE_ROLES = _MANAGER_ROLES | {"CONSEJERO_REGIONAL"}


def _require_manager(user: dict) -> None:
    if user["role_code"] not in _MANAGER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sin permisos suficientes",
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _ensure_core_committee(db: AsyncSession) -> str:
    """Find or create the CORE committee. Returns its id as string."""
    result = await db.execute(
        text("SELECT id FROM core.committee WHERE code = :code AND deleted_at IS NULL"),
        {"code": CORE_COMMITTEE_CODE},
    )
    row = result.mappings().first()
    if row:
        return str(row["id"])

    # Look up committee_type = CORE
    ct_result = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'committee_type' AND code = 'CORE'"),
    )
    ct_row = ct_result.mappings().first()
    ct_id = str(ct_row["id"]) if ct_row else None

    result = await db.execute(
        text("""
            INSERT INTO core.committee (code, name, committee_type_id, is_permanent)
            VALUES (:code, :name, :ct_id, TRUE)
            RETURNING id
        """),
        {"code": CORE_COMMITTEE_CODE, "name": CORE_COMMITTEE_NAME, "ct_id": ct_id},
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


async def _get_session_or_404(session_id: UUID, db: AsyncSession) -> dict:
    result = await db.execute(
        text("""
            SELECT
                s.id,
                s.committee_id,
                s.session_number,
                s.scheduled_at,
                s.started_at,
                s.ended_at,
                s.location,
                s.quorum_reached,
                st.code AS session_type,
                m.id AS minute_id,
                s.metadata
            FROM core.session s
            LEFT JOIN ref.category st ON st.id = s.session_type_id
            LEFT JOIN core.minute m ON m.session_id = s.id
            WHERE s.id = :id AND s.deleted_at IS NULL
        """),
        {"id": str(session_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada")
    return dict(row)


def _compute_status(row: dict) -> str:
    if row.get("ended_at"):
        return "FINALIZADA"
    if row.get("started_at"):
        return "EN_CURSO"
    return "PROGRAMADA"


def _compute_vote_result(
    votes_favor: int, votes_contra: int, quorum_type: str
) -> str:
    """Compute vote result based on quorum type."""
    required = QUORUM_CALIFICADA if quorum_type == "CALIFICADA" else QUORUM_SIMPLE
    total = votes_favor + votes_contra
    if total == 0:
        return "PENDIENTE"
    if votes_favor >= required:
        return "APROBADO"
    # Check if it's still possible to reach quorum
    remaining = CORE_MEMBER_COUNT - (votes_favor + votes_contra)
    if votes_favor + remaining < required:
        return "RECHAZADO"
    return "PENDIENTE"


async def _build_topics_with_votes(
    minute_id: str, db: AsyncSession
) -> list[TopicWithVotes]:
    """Fetch topics with vote counts for a session."""
    topics_result = await db.execute(
        text("""
            SELECT
                sa.id,
                sa.agreement_number,
                sa.subject,
                sa.decision,
                sa.ipr_id,
                ipr.codigo_bip AS ipr_codigo_bip,
                COALESCE(sa.metadata->>'quorum_type', 'SIMPLE') AS quorum_type,
                COALESCE(
                    (SELECT COUNT(*) FROM core.session_vote sv
                     JOIN ref.category vc ON vc.id = sv.vote_option_id
                     WHERE sv.session_agreement_id = sa.id AND vc.code = 'A_FAVOR'), 0
                ) AS votes_favor,
                COALESCE(
                    (SELECT COUNT(*) FROM core.session_vote sv
                     JOIN ref.category vc ON vc.id = sv.vote_option_id
                     WHERE sv.session_agreement_id = sa.id AND vc.code = 'EN_CONTRA'), 0
                ) AS votes_contra,
                COALESCE(
                    (SELECT COUNT(*) FROM core.session_vote sv
                     JOIN ref.category vc ON vc.id = sv.vote_option_id
                     WHERE sv.session_agreement_id = sa.id AND vc.code = 'ABSTENCION'), 0
                ) AS votes_abstencion
            FROM core.session_agreement sa
            LEFT JOIN core.ipr ipr ON ipr.id = sa.ipr_id
            WHERE sa.minute_id = :minute_id
            ORDER BY sa.agreement_number ASC
        """),
        {"minute_id": minute_id},
    )
    topics = []
    for t in topics_result.mappings().all():
        qt = t["quorum_type"]
        required = QUORUM_CALIFICADA if qt == "CALIFICADA" else QUORUM_SIMPLE
        favor = t["votes_favor"]
        contra = t["votes_contra"]
        abstencion = t["votes_abstencion"]
        result = _compute_vote_result(favor, contra, qt)
        topics.append(TopicWithVotes(
            id=t["id"],
            agreement_number=t["agreement_number"],
            subject=t["subject"],
            decision=t["decision"],
            ipr_id=t["ipr_id"],
            ipr_codigo_bip=t["ipr_codigo_bip"],
            quorum_type=qt,
            votes_favor=favor,
            votes_contra=contra,
            votes_abstencion=abstencion,
            votes_total=favor + contra + abstencion,
            required_votes=required,
            result=result,
        ))
    return topics


async def _count_members(committee_id: str, db: AsyncSession) -> int:
    """Count active voting members in committee."""
    result = await db.execute(
        text("""
            SELECT COUNT(*) FROM core.committee_member
            WHERE committee_id = :cid AND is_voting_member = TRUE
              AND (end_date IS NULL OR end_date >= CURRENT_DATE)
        """),
        {"cid": committee_id},
    )
    return result.scalar() or 0


async def _count_voters_in_session(session_id: str, db: AsyncSession) -> int:
    """Count distinct voters who have cast votes in this session."""
    result = await db.execute(
        text("""
            SELECT COUNT(DISTINCT sv.voter_id)
            FROM core.session_vote sv
            JOIN core.session_agreement sa ON sa.id = sv.session_agreement_id
            JOIN core.minute m ON m.id = sa.minute_id
            WHERE m.session_id = :sid
        """),
        {"sid": session_id},
    )
    return result.scalar() or 0


# ---------------------------------------------------------------------------
# POST /api/core-sessions — Create CORE session
# ---------------------------------------------------------------------------

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_core_session(
    body: CoreSessionCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_manager(user)
    committee_id = await _ensure_core_committee(db)
    session_number = await _next_session_number(committee_id, db)

    # Resolve session_type_id
    st_result = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'session_type' AND code = :code"),
        {"code": body.session_type},
    )
    st_row = st_result.mappings().first()
    if not st_row:
        raise HTTPException(status_code=400, detail=f"Tipo de sesión inválido: {body.session_type}")
    session_type_id = str(st_row["id"])

    # 1. Create session
    session_result = await db.execute(
        text("""
            INSERT INTO core.session (
                committee_id, session_number, session_type_id,
                scheduled_at, location, created_by_id
            ) VALUES (
                :committee_id, :session_number, :session_type_id,
                :scheduled_at, :location, :created_by_id
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
        },
    )
    session_id = str(session_result.mappings().first()["id"])

    # 2. Auto-create minute
    minute_number = f"ACTA-CORE-{session_number}"
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
    return {"id": session_id, "session_number": session_number}


# ---------------------------------------------------------------------------
# GET /api/core-sessions — List CORE sessions (paginated)
# ---------------------------------------------------------------------------

@router.get("", response_model=PaginatedResponse)
async def list_core_sessions(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    session_type: str | None = Query(None),
):
    committee_id = await _ensure_core_committee(db)

    params: dict = {"cid": committee_id}
    conditions = ["s.committee_id = :cid", "s.deleted_at IS NULL"]

    if status_filter:
        if status_filter == "FINALIZADA":
            conditions.append("s.ended_at IS NOT NULL")
        elif status_filter == "EN_CURSO":
            conditions.append("s.started_at IS NOT NULL AND s.ended_at IS NULL")
        elif status_filter == "PROGRAMADA":
            conditions.append("s.started_at IS NULL AND s.ended_at IS NULL")

    if session_type:
        conditions.append("st.code = :st_code")
        params["st_code"] = session_type

    where_clause = " AND ".join(conditions)

    base_query = f"""
        FROM core.session s
        LEFT JOIN ref.category st ON st.id = s.session_type_id
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
                s.id,
                s.session_number,
                COALESCE(st.code, 'ORDINARIA') AS session_type,
                s.scheduled_at,
                s.started_at,
                s.ended_at,
                s.quorum_reached,
                COALESCE(s.metadata->>'summary', '') AS summary,
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
        CoreSessionListItem(
            id=r["id"],
            session_number=r["session_number"],
            session_type=r["session_type"],
            scheduled_at=r["scheduled_at"],
            started_at=r["started_at"],
            ended_at=r["ended_at"],
            summary=r["summary"] or None,
            status=_compute_status(dict(r)),
            topic_count=r["topic_count"],
            quorum_reached=r["quorum_reached"],
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
# GET /api/core-sessions/{id} — Detail with topics + vote counts
# ---------------------------------------------------------------------------

@router.get("/{session_id}", response_model=CoreSessionDetail)
async def get_core_session(
    session_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_session_or_404(session_id, db)
    minute_id = row.get("minute_id")

    topics: list[TopicWithVotes] = []
    if minute_id:
        topics = await _build_topics_with_votes(str(minute_id), db)

    members_total = await _count_members(str(row["committee_id"]), db)
    members_present = await _count_voters_in_session(str(session_id), db)

    return CoreSessionDetail(
        id=row["id"],
        session_number=row["session_number"],
        session_type=row.get("session_type") or "ORDINARIA",
        scheduled_at=row["scheduled_at"],
        started_at=row["started_at"],
        ended_at=row["ended_at"],
        summary=(row.get("metadata") or {}).get("summary"),
        status=_compute_status(row),
        topic_count=len(topics),
        quorum_reached=row["quorum_reached"],
        location=row["location"],
        minute_id=minute_id,
        topics=topics,
        members_present=members_present,
        members_total=members_total,
    )


# ---------------------------------------------------------------------------
# POST /api/core-sessions/{id}/iniciar — Start session
# ---------------------------------------------------------------------------

@router.post("/{session_id}/iniciar")
async def start_core_session(
    session_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_manager(user)
    row = await _get_session_or_404(session_id, db)

    if row.get("started_at"):
        raise HTTPException(status_code=400, detail="La sesión ya fue iniciada")

    # Check quorum: at least QUORUM_SIMPLE members registered
    member_count = await _count_members(str(row["committee_id"]), db)
    quorum_reached = member_count >= QUORUM_SIMPLE

    await db.execute(
        text("""
            UPDATE core.session
            SET started_at = NOW(), quorum_reached = :quorum, updated_at = NOW()
            WHERE id = :id
        """),
        {"id": str(session_id), "quorum": quorum_reached},
    )
    await db.commit()
    return {
        "message": "Sesión iniciada",
        "quorum_reached": quorum_reached,
        "members_registered": member_count,
    }


# ---------------------------------------------------------------------------
# POST /api/core-sessions/{id}/finalizar — End session
# ---------------------------------------------------------------------------

@router.post("/{session_id}/finalizar")
async def finish_core_session(
    session_id: UUID,
    body: FinalizarBody,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_manager(user)
    row = await _get_session_or_404(session_id, db)

    if not row.get("started_at"):
        raise HTTPException(status_code=400, detail="La sesión no ha sido iniciada")
    if row.get("ended_at"):
        raise HTTPException(status_code=400, detail="La sesión ya fue finalizada")

    # Store summary in metadata jsonb
    if body.summary:
        await db.execute(
            text("""
                UPDATE core.session
                SET ended_at = NOW(), updated_at = NOW(),
                    metadata = jsonb_set(COALESCE(metadata, '{}'), '{summary}', CAST(:summary AS jsonb))
                WHERE id = :id
            """),
            {"id": str(session_id), "summary": f'"{body.summary}"'},
        )
    else:
        await db.execute(
            text("UPDATE core.session SET ended_at = NOW(), updated_at = NOW() WHERE id = :id"),
            {"id": str(session_id)},
        )

    await db.commit()
    return {"message": "Sesión finalizada"}


# ---------------------------------------------------------------------------
# POST /api/core-sessions/{id}/temas — Add topic for voting
# ---------------------------------------------------------------------------

@router.post("/{session_id}/temas", status_code=status.HTTP_201_CREATED)
async def add_topic(
    session_id: UUID,
    body: TopicCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    _require_manager(user)
    row = await _get_session_or_404(session_id, db)
    minute_id = row.get("minute_id")
    if not minute_id:
        raise HTTPException(status_code=400, detail="No hay acta asociada a esta sesión")

    if row.get("ended_at"):
        raise HTTPException(status_code=400, detail="No se pueden agregar temas a una sesión finalizada")

    # Auto-increment agreement_number
    next_num_result = await db.execute(
        text("SELECT COALESCE(MAX(agreement_number), 0) + 1 AS next_num FROM core.session_agreement WHERE minute_id = :mid"),
        {"mid": str(minute_id)},
    )
    next_num = next_num_result.mappings().first()["next_num"]

    # Store quorum_type in metadata since session_agreement doesn't have the column
    sa_result = await db.execute(
        text("""
            INSERT INTO core.session_agreement (
                minute_id, agreement_number, subject, decision,
                ipr_id, created_by_id,
                metadata
            ) VALUES (
                :minute_id, :agreement_number, :subject, '',
                :ipr_id, :created_by_id,
                CAST(:metadata AS jsonb)
            )
            RETURNING id
        """),
        {
            "minute_id": str(minute_id),
            "agreement_number": next_num,
            "subject": body.subject,
            "ipr_id": str(body.ipr_id) if body.ipr_id else None,
            "created_by_id": str(user["id"]),
            "metadata": f'{{"quorum_type": "{body.quorum_type}"}}',
        },
    )
    sa_id = str(sa_result.mappings().first()["id"])

    await db.commit()
    return {"id": sa_id, "agreement_number": next_num}


# ---------------------------------------------------------------------------
# POST /api/core-sessions/{id}/temas/{tema_id}/votar — Cast vote
# ---------------------------------------------------------------------------

@router.post("/{session_id}/temas/{tema_id}/votar")
async def cast_vote(
    session_id: UUID,
    tema_id: UUID,
    body: VoteCreate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    if user["role_code"] != "CONSEJERO_REGIONAL":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo consejeros regionales pueden votar",
        )

    row = await _get_session_or_404(session_id, db)
    if not row.get("started_at"):
        raise HTTPException(status_code=400, detail="La sesión no ha sido iniciada")
    if row.get("ended_at"):
        raise HTTPException(status_code=400, detail="La sesión ya fue finalizada")

    # Verify topic belongs to this session
    topic_check = await db.execute(
        text("""
            SELECT sa.id FROM core.session_agreement sa
            JOIN core.minute m ON m.id = sa.minute_id
            WHERE sa.id = :tema_id AND m.session_id = :session_id
        """),
        {"tema_id": str(tema_id), "session_id": str(session_id)},
    )
    if not topic_check.scalar():
        raise HTTPException(status_code=404, detail="Tema no encontrado en esta sesión")

    # Find voter's committee_member record
    voter_result = await db.execute(
        text("""
            SELECT cm.id FROM core.committee_member cm
            JOIN core."user" u ON u.person_id = cm.person_id
            WHERE u.id = :user_id AND cm.committee_id = :cid
              AND cm.is_voting_member = TRUE
              AND (cm.end_date IS NULL OR cm.end_date >= CURRENT_DATE)
        """),
        {"user_id": str(user["id"]), "cid": str(row["committee_id"])},
    )
    voter_row = voter_result.mappings().first()
    if not voter_row:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no es miembro votante del Consejo Regional",
        )
    voter_member_id = str(voter_row["id"])

    # Resolve vote_option_id
    vote_result = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'vote_option' AND code = :code"),
        {"code": body.vote},
    )
    vote_row = vote_result.mappings().first()
    if not vote_row:
        raise HTTPException(status_code=400, detail=f"Opción de voto inválida: {body.vote}")
    vote_option_id = str(vote_row["id"])

    # Insert vote (UNIQUE constraint catches duplicates)
    try:
        await db.execute(
            text("""
                INSERT INTO core.session_vote (session_agreement_id, voter_id, vote_option_id)
                VALUES (:sa_id, :voter_id, :vote_id)
            """),
            {
                "sa_id": str(tema_id),
                "voter_id": voter_member_id,
                "vote_id": vote_option_id,
            },
        )
        await db.commit()
    except Exception as e:
        await db.rollback()
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya registró su voto para este tema",
            )
        raise

    return {"message": "Voto registrado"}


# ---------------------------------------------------------------------------
# GET /api/core-sessions/{id}/temas/{tema_id}/votos — Vote detail
# ---------------------------------------------------------------------------

@router.get("/{session_id}/temas/{tema_id}/votos")
async def get_topic_votes(
    session_id: UUID,
    tema_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    # Verify topic belongs to this session
    topic_check = await db.execute(
        text("""
            SELECT sa.id, COALESCE(sa.metadata->>'quorum_type', 'SIMPLE') AS quorum_type
            FROM core.session_agreement sa
            JOIN core.minute m ON m.id = sa.minute_id
            WHERE sa.id = :tema_id AND m.session_id = :session_id
        """),
        {"tema_id": str(tema_id), "session_id": str(session_id)},
    )
    topic_row = topic_check.mappings().first()
    if not topic_row:
        raise HTTPException(status_code=404, detail="Tema no encontrado en esta sesión")

    quorum_type = topic_row["quorum_type"]
    required = QUORUM_CALIFICADA if quorum_type == "CALIFICADA" else QUORUM_SIMPLE

    # Fetch individual votes
    votes_result = await db.execute(
        text("""
            SELECT
                sv.id AS vote_id,
                (p.names || ' ' || p.paternal_surname) AS voter_name,
                vc.code AS vote,
                vc.label AS vote_label,
                sv.recorded_at
            FROM core.session_vote sv
            JOIN core.committee_member cm ON cm.id = sv.voter_id
            JOIN core.person p ON p.id = cm.person_id
            JOIN ref.category vc ON vc.id = sv.vote_option_id
            WHERE sv.session_agreement_id = :tema_id
            ORDER BY sv.recorded_at ASC
        """),
        {"tema_id": str(tema_id)},
    )
    votes = [dict(r) for r in votes_result.mappings().all()]

    favor = sum(1 for v in votes if v["vote"] == "A_FAVOR")
    contra = sum(1 for v in votes if v["vote"] == "EN_CONTRA")
    abstencion = sum(1 for v in votes if v["vote"] == "ABSTENCION")
    result = _compute_vote_result(favor, contra, quorum_type)

    return {
        "votes": votes,
        "summary": {
            "favor": favor,
            "contra": contra,
            "abstencion": abstencion,
            "total": len(votes),
            "required": required,
            "quorum_type": quorum_type,
            "result": result,
        },
    }


# ---------------------------------------------------------------------------
# GET /api/core-sessions/{id}/miembros — Members with attendance
# ---------------------------------------------------------------------------

@router.get("/{session_id}/miembros", response_model=list[MemberAttendance])
async def get_session_members(
    session_id: UUID,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    row = await _get_session_or_404(session_id, db)

    result = await db.execute(
        text("""
            SELECT
                cm.id AS member_id,
                (p.names || ' ' || p.paternal_surname) AS person_name,
                rc.label AS role_in_committee,
                EXISTS (
                    SELECT 1 FROM core.session_vote sv
                    JOIN core.session_agreement sa ON sa.id = sv.session_agreement_id
                    JOIN core.minute m ON m.id = sa.minute_id
                    WHERE sv.voter_id = cm.id AND m.session_id = :sid
                ) AS has_voted_in_session
            FROM core.committee_member cm
            JOIN core.person p ON p.id = cm.person_id
            LEFT JOIN ref.category rc ON rc.id = cm.role_in_committee_id
            WHERE cm.committee_id = :cid
              AND cm.is_voting_member = TRUE
              AND (cm.end_date IS NULL OR cm.end_date >= CURRENT_DATE)
            ORDER BY p.paternal_surname, p.names
        """),
        {"sid": str(session_id), "cid": str(row["committee_id"])},
    )
    return [
        MemberAttendance(
            member_id=r["member_id"],
            person_name=r["person_name"],
            role_in_committee=r["role_in_committee"],
            has_voted_in_session=r["has_voted_in_session"],
        )
        for r in result.mappings().all()
    ]
