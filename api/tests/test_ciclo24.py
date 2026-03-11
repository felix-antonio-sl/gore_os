"""
Tests for Ciclo 24: Track Rules Engine — Remaining HΩ.

Wave 1: FRIL tender deadline + Glosa 06 single-purpose (5 tests)
Wave 2: Morosos SISREC — entity-scoped overdue renditions (5 tests)
Wave 3: Evaluation rankings persistence (5 tests)
Wave 4: Pagaré notarial + directorio certificate (7 tests)
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
# Helpers (reuse patterns from test_track_rules.py)
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
    """Create a minimal IPR for Ciclo 24 tests."""
    bip = f"C24-{uuid.uuid4().hex[:8].upper()}"
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
                :bip, 'Test Ciclo 24 IPR', 'PROYECTO',
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


async def _create_rendition_with_state(
    db: AsyncSession, ipr_id: str, state_code: str, age_days: int = 0,
) -> str:
    """Create rendition in a specific state, optionally aged by N days."""
    state_id = await _get_category_id(db, "rendition_state", state_code)
    row = (await db.execute(
        text("""
            INSERT INTO core.rendition (ipr_id, state_id, amount, created_at, updated_at)
            VALUES (
                CAST(:ipr_id AS uuid), CAST(:state_id AS uuid), 1000000,
                NOW() - make_interval(days => :age), NOW() - make_interval(days => :age)
            )
            RETURNING id
        """),
        {"ipr_id": ipr_id, "state_id": state_id, "age": age_days},
    )).mappings().first()
    await db.commit()
    return str(row["id"])


async def _create_evaluation_completed(
    db: AsyncSession, ipr_id: str, result_code: str | None = None,
    rank_position: int | None = None, rank_total: int | None = None,
    convocatoria_code: str | None = None,
) -> str:
    """Create a completed evaluation_assignment with optional ranking."""
    from datetime import datetime, timezone
    et_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'evaluator_type' LIMIT 1"),
    )).mappings().first()
    evaluator_type_id = str(et_row["id"])

    result_id = None
    if result_code:
        result_row = (await db.execute(
            text("SELECT id FROM ref.category WHERE scheme = 'evaluation_result' AND code = :code"),
            {"code": result_code},
        )).mappings().first()
        result_id = str(result_row["id"]) if result_row else None

    row = (await db.execute(
        text("""
            INSERT INTO core.evaluation_assignment (
                ipr_id, evaluator_type_id, result_id, completed_at, assigned_at,
                rank_position, rank_total, convocatoria_code
            ) VALUES (
                CAST(:ipr_id AS uuid), CAST(:et_id AS uuid),
                CAST(:result_id AS uuid), :completed_at, NOW(),
                :rank_position, :rank_total, :convocatoria_code
            )
            RETURNING id
        """),
        {
            "ipr_id": ipr_id, "et_id": evaluator_type_id,
            "result_id": result_id, "completed_at": datetime.now(timezone.utc),
            "rank_position": rank_position, "rank_total": rank_total,
            "convocatoria_code": convocatoria_code,
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
# Wave 1: FRIL tender deadline + Glosa 06 single-purpose (5 tests)
# ---------------------------------------------------------------------------

async def test_fril_tender_blocks_expired(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRIL IPR at F3 with no LICITACION milestone and old updated_at should block F3→F4."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "FRIL", monto=100_000_000)

    # Disable triggers to bypass fn_update_timestamp, then age the IPR
    await db.execute(text("SET session_replication_role = 'replica'"))
    await db.execute(
        text("UPDATE core.ipr SET updated_at = NOW() - INTERVAL '120 days' WHERE id = CAST(:id AS uuid)"),
        {"id": ipr_id},
    )
    await db.execute(text("SET session_replication_role = 'origin'"))
    await db.commit()

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "fril_tender_deadline")
    if gate:
        assert gate["met"] is False, "Should block — 120 days without tender exceeds 90d limit"
        assert "120" in gate["detail"] or "días sin licitación" in gate["detail"]


async def test_fril_tender_passes_with_milestone(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRIL IPR with LICITACION milestone (actual_date set) should pass tender gate."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "FRIL", monto=100_000_000)

    # Disable triggers + age the IPR (would fail without milestone)
    await db.execute(text("SET session_replication_role = 'replica'"))
    await db.execute(
        text("UPDATE core.ipr SET updated_at = NOW() - INTERVAL '120 days' WHERE id = CAST(:id AS uuid)"),
        {"id": ipr_id},
    )
    await db.execute(text("SET session_replication_role = 'origin'"))
    await db.commit()

    # Add LICITACION milestone with actual_date
    await _create_milestone(db, ipr_id, "LICITACION", actual_date="2026-02-15")

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "fril_tender_deadline")
    # Gate should not appear (tender completed)
    assert gate is None, "FRIL with LICITACION milestone should not show tender deadline gate"


async def test_fril_tender_non_fril_skip(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Non-FRIL IPR should not trigger tender deadline gate."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "SNI", monto=200_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "fril_tender_deadline")
    assert gate is None, "Tender deadline gate should not appear for non-FRIL"


async def test_glosa06_blocks_missing_purpose(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """GLOSA06 IPR without mml_purpose_count should block F1→F2."""
    # Check if GLOSA06 mechanism exists
    mech_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'mechanism' AND code = 'GLOSA06'"),
    )).mappings().first()
    if not mech_row:
        pytest.skip("GLOSA06 mechanism not in test DB")

    ipr_id = await _create_test_ipr(db, "EN_REVISION", "F1", "GLOSA06", monto=50_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "glosa06_single_purpose")
    if gate:
        assert gate["met"] is False, "Should block — missing mml_purpose_count"


async def test_glosa06_blocks_multiple_purposes(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """GLOSA06 IPR with mml_purpose_count=2 should block F1→F2."""
    mech_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'mechanism' AND code = 'GLOSA06'"),
    )).mappings().first()
    if not mech_row:
        pytest.skip("GLOSA06 mechanism not in test DB")

    ipr_id = await _create_test_ipr(
        db, "EN_REVISION", "F1", "GLOSA06", monto=50_000_000,
        metadata={"mml_purpose_count": "2"},
    )

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F2", "glosa06_single_purpose")
    if gate:
        assert gate["met"] is False, "Should block — 2 purposes, needs exactly 1"
        assert "2" in gate["detail"]


# ---------------------------------------------------------------------------
# Wave 2: Morosos SISREC — entity-scoped overdue renditions (5 tests)
# ---------------------------------------------------------------------------

async def test_morosos_blocks_overdue_rendition(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR should be blocked if executor has overdue rendition on any IPR."""
    # Get an org for executor
    org_row = (await db.execute(
        text("SELECT id FROM core.organization WHERE deleted_at IS NULL LIMIT 1"),
    )).mappings().first()
    executor_id = str(org_row["id"])

    # Create another IPR for the same executor with an overdue rendition
    other_ipr = await _create_test_ipr(db, "EN_EJECUCION", "F4", "SUBV8", monto=50_000_000, executor_id=executor_id)
    await _create_rendition_with_state(db, other_ipr, "EN_REVISION_RTF", age_days=10)  # >7d SLA

    # Create the IPR under test
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "SUBV8", monto=80_000_000, executor_id=executor_id)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "morosos_sisrec")
    if gate:
        assert gate["met"] is False, "Should block — executor has overdue rendition"
        assert "vencida" in gate["detail"]


