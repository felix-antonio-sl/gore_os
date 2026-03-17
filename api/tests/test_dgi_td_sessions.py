"""
Integration tests for DGI TD Committee Sessions router (Wave D — CI-016).

10 tests covering:
- Session CRUD: create, list, detail (3)
- Session FSM: PROGRAMADA -> EN_CURSO -> FINALIZADA (1)
- FSM guards: cannot start twice, cannot finalize before starting (2)
- Topics: add topic, update topic with agreement (2)
- Topic guard: cannot add to finalized session (1)
- Role restrictions: analista_token -> 403 (1)
"""

import pytest
from httpx import AsyncClient
from tests.conftest import auth


# ═══════════════════════════════════════════════════════════════════════════
# SESSION CRUD
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_td_session_create(client: AsyncClient, dgi_token):
    """JEFE_DGI can create a TD session."""
    resp = await client.post(
        "/api/dgi/td-sessions",
        json={
            "scheduled_at": "2026-04-15T10:00:00",
            "description": "Reunion mensual TD",
            "location": "Sala 3",
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert "session_number" in data
    assert data["session_number"] >= 1


@pytest.mark.asyncio
async def test_td_session_list(client: AsyncClient, dgi_token):
    """List TD sessions with pagination."""
    # Create one first
    await client.post(
        "/api/dgi/td-sessions",
        json={
            "scheduled_at": "2026-04-20T14:00:00",
            "description": "Test list session",
        },
        headers=auth(dgi_token),
    )

    resp = await client.get(
        "/api/dgi/td-sessions",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["total"] >= 1

    # Verify item structure
    item = data["items"][0]
    assert "session_number" in item
    assert "scheduled_at" in item
    assert "status" in item
    assert item["status"] in ("PROGRAMADA", "EN_CURSO", "FINALIZADA")
    assert "topic_count" in item
    assert "pending_agreements" in item


@pytest.mark.asyncio
async def test_td_session_detail(client: AsyncClient, dgi_token):
    """Get TD session detail with topics."""
    create_resp = await client.post(
        "/api/dgi/td-sessions",
        json={
            "scheduled_at": "2026-05-01T09:00:00",
            "description": "Detail test session",
            "location": "Oficina DGI",
        },
        headers=auth(dgi_token),
    )
    session_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/dgi/td-sessions/{session_id}",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == session_id
    assert data["status"] == "PROGRAMADA"
    assert data["location"] == "Oficina DGI"
    assert data["description"] == "Detail test session"
    assert "topics" in data
    assert isinstance(data["topics"], list)


# ═══════════════════════════════════════════════════════════════════════════
# SESSION FSM
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_td_session_fsm_full(client: AsyncClient, dgi_token):
    """Full FSM: PROGRAMADA -> EN_CURSO -> FINALIZADA."""
    create_resp = await client.post(
        "/api/dgi/td-sessions",
        json={"scheduled_at": "2026-05-10T10:00:00"},
        headers=auth(dgi_token),
    )
    session_id = create_resp.json()["id"]

    # Verify initial state
    detail = await client.get(
        f"/api/dgi/td-sessions/{session_id}",
        headers=auth(dgi_token),
    )
    assert detail.json()["status"] == "PROGRAMADA"

    # PROGRAMADA -> EN_CURSO (iniciar)
    r1 = await client.patch(
        f"/api/dgi/td-sessions/{session_id}",
        params={"action": "iniciar"},
        headers=auth(dgi_token),
    )
    assert r1.status_code == 200
    assert r1.json()["message"] == "Sesión iniciada"

    # Verify EN_CURSO
    detail2 = await client.get(
        f"/api/dgi/td-sessions/{session_id}",
        headers=auth(dgi_token),
    )
    assert detail2.json()["status"] == "EN_CURSO"
    assert detail2.json()["started_at"] is not None

    # EN_CURSO -> FINALIZADA (finalizar with summary)
    r2 = await client.patch(
        f"/api/dgi/td-sessions/{session_id}",
        params={"action": "finalizar", "summary": "Se revisaron 3 temas pendientes"},
        headers=auth(dgi_token),
    )
    assert r2.status_code == 200
    assert r2.json()["message"] == "Sesión finalizada"

    # Verify FINALIZADA
    detail3 = await client.get(
        f"/api/dgi/td-sessions/{session_id}",
        headers=auth(dgi_token),
    )
    assert detail3.json()["status"] == "FINALIZADA"
    assert detail3.json()["ended_at"] is not None


@pytest.mark.asyncio
async def test_td_session_cannot_start_twice(client: AsyncClient, dgi_token):
    """Cannot start an already started session."""
    create_resp = await client.post(
        "/api/dgi/td-sessions",
        json={"scheduled_at": "2026-05-11T10:00:00"},
        headers=auth(dgi_token),
    )
    session_id = create_resp.json()["id"]

    # Start
    await client.patch(
        f"/api/dgi/td-sessions/{session_id}",
        params={"action": "iniciar"},
        headers=auth(dgi_token),
    )

    # Try to start again
    resp = await client.patch(
        f"/api/dgi/td-sessions/{session_id}",
        params={"action": "iniciar"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 400
    assert "ya fue iniciada" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_td_session_cannot_finalize_before_starting(client: AsyncClient, dgi_token):
    """Cannot finalize a session that has not been started."""
    create_resp = await client.post(
        "/api/dgi/td-sessions",
        json={"scheduled_at": "2026-05-12T10:00:00"},
        headers=auth(dgi_token),
    )
    session_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/dgi/td-sessions/{session_id}",
        params={"action": "finalizar"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 400
    assert "no ha sido iniciada" in resp.json()["detail"]


# ═══════════════════════════════════════════════════════════════════════════
# TOPICS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_td_topic_add(client: AsyncClient, dgi_token):
    """Add a topic to a TD session."""
    create_resp = await client.post(
        "/api/dgi/td-sessions",
        json={"scheduled_at": "2026-05-15T10:00:00"},
        headers=auth(dgi_token),
    )
    session_id = create_resp.json()["id"]

    resp = await client.post(
        f"/api/dgi/td-sessions/{session_id}/topics",
        json={"subject": "Avance firma electronica"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["topic_number"] == 1

    # Add second topic
    resp2 = await client.post(
        f"/api/dgi/td-sessions/{session_id}/topics",
        json={"subject": "Estado plataforma GESDOC"},
        headers=auth(dgi_token),
    )
    assert resp2.status_code == 201
    assert resp2.json()["topic_number"] == 2

    # Verify topics appear in detail
    detail = await client.get(
        f"/api/dgi/td-sessions/{session_id}",
        headers=auth(dgi_token),
    )
    assert detail.json()["topic_count"] == 2
    assert len(detail.json()["topics"]) == 2


@pytest.mark.asyncio
async def test_td_topic_update(client: AsyncClient, dgi_token):
    """Update topic subject and add agreement."""
    create_resp = await client.post(
        "/api/dgi/td-sessions",
        json={"scheduled_at": "2026-05-16T10:00:00"},
        headers=auth(dgi_token),
    )
    session_id = create_resp.json()["id"]

    topic_resp = await client.post(
        f"/api/dgi/td-sessions/{session_id}/topics",
        json={"subject": "Original subject"},
        headers=auth(dgi_token),
    )
    topic_id = topic_resp.json()["id"]

    # Update subject
    resp = await client.patch(
        f"/api/dgi/td-sessions/{session_id}/topics/{topic_id}",
        json={"subject": "Updated subject", "agreement": "Se acuerda implementar en Q2"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Tema actualizado"

    # Verify in detail
    detail = await client.get(
        f"/api/dgi/td-sessions/{session_id}",
        headers=auth(dgi_token),
    )
    topic = detail.json()["topics"][0]
    assert topic["subject"] == "Updated subject"
    assert topic["agreement"] == "Se acuerda implementar en Q2"


@pytest.mark.asyncio
async def test_td_topic_cannot_add_to_finalized(client: AsyncClient, dgi_token):
    """Cannot add topics to a finalized session."""
    create_resp = await client.post(
        "/api/dgi/td-sessions",
        json={"scheduled_at": "2026-05-17T10:00:00"},
        headers=auth(dgi_token),
    )
    session_id = create_resp.json()["id"]

    # Start and finalize
    await client.patch(
        f"/api/dgi/td-sessions/{session_id}",
        params={"action": "iniciar"},
        headers=auth(dgi_token),
    )
    await client.patch(
        f"/api/dgi/td-sessions/{session_id}",
        params={"action": "finalizar"},
        headers=auth(dgi_token),
    )

    # Try to add topic
    resp = await client.post(
        f"/api/dgi/td-sessions/{session_id}/topics",
        json={"subject": "Should fail"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 400
    assert "finalizada" in resp.json()["detail"]


# ═══════════════════════════════════════════════════════════════════════════
# ROLE RESTRICTIONS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_analista_cannot_access_td_sessions(client: AsyncClient, analista_token):
    """Operational roles (ANALISTA) cannot access TD session endpoints."""
    # List
    resp_list = await client.get(
        "/api/dgi/td-sessions",
        headers=auth(analista_token),
    )
    assert resp_list.status_code == 403

    # Create
    resp_create = await client.post(
        "/api/dgi/td-sessions",
        json={"scheduled_at": "2026-06-01T10:00:00"},
        headers=auth(analista_token),
    )
    assert resp_create.status_code == 403
