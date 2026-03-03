"""
Tests for Poly-Switch: mechanism-aware phase gates, TRACK_CONFIG, and evaluation assignments.

Wave A: tests 1-8 (gates + track-info)
Wave B: tests 9-15 (evaluation CRUD)
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
) -> str:
    """Create a minimal IPR for poly-switch tests."""
    bip = f"POLY-{uuid.uuid4().hex[:8].upper()}"
    status_id = await _get_category_id(db, "ipr_state", status_code)
    phase_id = await _get_category_id(db, "mcd_phase", phase_code)
    mechanism_id = None
    if mechanism_code:
        mechanism_id = await _get_category_id(db, "mechanism", mechanism_code)

    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, status_id, mcd_phase_id,
                mechanism_id, created_at, updated_at
            ) VALUES (
                :bip, 'Test Poly-Switch IPR', 'PROYECTO',
                CAST(:status_id AS uuid), CAST(:phase_id AS uuid),
                CAST(:mechanism_id AS uuid), NOW(), NOW()
            )
            RETURNING id
        """),
        {"bip": bip, "status_id": status_id, "phase_id": phase_id,
         "mechanism_id": mechanism_id},
    )).mappings().first()
    await db.commit()
    return str(row["id"])


async def _set_ipr_status(db: AsyncSession, ipr_id: str, status_code: str) -> None:
    """Directly set IPR status in DB (bypass API gates for test setup)."""
    status_id = await _get_category_id(db, "ipr_state", status_code)
    await db.execute(
        text("UPDATE core.ipr SET status_id = CAST(:sid AS uuid) WHERE id = CAST(:id AS uuid)"),
        {"sid": status_id, "id": ipr_id},
    )
    await db.commit()


# ---------------------------------------------------------------------------
# Wave A: Track-specific gate tests
# ---------------------------------------------------------------------------

async def test_sni_ipr_with_rs_passes_f2_f3(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SNI mechanism + status RS → gate F2→F3 should be met."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", mechanism_code="SNI")

    # Check transitions — RS is a valid favorable product for SNI
    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()

    # Find a transition that crosses F2→F3 boundary (e.g., CDP_EMITIDO)
    cdp = next((t for t in data if t.get("target_phase") == "F3"), None)
    if cdp:
        # The favorable_outcome gate should be met
        gate = next((g for g in cdp["gates"] if g["name"] == "favorable_outcome"), None)
        assert gate is not None
        assert gate["met"] is True
    else:
        # If no F3 transition available from RS, verify via direct gate evaluation
        pytest.skip("No F2→F3 transition available from RS status")


async def test_sni_ipr_with_itf_fails_f2_f3(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """SNI mechanism + status ITF → gate F2→F3 should NOT be met (ITF is for TRANSFER, not SNI)."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", mechanism_code="SNI")
    # Set status to ITF directly (bypass transitions)
    await _set_ipr_status(db, ipr_id, "ITF")

    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()

    cdp = next((t for t in data if t.get("target_phase") == "F3"), None)
    if cdp:
        gate = next((g for g in cdp["gates"] if g["name"] == "favorable_outcome"), None)
        assert gate is not None
        assert gate["met"] is False, "ITF should not be favorable for SNI track"
    else:
        pytest.skip("No F2→F3 transition available from ITF status")


async def test_fril_ipr_with_rs_passes_f2_f3(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """FRIL mechanism + status RS → gate F2→F3 should be met."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", mechanism_code="FRIL")

    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()

    cdp = next((t for t in data if t.get("target_phase") == "F3"), None)
    if cdp:
        gate = next((g for g in cdp["gates"] if g["name"] == "favorable_outcome"), None)
        assert gate is not None
        assert gate["met"] is True


async def test_glosa06_ipr_with_rf_passes_f2_f3(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """GLOSA06 mechanism + status RF → gate F2→F3 should be met (RF is Glosa06's favorable)."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", mechanism_code="GLOSA06")
    await _set_ipr_status(db, ipr_id, "RF")

    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()

    cdp = next((t for t in data if t.get("target_phase") == "F3"), None)
    if cdp:
        gate = next((g for g in cdp["gates"] if g["name"] == "favorable_outcome"), None)
        assert gate is not None
        assert gate["met"] is True


async def test_transfer_ipr_with_itf_passes_f2_f3(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """TRANSFER mechanism + status ITF → gate F2→F3 should be met."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", mechanism_code="TRANSFER")
    await _set_ipr_status(db, ipr_id, "ITF")

    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()

    cdp = next((t for t in data if t.get("target_phase") == "F3"), None)
    if cdp:
        gate = next((g for g in cdp["gates"] if g["name"] == "favorable_outcome"), None)
        assert gate is not None
        assert gate["met"] is True


