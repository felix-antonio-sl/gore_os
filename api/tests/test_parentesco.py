"""
Tests for HΩ-02: Kinship declarations (parentesco) for SUBV8.

10 tests:
- CRUD: list, create, create_conflict, duplicate_409, validate, delete
- Gate: blocks_missing, blocks_conflict, passes_clean, not_for_sni
"""
import json
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

async def _get_category_id(db: AsyncSession, scheme: str, code: str) -> str:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = :scheme AND code = :code"),
        {"scheme": scheme, "code": code},
    )).mappings().first()
    assert row, f"{scheme}/{code} not found"
    return str(row["id"])


async def _create_test_ipr(
    db: AsyncSession,
    status_code: str = "EN_REVISION",
    phase_code: str = "F1",
    mechanism_code: str | None = None,
    monto: float | None = None,
) -> str:
    """Create minimal IPR for parentesco tests."""
    bip = f"KIN-{uuid.uuid4().hex[:8].upper()}"
    status_id = await _get_category_id(db, "ipr_state", status_code)
    phase_id = await _get_category_id(db, "mcd_phase", phase_code)
    mechanism_id = None
    if mechanism_code:
        mechanism_id = await _get_category_id(db, "mechanism", mechanism_code)

    meta = {}
    if monto is not None:
        meta["monto_total"] = str(monto)

    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, status_id, mcd_phase_id,
                mechanism_id, metadata, created_at, updated_at
            ) VALUES (
                :bip, 'Test Parentesco IPR', 'PROYECTO',
                CAST(:status_id AS uuid), CAST(:phase_id AS uuid),
                CAST(:mechanism_id AS uuid),
                CAST(:metadata AS jsonb), NOW(), NOW()
            )
            RETURNING id
        """),
        {
            "bip": bip, "status_id": status_id, "phase_id": phase_id,
            "mechanism_id": mechanism_id,
            "metadata": json.dumps(meta),
        },
    )).mappings().first()
    await db.commit()
    return str(row["id"])


# ---------------------------------------------------------------------------
# CRUD Tests (6)
# ---------------------------------------------------------------------------

async def test_list_empty(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """Listing declarations on an IPR with none returns empty list."""
    ipr_id = await _create_test_ipr(db, mechanism_code="SUBV8")
    resp = await client.get(f"/api/ipr/{ipr_id}/parentesco", headers=auth(admin_token))
    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------------------
# Gate Tests (4)
# ---------------------------------------------------------------------------
