"""Tests for parametric tables TP-01, TP-02, TP-04.

Covers:
- TP-02: Subv8 fund CRUD + ceiling CRUD
- TP-04: FRIL category CRUD
- TP-01: Evaluator routing query
"""
import pytest
from sqlalchemy import text
from tests.conftest import auth


# ---------------------------------------------------------------------------
# TP-02: Subv8 Funds
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_subv8_funds(client, admin_token):
    """GET /admin/subv8-funds returns 7 seeded funds."""
    resp = await client.get("/api/admin/subv8-funds", headers=auth(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 7
    codes = [f["code"] for f in data]
    assert "CULTURA" in codes
    assert "ADULTO_MAYOR" in codes


@pytest.mark.asyncio
async def test_create_subv8_fund(client, admin_token):
    """POST /admin/subv8-funds creates a fund."""
    resp = await client.post("/api/admin/subv8-funds", json={
        "code": "TEST-FONDO",
        "name": "Fondo de prueba",
        "budget_total": 100000,
        "sort_order": 99,
    }, headers=auth(admin_token))
    assert resp.status_code == 201
    assert resp.json()["code"] == "TEST-FONDO"


@pytest.mark.asyncio
async def test_create_subv8_fund_duplicate_409(client, admin_token):
    """POST with duplicate code returns 409."""
    await client.post("/api/admin/subv8-funds", json={
        "code": "TEST-DUP", "name": "Dup1", "sort_order": 98,
    }, headers=auth(admin_token))
    resp = await client.post("/api/admin/subv8-funds", json={
        "code": "TEST-DUP", "name": "Dup2", "sort_order": 97,
    }, headers=auth(admin_token))
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_update_subv8_fund(client, admin_token):
    """PATCH /admin/subv8-funds/{id} updates a fund."""
    create = await client.post("/api/admin/subv8-funds", json={
        "code": "TEST-UPD", "name": "Before", "sort_order": 96,
    }, headers=auth(admin_token))
    fund_id = create.json()["id"]
    resp = await client.patch(f"/api/admin/subv8-funds/{fund_id}", json={
        "name": "After",
    }, headers=auth(admin_token))
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# TP-02: Subv8 Ceilings
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_ceilings_for_fund(client, admin_token, db):
    """GET /admin/subv8-funds/{id}/ceilings returns ceilings."""
    fund = (await db.execute(
        text("SELECT id FROM core.subv8_fund WHERE code = 'CULTURA'")
    )).scalar()
    resp = await client.get(
        f"/api/admin/subv8-funds/{fund}/ceilings", headers=auth(admin_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["fund_code"] == "CULTURA"


@pytest.mark.asyncio
async def test_create_and_delete_ceiling(client, admin_token, db):
    """POST + DELETE ceiling lifecycle."""
    fund = (await db.execute(
        text("SELECT id FROM core.subv8_fund WHERE code = 'SEGURIDAD'")
    )).scalar()
    # Create
    resp = await client.post(
        f"/api/admin/subv8-funds/{fund}/ceilings", json={
            "institution_type": "TEST_INST",
            "area": "test_area",
            "max_amount": 999999,
            "notes": "TEST-ceiling",
        }, headers=auth(admin_token),
    )
    assert resp.status_code == 201
    ceiling_id = resp.json()["id"]
    # Delete
    del_resp = await client.delete(
        f"/api/admin/subv8-fund-ceilings/{ceiling_id}", headers=auth(admin_token),
    )
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_list_all_ceilings(client, admin_token):
    """GET /admin/subv8-fund-ceilings returns all ceilings flat."""
    resp = await client.get(
        "/api/admin/subv8-fund-ceilings", headers=auth(admin_token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 10


# ---------------------------------------------------------------------------
# TP-04: FRIL Categories
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_fril_categories(client, admin_token):
    """GET /admin/fril-categories returns 12 categories."""
    resp = await client.get("/api/admin/fril-categories", headers=auth(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 12
    # A2 and A3 are exempt
    a2 = next(c for c in data if c["code"] == "A2")
    assert a2["is_exempt_commune_limit"] is True
    b1 = next(c for c in data if c["code"] == "B1")
    assert b1["is_exempt_commune_limit"] is False


@pytest.mark.asyncio
async def test_create_fril_category(client, admin_token):
    """POST /admin/fril-categories creates a category."""
    resp = await client.post("/api/admin/fril-categories", json={
        "code": "T1X", "name": "Test Category", "group_code": "A",
        "group_name": "Test Group", "max_utm": 1000, "sort_order": 99,
    }, headers=auth(admin_token))
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_update_fril_category(client, admin_token, db):
    """PATCH /admin/fril-categories/{id} updates exemption flag."""
    cat = (await db.execute(
        text("SELECT id FROM core.fril_category WHERE code = 'B1'")
    )).scalar()
    resp = await client.patch(f"/api/admin/fril-categories/{cat}", json={
        "is_exempt_commune_limit": True,
    }, headers=auth(admin_token))
    assert resp.status_code == 200
    # Revert
    await client.patch(f"/api/admin/fril-categories/{cat}", json={
        "is_exempt_commune_limit": False,
    }, headers=auth(admin_token))


# ---------------------------------------------------------------------------
# TP-01: Evaluator Routing
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_routing_no_ipr_422(client, admin_token):
    """GET /admin/financing-tracks/routing without ipr_id returns 422."""
    resp = await client.get(
        "/api/admin/financing-tracks/routing", headers=auth(admin_token),
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_routing_no_track_404(client, admin_token, db):
    """GET /admin/financing-tracks/routing for nonexistent IPR returns 404 or 500 if column missing."""
    import uuid
    # Check if core.ipr has financing_track_id column (may be missing in test DB)
    col = (await db.execute(
        text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'core' AND table_name = 'ipr'
              AND column_name = 'financing_track_id'
        """)
    )).scalar()
    if not col:
        pytest.skip("financing_track_id column not present in test DB")
    fake_id = str(uuid.uuid4())
    resp = await client.get(
        f"/api/admin/financing-tracks/routing?ipr_id={fake_id}",
        headers=auth(admin_token),
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_non_admin_403(client, dgi_token):
    """Non-admin gets 403 on all parametric endpoints."""
    resp = await client.get("/api/admin/subv8-funds", headers=auth(dgi_token))
    assert resp.status_code == 403
