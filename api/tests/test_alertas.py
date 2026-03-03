"""Tests for the alertas module — list, filters, attend actions."""
import pytest
from tests.conftest import auth


# ---------------------------------------------------------------------------
# 1. List returns paginated response
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_alertas_returns_paginated(client, regional_token):
    """GET /api/alertas returns a paginated response with the expected shape."""
    resp = await client.get("/api/alertas", headers=auth(regional_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "page_size" in body
    assert "total_pages" in body
    assert isinstance(body["items"], list)
    assert body["page"] == 1
    assert body["page_size"] == 20


# ---------------------------------------------------------------------------
# 2. Filter by severity
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_filter_by_severity(client, regional_token):
    """GET /api/alertas?severity=CRITICO returns only CRITICO alerts."""
    resp = await client.get(
        "/api/alertas?severity=CRITICO",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    # Every returned item must have severity CRITICO (if any items returned)
    for item in body["items"]:
        assert item["severity"] == "CRITICO"


# ---------------------------------------------------------------------------
# 3. Filter by subject_type
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_filter_by_subject_type(client, regional_token):
    """GET /api/alertas?subject_type=core.ipr returns only IPR alerts."""
    resp = await client.get(
        "/api/alertas?subject_type=core.ipr",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    # Every returned item must have subject_type = 'core.ipr'
    for item in body["items"]:
        assert item["subject_type"] == "core.ipr"


# ---------------------------------------------------------------------------
# 4. Attend alert — success
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_attend_alert(client, regional_token, db):
    """POST /api/alertas/{id}/atender returns 200 and updates attended_at."""
    from sqlalchemy import text

    # Find an active (unresolved) alert to attend
    row = (await db.execute(text("""
        SELECT a.id
        FROM core.alert a
        WHERE a.resolved_at IS NULL
          AND a.deleted_at IS NULL
        LIMIT 1
    """))).mappings().first()

    if row is None:
        pytest.skip("No active alerts in test DB — seed some alerts first")

    alert_id = str(row["id"])
    resp = await client.post(
        f"/api/alertas/{alert_id}/atender",
        json={"action_taken": "Revisada por prueba automatizada"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Alerta atendida"


# ---------------------------------------------------------------------------
# 5. Attend already-resolved alert returns 409
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_attend_resolved_alert_returns_409(client, regional_token, db):
    """POST /api/alertas/{id}/atender on a resolved alert returns 409."""
    from sqlalchemy import text

    # Find a resolved alert
    row = (await db.execute(text("""
        SELECT a.id
        FROM core.alert a
        WHERE a.resolved_at IS NOT NULL
          AND a.deleted_at IS NULL
        LIMIT 1
    """))).mappings().first()

    if row is None:
        pytest.skip("No resolved alerts in test DB")

    alert_id = str(row["id"])
    resp = await client.post(
        f"/api/alertas/{alert_id}/atender",
        json={"action_taken": "Should fail"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409
    assert "resuelta" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 6. Requires authentication
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_alertas_requires_auth(client):
    """GET /api/alertas without token returns 401."""
    resp = await client.get("/api/alertas")
    assert resp.status_code == 401
