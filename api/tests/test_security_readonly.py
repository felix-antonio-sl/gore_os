"""
Tests: CONSEJERO_REGIONAL read-only enforcement.

The CR role is a supervisory/oversight role that must have full READ access
but zero WRITE access to operational endpoints.
"""
import pytest
from tests.conftest import auth


# ---------------------------------------------------------------------------
# Helper: create test data as regional (write-capable role) so CR can read it
# ---------------------------------------------------------------------------

@pytest.fixture
async def seed_data(client, regional_token, catalog):
    """Create a problema and a convenio as regional so CR can attempt operations."""
    # Create a problema
    from sqlalchemy import text

    # We need an IPR to create a problema — use existing one
    ipr_resp = await client.get("/api/ipr?page_size=1", headers=auth(regional_token))
    iprs = ipr_resp.json()
    ipr_id = iprs["items"][0]["id"] if iprs["items"] else None

    problema_id = None
    if ipr_id:
        resp = await client.post(
            "/api/problemas",
            json={
                "ipr_id": ipr_id,
                "problem_type_id": catalog["problem_type_id"],
                "description": "Test problema for CR readonly",
            },
            headers=auth(regional_token),
        )
        if resp.status_code == 201:
            problema_id = resp.json()["id"]

    # Create a convenio
    convenio_resp = await client.post(
        "/api/convenios",
        json={
            "agreement_type_id": catalog["agreement_type_id"],
            "state_id": catalog["agreement_state_borrador_id"],
            "total_amount": 1000000,
        },
        headers=auth(regional_token),
    )
    convenio_id = convenio_resp.json()["id"] if convenio_resp.status_code == 201 else None

    return {
        "ipr_id": ipr_id,
        "problema_id": problema_id,
        "convenio_id": convenio_id,
    }


# ---------------------------------------------------------------------------
# WRITE endpoints must return 403 for CONSEJERO_REGIONAL
# ---------------------------------------------------------------------------

class TestConsejeroWriteBlocked:
    """All POST/PATCH write endpoints must reject CONSEJERO_REGIONAL."""

    @pytest.mark.asyncio
    async def test_create_problema_forbidden(self, client, consejero_token, catalog, seed_data):
        # Use a fake UUID if no IPR exists — the role check runs before DB validation
        ipr_id = seed_data["ipr_id"] or "00000000-0000-0000-0000-000000000001"
        resp = await client.post(
            "/api/problemas",
            json={
                "ipr_id": ipr_id,
                "problem_type_id": catalog["problem_type_id"],
                "description": "CR should not create",
            },
            headers=auth(consejero_token),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_update_problema_forbidden(self, client, consejero_token, seed_data):
        if not seed_data["problema_id"]:
            pytest.skip("No problema created in seed")
        resp = await client.patch(
            f"/api/problemas/{seed_data['problema_id']}",
            json={"proposed_solution": "CR hack"},
            headers=auth(consejero_token),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_attend_alerta_forbidden(self, client, consejero_token, regional_token):
        # Get an alert if one exists
        resp = await client.get("/api/alertas?page_size=1", headers=auth(regional_token))
        items = resp.json().get("items", [])
        if not items:
            pytest.skip("No alerts in test DB")
        alerta_id = items[0]["id"]

        resp = await client.post(
            f"/api/alertas/{alerta_id}/atender",
            json={"action_taken": "CR should not attend"},
            headers=auth(consejero_token),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_create_progress_report_forbidden(self, client, consejero_token, seed_data):
        if not seed_data["ipr_id"]:
            pytest.skip("No IPR in test DB")
        resp = await client.post(
            f"/api/ipr/{seed_data['ipr_id']}/avances",
            json={
                "report_date": "2026-02-26",
                "physical_progress": 50,
                "financial_progress": 40,
                "description": "CR should not create reports",
            },
            headers=auth(consejero_token),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_create_convenio_forbidden(self, client, consejero_token, catalog):
        resp = await client.post(
            "/api/convenios",
            json={
                "agreement_type_id": catalog["agreement_type_id"],
                "state_id": catalog["agreement_state_borrador_id"],
                "total_amount": 500000,
            },
            headers=auth(consejero_token),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_update_convenio_forbidden(self, client, consejero_token, seed_data):
        if not seed_data["convenio_id"]:
            pytest.skip("No convenio created in seed")
        resp = await client.patch(
            f"/api/convenios/{seed_data['convenio_id']}",
            json={"total_amount": 999},
            headers=auth(consejero_token),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_add_cuota_forbidden(self, client, consejero_token, catalog, seed_data):
        if not seed_data["convenio_id"]:
            pytest.skip("No convenio created in seed")
        resp = await client.post(
            f"/api/convenios/{seed_data['convenio_id']}/cuotas",
            json={
                "installment_number": 1,
                "amount": 100000,
                "due_date": "2026-06-30",
                "payment_status_id": catalog["payment_status_pendiente_id"],
            },
            headers=auth(consejero_token),
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_update_cuota_forbidden(self, client, consejero_token, regional_token, catalog, seed_data):
        if not seed_data["convenio_id"]:
            pytest.skip("No convenio created in seed")
        # Create a cuota as regional first
        cuota_resp = await client.post(
            f"/api/convenios/{seed_data['convenio_id']}/cuotas",
            json={
                "installment_number": 99,
                "amount": 50000,
                "due_date": "2026-12-31",
                "payment_status_id": catalog["payment_status_pendiente_id"],
            },
            headers=auth(regional_token),
        )
        if cuota_resp.status_code != 201:
            pytest.skip("Could not create cuota for test")
        cuota_id = cuota_resp.json()["id"]

        resp = await client.patch(
            f"/api/convenios/{seed_data['convenio_id']}/cuotas/{cuota_id}",
            json={"amount": 1},
            headers=auth(consejero_token),
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# READ endpoints must still work for CONSEJERO_REGIONAL
# ---------------------------------------------------------------------------

class TestConsejeroReadAllowed:
    """GET endpoints must return 200 for CONSEJERO_REGIONAL."""

    @pytest.mark.asyncio
    async def test_list_problemas_ok(self, client, consejero_token):
        resp = await client.get("/api/problemas", headers=auth(consejero_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_list_alertas_ok(self, client, consejero_token):
        resp = await client.get("/api/alertas", headers=auth(consejero_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_list_convenios_ok(self, client, consejero_token):
        resp = await client.get("/api/convenios", headers=auth(consejero_token))
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_list_iprs_ok(self, client, consejero_token):
        resp = await client.get("/api/ipr", headers=auth(consejero_token))
        assert resp.status_code == 200
