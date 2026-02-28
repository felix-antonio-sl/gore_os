"""Tests for the global search endpoint."""
from tests.conftest import auth

VALID_ENTITY_TYPES = {"ipr", "compromiso", "problema", "persona"}


async def test_search_returns_results(client, regional_token):
    """Search for 'Test' returns results (test DB has IPRs named 'Test IPR...')."""
    resp = await client.get(
        "/api/search?q=Test",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "results" in body
    assert isinstance(body["results"], list)
    assert len(body["results"]) > 0


async def test_search_min_length(client, regional_token):
    """Query shorter than 2 characters returns 422 validation error."""
    resp = await client.get(
        "/api/search?q=x",
        headers=auth(regional_token),
    )
    assert resp.status_code == 422


async def test_search_no_auth(client):
    """Search without auth token returns 401."""
    resp = await client.get("/api/search?q=test")
    assert resp.status_code == 401


async def test_search_response_shape(client, regional_token):
    """Each search result has the expected keys and valid entity_type."""
    resp = await client.get(
        "/api/search?q=IPR",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    for item in results:
        assert "id" in item
        assert "code" in item  # nullable, but key must exist
        assert "name" in item
        assert "entity_type" in item
        assert item["entity_type"] in VALID_ENTITY_TYPES
