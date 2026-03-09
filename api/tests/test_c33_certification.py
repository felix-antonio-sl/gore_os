"""Tests for C33 technical certification workflow (gate at F1→F2)."""
import uuid
import json
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
    )).scalar()
    assert row, f"{scheme}/{code} not found"
    return str(row)


async def _create_c33_ipr(
    db: AsyncSession,
    status_code: str = "ADMISIBLE",
    phase_code: str = "F1",
    categoria: str | None = None,
    informe: bool | None = None,
    cert_metadata: dict | None = None,
) -> str:
    """Create a C33 IPR with optional certification metadata."""
    bip = f"C33-{uuid.uuid4().hex[:8].upper()}"
    status_id = await _get_category_id(db, "ipr_state", status_code)
    phase_id = await _get_category_id(db, "mcd_phase", phase_code)
    mechanism_id = await _get_category_id(db, "mechanism", "C33")

    meta = cert_metadata or {}
    if categoria:
        meta["categoria_c33"] = categoria
    if informe is not None:
        meta["informe_tecnico_favorable"] = informe
    meta_json = json.dumps(meta)

    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (
                codigo_bip, name, ipr_nature, status_id, mcd_phase_id,
                mechanism_id, metadata, created_at, updated_at
            ) VALUES (
                :bip, 'Test C33 IPR', 'PROYECTO',
                CAST(:status_id AS uuid), CAST(:phase_id AS uuid),
                CAST(:mechanism_id AS uuid),
                CAST(:metadata AS jsonb), NOW(), NOW()
            )
            RETURNING id
        """),
        {
            "bip": bip, "status_id": status_id, "phase_id": phase_id,
            "mechanism_id": mechanism_id, "metadata": meta_json,
        },
    )).mappings().first()
    await db.commit()
    return str(row["id"])


# ---------------------------------------------------------------------------
# Gate tests
# ---------------------------------------------------------------------------

async def test_c33_gate_blocks_no_categoria(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """F1→F2: blocks C33 IPR without categoria_c33."""
    ipr_id = await _create_c33_ipr(db, "ADMISIBLE", "F1")
    target_id = await _get_category_id(db, "ipr_state", "EN_EVALUACION")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409
    assert "categor" in resp.json()["detail"].lower()


async def test_c33_gate_blocks_no_certification(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """F1→F2: blocks C33 IPR with categoria but no certification result."""
    ipr_id = await _create_c33_ipr(db, "ADMISIBLE", "F1", categoria="EDIFICACION")
    target_id = await _get_category_id(db, "ipr_state", "EN_EVALUACION")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409
    detail = resp.json()["detail"].lower()
    assert "pendiente" in detail or "serviu" in detail


async def test_c33_gate_blocks_unfavorable(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """F1→F2: blocks C33 IPR with unfavorable certification."""
    ipr_id = await _create_c33_ipr(
        db, "ADMISIBLE", "F1", categoria="VIALIDAD", informe=False,
    )
    target_id = await _get_category_id(db, "ipr_state", "EN_EVALUACION")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409
    assert "desfavorable" in resp.json()["detail"].lower()


async def test_c33_gate_passes_favorable(
    client: AsyncClient, regional_token: str, db: AsyncSession,
):
    """F1→F2: allows C33 IPR with favorable certification."""
    ipr_id = await _create_c33_ipr(
        db, "ADMISIBLE", "F1", categoria="EDIFICACION", informe=True,
    )
    target_id = await _get_category_id(db, "ipr_state", "EN_EVALUACION")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}",
        json={"status_id": target_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Endpoint tests
# ---------------------------------------------------------------------------

# ── GET status endpoint ──

async def test_get_certification_status_empty(client: AsyncClient, regional_token: str, db: AsyncSession):
    """GET returns empty status for IPR without certification."""
    ipr_id = await _create_c33_ipr(db, "EN_REVISION", "F1", categoria="EDIFICACION")
    resp = await client.get(
        f"/api/ipr/{ipr_id}/certificacion-tecnica",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["categoria_c33"] == "EDIFICACION"
    assert data["certifier_org"] == "SERVIU"
    assert data["requested"] is False
    assert data["resolved"] is False


# ── POST solicitar endpoint ──

async def test_solicitar_certification(client: AsyncClient, jefe_token: str, db: AsyncSession):
    """JEFE_DIVISION can request certification."""
    ipr_id = await _create_c33_ipr(db, "EN_REVISION", "F1", categoria="EDIFICACION")
    resp = await client.post(
        f"/api/ipr/{ipr_id}/certificacion-tecnica/solicitar",
        json={},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["certifier_org"] == "SERVIU"
    assert data["requested_at"] is not None


async def test_solicitar_no_categoria(client: AsyncClient, jefe_token: str, db: AsyncSession):
    """POST solicitar fails if categoria_c33 not assigned."""
    ipr_id = await _create_c33_ipr(db, "EN_REVISION", "F1")
    resp = await client.post(
        f"/api/ipr/{ipr_id}/certificacion-tecnica/solicitar",
        json={},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 409


async def test_solicitar_wrong_role(client: AsyncClient, encargado_token: str, db: AsyncSession):
    """ENCARGADO cannot request certification."""
    ipr_id = await _create_c33_ipr(db, "EN_REVISION", "F1", categoria="EDIFICACION")
    resp = await client.post(
        f"/api/ipr/{ipr_id}/certificacion-tecnica/solicitar",
        json={},
        headers=auth(encargado_token),
    )
    assert resp.status_code == 403


# ── PATCH resolver endpoint ──

async def test_resolver_favorable(client: AsyncClient, jefe_token: str, regional_token: str, db: AsyncSession):
    """ADMIN_REGIONAL can register favorable result."""
    ipr_id = await _create_c33_ipr(db, "EN_REVISION", "F1", categoria="VIALIDAD")
    await client.post(
        f"/api/ipr/{ipr_id}/certificacion-tecnica/solicitar",
        json={},
        headers=auth(jefe_token),
    )
    resp = await client.patch(
        f"/api/ipr/{ipr_id}/certificacion-tecnica",
        json={"favorable": True, "document_reference": "ORD. 123/2026"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    assert resp.json()["informe_tecnico_favorable"] is True


async def test_resolver_without_request(client: AsyncClient, regional_token: str, db: AsyncSession):
    """Cannot resolve without prior request."""
    ipr_id = await _create_c33_ipr(db, "EN_REVISION", "F1", categoria="EDIFICACION")
    resp = await client.patch(
        f"/api/ipr/{ipr_id}/certificacion-tecnica",
        json={"favorable": True},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409


async def test_resolver_wrong_role(client: AsyncClient, jefe_token: str, db: AsyncSession):
    """JEFE_DIVISION cannot resolve certification."""
    ipr_id = await _create_c33_ipr(db, "EN_REVISION", "F1", categoria="EDIFICACION")
    await client.post(
        f"/api/ipr/{ipr_id}/certificacion-tecnica/solicitar",
        json={},
        headers=auth(jefe_token),
    )
    resp = await client.patch(
        f"/api/ipr/{ipr_id}/certificacion-tecnica",
        json={"favorable": True},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 403
