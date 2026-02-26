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


# ---------------------------------------------------------------------------
# Password change tests
# ---------------------------------------------------------------------------

async def test_change_password_success(client, regional_token):
    """Change password and verify login with new password works."""
    from tests.conftest import auth

    # Change password
    resp = await client.post(
        "/api/auth/change-password",
        json={"current_password": "admin123", "new_password": "newpass1234"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200

    # Login with new password
    resp2 = await client.post(
        "/api/auth/login",
        data={"username": "regional@goreos.cl", "password": "newpass1234"},
    )
    assert resp2.status_code == 200

    # Restore original password
    new_token = resp2.json()["access_token"]
    await client.post(
        "/api/auth/change-password",
        json={"current_password": "newpass1234", "new_password": "admin123"},
        headers=auth(new_token),
    )


async def test_change_password_wrong_current(client, admin_token):
    """Wrong current password returns 401."""
    from tests.conftest import auth

    resp = await client.post(
        "/api/auth/change-password",
        json={"current_password": "wrongpassword", "new_password": "newpass1234"},
        headers=auth(admin_token),
    )
    assert resp.status_code == 401


async def test_change_password_too_short(client, admin_token):
    """Password shorter than 8 chars returns 422."""
    from tests.conftest import auth

    resp = await client.post(
        "/api/auth/change-password",
        json={"current_password": "admin123", "new_password": "short"},
        headers=auth(admin_token),
    )
    assert resp.status_code == 422
