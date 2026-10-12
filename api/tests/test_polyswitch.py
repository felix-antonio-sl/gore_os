"""
Tests for Poly-Switch: mechanism-aware phase gates, TRACK_CONFIG, and evaluation assignments.

Wave A: tests 1-8 (gates + track-info)
Wave B: tests 9-15 (evaluation CRUD)
"""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
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
    assignee_id: str | None = None,
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
                mechanism_id, assignee_id, created_at, updated_at
            ) VALUES (
                :bip, 'Test Poly-Switch IPR', 'PROYECTO',
                CAST(:status_id AS uuid), CAST(:phase_id AS uuid),
                CAST(:mechanism_id AS uuid), CAST(:assignee_id AS uuid), NOW(), NOW()
            )
            RETURNING id
        """),
        {"bip": bip, "status_id": status_id, "phase_id": phase_id,
         "mechanism_id": mechanism_id, "assignee_id": assignee_id},
    )).mappings().first()
    await db.commit()
    return str(row["id"])


# ---------------------------------------------------------------------------
# Wave A: Track-specific gate tests
# ---------------------------------------------------------------------------


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
    assert data["mechanism_label"]
    assert data["mechanism_attrs"] == {}
    assert set(data) == {"mechanism", "mechanism_label", "mechanism_attrs"}


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
    assert data["mechanism_label"] is None
    assert data["mechanism_attrs"] == {}


# ---------------------------------------------------------------------------
# Wave B: Evaluation Assignment CRUD tests
# ---------------------------------------------------------------------------


async def test_db_rejects_completed_evaluation_without_result(
    db: AsyncSession,
):
    """A direct writer cannot complete an evaluation without a dictamen."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", mechanism_code="SNI")
    evaluator_type_id = await _get_category_id(db, "evaluator_type", "MDSF")

    try:
        with pytest.raises(DBAPIError, match="cannot complete without result_id"):
            await db.execute(
                text("""
                    INSERT INTO core.evaluation_assignment (
                        ipr_id, evaluator_type_id, completed_at
                    ) VALUES (
                        CAST(:ipr_id AS uuid), CAST(:evaluator_type_id AS uuid), NOW()
                    )
                """),
                {"ipr_id": ipr_id, "evaluator_type_id": evaluator_type_id},
            )
    finally:
        await db.rollback()


async def test_db_derives_result_code_from_result_id(
    db: AsyncSession,
):
    """result_id is authoritative even when a direct writer supplies a stale code."""
    ipr_id = await _create_test_ipr(db, "EN_EVALUACION", "F2", mechanism_code="SNI")
    evaluator_type_id = await _get_category_id(db, "evaluator_type", "MDSF")
    result_id = await _get_category_id(db, "evaluation_result", "RS")

    try:
        stored_code = (await db.execute(
            text("""
                INSERT INTO core.evaluation_assignment (
                    ipr_id, evaluator_type_id, result_id, result_code
                ) VALUES (
                    CAST(:ipr_id AS uuid), CAST(:evaluator_type_id AS uuid),
                    CAST(:result_id AS uuid), 'FI'
                )
                RETURNING result_code
            """),
            {
                "ipr_id": ipr_id,
                "evaluator_type_id": evaluator_type_id,
                "result_id": result_id,
            },
        )).scalar_one()
        assert stored_code == "RS"
    finally:
        await db.rollback()
