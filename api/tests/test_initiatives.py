"""Tests for initiative CRUD and Kanban movement."""
import uuid
from tests.conftest import auth


async def _create_initiative(client, token, **overrides):
    payload = {
        "name": f"Test Initiative {uuid.uuid4().hex[:8]}",
        **overrides,
    }
    resp = await client.post("/api/dgi/initiatives", json=payload, headers=auth(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_create_initiative(client, dgi_token):
    """Create initiative defaults to BACKLOG with auto-generated code."""
    data = await _create_initiative(client, dgi_token)
    assert data["code"].startswith("INI-")
    assert data["status"] == "BACKLOG"


async def test_move_to_en_curso(client, dgi_token):
    """Move initiative from BACKLOG to EN_CURSO."""
    data = await _create_initiative(client, dgi_token)
    resp = await client.post(
        f"/api/dgi/initiatives/{data['id']}/move",
        json={"status": "EN_CURSO"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "EN_CURSO"


async def test_move_beyond_legacy_fixed_caps(client, dgi_token):
    """C62 removed fixed caps; Kanban movement remains available at prior thresholds."""
    for target_status, quantity in (("EN_CURSO", 6), ("REVISION", 3)):
        for _ in range(quantity):
            data = await _create_initiative(client, dgi_token)
            resp = await client.post(
                f"/api/dgi/initiatives/{data['id']}/move",
                json={"status": target_status},
                headers=auth(dgi_token),
            )
            assert resp.status_code == 200


async def test_move_to_completado(client, dgi_token):
    """Move an initiative from BACKLOG to COMPLETADO."""
    data = await _create_initiative(client, dgi_token)
    resp = await client.post(
        f"/api/dgi/initiatives/{data['id']}/move",
        json={"status": "COMPLETADO"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "COMPLETADO"


async def test_move_noop(client, dgi_token):
    """Moving to current status is a no-op (returns 200)."""
    data = await _create_initiative(client, dgi_token)
    # Already BACKLOG, move to BACKLOG
    resp = await client.post(
        f"/api/dgi/initiatives/{data['id']}/move",
        json={"status": "BACKLOG"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "BACKLOG"


async def test_operational_user_forbidden(client, regional_token):
    """Operational users cannot manage DGI initiatives."""
    resp = await client.post(
        "/api/dgi/initiatives",
        json={"name": "Should fail"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 403
