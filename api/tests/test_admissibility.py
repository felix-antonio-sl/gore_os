"""Tests for admissibility sub-states (PRE_ADMISIBLE checklist)."""
import uuid
from httpx import AsyncClient
from tests.conftest import auth


async def _get_track_id(client, token):
    resp = await client.get("/api/admin/financing-tracks", headers=auth(token))
    assert resp.status_code == 200
    data = resp.json()
    items = data["items"] if isinstance(data, dict) and "items" in data else data
    assert len(items) > 0, "Need at least one financing track"
    return items[0]["id"]


async def _create_item(client, admin_token, track_id, code, role="JEFE_DIVISION"):
    resp = await client.post(
        "/api/admin/admissibility-items",
        json={
            "financing_track_id": track_id,
            "code": code,
            "label": f"Test item {code}",
            "responsible_role": role,
            "is_required": True,
        },
        headers=auth(admin_token),
    )
    assert resp.status_code in (201, 409), resp.text
    if resp.status_code == 201:
        return resp.json()["id"]
    items_resp = await client.get(
        f"/api/admin/admissibility-items?track_id={track_id}",
        headers=auth(admin_token),
    )
    return next(i["id"] for i in items_resp.json() if i["code"] == code)


async def _create_ipr_pre_admisible(db, track_id):
    """Create a PRE_ADMISIBLE IPR linked to the given financing track.

    The track_id is from core.financing_track; we look up the matching
    ref.category(scheme='mechanism') to set core.ipr.mechanism_id.
    """
    from sqlalchemy import text as sa_text
    status_id = str((await db.execute(sa_text(
        "SELECT id FROM ref.category WHERE scheme='ipr_state' AND code='PRE_ADMISIBLE'"
    ))).scalar())
    # Get the mechanism category that matches this financing track's code
    mechanism_id = str((await db.execute(sa_text("""
        SELECT c.id FROM ref.category c
        JOIN core.financing_track ft ON ft.code = c.code
        WHERE c.scheme = 'mechanism' AND ft.id = CAST(:track_id AS uuid)
    """), {"track_id": track_id})).scalar())
    code = f"ADM-{uuid.uuid4().hex[:6]}"
    ipr_id = str((await db.execute(sa_text("""
        INSERT INTO core.ipr (codigo_bip, name, ipr_nature, status_id, mechanism_id)
        VALUES (:code, 'Test Admissibility', 'PROYECTO', :status_id, CAST(:mechanism_id AS uuid))
        RETURNING id
    """), {"code": code, "status_id": status_id, "mechanism_id": mechanism_id})).scalar())
    await db.commit()
    return ipr_id


# ── Admin CRUD ──

async def test_admin_create_admissibility_item(client: AsyncClient, admin_token: str):
    track_id = await _get_track_id(client, admin_token)
    resp = await client.post(
        "/api/admin/admissibility-items",
        json={
            "financing_track_id": track_id,
            "code": f"TEST-CREATE-{uuid.uuid4().hex[:4]}",
            "label": "Documentación legal completa",
            "responsible_role": "JEFE_DIVISION",
            "sort_order": 1,
            "is_required": True,
        },
        headers=auth(admin_token),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["responsible_role"] == "JEFE_DIVISION"


async def test_admin_list_admissibility_items(client: AsyncClient, admin_token: str):
    track_id = await _get_track_id(client, admin_token)
    code = f"TEST-LIST-{uuid.uuid4().hex[:4]}"
    await client.post(
        "/api/admin/admissibility-items",
        json={"financing_track_id": track_id, "code": code, "label": "List test", "responsible_role": "ADMIN_REGIONAL"},
        headers=auth(admin_token),
    )
    resp = await client.get(f"/api/admin/admissibility-items?track_id={track_id}", headers=auth(admin_token))
    assert resp.status_code == 200
    assert any(i["code"] == code for i in resp.json())


async def test_admin_update_admissibility_item(client: AsyncClient, admin_token: str):
    track_id = await _get_track_id(client, admin_token)
    code = f"TEST-UPD-{uuid.uuid4().hex[:4]}"
    create = await client.post(
        "/api/admin/admissibility-items",
        json={"financing_track_id": track_id, "code": code, "label": "Original", "responsible_role": "JEFE_DIVISION"},
        headers=auth(admin_token),
    )
    item_id = create.json()["id"]
    resp = await client.patch(
        f"/api/admin/admissibility-items/{item_id}",
        json={"label": "Updated", "is_required": False},
        headers=auth(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["label"] == "Updated"


# ── Checklist endpoints ──

async def test_get_checklist(client: AsyncClient, admin_token: str, jefe_token: str, db):
    track_id = await _get_track_id(client, admin_token)
    await _create_item(client, admin_token, track_id, f"TEST-CHK-{uuid.uuid4().hex[:4]}")
    ipr_id = await _create_ipr_pre_admisible(db, track_id)
    resp = await client.get(f"/api/ipr/{ipr_id}/admisibilidad", headers=auth(jefe_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_items"] >= 1
    assert "items" in data


async def test_verify_item_correct_role(client: AsyncClient, admin_token: str, jefe_token: str, db):
    track_id = await _get_track_id(client, admin_token)
    item_id = await _create_item(client, admin_token, track_id, f"TEST-VER-{uuid.uuid4().hex[:4]}", "JEFE_DIVISION")
    ipr_id = await _create_ipr_pre_admisible(db, track_id)
    resp = await client.post(
        f"/api/ipr/{ipr_id}/admisibilidad/{item_id}/verificar",
        json={"notes": "OK"},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 200, resp.text


async def test_verify_item_wrong_role(client: AsyncClient, admin_token: str, encargado_token: str, db):
    track_id = await _get_track_id(client, admin_token)
    item_id = await _create_item(client, admin_token, track_id, f"TEST-ROLE-{uuid.uuid4().hex[:4]}", "JEFE_DIVISION")
    ipr_id = await _create_ipr_pre_admisible(db, track_id)
    resp = await client.post(
        f"/api/ipr/{ipr_id}/admisibilidad/{item_id}/verificar",
        json={},
        headers=auth(encargado_token),
    )
    assert resp.status_code == 403


async def test_unverify_item(client: AsyncClient, admin_token: str, jefe_token: str, db):
    track_id = await _get_track_id(client, admin_token)
    item_id = await _create_item(client, admin_token, track_id, f"TEST-UNVER-{uuid.uuid4().hex[:4]}", "JEFE_DIVISION")
    ipr_id = await _create_ipr_pre_admisible(db, track_id)
    await client.post(f"/api/ipr/{ipr_id}/admisibilidad/{item_id}/verificar", json={}, headers=auth(jefe_token))
    resp = await client.delete(f"/api/ipr/{ipr_id}/admisibilidad/{item_id}/verificar", headers=auth(jefe_token))
    assert resp.status_code == 200
