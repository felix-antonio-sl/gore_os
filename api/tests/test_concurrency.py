"""Tests for code generator uniqueness and advisory lock presence.

True concurrency tests require separate DB connections, which our shared-session
test fixture doesn't support. These tests verify:
1. Sequential code generators produce unique results
2. Advisory locks are present in the codebase (structural verification)
"""


async def test_sequential_compromiso_codes_unique(client, regional_token, catalog):
    """Two sequential commitment creations produce distinct codes."""
    from tests.conftest import auth

    ipr_row = await client.get(
        "/api/ipr?page=1&page_size=1",
        headers=auth(regional_token),
    )
    items = ipr_row.json().get("items", [])
    if not items:
        return  # skip if no IPRs
    ipr_id = str(items[0]["id"])

    payload = {
        "description": "Sequential test commitment",
        "due_date": "2026-06-01",
        "commitment_type_id": catalog["commitment_type_id"],
        "ipr_id": ipr_id,
        "responsible_id": catalog["users"]["encargado.daf@goreos.cl"]["id"],
    }

    r1 = await client.post("/api/compromisos", json=payload, headers=auth(regional_token))
    r2 = await client.post("/api/compromisos", json=payload, headers=auth(regional_token))

    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["code"] != r2.json()["code"], "Codes must be unique"


async def test_sequential_agreement_numbers_unique(client, regional_token, catalog):
    """Two sequential agreement creations produce distinct agreement numbers."""
    from tests.conftest import auth

    payload = {
        "agreement_type_id": catalog["agreement_type_id"],
        "state_id": catalog["agreement_state_borrador_id"],
        "counterpart": "Test Org Sequential",
        "subject": "Sequential test agreement",
    }

    r1 = await client.post("/api/convenios", json=payload, headers=auth(regional_token))
    r2 = await client.post("/api/convenios", json=payload, headers=auth(regional_token))

    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["agreement_number"] != r2.json()["agreement_number"]


async def test_sequential_act_numbers_unique(client, regional_token, db):
    """Two sequential act creations produce distinct act numbers."""
    from tests.conftest import auth
    from sqlalchemy import text

    act_type = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'act_type' AND code = 'DECRETO' LIMIT 1"),
    )
    act_type_id = str(act_type.scalar())

    payload = {
        "act_type_id": act_type_id,
        "subject": "Sequential test act",
        "issued_at": "2026-03-01T00:00:00",
        "requires_cgr": False,
    }

    r1 = await client.post("/api/actos", json=payload, headers=auth(regional_token))
    r2 = await client.post("/api/actos", json=payload, headers=auth(regional_token))

    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["act_number"] != r2.json()["act_number"]


async def test_advisory_locks_present_in_code_generators(db):
    """Verify that advisory locks are used in all code generators (structural test)."""
    import inspect
    from app.routers import compromisos, convenios, actos, dgi_initiatives

    # Check that advisory lock pattern exists in each module
    modules_with_locks = {
        "compromisos._next_oc_code": inspect.getsource(compromisos._next_oc_code),
        "convenios._next_agreement_number": inspect.getsource(convenios._next_agreement_number),
        "actos._next_act_number": inspect.getsource(actos._next_act_number),
    }

    for name, source in modules_with_locks.items():
        assert "pg_advisory_xact_lock" in source, (
            f"{name} must use pg_advisory_xact_lock for concurrency safety"
        )


async def test_wip_advisory_lock_present():
    """Verify that WIP limit check uses advisory lock (structural test)."""
    import inspect
    from app.routers import dgi_initiatives

    source = inspect.getsource(dgi_initiatives.move_initiative)
    assert "pg_advisory_xact_lock" in source, (
        "move_initiative must use pg_advisory_xact_lock for WIP limit checks"
    )
