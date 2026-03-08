"""Tests for Kanban WIP limits and initiative CRUD."""
import uuid
import pytest
from sqlalchemy import text
from tests.conftest import auth


@pytest.fixture
async def clean_initiatives(db):
    """Soft-delete accumulated initiatives from prior runs to prevent WIP pollution."""
    await db.execute(text(
        "UPDATE core.dgi_initiative SET deleted_at = NOW() WHERE deleted_at IS NULL"
    ))
    await db.commit()


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


async def test_move_to_en_curso(client, dgi_token, clean_initiatives):
    """Move initiative from BACKLOG to EN_CURSO."""
    data = await _create_initiative(client, dgi_token)
    resp = await client.post(
        f"/api/dgi/initiatives/{data['id']}/move",
        json={"status": "EN_CURSO"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "EN_CURSO"


async def test_wip_limit_en_curso(client, dgi_token, clean_initiatives):
    """6th initiative in EN_CURSO triggers 409 (limit 5)."""
    # Create 5 in EN_CURSO
    for _ in range(5):
        data = await _create_initiative(client, dgi_token)
        await client.post(
            f"/api/dgi/initiatives/{data['id']}/move",
            json={"status": "EN_CURSO"},
            headers=auth(dgi_token),
        )

    # 6th should fail
    data = await _create_initiative(client, dgi_token)
    resp = await client.post(
        f"/api/dgi/initiatives/{data['id']}/move",
        json={"status": "EN_CURSO"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 409
    assert "WIP" in resp.json()["detail"]


async def test_wip_limit_revision(client, dgi_token, clean_initiatives):
    """3rd initiative in REVISION triggers 409 (limit 2)."""
    for _ in range(2):
        data = await _create_initiative(client, dgi_token)
        await client.post(
            f"/api/dgi/initiatives/{data['id']}/move",
            json={"status": "REVISION"},
            headers=auth(dgi_token),
        )

    data = await _create_initiative(client, dgi_token)
    resp = await client.post(
        f"/api/dgi/initiatives/{data['id']}/move",
        json={"status": "REVISION"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 409


async def test_move_to_completado_no_limit(client, dgi_token):
    """COMPLETADO has no WIP limit."""
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
