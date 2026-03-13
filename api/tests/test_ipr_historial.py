import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_historial_endpoint(client: AsyncClient, admin_token: str):
    """GET /api/ipr/{id}/historial returns history entries."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Get any existing IPR
    resp = await client.get("/api/ipr?page=1&page_size=1", headers=headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    if not items:
        pytest.skip("No IPRs in test DB")

    ipr_id = items[0]["id"]
    resp = await client.get(f"/api/ipr/{ipr_id}/historial", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Each entry should have the right shape
    for entry in data:
        assert "id" in entry
        assert "new_state" in entry
        assert "changed_at" in entry


async def test_historial_404(client: AsyncClient, admin_token: str):
    """Nonexistent IPR returns 404."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await client.get(
        "/api/ipr/00000000-0000-0000-0000-000000000000/historial",
        headers=headers,
    )
    assert resp.status_code == 404
