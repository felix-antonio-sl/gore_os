"""
Tests for IPR lifecycle Wave 3: closure records + ex-post evaluations + F5 states.
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
# F5 States
# ---------------------------------------------------------------------------

async def test_rendicion_aprobada_state_exists(db: AsyncSession):
    """RENDICION_APROBADA state should exist."""
    sid = await _get_cat_id(db, "ipr_state", "RENDICION_APROBADA")
    assert sid is not None


async def test_en_cierre_administrativo_state_exists(db: AsyncSession):
    """EN_CIERRE_ADMINISTRATIVO state should exist."""
    sid = await _get_cat_id(db, "ipr_state", "EN_CIERRE_ADMINISTRATIVO")
    assert sid is not None


# ---------------------------------------------------------------------------
# Closure CRUD
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Closure Gate: EN_CIERRE_ADMINISTRATIVO → CERRADO
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Ex-Post Evaluations
# ---------------------------------------------------------------------------
