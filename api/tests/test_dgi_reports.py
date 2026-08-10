"""Tests for the DGI reports module — list, create, status transitions."""
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth


# ---------------------------------------------------------------------------
# Helper: create a report via API, return response JSON
# ---------------------------------------------------------------------------

async def _create_report(client, token, **overrides):
    """Create a DGI report with a default SEMANAL payload. Returns {'id': ...}."""
    payload = {
        "title": "Informe Semanal de Prueba",
        "report_type": "SEMANAL",
        "period_start": "2026-03-03",
        "period_end": "2026-03-07",
        **overrides,
    }
    resp = await client.post("/api/dgi/reports", json=payload, headers=auth(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# 1. List reports returns a list
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_reports(client, dgi_token):
    """GET /api/dgi/reports with DGI token returns 200 with a list."""
    resp = await client.get("/api/dgi/reports", headers=auth(dgi_token))
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)


# ---------------------------------------------------------------------------
# 2. Create report produces an id in BORRADOR state
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_report(client, dgi_token):
    """POST /api/dgi/reports creates a report with BORRADOR status."""
    data = await _create_report(client, dgi_token)
    assert "id" in data

    # Verify the report appears in the list
    resp = await client.get("/api/dgi/reports", headers=auth(dgi_token))
    assert resp.status_code == 200
    report_ids = [r["id"] for r in resp.json()]
    assert str(data["id"]) in report_ids


# ---------------------------------------------------------------------------
# 3. Non-DGI role can list reports (list endpoint has no role restriction)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_non_dgi_can_list_reports(client, regional_token):
    """GET /api/dgi/reports with ADMIN_REGIONAL returns 200.

    The list endpoint has no DGI-role restriction — access is open to any
    authenticated user. Only status transitions (POST /{id}/status) are
    DGI-restricted.
    """
    resp = await client.get("/api/dgi/reports", headers=auth(regional_token))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ---------------------------------------------------------------------------
# 4. Requires authentication
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_reports_require_auth(client):
    """GET /api/dgi/reports without token returns 401."""
    resp = await client.get("/api/dgi/reports")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_report_review_and_send_authority(client, dgi_token, esp_control_token):
    """DGI can submit a draft, but only JEFE_DGI can send it."""
    report = await _create_report(client, dgi_token, title="Informe Flujo de Aprobación")
    report_id = report["id"]

    review_resp = await client.post(
        f"/api/dgi/reports/{report_id}/status",
        json={"status": "EN_REVISION"},
        headers=auth(esp_control_token),
    )
    assert review_resp.status_code == 200

    forbidden_resp = await client.post(
        f"/api/dgi/reports/{report_id}/status",
        json={"status": "ENVIADO"},
        headers=auth(esp_control_token),
    )
    assert forbidden_resp.status_code == 403

    send_resp = await client.post(
        f"/api/dgi/reports/{report_id}/status",
        json={"status": "ENVIADO"},
        headers=auth(dgi_token),
    )
    assert send_resp.status_code == 200


@pytest.mark.asyncio
async def test_report_status_is_enforced_by_db(
    client,
    dgi_token,
    db: AsyncSession,
):
    """A direct write cannot skip the canonical report review state."""
    report = await _create_report(client, dgi_token, title="Informe Autoridad DB")

    try:
        with pytest.raises(DBAPIError) as exc_info:
            await db.execute(
                text("""
                    UPDATE core.dgi_report
                    SET status_id = (
                        SELECT id FROM ref.category
                        WHERE scheme = 'dgi_report_status'
                          AND code = 'ENVIADO'
                    )
                    WHERE id = :id
                """),
                {"id": report["id"]},
            )
    finally:
        await db.rollback()

    assert "Transición de estado inválida" in str(exc_info.value.orig)
