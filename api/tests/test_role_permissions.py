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


async def _get_mechanism_id(db: AsyncSession, code: str) -> str | None:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'mechanism' AND code = :code"),
        {"code": code},
    )).mappings().first()
    return str(row["id"]) if row else None


async def _create_ipr(
    db: AsyncSession,
    status_code: str,
    phase_code: str,
    nature: str = "PROYECTO",
    mechanism_code: str | None = None,
) -> str:
    """Create a minimal IPR for role permission tests."""
    bip = f"RLP-{uuid.uuid4().hex[:8].upper()}"
    status_id = await _get_status_id(db, status_code)
    phase_id = await _get_phase_id(db, phase_code)
    mechanism_id = await _get_mechanism_id(db, mechanism_code) if mechanism_code else None

    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, status_id, mcd_phase_id,
                mechanism_id, created_at, updated_at
            ) VALUES (
                :bip, 'Role Permission Test IPR', :nature,
                CAST(:status_id AS uuid), CAST(:phase_id AS uuid),
                CAST(:mechanism_id AS uuid),
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


async def _transition(client: AsyncClient, ipr_id: str, target_code: str, token: str, db: AsyncSession) -> int:
    """Attempt an IPR transition, return status code."""
    target_id = await _get_status_id(db, target_code)
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_id},
        headers=auth(token),
    )
    return resp.status_code


async def _ensure_test_user(db: AsyncSession, email: str, role_code: str) -> str:
    """Ensure a test user exists for the given role, create if missing. Returns JWT token."""
    uid = (await db.execute(
        text("SELECT id FROM core.\"user\" WHERE email = :e"),
        {"e": email},
    )).scalar()

    if not uid:
        # Create person + user on-the-fly for roles not in goreos_seed_users.sql
        rut = f"99.{uuid.uuid4().hex[:3]}.{uuid.uuid4().hex[:3]}-K"
        person_id = (await db.execute(
            text("""
                INSERT INTO core.person (rut, names, paternal_surname, maternal_surname)
                VALUES (:rut, 'Test', :role, 'User')
                RETURNING id
            """),
            {"rut": rut, "role": role_code},
        )).scalar()

        role_id = (await db.execute(
            text("SELECT id FROM ref.category WHERE scheme = 'system_role' AND code = :code"),
            {"code": role_code},
        )).scalar()
        assert role_id, f"system_role {role_code} not found"

        uid = (await db.execute(
            text("""
                INSERT INTO core."user" (person_id, email, password_hash, system_role_id, is_active)
                VALUES (CAST(:pid AS uuid), :email,
                        '$2b$12$i3hvqlxesIL8chg5P7rii.f1UuWsZfCDK4dkbSmHqAtCIJSm3cIQe',
                        CAST(:rid AS uuid), true)
                RETURNING id
            """),
            {"pid": str(person_id), "email": email, "rid": str(role_id)},
        )).scalar()
        await db.commit()

    return create_access_token({"sub": str(uid), "role": role_code})


# ---------------------------------------------------------------------------
# 5A. Boundary key mapping unit tests (via transitions endpoint)
# ---------------------------------------------------------------------------

async def test_transiciones_includes_allowed_field(client: AsyncClient, regional_token: str, db: AsyncSession):
    """GET /transiciones should include 'allowed' field."""
    ipr_id = await _create_ipr(db, "EN_FORMALIZACION", "F4", nature="PROYECTO")
    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    transitions = resp.json()
    assert len(transitions) > 0
    for t in transitions:
        assert "allowed" in t, f"Missing 'allowed' field in transition {t['code']}"


async def test_transiciones_admin_all_allowed(client: AsyncClient, admin_token: str, db: AsyncSession):
    """ADMIN_SISTEMA should have allowed=True for all transitions."""
    ipr_id = await _create_ipr(db, "EN_REVISION", "F1")
    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(admin_token))
    assert resp.status_code == 200
    for t in resp.json():
        assert t["allowed"] is True, f"ADMIN_SISTEMA should be allowed for {t['code']}"


