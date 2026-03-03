"""Tests para SISREC MVP — POST /api/dgi/data/rendiciones + GET detail."""
import uuid
import pytest
from sqlalchemy import text
from tests.conftest import auth


async def _get_ipr_id(db) -> str:
    """Obtener un IPR existente en el test DB."""
    r = await db.execute(text("SELECT id FROM core.ipr LIMIT 1"))
    return str(r.scalar())


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_rendicion_with_ipr(client, dgi_token, db):
    """POST con ipr_id → 201, estado inicial PENDIENTE en DB."""
    ipr_id = await _get_ipr_id(db)

    resp = await client.post(
        "/api/dgi/data/rendiciones",
        json={"ipr_id": ipr_id},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert "id" in data

    # Verificar estado en DB
    row = (await db.execute(
        text("""
            SELECT rc.code AS state_code
            FROM core.rendition r
            JOIN ref.category rc ON rc.id = r.state_id
            WHERE r.id = :id
        """),
        {"id": data["id"]},
    )).mappings().first()
    assert row is not None
    assert row["state_code"] == "PENDIENTE"


@pytest.mark.asyncio
async def test_create_rendicion_missing_link(client, dgi_token, db):
    """POST sin agreement_id ni ipr_id → 422 Unprocessable."""
    resp = await client.post(
        "/api/dgi/data/rendiciones",
        json={},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 422, resp.text


@pytest.mark.asyncio
async def test_create_rendicion_operativa_role(client, regional_token, db):
    """POST como ADMIN_REGIONAL (rol operativo) → 201 (operativa registra recepción)."""
    ipr_id = await _get_ipr_id(db)

    resp = await client.post(
        "/api/dgi/data/rendiciones",
        json={"ipr_id": ipr_id},
        headers=auth(regional_token),
    )
    assert resp.status_code == 201, resp.text
    assert "id" in resp.json()


@pytest.mark.asyncio
async def test_get_rendicion_detail(client, dgi_token, db):
    """POST luego GET /{id} → state_code PENDIENTE, ipr_id presente."""
    ipr_id = await _get_ipr_id(db)

    create_resp = await client.post(
        "/api/dgi/data/rendiciones",
        json={"ipr_id": ipr_id},
        headers=auth(dgi_token),
    )
    assert create_resp.status_code == 201
    rendicion_id = create_resp.json()["id"]

    get_resp = await client.get(
        f"/api/dgi/data/rendiciones/{rendicion_id}",
        headers=auth(dgi_token),
    )
    assert get_resp.status_code == 200, get_resp.text
    detail = get_resp.json()
    assert detail["state_code"] == "PENDIENTE"
    assert detail["ipr_id"] == ipr_id


@pytest.mark.asyncio
async def test_get_rendicion_not_found(client, dgi_token, db):
    """GET con UUID aleatorio → 404."""
    random_id = str(uuid.uuid4())
    resp = await client.get(
        f"/api/dgi/data/rendiciones/{random_id}",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 404, resp.text
