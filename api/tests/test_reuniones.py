"""Tests for the reuniones (crisis meetings) module — full lifecycle."""
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from tests.conftest import auth


# ---------------------------------------------------------------------------
# Helper: create a reunion via API, return response JSON
# ---------------------------------------------------------------------------

async def _create_reunion(client, token):
    """Create a reunion with default payload. Returns {'id', 'session_id'}."""
    resp = await client.post(
        "/api/reuniones",
        json={
            "scheduled_at": "2026-03-15T10:00:00",
            "location": "Sala Principal",
            "summary": "Test reunion",
        },
        headers=auth(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# 1. Create
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_reunion(client, regional_token):
    """POST /api/reuniones creates a crisis meeting + session + minute."""
    data = await _create_reunion(client, regional_token)
    assert "id" in data
    assert "session_id" in data


# ---------------------------------------------------------------------------
# 2. List
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_reuniones(client, regional_token):
    """GET /api/reuniones returns paginated list with at least 1 item."""
    await _create_reunion(client, regional_token)

    resp = await client.get("/api/reuniones", headers=auth(regional_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "page_size" in body
    assert "total_pages" in body
    assert body["total"] >= 1
    assert len(body["items"]) >= 1


# ---------------------------------------------------------------------------
# 3. Detail
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_reunion_detail(client, regional_token):
    """GET /api/reuniones/{id} returns detail with status PROGRAMADA and topics list."""
    data = await _create_reunion(client, regional_token)

    resp = await client.get(f"/api/reuniones/{data['id']}", headers=auth(regional_token))
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["session_number"] >= 1
    assert detail["status"] == "PROGRAMADA"
    assert isinstance(detail["topics"], list)
    assert "location" in detail


# ---------------------------------------------------------------------------
# 4. Iniciar reunion
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_iniciar_reunion(client, regional_token):
    """POST /api/reuniones/{id}/iniciar starts the meeting → EN_CURSO."""
    data = await _create_reunion(client, regional_token)

    resp = await client.post(
        f"/api/reuniones/{data['id']}/iniciar",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Reunion iniciada"

    # Verify status changed
    detail = await client.get(f"/api/reuniones/{data['id']}", headers=auth(regional_token))
    assert detail.json()["status"] == "EN_CURSO"
    assert detail.json()["started_at"] is not None


# ---------------------------------------------------------------------------
# 5. Finalizar reunion
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_finalizar_reunion(client, regional_token):
    """Full lifecycle: create → iniciar → finalizar → FINALIZADA."""
    data = await _create_reunion(client, regional_token)

    # Start first
    await client.post(f"/api/reuniones/{data['id']}/iniciar", headers=auth(regional_token))

    # Finish
    resp = await client.post(
        f"/api/reuniones/{data['id']}/finalizar",
        json={"summary": "Resumen final"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Reunion finalizada"

    # Verify status
    detail = await client.get(f"/api/reuniones/{data['id']}", headers=auth(regional_token))
    assert detail.json()["status"] == "FINALIZADA"
    assert detail.json()["finished_at"] is not None


# ---------------------------------------------------------------------------
# 6. Add topic
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_add_topic(client, regional_token):
    """A new topic starts in the canonical PENDIENTE state."""
    data = await _create_reunion(client, regional_token)

    resp = await client.post(
        f"/api/reuniones/{data['id']}/temas",
        json={"subject": "Tema de prueba"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 201, resp.text
    topic = resp.json()
    assert "id" in topic
    assert "agreement_number" in topic
    assert topic["agreement_number"] == 1

    detail = await client.get(f"/api/reuniones/{data['id']}", headers=auth(regional_token))
    created = next(t for t in detail.json()["topics"] if t["id"] == topic["id"])
    assert created["status"] == "PENDIENTE"


# ---------------------------------------------------------------------------
# 7. Review topic
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_review_topic(client, regional_token):
    """POST /api/reuniones/{id}/temas/{tema_id}/revisar updates decision."""
    data = await _create_reunion(client, regional_token)

    # Add topic first
    topic_resp = await client.post(
        f"/api/reuniones/{data['id']}/temas",
        json={"subject": "Tema para revisar"},
        headers=auth(regional_token),
    )
    topic_id = topic_resp.json()["id"]

    # Review it
    resp = await client.post(
        f"/api/reuniones/{data['id']}/temas/{topic_id}/revisar",
        json={"decision": "Aprobado", "status": "COMPLETADO"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Tema revisado"

    # Verify decision persisted in detail
    detail = await client.get(f"/api/reuniones/{data['id']}", headers=auth(regional_token))
    topics = detail.json()["topics"]
    reviewed = [t for t in topics if t["id"] == topic_id]
    assert len(reviewed) == 1
    assert reviewed[0]["decision"] == "Aprobado"
    assert reviewed[0]["status"] == "COMPLETADO"


@pytest.mark.asyncio
async def test_db_rejects_invalid_topic_status_transition(client, regional_token, db):
    """A direct writer cannot skip PENDIENTE and jump to VERIFICADO."""
    data = await _create_reunion(client, regional_token)
    topic_resp = await client.post(
        f"/api/reuniones/{data['id']}/temas",
        json={"subject": "Tema con estado protegido"},
        headers=auth(regional_token),
    )
    topic_id = topic_resp.json()["id"]

    await db.execute(
        text("""
            UPDATE core.session_agreement
            SET status_id = (
                SELECT id FROM ref.category
                WHERE scheme = 'commitment_state' AND code = 'PENDIENTE'
            )
            WHERE id = :id
        """),
        {"id": topic_id},
    )
    await db.commit()

    with pytest.raises(DBAPIError, match="Transición de estado inválida"):
        await db.execute(
            text("""
                UPDATE core.session_agreement
                SET status_id = (
                    SELECT id FROM ref.category
                    WHERE scheme = 'commitment_state' AND code = 'VERIFICADO'
                )
                WHERE id = :id
            """),
            {"id": topic_id},
        )
        await db.commit()
    await db.rollback()


@pytest.mark.asyncio
async def test_analista_cannot_mutate_reunion_topics(
    client, regional_token, analista_token,
):
    """Topic creation and review use the same manager authority as the meeting."""
    data = await _create_reunion(client, regional_token)

    denied_create = await client.post(
        f"/api/reuniones/{data['id']}/temas",
        json={"subject": "No autorizado"},
        headers=auth(analista_token),
    )
    assert denied_create.status_code == 403

    topic_resp = await client.post(
        f"/api/reuniones/{data['id']}/temas",
        json={"subject": "Tema autorizado"},
        headers=auth(regional_token),
    )
    denied_review = await client.post(
        f"/api/reuniones/{data['id']}/temas/{topic_resp.json()['id']}/revisar",
        json={"decision": "No autorizada", "status": "COMPLETADO"},
        headers=auth(analista_token),
    )
    assert denied_review.status_code == 403


@pytest.mark.asyncio
async def test_cannot_review_topic_through_another_reunion(client, regional_token):
    """The reunion path cannot mutate a topic owned by another session."""
    first = await _create_reunion(client, regional_token)
    second = await _create_reunion(client, regional_token)
    topic_resp = await client.post(
        f"/api/reuniones/{first['id']}/temas",
        json={"subject": "Tema de la primera reunión"},
        headers=auth(regional_token),
    )

    response = await client.post(
        f"/api/reuniones/{second['id']}/temas/{topic_resp.json()['id']}/revisar",
        json={"decision": "Cruce inválido", "status": "COMPLETADO"},
        headers=auth(regional_token),
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# 8. Preparar suggestions
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_preparar_suggestions(client, regional_token):
    """GET /api/reuniones/{id}/preparar returns a list (may be empty in test DB)."""
    data = await _create_reunion(client, regional_token)

    resp = await client.get(
        f"/api/reuniones/{data['id']}/preparar",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    suggestions = resp.json()
    assert isinstance(suggestions, list)
    # Each suggestion (if any) must have the expected shape
    for s in suggestions:
        assert s["type"] in ("alerta_critica", "compromiso_vencido", "problema_abierto")
        assert "subject" in s
        assert "detail" in s
        assert "target_id" in s


# ---------------------------------------------------------------------------
# 9. Double start error
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_double_start_error(client, regional_token):
    """Starting an already-started reunion returns 400."""
    data = await _create_reunion(client, regional_token)

    # Start once — OK
    resp1 = await client.post(f"/api/reuniones/{data['id']}/iniciar", headers=auth(regional_token))
    assert resp1.status_code == 200

    # Start again — 400
    resp2 = await client.post(f"/api/reuniones/{data['id']}/iniciar", headers=auth(regional_token))
    assert resp2.status_code == 400
    assert "ya fue iniciada" in resp2.json()["detail"]


# ---------------------------------------------------------------------------
# 10. Finish before start error
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_finish_before_start_error(client, regional_token):
    """Finishing a reunion that hasn't started returns 400."""
    data = await _create_reunion(client, regional_token)

    resp = await client.post(
        f"/api/reuniones/{data['id']}/finalizar",
        json={"summary": "Should fail"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 400
    assert "no ha sido iniciada" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_session_lifecycle_syncs_crisis_meeting_mirror(client, regional_token, db):
    """The parent session is the sole lifecycle authority for a crisis meeting."""
    data = await _create_reunion(client, regional_token)

    await db.execute(
        text("UPDATE core.session SET started_at = NOW() WHERE id = :id"),
        {"id": data["session_id"]},
    )
    await db.commit()

    row = (await db.execute(
        text("""
            SELECT s.started_at, cm.started_at AS mirror_started_at
            FROM core.session s
            JOIN core.crisis_meeting cm ON cm.session_id = s.id
            WHERE s.id = :id
        """),
        {"id": data["session_id"]},
    )).mappings().one()
    assert row["started_at"] is not None
    assert row["mirror_started_at"] == row["started_at"]


@pytest.mark.asyncio
async def test_db_rejects_direct_crisis_meeting_lifecycle_update(client, regional_token, db):
    """The crisis_meeting lifecycle mirror cannot be mutated directly."""
    data = await _create_reunion(client, regional_token)

    with pytest.raises(DBAPIError, match="lifecycle is derived from core.session"):
        await db.execute(
            text("UPDATE core.crisis_meeting SET started_at = NOW() WHERE id = :id"),
            {"id": data["id"]},
        )
        await db.commit()
    await db.rollback()


# ---------------------------------------------------------------------------
# 11. ANALISTA cannot create reunion (role restriction)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_encargado_cannot_create(client, analista_token):
    """ANALISTA is not a manager role — creation returns 403."""
    resp = await client.post(
        "/api/reuniones",
        json={
            "scheduled_at": "2026-03-15T10:00:00",
            "location": "Test",
        },
        headers=auth(analista_token),
    )
    assert resp.status_code == 403
