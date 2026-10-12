"""
Tests for IPR lifecycle Wave 5: role-based transition permissions.
Pullback categórico: Permission = Phase_Boundary ×_Track Role.
"""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from tests.conftest import auth

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 5A. Boundary key mapping unit tests (via transitions endpoint)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 5B. Role-based transition blocking (PATCH endpoint)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 5C. Roles without transition authority are blocked at endpoint level
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 5D. Track overrides (FRIL-specific)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 5E. JEFE_DIVISION status_id update (was previously blocked, now boundary-controlled)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 5F. New gates
# ---------------------------------------------------------------------------

async def test_supervisor_gore_party_role_exists(db: AsyncSession):
    """SUPERVISOR_GORE party role should exist in ref.category."""
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'SUPERVISOR_GORE'"),
    )).mappings().first()
    assert row is not None


async def test_fril_role_permissions_seeded(db: AsyncSession):
    """FRIL financing_track should have non-empty role_permissions."""
    row = (await db.execute(
        text("SELECT role_permissions FROM core.financing_track WHERE code = 'FRIL'"),
    )).mappings().first()
    assert row is not None
    perms = row["role_permissions"]
    assert isinstance(perms, dict)
    assert "register_eval_result" in perms
    assert "JEFE_DIVISION" in perms["register_eval_result"]


async def test_fril_vigencia_90d_in_sla_days(db: AsyncSession):
    """FRIL should have rs_validity_days=90 in sla_days."""
    row = (await db.execute(
        text("SELECT sla_days FROM core.financing_track WHERE code = 'FRIL'"),
    )).mappings().first()
    assert row is not None
    assert row["sla_days"].get("rs_validity_days") == 90
