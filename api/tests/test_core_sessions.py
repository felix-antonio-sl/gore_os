"""Tests for the CORE sessions (Consejo Regional) module — governance + voting."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from tests.conftest import auth


# ---------------------------------------------------------------------------
# Helper: create a CORE session via API
# ---------------------------------------------------------------------------

async def _create_core_session(client, token, session_type="ORDINARIA"):
    """Create a CORE session. Returns {'id', 'session_number'}."""
    resp = await client.post(
        "/api/core-sessions",
        json={
            "scheduled_at": "2026-03-20T10:00:00",
            "session_type": session_type,
            "location": "Sala del Consejo",
        },
        headers=auth(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def _add_topic(client, token, session_id, subject="Tema de prueba", quorum="SIMPLE"):
    """Add a topic to a session. Returns {'id', 'agreement_number'}."""
    resp = await client.post(
        f"/api/core-sessions/{session_id}/temas",
        json={"subject": subject, "quorum_type": quorum},
        headers=auth(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def _ensure_consejero_is_voting_member(db: AsyncSession):
    """Ensure consejero1 is a voting member of CONSEJO-REGIONAL committee."""
    # Get or create the committee
    row = (await db.execute(
        text("SELECT id FROM core.committee WHERE code = 'CONSEJO-REGIONAL' AND deleted_at IS NULL")
    )).mappings().first()
    if not row:
        return  # Committee auto-created by session creation
    committee_id = str(row["id"])

    # Get consejero1's person_id
    person_row = (await db.execute(
        text("""SELECT p.id FROM core.person p
                JOIN core."user" u ON u.person_id = p.id
                WHERE u.email = 'consejero1@goreos.cl'""")
    )).mappings().first()
    if not person_row:
        return
    person_id = str(person_row["id"])

    # Check if already a member
    existing = (await db.execute(
        text("""SELECT id FROM core.committee_member
                WHERE committee_id = :cid AND person_id = :pid"""),
        {"cid": committee_id, "pid": person_id},
    )).mappings().first()
    if not existing:
        await db.execute(
            text("""INSERT INTO core.committee_member
                    (committee_id, person_id, is_voting_member, start_date)
                    VALUES (:cid, :pid, TRUE, CURRENT_DATE)"""),
            {"cid": committee_id, "pid": person_id},
        )
        await db.commit()


# ---------------------------------------------------------------------------
# 1. Create
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_core_session(client, regional_token):
    """POST /api/core-sessions creates session + minute, auto-creates committee."""
    data = await _create_core_session(client, regional_token)
    assert "id" in data
    assert "session_number" in data
    assert data["session_number"] >= 1


# ---------------------------------------------------------------------------
# 2. List
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_core_sessions(client, regional_token):
    """GET /api/core-sessions returns paginated list."""
    await _create_core_session(client, regional_token)

    resp = await client.get("/api/core-sessions", headers=auth(regional_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert body["total"] >= 1
    assert len(body["items"]) >= 1
    item = body["items"][0]
    assert "session_number" in item
    assert "session_type" in item
    assert "status" in item


# ---------------------------------------------------------------------------
# 3. Detail
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_core_session_detail(client, regional_token):
    """GET /api/core-sessions/{id} returns detail with topics and member counts."""
    data = await _create_core_session(client, regional_token)

    resp = await client.get(f"/api/core-sessions/{data['id']}", headers=auth(regional_token))
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["status"] == "PROGRAMADA"
    assert isinstance(detail["topics"], list)
    assert "members_present" in detail
    assert "members_total" in detail


# ---------------------------------------------------------------------------
# 4. Iniciar session
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_iniciar_session(client, regional_token):
    """POST iniciar → session becomes EN_CURSO with quorum info."""
    data = await _create_core_session(client, regional_token)

    resp = await client.post(
        f"/api/core-sessions/{data['id']}/iniciar",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["message"] == "Sesión iniciada"
    assert "quorum_reached" in body
    assert "members_registered" in body

    # Verify status changed
    detail = await client.get(
        f"/api/core-sessions/{data['id']}", headers=auth(regional_token)
    )
    assert detail.json()["status"] == "EN_CURSO"


# ---------------------------------------------------------------------------
# 5. Add topic with quorum type
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_add_tema_with_quorum(client, regional_token):
    """POST temas → creates topic with quorum_type stored in metadata."""
    data = await _create_core_session(client, regional_token)
    topic = await _add_topic(client, regional_token, data["id"], "Aprobacion IPR", "CALIFICADA")

    assert "id" in topic
    assert topic["agreement_number"] == 1

    # Verify in detail
    detail = await client.get(
        f"/api/core-sessions/{data['id']}", headers=auth(regional_token)
    )
    topics = detail.json()["topics"]
    assert len(topics) >= 1
    assert topics[0]["quorum_type"] == "CALIFICADA"
    assert topics[0]["result"] == "PENDIENTE"


# ---------------------------------------------------------------------------
# 6. Vote A_FAVOR (consejero)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_votar_a_favor(client, regional_token, consejero_token, db):
    """POST votar with consejero → 200, vote recorded."""
    data = await _create_core_session(client, regional_token)
    await _ensure_consejero_is_voting_member(db)
    topic = await _add_topic(client, regional_token, data["id"])

    # Must start session first
    await client.post(
        f"/api/core-sessions/{data['id']}/iniciar",
        headers=auth(regional_token),
    )

    resp = await client.post(
        f"/api/core-sessions/{data['id']}/temas/{topic['id']}/votar",
        json={"vote": "A_FAVOR"},
        headers=auth(consejero_token),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["message"] == "Voto registrado"

    # Verify vote in detail
    detail = await client.get(
        f"/api/core-sessions/{data['id']}", headers=auth(regional_token)
    )
    t = detail.json()["topics"][0]
    assert t["votes_favor"] == 1
    assert t["votes_total"] == 1


# ---------------------------------------------------------------------------
# 7. Duplicate vote rejected
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_votar_duplicate_rejected(client, regional_token, consejero_token, db):
    """POST votar x2 by same consejero → 409 second time."""
    data = await _create_core_session(client, regional_token)
    await _ensure_consejero_is_voting_member(db)
    topic = await _add_topic(client, regional_token, data["id"])

    await client.post(
        f"/api/core-sessions/{data['id']}/iniciar",
        headers=auth(regional_token),
    )

    # First vote OK
    resp1 = await client.post(
        f"/api/core-sessions/{data['id']}/temas/{topic['id']}/votar",
        json={"vote": "A_FAVOR"},
        headers=auth(consejero_token),
    )
    assert resp1.status_code == 200

    # Second vote rejected
    resp2 = await client.post(
        f"/api/core-sessions/{data['id']}/temas/{topic['id']}/votar",
        json={"vote": "EN_CONTRA"},
        headers=auth(consejero_token),
    )
    assert resp2.status_code == 409
    assert "Ya registró su voto" in resp2.json()["detail"]


# ---------------------------------------------------------------------------
# 8. Non-consejero cannot vote
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_non_consejero_cannot_vote(client, regional_token):
    """POST votar with non-consejero → 403."""
    data = await _create_core_session(client, regional_token)
    topic = await _add_topic(client, regional_token, data["id"])

    await client.post(
        f"/api/core-sessions/{data['id']}/iniciar",
        headers=auth(regional_token),
    )

    resp = await client.post(
        f"/api/core-sessions/{data['id']}/temas/{topic['id']}/votar",
        json={"vote": "A_FAVOR"},
        headers=auth(regional_token),  # ADMIN_REGIONAL, not CONSEJERO
    )
    assert resp.status_code == 403
    assert "consejeros regionales" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 9. Members endpoint
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_session_members(client, regional_token):
    """GET miembros returns list with attendance info."""
    data = await _create_core_session(client, regional_token)

    resp = await client.get(
        f"/api/core-sessions/{data['id']}/miembros",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    members = resp.json()
    assert isinstance(members, list)
    # Should have members if CORE committee was seeded
    if len(members) > 0:
        m = members[0]
        assert "member_id" in m
        assert "person_name" in m
        assert "has_voted_in_session" in m


# ---------------------------------------------------------------------------
# 10. Finalizar session
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_finalizar_session(client, regional_token):
    """Full lifecycle: create → iniciar → finalizar → FINALIZADA."""
    data = await _create_core_session(client, regional_token)

    # Start
    await client.post(
        f"/api/core-sessions/{data['id']}/iniciar",
        headers=auth(regional_token),
    )

    # Finish
    resp = await client.post(
        f"/api/core-sessions/{data['id']}/finalizar",
        json={"summary": "Sesion completada"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Sesión finalizada"

    # Verify
    detail = await client.get(
        f"/api/core-sessions/{data['id']}", headers=auth(regional_token)
    )
    assert detail.json()["status"] == "FINALIZADA"


@pytest.mark.asyncio
async def test_db_rejects_finishing_session_before_start(client, regional_token, db):
    """A direct SQL write cannot skip PROGRAMADA -> EN_CURSO."""
    data = await _create_core_session(client, regional_token)

    with pytest.raises(DBAPIError, match="cannot finish before it starts"):
        await db.execute(
            text("UPDATE core.session SET ended_at = NOW() WHERE id = :id"),
            {"id": data["id"]},
        )
        await db.commit()
    await db.rollback()


@pytest.mark.asyncio
async def test_db_rejects_reopening_finished_session(client, regional_token, db):
    """A completed session cannot be reopened by clearing ended_at."""
    data = await _create_core_session(client, regional_token)
    await client.post(
        f"/api/core-sessions/{data['id']}/iniciar",
        headers=auth(regional_token),
    )
    await client.post(
        f"/api/core-sessions/{data['id']}/finalizar",
        json={"summary": "Sesion completada"},
        headers=auth(regional_token),
    )

    with pytest.raises(DBAPIError, match="ended_at is immutable"):
        await db.execute(
            text("UPDATE core.session SET ended_at = NULL WHERE id = :id"),
            {"id": data["id"]},
        )
        await db.commit()
    await db.rollback()
