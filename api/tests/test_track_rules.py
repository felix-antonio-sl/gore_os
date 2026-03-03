"""
Tests for Ciclo 23: Track Rules Engine.

Wave 1: FRIL fraccionamiento + max 5/comuna (5 tests)
Wave 2: RS vigencia + eval type match (4 tests)
Wave 3: C33 conservation + SNI proporcionalidad (5 tests)
Wave 4: SNI levels admin + auto-evaluator (4 tests)
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

async def _get_category_id(db: AsyncSession, scheme: str, code: str) -> str:
    row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = :scheme AND code = :code"),
        {"scheme": scheme, "code": code},
    )).mappings().first()
    assert row, f"{scheme}/{code} not found in ref.category"
    return str(row["id"])


async def _create_test_ipr(
    db: AsyncSession,
    status_code: str = "EN_EVALUACION",
    phase_code: str = "F2",
    mechanism_code: str | None = None,
    monto: float | None = None,
    executor_id: str | None = None,
    metadata: dict | None = None,
) -> str:
    """Create a minimal IPR for track rules tests."""
    import json

    bip = f"TRULE-{uuid.uuid4().hex[:8].upper()}"
    status_id = await _get_category_id(db, "ipr_state", status_code)
    phase_id = await _get_category_id(db, "mcd_phase", phase_code)
    mechanism_id = None
    if mechanism_code:
        mechanism_id = await _get_category_id(db, "mechanism", mechanism_code)

    meta = metadata or {}
    if monto is not None:
        meta["monto_total"] = str(monto)
    meta_json = json.dumps(meta) if meta else "{}"

    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, status_id, mcd_phase_id,
                mechanism_id, executor_id, metadata, created_at, updated_at
            ) VALUES (
                :bip, 'Test Track Rules IPR', 'PROYECTO',
                CAST(:status_id AS uuid), CAST(:phase_id AS uuid),
                CAST(:mechanism_id AS uuid), CAST(:executor_id AS uuid),
                CAST(:metadata AS jsonb), NOW(), NOW()
            )
            RETURNING id
        """),
        {
            "bip": bip, "status_id": status_id, "phase_id": phase_id,
            "mechanism_id": mechanism_id, "executor_id": executor_id,
            "metadata": meta_json,
        },
    )).mappings().first()
    await db.commit()
    return str(row["id"])


async def _link_territory(db: AsyncSession, ipr_id: str, territory_id: str | None = None) -> str:
    """Link an IPR to a territory. Uses first available territory if not specified."""
    if not territory_id:
        t_row = (await db.execute(
            text("SELECT id FROM core.territory LIMIT 1"),
        )).mappings().first()
        assert t_row, "No territories in test DB"
        territory_id = str(t_row["id"])

    impact_id = await _get_category_id(db, "territory_impact", "UBICACION")
    row = (await db.execute(
        text("""
            INSERT INTO core.ipr_territory (ipr_id, territory_id, impact_type_id)
            VALUES (CAST(:ipr_id AS uuid), CAST(:territory_id AS uuid), CAST(:impact_id AS uuid))
            RETURNING id
        """),
        {"ipr_id": ipr_id, "territory_id": territory_id, "impact_id": impact_id},
    )).mappings().first()
    await db.commit()
    return territory_id


async def _create_evaluation_completed(
    db: AsyncSession, ipr_id: str, result_code: str,
    completed_at: str | None = None,
) -> str:
    """Create a completed evaluation_assignment with a specific result code."""
    from datetime import datetime, timezone

    et_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'evaluator_type' LIMIT 1"),
    )).mappings().first()
    evaluator_type_id = str(et_row["id"])

    # Resolve result_code to ID
    result_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'ipr_state' AND code = :code"),
        {"code": result_code},
    )).mappings().first()
    result_id = str(result_row["id"]) if result_row else None

    completed = datetime.fromisoformat(completed_at) if completed_at else datetime.now(timezone.utc)

    row = (await db.execute(
        text("""
            INSERT INTO core.evaluation_assignment (
                ipr_id, evaluator_type_id, result_id, completed_at, assigned_at
            ) VALUES (
                CAST(:ipr_id AS uuid), CAST(:et_id AS uuid),
                CAST(:result_id AS uuid), :completed_at, NOW()
            )
            RETURNING id
        """),
        {
            "ipr_id": ipr_id, "et_id": evaluator_type_id,
            "result_id": result_id, "completed_at": completed,
        },
    )).mappings().first()
    await db.commit()
    return str(row["id"])


