import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_readiness_endpoint(client: AsyncClient, admin_token: str):
    """GET /api/ipr/{id}/readiness returns satellite counts."""
    # Get any existing IPR
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await client.get("/api/ipr?page=1&page_size=1", headers=headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    if not items:
        pytest.skip("No IPRs in test DB")

    ipr_id = items[0]["id"]
    resp = await client.get(f"/api/ipr/{ipr_id}/readiness", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "satellites" in data
    assert "next_transitions" in data
    assert len(data["satellites"]) == 9
    # Each satellite has name, label, count
    for sat in data["satellites"]:
        assert "name" in sat
        assert "label" in sat
        assert "count" in sat
        assert isinstance(sat["count"], int)


async def test_readiness_404(client: AsyncClient, admin_token: str):
    """Nonexistent IPR returns 404."""
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await client.get(
        "/api/ipr/00000000-0000-0000-0000-000000000000/readiness",
        headers=headers,
    )
    assert resp.status_code == 404
