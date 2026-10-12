"""
Tests for IPR lifecycle Wave 1: nature-aware bifurcation, new SSOT states,
ANULADO/TERMINADO_ANTICIPADAMENTE cross-cutting.
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

async def _get_status_id(db: AsyncSession, code: str) -> str:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'ipr_state' AND code = :code"),
        {"code": code},
    )).mappings().first()
    assert row, f"ipr_state code {code!r} not found"
    return str(row["id"])


# ---------------------------------------------------------------------------
# 1A. New SSOT states
# ---------------------------------------------------------------------------

async def test_contrato_firmado_state_exists(db: AsyncSession):
    """CONTRATO_FIRMADO state should exist in ref.category."""
    sid = await _get_status_id(db, "CONTRATO_FIRMADO")
    assert sid is not None


async def test_terminado_anticipadamente_state_exists(db: AsyncSession):
    """TERMINADO_ANTICIPADAMENTE state should exist in ref.category."""
    sid = await _get_status_id(db, "TERMINADO_ANTICIPADAMENTE")
    assert sid is not None


async def test_terminado_anticipadamente_is_terminal(db: AsyncSession):
    """TERMINADO_ANTICIPADAMENTE should have empty valid_transitions."""
    row = (await db.execute(
        text("SELECT valid_transitions FROM ref.category WHERE scheme = 'ipr_state' AND code = 'TERMINADO_ANTICIPADAMENTE'"),
    )).mappings().first()
    assert row is not None
    assert row["valid_transitions"] == []


# ---------------------------------------------------------------------------
# 1B. Bifurcation: EN_FORMALIZACION → [FORMALIZADO | EN_LICITACION]
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 1B. PROYECTO full flow: ADJUDICADO → CONTRATO_FIRMADO → EN_OBRA
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 1C. TERMINADO_ANTICIPADAMENTE cross-cutting
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 1C. ANULADO universal
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 1D. /transiciones endpoint reflects nature-aware filtering
# ---------------------------------------------------------------------------
