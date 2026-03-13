"""Tests for IPR list endpoint filters."""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_division_id(db: AsyncSession) -> str:
    """Get first DIVISION org id from catalog."""
    row = (await db.execute(
        text("""
            SELECT o.id FROM core.organization o
            JOIN ref.category c ON o.org_type_id = c.id
            WHERE c.code = 'DIVISION' AND o.deleted_at IS NULL
            LIMIT 1
        """)
    )).mappings().first()
    assert row, "No DIVISION organization found in test DB"
    return str(row["id"])


async def _create_ipr_with_division(db: AsyncSession, division_id: str) -> str:
    """Create a minimal IPR assigned to a specific sponsor division."""
    bip = f"DIVF-{uuid.uuid4().hex[:8].upper()}"
    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, sponsor_division_id,
                created_at, updated_at
            ) VALUES (
                :bip, 'Test Division Filter IPR', 'PROYECTO',
                CAST(:div_id AS uuid), NOW(), NOW()
            )
            RETURNING id
        """),
        {"bip": bip, "div_id": division_id},
    )).mappings().first()
    await db.commit()
    return str(row["id"])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

async def test_list_iprs_division_filter(
    client: AsyncClient, admin_token: str, db: AsyncSession
):
    """GET /api/ipr?sponsor_division_id=<uuid> filters by sponsor division."""
    # Get a division ID
    division_id = await _get_division_id(db)

    # Create an IPR with that division
    ipr_id = await _create_ipr_with_division(db, division_id)

    # Query with division filter
    resp = await client.get(
        "/api/ipr",
        params={"sponsor_division_id": division_id, "page_size": 100},
        headers=auth(admin_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1

    # All returned items should belong to the filtered division
    # Verify our created IPR is in the results
    ids = [item["id"] for item in data["items"]]
    assert ipr_id in ids

    # Cleanup
    await db.execute(
        text("DELETE FROM core.ipr WHERE id = CAST(:id AS uuid)"),
        {"id": ipr_id},
    )
    await db.commit()


async def test_list_iprs_division_filter_excludes_other(
    client: AsyncClient, admin_token: str, db: AsyncSession
):
    """Division filter should NOT return IPRs from other divisions."""
    # Get two different divisions
    rows = (await db.execute(
        text("""
            SELECT o.id FROM core.organization o
            JOIN ref.category c ON o.org_type_id = c.id
            WHERE c.code = 'DIVISION' AND o.deleted_at IS NULL
            ORDER BY o.name
            LIMIT 2
        """)
    )).mappings().all()
    assert len(rows) >= 2, "Need at least 2 DIVISION orgs for exclusion test"
    div_a = str(rows[0]["id"])
    div_b = str(rows[1]["id"])

    # Create IPR in division A
    ipr_id = await _create_ipr_with_division(db, div_a)

    # Query filtering by division B — should NOT include our IPR
    resp = await client.get(
        "/api/ipr",
        params={"sponsor_division_id": div_b, "page_size": 100},
        headers=auth(admin_token),
    )
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()["items"]]
    assert ipr_id not in ids

    # Cleanup
    await db.execute(
        text("DELETE FROM core.ipr WHERE id = CAST(:id AS uuid)"),
        {"id": ipr_id},
    )
    await db.commit()