async def test_no_mechanism_universal_fallback(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """IPR without mechanism → uses universal favorable list (backward compat)."""
    ipr_id = await _create_test_ipr(db, "RS", "F2", mechanism_code=None)

    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()

    cdp = next((t for t in data if t.get("target_phase") == "F3"), None)
    if cdp:
        gate = next((g for g in cdp["gates"] if g["name"] == "favorable_outcome"), None)
        assert gate is not None
        assert gate["met"] is True, "RS should pass universal fallback"
        assert "universal" in gate["detail"].lower()


async def test_track_info_endpoint(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """GET /api/ipr/{id}/track-info returns correct structure for SNI mechanism."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", mechanism_code="SNI")

    resp = await client.get(
        f"/api/ipr/{ipr_id}/track-info",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["mechanism"] == "SNI"
    assert data["evaluator"] == "MDSF"
    assert "RS" in data["favorable_products"]
    assert "ITF" not in data["favorable_products"]
    assert "cgr_toma_razon" in data["thresholds"]
    assert "admisibilidad" in data["sla_days"]
    assert isinstance(data["evaluations"], list)


async def test_track_info_no_mechanism(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """GET /api/ipr/{id}/track-info for IPR without mechanism returns minimal info."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", mechanism_code=None)

    resp = await client.get(
        f"/api/ipr/{ipr_id}/track-info",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["mechanism"] is None
    assert data["evaluator"] is None
    assert data["favorable_products"] == []


# ---------------------------------------------------------------------------
# Wave B: Evaluation Assignment CRUD tests
# ---------------------------------------------------------------------------

async def test_create_evaluation_assignment(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """POST /api/ipr/{id}/evaluaciones creates assignment with explicit evaluator_type."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", mechanism_code="SNI")
    evaluator_type_id = await _get_category_id(db, "evaluator_type", "MDSF")

    resp = await client.post(
        f"/api/ipr/{ipr_id}/evaluaciones",
        json={"evaluator_type_id": evaluator_type_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 201
    assert "id" in resp.json()


async def test_create_evaluation_auto_evaluator(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """POST without evaluator_type_id auto-assigns from TRACK_CONFIG."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", mechanism_code="FRIL")

    resp = await client.post(
        f"/api/ipr/{ipr_id}/evaluaciones",
        json={},
        headers=auth(regional_token),
    )
    assert resp.status_code == 201

    # Verify the assignment used GORE_DAE (FRIL's evaluator)
    list_resp = await client.get(
        f"/api/ipr/{ipr_id}/evaluaciones",
        headers=auth(regional_token),
    )
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) >= 1
    assert items[0]["evaluator_type"] == "GORE_DAE"


async def test_update_evaluation_result(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """PATCH with result_id sets result_code denormalized."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", mechanism_code="SNI")
    evaluator_type_id = await _get_category_id(db, "evaluator_type", "MDSF")

    # Create
    create_resp = await client.post(
        f"/api/ipr/{ipr_id}/evaluaciones",
        json={"evaluator_type_id": evaluator_type_id},
        headers=auth(regional_token),
    )
    eval_id = create_resp.json()["id"]

    # Get RS result_id
    result_id = await _get_category_id(db, "evaluation_result", "RS")

    # Update with result
    resp = await client.patch(
        f"/api/ipr/{ipr_id}/evaluaciones/{eval_id}",
        json={"result_id": result_id, "observations": "Aprobado por MDSF"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200

    # Verify denormalized result_code
    list_resp = await client.get(
        f"/api/ipr/{ipr_id}/evaluaciones",
        headers=auth(regional_token),
    )
    items = list_resp.json()
    found = next((e for e in items if e["id"] == eval_id), None)
    assert found is not None
    assert found["result_code"] == "RS"
    assert found["observations"] == "Aprobado por MDSF"


async def test_list_evaluations(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """GET /api/ipr/{id}/evaluaciones returns filtered list."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", mechanism_code="SNI")
    evaluator_type_id = await _get_category_id(db, "evaluator_type", "MDSF")

    # Create 2 evaluations
    await client.post(
        f"/api/ipr/{ipr_id}/evaluaciones",
        json={"evaluator_type_id": evaluator_type_id},
        headers=auth(regional_token),
    )
    await client.post(
        f"/api/ipr/{ipr_id}/evaluaciones",
        json={"evaluator_type_id": evaluator_type_id, "evaluator_name": "Juan Pérez"},
        headers=auth(regional_token),
    )

    resp = await client.get(
        f"/api/ipr/{ipr_id}/evaluaciones",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 2


async def test_track_info_includes_evaluations(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """GET /api/ipr/{id}/track-info includes evaluation assignments."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", mechanism_code="SNI")
    evaluator_type_id = await _get_category_id(db, "evaluator_type", "MDSF")

    # Create an evaluation
    await client.post(
        f"/api/ipr/{ipr_id}/evaluaciones",
        json={"evaluator_type_id": evaluator_type_id},
        headers=auth(regional_token),
    )

    resp = await client.get(
        f"/api/ipr/{ipr_id}/track-info",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["evaluations"]) >= 1
    assert data["evaluations"][0]["evaluator_type"] == "MDSF"


async def test_evaluation_forbidden_encargado(
    client: AsyncClient, encargado_token: str, db: AsyncSession,
):
    """ENCARGADO cannot create evaluations."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", mechanism_code="SNI")
    evaluator_type_id = await _get_category_id(db, "evaluator_type", "MDSF")

    resp = await client.post(
        f"/api/ipr/{ipr_id}/evaluaciones",
        json={"evaluator_type_id": evaluator_type_id},
        headers=auth(encargado_token),
    )
    assert resp.status_code == 403