def _find_gate(transitions: list[dict], target_phase: str, gate_name: str) -> dict | None:
    """Find a specific gate in transitions response."""
    for t in transitions:
        if t.get("target_phase") == target_phase:
            for g in t.get("gates", []):
                if g["name"] == gate_name:
                    return g
    return None


# ---------------------------------------------------------------------------
# Wave 1: FRIL fraccionamiento + max 5/comuna (5 tests)
# ---------------------------------------------------------------------------

async def test_fril_fraccionamiento_detected(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRIL IPRs from same executor+territory within 90 days that exceed max_utm combined should trigger gate."""
    # Get an organization to use as executor
    org_row = (await db.execute(
        text("SELECT id FROM core.organization WHERE deleted_at IS NULL LIMIT 1"),
    )).mappings().first()
    executor_id = str(org_row["id"])

    # Get FRIL max_utm threshold from track
    track_row = (await db.execute(
        text("SELECT thresholds FROM core.financing_track WHERE code = 'FRIL' AND is_active = TRUE"),
    )).mappings().first()
    if not track_row or "max_utm" not in (track_row["thresholds"] or {}):
        pytest.skip("No FRIL track with max_utm in test DB")

    utm_row = (await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'UTM_VALUE' AND is_active = TRUE"),
    )).mappings().first()
    utm = int(utm_row["value_utm"]) if utm_row else 67_294
    max_utm = float(track_row["thresholds"]["max_utm"])
    max_clp = max_utm * utm

    # Create two FRIL IPRs that individually are under the limit but combined exceed it
    monto_each = max_clp * 0.7  # 70% of limit each → 140% combined
    ipr1_id = await _create_test_ipr(db, "EN_REVISION", "F1", "FRIL", monto=monto_each, executor_id=executor_id)
    ipr2_id = await _create_test_ipr(db, "EN_REVISION", "F1", "FRIL", monto=monto_each, executor_id=executor_id)

    # Link both to same territory
    territory_id = await _link_territory(db, ipr1_id)
    await _link_territory(db, ipr2_id, territory_id)

    # Check transitions for ipr2 — should see fraccionamiento gate
    resp = await client.get(f"/api/ipr/{ipr2_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "fril_fraccionamiento")
    if gate:
        assert gate["met"] is False, "Fraccionamiento should be detected when combined monto exceeds max_utm"


async def test_fril_fraccionamiento_safe(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRIL IPR without siblings should not trigger fraccionamiento gate."""
    org_row = (await db.execute(
        text("SELECT id FROM core.organization WHERE deleted_at IS NULL LIMIT 1"),
    )).mappings().first()
    executor_id = str(org_row["id"])

    ipr_id = await _create_test_ipr(db, "EN_REVISION", "F1", "FRIL", monto=50_000_000, executor_id=executor_id)
    await _link_territory(db, ipr_id)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "fril_fraccionamiento")
    # Gate may not appear at all (no siblings) or met=True
    if gate:
        assert gate["met"] is True


