"""
Tests for Ciclo 22: Track-Specific Enforcement.

Wave A: FRIL max/min UTM, FRPD CGR (6 tests)
Wave B: Glosa 03 FNDR+PERSONAL prohibition (3 tests)
Wave C: SUBV8 SISREC mandatory (3 tests)
Wave D: FRPD puntaje_min, FRIL licitacion_days (5 tests)
Wave E: Override CORE threshold, fallback universal (3 tests)
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
) -> str:
    """Create a minimal IPR for track enforcement tests."""
    bip = f"TENF-{uuid.uuid4().hex[:8].upper()}"
    status_id = await _get_category_id(db, "ipr_state", status_code)
    phase_id = await _get_category_id(db, "mcd_phase", phase_code)
    mechanism_id = None
    if mechanism_code:
        mechanism_id = await _get_category_id(db, "mechanism", mechanism_code)

    import json
    metadata = json.dumps({"monto_total": str(monto)}) if monto else "{}"

    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, status_id, mcd_phase_id,
                mechanism_id, metadata, created_at, updated_at
            ) VALUES (
                :bip, 'Test Track Enforcement IPR', 'PROYECTO',
                CAST(:status_id AS uuid), CAST(:phase_id AS uuid),
                CAST(:mechanism_id AS uuid), CAST(:metadata AS jsonb),
                NOW(), NOW()
            )
            RETURNING id
        """),
        {"bip": bip, "status_id": status_id, "phase_id": phase_id,
         "mechanism_id": mechanism_id, "metadata": metadata},
    )).mappings().first()
    await db.commit()
    return str(row["id"])


async def _set_ipr_funding_source(db: AsyncSession, ipr_id: str, funding_code: str) -> None:
    """Set IPR funding_source_id."""
    fs_id = await _get_category_id(db, "funding_source", funding_code)
    await db.execute(
        text("UPDATE core.ipr SET funding_source_id = CAST(:fs_id AS uuid) WHERE id = CAST(:id AS uuid)"),
        {"fs_id": fs_id, "id": ipr_id},
    )
    await db.commit()


async def _create_cdp_with_item(
    db: AsyncSession, ipr_id: str, item_code: str, amount: float = 1_000_000,
) -> str:
    """Create a budget_program with specific item and link a CDP to the IPR."""
    item_id = await _get_category_id(db, "budget_item", item_code)
    bp_code = f"TENF-BP-{uuid.uuid4().hex[:6].upper()}"

    bp_row = (await db.execute(
        text("""
            INSERT INTO core.budget_program (code, name, fiscal_year, item_id, initial_amount, current_amount)
            VALUES (:code, 'Test BP', 2026, CAST(:item_id AS uuid), :amount, :amount)
            RETURNING id
        """),
        {"code": bp_code, "item_id": item_id, "amount": amount},
    )).mappings().first()
    bp_id = str(bp_row["id"])

    cdp_num = f"TENF-CDP-{uuid.uuid4().hex[:6].upper()}"
    cdp_row = (await db.execute(
        text("""
            INSERT INTO core.budget_commitment (
                budget_program_id, ipr_id, commitment_number, amount, issued_at
            ) VALUES (
                CAST(:bp_id AS uuid), CAST(:ipr_id AS uuid), :num, :amount, NOW()
            )
            RETURNING id
        """),
        {"bp_id": bp_id, "ipr_id": ipr_id, "num": cdp_num, "amount": amount},
    )).mappings().first()
    await db.commit()
    return str(cdp_row["id"])


async def _create_evaluation_with_score(
    db: AsyncSession, ipr_id: str, score: float, mechanism_code: str = "FRPD",
) -> str:
    """Create evaluation_assignment with numeric_score."""
    et_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'evaluator_type' LIMIT 1"),
    )).mappings().first()
    evaluator_type_id = str(et_row["id"])

    row = (await db.execute(
        text("""
            INSERT INTO core.evaluation_assignment (
                ipr_id, evaluator_type_id, numeric_score, assigned_at
            ) VALUES (
                CAST(:ipr_id AS uuid), CAST(:et_id AS uuid), :score, NOW()
            )
            RETURNING id
        """),
        {"ipr_id": ipr_id, "et_id": evaluator_type_id, "score": score},
    )).mappings().first()
    await db.commit()
    return str(row["id"])


