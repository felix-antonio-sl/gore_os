"""Tests for the DGI reports module — list, create, status transitions."""
import pytest
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
