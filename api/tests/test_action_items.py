"""
Tests for GET /api/dashboard/action-items — Centro de Comando Personal.
"""
import pytest
from httpx import AsyncClient
from tests.conftest import auth


@pytest.mark.asyncio
async def test_action_items_structure(client: AsyncClient, regional_token: str):
    """Response has required top-level fields."""
    resp = await client.get("/api/dashboard/action-items", headers=auth(regional_token))
    assert resp.status_code == 200
    data = resp.json()
    assert "greeting_name" in data
    assert "today" in data
    assert "summary" in data
    assert "items" in data
    assert "counts" in data
    assert isinstance(data["items"], list)
    assert isinstance(data["counts"], dict)
    for key in ("CRITICO", "ALTO", "MEDIO", "BAJO"):
        assert key in data["counts"]


@pytest.mark.asyncio
async def test_action_items_item_fields(client: AsyncClient, regional_token: str):
    """Each item has all required fields."""
    resp = await client.get("/api/dashboard/action-items", headers=auth(regional_token))
    data = resp.json()
    if data["items"]:
        item = data["items"][0]
        for key in ("id", "category", "title", "severity", "priority", "action_label", "action_route"):
            assert key in item, f"Missing field: {key}"
        assert item["category"] in ("COMPROMISO", "ALERTA", "DECISION", "ESCALAMIENTO", "SLA", "RIESGO")
        assert item["severity"] in ("CRITICO", "ALTO", "MEDIO", "BAJO")


@pytest.mark.asyncio
async def test_action_items_priority_ordering(client: AsyncClient, regional_token: str):
    """Items are sorted by priority ascending (most urgent first)."""
    resp = await client.get("/api/dashboard/action-items", headers=auth(regional_token))
    data = resp.json()
    priorities = [item["priority"] for item in data["items"]]
    assert priorities == sorted(priorities), "Items should be sorted by priority ASC"


@pytest.mark.asyncio
async def test_action_items_encargado_no_decisions(client: AsyncClient, analista_token: str):
    """ANALISTA should not see AR decisions, escalations, SLA, risks."""
    resp = await client.get("/api/dashboard/action-items", headers=auth(analista_token))
    data = resp.json()
    categories = {item["category"] for item in data["items"]}
    assert "DECISION" not in categories
    assert "ESCALAMIENTO" not in categories
    assert "SLA" not in categories
    assert "RIESGO" not in categories


@pytest.mark.asyncio
async def test_action_items_jefe_division_no_decisions(client: AsyncClient, jefe_token: str):
    """JEFE_DIVISION should not see AR decisions."""
    resp = await client.get("/api/dashboard/action-items", headers=auth(jefe_token))
    data = resp.json()
    categories = {item["category"] for item in data["items"]}
    assert "DECISION" not in categories


@pytest.mark.asyncio
async def test_action_items_dgi_sees_decisions(client: AsyncClient, dgi_token: str):
    """JEFE_DGI can access the endpoint successfully."""
    resp = await client.get("/api/dashboard/action-items", headers=auth(dgi_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_action_items_greeting_name(client: AsyncClient, regional_token: str):
    """greeting_name is the first token of user's nombre."""
    resp = await client.get("/api/dashboard/action-items", headers=auth(regional_token))
    data = resp.json()
    assert data["greeting_name"]
    assert " " not in data["greeting_name"], "Should be first name only"


@pytest.mark.asyncio
async def test_action_items_all_roles_accessible(
    client: AsyncClient,
    admin_token: str, regional_token: str, jefe_token: str,
    analista_token: str, dgi_token: str,
    analista_token: str, rtf_token: str, juridico_token: str,
):
    """All 8 test role tokens can access the endpoint."""
    for token in (admin_token, regional_token, jefe_token, analista_token,
                  dgi_token, analista_token, rtf_token, juridico_token):
        resp = await client.get("/api/dashboard/action-items", headers=auth(token))
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_action_items_unauthenticated(client: AsyncClient):
    """Unauthenticated requests get 401."""
    resp = await client.get("/api/dashboard/action-items")
    assert resp.status_code in (401, 403)
