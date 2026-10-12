"""Rendition capture, state authority and SISREC evidence used by the inbox."""

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth


@pytest.mark.asyncio
async def test_list_rendiciones(client: AsyncClient, dgi_token):
    """GET /api/dgi/data/rendiciones returns paginated renditions."""
    resp = await client.get(
        "/api/dgi/data/rendiciones?page=1&page_size=10",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_create_rendicion(client: AsyncClient, dgi_token, db):
    """POST /api/dgi/data/rendiciones creates a new rendition."""
    from sqlalchemy import text as sa_text

    # Get an IPR to link to
    ipr_row = (await db.execute(
        sa_text("SELECT id FROM core.ipr WHERE deleted_at IS NULL LIMIT 1")
    )).mappings().first()
    if not ipr_row:
        pytest.skip("No IPRs in test DB")

    resp = await client.post(
        "/api/dgi/data/rendiciones",
        json={
            "ipr_id": str(ipr_row["id"]),
            "period_start": "2026-01-01",
            "period_end": "2026-03-31",
            "amount": 1500000,
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_create_rendicion_requires_link(client: AsyncClient, dgi_token):
    """POST /api/dgi/data/rendiciones requires agreement_id or ipr_id."""
    resp = await client.post(
        "/api/dgi/data/rendiciones",
        json={
            "period_start": "2026-01-01",
            "period_end": "2026-03-31",
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_rendicion_detail(client: AsyncClient, dgi_token, db):
    """GET /api/dgi/data/rendiciones/{id} returns rendition detail with history."""
    from sqlalchemy import text as sa_text

    ipr_row = (await db.execute(
        sa_text("SELECT id FROM core.ipr WHERE deleted_at IS NULL LIMIT 1")
    )).mappings().first()
    if not ipr_row:
        pytest.skip("No IPRs in test DB")

    create_resp = await client.post(
        "/api/dgi/data/rendiciones",
        json={
            "ipr_id": str(ipr_row["id"]),
            "amount": 500000,
        },
        headers=auth(dgi_token),
    )
    rend_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/dgi/data/rendiciones/{rend_id}",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == rend_id
    assert data["state_code"] == "PENDIENTE"
    assert "history" in data
    assert "days_in_state" in data


@pytest.mark.asyncio
async def test_rendicion_fsm_transition(client: AsyncClient, dgi_token, db):
    """PATCH /api/dgi/data/rendiciones/{id} transitions PENDIENTE→EN_REVISION_RTF."""
    from sqlalchemy import text as sa_text

    ipr_row = (await db.execute(
        sa_text("SELECT id FROM core.ipr WHERE deleted_at IS NULL LIMIT 1")
    )).mappings().first()
    if not ipr_row:
        pytest.skip("No IPRs in test DB")

    create_resp = await client.post(
        "/api/dgi/data/rendiciones",
        json={"ipr_id": str(ipr_row["id"]), "amount": 100000},
        headers=auth(dgi_token),
    )
    rend_id = create_resp.json()["id"]

    # Get the EN_REVISION_RTF state_id
    state_row = (await db.execute(
        sa_text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'EN_REVISION_RTF'")
    )).mappings().first()
    assert state_row

    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rend_id}",
        json={"state_id": str(state_row["id"])},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200

    # Verify the state changed
    detail = await client.get(
        f"/api/dgi/data/rendiciones/{rend_id}",
        headers=auth(dgi_token),
    )
    assert detail.json()["state_code"] == "EN_REVISION_RTF"


@pytest.mark.asyncio
async def test_rendicion_invalid_transition(client: AsyncClient, dgi_token, db):
    """PATCH rejects invalid transition PENDIENTE→APROBADA."""
    from sqlalchemy import text as sa_text

    ipr_row = (await db.execute(
        sa_text("SELECT id FROM core.ipr WHERE deleted_at IS NULL LIMIT 1")
    )).mappings().first()
    if not ipr_row:
        pytest.skip("No IPRs in test DB")

    create_resp = await client.post(
        "/api/dgi/data/rendiciones",
        json={"ipr_id": str(ipr_row["id"]), "amount": 100000},
        headers=auth(dgi_token),
    )
    rend_id = create_resp.json()["id"]

    # Get APROBADA state_id
    state_row = (await db.execute(
        sa_text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'APROBADA'")
    )).mappings().first()

    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rend_id}",
        json={"state_id": str(state_row["id"])},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_rendicion_phases(client: AsyncClient, dgi_token):
    """GET /api/dgi/data/rendiciones/fases returns phase definitions."""
    resp = await client.get(
        "/api/dgi/data/rendiciones/fases",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if len(data) > 0:
        phase = data[0]
        assert "code" in phase
        assert "name" in phase
        assert "sla_days" in phase
        assert "ordinal" in phase


@pytest.mark.asyncio
async def test_rendiciones_vencidas(client: AsyncClient, dgi_token):
    """GET /api/dgi/data/rendiciones/vencidas returns overdue renditions."""
    resp = await client.get(
        "/api/dgi/data/rendiciones/vencidas?page=1&page_size=10",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_rendicion_ciclo(client: AsyncClient, dgi_token, db):
    """GET /api/dgi/data/rendiciones/{id}/ciclo returns phase timeline."""
    from sqlalchemy import text as sa_text

    ipr_row = (await db.execute(
        sa_text("SELECT id FROM core.ipr WHERE deleted_at IS NULL LIMIT 1")
    )).mappings().first()
    if not ipr_row:
        pytest.skip("No IPRs in test DB")

    create_resp = await client.post(
        "/api/dgi/data/rendiciones",
        json={"ipr_id": str(ipr_row["id"]), "amount": 200000},
        headers=auth(dgi_token),
    )
    rend_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/dgi/data/rendiciones/{rend_id}/ciclo",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "rendicion_id" in data
    assert "current_state" in data
    assert "phases" in data
    assert "total_elapsed_days" in data
    assert isinstance(data["phases"], list)


@pytest.mark.asyncio
async def test_rendicion_escalamientos(client: AsyncClient, dgi_token, db):
    """GET /api/dgi/data/rendiciones/{id}/escalamientos returns escalation list."""
    from sqlalchemy import text as sa_text

    ipr_row = (await db.execute(
        sa_text("SELECT id FROM core.ipr WHERE deleted_at IS NULL LIMIT 1")
    )).mappings().first()
    if not ipr_row:
        pytest.skip("No IPRs in test DB")

    create_resp = await client.post(
        "/api/dgi/data/rendiciones",
        json={"ipr_id": str(ipr_row["id"]), "amount": 300000},
        headers=auth(dgi_token),
    )
    rend_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/dgi/data/rendiciones/{rend_id}/escalamientos",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_check_escalations(client: AsyncClient, dgi_token):
    """POST /api/dgi/data/rendiciones/check-escalations runs batch check."""
    resp = await client.post(
        "/api/dgi/data/rendiciones/check-escalations",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "checked" in data
    assert "new_escalations" in data
    assert "details" in data


@pytest.mark.asyncio
async def test_archive_rendicion_requires_aprobada(client: AsyncClient, dgi_token, db):
    """PATCH /api/dgi/data/rendiciones/{id}/archivar rejects non-APROBADA renditions."""
    from sqlalchemy import text as sa_text

    ipr_row = (await db.execute(
        sa_text("SELECT id FROM core.ipr WHERE deleted_at IS NULL LIMIT 1")
    )).mappings().first()
    if not ipr_row:
        pytest.skip("No IPRs in test DB")

    create_resp = await client.post(
        "/api/dgi/data/rendiciones",
        json={"ipr_id": str(ipr_row["id"]), "amount": 100000},
        headers=auth(dgi_token),
    )
    rend_id = create_resp.json()["id"]

    # Try to archive PENDIENTE — should fail
    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rend_id}/archivar",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Rendiciones resumen
# ---------------------------------------------------------------------------


async def test_rendiciones_resumen(client, dgi_token):
    """GET /api/dgi/data/rendiciones/resumen returns aggregate stats."""
    resp = await client.get("/api/dgi/data/rendiciones/resumen", headers=auth(dgi_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "total" in body
    assert "active" in body
    assert "sla_compliance_pct" in body
    assert "by_state" in body
    assert isinstance(body["by_state"], list)
    # SLA compliance should be 0-100
    assert 0 <= body["sla_compliance_pct"] <= 100
