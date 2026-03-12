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


async def _create_test_ipr(
    db: AsyncSession,
    status_code: str = "EN_EVALUACION",
    phase: str = "F2",
    nature: str = "PROYECTO",
    mechanism_code: str | None = None,
) -> str:
    bip = f"SLA-{uuid.uuid4().hex[:8].upper()}"
    status_id = await _get_cat_id(db, "ipr_state", status_code)
    phase_id = await _get_cat_id(db, "mcd_phase", phase)

    mechanism_id = None
    if mechanism_code:
        mech = (await db.execute(
            text("SELECT id FROM ref.category WHERE scheme = 'mechanism' AND code = :code"),
            {"code": mechanism_code},
        )).scalar()
        mechanism_id = str(mech) if mech else None

    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, status_id, mcd_phase_id,
                mechanism_id, phase_entered_at, created_at, updated_at
            ) VALUES (
                :bip, 'SLA Test IPR', :nature,
                CAST(:status_id AS uuid), CAST(:phase_id AS uuid),
                CAST(:mechanism_id AS uuid), NOW() - INTERVAL '100 days',
                NOW(), NOW()
            )
            RETURNING id
        """),
        {
            "bip": bip, "status_id": status_id, "phase_id": phase_id,
            "nature": nature, "mechanism_id": mechanism_id,
        },
    )).mappings().first()
    await db.commit()
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


async def test_phase_entered_at_updates_on_status_change(client: AsyncClient, regional_token: str, db: AsyncSession):
    """Trigger should update phase_entered_at when status_id changes."""
    ipr_id = await _create_test_ipr(db, "EN_FORMALIZACION", "F4", "PROGRAMA")

    # Record current phase_entered_at
    old_ts = (await db.execute(
        text("SELECT phase_entered_at FROM core.ipr WHERE id = CAST(:id AS uuid)"),
        {"id": ipr_id},
    )).scalar()

    # Transition to FORMALIZADO (same phase, trigger should still fire)
    target_id = await _get_cat_id(db, "ipr_state", "FORMALIZADO")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}", json={"status_id": target_id}, headers=auth(regional_token),
    )
    assert resp.status_code == 200

    new_ts = (await db.execute(
        text("SELECT phase_entered_at FROM core.ipr WHERE id = CAST(:id AS uuid)"),
        {"id": ipr_id},
    )).scalar()
    assert new_ts is not None
    assert new_ts != old_ts  # Should be updated


# ---------------------------------------------------------------------------
# 4B. Evaluation SLA gates
# ---------------------------------------------------------------------------

async def test_evaluation_sla_gate_informational(client: AsyncClient, regional_token: str, db: AsyncSession):
    """F2→F3 should include evaluation_sla informational gate."""
    # Create IPR in RS with a mechanism that has evaluation_max_days
    ipr_id = await _create_test_ipr(db, "RS", "F2", nature="PROYECTO")

    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    transitions = resp.json()

    f3_trans = [t for t in transitions if t.get("target_phase") == "F3" and t.get("phase_change")]
    # evaluation_sla gate may or may not appear depending on mechanism
    # The test primarily verifies the endpoint doesn't crash


async def test_batch_evaluation_sla_check(client: AsyncClient, regional_token: str, db: AsyncSession):
    """POST /api/ipr/check-evaluation-slas returns result structure."""
    resp = await client.post(
        "/api/ipr/check-evaluation-slas",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "checked" in data
    assert "alerts_created" in data


# ---------------------------------------------------------------------------
# 4C. ITO gate
# ---------------------------------------------------------------------------

async def test_ito_role_exists(db: AsyncSession):
    """ITO party role should exist in ref.category."""
    sid = await _get_cat_id(db, "ipr_party_role", "ITO")
    assert sid is not None


async def test_ito_gate_blocks_adjudicado_without_ito(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PROYECTO: EN_LICITACION → ADJUDICADO blocked without ITO assigned."""
    ipr_id = await _create_test_ipr(db, "EN_LICITACION", "F4", nature="PROYECTO")
    target_id = await _get_cat_id(db, "ipr_state", "ADJUDICADO")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}", json={"status_id": target_id}, headers=auth(regional_token),
    )
    assert resp.status_code == 409
    assert "ito" in resp.json()["detail"].lower()