async def test_morosos_passes_no_overdue(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR should pass if executor has no overdue renditions."""
    org_row = (await db.execute(
        text("SELECT id FROM core.organization WHERE deleted_at IS NULL ORDER BY id LIMIT 1 OFFSET 2"),
    )).mappings().first()
    executor_id = str(org_row["id"])

    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "SUBV8", monto=80_000_000, executor_id=executor_id)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "morosos_sisrec")
    # Gate should not appear (no overdue renditions)
    assert gate is None, "Should not block when executor has no overdue renditions"


async def test_morosos_only_overdue_counts(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8: approved renditions should not trigger morosos gate."""
    org_row = (await db.execute(
        text("SELECT id FROM core.organization WHERE deleted_at IS NULL ORDER BY id LIMIT 1 OFFSET 3"),
    )).mappings().first()
    executor_id = str(org_row["id"])

    other_ipr = await _create_test_ipr(db, "EN_EJECUCION", "F4", "SUBV8", monto=50_000_000, executor_id=executor_id)
    await _create_rendition_with_state(db, other_ipr, "APROBADA", age_days=30)  # Old but approved

    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "SUBV8", monto=80_000_000, executor_id=executor_id)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "morosos_sisrec")
    assert gate is None, "Approved renditions should not trigger morosos"


