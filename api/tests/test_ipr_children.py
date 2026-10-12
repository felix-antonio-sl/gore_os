"""
Integration tests for IPR child entities: parties, territories, milestones.
Tests nested endpoints: GET/POST/DELETE /api/ipr/{id}/partes, territorio, hitos.
Also tests catalog endpoints: organizations, territories.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_ipr_id(db: AsyncSession) -> str:
    result = await db.execute(
        text("SELECT id FROM core.ipr WHERE deleted_at IS NULL LIMIT 1")
    )
    row = result.scalar()
    assert row, "No IPR found in goreos_test"
    return str(row)


# ---------------------------------------------------------------------------
# Partes Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_parties_empty(client: AsyncClient, regional_token: str, db: AsyncSession):
    """GET /api/ipr/{id}/partes returns empty list for IPR with no parties."""
    ipr_id = await _get_ipr_id(db)
    # Clean any existing parties for this IPR in test DB
    await db.execute(
        text("DELETE FROM core.ipr_party WHERE ipr_id = :id"),
        {"id": ipr_id},
    )
    await db.commit()

    r = await client.get(f"/api/ipr/{ipr_id}/partes", headers=auth(regional_token))
    assert r.status_code == 200
    assert r.json() == []


# ---------------------------------------------------------------------------
# Territorio Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_territories_empty(client: AsyncClient, regional_token: str, db: AsyncSession):
    """GET /api/ipr/{id}/territorio returns empty list when no territories."""
    ipr_id = await _get_ipr_id(db)
    await db.execute(
        text("DELETE FROM core.ipr_territory WHERE ipr_id = :id"),
        {"id": ipr_id},
    )
    await db.commit()

    r = await client.get(f"/api/ipr/{ipr_id}/territorio", headers=auth(regional_token))
    assert r.status_code == 200
    assert r.json() == []


# ---------------------------------------------------------------------------
# Hitos Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_milestones_empty(client: AsyncClient, regional_token: str, db: AsyncSession):
    """GET /api/ipr/{id}/hitos returns empty list."""
    ipr_id = await _get_ipr_id(db)
    r = await client.get(f"/api/ipr/{ipr_id}/hitos", headers=auth(regional_token))
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ---------------------------------------------------------------------------
# Catalog Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_catalogs_territories(client: AsyncClient, regional_token: str):
    """GET /api/catalogs/territories returns territory list."""
    r = await client.get("/api/catalogs/territories", headers=auth(regional_token))
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 25  # 1 region + 3 provinces + 21 comunas
    assert "territory_type" in data[0]


@pytest.mark.asyncio
async def test_catalogs_organizations_search(client: AsyncClient, regional_token: str):
    """GET /api/catalogs/organizations?search=X returns filtered orgs."""
    r = await client.get(
        "/api/catalogs/organizations?search=GORE",
        headers=auth(regional_token),
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert "org_type" in data[0]
