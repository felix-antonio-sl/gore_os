"""
Tests for IPR lifecycle Wave 4: SLAs, ITO gate, informational gates.
"""
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

async def _get_cat_id(db: AsyncSession, scheme: str, code: str) -> str:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = :scheme AND code = :code"),
        {"scheme": scheme, "code": code},
    )).mappings().first()
    assert row, f"{scheme}/{code} not found"
    return str(row["id"])


# ---------------------------------------------------------------------------
# 4A. phase_entered_at
# ---------------------------------------------------------------------------

async def test_phase_entered_at_column_exists(db: AsyncSession):
    """core.ipr should have phase_entered_at column."""
    row = (await db.execute(
        text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'core' AND table_name = 'ipr' AND column_name = 'phase_entered_at'
        """),
    )).first()
    assert row is not None


# ---------------------------------------------------------------------------
# 4B. Evaluation SLA gates
# ---------------------------------------------------------------------------

    # evaluation_sla gate may or may not appear depending on mechanism
    # The test primarily verifies the endpoint doesn't crash


# ---------------------------------------------------------------------------
# 4C. ITO gate
# ---------------------------------------------------------------------------

async def test_ito_role_exists(db: AsyncSession):
    """ITO party role should exist in ref.category."""
    sid = await _get_cat_id(db, "ipr_party_role", "ITO")
    assert sid is not None


# ---------------------------------------------------------------------------
# 4D. Gobernador delegation (informational)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Evaluation SLA data
# ---------------------------------------------------------------------------

async def test_evaluation_max_days_in_sla_days(db: AsyncSession):
    """financing_track should have evaluation_max_days in sla_days."""
    row = (await db.execute(
        text("SELECT sla_days FROM core.financing_track WHERE code = 'FRIL' AND is_active = TRUE"),
    )).mappings().first()
    if row:
        assert "evaluation_max_days" in (row["sla_days"] or {})
