import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_cartera_por_division(client: AsyncClient, admin_token: str):
    """GET /api/ipr/cartera-por-division returns division summaries."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await client.get("/api/ipr/cartera-por-division", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if len(data) > 0:
        item = data[0]
        assert "division_id" in item
        assert "division_name" in item
        assert "total_iprs" in item
        assert "by_phase" in item
        assert "health_signal" in item
        assert item["health_signal"] in ("VERDE", "AMARILLO", "ROJO")


async def test_cartera_por_division_requires_admin(client: AsyncClient, encargado_token: str):
    """Non-admin roles cannot access cartera."""
    headers = {"Authorization": f"Bearer {encargado_token}"}
    resp = await client.get("/api/ipr/cartera-por-division", headers=headers)
    assert resp.status_code == 403