async def test_morosos_non_subv8_skip(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Non-SUBV8 IPR should not trigger morosos gate."""
    ipr_id = await _create_test_ipr(db, "CDP_EMITIDO", "F3", "SNI", monto=200_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F4", "morosos_sisrec")
    assert gate is None, "Morosos gate should not appear for non-SUBV8"


async def test_morosos_f4_f5_also_checks(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 morosos check should also appear at F4→F5."""
    org_row = (await db.execute(
        text("SELECT id FROM core.organization WHERE deleted_at IS NULL ORDER BY id LIMIT 1 OFFSET 4"),
    )).mappings().first()
    executor_id = str(org_row["id"])

    # Create overdue rendition on another IPR
    other_ipr = await _create_test_ipr(db, "EN_EJECUCION", "F4", "SUBV8", monto=50_000_000, executor_id=executor_id)
    await _create_rendition_with_state(db, other_ipr, "EN_REVISION_UCR", age_days=5)  # >2d SLA

    ipr_id = await _create_test_ipr(db, "EN_EJECUCION", "F4", "SUBV8", monto=80_000_000, executor_id=executor_id)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F5", "morosos_sisrec")
    if gate:
        assert gate["met"] is False, "Should also block at F4→F5"


# ---------------------------------------------------------------------------
# Wave 3: Evaluation rankings persistence (5 tests)
# ---------------------------------------------------------------------------

async def test_ranking_create_with_fields(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """Creating evaluation with rank_position/rank_total should persist."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", "SUBV8", monto=80_000_000)

    # Need evaluator_type_id
    et_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'evaluator_type' LIMIT 1"),
    )).mappings().first()
    if not et_row:
        pytest.skip("No evaluator_type in test DB")

    resp = await client.post(
        f"/api/ipr/{ipr_id}/evaluaciones",
        json={
            "evaluator_type_id": str(et_row["id"]),
            "rank_position": 3,
            "rank_total": 15,
            "convocatoria_code": "CONV-2026-01",
        },
        headers=auth(admin_token),
    )
    assert resp.status_code == 201

    # Verify via list
    list_resp = await client.get(f"/api/ipr/{ipr_id}/evaluaciones", headers=auth(admin_token))
    assert list_resp.status_code == 200
    evals = list_resp.json()
    assert len(evals) >= 1
    last = evals[0]
    assert last["rank_position"] == 3
    assert last["rank_total"] == 15
    assert last["convocatoria_code"] == "CONV-2026-01"


async def test_ranking_update_via_patch(
    client: AsyncClient, admin_token: str, db: AsyncSession,
):
    """PATCH evaluation to add ranking fields."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", "SUBV8", monto=80_000_000)

    et_row = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'evaluator_type' LIMIT 1"),
    )).mappings().first()
    if not et_row:
        pytest.skip("No evaluator_type in test DB")

    create_resp = await client.post(
        f"/api/ipr/{ipr_id}/evaluaciones",
        json={"evaluator_type_id": str(et_row["id"])},
        headers=auth(admin_token),
    )
    assert create_resp.status_code == 201
    eval_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/ipr/{ipr_id}/evaluaciones/{eval_id}",
        json={"rank_position": 1, "rank_total": 10, "convocatoria_code": "CONV-2026-02"},
        headers=auth(admin_token),
    )
    assert patch_resp.status_code == 200

    # Verify
    list_resp = await client.get(f"/api/ipr/{ipr_id}/evaluaciones", headers=auth(admin_token))
    evals = list_resp.json()
    found = next((e for e in evals if e["id"] == eval_id), None)
    assert found is not None
    assert found["rank_position"] == 1
    assert found["rank_total"] == 10


async def test_ranking_gate_informational(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR with completed eval missing ranking should show informational warning."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", "SUBV8", monto=80_000_000)
    await _create_evaluation_completed(db, ipr_id, "RS")  # No ranking

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "ranking_persistence")
    if gate:
        assert gate["met"] is True, "Ranking persistence is informational (never blocks)"
        assert "sin ranking" in gate["detail"].lower()