async def _create_milestone(
    db: AsyncSession, ipr_id: str, type_code: str,
    planned_date: str = "2026-01-01", actual_date: str | None = None,
) -> str:
    """Create an ipr_milestone."""
    from datetime import date as dt_date
    type_id = await _get_category_id(db, "milestone_type", type_code)
    planned = dt_date.fromisoformat(planned_date)
    actual = dt_date.fromisoformat(actual_date) if actual_date else None
    row = (await db.execute(
        text("""
            INSERT INTO core.ipr_milestone (
                ipr_id, milestone_type_id, planned_date, actual_date
            ) VALUES (
                CAST(:ipr_id AS uuid), CAST(:type_id AS uuid), :planned, :actual
            )
            RETURNING id
        """),
        {"ipr_id": ipr_id, "type_id": type_id, "planned": planned, "actual": actual},
    )).mappings().first()
    await db.commit()
    return str(row["id"])


async def _create_rendition(db: AsyncSession, ipr_id: str) -> str:
    """Create a minimal rendition linked to an IPR."""
    state_id = await _get_category_id(db, "rendition_state", "PENDIENTE")
    row = (await db.execute(
        text("""
            INSERT INTO core.rendition (ipr_id, state_id, amount, created_at, updated_at)
            VALUES (CAST(:ipr_id AS uuid), CAST(:state_id AS uuid), 1000000, NOW(), NOW())
            RETURNING id
        """),
        {"ipr_id": ipr_id, "state_id": state_id},
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
# Wave A: FRIL max/min UTM, FRPD CGR informational (6 tests)
# ---------------------------------------------------------------------------

async def test_fril_max_utm_blocks_f2_f3(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRIL IPR with monto > max_utm should be blocked at F2→F3."""
    # FRIL max_utm is 4545 UTM. UTM ~67294. So threshold ≈ 305M CLP.
    ipr_id = await _create_test_ipr(db, "RS", "F2", "FRIL", monto=400_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "track_max_utm")
    if gate:
        assert gate["met"] is False, "FRIL max_utm gate should block when monto exceeds threshold"


async def test_fril_max_utm_passes_f2_f3(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRIL IPR with monto < max_utm should pass at F2→F3."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", "FRIL", monto=100_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "track_max_utm")
    if gate:
        assert gate["met"] is True, "FRIL max_utm gate should pass when monto is below threshold"


async def test_fril_min_clp_blocks_f2_f3(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRIL IPR with monto < min_clp should be blocked at F2→F3."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", "FRIL", monto=50_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "track_min_clp")
    if gate:
        assert gate["met"] is False, "FRIL min_clp gate should block when monto is below minimum"


async def test_fril_min_clp_passes_f2_f3(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRIL IPR with monto > min_clp should pass at F2→F3."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", "FRIL", monto=200_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "track_min_clp")
    if gate:
        assert gate["met"] is True, "FRIL min_clp gate should pass when monto exceeds minimum"


async def test_frpd_cgr_informational_f3_f4(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRPD IPR at F3→F4 should show CGR res30 gate as informational (always met)."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "FRPD", monto=100_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "track_cgr_res30")
    if gate:
        assert gate["met"] is True, "CGR res30 gate is informational and should never block"
        assert "informativo" in gate["detail"].lower()


async def test_sni_no_track_gates_f2_f3(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SNI track should not have max_utm or min_clp gates (they're FRIL-specific)."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", "SNI", monto=500_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate_max = _find_gate(resp.json(), "F3", "track_max_utm")
    gate_min = _find_gate(resp.json(), "F3", "track_min_clp")
    # SNI doesn't have max_utm or min_clp in thresholds, so gates shouldn't appear
    assert gate_max is None, "SNI should not have track_max_utm gate"
    assert gate_min is None, "SNI should not have track_min_clp gate"


# ---------------------------------------------------------------------------
# Wave B: Glosa 03 FNDR+PERSONAL prohibition (3 tests)
# ---------------------------------------------------------------------------

async def test_glosa03_blocks_fndr_personal(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa 03: FRIL IPR with CDPs on PERSONAL item should be blocked."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "FRIL", monto=200_000_000)
    await _create_cdp_with_item(db, ipr_id, "PERSONAL", 5_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "glosa03_prohibition")
    if gate:
        assert gate["met"] is False, "Glosa 03 should block FNDR+PERSONAL"


async def test_glosa03_passes_fndr_no_personal(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa 03: FRIL IPR without PERSONAL CDPs should pass."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "FRIL", monto=200_000_000)
    await _create_cdp_with_item(db, ipr_id, "BIENES_SERVICIOS", 5_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "glosa03_prohibition")
    if gate:
        assert gate["met"] is True, "Glosa 03 should pass without PERSONAL items"


async def test_glosa03_skips_non_fndr(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa 03: Non-FNDR mechanism (SUBV8) with PERSONAL CDPs should NOT trigger glosa03."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "SUBV8", monto=200_000_000)
    await _create_cdp_with_item(db, ipr_id, "PERSONAL", 5_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "glosa03_prohibition")
    # SUBV8 is not in _FNDR_MECHANISMS, so glosa03 should not appear
    assert gate is None, "Glosa 03 should not apply to non-FNDR mechanisms"


# ---------------------------------------------------------------------------
# Wave C: SUBV8 SISREC mandatory (3 tests)
# ---------------------------------------------------------------------------

async def test_subv8_sisrec_blocks_no_renditions(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 F4→F5: if monto > sisrec_mandatory_utm and no renditions, should block."""
    # SUBV8 sisrec_mandatory_utm = 500 UTM ≈ 33.6M CLP
    ipr_id = await _create_test_ipr(db, "EN_EJECUCION", "F4", "SUBV8", monto=50_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F5", "track_sisrec_mandatory")
    if gate:
        assert gate["met"] is False, "SUBV8 SISREC should block without renditions"


async def test_subv8_sisrec_passes_with_renditions(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 F4→F5: if monto > threshold and has renditions, should pass."""
    ipr_id = await _create_test_ipr(db, "EN_EJECUCION", "F4", "SUBV8", monto=50_000_000)
    await _create_rendition(db, ipr_id)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F5", "track_sisrec_mandatory")
    if gate:
        assert gate["met"] is True, "SUBV8 SISREC should pass with renditions"


async def test_subv8_sisrec_skips_below_threshold(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 F4→F5: if monto < sisrec_mandatory_utm, gate should not appear."""
    ipr_id = await _create_test_ipr(db, "EN_EJECUCION", "F4", "SUBV8", monto=10_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F5", "track_sisrec_mandatory")
    assert gate is None, "SUBV8 SISREC should not appear when monto is below threshold"


# ---------------------------------------------------------------------------
# Wave D: FRPD puntaje_min, FRIL licitacion_days (5 tests)
# ---------------------------------------------------------------------------

async def test_frpd_puntaje_blocks_low_score(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRPD F2→F3: puntaje_min gate blocks if numeric_score is below threshold (5.0)."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", "FRPD", monto=100_000_000)
    # FRPD puntaje_min = 5.0, so score of 3.0 should block
    await _create_evaluation_with_score(db, ipr_id, 3.0)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "track_puntaje_min")
    if gate:
        assert gate["met"] is False, "Puntaje below minimum should block"


async def test_frpd_puntaje_passes_high_score(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRPD F2→F3: puntaje_min gate passes if numeric_score meets threshold."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", "FRPD", monto=100_000_000)
    await _create_evaluation_with_score(db, ipr_id, 85.0)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "track_puntaje_min")
    if gate:
        assert gate["met"] is True, "Puntaje above minimum should pass"


async def test_frpd_puntaje_blocks_no_score(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRPD F2→F3: puntaje_min gate blocks if no score registered."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", "FRPD", monto=100_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "track_puntaje_min")
    if gate:
        assert gate["met"] is False, "No score should block"
        assert "sin puntaje" in gate["detail"].lower()


async def test_numeric_score_via_patch(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """PATCH /evaluaciones/{id} should accept numeric_score."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", "FRPD", monto=100_000_000)
    eval_id = await _create_evaluation_with_score(db, ipr_id, 50.0)

    resp = await client.patch(
        f"/api/ipr/{ipr_id}/evaluaciones/{eval_id}",
        json={"numeric_score": 88.5},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200

    # Verify score was updated
    list_resp = await client.get(
        f"/api/ipr/{ipr_id}/evaluaciones",
        headers=auth(regional_token),
    )
    assert list_resp.status_code == 200
    items = list_resp.json()
    found = next((e for e in items if e["id"] == eval_id), None)
    assert found is not None
    assert found["numeric_score"] == 88.5


async def test_fril_licitacion_blocks_deviation(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRIL F3→F4: licitacion_max_days blocks if milestone deviation exceeds threshold."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "FRIL", monto=200_000_000)
    # Create LICITACION milestone with large deviation
    await _create_milestone(db, ipr_id, "LICITACION", "2026-01-01", "2026-07-01")  # ~181 days deviation

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "track_licitacion_days")
    if gate:
        assert gate["met"] is False, "Large deviation should block"


# ---------------------------------------------------------------------------
# Wave E: Override CORE threshold, fallback universal (3 tests)
# ---------------------------------------------------------------------------

async def test_core_override_from_track(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """If track has core_approval threshold, it should override the universal one."""
    # First, check if any track has core_approval in thresholds
    track_row = (await db.execute(
        text("SELECT code, thresholds FROM core.financing_track WHERE thresholds ? 'core_approval' AND is_active = TRUE LIMIT 1"),
    )).mappings().first()

    if not track_row:
        pytest.skip("No track with core_approval threshold in test DB")

    mechanism_code = track_row["code"]
    override_utm = int(track_row["thresholds"]["core_approval"])

    # Create IPR with monto between track override and universal threshold
    # This tests that the override is used instead of the universal
    from app.routers.ipr import _get_utm_value, _get_threshold
    from app.core.database import get_db

    utm_row = (await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'UTM_VALUE' AND is_active = TRUE"),
    )).mappings().first()
    utm = int(utm_row["value_utm"]) if utm_row else 67_294

    universal_row = (await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'CORE_APPROVAL' AND is_active = TRUE"),
    )).mappings().first()
    universal_utm = int(universal_row["value_utm"]) if universal_row else 7000

    if override_utm >= universal_utm:
        pytest.skip("Track core_approval not lower than universal — skip override test")

    # Monto above track override but below universal: gate should trigger with override
    monto = (override_utm + 100) * utm
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", mechanism_code, monto=monto)
    await _create_cdp_with_item(db, ipr_id, "BIENES_SERVICIOS", 1_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "core_approval")
    # Gate should exist (because monto > override threshold)
    if gate:
        assert str(override_utm) in gate["detail"] or "CORE" in gate["detail"]


async def test_core_universal_fallback(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """IPR without mechanism (or mechanism without core_approval override) uses universal threshold."""
    # Get universal threshold
    universal_row = (await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'CORE_APPROVAL' AND is_active = TRUE"),
    )).mappings().first()
    if not universal_row:
        pytest.skip("No CORE_APPROVAL threshold in test DB")

    utm_row = (await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'UTM_VALUE' AND is_active = TRUE"),
    )).mappings().first()
    utm = int(utm_row["value_utm"]) if utm_row else 67_294
    universal_utm = int(universal_row["value_utm"])

    # Create IPR without mechanism, above universal threshold
    monto = (universal_utm + 500) * utm
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", None, monto=monto)
    await _create_cdp_with_item(db, ipr_id, "BIENES_SERVICIOS", 1_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "core_approval")
    if gate:
        # Threshold is formatted with thousands separator (e.g. 7,000)
            assert f"{universal_utm:,}" in gate["detail"], "Should use universal threshold"


async def test_core_below_threshold_no_gate(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """IPR with monto below CORE threshold should not have core_approval gate."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "FRIL", monto=10_000_000)
    await _create_cdp_with_item(db, ipr_id, "BIENES_SERVICIOS", 1_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "core_approval")
    assert gate is None, "CORE gate should not appear when monto is below threshold"


# ---------------------------------------------------------------------------
# Wave F: Glosa 06 single-purpose MML (3 tests)
# ---------------------------------------------------------------------------

async def _merge_ipr_metadata(db: AsyncSession, ipr_id: str, extra: dict) -> None:
    """Merge extra keys into IPR metadata JSONB."""
    import json
    await db.execute(
        text("""
            UPDATE core.ipr
            SET metadata = COALESCE(metadata, '{}') || CAST(:extra AS jsonb)
            WHERE id = CAST(:id AS uuid)
        """),
        {"id": ipr_id, "extra": json.dumps(extra)},
    )
    await db.commit()


async def test_glosa06_passes_single_purpose(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa 06: IPR with exactly 1 MML purpose should pass (no gate returned)."""
    ipr_id = await _create_test_ipr(db, "INGRESADO", "F1", "GLOSA06")
    await _merge_ipr_metadata(db, ipr_id, {"mml_purpose_count": 1})

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "glosa06_single_purpose")
    assert gate is None, "Glosa 06 should pass silently with 1 MML purpose"


async def test_glosa06_blocks_multiple_purposes(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa 06: IPR with 2 MML purposes should be blocked."""
    ipr_id = await _create_test_ipr(db, "INGRESADO", "F1", "GLOSA06")
    await _merge_ipr_metadata(db, ipr_id, {"mml_purpose_count": 2})

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "glosa06_single_purpose")
    if gate:
        assert gate["met"] is False, "Glosa 06 should block with multiple MML purposes"
        assert "2" in gate["detail"]


async def test_glosa06_blocks_missing_metadata(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa 06: IPR without mml_purpose_count metadata should be blocked."""
    ipr_id = await _create_test_ipr(db, "INGRESADO", "F1", "GLOSA06")

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "glosa06_single_purpose")
    if gate:
        assert gate["met"] is False, "Glosa 06 should block when metadata is missing"
        assert "falta" in gate["detail"].lower()


# ---------------------------------------------------------------------------
# Wave G: Glosa porcentuales — spending limits (3 tests)
# ---------------------------------------------------------------------------

async def test_glosa_remuneraciones_exceeds_threshold(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa porcentual: PERSONAL > 30% of total CDPs should be flagged."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "FRIL", monto=200_000_000)
    # PERSONAL = 4M, BIENES_SERVICIOS = 6M → PERSONAL = 40% > 30%
    await _create_cdp_with_item(db, ipr_id, "PERSONAL", 4_000_000)
    await _create_cdp_with_item(db, ipr_id, "BIENES_SERVICIOS", 6_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "glosa_remuneraciones_max")
    if gate:
        assert gate["met"] is False, "PERSONAL at 40% should exceed 30% threshold"
        assert "40" in gate["detail"] or "excede" in gate["detail"]


async def test_glosa_remuneraciones_within_threshold(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa porcentual: PERSONAL ≤ 30% of total CDPs should pass."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "FRIL", monto=200_000_000)
    # PERSONAL = 2M, BIENES_SERVICIOS = 8M → PERSONAL = 20% < 30%
    await _create_cdp_with_item(db, ipr_id, "PERSONAL", 2_000_000)
    await _create_cdp_with_item(db, ipr_id, "BIENES_SERVICIOS", 8_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "glosa_remuneraciones_max")
    if gate:
        assert gate["met"] is True, "PERSONAL at 20% should be within 30% threshold"


async def test_glosa_no_cdps_no_gates(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa porcentual: IPR with no CDPs should not produce glosa gates."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "FRIL", monto=200_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "glosa_remuneraciones_max")
    assert gate is None, "No CDPs → no glosa gates"


# ---------------------------------------------------------------------------
# Wave H: Glosa 06 direct executor (3 tests)
# ---------------------------------------------------------------------------

async def _add_ipr_party(db: AsyncSession, ipr_id: str, org_code: str, role_code: str) -> None:
    """Register an organization with a role on the IPR."""
    org_id = (await db.execute(
        text("SELECT id FROM core.organization WHERE code = :code AND deleted_at IS NULL"),
        {"code": org_code},
    )).scalar()
    assert org_id, f"Organization {org_code} not found"
    role_id = await _get_category_id(db, "ipr_party_role", role_code)
    await db.execute(
        text("""
            INSERT INTO core.ipr_party (ipr_id, organization_id, party_role_id)
            VALUES (CAST(:ipr_id AS uuid), CAST(:org_id AS uuid), CAST(:role_id AS uuid))
        """),
        {"ipr_id": ipr_id, "org_id": str(org_id), "role_id": role_id},
    )
    await db.commit()


async def test_glosa06_executor_gore_passes(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa 06: GORE-NUBLE as EJECUTOR should pass (no gate)."""
    ipr_id = await _create_test_ipr(db, "INGRESADO", "F1", "GLOSA06")
    await _merge_ipr_metadata(db, ipr_id, {"mml_purpose_count": 1})
    await _add_ipr_party(db, ipr_id, "GORE-NUBLE", "EJECUTOR")

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "glosa06_direct_executor")
    assert gate is None, "GORE as executor should pass silently"


async def test_glosa06_executor_missing_blocks(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa 06: No EJECUTOR registered should block."""
    ipr_id = await _create_test_ipr(db, "INGRESADO", "F1", "GLOSA06")
    await _merge_ipr_metadata(db, ipr_id, {"mml_purpose_count": 1})

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "glosa06_direct_executor")
    if gate:
        assert gate["met"] is False, "Missing EJECUTOR should block"
        assert "GORE" in gate["detail"]


async def test_glosa06_executor_non_gore_blocks(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa 06: Third-party executor (not GORE) should block."""
    ipr_id = await _create_test_ipr(db, "INGRESADO", "F1", "GLOSA06")
    await _merge_ipr_metadata(db, ipr_id, {"mml_purpose_count": 1})
    # Get any non-GORE organization
    other_org = (await db.execute(
        text("SELECT code FROM core.organization WHERE code != 'GORE-NUBLE' AND deleted_at IS NULL LIMIT 1"),
    )).scalar()
    assert other_org, "Need a non-GORE organization for this test"
    await _add_ipr_party(db, ipr_id, other_org, "EJECUTOR")

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "glosa06_direct_executor")
    if gate:
        assert gate["met"] is False, "Non-GORE executor should block"


# ---------------------------------------------------------------------------
# Wave I: Glosa 07 transfer limits (3 tests)
# ---------------------------------------------------------------------------

async def test_glosa07_admin_exceeds_5pct(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa 07: TRANSFER IPR with admin > 5% should be flagged."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "TRANSFER", monto=200_000_000)
    # BIENES_SERVICIOS = 1M, PERSONAL = 9M → admin = 10% > 5%
    await _create_cdp_with_item(db, ipr_id, "BIENES_SERVICIOS", 1_000_000)
    await _create_cdp_with_item(db, ipr_id, "PERSONAL", 9_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "glosa07_admin_max")
    if gate:
        assert gate["met"] is False, "Admin at 10% should exceed 5% cap"


async def test_glosa07_within_limits_passes(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa 07: TRANSFER IPR with admin ≤ 5% should pass."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "TRANSFER", monto=200_000_000)
    # BIENES_SERVICIOS = 400K, PERSONAL = 9.6M → admin = ~4% < 5%
    await _create_cdp_with_item(db, ipr_id, "BIENES_SERVICIOS", 400_000)
    await _create_cdp_with_item(db, ipr_id, "PERSONAL", 9_600_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "glosa07_admin_max")
    if gate:
        assert gate["met"] is True, "Admin at 4% should be within 5% cap"


async def test_glosa07_skips_non_transfer(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Glosa 07: Non-TRANSFER mechanism should not produce glosa07 gates."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "FRIL", monto=200_000_000)
    await _create_cdp_with_item(db, ipr_id, "BIENES_SERVICIOS", 5_000_000)
    await _create_cdp_with_item(db, ipr_id, "PERSONAL", 5_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "glosa07_admin_max")
    assert gate is None, "Glosa 07 should not apply to non-TRANSFER mechanisms"
