"""Tests for authentication endpoints."""
from datetime import datetime, timedelta, timezone
from jose import jwt


async def test_login_success(client):
    """Valid credentials return access_token and user info."""
    resp = await client.post(
        "/api/auth/login",
        data={"username": "admin@goreos.cl", "password": "admin123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["user"]["email"] == "admin@goreos.cl"
    assert body["user"]["role_code"] == "ADMIN_SISTEMA"
    assert body["user"]["population"] == "operativa"


async def test_login_dgi_population(client):
    """DGI user login returns population=dgi."""
    resp = await client.post(
        "/api/auth/login",
        data={"username": "jefe.dgi@goreos.cl", "password": "admin123"},
    )
    assert resp.status_code == 200
    assert resp.json()["user"]["population"] == "dgi"


async def test_login_wrong_password(client):
    """Wrong password returns 401."""
    resp = await client.post(
        "/api/auth/login",
        data={"username": "admin@goreos.cl", "password": "wrongpass"},
    )
    assert resp.status_code == 401


async def test_protected_endpoint_no_token(client):
    """Accessing protected endpoint without token returns 401."""
    resp = await client.get("/api/dashboard")
    assert resp.status_code == 401


async def test_protected_endpoint_expired_token(client):
    """Expired JWT returns 401."""
    expired = jwt.encode(
        {"sub": "fake-id", "exp": datetime.now(timezone.utc) - timedelta(hours=1)},
        "goreos-dev-secret-change-in-production",
        algorithm="HS256",
    )
    resp = await client.get(
        "/api/dashboard",
        headers={"Authorization": f"Bearer {expired}"},
    )
    assert resp.status_code == 401
