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


# ---------------------------------------------------------------------------
# Brute-force protection tests
# ---------------------------------------------------------------------------

async def test_login_lockout_after_5_failures(client, db):
    """Account is locked after 5 failed login attempts, returns 429 on 6th."""
    from sqlalchemy import text
    # Reset lockout state for admin user
    await db.execute(
        text('UPDATE core."user" SET failed_login_attempts = 0, locked_until = NULL WHERE email = :e'),
        {"e": "admin@goreos.cl"},
    )
    await db.commit()

    for i in range(5):
        resp = await client.post(
            "/api/auth/login",
            data={"username": "admin@goreos.cl", "password": "wrongpass"},
        )
        assert resp.status_code == 401, f"Attempt {i+1} should return 401"

    # 6th attempt → 429
    resp = await client.post(
        "/api/auth/login",
        data={"username": "admin@goreos.cl", "password": "wrongpass"},
    )
    assert resp.status_code == 429

    # Cleanup: unlock the user
    await db.execute(
        text('UPDATE core."user" SET failed_login_attempts = 0, locked_until = NULL WHERE email = :e'),
        {"e": "admin@goreos.cl"},
    )
    await db.commit()


async def test_login_locked_blocks_correct_password(client, db):
    """Even correct password is rejected while account is locked."""
    from sqlalchemy import text
    # Force lock
    await db.execute(
        text("UPDATE core.\"user\" SET failed_login_attempts = 5, locked_until = NOW() + INTERVAL '15 minutes' WHERE email = :e"),
        {"e": "admin@goreos.cl"},
    )
    await db.commit()

    resp = await client.post(
        "/api/auth/login",
        data={"username": "admin@goreos.cl", "password": "admin123"},
    )
    assert resp.status_code == 429

    # Cleanup
    await db.execute(
        text('UPDATE core."user" SET failed_login_attempts = 0, locked_until = NULL WHERE email = :e'),
        {"e": "admin@goreos.cl"},
    )
    await db.commit()


async def test_login_lockout_resets_on_success(client, db):
    """Successful login resets failed_login_attempts counter."""
    from sqlalchemy import text
    # Set 3 failed attempts (below threshold)
    await db.execute(
        text('UPDATE core."user" SET failed_login_attempts = 3, locked_until = NULL WHERE email = :e'),
        {"e": "admin@goreos.cl"},
    )
    await db.commit()

    resp = await client.post(
        "/api/auth/login",
        data={"username": "admin@goreos.cl", "password": "admin123"},
    )
    assert resp.status_code == 200

    # Verify counter was reset
    result = await db.execute(
        text('SELECT failed_login_attempts FROM core."user" WHERE email = :e'),
        {"e": "admin@goreos.cl"},
    )
    row = result.mappings().first()
    assert row["failed_login_attempts"] == 0


async def test_security_headers_present(client):
    """Security headers are present in API responses."""
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-XSS-Protection") == "1; mode=block"
    assert resp.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
