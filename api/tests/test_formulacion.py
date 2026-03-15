"""Tests for GET /api/ipr/mis-formulaciones endpoint."""
from httpx import AsyncClient


async def test_mis_formulaciones_endpoint(client: AsyncClient, analista_token: str):
    """ANALISTA can fetch their IPRs in formulation phases."""
    resp = await client.get(
        "/api/ipr/mis-formulaciones",
        headers={"Authorization": f"Bearer {analista_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "by_phase" in data
    assert "F0" in data["by_phase"]
    assert "F1" in data["by_phase"]
    assert "F2" in data["by_phase"]


async def test_mis_formulaciones_has_suggested_action(client: AsyncClient, analista_token: str):
    """Each IPR in response must have suggested_action and suggested_tab."""
    resp = await client.get(
        "/api/ipr/mis-formulaciones",
        headers={"Authorization": f"Bearer {analista_token}"},
    )
    data = resp.json()
    for phase_items in data["by_phase"].values():
        for item in phase_items:
            assert "suggested_action" in item
            assert "suggested_tab" in item
            assert item["suggested_action"]
