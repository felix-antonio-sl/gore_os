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


async def _get_phase_id(db: AsyncSession, code: str) -> str:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'mcd_phase' AND code = :code"),
        {"code": code},
    )).mappings().first()
    assert row, f"mcd_phase code {code!r} not found"
    return str(row["id"])


async def _create_ipr(
    db: AsyncSession,
    status_code: str,
    phase_code: str,
    nature: str = "PROYECTO",
) -> str:
    """Create a minimal IPR for lifecycle bifurcation tests."""
    bip = f"BIF-{uuid.uuid4().hex[:8].upper()}"
    status_id = await _get_status_id(db, status_code)
    phase_id = await _get_phase_id(db, phase_code)

    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, status_id, mcd_phase_id,
                created_at, updated_at
            ) VALUES (
                :bip, 'Bifurcation Test IPR', :nature,
                CAST(:status_id AS uuid), CAST(:phase_id AS uuid),
                NOW(), NOW()
            )
            RETURNING id
        """),
        {"bip": bip, "status_id": status_id, "phase_id": phase_id, "nature": nature},
    )).mappings().first()
    await db.commit()
    return str(row["id"])


async def _transition(client: AsyncClient, ipr_id: str, target_code: str, token: str, db: AsyncSession) -> int:
    """Attempt an IPR transition, return status code."""
    target_id = await _get_status_id(db, target_code)
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_id},
        headers=auth(token),
    )
    return resp.status_code


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

async def test_proyecto_en_formalizacion_to_en_licitacion(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PROYECTO: EN_FORMALIZACION → EN_LICITACION should succeed."""
    ipr_id = await _create_ipr(db, "EN_FORMALIZACION", "F4", nature="PROYECTO")
    code = await _transition(client, ipr_id, "EN_LICITACION", regional_token, db)
    assert code == 200


