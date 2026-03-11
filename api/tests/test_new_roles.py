"""Tests for new roles: ANALISTA, RTF, ASESOR_JURIDICO.

Validates that each new role can access its intended endpoints
and is correctly blocked from unauthorized endpoints.
"""
import pytest
from httpx import AsyncClient
from tests.conftest import auth


# ─────────────────────────────────────────────────────────────────────────────
# ANALISTA — F0-F3: Create IPR, manage satellites, create CDPs
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_analista_can_list_ipr(client: AsyncClient, analista_token: str):
    resp = await client.get("/api/ipr", params={"page": 1, "page_size": 1}, headers=auth(analista_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_analista_can_create_ipr(client: AsyncClient, analista_token: str, db):
    """ANALISTA should be able to create an IPR (F0 Postulación)."""
    from sqlalchemy import text

    ipr_type = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'ipr_type' LIMIT 1")
    )
    ipr_type_id = str(ipr_type.scalar())

    resp = await client.post("/api/ipr", json={
        "codigo_bip": "ROLE-TEST-001",
        "name": "Test IPR from ANALISTA",
        "ipr_type_id": ipr_type_id,
    }, headers=auth(analista_token))
    assert resp.status_code == 201, resp.text


@pytest.mark.asyncio
async def test_analista_can_list_compromisos(client: AsyncClient, analista_token: str):
    """ANALISTA can list operational commitments."""
    resp = await client.get("/api/compromisos", headers=auth(analista_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_analista_cannot_create_compromiso(client: AsyncClient, analista_token: str, catalog: dict):
    """ANALISTA should NOT create commitments (requires JEFE_DIVISION+)."""
    resp = await client.post("/api/compromisos", json={
        "description": "Test commitment from ANALISTA",
        "commitment_type_id": catalog["commitment_type_id"],
        "responsible_id": catalog["users"]["admin@goreos.cl"]["id"],
        "due_date": "2026-12-31",
    }, headers=auth(analista_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_analista_cannot_access_admin(client: AsyncClient, analista_token: str):
    """ANALISTA should NOT access admin endpoints."""
    resp = await client.get("/api/admin/usuarios", headers=auth(analista_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_analista_cannot_access_dgi(client: AsyncClient, analista_token: str):
    """ANALISTA should NOT access DGI-only endpoints."""
    resp = await client.get("/api/dgi/cartera", headers=auth(analista_token))
    assert resp.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# RTF — F5: Review rendiciones SISREC
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rtf_can_list_rendiciones(client: AsyncClient, rtf_token: str):
    """RTF should access rendiciones list."""
    resp = await client.get("/api/dgi/data/rendiciones", headers=auth(rtf_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_rtf_can_list_problemas(client: AsyncClient, rtf_token: str):
    """RTF can list problems (via WRITE_OPERATIONAL_ROLES)."""
    resp = await client.get("/api/problemas", headers=auth(rtf_token))
    assert resp.status_code == 200


async def _create_test_ipr(db, suffix="001"):
    """Helper: create a minimal IPR for tests that need FK references."""
    from sqlalchemy import text
    ipr_type = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'ipr_type' LIMIT 1")
    )
    ipr_type_id = ipr_type.scalar()
    result = await db.execute(text("""
        INSERT INTO core.ipr (codigo_bip, name, ipr_type_id, ipr_nature)
        VALUES (:code, 'IPR for rendition test', :type_id, 'PROYECTO')
        RETURNING id
    """), {"code": f"ROLE-REND-{suffix}", "type_id": str(ipr_type_id)})
    ipr_id = result.scalar()
    await db.commit()
    return ipr_id


@pytest.mark.asyncio
async def test_rtf_can_transition_rendicion_to_visada(client: AsyncClient, rtf_token: str, db):
    """RTF should be able to visar a rendición in EN_REVISION_RTF (H-04 fix)."""
    from sqlalchemy import text

    state = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'EN_REVISION_RTF'")
    )
    state_rtf_id = state.scalar()
    if state_rtf_id is None:
        pytest.skip("rendition_state EN_REVISION_RTF not seeded")

    visada = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'VISADA_RTF'")
    )
    visada_id = visada.scalar()
    if visada_id is None:
        pytest.skip("rendition_state VISADA_RTF not seeded")

    ipr_id = await _create_test_ipr(db, "001")

    result = await db.execute(text("""
        INSERT INTO core.rendition (ipr_id, state_id, period_start, period_end, amount)
        VALUES (:ipr_id, :state_id, '2026-01-01', '2026-01-31', 1000000)
        RETURNING id
    """), {"ipr_id": str(ipr_id), "state_id": str(state_rtf_id)})
    rend_id = str(result.scalar())
    await db.commit()

    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rend_id}",
        json={"state_id": str(visada_id)},
        headers=auth(rtf_token),
    )
    assert resp.status_code == 200, f"RTF should visar rendición: {resp.text}"


@pytest.mark.asyncio
async def test_rtf_cannot_approve_rendicion(client: AsyncClient, rtf_token: str, db):
    """RTF should NOT approve rendiciones (EN_REVISION_UCR → APROBADA is DGI-only)."""
    from sqlalchemy import text

    state_ucr = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'EN_REVISION_UCR'")
    )
    state_ucr_id = state_ucr.scalar()
    if state_ucr_id is None:
        pytest.skip("rendition_state EN_REVISION_UCR not seeded")

    aprobada = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'APROBADA'")
    )
    aprobada_id = aprobada.scalar()

    ipr_id = await _create_test_ipr(db, "002")

    result = await db.execute(text("""
        INSERT INTO core.rendition (ipr_id, state_id, period_start, period_end, amount)
        VALUES (:ipr_id, :state_id, '2026-02-01', '2026-02-28', 500000)
        RETURNING id
    """), {"ipr_id": str(ipr_id), "state_id": str(state_ucr_id)})
    rend_id = str(result.scalar())
    await db.commit()

    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rend_id}",
        json={"state_id": str(aprobada_id)},
        headers=auth(rtf_token),
    )
    assert resp.status_code == 403, "RTF should NOT approve rendiciones"