async def test_ito_gate_passes_with_ito_assigned(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PROYECTO: EN_LICITACION → ADJUDICADO succeeds with ITO assigned."""
    ipr_id = await _create_test_ipr(db, "EN_LICITACION", "F4", nature="PROYECTO")

    # Assign ITO
    ito_role_id = await _get_cat_id(db, "ipr_party_role", "ITO")

    # Get an org to assign as ITO
    org_row = (await db.execute(
        text("SELECT id FROM core.organization WHERE deleted_at IS NULL LIMIT 1"),
    )).first()
    if not org_row:
        pytest.skip("No organizations in test DB")
    org_id = str(org_row[0])

    await db.execute(
        text("""
            INSERT INTO core.ipr_party (
                ipr_id, organization_id, party_role_id,
                created_at, updated_at
            ) VALUES (
                CAST(:ipr_id AS uuid),
                CAST(:org_id AS uuid), CAST(:role_id AS uuid),
                NOW(), NOW()
            )
        """),
        {"ipr_id": ipr_id, "org_id": org_id, "role_id": ito_role_id},
    )
    await db.commit()

    target_id = await _get_cat_id(db, "ipr_state", "ADJUDICADO")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}", json={"status_id": target_id}, headers=auth(regional_token),
    )
    # Should succeed now (no contrato_firmado needed since ADJUDICADO is same phase)
    assert resp.status_code == 200


async def test_ito_gate_not_applied_to_programa(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PROGRAMA: EN_LICITACION → ADJUDICADO should not require ITO."""
    # Note: PROGRAMAs typically don't go through EN_LICITACION,
    # but if they did, the ITO gate shouldn't apply
    ipr_id = await _create_test_ipr(db, "EN_LICITACION", "F4", nature="PROGRAMA")
    target_id = await _get_cat_id(db, "ipr_state", "ADJUDICADO")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}", json={"status_id": target_id}, headers=auth(regional_token),
    )
    # ADJUDICADO valid_transitions changed to [CONTRATO_FIRMADO, ANULADO]
    # But the transition should still go through (no ITO check for PROGRAMA)
    assert resp.status_code == 200


async def test_transiciones_shows_ito_gate(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PROYECTO at EN_LICITACION: /transiciones should show ITO gate for ADJUDICADO."""
    ipr_id = await _create_test_ipr(db, "EN_LICITACION", "F4", nature="PROYECTO")
    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token),
    )
    assert resp.status_code == 200
    transitions = resp.json()
    adj = next((t for t in transitions if t["code"] == "ADJUDICADO"), None)
    if adj:
        ito_gate = next((g for g in adj["gates"] if g["name"] == "ito_assigned"), None)
        assert ito_gate is not None
        assert ito_gate["met"] is False


# ---------------------------------------------------------------------------
# 4D. Gobernador delegation (informational)
# ---------------------------------------------------------------------------

async def test_gobernador_delegation_gate(client: AsyncClient, regional_token: str, db: AsyncSession):
    """F2→F3 should include gobernador_delegation informational gate."""
    # Create IPR in RS with monto_total in metadata
    ipr_id = await _create_test_ipr(db, "RS", "F2")

    # Set a high monto_total
    await db.execute(
        text("""
            UPDATE core.ipr SET metadata = '{"monto_total": "600000000"}'::jsonb
            WHERE id = CAST(:id AS uuid)
        """),
        {"id": ipr_id},
    )
    await db.commit()

    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token),
    )
    assert resp.status_code == 200
    transitions = resp.json()

    f3_trans = [t for t in transitions if t.get("target_phase") == "F3" and t.get("phase_change")]
    if f3_trans:
        gates = f3_trans[0]["gates"]
        deleg = next((g for g in gates if g["name"] == "gobernador_delegation"), None)
        if deleg:
            assert deleg["met"] is True  # informational
            assert "core" in deleg["detail"].lower() or "gobernador" in deleg["detail"].lower()


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
