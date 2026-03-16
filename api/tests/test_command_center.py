"""
Wave E: Command Center tests (E-2).

Tests: summary returns all sections, timeline pagination,
role permissions, empty state.
"""
import pytest
from httpx import AsyncClient

from tests.conftest import auth


@pytest.mark.asyncio
async def test_summary_returns_all_sections(client: AsyncClient, dgi_token: str):
    resp = await client.get("/api/command-center/summary", headers=auth(dgi_token))
    assert resp.status_code == 200
    data = resp.json()
    for key in ("escalations", "alerts", "risks", "decisions", "meetings", "sla_breaches"):
        assert key in data, f"Missing key: {key}"


@pytest.mark.asyncio
async def test_summary_escalations_structure(client: AsyncClient, dgi_token: str):
    resp = await client.get("/api/command-center/summary", headers=auth(dgi_token))
    data = resp.json()
    esc = data["escalations"]
    assert "active" in esc
    assert "by_level" in esc
    assert "top" in esc
    assert isinstance(esc["active"], int)


@pytest.mark.asyncio
async def test_timeline_pagination(client: AsyncClient, dgi_token: str):
    resp = await client.get(
        "/api/command-center/timeline?days=30&page=1&page_size=5",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert data["page"] == 1
    assert data["page_size"] == 5


@pytest.mark.asyncio
async def test_timeline_category_filter(client: AsyncClient, dgi_token: str):
    resp = await client.get(
        "/api/command-center/timeline?category=RISK",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    for item in data["items"]:
        assert item["category"] == "RISK"


@pytest.mark.asyncio
async def test_role_dgi_can_access(client: AsyncClient, dgi_token: str):
    resp = await client.get("/api/command-center/summary", headers=auth(dgi_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_role_admin_can_access(client: AsyncClient, admin_token: str):
    resp = await client.get("/api/command-center/summary", headers=auth(admin_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_role_regional_can_access(client: AsyncClient, regional_token: str):
    resp = await client.get("/api/command-center/summary", headers=auth(regional_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_role_encargado_denied(client: AsyncClient, analista_token: str):
    resp = await client.get("/api/command-center/summary", headers=auth(analista_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_empty_state(client: AsyncClient, dgi_token: str):
    """Even with no data, summary should return valid structure."""
    resp = await client.get("/api/command-center/summary", headers=auth(dgi_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["escalations"]["active"] >= 0
    assert data["risks"]["high_count"] >= 0
