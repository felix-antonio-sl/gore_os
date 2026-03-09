"""
Tests for IPR lifecycle: fibration STATUS_PHASE_FIBER, phase gates, transitions endpoint.
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


async def _create_test_ipr(
    db: AsyncSession, status_code: str = "INGRESADO", phase_code: str | None = "F0",
    mechanism: bool = False,
) -> str:
    """Create a minimal IPR with specific status + phase for lifecycle tests."""
    bip = f"LIFECYCLE-{uuid.uuid4().hex[:8].upper()}"
    status_id = await _get_status_id(db, status_code)
    phase_id = await _get_phase_id(db, phase_code) if phase_code else None

    # Optionally assign a mechanism
    mechanism_id = None
    if mechanism:
        mech = (await db.execute(
            text("SELECT id FROM ref.category WHERE scheme = 'mechanism' LIMIT 1"),
        )).scalar()
        mechanism_id = str(mech) if mech else None

    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, status_id, mcd_phase_id,
                mechanism_id, created_at, updated_at
            ) VALUES (
                :bip, 'Test Lifecycle IPR', 'PROYECTO', CAST(:status_id AS uuid),
                CAST(:phase_id AS uuid), CAST(:mechanism_id AS uuid), NOW(), NOW()
            )
            RETURNING id
        """),
        {"bip": bip, "status_id": status_id, "phase_id": phase_id, "mechanism_id": mechanism_id},
    )).mappings().first()
    await db.commit()
    return str(row["id"])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

async def test_transition_updates_phase(client: AsyncClient, regional_token: str, db: AsyncSession):
    """INGRESADO(F0) → EN_REVISION(F1) should auto-set mcd_phase to F1."""
    # Create IPR in INGRESADO with mechanism (needed for F0→F1 gate)
    ipr_id = await _create_test_ipr(db, "INGRESADO", "F0", mechanism=True)

    target_status_id = await _get_status_id(db, "EN_REVISION")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_status_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200

    # Verify phase was auto-updated
    row = (await db.execute(
        text("""
            SELECT mcd.code AS phase FROM core.ipr i
            JOIN ref.category mcd ON mcd.id = i.mcd_phase_id
            WHERE i.id = CAST(:id AS uuid)
        """),
        {"id": ipr_id},
    )).mappings().first()
    assert row is not None
    assert row["phase"] == "F1"


async def test_phase_gate_f0_f1_mechanism(client: AsyncClient, regional_token: str, db: AsyncSession):
    """F0→F1 gate: blocks when mechanism_id is NULL."""
    # Create IPR in INGRESADO without mechanism
    ipr_id = await _create_test_ipr(db, "INGRESADO", "F0", mechanism=False)

    target_status_id = await _get_status_id(db, "EN_REVISION")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_status_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409
    assert "mechanism" in resp.json()["detail"].lower() or "mecanismo" in resp.json()["detail"].lower()


async def test_phase_gate_f4_f5_renditions(client: AsyncClient, regional_token: str, db: AsyncSession):
    """F4→F5 gate: blocks when there are non-terminal renditions."""
    ipr_id = await _create_test_ipr(db, "EN_EJECUCION", "F4")

    # Create a pending rendition linked to this IPR
    pending_state_id = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'PENDIENTE'"),
    )).scalar()

    if pending_state_id:
        await db.execute(
            text("""
                INSERT INTO core.rendition (ipr_id, state_id, created_at, updated_at)
                VALUES (CAST(:ipr_id AS uuid), CAST(:state_id AS uuid), NOW(), NOW())
            """),
            {"ipr_id": ipr_id, "state_id": str(pending_state_id)},
        )
        await db.commit()

        target_status_id = await _get_status_id(db, "EN_RENDICION")
        resp = await client.patch(
            f"/api/ipr/{ipr_id}",
            json={"status_id": target_status_id},
            headers=auth(regional_token),
        )
        assert resp.status_code == 409
        assert "rendicion" in resp.json()["detail"].lower()
    else:
        pytest.skip("rendition_state PENDIENTE not found in test DB")


async def test_anulado_preserves_phase(client: AsyncClient, regional_token: str, db: AsyncSession):
    """ANULADO should preserve the existing mcd_phase (no gate evaluation)."""
    # EN_REVISION has valid_transitions including... let's check.
    # Actually INGRESADO has ["EN_REVISION", "ANULADO"] — so we use INGRESADO with mechanism
    ipr_id = await _create_test_ipr(db, "INGRESADO", "F0", mechanism=True)

    target_status_id = await _get_status_id(db, "ANULADO")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_status_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200

    # Phase should still be F0
    row = (await db.execute(
        text("""
            SELECT mcd.code AS phase FROM core.ipr i
            LEFT JOIN ref.category mcd ON mcd.id = i.mcd_phase_id
            WHERE i.id = CAST(:id AS uuid)
        """),
        {"id": ipr_id},
    )).mappings().first()
    assert row is not None
    assert row["phase"] == "F0"


async def test_transition_same_phase_no_gate(client: AsyncClient, regional_token: str, db: AsyncSession):
    """Intra-fiber transition (e.g. EN_REVISION→PRE_ADMISIBLE, both F1) should not evaluate gates."""
    # Create IPR in EN_REVISION (F1) with mechanism
    ipr_id = await _create_test_ipr(db, "EN_REVISION", "F1", mechanism=True)

    target_status_id = await _get_status_id(db, "PRE_ADMISIBLE")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_status_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200

    # Phase should remain F1
    row = (await db.execute(
        text("""
            SELECT mcd.code AS phase FROM core.ipr i
            LEFT JOIN ref.category mcd ON mcd.id = i.mcd_phase_id
            WHERE i.id = CAST(:id AS uuid)
        """),
        {"id": ipr_id},
    )).mappings().first()
    assert row is not None
    assert row["phase"] == "F1"


async def test_transitions_endpoint_returns_gates(client: AsyncClient, regional_token: str, db: AsyncSession):
    """GET /api/ipr/{id}/transiciones returns gate status for phase boundary crossings."""
    # INGRESADO without mechanism — should show F0→F1 gate as not met
    ipr_id = await _create_test_ipr(db, "INGRESADO", "F0", mechanism=False)

    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # at least EN_REVISION

    # Find EN_REVISION transition
    en_rev = next((t for t in data if t["code"] == "EN_REVISION"), None)
    assert en_rev is not None
    assert en_rev["phase_change"] is True
    assert en_rev["target_phase"] == "F1"
    assert en_rev["blocked"] is True
    assert len(en_rev["gates"]) >= 1
    assert en_rev["gates"][0]["name"] == "mechanism_required"
    assert en_rev["gates"][0]["met"] is False

    # ANULADO should not be blocked
    anulado = next((t for t in data if t["code"] == "ANULADO"), None)
    assert anulado is not None
    assert anulado["phase_change"] is False
    assert anulado["blocked"] is False