async def test_programa_en_formalizacion_to_en_licitacion_blocked(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PROGRAMA: EN_FORMALIZACION → EN_LICITACION should be blocked (409)."""
    ipr_id = await _create_ipr(db, "EN_FORMALIZACION", "F4", nature="PROGRAMA")
    code = await _transition(client, ipr_id, "EN_LICITACION", regional_token, db)
    assert code == 409


async def test_programa_en_formalizacion_to_formalizado(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PROGRAMA: EN_FORMALIZACION → FORMALIZADO should succeed."""
    ipr_id = await _create_ipr(db, "EN_FORMALIZACION", "F4", nature="PROGRAMA")
    code = await _transition(client, ipr_id, "FORMALIZADO", regional_token, db)
    assert code == 200


async def test_proyecto_formalizado_to_en_ejecucion_blocked(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PROYECTO: FORMALIZADO → EN_EJECUCION should be blocked (409)."""
    ipr_id = await _create_ipr(db, "FORMALIZADO", "F4", nature="PROYECTO")
    code = await _transition(client, ipr_id, "EN_EJECUCION", regional_token, db)
    assert code == 409


async def test_programa_formalizado_to_en_ejecucion(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PROGRAMA: FORMALIZADO → EN_EJECUCION should succeed."""
    ipr_id = await _create_ipr(db, "FORMALIZADO", "F4", nature="PROGRAMA")
    code = await _transition(client, ipr_id, "EN_EJECUCION", regional_token, db)
    assert code == 200


# ---------------------------------------------------------------------------
# 1B. PROYECTO full flow: ADJUDICADO → CONTRATO_FIRMADO → EN_OBRA
# ---------------------------------------------------------------------------

async def test_proyecto_adjudicado_to_contrato_firmado(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PROYECTO: ADJUDICADO → CONTRATO_FIRMADO should succeed."""
    ipr_id = await _create_ipr(db, "ADJUDICADO", "F4", nature="PROYECTO")
    code = await _transition(client, ipr_id, "CONTRATO_FIRMADO", regional_token, db)
    assert code == 200


async def test_proyecto_contrato_firmado_to_en_obra(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PROYECTO: CONTRATO_FIRMADO → EN_OBRA should succeed."""
    ipr_id = await _create_ipr(db, "CONTRATO_FIRMADO", "F4", nature="PROYECTO")
    code = await _transition(client, ipr_id, "EN_OBRA", regional_token, db)
    assert code == 200


async def test_proyecto_adjudicado_to_en_obra_blocked(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PROYECTO: ADJUDICADO → EN_OBRA should be blocked (CONTRATO_FIRMADO required)."""
    ipr_id = await _create_ipr(db, "ADJUDICADO", "F4", nature="PROYECTO")
    # ADJUDICADO valid_transitions = [CONTRATO_FIRMADO, ANULADO] — EN_OBRA not in list
    target_id = await _get_status_id(db, "EN_OBRA")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_id},
        headers=auth(regional_token),
    )
    # API or DB trigger should reject invalid transition
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# 1C. TERMINADO_ANTICIPADAMENTE cross-cutting
# ---------------------------------------------------------------------------

async def test_en_ejecucion_to_terminado_anticipadamente(client: AsyncClient, regional_token: str, db: AsyncSession):
    """EN_EJECUCION → TERMINADO_ANTICIPADAMENTE should succeed."""
    ipr_id = await _create_ipr(db, "EN_EJECUCION", "F4", nature="PROGRAMA")
    code = await _transition(client, ipr_id, "TERMINADO_ANTICIPADAMENTE", regional_token, db)
    assert code == 200


async def test_en_obra_to_terminado_anticipadamente(client: AsyncClient, regional_token: str, db: AsyncSession):
    """EN_OBRA → TERMINADO_ANTICIPADAMENTE should succeed."""
    ipr_id = await _create_ipr(db, "EN_OBRA", "F4", nature="PROYECTO")
    code = await _transition(client, ipr_id, "TERMINADO_ANTICIPADAMENTE", regional_token, db)
    assert code == 200


async def test_contrato_firmado_to_terminado_anticipadamente(client: AsyncClient, regional_token: str, db: AsyncSession):
    """CONTRATO_FIRMADO → TERMINADO_ANTICIPADAMENTE should succeed."""
    ipr_id = await _create_ipr(db, "CONTRATO_FIRMADO", "F4", nature="PROYECTO")
    code = await _transition(client, ipr_id, "TERMINADO_ANTICIPADAMENTE", regional_token, db)
    assert code == 200


async def test_suspendido_to_terminado_anticipadamente(client: AsyncClient, regional_token: str, db: AsyncSession):
    """SUSPENDIDO → TERMINADO_ANTICIPADAMENTE should succeed."""
    ipr_id = await _create_ipr(db, "SUSPENDIDO", "F4", nature="PROYECTO")
    code = await _transition(client, ipr_id, "TERMINADO_ANTICIPADAMENTE", regional_token, db)
    assert code == 200


async def test_terminado_anticipadamente_preserves_phase(client: AsyncClient, regional_token: str, db: AsyncSession):
    """TERMINADO_ANTICIPADAMENTE should preserve the existing mcd_phase."""
    ipr_id = await _create_ipr(db, "EN_EJECUCION", "F4", nature="PROGRAMA")
    await _transition(client, ipr_id, "TERMINADO_ANTICIPADAMENTE", regional_token, db)

    row = (await db.execute(
        text("""
            SELECT mcd.code AS phase FROM core.ipr i
            LEFT JOIN ref.category mcd ON mcd.id = i.mcd_phase_id
            WHERE i.id = CAST(:id AS uuid)
        """),
        {"id": ipr_id},
    )).mappings().first()
    assert row is not None
    assert row["phase"] == "F4"


# ---------------------------------------------------------------------------
# 1C. ANULADO universal
# ---------------------------------------------------------------------------

async def test_en_evaluacion_to_anulado(client: AsyncClient, regional_token: str, db: AsyncSession):
    """EN_EVALUACION → ANULADO should succeed (new transition)."""
    ipr_id = await _create_ipr(db, "EN_EVALUACION", "F2")
    code = await _transition(client, ipr_id, "ANULADO", regional_token, db)
    assert code == 200


async def test_cdp_emitido_to_anulado(client: AsyncClient, regional_token: str, db: AsyncSession):
    """CDP_EMITIDO → ANULADO should succeed (new transition)."""
    ipr_id = await _create_ipr(db, "CDP_EMITIDO", "F3")
    code = await _transition(client, ipr_id, "ANULADO", regional_token, db)
    assert code == 200


async def test_en_formalizacion_to_anulado(client: AsyncClient, regional_token: str, db: AsyncSession):
    """EN_FORMALIZACION → ANULADO should succeed."""
    ipr_id = await _create_ipr(db, "EN_FORMALIZACION", "F4")
    code = await _transition(client, ipr_id, "ANULADO", regional_token, db)
    assert code == 200


# ---------------------------------------------------------------------------
# 1D. /transiciones endpoint reflects nature-aware filtering
# ---------------------------------------------------------------------------

async def test_transiciones_proyecto_en_formalizacion(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PROYECTO at EN_FORMALIZACION: /transiciones should show EN_LICITACION, not FORMALIZADO."""
    ipr_id = await _create_ipr(db, "EN_FORMALIZACION", "F4", nature="PROYECTO")
    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    codes = [t["code"] for t in resp.json()]
    assert "EN_LICITACION" in codes
    assert "FORMALIZADO" not in codes
    assert "ANULADO" in codes


async def test_transiciones_programa_en_formalizacion(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PROGRAMA at EN_FORMALIZACION: /transiciones should show FORMALIZADO, not EN_LICITACION."""
    ipr_id = await _create_ipr(db, "EN_FORMALIZACION", "F4", nature="PROGRAMA")
    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    codes = [t["code"] for t in resp.json()]
    assert "FORMALIZADO" in codes
    assert "EN_LICITACION" not in codes
    assert "ANULADO" in codes


async def test_transiciones_contrato_firmado_shows_targets(client: AsyncClient, regional_token: str, db: AsyncSession):
    """CONTRATO_FIRMADO: /transiciones should show EN_OBRA, SUSPENDIDO, TERMINADO_ANTICIPADAMENTE, ANULADO."""
    ipr_id = await _create_ipr(db, "CONTRATO_FIRMADO", "F4", nature="PROYECTO")
    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    codes = [t["code"] for t in resp.json()]
    assert "EN_OBRA" in codes
    assert "TERMINADO_ANTICIPADAMENTE" in codes
    assert "ANULADO" in codes


async def test_status_phase_fiber_new_states(db: AsyncSession):
    """Verify STATUS_PHASE_FIBER includes new states."""
    from app.routers.ipr import STATUS_PHASE_FIBER
    assert STATUS_PHASE_FIBER["CONTRATO_FIRMADO"] == "F4"
    assert STATUS_PHASE_FIBER["TERMINADO_ANTICIPADAMENTE"] == "F5"
