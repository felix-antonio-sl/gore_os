"""Tests for the DGI cockpit endpoint — role-dispatched views."""
import pytest
from sqlalchemy import text
from app.core.security import create_access_token
from tests.conftest import auth, _get_user_id


# ---------------------------------------------------------------------------
# 1. JEFE_DGI gets semaforo-based cockpit
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_jefe_dgi_cockpit(client, dgi_token):
    """GET /api/dgi/cockpit with JEFE_DGI token returns 200 with semaforo."""
    resp = await client.get("/api/dgi/cockpit", headers=auth(dgi_token))
    assert resp.status_code == 200
    body = resp.json()
    # JEFE_DGI cockpit includes semaforo and decisions_pending
    assert "semaforo" in body
    assert "decisions_pending" in body
    assert isinstance(body["semaforo"], list)
    assert isinstance(body["decisions_pending"], int)


# ---------------------------------------------------------------------------
# 2. ESP_CONTROL_GESTION gets indicators/data sources cockpit
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_control_gestion_cockpit(client, db):
    """GET /api/dgi/cockpit with ESP_CONTROL_GESTION token returns indicator view."""
    uid = await _get_user_id(db, "control.gestion@goreos.cl")
    token = create_access_token({"sub": uid, "role": "ESP_CONTROL_GESTION"})

    resp = await client.get("/api/dgi/cockpit", headers=auth(token))
    assert resp.status_code == 200
    body = resp.json()
    # ESP_CONTROL_GESTION cockpit includes data_sources, trends, work_queue
    assert "data_sources" in body
    assert "trends" in body
    assert "work_queue" in body
    assert isinstance(body["data_sources"], list)
    assert isinstance(body["trends"], list)
    assert isinstance(body["work_queue"], list)


# ---------------------------------------------------------------------------
# 3. Non-DGI role falls through to jefe_dgi view (no 403 — fallback by design)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_non_dgi_gets_fallback_view(client, regional_token):
    """GET /api/dgi/cockpit with ADMIN_REGIONAL returns 200 (fallback to jefe_dgi view).

    The cockpit endpoint does not restrict access to DGI roles — non-DGI users
    fall through to the JEFE_DGI view. This is by design (see dgi_cockpit.py).
    """
    resp = await client.get("/api/dgi/cockpit", headers=auth(regional_token))
    assert resp.status_code == 200
    body = resp.json()
    # Fallback returns JEFE_DGI cockpit shape
    assert "semaforo" in body
    assert "decisions_pending" in body


# ---------------------------------------------------------------------------
# 4. Requires authentication
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cockpit_requires_auth(client):
    """GET /api/dgi/cockpit without token returns 401."""
    resp = await client.get("/api/dgi/cockpit")
    assert resp.status_code == 401
