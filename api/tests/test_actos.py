"""Tests for administrative acts CRUD + 7-step workflow."""
import pytest
from datetime import datetime
from sqlalchemy import text
from tests.conftest import auth


# ---------------------------------------------------------------------------
# Catalog fixture extension — act-specific IDs
# ---------------------------------------------------------------------------

@pytest.fixture
def act_catalog(catalog):
    """Extends base catalog with act-specific IDs (populated by conftest catalog)."""
    return catalog


@pytest.fixture
def _act_ids():
    """Lazy container for act state IDs — filled per-test from DB."""
    return {}


async def _fetch_act_ids(db) -> dict:
    """Fetch act_type and act_state IDs from test DB."""
    ids = {}

    # act_type RESOLUCION
    r = await db.execute(text("SELECT id FROM ref.category WHERE scheme = 'act_type' AND code = 'RESOLUCION'"))
    ids["act_type_resolucion_id"] = str(r.scalar())

    # act_type OFICIO
    r = await db.execute(text("SELECT id FROM ref.category WHERE scheme = 'act_type' AND code = 'OFICIO'"))
    ids["act_type_oficio_id"] = str(r.scalar())

    # act_state BORRADOR
    r = await db.execute(text("SELECT id FROM ref.category WHERE scheme = 'act_state' AND code = 'BORRADOR'"))
    ids["state_borrador_id"] = str(r.scalar())

    # act_state EN_REVISION
    r = await db.execute(text("SELECT id FROM ref.category WHERE scheme = 'act_state' AND code = 'EN_REVISION'"))
    ids["state_en_revision_id"] = str(r.scalar())

    # act_state VISADO
    r = await db.execute(text("SELECT id FROM ref.category WHERE scheme = 'act_state' AND code = 'VISADO'"))
    ids["state_visado_id"] = str(r.scalar())

    # act_state FIRMADO
    r = await db.execute(text("SELECT id FROM ref.category WHERE scheme = 'act_state' AND code = 'FIRMADO'"))
    ids["state_firmado_id"] = str(r.scalar())

    # act_state ANULADO
    r = await db.execute(text("SELECT id FROM ref.category WHERE scheme = 'act_state' AND code = 'ANULADO'"))
    ids["state_anulado_id"] = str(r.scalar())

    # resolution_type (first)
    r = await db.execute(text("SELECT id FROM ref.category WHERE scheme = 'resolution_type' LIMIT 1"))
    ids["resolution_type_id"] = str(r.scalar())

    return ids