async def test_transiciones_analista_allowed_in_f4(client: AsyncClient, analista_token: str, db: AsyncSession):
    """ANALISTA should have allowed=True for intra-F4 transitions (absorbed ENCARGADO permissions)."""
    ipr_id = await _create_ipr(db, "EN_EJECUCION", "F4", nature="PROGRAMA")
    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(analista_token))
    assert resp.status_code == 200
    # ANULADO/TERMINADO_ANTICIPADAMENTE are cross-cutting terminal states — require anulacion roles
    terminal_codes = {"ANULADO", "TERMINADO_ANTICIPADAMENTE"}
    for t in resp.json():
        if t["code"] in terminal_codes:
            assert t["allowed"] is False, f"ANALISTA should NOT be allowed for {t['code']}"
        else:
            assert t["allowed"] is True, f"ANALISTA should be allowed for {t['code']}"


# ---------------------------------------------------------------------------
# 5B. Role-based transition blocking (PATCH endpoint)
# ---------------------------------------------------------------------------

async def test_admin_can_transition_admissibility(client: AsyncClient, admin_token: str, db: AsyncSession):
    """ADMIN_SISTEMA can advance EN_REVISION → PRE_ADMISIBLE."""
    ipr_id = await _create_ipr(db, "EN_REVISION", "F1")
    code = await _transition(client, ipr_id, "PRE_ADMISIBLE", admin_token, db)
    assert code == 200


async def test_analista_can_transition_admissibility(client: AsyncClient, analista_token: str, db: AsyncSession):
    """ANALISTA can advance EN_REVISION → PRE_ADMISIBLE (admissibility_check boundary)."""
    ipr_id = await _create_ipr(db, "EN_REVISION", "F1")
    code = await _transition(client, ipr_id, "PRE_ADMISIBLE", analista_token, db)
    assert code == 200


async def test_jefe_division_can_transition_admissibility(client: AsyncClient, jefe_token: str, db: AsyncSession):
    """JEFE_DIVISION can now execute status transitions (was previously restricted to assignee_id only).
    EN_REVISION → PRE_ADMISIBLE is in admissibility_check which includes JEFE_DIVISION... wait no.
    admissibility_check does NOT include JEFE_DIVISION. Test should be 403."""
    ipr_id = await _create_ipr(db, "EN_REVISION", "F1")
    code = await _transition(client, ipr_id, "PRE_ADMISIBLE", jefe_token, db)
    # admissibility_check = {ADMIN_SISTEMA, ADMIN_REGIONAL, GOBERNADOR, ANALISTA}
    # JEFE_DIVISION NOT in admissibility_check
    assert code == 403


async def test_jefe_division_can_send_evaluation(client: AsyncClient, jefe_token: str, db: AsyncSession):
    """JEFE_DIVISION can advance ADMISIBLE → EN_EVALUACION (send_evaluation boundary)."""
    ipr_id = await _create_ipr(db, "ADMISIBLE", "F1")
    code = await _transition(client, ipr_id, "EN_EVALUACION", jefe_token, db)
    assert code == 200


async def test_jefe_departamento_blocked_from_admissibility(client: AsyncClient, db: AsyncSession):
    """JEFE_DEPARTAMENTO cannot execute admissibility_check (not in boundary)."""
    token = await _ensure_test_user(db, "jefe.finanzas.test@goreos.cl", "JEFE_DEPARTAMENTO")
    ipr_id = await _create_ipr(db, "EN_REVISION", "F1")
    code = await _transition(client, ipr_id, "PRE_ADMISIBLE", token, db)
    assert code == 403


async def test_jefe_departamento_can_do_intra_f4(client: AsyncClient, db: AsyncSession):
    """JEFE_DEPARTAMENTO can execute intra-F4 transitions (only boundary they're in)."""
    token = await _ensure_test_user(db, "jefe.finanzas.test@goreos.cl", "JEFE_DEPARTAMENTO")
    ipr_id = await _create_ipr(db, "EN_EJECUCION", "F4", nature="PROGRAMA")
    code = await _transition(client, ipr_id, "SUSPENDIDO", token, db)
    assert code == 200


async def test_analista_blocked_from_closure(client: AsyncClient, analista_token: str, db: AsyncSession):
    """ANALISTA cannot execute closure transitions (only ADMIN+ can close)."""
    ipr_id = await _create_ipr(db, "RENDICION_APROBADA", "F5")
    code = await _transition(client, ipr_id, "EN_CIERRE_ADMINISTRATIVO", analista_token, db)
    assert code == 403


async def test_analista_blocked_from_anulacion(client: AsyncClient, analista_token: str, db: AsyncSession):
    """ANALISTA cannot anular IPRs (only ADMIN_REGIONAL+ and GOBERNADOR)."""
    ipr_id = await _create_ipr(db, "EN_EVALUACION", "F2")
    code = await _transition(client, ipr_id, "ANULADO", analista_token, db)
    assert code == 403


