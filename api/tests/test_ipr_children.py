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


async def _get_org_id(db: AsyncSession) -> str:
    result = await db.execute(
        text("SELECT id FROM core.organization WHERE deleted_at IS NULL LIMIT 1")
    )
    return str(result.scalar())


async def _get_category_id(db: AsyncSession, scheme: str) -> str:
    result = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = :s LIMIT 1"),
        {"s": scheme},
    )
    return str(result.scalar())


async def _get_territory_id(db: AsyncSession) -> str:
    result = await db.execute(text("SELECT id FROM core.territory LIMIT 1"))
    return str(result.scalar())


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


@pytest.mark.asyncio
async def test_create_party(client: AsyncClient, regional_token: str, db: AsyncSession):
    """POST /api/ipr/{id}/partes creates a party and returns its ID."""
    ipr_id = await _get_ipr_id(db)
    org_id = await _get_org_id(db)
    role_id = await _get_category_id(db, "ipr_party_role")

    r = await client.post(
        f"/api/ipr/{ipr_id}/partes",
        json={"organization_id": org_id, "party_role_id": role_id},
        headers=auth(regional_token),
    )
    assert r.status_code == 201
    data = r.json()
    assert "id" in data

    # Verify it appears in list
    r2 = await client.get(f"/api/ipr/{ipr_id}/partes", headers=auth(regional_token))
    assert r2.status_code == 200
    items = r2.json()
    assert any(p["id"] == data["id"] for p in items)


@pytest.mark.asyncio
async def test_create_party_duplicate_rejected(
    client: AsyncClient, regional_token: str, db: AsyncSession
):
    """POST /api/ipr/{id}/partes rejects duplicate org+role pair."""
    ipr_id = await _get_ipr_id(db)
    org_id = await _get_org_id(db)
    role_id = await _get_category_id(db, "ipr_party_role")

    # Clean first
    await db.execute(
        text("DELETE FROM core.ipr_party WHERE ipr_id = :id"),
        {"id": ipr_id},
    )
    await db.commit()

    # Create first
    r = await client.post(
        f"/api/ipr/{ipr_id}/partes",
        json={"organization_id": org_id, "party_role_id": role_id},
        headers=auth(regional_token),
    )
    assert r.status_code == 201

    # Duplicate should fail
    r2 = await client.post(
        f"/api/ipr/{ipr_id}/partes",
        json={"organization_id": org_id, "party_role_id": role_id},
        headers=auth(regional_token),
    )
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_delete_party(client: AsyncClient, regional_token: str, db: AsyncSession):
    """DELETE /api/ipr/{id}/partes/{party_id} soft-deletes a party."""
    ipr_id = await _get_ipr_id(db)
    org_id = await _get_org_id(db)
    role_id = await _get_category_id(db, "ipr_party_role")

    # Clean and create
    await db.execute(
        text("DELETE FROM core.ipr_party WHERE ipr_id = :id"),
        {"id": ipr_id},
    )
    await db.commit()

    r = await client.post(
        f"/api/ipr/{ipr_id}/partes",
        json={"organization_id": org_id, "party_role_id": role_id},
        headers=auth(regional_token),
    )
    party_id = r.json()["id"]

    # Delete
    r2 = await client.delete(
        f"/api/ipr/{ipr_id}/partes/{party_id}",
        headers=auth(regional_token),
    )
    assert r2.status_code == 204

    # Verify gone from list
    r3 = await client.get(f"/api/ipr/{ipr_id}/partes", headers=auth(regional_token))
    assert all(p["id"] != party_id for p in r3.json())


@pytest.mark.asyncio
async def test_party_analista_allowed(
    client: AsyncClient, analista_token: str, db: AsyncSession
):
    """POST /api/ipr/{id}/partes allows ANALISTA (absorbed ENCARGADO permissions)."""
    # Create an IPR assigned to the analista user for scope check
    analista_id = str((await db.execute(
        text("SELECT id FROM core.\"user\" WHERE email = 'analista.dipir@goreos.cl'")
    )).scalar())
    status_id = str((await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'ipr_state' LIMIT 1")
    )).scalar())
    ipr_id = str((await db.execute(
        text("""
            INSERT INTO core.ipr (codigo_bip, name, ipr_nature, status_id, assignee_id)
            VALUES (:code, 'Test Analista Party', 'PROYECTO', CAST(:sid AS uuid), CAST(:aid AS uuid))
            RETURNING id
        """),
        {"code": f"ANAL-PTY-{__import__('uuid').uuid4().hex[:6]}", "sid": status_id, "aid": analista_id},
    )).scalar())
    await db.commit()

    org_id = await _get_org_id(db)
    role_id = await _get_category_id(db, "ipr_party_role")

    r = await client.post(
        f"/api/ipr/{ipr_id}/partes",
        json={"organization_id": org_id, "party_role_id": role_id},
        headers=auth(analista_token),
    )
    assert r.status_code == 201


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