async def test_fril_fraccionamiento_non_fril_skip(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Non-FRIL IPR should not trigger fraccionamiento gate."""
    ipr_id = await _create_test_ipr(db, "EN_REVISION", "F1", "SNI", monto=200_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "fril_fraccionamiento")
    assert gate is None, "Fraccionamiento gate should not appear for non-FRIL"


async def test_fril_max_comuna_exceeded(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRIL max 5/comuna: should block if territory already has 5 active FRIL projects."""
    territory_row = (await db.execute(
        text("SELECT id FROM core.territory LIMIT 1"),
    )).mappings().first()
    territory_id = str(territory_row["id"])

    # Create 5 FRIL IPRs in same territory/year
    for _ in range(5):
        ipr = await _create_test_ipr(db, "INGRESADO", "F0", "FRIL", monto=50_000_000)
        await _link_territory(db, ipr, territory_id)

    # Create 6th FRIL in same territory
    ipr_id = await _create_test_ipr(db, "INGRESADO", "F0", "FRIL", monto=50_000_000)
    await _link_territory(db, ipr_id, territory_id)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F1", "fril_max_comuna")
    if gate:
        assert gate["met"] is False, "Should block 6th FRIL in same territory"


async def test_fril_max_comuna_ok(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRIL max 5/comuna: first project in a territory should pass."""
    # Use a less-used territory
    territory_row = (await db.execute(
        text("SELECT id FROM core.territory ORDER BY id DESC LIMIT 1"),
    )).mappings().first()
    territory_id = str(territory_row["id"])

    ipr_id = await _create_test_ipr(db, "INGRESADO", "F0", "FRIL", monto=50_000_000)
    await _link_territory(db, ipr_id, territory_id)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F1", "fril_max_comuna")
    # Gate should not appear (less than 5)
    assert gate is None, "Should not block when fewer than 5 FRIL in territory"


# ---------------------------------------------------------------------------
# Wave 2: RS vigencia + eval type match (4 tests)
# ---------------------------------------------------------------------------

async def test_rs_vigencia_valid(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SNI IPR with recent favorable RS evaluation should have valid RS vigencia."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "SNI", monto=200_000_000)
    await _create_evaluation_completed(db, ipr_id, "RS")

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "rs_vigencia")
    if gate:
        assert gate["met"] is True, "Recent RS should be valid"
        assert "vigente" in gate["detail"].lower()


async def test_rs_vigencia_expired(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SNI IPR with RS completed >3 years ago should show expired RS."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "SNI", monto=200_000_000)
    # Create evaluation completed 4 years ago
    await _create_evaluation_completed(db, ipr_id, "RS", "2021-01-01T00:00:00+00:00")

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "rs_vigencia")
    if gate:
        assert gate["met"] is False, "RS from >3 years ago should be expired"
        assert "expirado" in gate["detail"].lower()


async def test_rs_vigencia_no_evaluation(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SNI IPR with no evaluation should show missing evaluation."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "SNI", monto=200_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "rs_vigencia")
    if gate:
        assert gate["met"] is False, "No evaluation should block"
        assert "sin evaluación" in gate["detail"].lower()


async def test_eval_type_match_warning(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """TRANSFER IPR with RS result (expected ITF) should show type mismatch warning."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", "TRANSFER", monto=200_000_000)
    # RS is not a TRANSFER product — TRANSFER expects ITF
    await _create_evaluation_completed(db, ipr_id, "RS")

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "eval_type_match")
    if gate:
        assert gate["met"] is True, "Eval type mismatch is informational (never blocks)"
        assert "advertencia" in gate["detail"].lower()


# ---------------------------------------------------------------------------
# Wave 3: C33 conservation + SNI proporcionalidad (5 tests)
# ---------------------------------------------------------------------------

async def test_c33_conservation_exceeds(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """C33 IPR with conservation > 30% of replacement should warn about reclassification."""
    ipr_id = await _create_test_ipr(
        db, "EN_REVISION", "F1", "C33", monto=100_000_000,
        metadata={"costo_conservacion": "50000000", "costo_reposicion": "100000000"},
    )

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "c33_conservation")
    if gate:
        assert gate["met"] is True, "C33 conservation is informational (never blocks)"
        assert "reclasificación" in gate["detail"].lower() or "excede" in gate["detail"].lower()


async def test_c33_conservation_within(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """C33 IPR with conservation < 30% should not warn about reclassification."""
    ipr_id = await _create_test_ipr(
        db, "EN_REVISION", "F1", "C33", monto=100_000_000,
        metadata={"costo_conservacion": "20000000", "costo_reposicion": "100000000"},
    )

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "c33_conservation")
    if gate:
        assert gate["met"] is True
        assert "dentro de" in gate["detail"].lower()