async def test_regional_can_anular(client: AsyncClient, regional_token: str, db: AsyncSession):
    """ADMIN_REGIONAL can anular IPRs."""
    ipr_id = await _create_ipr(db, "EN_EVALUACION", "F2")
    code = await _transition(client, ipr_id, "ANULADO", regional_token, db)
    assert code == 200


# ---------------------------------------------------------------------------
# 5C. Roles without transition authority are blocked at endpoint level
# ---------------------------------------------------------------------------

async def test_consejero_blocked_from_transitions(client: AsyncClient, consejero_token: str, db: AsyncSession):
    """CONSEJERO_REGIONAL operates via core_sessions.py, not ipr.py transitions."""
    ipr_id = await _create_ipr(db, "EN_REVISION", "F1")
    code = await _transition(client, ipr_id, "PRE_ADMISIBLE", consejero_token, db)
    assert code == 403


async def test_dgi_blocked_from_transitions(client: AsyncClient, dgi_token: str, db: AsyncSession):
    """DGI roles observe cartera but cannot execute transitions."""
    ipr_id = await _create_ipr(db, "EN_REVISION", "F1")
    code = await _transition(client, ipr_id, "PRE_ADMISIBLE", dgi_token, db)
    assert code == 403


async def test_rtf_blocked_from_transitions(client: AsyncClient, rtf_token: str, db: AsyncSession):
    """RTF operates via rendiciones.py, not ipr.py transitions."""
    ipr_id = await _create_ipr(db, "EN_REVISION", "F1")
    code = await _transition(client, ipr_id, "PRE_ADMISIBLE", rtf_token, db)
    assert code == 403


async def test_juridico_blocked_from_transitions(client: AsyncClient, juridico_token: str, db: AsyncSession):
    """ASESOR_JURIDICO operates via actos.py/convenios.py, not ipr.py transitions."""
    ipr_id = await _create_ipr(db, "EN_REVISION", "F1")
    code = await _transition(client, ipr_id, "PRE_ADMISIBLE", juridico_token, db)
    assert code == 403


# ---------------------------------------------------------------------------
# 5D. Track overrides (FRIL-specific)
# ---------------------------------------------------------------------------

async def test_fril_jefe_division_can_register_eval_result(client: AsyncClient, jefe_token: str, db: AsyncSession):
    """FRIL override: JEFE_DIVISION can register eval results (DIPIR evaluates internally)."""
    ipr_id = await _create_ipr(db, "EN_EVALUACION", "F2", mechanism_code="FRIL")
    code = await _transition(client, ipr_id, "AD", jefe_token, db)
    assert code == 200


async def test_sni_jefe_division_blocked_from_eval_result(client: AsyncClient, jefe_token: str, db: AsyncSession):
    """SNI: JEFE_DIVISION cannot register eval results (external MDSF evaluation)."""
    ipr_id = await _create_ipr(db, "EN_EVALUACION", "F2", mechanism_code="SNI")
    code = await _transition(client, ipr_id, "RS", jefe_token, db)
    assert code == 403


async def test_no_mechanism_uses_universal_defaults(client: AsyncClient, jefe_token: str, db: AsyncSession):
    """IPR without mechanism uses universal boundary defaults (JEFE_DIVISION blocked from register_eval_result)."""
    ipr_id = await _create_ipr(db, "EN_EVALUACION", "F2")
    code = await _transition(client, ipr_id, "RS", jefe_token, db)
    assert code == 403


# ---------------------------------------------------------------------------
# 5E. JEFE_DIVISION status_id update (was previously blocked, now boundary-controlled)
# ---------------------------------------------------------------------------

async def test_jefe_division_can_update_status_when_allowed(client: AsyncClient, jefe_token: str, db: AsyncSession):
    """JEFE_DIVISION can now update status_id for boundaries they're in."""
    ipr_id = await _create_ipr(db, "ADMISIBLE", "F1")
    target_id = await _get_status_id(db, "EN_EVALUACION")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_id},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 200


async def test_jefe_division_still_restricted_on_other_fields(client: AsyncClient, jefe_token: str, db: AsyncSession):
    """JEFE_DIVISION cannot update fields other than assignee_id and status_id."""
    ipr_id = await _create_ipr(db, "EN_REVISION", "F1")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"name": "Should not work"},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 403


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
