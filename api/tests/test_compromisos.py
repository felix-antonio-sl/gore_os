"""Tests for the commitment state machine and role-based access."""
import uuid
from datetime import date, timedelta
from tests.conftest import auth


# ---------------------------------------------------------------------------
# Helper: create a commitment via API, return response JSON
# ---------------------------------------------------------------------------
async def _create_commitment(client, token, catalog, **overrides):
    users = catalog["users"]
    payload = {
        "description": f"Test commitment {uuid.uuid4().hex[:8]}",
        "commitment_type_id": catalog["commitment_type_id"],
        "responsible_id": users["encargado.daf@goreos.cl"]["id"],
        "due_date": str(date.today() + timedelta(days=30)),
        **overrides,
    }
    resp = await client.post("/api/compromisos", json=payload, headers=auth(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Creation
# ---------------------------------------------------------------------------

async def test_create_commitment(client, regional_token, catalog):
    """ADMIN_REGIONAL can create a commitment with auto-generated code."""
    data = await _create_commitment(client, regional_token, catalog)
    assert data["code"].startswith("OC-")
    assert "id" in data


async def test_create_encargado_allowed(client, encargado_token, catalog):
    """ENCARGADO can create commitments (expanded permissions)."""
    resp = await client.post(
        "/api/compromisos",
        json={
            "description": "Created by encargado",
            "commitment_type_id": catalog["commitment_type_id"],
            "responsible_id": catalog["users"]["encargado.daf@goreos.cl"]["id"],
            "due_date": str(date.today() + timedelta(days=30)),
        },
        headers=auth(encargado_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"].startswith("OC-")


# ---------------------------------------------------------------------------
# Completar
# ---------------------------------------------------------------------------

async def test_complete_as_responsible(client, regional_token, encargado_token, catalog):
    """Responsible user (ENCARGADO) can complete their own commitment."""
    data = await _create_commitment(client, regional_token, catalog)
    cid = data["id"]

    resp = await client.post(
        f"/api/compromisos/{cid}/completar",
        json={"observations": "Completado por responsable"},
        headers=auth(encargado_token),
    )
    assert resp.status_code == 200

    # Verify state changed
    detail = await client.get(f"/api/compromisos/{cid}", headers=auth(regional_token))
    assert detail.json()["state"] == "COMPLETADO"
    assert detail.json()["completed_at"] is not None


async def test_complete_as_admin(client, regional_token, catalog):
    """Admin can complete any commitment."""
    data = await _create_commitment(client, regional_token, catalog)
    resp = await client.post(
        f"/api/compromisos/{data['id']}/completar",
        json={"observations": "Admin override"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200


async def test_complete_already_verified(client, regional_token, encargado_token, jefe_token, catalog):
    """Cannot complete a VERIFICADO commitment (409)."""
    data = await _create_commitment(client, regional_token, catalog)
    cid = data["id"]

    # PENDIENTE -> COMPLETADO
    await client.post(f"/api/compromisos/{cid}/completar", json={}, headers=auth(encargado_token))
    # COMPLETADO -> VERIFICADO
    await client.post(f"/api/compromisos/{cid}/verificar", json={}, headers=auth(jefe_token))

    # Try to complete VERIFICADO -> should 409
    resp = await client.post(
        f"/api/compromisos/{cid}/completar",
        json={"observations": "Should fail"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Verificar
# ---------------------------------------------------------------------------

async def test_verify_as_jefe_own_division(client, regional_token, encargado_token, jefe_token, catalog):
    """JEFE_DIVISION can verify commitment in own division."""
    data = await _create_commitment(client, regional_token, catalog)
    cid = data["id"]

    await client.post(f"/api/compromisos/{cid}/completar", json={}, headers=auth(encargado_token))
    resp = await client.post(f"/api/compromisos/{cid}/verificar", json={}, headers=auth(jefe_token))
    assert resp.status_code == 200

    detail = await client.get(f"/api/compromisos/{cid}", headers=auth(regional_token))
    assert detail.json()["state"] == "VERIFICADO"
    assert detail.json()["verified_at"] is not None


async def test_verify_from_pendiente(client, regional_token, jefe_token, catalog):
    """Cannot verify from PENDIENTE — only from COMPLETADO (409)."""
    data = await _create_commitment(client, regional_token, catalog)
    resp = await client.post(
        f"/api/compromisos/{data['id']}/verificar",
        json={},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 409


async def test_encargado_cannot_verify(client, regional_token, encargado_token, catalog):
    """ENCARGADO cannot verify commitments (403)."""
    data = await _create_commitment(client, regional_token, catalog)
    cid = data["id"]

    await client.post(f"/api/compromisos/{cid}/completar", json={}, headers=auth(encargado_token))
    resp = await client.post(
        f"/api/compromisos/{cid}/verificar",
        json={},
        headers=auth(encargado_token),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Devolver
# ---------------------------------------------------------------------------

async def test_devolver_from_completado(client, regional_token, encargado_token, jefe_token, catalog):
    """Devolver returns COMPLETADO -> EN_PROGRESO and clears completed_at."""
    data = await _create_commitment(client, regional_token, catalog)
    cid = data["id"]

    await client.post(f"/api/compromisos/{cid}/completar", json={}, headers=auth(encargado_token))
    resp = await client.post(
        f"/api/compromisos/{cid}/devolver",
        json={"observations": "Requiere corrección"},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 200

    detail = await client.get(f"/api/compromisos/{cid}", headers=auth(regional_token))
    assert detail.json()["state"] == "EN_PROGRESO"
    assert detail.json()["completed_at"] is None


async def test_devolver_requires_observations(client, regional_token, encargado_token, jefe_token, catalog):
    """Devolver without observations returns 422."""
    data = await _create_commitment(client, regional_token, catalog)
    cid = data["id"]

    await client.post(f"/api/compromisos/{cid}/completar", json={}, headers=auth(encargado_token))
    resp = await client.post(
        f"/api/compromisos/{cid}/devolver",
        json={},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 422


async def test_devolver_from_pendiente(client, regional_token, jefe_token, catalog):
    """Cannot devolver from PENDIENTE (409)."""
    data = await _create_commitment(client, regional_token, catalog)
    resp = await client.post(
        f"/api/compromisos/{data['id']}/devolver",
        json={"observations": "Should fail"},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# List filtering
# ---------------------------------------------------------------------------

async def test_encargado_sees_only_own(client, regional_token, encargado_token, catalog):
    """ENCARGADO list is auto-filtered to responsible_id = self."""
    await _create_commitment(client, regional_token, catalog)

    resp = await client.get("/api/compromisos", headers=auth(encargado_token))
    assert resp.status_code == 200
    items = resp.json()["items"]
    encargado_id = catalog["users"]["encargado.daf@goreos.cl"]["id"]
    for item in items:
        assert item["responsible_id"] == encargado_id


# ---------------------------------------------------------------------------
# PATCH observations
# ---------------------------------------------------------------------------

async def test_patch_observations(client, regional_token, catalog):
    """PATCH observations updates text without changing state."""
    data = await _create_commitment(client, regional_token, catalog)
    cid = data["id"]

    resp = await client.patch(
        f"/api/compromisos/{cid}",
        json={"observations": "Nota actualizada"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200

    detail = await client.get(f"/api/compromisos/{cid}", headers=auth(regional_token))
    assert detail.json()["observations"] == "Nota actualizada"
    assert detail.json()["state"] == "PENDIENTE"  # state unchanged


async def test_patch_no_state_change(client, regional_token, catalog):
    """PATCH with empty body returns 'Sin cambios'."""
    data = await _create_commitment(client, regional_token, catalog)
    resp = await client.patch(
        f"/api/compromisos/{data['id']}",
        json={},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    assert "Sin cambios" in resp.json().get("message", "")


# ---------------------------------------------------------------------------
# Reassignment
# ---------------------------------------------------------------------------

async def test_reassign_commitment(client, regional_token, jefe_token, catalog):
    """JEFE can reassign a commitment to another user."""
    data = await _create_commitment(client, regional_token, catalog)
    cid = data["id"]
    new_responsible = catalog["users"]["jefe.daf@goreos.cl"]["id"]

    resp = await client.patch(
        f"/api/compromisos/{cid}",
        json={"responsible_id": new_responsible},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 200

    detail = await client.get(f"/api/compromisos/{cid}", headers=auth(regional_token))
    assert detail.json()["responsible_id"] == new_responsible


async def test_reassign_forbidden_encargado(client, regional_token, encargado_token, catalog):
    """ENCARGADO cannot reassign (403)."""
    data = await _create_commitment(client, regional_token, catalog)
    resp = await client.patch(
        f"/api/compromisos/{data['id']}",
        json={"responsible_id": catalog["users"]["admin@goreos.cl"]["id"]},
        headers=auth(encargado_token),
    )
    assert resp.status_code == 403
