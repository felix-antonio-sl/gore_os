"""Tests for admin router — user + division management (ADMIN_SISTEMA only)."""
import pytest
from uuid import uuid4
from sqlalchemy import text
from tests.conftest import auth


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_role_id(db, code: str = "ANALISTA") -> str:
    """Fetch a system_role category ID from the test DB."""
    result = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = :code"),
        {"code": code},
    )
    role_id = result.scalar()
    assert role_id, f"system_role '{code}' not found in goreos_test"
    return str(role_id)


async def _create_test_user(client, admin_token, db, catalog, *, email=None):
    """Helper: create a user via POST and return the response body."""
    role_id = await _get_role_id(db, "ANALISTA")
    email = email or f"test-{uuid4().hex[:8]}@goreos.cl"
    payload = {
        "email": email,
        "password": "testpass123",
        "names": "Test",
        "paternal_surname": "Integration",
        "maternal_surname": "Suite",
        "system_role_id": role_id,
        "division_id": catalog["division_id"],
    }
    resp = await client.post("/api/admin/usuarios", json=payload, headers=auth(admin_token))
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# 1. List users
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_usuarios(client, admin_token):
    """GET /api/admin/usuarios returns paginated response with items."""
    resp = await client.get("/api/admin/usuarios", headers=auth(admin_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "page_size" in body
    assert "total_pages" in body
    assert body["total"] > 0
    assert len(body["items"]) > 0
    # Verify item shape
    item = body["items"][0]
    assert "id" in item
    assert "email" in item
    assert "role_code" in item
    assert "is_active" in item


# ---------------------------------------------------------------------------
# 2. List users with search
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_usuarios_search(client, admin_token):
    """GET /api/admin/usuarios?search=admin filters results."""
    resp = await client.get(
        "/api/admin/usuarios?search=admin", headers=auth(admin_token)
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    emails = [item["email"] for item in body["items"]]
    assert any("admin" in e for e in emails)


# ---------------------------------------------------------------------------
# 3. Create user
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_usuario(client, admin_token, db, catalog):
    """POST /api/admin/usuarios creates a new user and returns id + email."""
    role_id = await _get_role_id(db, "ANALISTA")
    unique_email = f"test-create-{uuid4().hex[:8]}@goreos.cl"

    payload = {
        "email": unique_email,
        "password": "testpass123",
        "names": "Nuevo",
        "paternal_surname": "Usuario",
        "maternal_surname": "Test",
        "system_role_id": role_id,
        "division_id": catalog["division_id"],
    }
    resp = await client.post(
        "/api/admin/usuarios", json=payload, headers=auth(admin_token)
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["email"] == unique_email

    # Verify user exists in DB
    check = await db.execute(
        text('SELECT id FROM core."user" WHERE email = :e AND deleted_at IS NULL'),
        {"e": unique_email},
    )
    assert check.scalar() is not None


# ---------------------------------------------------------------------------
# 4. Duplicate email → 409
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_usuario_duplicate_email(client, admin_token, db, catalog):
    """POST /api/admin/usuarios with existing email returns 409."""
    role_id = await _get_role_id(db, "ANALISTA")
    payload = {
        "email": "admin@goreos.cl",
        "password": "testpass123",
        "names": "Duplicate",
        "paternal_surname": "Test",
        "system_role_id": role_id,
        "division_id": catalog["division_id"],
    }
    resp = await client.post(
        "/api/admin/usuarios", json=payload, headers=auth(admin_token)
    )
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# 5. Update user
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_usuario(client, admin_token, catalog):
    """PATCH /api/admin/usuarios/{id} updates person fields."""
    admin_id = catalog["users"]["admin@goreos.cl"]["id"]

    resp = await client.patch(
        f"/api/admin/usuarios/{admin_id}",
        json={"names": "Administrador"},
        headers=auth(admin_token),
    )
    assert resp.status_code == 200
    assert "message" in resp.json()

    # Verify via detail endpoint
    detail_resp = await client.get(
        f"/api/admin/usuarios/{admin_id}", headers=auth(admin_token)
    )
    assert detail_resp.status_code == 200
    assert detail_resp.json()["names"] == "Administrador"


# ---------------------------------------------------------------------------
# 6. Toggle active (create fresh user to avoid side effects)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_toggle_activo(client, admin_token, db, catalog):
    """POST /api/admin/usuarios/{id}/toggle-activo toggles is_active."""
    created = await _create_test_user(client, admin_token, db, catalog)
    user_id = created["id"]

    # First toggle: should deactivate (default is_active=True)
    resp = await client.post(
        f"/api/admin/usuarios/{user_id}/toggle-activo",
        headers=auth(admin_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "is_active" in body
    assert isinstance(body["is_active"], bool)
    assert body["is_active"] is False

    # Second toggle: should reactivate
    resp2 = await client.post(
        f"/api/admin/usuarios/{user_id}/toggle-activo",
        headers=auth(admin_token),
    )
    assert resp2.status_code == 200
    assert resp2.json()["is_active"] is True


# ---------------------------------------------------------------------------
# 7. Reset password
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_reset_password(client, admin_token, db, catalog):
    """POST /api/admin/usuarios/{id}/reset-password updates password."""
    created = await _create_test_user(client, admin_token, db, catalog)
    user_id = created["id"]

    resp = await client.post(
        f"/api/admin/usuarios/{user_id}/reset-password",
        json={"new_password": "newpass123"},
        headers=auth(admin_token),
    )
    assert resp.status_code == 200
    assert "message" in resp.json()

    # Verify: login with new password should work
    login_resp = await client.post(
        "/api/auth/login",
        data={"username": created["email"], "password": "newpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()


# ---------------------------------------------------------------------------
# 8. List divisiones
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_divisiones(client, admin_token):
    """GET /api/admin/divisiones returns list with at least 1 division."""
    resp = await client.get("/api/admin/divisiones", headers=auth(admin_token))
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    # Verify item shape
    item = body[0]
    assert "id" in item
    assert "code" in item
    assert "name" in item
    assert "organization_type" in item
    assert "user_count" in item


# ---------------------------------------------------------------------------
# 9. GET /api/admin/usuarios → 403 for ADMIN_REGIONAL
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_403_for_non_admin(client, regional_token):
    """GET /api/admin/usuarios with non-ADMIN_SISTEMA role returns 403."""
    resp = await client.get("/api/admin/usuarios", headers=auth(regional_token))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 10. POST /api/admin/usuarios → 403 for ANALISTA
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_403_for_encargado(client, analista_token, db):
    """POST /api/admin/usuarios with ANALISTA role returns 403."""
    role_id = await _get_role_id(db, "ANALISTA")
    payload = {
        "email": f"test-forbidden-{uuid4().hex[:8]}@goreos.cl",
        "password": "testpass123",
        "names": "Forbidden",
        "paternal_surname": "Test",
        "system_role_id": role_id,
    }
    resp = await client.post(
        "/api/admin/usuarios", json=payload, headers=auth(analista_token)
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 11. GET /api/admin/usuarios/{id} — User detail
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_usuario_detail(client, admin_token, catalog):
    """GET /api/admin/usuarios/{id} returns full user detail."""
    admin_id = catalog["users"]["admin@goreos.cl"]["id"]

    resp = await client.get(
        f"/api/admin/usuarios/{admin_id}", headers=auth(admin_token)
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == admin_id
    assert body["email"] == "admin@goreos.cl"
    assert body["role_code"] == "ADMIN_SISTEMA"
    assert "names" in body
    assert "paternal_surname" in body
    assert "is_active" in body
    assert "system_role_id" in body


# ---------------------------------------------------------------------------
# Data quality
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_data_quality_endpoint(client, admin_token):
    """GET /api/admin/data-quality returns metrics for all entity types."""
    resp = await client.get("/api/admin/data-quality", headers=auth(admin_token))
    assert resp.status_code == 200
    body = resp.json()
    for section in ("persons", "iprs", "agreements", "documents", "organizations"):
        assert section in body, f"Missing section: {section}"
        assert "total" in body[section]


@pytest.mark.asyncio
async def test_data_quality_requires_admin(client, regional_token):
    """Non-admin users cannot access data-quality endpoint."""
    resp = await client.get("/api/admin/data-quality", headers=auth(regional_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_data_quality_has_percentages(client, admin_token):
    """Data quality response includes percentage fields."""
    resp = await client.get("/api/admin/data-quality", headers=auth(admin_token))
    assert resp.status_code == 200
    body = resp.json()
    # Persons section must have percentage fields
    assert "pct_email" in body["persons"]
    assert "pct_rut" in body["persons"]
    # IPRs section must have percentage fields
    assert "pct_executor" in body["iprs"]
    assert "pct_mechanism" in body["iprs"]
    # All percentages should be 0-100 floats
    for pct_key in ("pct_email", "pct_rut", "pct_phone"):
        assert 0 <= body["persons"][pct_key] <= 100


# ---------------------------------------------------------------------------
# SLA Dashboard
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sla_dashboard(client, admin_token):
    """GET /api/admin/slas/dashboard returns 12 SLA items."""
    resp = await client.get("/api/admin/slas/dashboard", headers=auth(admin_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "total_monitored" in body
    assert body["total_monitored"] == 12
    assert "slas" in body
    assert len(body["slas"]) == 12
    for sla in body["slas"]:
        assert "name" in sla
        assert "signal" in sla
        assert sla["signal"] in ("VERDE", "AMARILLO", "ROJO")
        assert "compliance_pct" in sla
        assert 0 <= sla["compliance_pct"] <= 100


@pytest.mark.asyncio
async def test_sla_dashboard_requires_admin(client, regional_token):
    """Non-admin cannot access SLA dashboard."""
    resp = await client.get("/api/admin/slas/dashboard", headers=auth(regional_token))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Audit trail
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_audit_list(client, admin_token):
    """GET /api/admin/audit returns paginated events with filter metadata."""
    resp = await client.get("/api/admin/audit", headers=auth(admin_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert "filters" in body
    assert "event_types" in body["filters"]
    assert "subject_types" in body["filters"]


@pytest.mark.asyncio
async def test_audit_filter_by_subject_type(client, admin_token):
    """Audit can filter by subject_type."""
    resp = await client.get(
        "/api/admin/audit?subject_type=core.ipr", headers=auth(admin_token)
    )
    assert resp.status_code == 200
    body = resp.json()
    for item in body["items"]:
        assert item["subject_type"] == "core.ipr"


@pytest.mark.asyncio
async def test_audit_requires_admin(client, regional_token):
    """Non-admin cannot access audit."""
    resp = await client.get("/api/admin/audit", headers=auth(regional_token))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Document quality
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_document_quality(client, admin_token):
    """GET /api/admin/data-quality/documents returns document metrics."""
    resp = await client.get("/api/admin/data-quality/documents", headers=auth(admin_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "total" in body
    assert "pct_type" in body
    assert "pct_url" in body
    assert "by_type" in body
    assert isinstance(body["by_type"], list)


@pytest.mark.asyncio
async def test_document_quality_requires_admin(client, regional_token):
    """Non-admin cannot access document quality."""
    resp = await client.get("/api/admin/data-quality/documents", headers=auth(regional_token))
    assert resp.status_code == 403