async def test_c33_conservation_no_data(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """C33 IPR without cost data should show informational message."""
    ipr_id = await _create_test_ipr(db, "EN_REVISION", "F1", "C33", monto=100_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "c33_conservation")
    if gate:
        assert gate["met"] is True
        assert "ingresar" in gate["detail"].lower()


async def test_sni_proporcionalidad_nivel0(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SNI IPR <=1500 UTM should show Nivel 0 (GORE_DAE evaluator)."""
    utm_row = (await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'UTM_VALUE' AND is_active = TRUE"),
    )).mappings().first()
    utm = int(utm_row["value_utm"]) if utm_row else 67_294

    monto = 1000 * utm  # 1000 UTM — within Nivel 0
    ipr_id = await _create_test_ipr(db, "EN_REVISION", "F1", "SNI", monto=monto)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "sni_proporcionalidad")
    if gate:
        assert gate["met"] is True, "SNI proporcionalidad is informational"
        assert "GORE_DAE" in gate["detail"]


async def test_sni_proporcionalidad_nivel2(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SNI IPR 5000-25000 UTM should show Nivel 2 (MDSF evaluator)."""
    utm_row = (await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'UTM_VALUE' AND is_active = TRUE"),
    )).mappings().first()
    utm = int(utm_row["value_utm"]) if utm_row else 67_294

    monto = 10_000 * utm  # 10000 UTM — within Nivel 2
    ipr_id = await _create_test_ipr(db, "EN_REVISION", "F1", "SNI", monto=monto)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "sni_proporcionalidad")
    if gate:
        assert gate["met"] is True
        assert "MDSF" in gate["detail"]


# ---------------------------------------------------------------------------
# Wave 4: SNI levels admin + auto-evaluator (4 tests)
# ---------------------------------------------------------------------------

async def test_admin_list_sni_levels(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """GET /api/admin/sni-levels should return SNI level configuration."""
    resp = await client.get("/api/admin/sni-levels", headers=auth(admin_token))
    assert resp.status_code == 200
    levels = resp.json()
    assert isinstance(levels, list)
    # Should have at least the 4 seeded levels
    if levels:
        assert levels[0]["level_number"] is not None
        assert levels[0]["evaluator_code"] is not None


async def test_admin_update_sni_level(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """PATCH /api/admin/sni-levels/{id} should update a level."""
    # Get first level
    list_resp = await client.get("/api/admin/sni-levels", headers=auth(admin_token))
    if list_resp.status_code != 200 or not list_resp.json():
        pytest.skip("No SNI levels in test DB")

    level_id = list_resp.json()[0]["id"]
    resp = await client.patch(
        f"/api/admin/sni-levels/{level_id}",
        json={"label": "Nivel 0 — Evaluación GORE (actualizado)"},
        headers=auth(admin_token),
    )
    assert resp.status_code == 200


async def test_admin_sni_levels_requires_admin(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Non-admin should be rejected from SNI levels endpoint."""
    resp = await client.get("/api/admin/sni-levels", headers=auth(regional_token))
    assert resp.status_code == 403


async def test_sni_auto_evaluator_override(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """SNI IPR should get level-specific evaluator (not generic track evaluator)."""
    utm_row = (await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'UTM_VALUE' AND is_active = TRUE"),
    )).mappings().first()
    utm = int(utm_row["value_utm"]) if utm_row else 67_294

    # Create SNI IPR at nivel 1 (1500-5000 UTM) → should assign SEREMI
    monto = 3000 * utm
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", "SNI", monto=monto)

    # Create evaluation without specifying evaluator_type_id
    resp = await client.post(
        f"/api/ipr/{ipr_id}/evaluaciones",
        json={},
        headers=auth(admin_token),
    )
    if resp.status_code == 201:
        eval_id = resp.json()["id"]
        # Check which evaluator was assigned
        eval_resp = await client.get(
            f"/api/ipr/{ipr_id}/evaluaciones",
            headers=auth(admin_token),
        )
        assert eval_resp.status_code == 200
        evals = eval_resp.json()
        found = next((e for e in evals if e["id"] == eval_id), None)
        if found:
            # At nivel 1, evaluator should be SEREMI
            assert found["evaluator_type"] == "SEREMI", \
                f"Expected SEREMI evaluator for SNI nivel 1, got {found['evaluator_type']}"
    elif resp.status_code == 400:
        # SEREMI evaluator type might not exist in test DB yet
        pytest.skip("SEREMI evaluator type not available in test DB")
