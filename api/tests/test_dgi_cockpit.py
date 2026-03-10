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
    # Work queue deadlines include date context
    for item in body["work_queue"]:
        assert "deadline" in item
        assert isinstance(item["deadline"], str)


# ---------------------------------------------------------------------------
# 3. ESP_PROCESOS: typed agenda + portfolio stats
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_procesos_cockpit_typed(client, db):
    """GET /api/dgi/cockpit with ESP_PROCESOS returns typed agenda and portfolio_stats."""
    uid = await _get_user_id(db, "procesos@goreos.cl")
    token = create_access_token({"sub": uid, "role": "ESP_PROCESOS"})

    resp = await client.get("/api/dgi/cockpit", headers=auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert "today_agenda" in body
    assert "portfolio_stats" in body
    # Agenda items are typed AgendaItem dicts
    for item in body["today_agenda"]:
        assert "time" in item
        assert "activity" in item
        assert "process" in item
    # Portfolio stats has typed structure
    ps = body["portfolio_stats"]
    assert isinstance(ps["active"], int)
    assert isinstance(ps["completed"], int)
    assert isinstance(ps["target"], int)
    assert ps["target"] == 5  # named constant _DGI_PORTFOLIO_TARGET


# ---------------------------------------------------------------------------
# 4. ESP_TD: typed decrees + velocity + kb_stats + normative_alerts
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_td_cockpit_typed(client, db):
    """GET /api/dgi/cockpit with ESP_TD returns typed decree/velocity/kb/alerts."""
    uid = await _get_user_id(db, "td@goreos.cl")
    token = create_access_token({"sub": uid, "role": "ESP_TD"})

    resp = await client.get("/api/dgi/cockpit", headers=auth(token))
    assert resp.status_code == 200
    body = resp.json()

    # Velocity is typed VelocityStats
    v = body["velocity"]
    assert isinstance(v["current"], (int, float))
    assert isinstance(v["required"], (int, float))
    assert isinstance(v["months_remaining"], int)

    # KB stats is placeholder
    kb = body["kb_stats"]
    assert kb["module_status"] == "pending"
    assert "message" in kb

    # Decrees come from DB (may be empty in test DB without migration)
    assert isinstance(body["decrees"], list)
    for d in body["decrees"]:
        assert "id" in d
        assert "code" in d
        assert "status" in d

    # Normative alerts derived from decrees
    assert isinstance(body["normative_alerts"], list)


# ---------------------------------------------------------------------------
# 5. Non-DGI role falls through to jefe_dgi view (no 403 — fallback by design)
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
# 6. Requires authentication
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cockpit_requires_auth(client):
    """GET /api/dgi/cockpit without token returns 401."""
    resp = await client.get("/api/dgi/cockpit")
    assert resp.status_code == 401
