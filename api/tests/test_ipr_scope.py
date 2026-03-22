"""Tests for IPR IDOR scope checks (Sprint 2 Security — WP-A)."""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth

pytestmark = pytest.mark.asyncio

# Unique prefix for cleanup
_PREFIX = "SCOPE-"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_user_info(db: AsyncSession, email: str) -> dict:
    """Get user id and division_id."""
    row = (await db.execute(
        text('SELECT id, division_id FROM core."user" WHERE email = :e'),
        {"e": email},
    )).mappings().first()
    assert row, f"User {email} not found"
    return {"id": str(row["id"]), "division_id": str(row["division_id"]) if row["division_id"] else None}


async def _get_other_division_id(db: AsyncSession, exclude_div_id: str) -> str:
    """Get a division ID different from the given one."""
    row = (await db.execute(
        text("""
            SELECT o.id FROM core.organization o
            JOIN ref.category c ON o.org_type_id = c.id
            WHERE c.code = 'DIVISION' AND o.deleted_at IS NULL
              AND o.id != CAST(:exclude AS uuid)
            LIMIT 1
        """),
        {"exclude": exclude_div_id},
    )).mappings().first()
    assert row, "Need at least 2 divisions"
    return str(row["id"])


async def _create_scoped_ipr(
    db: AsyncSession,
    sponsor_division_id: str,
    assignee_id: str | None = None,
) -> str:
    """Create a minimal IPR for scope testing."""
    bip = f"{_PREFIX}{uuid.uuid4().hex[:8].upper()}"
    params: dict = {"bip": bip, "div_id": sponsor_division_id}

    assignee_clause = "NULL"
    if assignee_id:
        assignee_clause = "CAST(:assignee_id AS uuid)"
        params["assignee_id"] = assignee_id

    row = (await db.execute(
        text(f"""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, sponsor_division_id,
                assignee_id, created_at, updated_at
            ) VALUES (
                :bip, 'Test Scope IPR', 'PROYECTO',
                CAST(:div_id AS uuid), {assignee_clause}, NOW(), NOW()
            )
            RETURNING id
        """),
        params,
    )).mappings().first()
    await db.commit()
    return str(row["id"])


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
async def cleanup_scope_iprs(db: AsyncSession):
    """Remove scope test IPRs after each test."""
    yield
    await db.execute(
        text("DELETE FROM core.ipr WHERE codigo_bip LIKE :prefix"),
        {"prefix": f"{_PREFIX}%"},
    )
    await db.commit()


# ---------------------------------------------------------------------------
# 1. Admin can read any IPR
# ---------------------------------------------------------------------------

async def test_admin_can_read_any_ipr(
    client: AsyncClient, admin_token: str, db: AsyncSession
):
    """ADMIN_SISTEMA has global scope — can read any IPR."""
    info = await _get_user_info(db, "analista.dipir@goreos.cl")
    div_id = info["division_id"] or (await _get_other_division_id(db, ""))
    ipr_id = await _create_scoped_ipr(db, div_id)

    resp = await client.get(f"/api/ipr/{ipr_id}", headers=auth(admin_token))
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 2. DGI can read any IPR
# ---------------------------------------------------------------------------

async def test_dgi_can_read_any_ipr(
    client: AsyncClient, dgi_token: str, db: AsyncSession
):
    """JEFE_DGI has global scope — can read any IPR."""
    info = await _get_user_info(db, "jefe.daf@goreos.cl")
    div_id = info["division_id"]
    ipr_id = await _create_scoped_ipr(db, div_id)

    resp = await client.get(f"/api/ipr/{ipr_id}", headers=auth(dgi_token))
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 3. Analista cannot read unassigned IPR
# ---------------------------------------------------------------------------

async def test_analista_cannot_read_unassigned_ipr(
    client: AsyncClient, analista_token: str, admin_token: str, db: AsyncSession
):
    """ANALISTA (personal scope) blocked from IPR not assigned to them."""
    admin_info = await _get_user_info(db, "admin@goreos.cl")
    # Use any division
    row = (await db.execute(
        text("""
            SELECT o.id FROM core.organization o
            JOIN ref.category c ON o.org_type_id = c.id
            WHERE c.code = 'DIVISION' AND o.deleted_at IS NULL LIMIT 1
        """)
    )).mappings().first()
    div_id = str(row["id"])

    # Create IPR with admin as assignee — analista should be denied
    ipr_id = await _create_scoped_ipr(db, div_id, assignee_id=admin_info["id"])

    resp = await client.get(f"/api/ipr/{ipr_id}", headers=auth(analista_token))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 4. Analista can read own IPR
# ---------------------------------------------------------------------------

async def test_analista_can_read_own_ipr(
    client: AsyncClient, analista_token: str, db: AsyncSession
):
    """ANALISTA can read IPR assigned to them."""
    analista_info = await _get_user_info(db, "analista.dipir@goreos.cl")
    div_id = analista_info["division_id"]
    ipr_id = await _create_scoped_ipr(db, div_id, assignee_id=analista_info["id"])

    resp = await client.get(f"/api/ipr/{ipr_id}", headers=auth(analista_token))
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 5. Jefe can read division IPR
# ---------------------------------------------------------------------------

