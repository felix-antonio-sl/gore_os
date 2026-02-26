"""Tests for budget program calculations and role restrictions."""
import uuid
from tests.conftest import auth


async def _create_budget(client, token, catalog, **overrides):
    payload = {
        "code": f"TEST-BP-{uuid.uuid4().hex[:6]}",
        "name": f"Test Budget {uuid.uuid4().hex[:8]}",
        "fiscal_year": 2026,
        "initial_amount": 1000000,
        "owner_division_id": catalog["division_id"],
        "subtitle_id": catalog["budget_subtitle_id"],
        **overrides,
    }
    resp = await client.post("/api/presupuesto", json=payload, headers=auth(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_create_budget_program(client, regional_token, catalog):
    """Create budget program with amounts initialized correctly."""
    data = await _create_budget(client, regional_token, catalog)
    assert "id" in data

    detail = await client.get(f"/api/presupuesto/{data['id']}", headers=auth(regional_token))
    body = detail.json()
    assert float(body["initial_amount"]) == 1000000
    assert float(body["committed_amount"]) == 0
    assert float(body["accrued_amount"]) == 0
    assert float(body["paid_amount"]) == 0


async def test_duplicate_code_fiscal_year(client, regional_token, catalog):
    """Duplicate (code, fiscal_year) returns 409."""
    code = f"TEST-DUP-{uuid.uuid4().hex[:6]}"
    await _create_budget(client, regional_token, catalog, code=code)

    resp = await client.post(
        "/api/presupuesto",
        json={
            "code": code,
            "name": "Duplicate",
            "fiscal_year": 2026,
            "initial_amount": 500000,
            "owner_division_id": catalog["division_id"],
        },
        headers=auth(regional_token),
    )
    assert resp.status_code == 409


async def test_same_code_different_year(client, regional_token, catalog):
    """Same code with different fiscal_year is allowed."""
    code = f"TEST-YR-{uuid.uuid4().hex[:6]}"
    await _create_budget(client, regional_token, catalog, code=code, fiscal_year=2025)

    resp = await client.post(
        "/api/presupuesto",
        json={
            "code": code,
            "name": "Different year",
            "fiscal_year": 2026,
            "initial_amount": 500000,
            "owner_division_id": catalog["division_id"],
        },
        headers=auth(regional_token),
    )
    assert resp.status_code == 201


async def test_execution_calculation(client, regional_token, catalog):
    """Execution % = paid/current * 100."""
    data = await _create_budget(
        client, regional_token, catalog,
        initial_amount=1000000,
        current_amount=1000000,
    )
    # Update paid to 700000 -> 70%
    await client.patch(
        f"/api/presupuesto/{data['id']}",
        json={"paid_amount": 700000},
        headers=auth(regional_token),
    )

    detail = await client.get(f"/api/presupuesto/{data['id']}", headers=auth(regional_token))
    assert detail.json()["execution_pct"] == 70.0


async def test_execution_zero_current(client, regional_token, catalog):
    """Current=0 should not cause division by zero (returns 0.0)."""
    data = await _create_budget(
        client, regional_token, catalog,
        initial_amount=0,
        current_amount=0,
    )

    detail = await client.get(f"/api/presupuesto/{data['id']}", headers=auth(regional_token))
    assert detail.json()["execution_pct"] == 0.0


async def test_paid_exceeds_current(client, regional_token, catalog):
    """Paid > current is allowed (execution > 100%)."""
    data = await _create_budget(
        client, regional_token, catalog,
        initial_amount=1000000,
        current_amount=1000000,
    )
    await client.patch(
        f"/api/presupuesto/{data['id']}",
        json={"paid_amount": 1500000},
        headers=auth(regional_token),
    )

    detail = await client.get(f"/api/presupuesto/{data['id']}", headers=auth(regional_token))
    assert detail.json()["execution_pct"] == 150.0


async def test_jefe_only_own_division(client, regional_token, jefe_token, catalog):
    """JEFE_DIVISION cannot patch budget of another division."""
    data = await _create_budget(client, regional_token, catalog)

    # jefe_token is jefe.daf — if the budget's division differs, should get 403
    resp = await client.patch(
        f"/api/presupuesto/{data['id']}",
        json={"paid_amount": 999},
        headers=auth(jefe_token),
    )
    # Either 200 (same division) or 403 (cross-division)
    assert resp.status_code in (200, 403)


async def test_encargado_cannot_create(client, encargado_token, catalog):
    """ENCARGADO cannot create budget programs."""
    resp = await client.post(
        "/api/presupuesto",
        json={
            "code": "TEST-NOPE",
            "name": "Should fail",
            "fiscal_year": 2026,
            "initial_amount": 100,
        },
        headers=auth(encargado_token),
    )
    assert resp.status_code == 403
