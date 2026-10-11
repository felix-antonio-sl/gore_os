"""The work inbox resolves assignment, authority and state against real PostgreSQL."""
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import text

from tests.conftest import auth

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
async def cleanup_inbox_data(db):
    yield
    await db.execute(text("""
        DELETE FROM core.commitment_history WHERE commitment_id IN (
            SELECT id FROM core.operational_commitment WHERE description LIKE 'INBOX-TEST-%'
        )
    """))
    await db.execute(text(
        "DELETE FROM core.operational_commitment WHERE description LIKE 'INBOX-TEST-%'"
    ))
    await db.execute(text("DELETE FROM core.ipr WHERE codigo_bip LIKE 'INBOX-%'"))
    await db.commit()


async def create_commitment(client, token, catalog, **overrides):
    response = await client.post("/api/compromisos", headers=auth(token), json={
        "description": f"INBOX-TEST-{uuid.uuid4().hex[:8]}",
        "commitment_type_id": catalog["commitment_type_id"],
        "responsible_id": catalog["users"]["analista.dipir@goreos.cl"]["id"],
        "due_date": str(date.today() + timedelta(days=10)),
        **overrides,
    })
    assert response.status_code == 201, response.text
    return response.json()


async def test_personal_filter_cannot_request_another_responsible(
    client, regional_token, analista_token, catalog,
):
    other = catalog["users"]["rtf.daf@goreos.cl"]["id"]
    commitment = await create_commitment(client, regional_token, catalog, responsible_id=other)
    response = await client.get(
        "/api/compromisos", params={"responsible_id": other}, headers=auth(analista_token),
    )
    assert response.status_code == 200
    assert commitment["id"] not in {item["id"] for item in response.json()["items"]}
    assert all(
        item["responsible_id"] == catalog["users"]["analista.dipir@goreos.cl"]["id"]
        for item in response.json()["items"]
    )


async def test_personal_user_cannot_open_or_change_unassigned_commitment(
    client, regional_token, analista_token, catalog,
):
    commitment = await create_commitment(
        client, regional_token, catalog,
        responsible_id=catalog["users"]["rtf.daf@goreos.cl"]["id"],
    )
    path = f"/api/compromisos/{commitment['id']}"
    detail = await client.get(path, headers=auth(analista_token))
    update = await client.patch(path, json={"observations": "Denied"}, headers=auth(analista_token))
    complete = await client.post(path + "/completar", json={}, headers=auth(analista_token))
    assert [detail.status_code, update.status_code, complete.status_code] == [403, 403, 403]
    unchanged = await client.get(path, headers=auth(regional_token))
    assert unchanged.json()["state"] == "PENDIENTE"
    assert unchanged.json()["observations"] is None


async def test_readonly_role_cannot_complete_even_when_assigned(
    client, db, regional_token, consejero_token, catalog,
):
    user_id = str((await db.execute(text(
        'SELECT id FROM core."user" WHERE email = :email'
    ), {"email": "consejero1@goreos.cl"})).scalar_one())
    commitment = await create_commitment(client, regional_token, catalog, responsible_id=user_id)
    response = await client.post(
        f"/api/compromisos/{commitment['id']}/completar", json={}, headers=auth(consejero_token),
    )
    assert response.status_code == 403


async def test_assigned_commitment_journey_uses_its_own_identity(
    client, db, regional_token, analista_token, catalog,
):
    # The IPR is assigned to someone else. The commitment remains the analyst's work.
    ipr_id = str((await db.execute(text("""
        INSERT INTO core.ipr (codigo_bip, name, ipr_nature, assignee_id)
        VALUES (:bip, 'Synthetic inbox IPR', 'PROYECTO', CAST(:assignee AS uuid))
        RETURNING id
    """), {
        "bip": f"INBOX-{uuid.uuid4().hex[:8]}",
        "assignee": catalog["users"]["rtf.daf@goreos.cl"]["id"],
    })).scalar_one())
    await db.commit()
    commitment = await create_commitment(client, regional_token, catalog, ipr_id=ipr_id)
    cid = commitment["id"]
    denied_ipr = await client.get(f"/api/ipr/{ipr_id}", headers=auth(analista_token))
    assert denied_ipr.status_code == 403

    inbox = await client.get("/api/dashboard/action-items", headers=auth(analista_token))
    item = next(item for item in inbox.json()["items"] if item["id"] == cid)
    assert item["state"] == "PENDIENTE"
    assert item["responsible_id"] == catalog["users"]["analista.dipir@goreos.cl"]["id"]
    assert item["responsible_name"]
    assert item["action_label"] == "Completar"
    assert item["action_route"] == f"/compromisos?id={cid}"

    detail = await client.get(f"/api/compromisos/{cid}", headers=auth(analista_token))
    assert detail.status_code == 200
    assert "completar" in detail.json()["allowed_actions"]
    assert "verificar" not in detail.json()["allowed_actions"]
    complete = await client.post(
        f"/api/compromisos/{cid}/completar", json={"observations": "Synthetic completion"},
        headers=auth(analista_token),
    )
    assert complete.status_code == 200
    completed = await client.get(f"/api/compromisos/{cid}", headers=auth(analista_token))
    assert completed.json()["state"] == "COMPLETADO"
    assert completed.json()["history"][0]["new_state"] == "COMPLETADO"
    assert "completar" not in completed.json()["allowed_actions"]
    refreshed = await client.get("/api/dashboard/action-items", headers=auth(analista_token))
    assert cid not in {item["id"] for item in refreshed.json()["items"]}
    repeated = await client.post(
        f"/api/compromisos/{cid}/completar", json={}, headers=auth(analista_token),
    )
    assert repeated.status_code == 409


async def test_supervisor_sees_verification_without_an_ipr(
    client, regional_token, rtf_token, jefe_token, catalog,
):
    commitment = await create_commitment(
        client, regional_token, catalog,
        responsible_id=catalog["users"]["rtf.daf@goreos.cl"]["id"],
    )
    cid = commitment["id"]
    assert (await client.post(
        f"/api/compromisos/{cid}/completar", json={}, headers=auth(rtf_token),
    )).status_code == 200
    inbox = await client.get("/api/dashboard/action-items", headers=auth(jefe_token))
    item = next(item for item in inbox.json()["items"] if item["id"] == cid)
    assert item["state"] == "COMPLETADO"
    assert item["action_label"] == "Verificar"
    detail = await client.get(f"/api/compromisos/{cid}", headers=auth(jefe_token))
    assert "verificar" in detail.json()["allowed_actions"]
    assert "devolver" in detail.json()["allowed_actions"]
    assert (await client.post(
        f"/api/compromisos/{cid}/devolver", json={}, headers=auth(jefe_token),
    )).status_code == 422
    assert (await client.post(
        f"/api/compromisos/{cid}/verificar", json={}, headers=auth(jefe_token),
    )).status_code == 200
    refreshed = await client.get("/api/dashboard/action-items", headers=auth(jefe_token))
    assert cid not in {item["id"] for item in refreshed.json()["items"]}


async def test_personal_inbox_has_no_twenty_commitment_cutoff(
    client, regional_token, analista_token, catalog,
):
    created = {
        (await create_commitment(client, regional_token, catalog))["id"]
        for _ in range(21)
    }
    response = await client.get("/api/dashboard/action-items", headers=auth(analista_token))
    assert response.status_code == 200
    assert created <= {item["id"] for item in response.json()["items"]}
