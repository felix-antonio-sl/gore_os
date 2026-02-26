"""Tests for problem state transitions and PATCH behavior."""
import uuid
from sqlalchemy import text as sql_text
from tests.conftest import auth


async def _create_ipr_for_test(db) -> str:
    """Create a minimal IPR in test DB for problem association."""
    result = await db.execute(
        sql_text("""
            INSERT INTO core.ipr (codigo_bip, name, ipr_type_id, ipr_nature)
            VALUES (
                :bip, :name,
                (SELECT id FROM ref.category WHERE scheme = 'ipr_type' LIMIT 1),
                'PROYECTO'
            )
            RETURNING id
        """),
        {"bip": f"TEST-{uuid.uuid4().hex[:8]}", "name": f"Test IPR {uuid.uuid4().hex[:8]}"},
    )
    await db.commit()
    return str(result.scalar())


async def _create_problem(client, token, catalog, db, **overrides):
    ipr_id = await _create_ipr_for_test(db)
    payload = {
        "ipr_id": ipr_id,
        "problem_type_id": catalog["problem_type_id"],
        "description": f"Test problem {uuid.uuid4().hex[:8]}",
        **overrides,
    }
    resp = await client.post("/api/problemas", json=payload, headers=auth(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_create_problem(client, regional_token, catalog, db):
    """Create problem with auto-generated code and state ABIERTO."""
    data = await _create_problem(client, regional_token, catalog, db)
    assert data["code"].startswith("PR-")

    detail = await client.get(f"/api/problemas/{data['id']}", headers=auth(regional_token))
    assert detail.json()["state"] == "ABIERTO"


async def test_patch_to_en_gestion(client, regional_token, catalog, db):
    """Patch state_id to EN_GESTION."""
    data = await _create_problem(client, regional_token, catalog, db)

    result = await db.execute(
        sql_text("SELECT id FROM ref.category WHERE scheme = 'problem_state' AND code = 'EN_GESTION'")
    )
    en_gestion_id = str(result.scalar())

    resp = await client.patch(
        f"/api/problemas/{data['id']}",
        json={"state_id": en_gestion_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    assert resp.json()["state"] == "EN_GESTION"


async def test_resolve_sets_metadata(client, regional_token, catalog, db):
    """Patching to RESUELTO auto-sets resolved_by_id and resolved_at."""
    data = await _create_problem(client, regional_token, catalog, db)

    result = await db.execute(
        sql_text("SELECT id FROM ref.category WHERE scheme = 'problem_state' AND code = 'RESUELTO'")
    )
    resuelto_id = str(result.scalar())

    resp = await client.patch(
        f"/api/problemas/{data['id']}",
        json={"state_id": resuelto_id, "solution_applied": "Fixed it"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["state"] == "RESUELTO"
    assert body["resolved_by_name"] is not None
    assert body["resolved_at"] is not None


async def test_patch_invalid_state_id(client, regional_token, catalog, db):
    """Invalid state_id returns 422."""
    data = await _create_problem(client, regional_token, catalog, db)

    resp = await client.patch(
        f"/api/problemas/{data['id']}",
        json={"state_id": "00000000-0000-0000-0000-000000000000"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 422


async def test_patch_solution_only(client, regional_token, catalog, db):
    """Patching only proposed_solution doesn't change state."""
    data = await _create_problem(client, regional_token, catalog, db)

    resp = await client.patch(
        f"/api/problemas/{data['id']}",
        json={"proposed_solution": "Try rebooting"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    assert resp.json()["state"] == "ABIERTO"


async def test_days_open_calculation(client, regional_token, catalog, db):
    """Problem created today has days_open = 0."""
    data = await _create_problem(client, regional_token, catalog, db)

    detail = await client.get(f"/api/problemas/{data['id']}", headers=auth(regional_token))
    assert detail.json()["days_open"] == 0


async def test_search_filter(client, regional_token, catalog, db):
    """Search by description fragment returns matching results."""
    marker = f"UNIQUE-{uuid.uuid4().hex[:8]}"
    await _create_problem(
        client, regional_token, catalog, db,
        description=f"Problem with {marker} issue",
    )

    resp = await client.get(
        f"/api/problemas?search={marker}",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 1
    assert marker in items[0]["description"]


async def test_list_returns_paginated(client, regional_token):
    """Problem list returns paginated response format."""
    resp = await client.get("/api/problemas", headers=auth(regional_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "total_pages" in body