async def test_jefe_can_read_division_ipr(
    client: AsyncClient, jefe_token: str, db: AsyncSession
):
    """JEFE_DIVISION can read IPR in their division."""
    jefe_info = await _get_user_info(db, "jefe.daf@goreos.cl")
    div_id = jefe_info["division_id"]
    assert div_id, "jefe.daf must have division_id"
    ipr_id = await _create_scoped_ipr(db, div_id)

    resp = await client.get(f"/api/ipr/{ipr_id}", headers=auth(jefe_token))
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 6. Jefe cannot read other division IPR
# ---------------------------------------------------------------------------

async def test_jefe_cannot_read_other_division_ipr(
    client: AsyncClient, jefe_token: str, db: AsyncSession
):
    """JEFE_DIVISION blocked from IPR in a different division."""
    jefe_info = await _get_user_info(db, "jefe.daf@goreos.cl")
    other_div = await _get_other_division_id(db, jefe_info["division_id"])
    ipr_id = await _create_scoped_ipr(db, other_div)

    resp = await client.get(f"/api/ipr/{ipr_id}", headers=auth(jefe_token))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 7. Scope applies to satellite endpoints
# ---------------------------------------------------------------------------

async def test_scope_applies_to_satellite(
    client: AsyncClient, analista_token: str, db: AsyncSession
):
    """ANALISTA blocked from satellite endpoint on unassigned IPR."""
    admin_info = await _get_user_info(db, "admin@goreos.cl")
    row = (await db.execute(
        text("""
            SELECT o.id FROM core.organization o
            JOIN ref.category c ON o.org_type_id = c.id
            WHERE c.code = 'DIVISION' AND o.deleted_at IS NULL LIMIT 1
        """)
    )).mappings().first()
    div_id = str(row["id"])

    ipr_id = await _create_scoped_ipr(db, div_id, assignee_id=admin_info["id"])

    resp = await client.get(f"/api/ipr/{ipr_id}/partes", headers=auth(analista_token))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 8. Search scoped for analista
# ---------------------------------------------------------------------------

async def test_search_scoped_for_analista(
    client: AsyncClient, analista_token: str, db: AsyncSession
):
    """Search should not return unassigned IPRs for ANALISTA."""
    admin_info = await _get_user_info(db, "admin@goreos.cl")
    row = (await db.execute(
        text("""
            SELECT o.id FROM core.organization o
            JOIN ref.category c ON o.org_type_id = c.id
            WHERE c.code = 'DIVISION' AND o.deleted_at IS NULL LIMIT 1
        """)
    )).mappings().first()
    div_id = str(row["id"])

    # Create IPR with unique name, assigned to admin
    unique_name = f"XYZSCOPE{uuid.uuid4().hex[:6]}"
    params: dict = {
        "bip": f"{_PREFIX}{uuid.uuid4().hex[:8].upper()}",
        "div_id": div_id,
        "assignee_id": admin_info["id"],
        "name": unique_name,
    }
    await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, sponsor_division_id,
                assignee_id, created_at, updated_at
            ) VALUES (
                :bip, :name, 'PROYECTO',
                CAST(:div_id AS uuid), CAST(:assignee_id AS uuid), NOW(), NOW()
            )
        """),
        params,
    )
    await db.commit()

    resp = await client.get(
        "/api/search", params={"q": unique_name}, headers=auth(analista_token)
    )
    assert resp.status_code == 200
    ipr_results = [r for r in resp.json()["results"] if r["entity_type"] == "ipr"]
    # Should not find the IPR since analista is not assigned
    assert len(ipr_results) == 0


# ---------------------------------------------------------------------------
# 9. Search unscoped for admin
# ---------------------------------------------------------------------------

async def test_search_unscoped_for_admin(
    client: AsyncClient, admin_token: str, db: AsyncSession
):
    """Admin search returns all matching IPRs regardless of assignment."""
    row = (await db.execute(
        text("""
            SELECT o.id FROM core.organization o
            JOIN ref.category c ON o.org_type_id = c.id
            WHERE c.code = 'DIVISION' AND o.deleted_at IS NULL LIMIT 1
        """)
    )).mappings().first()
    div_id = str(row["id"])

    unique_name = f"XYZADMSCOPE{uuid.uuid4().hex[:6]}"
    await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, sponsor_division_id,
                created_at, updated_at
            ) VALUES (
                :bip, :name, 'PROYECTO',
                CAST(:div_id AS uuid), NOW(), NOW()
            )
        """),
        {
            "bip": f"{_PREFIX}{uuid.uuid4().hex[:8].upper()}",
            "div_id": div_id,
            "name": unique_name,
        },
    )
    await db.commit()

    resp = await client.get(
        "/api/search", params={"q": unique_name}, headers=auth(admin_token)
    )
    assert resp.status_code == 200
    ipr_results = [r for r in resp.json()["results"] if r["entity_type"] == "ipr"]
    assert len(ipr_results) >= 1
