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

async def _get_cat_id(db: AsyncSession, scheme: str, code: str) -> str:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = :scheme AND code = :code"),
        {"scheme": scheme, "code": code},
    )).mappings().first()
    assert row, f"{scheme}/{code} not found"
    return str(row["id"])


async def _create_test_ipr(db: AsyncSession, status_code: str = "EN_EJECUCION") -> str:
    bip = f"MOD-{uuid.uuid4().hex[:8].upper()}"
    status_id = await _get_cat_id(db, "ipr_state", status_code)
    phase_id = await _get_cat_id(db, "mcd_phase", "F4")
    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, status_id, mcd_phase_id,
                created_at, updated_at
            ) VALUES (
                :bip, 'Modification Test IPR', 'PROGRAMA',
                CAST(:status_id AS uuid), CAST(:phase_id AS uuid),
                NOW(), NOW()
            )
            RETURNING id
        """),
        {"bip": bip, "status_id": status_id, "phase_id": phase_id},
    )).mappings().first()
    await db.commit()
    return str(row["id"])


# ---------------------------------------------------------------------------
# CRUD Tests
# ---------------------------------------------------------------------------

async def test_create_modification(client: AsyncClient, regional_token: str, db: AsyncSession):
    """POST /api/ipr/{id}/modificaciones creates a modification with code MOD-YYYY-NNNN."""
    ipr_id = await _create_test_ipr(db)
    type_id = await _get_cat_id(db, "modification_type", "PRESUPUESTO")

    resp = await client.post(
        f"/api/ipr/{ipr_id}/modificaciones",
        json={
            "modification_type_id": type_id,
            "description": "Aumento de presupuesto por inflación",
            "amount_delta": 5000000,
        },
        headers=auth(regional_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"].startswith("MOD-")
    assert "id" in data


async def test_list_modifications(client: AsyncClient, regional_token: str, db: AsyncSession):
    """GET /api/ipr/{id}/modificaciones returns created modifications."""
    ipr_id = await _create_test_ipr(db)
    type_id = await _get_cat_id(db, "modification_type", "PLAZO")

    await client.post(
        f"/api/ipr/{ipr_id}/modificaciones",
        json={"modification_type_id": type_id, "description": "Extensión de plazo 30 días"},
        headers=auth(regional_token),
    )

    resp = await client.get(
        f"/api/ipr/{ipr_id}/modificaciones",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["status_code"] == "SOLICITADA"
    assert data[0]["modification_type_code"] == "PLAZO"


async def test_create_modification_all_types(client: AsyncClient, regional_token: str, db: AsyncSession):
    """All 5 modification types can be used."""
    ipr_id = await _create_test_ipr(db)
    for code in ("PRESUPUESTO", "PLAZO", "ALCANCE", "EJECUTOR", "TECNICO"):
        type_id = await _get_cat_id(db, "modification_type", code)
        resp = await client.post(
            f"/api/ipr/{ipr_id}/modificaciones",
            json={"modification_type_id": type_id, "description": f"Test {code}"},
            headers=auth(regional_token),
        )
        assert resp.status_code == 201, f"Failed for type {code}"


async def test_create_modification_with_field_details(client: AsyncClient, regional_token: str, db: AsyncSession):
    """Modification can include field_changed, old_value, new_value, amount_delta."""
    ipr_id = await _create_test_ipr(db)
    type_id = await _get_cat_id(db, "modification_type", "PRESUPUESTO")

    resp = await client.post(
        f"/api/ipr/{ipr_id}/modificaciones",
        json={
            "modification_type_id": type_id,
            "description": "Reajuste partida 22",
            "justification": "Inflación acumulada Q1 2026",
            "field_changed": "monto_total",
            "old_value": "100000000",
            "new_value": "115000000",
            "amount_delta": 15000000,
        },
        headers=auth(regional_token),
    )
    assert resp.status_code == 201


# ---------------------------------------------------------------------------
# FSM Tests
# ---------------------------------------------------------------------------

async def _create_mod(client: AsyncClient, ipr_id: str, token: str, db: AsyncSession) -> str:
    type_id = await _get_cat_id(db, "modification_type", "PRESUPUESTO")
    resp = await client.post(
        f"/api/ipr/{ipr_id}/modificaciones",
        json={"modification_type_id": type_id, "description": "Test mod"},
        headers=auth(token),
    )
    return resp.json()["id"]


async def test_fsm_solicitada_to_en_revision(client: AsyncClient, regional_token: str, db: AsyncSession):
    """SOLICITADA → EN_REVISION should succeed."""
    ipr_id = await _create_test_ipr(db)
    mod_id = await _create_mod(client, ipr_id, regional_token, db)
    target_id = await _get_cat_id(db, "modification_status", "EN_REVISION")

    resp = await client.patch(
        f"/api/ipr/{ipr_id}/modificaciones/{mod_id}",
        json={"status_id": target_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200


async def test_fsm_en_revision_to_aprobada(client: AsyncClient, regional_token: str, db: AsyncSession):
    """EN_REVISION → APROBADA should succeed and set approved_by."""
    ipr_id = await _create_test_ipr(db)
    mod_id = await _create_mod(client, ipr_id, regional_token, db)

    en_rev_id = await _get_cat_id(db, "modification_status", "EN_REVISION")
    await client.patch(
        f"/api/ipr/{ipr_id}/modificaciones/{mod_id}",
        json={"status_id": en_rev_id},
        headers=auth(regional_token),
    )

    aprobada_id = await _get_cat_id(db, "modification_status", "APROBADA")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}/modificaciones/{mod_id}",
        json={"status_id": aprobada_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200

    # Verify approved_by was set
    row = (await db.execute(
        text("SELECT approved_by_id, approved_at FROM core.ipr_modification WHERE id = CAST(:id AS uuid)"),
        {"id": mod_id},
    )).mappings().first()
    assert row["approved_by_id"] is not None
    assert row["approved_at"] is not None


async def test_fsm_en_revision_to_rechazada(client: AsyncClient, regional_token: str, db: AsyncSession):
    """EN_REVISION → RECHAZADA should succeed."""
    ipr_id = await _create_test_ipr(db)
    mod_id = await _create_mod(client, ipr_id, regional_token, db)

    en_rev_id = await _get_cat_id(db, "modification_status", "EN_REVISION")
    await client.patch(
        f"/api/ipr/{ipr_id}/modificaciones/{mod_id}",
        json={"status_id": en_rev_id},
        headers=auth(regional_token),
    )

    rechazada_id = await _get_cat_id(db, "modification_status", "RECHAZADA")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}/modificaciones/{mod_id}",
        json={"status_id": rechazada_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200


async def test_fsm_solicitada_to_aprobada_blocked(client: AsyncClient, regional_token: str, db: AsyncSession):
    """SOLICITADA → APROBADA (skip EN_REVISION) should be blocked by DB trigger."""
    ipr_id = await _create_test_ipr(db)
    mod_id = await _create_mod(client, ipr_id, regional_token, db)
    aprobada_id = await _get_cat_id(db, "modification_status", "APROBADA")

    resp = await client.patch(
        f"/api/ipr/{ipr_id}/modificaciones/{mod_id}",
        json={"status_id": aprobada_id},
        headers=auth(regional_token),
    )
    # API catches DB trigger error → 409
    assert resp.status_code == 409


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

async def test_create_modification_encargado(client: AsyncClient, encargado_token: str, db: AsyncSession):
    """ENCARGADO (in WRITE_OPERATIONAL_ROLES) can create modifications."""
    ipr_id = await _create_test_ipr(db)
    type_id = await _get_cat_id(db, "modification_type", "TECNICO")
    resp = await client.post(
        f"/api/ipr/{ipr_id}/modificaciones",
        json={"modification_type_id": type_id, "description": "Cambio técnico menor"},
        headers=auth(encargado_token),
    )
    assert resp.status_code == 201


async def test_approve_modification_requires_admin(client: AsyncClient, encargado_token: str, db: AsyncSession):
    """ENCARGADO cannot approve/reject modifications (only ADMIN roles)."""
    ipr_id = await _create_test_ipr(db)
    # Create as admin first
    type_id = await _get_cat_id(db, "modification_type", "PRESUPUESTO")
    status_id = await _get_cat_id(db, "modification_status", "SOLICITADA")
    row = (await db.execute(
        text("""
            INSERT INTO core.ipr_modification (
                ipr_id, code, modification_type_id, status_id,
                description, requested_by_id
            ) VALUES (
                CAST(:ipr_id AS uuid), 'MOD-TEST-ROLE', CAST(:tid AS uuid),
                CAST(:sid AS uuid), 'Test role', (SELECT id FROM core."user" LIMIT 1)
            )
            RETURNING id
        """),
        {"ipr_id": ipr_id, "tid": type_id, "sid": status_id},
    )).mappings().first()
    await db.commit()
    mod_id = str(row["id"])

    en_rev_id = await _get_cat_id(db, "modification_status", "EN_REVISION")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}/modificaciones/{mod_id}",
        json={"status_id": en_rev_id},
        headers=auth(encargado_token),
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Gate: pending modifications (informational at F4→F5)
# ---------------------------------------------------------------------------

async def test_gate_pending_modifications_informational(client: AsyncClient, regional_token: str, db: AsyncSession):
    """F4→F5 gate should include informational warning about pending modifications."""
    ipr_id = await _create_test_ipr(db, "EN_EJECUCION")
    type_id = await _get_cat_id(db, "modification_type", "PRESUPUESTO")

    await client.post(
        f"/api/ipr/{ipr_id}/modificaciones",
        json={"modification_type_id": type_id, "description": "Pending mod"},
        headers=auth(regional_token),
    )

    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    transitions = resp.json()

    # Find transitions that cross to F5 (e.g. EN_RENDICION, CERRADO)
    f5_trans = [t for t in transitions if t.get("target_phase") == "F5" and t.get("phase_change")]
    if f5_trans:
        gates = f5_trans[0]["gates"]
        mod_gate = next((g for g in gates if g["name"] == "pending_modifications"), None)
        assert mod_gate is not None
        assert mod_gate["met"] is True  # informational, not blocking
        assert "pendiente" in mod_gate["detail"].lower()


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


async def test_batch_report_compliance(client: AsyncClient, regional_token: str, db: AsyncSession):
    """POST /api/ipr/check-report-compliance returns checked count."""
    resp = await client.post(
        "/api/ipr/check-report-compliance",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "checked" in data
    assert "alerts_created" in data


async def test_modification_not_found(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PATCH non-existent modification returns 404."""
    ipr_id = await _create_test_ipr(db)
    fake_id = str(uuid.uuid4())
    resp = await client.patch(
        f"/api/ipr/{ipr_id}/modificaciones/{fake_id}",
        json={"description": "nope"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 404