async def _create_acto(client, token, act_ids, *, act_type_key="act_type_resolucion_id", **overrides):
    """Helper to create an act with defaults."""
    payload = {
        "act_type_id": act_ids[act_type_key],
        "subject": "Acto de prueba",
        "issued_at": datetime.now().isoformat(),
        "requires_cgr": False,
        "resolution_type_id": act_ids["resolution_type_id"],
        **overrides,
    }
    # Remove resolution_type_id for non-RESOLUCION types
    if act_type_key != "act_type_resolucion_id":
        payload.pop("resolution_type_id", None)

    resp = await client.post("/api/actos", json=payload, headers=auth(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_act_resolution(client, regional_token, db):
    """POST creates act + resolution pair for RESOLUCION type."""
    act_ids = await _fetch_act_ids(db)
    data = await _create_acto(client, regional_token, act_ids)

    assert "id" in data
    assert data["act_number"].startswith("ACT-")
    assert data["resolution_id"] is not None

    # Verify resolution exists in DB
    res = await db.execute(
        text("SELECT id FROM core.resolution WHERE administrative_act_id = :aid"),
        {"aid": data["id"]},
    )
    assert res.scalar() is not None


@pytest.mark.asyncio
async def test_create_act_oficio(client, regional_token, db):
    """POST creates act without resolution for OFICIO type."""
    act_ids = await _fetch_act_ids(db)
    data = await _create_acto(
        client, regional_token, act_ids,
        act_type_key="act_type_oficio_id",
        subject="Oficio de prueba",
    )

    assert "id" in data
    assert data["resolution_id"] is None


@pytest.mark.asyncio
async def test_list_paginated(client, regional_token, db):
    """GET /api/actos returns paginated response."""
    resp = await client.get("/api/actos?page_size=5", headers=auth(regional_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert body["total"] > 0
    assert len(body["items"]) <= 5


@pytest.mark.asyncio
async def test_get_detail(client, regional_token, db):
    """GET /api/actos/{id} returns detail."""
    act_ids = await _fetch_act_ids(db)
    created = await _create_acto(client, regional_token, act_ids)

    resp = await client.get(f"/api/actos/{created['id']}", headers=auth(regional_token))
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["act_type"] == "RESOLUCION"
    assert detail["state"] == "BORRADOR"
    assert "created_at" in detail


@pytest.mark.asyncio
async def test_state_transition_valid(client, regional_token, db):
    """BORRADOR -> EN_REVISION succeeds."""
    act_ids = await _fetch_act_ids(db)
    created = await _create_acto(client, regional_token, act_ids)

    resp = await client.patch(
        f"/api/actos/{created['id']}",
        json={"state_id": act_ids["state_en_revision_id"]},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200

    # Verify state changed
    detail = await client.get(f"/api/actos/{created['id']}", headers=auth(regional_token))
    assert detail.json()["state"] == "EN_REVISION"


@pytest.mark.asyncio
async def test_state_transition_invalid(client, regional_token, db):
    """BORRADOR -> FIRMADO is blocked (must go through EN_REVISION, VISADO)."""
    act_ids = await _fetch_act_ids(db)
    created = await _create_acto(client, regional_token, act_ids)

    resp = await client.patch(
        f"/api/actos/{created['id']}",
        json={"state_id": act_ids["state_firmado_id"]},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_anulado_from_any(client, regional_token, db):
    """ANULADO permitted from EN_REVISION (cross-cutting)."""
    act_ids = await _fetch_act_ids(db)
    created = await _create_acto(client, regional_token, act_ids)

    # Move to EN_REVISION first
    await client.patch(
        f"/api/actos/{created['id']}",
        json={"state_id": act_ids["state_en_revision_id"]},
        headers=auth(regional_token),
    )

    # Now ANULADO should work
    resp = await client.patch(
        f"/api/actos/{created['id']}",
        json={"state_id": act_ids["state_anulado_id"]},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200

    detail = await client.get(f"/api/actos/{created['id']}", headers=auth(regional_token))
    assert detail.json()["state"] == "ANULADO"


@pytest.mark.asyncio
async def test_transitions_endpoint(client, regional_token, db):
    """GET transiciones returns valid states + ANULADO."""
    act_ids = await _fetch_act_ids(db)
    created = await _create_acto(client, regional_token, act_ids)

    resp = await client.get(f"/api/actos/{created['id']}/transiciones", headers=auth(regional_token))
    assert resp.status_code == 200
    transitions = resp.json()

    codes = [t["code"] for t in transitions]
    assert "EN_REVISION" in codes  # normal transition from BORRADOR
    assert "ANULADO" in codes      # cross-cutting


@pytest.mark.asyncio
async def test_link_resolution_to_ipr(client, regional_token, db):
    """PATCH ipr_id updates resolution."""
    act_ids = await _fetch_act_ids(db)
    created = await _create_acto(client, regional_token, act_ids)

    # Create a minimal IPR for linking
    ipr_result = await db.execute(text("SELECT id FROM core.ipr LIMIT 1"))
    ipr_row = ipr_result.scalar()
    if not ipr_row:
        # Insert a minimal IPR if none exists in test DB
        ins = await db.execute(
            text("""
                INSERT INTO core.ipr (codigo_bip, name, ipr_nature, created_at, updated_at)
                VALUES ('99999999-0', 'Test IPR for actos', 'PROYECTO', NOW(), NOW())
                RETURNING id
            """)
        )
        ipr_id = str(ins.scalar())
        await db.commit()
    else:
        ipr_id = str(ipr_row)

    resp = await client.patch(
        f"/api/actos/{created['id']}",
        json={"ipr_id": ipr_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200, resp.text

    # Verify resolution was updated
    res = await db.execute(
        text("SELECT ipr_id FROM core.resolution WHERE administrative_act_id = :aid"),
        {"aid": created["id"]},
    )
    assert str(res.scalar()) == ipr_id