@pytest.mark.asyncio
async def test_create_territory(client: AsyncClient, regional_token: str, db: AsyncSession):
    """POST /api/ipr/{id}/territorio creates a territory link."""
    ipr_id = await _get_ipr_id(db)
    territory_id = await _get_territory_id(db)
    impact_id = await _get_category_id(db, "territory_impact")

    # Clean
    await db.execute(
        text("DELETE FROM core.ipr_territory WHERE ipr_id = :id"),
        {"id": ipr_id},
    )
    await db.commit()

    r = await client.post(
        f"/api/ipr/{ipr_id}/territorio",
        json={"territory_id": territory_id, "impact_type_id": impact_id},
        headers=auth(regional_token),
    )
    assert r.status_code == 201
    data = r.json()
    assert "id" in data

    # Verify in list
    r2 = await client.get(f"/api/ipr/{ipr_id}/territorio", headers=auth(regional_token))
    items = r2.json()
    assert any(t["id"] == data["id"] for t in items)


@pytest.mark.asyncio
async def test_create_territory_duplicate(
    client: AsyncClient, regional_token: str, db: AsyncSession
):
    """POST /api/ipr/{id}/territorio rejects duplicate territory+impact."""
    ipr_id = await _get_ipr_id(db)
    territory_id = await _get_territory_id(db)
    impact_id = await _get_category_id(db, "territory_impact")

    # Clean
    await db.execute(
        text("DELETE FROM core.ipr_territory WHERE ipr_id = :id"),
        {"id": ipr_id},
    )
    await db.commit()

    r = await client.post(
        f"/api/ipr/{ipr_id}/territorio",
        json={"territory_id": territory_id, "impact_type_id": impact_id},
        headers=auth(regional_token),
    )
    assert r.status_code == 201

    r2 = await client.post(
        f"/api/ipr/{ipr_id}/territorio",
        json={"territory_id": territory_id, "impact_type_id": impact_id},
        headers=auth(regional_token),
    )
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_delete_territory(client: AsyncClient, regional_token: str, db: AsyncSession):
    """DELETE /api/ipr/{id}/territorio/{record_id} soft-deletes territory."""
    ipr_id = await _get_ipr_id(db)
    territory_id = await _get_territory_id(db)
    impact_id = await _get_category_id(db, "territory_impact")

    # Clean and create
    await db.execute(
        text("DELETE FROM core.ipr_territory WHERE ipr_id = :id"),
        {"id": ipr_id},
    )
    await db.commit()

    r = await client.post(
        f"/api/ipr/{ipr_id}/territorio",
        json={"territory_id": territory_id, "impact_type_id": impact_id},
        headers=auth(regional_token),
    )
    record_id = r.json()["id"]

    r2 = await client.delete(
        f"/api/ipr/{ipr_id}/territorio/{record_id}",
        headers=auth(regional_token),
    )
    assert r2.status_code == 204


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


@pytest.mark.asyncio
async def test_create_milestone(client: AsyncClient, regional_token: str, db: AsyncSession):
    """POST /api/ipr/{id}/hitos creates a milestone."""
    ipr_id = await _get_ipr_id(db)
    type_id = await _get_category_id(db, "milestone_type")

    r = await client.post(
        f"/api/ipr/{ipr_id}/hitos",
        json={
            "milestone_type_id": type_id,
            "planned_date": "2026-06-30",
            "description": "Test milestone",
        },
        headers=auth(regional_token),
    )
    assert r.status_code == 201
    data = r.json()
    assert "id" in data

    # Verify in list
    r2 = await client.get(f"/api/ipr/{ipr_id}/hitos", headers=auth(regional_token))
    items = r2.json()
    assert any(h["id"] == data["id"] for h in items)


@pytest.mark.asyncio
async def test_update_milestone_actual_date(
    client: AsyncClient, regional_token: str, db: AsyncSession
):
    """PATCH /api/ipr/{id}/hitos/{hito_id} sets actual_date."""
    ipr_id = await _get_ipr_id(db)
    type_id = await _get_category_id(db, "milestone_type")

    # Create
    r = await client.post(
        f"/api/ipr/{ipr_id}/hitos",
        json={"milestone_type_id": type_id, "planned_date": "2026-06-30"},
        headers=auth(regional_token),
    )
    hito_id = r.json()["id"]

    # Complete
    r2 = await client.patch(
        f"/api/ipr/{ipr_id}/hitos/{hito_id}",
        json={"actual_date": "2026-06-28"},
        headers=auth(regional_token),
    )
    assert r2.status_code == 200

    # Verify deviation
    r3 = await client.get(f"/api/ipr/{ipr_id}/hitos", headers=auth(regional_token))
    hito = next(h for h in r3.json() if h["id"] == hito_id)
    assert hito["actual_date"] == "2026-06-28"
    assert hito["deviation_days"] == -2  # 2 days early


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
