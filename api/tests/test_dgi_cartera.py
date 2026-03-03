"""
Integration tests for DGI Cartera IPR endpoints.

Covers: auth, role restriction, pagination, health signals, filters,
summary coherence, and overdue installments.
"""
import pytest
from tests.conftest import auth


# ---------------------------------------------------------------------------
# Auth / Role guards
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cartera_requires_auth(client):
    """GET /api/dgi/cartera without token → 401."""
    resp = await client.get("/api/dgi/cartera")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_cartera_requires_dgi_role(client, jefe_token):
    """GET /api/dgi/cartera with operational role → 403."""
    resp = await client.get("/api/dgi/cartera", headers=auth(jefe_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_resumen_requires_dgi_role(client, encargado_token):
    """GET /api/dgi/cartera/resumen with operational role → 403."""
    resp = await client.get("/api/dgi/cartera/resumen", headers=auth(encargado_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_cuotas_requires_dgi_role(client, regional_token):
    """GET /api/dgi/cartera/cuotas-vencidas with operational role → 403."""
    resp = await client.get("/api/dgi/cartera/cuotas-vencidas", headers=auth(regional_token))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Cartera list
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cartera_returns_paginated(client, dgi_token):
    """GET /api/dgi/cartera returns standard paginated structure."""
    resp = await client.get("/api/dgi/cartera?page_size=5", headers=auth(dgi_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "page_size" in body
    assert "total_pages" in body
    assert body["page"] == 1
    assert body["page_size"] == 5


@pytest.mark.asyncio
async def test_cartera_item_has_health_signal(client, dgi_token):
    """Each item must have health_signal in VERDE/AMARILLO/ROJO."""
    resp = await client.get("/api/dgi/cartera?page_size=3", headers=auth(dgi_token))
    assert resp.status_code == 200
    body = resp.json()
    for item in body["items"]:
        assert item["health_signal"] in ("VERDE", "AMARILLO", "ROJO")
        assert isinstance(item["health_reasons"], list)


@pytest.mark.asyncio
async def test_cartera_item_has_aggregated_data(client, dgi_token):
    """Each item has all expected aggregated fields."""
    resp = await client.get("/api/dgi/cartera?page_size=1", headers=auth(dgi_token))
    assert resp.status_code == 200
    body = resp.json()
    if body["items"]:
        item = body["items"][0]
        expected_keys = [
            "id", "codigo_bip", "name", "mechanism", "mcd_phase",
            "health_signal", "health_reasons", "days_since_update",
            "physical_progress", "financial_progress",
            "cdp_total", "cdp_paid", "budget_execution_pct",
            "agreement_count", "agreement_latest_state", "overdue_installments",
            "resolution_count", "pending_cgr",
            "open_problems", "active_alerts", "critical_alerts",
            "overdue_commitments",
        ]
        for key in expected_keys:
            assert key in item, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cartera_filter_by_phase(client, dgi_token):
    """Filter by mcd_phase returns only that phase."""
    resp = await client.get("/api/dgi/cartera?mcd_phase=F4&page_size=50", headers=auth(dgi_token))
    assert resp.status_code == 200
    body = resp.json()
    for item in body["items"]:
        assert item["mcd_phase"] == "F4"


@pytest.mark.asyncio
async def test_cartera_search(client, dgi_token):
    """Search filters by BIP code or name (ILIKE)."""
    # First get any item to search for
    resp = await client.get("/api/dgi/cartera?page_size=1", headers=auth(dgi_token))
    body = resp.json()
    if not body["items"]:
        pytest.skip("No IPRs in test DB")
    bip = body["items"][0]["codigo_bip"]
    # Search for first few chars of BIP
    term = bip[:5]
    resp2 = await client.get(f"/api/dgi/cartera?search={term}", headers=auth(dgi_token))
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2["total"] >= 1
    assert any(term in item["codigo_bip"] for item in body2["items"])


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_resumen_returns_summary(client, dgi_token):
    """GET /api/dgi/cartera/resumen returns CarteraSummary structure."""
    resp = await client.get("/api/dgi/cartera/resumen", headers=auth(dgi_token))
    assert resp.status_code == 200
    body = resp.json()
    for key in ["total", "verde", "amarillo", "rojo", "overdue_installments_total",
                "pending_cgr_total", "monto_total", "total_paid"]:
        assert key in body, f"Missing summary key: {key}"


@pytest.mark.asyncio
async def test_resumen_totals_consistent(client, dgi_token):
    """verde + amarillo + rojo must equal total (diagram commutes)."""
    resp = await client.get("/api/dgi/cartera/resumen", headers=auth(dgi_token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["verde"] + body["amarillo"] + body["rojo"] == body["total"]


# ---------------------------------------------------------------------------
# Cuotas vencidas
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cuotas_vencidas_returns_paginated(client, dgi_token):
    """GET /api/dgi/cartera/cuotas-vencidas returns paginated structure."""
    resp = await client.get("/api/dgi/cartera/cuotas-vencidas", headers=auth(dgi_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body
    # Each overdue item should have expected fields
    for item in body["items"]:
        assert "amount" in item
        assert "days_overdue" in item
        assert "agreement_number" in item or item["agreement_number"] is None
        assert item["days_overdue"] >= 0
