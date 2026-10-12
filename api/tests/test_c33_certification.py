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
    sponsor_division_id: str | None = None,
) -> str:
    """Create a C33 IPR with optional certification metadata."""
    bip = f"C33-{uuid.uuid4().hex[:8].upper()}"
    status_id = await _get_category_id(db, "ipr_state", status_code)
    phase_id = await _get_category_id(db, "mcd_phase", phase_code)
    mechanism_id = await _get_category_id(db, "mechanism", "C33")

    # Default sponsor_division_id to DAF for scope check compatibility
    if not sponsor_division_id:
        sponsor_division_id = str((await db.execute(
            text("SELECT id FROM core.organization WHERE code = 'DAF' AND deleted_at IS NULL")
        )).scalar())

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
                mechanism_id, metadata, sponsor_division_id, created_at, updated_at
            ) VALUES (
                :bip, 'Test C33 IPR', 'PROYECTO',
                CAST(:status_id AS uuid), CAST(:phase_id AS uuid),
                CAST(:mechanism_id AS uuid),
                CAST(:metadata AS jsonb), CAST(:div_id AS uuid), NOW(), NOW()
            )
            RETURNING id
        """),
        {
            "bip": bip, "status_id": status_id, "phase_id": phase_id,
            "mechanism_id": mechanism_id, "metadata": meta_json,
            "div_id": sponsor_division_id,
        },
    )).mappings().first()
    await db.commit()
    return str(row["id"])


# ---------------------------------------------------------------------------
# Gate tests
# ---------------------------------------------------------------------------


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


# ── PATCH resolver endpoint ──
