"""Tests for catalog endpoints (/api/catalogs/*)."""
from tests.conftest import auth


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------


async def test_get_categories_ipr_type(client, regional_token):
    """GET /api/catalogs/categories/ipr_type returns all 8 IPR types."""
    resp = await client.get(
        "/api/catalogs/categories/ipr_type",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 8
    codes = {it["code"] for it in items}
    assert "INFRAESTRUCTURA" in codes
    assert "EQUIPAMIENTO" in codes
    for it in items:
        assert "id" in it
        assert "code" in it
        assert "label" in it


async def test_get_categories_agreement_type(client, regional_token):
    """GET /api/catalogs/categories/agreement_type returns items with id, code, label."""
    resp = await client.get(
        "/api/catalogs/categories/agreement_type",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0
    for it in items:
        assert "id" in it
        assert "code" in it
        assert "label" in it


async def test_get_categories_empty_scheme(client, regional_token):
    """GET /api/catalogs/categories/nonexistent_scheme returns empty list."""
    resp = await client.get(
        "/api/catalogs/categories/nonexistent_scheme",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------------------
# Commitment types
# ---------------------------------------------------------------------------


async def test_get_commitment_types(client, regional_token):
    """GET /api/catalogs/commitment-types returns non-empty list with expected fields."""
    resp = await client.get(
        "/api/catalogs/commitment-types",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0
    for it in items:
        assert "code" in it
        assert "name" in it
        assert "id" in it


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


async def test_get_users_list(client, regional_token):
    """GET /api/catalogs/users returns at least the 5 seeded test users."""
    resp = await client.get(
        "/api/catalogs/users",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 5
    for it in items:
        assert "id" in it
        assert "email" in it
        assert "role_code" in it


async def test_get_users_search(client, regional_token):
    """GET /api/catalogs/users?search=admin filters by email substring."""
    resp = await client.get(
        "/api/catalogs/users?search=admin",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    emails = {it["email"] for it in items}
    assert "admin@goreos.cl" in emails


# ---------------------------------------------------------------------------
# Territories
# ---------------------------------------------------------------------------


async def test_get_territories(client, regional_token):
    """GET /api/catalogs/territories returns all 25 territories (1 REGION + 3 PROVINCIA + 21 COMUNA)."""
    resp = await client.get(
        "/api/catalogs/territories",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 25
    for it in items:
        assert "id" in it
        assert "code" in it
        assert "name" in it
        assert "territory_type" in it
    types = {it["territory_type"] for it in items}
    assert "REGION" in types
    assert "COMUNA" in types


# ---------------------------------------------------------------------------
# Divisions
# ---------------------------------------------------------------------------


async def test_get_divisions(client, regional_token):
    """GET /api/catalogs/divisions returns non-empty list including GORE-NUBLE."""
    resp = await client.get(
        "/api/catalogs/divisions",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0
    codes = {it["code"] for it in items}
    assert "GORE-NUBLE" in codes
    for it in items:
        assert "id" in it
        assert "code" in it
        assert "name" in it
