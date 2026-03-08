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


async def _get_test_person_id(db: AsyncSession) -> str:
    """Get any active person from DB."""
    row = (await db.execute(
        text("SELECT id FROM core.person WHERE is_active = true LIMIT 1")
    )).mappings().first()
    assert row, "No active person found in goreos_test"
    return str(row["id"])


async def _get_authority_person_id(db: AsyncSession) -> str:
    """Get person_id of a user with authority role."""
    row = (await db.execute(
        text("""
            SELECT u.person_id FROM core."user" u
            JOIN ref.category r ON u.system_role_id = r.id
            WHERE u.is_active = true
              AND r.code IN ('GOBERNADOR', 'CONSEJERO_REGIONAL', 'SECRETARIO_EJECUTIVO',
                             'ADMIN_REGIONAL', 'JEFE_DIVISION')
            LIMIT 1
        """)
    )).mappings().first()
    assert row, "No authority user found in goreos_test"
    return str(row["person_id"])


def _find_gate(transitions: list[dict], target_phase: str, gate_name: str) -> dict | None:
    """Find a specific gate in transitions response."""
    for t in transitions:
        if t.get("target_phase") == target_phase:
            for g in t.get("gates", []):
                if g["name"] == gate_name:
                    return g
    return None


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


async def test_create_no_conflict(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """Create a declaration with no conflict."""
    ipr_id = await _create_test_ipr(db, mechanism_code="SUBV8")
    person_id = await _get_test_person_id(db)

    resp = await client.post(
        f"/api/ipr/{ipr_id}/parentesco",
        json={
            "person_id": person_id,
            "declaration_type": "EVALUADOR",
            "declares_no_conflict": True,
        },
        headers=auth(admin_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["declares_no_conflict"] is True
    assert data["person_id"] == person_id
    assert data["declaration_type"] == "EVALUADOR"


async def test_create_with_conflict(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """Create a declaration declaring conflict with authority."""
    ipr_id = await _create_test_ipr(db, mechanism_code="SUBV8")
    person_id = await _get_test_person_id(db)
    authority_id = await _get_authority_person_id(db)

    resp = await client.post(
        f"/api/ipr/{ipr_id}/parentesco",
        json={
            "person_id": person_id,
            "declaration_type": "EVALUADOR",
            "declares_no_conflict": False,
            "related_authority_id": authority_id,
            "relationship_type": "CONSANGUINIDAD",
            "relationship_degree": 2,
        },
        headers=auth(admin_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["declares_no_conflict"] is False
    assert data["relationship_degree"] == 2
    assert data["related_authority_name"] is not None


async def test_duplicate_409(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """Duplicate (same person + type + IPR) returns 409."""
    ipr_id = await _create_test_ipr(db, mechanism_code="SUBV8")
    person_id = await _get_test_person_id(db)

    body = {
        "person_id": person_id,
        "declaration_type": "EVALUADOR",
        "declares_no_conflict": True,
    }
    resp1 = await client.post(f"/api/ipr/{ipr_id}/parentesco", json=body, headers=auth(admin_token))
    assert resp1.status_code == 201

    resp2 = await client.post(f"/api/ipr/{ipr_id}/parentesco", json=body, headers=auth(admin_token))
    assert resp2.status_code == 409


async def test_validate_declaration(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """Admin can validate a declaration."""
    ipr_id = await _create_test_ipr(db, mechanism_code="SUBV8")
    person_id = await _get_test_person_id(db)

    create_resp = await client.post(
        f"/api/ipr/{ipr_id}/parentesco",
        json={"person_id": person_id, "declaration_type": "EVALUADOR", "declares_no_conflict": True},
        headers=auth(admin_token),
    )
    decl_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/ipr/{ipr_id}/parentesco/{decl_id}",
        json={"validated": True},
        headers=auth(admin_token),
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["validated_at"] is not None


async def test_delete_declaration(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """Admin can soft-delete a declaration."""
    ipr_id = await _create_test_ipr(db, mechanism_code="SUBV8")
    person_id = await _get_test_person_id(db)

    create_resp = await client.post(
        f"/api/ipr/{ipr_id}/parentesco",
        json={"person_id": person_id, "declaration_type": "EVALUADOR", "declares_no_conflict": True},
        headers=auth(admin_token),
    )
    decl_id = create_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/ipr/{ipr_id}/parentesco/{decl_id}",
        headers=auth(admin_token),
    )
    assert del_resp.status_code == 204

    # Verify gone from list
    list_resp = await client.get(f"/api/ipr/{ipr_id}/parentesco", headers=auth(admin_token))
    assert len(list_resp.json()) == 0


# ---------------------------------------------------------------------------
# Gate Tests (4)
# ---------------------------------------------------------------------------

async def test_gate_blocks_missing_declarations(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR at F1 with no declarations should block F1→F2."""
    ipr_id = await _create_test_ipr(db, "ADMISIBLE", "F1", "SUBV8", monto=50_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "kinship_declarations")
    assert gate is not None
    assert gate["met"] is False
    assert "declaración jurada" in gate["detail"].lower()


async def test_gate_blocks_conflict(
    client: AsyncClient, admin_token: str, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR with a conflict declaration should block F1→F2."""
    ipr_id = await _create_test_ipr(db, "ADMISIBLE", "F1", "SUBV8", monto=50_000_000)
    person_id = await _get_test_person_id(db)
    authority_id = await _get_authority_person_id(db)

    await client.post(
        f"/api/ipr/{ipr_id}/parentesco",
        json={
            "person_id": person_id,
            "declaration_type": "EVALUADOR",
            "declares_no_conflict": False,
            "related_authority_id": authority_id,
            "relationship_type": "CONSANGUINIDAD",
            "relationship_degree": 3,
        },
        headers=auth(admin_token),
    )

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "kinship_declarations")
    assert gate is not None
    assert gate["met"] is False
    assert "conflicto" in gate["detail"].lower()


async def test_gate_passes_clean(
    client: AsyncClient, admin_token: str, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR with clean declarations should pass (gate absent = silent pass)."""
    ipr_id = await _create_test_ipr(db, "ADMISIBLE", "F1", "SUBV8", monto=50_000_000)
    person_id = await _get_test_person_id(db)

    await client.post(
        f"/api/ipr/{ipr_id}/parentesco",
        json={"person_id": person_id, "declaration_type": "EVALUADOR", "declares_no_conflict": True},
        headers=auth(admin_token),
    )

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "kinship_declarations")
    assert gate is None, "Clean declarations should result in silent pass (no gate shown)"


async def test_gate_not_for_sni(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Non-SUBV8 mechanism (SNI) should not show kinship gate."""
    ipr_id = await _create_test_ipr(db, "ADMISIBLE", "F1", "SNI", monto=200_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "kinship_declarations")
    assert gate is None, "Kinship gate should not appear for non-SUBV8 mechanisms"
