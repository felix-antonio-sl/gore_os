"""
Tests for IPR lifecycle Wave 3: closure records + ex-post evaluations + F5 states.
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


async def _create_test_ipr(db: AsyncSession, status_code: str = "EN_RENDICION", phase: str = "F5") -> str:
    bip = f"CLO-{uuid.uuid4().hex[:8].upper()}"
    status_id = await _get_cat_id(db, "ipr_state", status_code)
    phase_id = await _get_cat_id(db, "mcd_phase", phase)
    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, status_id, mcd_phase_id,
                created_at, updated_at
            ) VALUES (
                :bip, 'Closure Test IPR', 'PROGRAMA',
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
# F5 States
# ---------------------------------------------------------------------------

async def test_rendicion_aprobada_state_exists(db: AsyncSession):
    """RENDICION_APROBADA state should exist."""
    sid = await _get_cat_id(db, "ipr_state", "RENDICION_APROBADA")
    assert sid is not None


async def test_en_cierre_administrativo_state_exists(db: AsyncSession):
    """EN_CIERRE_ADMINISTRATIVO state should exist."""
    sid = await _get_cat_id(db, "ipr_state", "EN_CIERRE_ADMINISTRATIVO")
    assert sid is not None


async def test_en_rendicion_to_rendicion_aprobada(client: AsyncClient, regional_token: str, db: AsyncSession):
    """EN_RENDICION → RENDICION_APROBADA should succeed."""
    ipr_id = await _create_test_ipr(db, "EN_RENDICION")
    target_id = await _get_cat_id(db, "ipr_state", "RENDICION_APROBADA")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}", json={"status_id": target_id}, headers=auth(regional_token),
    )
    assert resp.status_code == 200


async def test_rendicion_aprobada_to_en_cierre(client: AsyncClient, regional_token: str, db: AsyncSession):
    """RENDICION_APROBADA → EN_CIERRE_ADMINISTRATIVO should succeed."""
    ipr_id = await _create_test_ipr(db, "RENDICION_APROBADA")
    target_id = await _get_cat_id(db, "ipr_state", "EN_CIERRE_ADMINISTRATIVO")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}", json={"status_id": target_id}, headers=auth(regional_token),
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Closure CRUD
# ---------------------------------------------------------------------------

async def test_create_closure(client: AsyncClient, regional_token: str, db: AsyncSession):
    """POST /api/ipr/{id}/cierre creates a closure record."""
    ipr_id = await _create_test_ipr(db, "EN_CIERRE_ADMINISTRATIVO")
    resp = await client.post(
        f"/api/ipr/{ipr_id}/cierre",
        json={
            "closure_date": "2026-03-11",
            "closure_report": "IPR completado satisfactoriamente",
            "physical_completion": 100.0,
            "financial_completion": 98.5,
            "final_amount": 150000000,
        },
        headers=auth(regional_token),
    )
    assert resp.status_code == 201
    assert "id" in resp.json()


async def test_get_closure(client: AsyncClient, regional_token: str, db: AsyncSession):
    """GET /api/ipr/{id}/cierre returns the closure record."""
    ipr_id = await _create_test_ipr(db, "EN_CIERRE_ADMINISTRATIVO")
    await client.post(
        f"/api/ipr/{ipr_id}/cierre",
        json={"closure_date": "2026-03-11", "physical_completion": 95.0},
        headers=auth(regional_token),
    )
    resp = await client.get(
        f"/api/ipr/{ipr_id}/cierre", headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data is not None
    assert data["physical_completion"] == 95.0


async def test_closure_duplicate_rejected(client: AsyncClient, regional_token: str, db: AsyncSession):
    """Cannot create two closure records for the same IPR."""
    ipr_id = await _create_test_ipr(db, "EN_CIERRE_ADMINISTRATIVO")
    await client.post(
        f"/api/ipr/{ipr_id}/cierre", json={"closure_date": "2026-03-11"}, headers=auth(regional_token),
    )
    resp = await client.post(
        f"/api/ipr/{ipr_id}/cierre", json={"closure_date": "2026-03-12"}, headers=auth(regional_token),
    )
    assert resp.status_code == 409


async def test_sign_closure(client: AsyncClient, regional_token: str, db: AsyncSession):
    """PATCH /api/ipr/{id}/cierre with sign=true sets signed_by and signed_at."""
    ipr_id = await _create_test_ipr(db, "EN_CIERRE_ADMINISTRATIVO")
    await client.post(
        f"/api/ipr/{ipr_id}/cierre", json={"closure_date": "2026-03-11"}, headers=auth(regional_token),
    )
    resp = await client.patch(
        f"/api/ipr/{ipr_id}/cierre", json={"sign": True}, headers=auth(regional_token),
    )
    assert resp.status_code == 200

    # Verify signature
    row = (await db.execute(
        text("SELECT signed_by_id, signed_at FROM core.ipr_closure WHERE ipr_id = CAST(:id AS uuid)"),
        {"id": ipr_id},
    )).mappings().first()
    assert row["signed_by_id"] is not None
    assert row["signed_at"] is not None


# ---------------------------------------------------------------------------
# Closure Gate: EN_CIERRE_ADMINISTRATIVO → CERRADO
# ---------------------------------------------------------------------------

async def test_cierre_to_cerrado_without_firma_blocked(client: AsyncClient, regional_token: str, db: AsyncSession):
    """EN_CIERRE_ADMINISTRATIVO → CERRADO should be blocked without signed closure."""
    ipr_id = await _create_test_ipr(db, "EN_CIERRE_ADMINISTRATIVO")
    # Create closure but don't sign
    await client.post(
        f"/api/ipr/{ipr_id}/cierre", json={"closure_date": "2026-03-11"}, headers=auth(regional_token),
    )
    target_id = await _get_cat_id(db, "ipr_state", "CERRADO")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}", json={"status_id": target_id}, headers=auth(regional_token),
    )
    assert resp.status_code == 409
    assert "cierre" in resp.json()["detail"].lower()


async def test_cierre_to_cerrado_with_firma_succeeds(client: AsyncClient, regional_token: str, db: AsyncSession):
    """EN_CIERRE_ADMINISTRATIVO → CERRADO should succeed with signed closure."""
    ipr_id = await _create_test_ipr(db, "EN_CIERRE_ADMINISTRATIVO")
    await client.post(
        f"/api/ipr/{ipr_id}/cierre", json={"closure_date": "2026-03-11"}, headers=auth(regional_token),
    )
    await client.patch(
        f"/api/ipr/{ipr_id}/cierre", json={"sign": True}, headers=auth(regional_token),
    )
    target_id = await _get_cat_id(db, "ipr_state", "CERRADO")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}", json={"status_id": target_id}, headers=auth(regional_token),
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Ex-Post Evaluations
# ---------------------------------------------------------------------------

async def test_expost_only_for_cerrado(client: AsyncClient, regional_token: str, db: AsyncSession):
    """Cannot create ex-post evaluation for non-CERRADO IPR."""
    ipr_id = await _create_test_ipr(db, "EN_RENDICION")
    eval_type_id = await _get_cat_id(db, "expost_eval_type", "SIMPLIFICADA")
    resp = await client.post(
        f"/api/ipr/{ipr_id}/evaluacion-expost",
        json={"evaluation_type_id": eval_type_id, "evaluation_date": "2026-03-11"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409


async def test_create_expost_evaluation(client: AsyncClient, regional_token: str, db: AsyncSession):
    """POST /api/ipr/{id}/evaluacion-expost for CERRADO IPR works."""
    ipr_id = await _create_test_ipr(db, "CERRADO")
    eval_type_id = await _get_cat_id(db, "expost_eval_type", "SIMPLIFICADA")
    rating_id = await _get_cat_id(db, "expost_rating", "SATISFACTORIO")

    resp = await client.post(
        f"/api/ipr/{ipr_id}/evaluacion-expost",
        json={
            "evaluation_type_id": eval_type_id,
            "evaluation_date": "2026-03-11",
            "impact_score": 85.5,
            "sustainability_score": 72.0,
            "efficiency_score": 90.0,
            "effectiveness_score": 78.5,
            "overall_rating_id": rating_id,
            "findings": "Impacto positivo en la comunidad",
            "recommendations": "Replicar en otras comunas",
            "lessons_learned": "Importancia de la participación ciudadana",
        },
        headers=auth(regional_token),
    )
    assert resp.status_code == 201


async def test_list_expost_evaluations(client: AsyncClient, regional_token: str, db: AsyncSession):
    """GET /api/ipr/{id}/evaluacion-expost lists evaluations."""
    ipr_id = await _create_test_ipr(db, "CERRADO")
    eval_type_id = await _get_cat_id(db, "expost_eval_type", "PROFUNDIDAD")

    await client.post(
        f"/api/ipr/{ipr_id}/evaluacion-expost",
        json={"evaluation_type_id": eval_type_id, "evaluation_date": "2026-03-11"},
        headers=auth(regional_token),
    )

    resp = await client.get(
        f"/api/ipr/{ipr_id}/evaluacion-expost", headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["eval_type_code"] == "PROFUNDIDAD"


async def test_status_phase_fiber_f5_states(db: AsyncSession):
    """Verify STATUS_PHASE_FIBER includes new F5 states."""
    from app.routers.ipr import STATUS_PHASE_FIBER
    assert STATUS_PHASE_FIBER["RENDICION_APROBADA"] == "F5"
    assert STATUS_PHASE_FIBER["EN_CIERRE_ADMINISTRATIVO"] == "F5"
