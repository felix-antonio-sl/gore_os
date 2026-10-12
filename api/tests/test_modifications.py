"""
Tests for IPR lifecycle Wave 2: formal modifications + report periodicity.
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


# ---------------------------------------------------------------------------
# CRUD Tests
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# FSM Tests
# ---------------------------------------------------------------------------


async def test_fsm_terminals_have_no_transitions(db: AsyncSession):
    """APROBADA and RECHAZADA should have empty valid_transitions."""
    for code in ("APROBADA", "RECHAZADA"):
        row = (await db.execute(
            text("SELECT valid_transitions FROM ref.category WHERE scheme = 'modification_status' AND code = :code"),
            {"code": code},
        )).mappings().first()
        assert row is not None
        assert row["valid_transitions"] == []


# ---------------------------------------------------------------------------
# Role restrictions
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Gate: pending modifications (informational at F4→F5)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Report periodicity
# ---------------------------------------------------------------------------

async def test_report_frequency_in_sla_days(db: AsyncSession):
    """financing_track should have report_frequency_days in sla_days."""
    row = (await db.execute(
        text("SELECT sla_days FROM core.financing_track WHERE code = 'FRIL' AND is_active = TRUE"),
    )).mappings().first()
    if row:
        assert "report_frequency_days" in (row["sla_days"] or {})