@pytest.mark.asyncio
async def test_rtf_cannot_create_ipr(client: AsyncClient, rtf_token: str, db):
    """RTF should NOT be able to create IPR (not in _CREATE_ROLES)."""
    from sqlalchemy import text

    ipr_type = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'ipr_type' LIMIT 1")
    )
    ipr_type_id = str(ipr_type.scalar())

    resp = await client.post("/api/ipr", json={
        "codigo_bip": "ROLE-RTF-001",
        "name": "Test IPR from RTF",
        "ipr_type_id": ipr_type_id,
    }, headers=auth(rtf_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_rtf_cannot_access_admin(client: AsyncClient, rtf_token: str):
    """RTF should NOT access admin endpoints."""
    resp = await client.get("/api/admin/usuarios", headers=auth(rtf_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_rtf_cannot_access_dgi(client: AsyncClient, rtf_token: str):
    """RTF should NOT access DGI-only endpoints."""
    resp = await client.get("/api/dgi/cartera", headers=auth(rtf_token))
    assert resp.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# ASESOR_JURIDICO — F4: V.B. legalidad actos y convenios
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_juridico_can_list_convenios(client: AsyncClient, juridico_token: str):
    """ASESOR_JURIDICO should access convenios."""
    resp = await client.get("/api/convenios", headers=auth(juridico_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_juridico_can_list_actos(client: AsyncClient, juridico_token: str):
    """ASESOR_JURIDICO should access administrative acts list."""
    resp = await client.get("/api/actos", headers=auth(juridico_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_juridico_cannot_create_ipr(client: AsyncClient, juridico_token: str, db):
    """ASESOR_JURIDICO should NOT be able to create IPR."""
    from sqlalchemy import text

    ipr_type = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'ipr_type' LIMIT 1")
    )
    ipr_type_id = str(ipr_type.scalar())

    resp = await client.post("/api/ipr", json={
        "codigo_bip": "ROLE-JUR-001",
        "name": "Test IPR from JURIDICO",
        "ipr_type_id": ipr_type_id,
    }, headers=auth(juridico_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_juridico_cannot_access_admin(client: AsyncClient, juridico_token: str):
    """ASESOR_JURIDICO should NOT access admin endpoints."""
    resp = await client.get("/api/admin/usuarios", headers=auth(juridico_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_juridico_cannot_access_dgi(client: AsyncClient, juridico_token: str):
    """ASESOR_JURIDICO should NOT access DGI-only endpoints (uses /dgi/cartera which has guard)."""
    resp = await client.get("/api/dgi/cartera", headers=auth(juridico_token))
    assert resp.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# Cross-role: login verification
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize("email", [
    "analista.dipir@goreos.cl",
    "rtf.daf@goreos.cl",
    "juridico@goreos.cl",
])
async def test_new_roles_can_login(client: AsyncClient, email: str):
    """All new role users should be able to login."""
    resp = await client.post("/api/auth/login", data={
        "username": email,
        "password": "admin123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
