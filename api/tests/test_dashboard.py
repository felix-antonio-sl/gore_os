"""Tests for role-aware dashboard dispatch and chart data."""
from tests.conftest import auth


async def test_admin_dashboard(client, regional_token):
    """ADMIN_REGIONAL gets global dashboard with KPIs."""
    resp = await client.get("/api/dashboard", headers=auth(regional_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "kpis" in body
    assert len(body["kpis"]) >= 4


async def test_jefe_dashboard(client, jefe_token):
    """JEFE_DIVISION gets division-scoped dashboard."""
    resp = await client.get("/api/dashboard", headers=auth(jefe_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "kpis" in body


async def test_encargado_dashboard(client, encargado_token):
    """ENCARGADO gets personal dashboard."""
    resp = await client.get("/api/dashboard", headers=auth(encargado_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "kpis" in body


async def test_mi_division_endpoint(client, jefe_token):
    """GET /api/dashboard/mi-division returns team load."""
    resp = await client.get("/api/dashboard/mi-division", headers=auth(jefe_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "kpis" in body


async def test_mis_compromisos_endpoint(client, encargado_token):
    """GET /api/dashboard/mis-compromisos returns grouped commitments."""
    resp = await client.get("/api/dashboard/mis-compromisos", headers=auth(encargado_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "kpis" in body


async def test_chart_data(client, regional_token):
    """GET /api/dashboard/chart-data returns 3 chart datasets."""
    resp = await client.get("/api/dashboard/chart-data", headers=auth(regional_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "commitments_by_state" in body
    assert "alerts_by_severity" in body
    assert "budget_by_division" in body