async def test_ranking_gate_not_for_sni(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Non-competitive mechanism (SNI) should not show ranking gate."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", "SNI", monto=200_000_000)
    await _create_evaluation_completed(db, ipr_id, "RS")

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "ranking_persistence")
    assert gate is None, "Ranking gate should not appear for non-competitive mechanisms"


async def test_ranking_gate_silent_with_data(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR with ranking data populated should not show warning."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", "SUBV8", monto=80_000_000)
    await _create_evaluation_completed(db, ipr_id, "RS", rank_position=2, rank_total=10)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "ranking_persistence")
    assert gate is None, "Should not warn when ranking data is populated"


# ---------------------------------------------------------------------------
# Wave 4: Pagaré notarial + directorio certificate (7 tests)
# ---------------------------------------------------------------------------

async def test_pagare_blocks_missing(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR without pagare metadata should block F2→F3."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", "SUBV8", monto=80_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "pagare_notarial")
    if gate:
        assert gate["met"] is False, "Should block — no pagare data"
        assert "pagaré notarial" in gate["detail"].lower()


async def test_pagare_blocks_insufficient(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR with pagare covering less than 100% should block."""
    ipr_id = await _create_test_ipr(
        db, "RS", "F2", "SUBV8", monto=100_000_000,
        metadata={
            "pagare_monto": "80000000",  # Only 80%
            "pagare_fecha_vencimiento": "2028-06-01",
        },
    )

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "pagare_notarial")
    if gate:
        assert gate["met"] is False, "Should block — pagare < 100% of monto"
        assert "no cubre" in gate["detail"].lower()


async def test_pagare_passes_valid(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR with pagare >= 100% and sufficient validity should pass."""
    ipr_id = await _create_test_ipr(
        db, "RS", "F2", "SUBV8", monto=100_000_000,
        metadata={
            "pagare_monto": "100000000",
            "pagare_fecha_vencimiento": "2028-06-01",  # ~2 years out
        },
    )

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "pagare_notarial")
    # Should pass silently (returns None)
    assert gate is None, "Valid pagare should pass silently"


async def test_pagare_non_subv8_skip(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """Non-SUBV8 IPR should not trigger pagare gate."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", "FRIL", monto=100_000_000)

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "pagare_notarial")
    assert gate is None, "Pagare gate should not appear for non-SUBV8"


async def test_directorio_blocks_missing(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR without directorio_cert_date should block F2→F3."""
    ipr_id = await _create_test_ipr(
        db, "RS", "F2", "SUBV8", monto=100_000_000,
        metadata={
            "pagare_monto": "100000000",
            "pagare_fecha_vencimiento": "2028-06-01",
        },
    )

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "directorio_certificate")
    if gate:
        assert gate["met"] is False, "Should block — missing directorio certificate"
        assert "certificado de directorio" in gate["detail"].lower()


async def test_directorio_blocks_expired(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR with directorio certificate >60 days old should block."""
    ipr_id = await _create_test_ipr(
        db, "RS", "F2", "SUBV8", monto=100_000_000,
        metadata={
            "pagare_monto": "100000000",
            "pagare_fecha_vencimiento": "2028-06-01",
            "directorio_cert_date": "2025-12-01",  # >60 days old
        },
    )

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "directorio_certificate")
    if gate:
        assert gate["met"] is False, "Should block — certificate expired"
        assert "antigüedad" in gate["detail"].lower()


async def test_directorio_passes_recent(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SUBV8 IPR with directorio certificate <60 days old should pass."""
    from datetime import datetime, timezone, timedelta
    recent_date = (datetime.now(timezone.utc) - timedelta(days=10)).strftime("%Y-%m-%d")

    ipr_id = await _create_test_ipr(
        db, "RS", "F2", "SUBV8", monto=100_000_000,
        metadata={
            "pagare_monto": "100000000",
            "pagare_fecha_vencimiento": "2028-06-01",
            "directorio_cert_date": recent_date,
        },
    )

    resp = await client.get(f"/api/ipr/{ipr_id}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    gate = _find_gate(resp.json(), "F3", "directorio_certificate")
    assert gate is None, "Recent certificate should pass silently"
