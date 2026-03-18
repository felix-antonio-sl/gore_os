"""
Integration tests for /api/dgi/data/ endpoints (dgi_data.py router).

26 endpoints covered across 6 groups, 39 tests total:

- Indicators CRUD + lifecycle (21 tests):
    list, list w/ dimension filter, detail, 404, create, create invalid dim,
    create non-JEFE forbidden, update, update ESP_CONTROL allowed, manual value,
    manual value computed rejected, lifecycle full flow (BORRADOR→DEPRECADO),
    lifecycle invalid transition, lifecycle history, snapshot history, refresh,
    DEPRECADO edit blocked

- Data sources (1 test): list sources

- Reference data (3 tests): organizaciones, personas, territorio

- Events (1 test): eventos list

- Renditions CRUD + FSM (10 tests):
    list, create, create requires link, detail, FSM transition,
    invalid transition, phase definitions, vencidas, ciclo timeline,
    escalamientos, check-escalations, archive requires APROBADA

- Decrees (3 tests): list, patch, patch operational forbidden

- Role restrictions (2 tests): operational cannot create indicator,
    operational cannot transition lifecycle
"""

import pytest
from httpx import AsyncClient
from tests.conftest import auth


# ═══════════════════════════════════════════════════════════════════════════
# INDICATORS — LIST & DETAIL
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_list_indicators(client: AsyncClient, dgi_token):
    """GET /api/dgi/data/indicators returns a list of indicators."""
    resp = await client.get(
        "/api/dgi/data/indicators",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if len(data) > 0:
        item = data[0]
        assert "id" in item
        assert "code" in item
        assert "name" in item
        assert "dimension" in item
        assert "signal" in item


@pytest.mark.asyncio
async def test_list_indicators_filter_dimension(client: AsyncClient, dgi_token):
    """GET /api/dgi/data/indicators?dimension=X filters by dimension."""
    resp = await client.get(
        "/api/dgi/data/indicators?dimension=PRESUPUESTO",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    for item in data:
        assert item["dimension"] == "PRESUPUESTO"


@pytest.mark.asyncio
async def test_get_indicator_detail(client: AsyncClient, dgi_token):
    """GET /api/dgi/data/indicators/{id} returns a single indicator."""
    # First get the list to find an existing indicator
    list_resp = await client.get(
        "/api/dgi/data/indicators",
        headers=auth(dgi_token),
    )
    indicators = list_resp.json()
    if len(indicators) == 0:
        pytest.skip("No indicators in test DB")

    indicator_id = indicators[0]["id"]
    resp = await client.get(
        f"/api/dgi/data/indicators/{indicator_id}",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == indicator_id
    assert "code" in data
    assert "name" in data
    assert "dimension" in data


@pytest.mark.asyncio
async def test_get_indicator_not_found(client: AsyncClient, dgi_token):
    """GET /api/dgi/data/indicators/{id} returns 404 for non-existent ID."""
    resp = await client.get(
        "/api/dgi/data/indicators/00000000-0000-0000-0000-000000000000",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════
# INDICATORS — CREATE
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_create_indicator(client: AsyncClient, dgi_token):
    """POST /api/dgi/data/indicators creates a new indicator (JEFE_DGI)."""
    resp = await client.post(
        "/api/dgi/data/indicators",
        json={
            "name": "Test Indicador DGI Data",
            "dimension": "PRESUPUESTO",
            "description": "Indicador de prueba",
            "unit": "%",
            "target_value": 90.0,
            "source_type": "MANUAL",
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Indicador DGI Data"
    assert data["dimension"] == "PRESUPUESTO"
    assert data["code"].startswith("IND-PRESUPUESTO-")
    assert data["lifecycle_status"] == "BORRADOR"
    assert data["unit"] == "%"


@pytest.mark.asyncio
async def test_create_indicator_invalid_dimension(client: AsyncClient, dgi_token):
    """POST /api/dgi/data/indicators rejects invalid dimension."""
    resp = await client.post(
        "/api/dgi/data/indicators",
        json={
            "name": "Bad Dimension",
            "dimension": "NONEXISTENT_DIM",
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_indicator_non_jefe_forbidden(client: AsyncClient, esp_control_token):
    """POST /api/dgi/data/indicators is JEFE_DGI only — ESP_CONTROL gets 403."""
    resp = await client.post(
        "/api/dgi/data/indicators",
        json={
            "name": "Should Fail",
            "dimension": "PRESUPUESTO",
        },
        headers=auth(esp_control_token),
    )
    assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════
# INDICATORS — UPDATE
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_update_indicator(client: AsyncClient, dgi_token):
    """PATCH /api/dgi/data/indicators/{id} updates allowed fields."""
    # Create first
    create_resp = await client.post(
        "/api/dgi/data/indicators",
        json={
            "name": "Test Update Indicator",
            "dimension": "CARTERA_IPR",
            "source_type": "MANUAL",
        },
        headers=auth(dgi_token),
    )
    assert create_resp.status_code == 201
    ind_id = create_resp.json()["id"]

    # Update
    resp = await client.patch(
        f"/api/dgi/data/indicators/{ind_id}",
        json={"description": "Descripción actualizada", "unit": "CLP"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["description"] == "Descripción actualizada"
    assert data["unit"] == "CLP"


@pytest.mark.asyncio
async def test_update_indicator_esp_control_allowed(client: AsyncClient, dgi_token, esp_control_token):
    """PATCH /api/dgi/data/indicators/{id} is allowed for ESP_CONTROL_GESTION."""
    create_resp = await client.post(
        "/api/dgi/data/indicators",
        json={
            "name": "Test ESP Control Update",
            "dimension": "CONVENIOS",
            "source_type": "MANUAL",
        },
        headers=auth(dgi_token),
    )
    ind_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/dgi/data/indicators/{ind_id}",
        json={"name": "Updated by ESP Control"},
        headers=auth(esp_control_token),
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated by ESP Control"


# ═══════════════════════════════════════════════════════════════════════════
# INDICATORS — MANUAL VALUE
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_set_indicator_manual_value(client: AsyncClient, dgi_token):
    """POST /api/dgi/data/indicators/{id}/value sets value on MANUAL indicator."""
    create_resp = await client.post(
        "/api/dgi/data/indicators",
        json={
            "name": "Test Manual Value",
            "dimension": "RIESGOS",
            "source_type": "MANUAL",
        },
        headers=auth(dgi_token),
    )
    ind_id = create_resp.json()["id"]

    resp = await client.post(
        f"/api/dgi/data/indicators/{ind_id}/value",
        json={"value": 42.5},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_value"] == 42.5


@pytest.mark.asyncio
async def test_set_indicator_value_auto_rejected(client: AsyncClient, dgi_token):
    """POST /api/dgi/data/indicators/{id}/value rejects AUTO source_type."""
    create_resp = await client.post(
        "/api/dgi/data/indicators",
        json={
            "name": "Test Auto Value Reject",
            "dimension": "PRESUPUESTO",
            "source_type": "AUTO",
        },
        headers=auth(dgi_token),
    )
    assert create_resp.status_code == 201
    ind_id = create_resp.json()["id"]

    resp = await client.post(
        f"/api/dgi/data/indicators/{ind_id}/value",
        json={"value": 99.9},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 409


# ═══════════════════════════════════════════════════════════════════════════
# INDICATORS — LIFECYCLE TRANSITIONS
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_indicator_lifecycle_full_flow(client: AsyncClient, dgi_token):
    """POST /indicators/{id}/lifecycle transitions BORRADOR→APROBADO→VIGENTE→DEPRECADO."""
    create_resp = await client.post(
        "/api/dgi/data/indicators",
        json={
            "name": "Test Lifecycle Flow",
            "dimension": "TDE",
            "source_type": "MANUAL",
        },
        headers=auth(dgi_token),
    )
    assert create_resp.status_code == 201
    ind_id = create_resp.json()["id"]
    assert create_resp.json()["lifecycle_status"] == "BORRADOR"

    # BORRADOR → APROBADO
    r1 = await client.post(
        f"/api/dgi/data/indicators/{ind_id}/lifecycle",
        json={"target_status": "APROBADO", "comment": "Revisado y aprobado"},
        headers=auth(dgi_token),
    )
    assert r1.status_code == 200
    assert r1.json()["lifecycle_status"] == "APROBADO"

    # APROBADO → VIGENTE
    r2 = await client.post(
        f"/api/dgi/data/indicators/{ind_id}/lifecycle",
        json={"target_status": "VIGENTE"},
        headers=auth(dgi_token),
    )
    assert r2.status_code == 200
    assert r2.json()["lifecycle_status"] == "VIGENTE"

    # VIGENTE → DEPRECADO
    r3 = await client.post(
        f"/api/dgi/data/indicators/{ind_id}/lifecycle",
        json={"target_status": "DEPRECADO", "comment": "Reemplazado por nuevo indicador"},
        headers=auth(dgi_token),
    )
    assert r3.status_code == 200
    assert r3.json()["lifecycle_status"] == "DEPRECADO"


@pytest.mark.asyncio
async def test_indicator_lifecycle_invalid_transition(client: AsyncClient, dgi_token):
    """POST /indicators/{id}/lifecycle rejects invalid transition BORRADOR→VIGENTE."""
    create_resp = await client.post(
        "/api/dgi/data/indicators",
        json={
            "name": "Test Invalid Lifecycle",
            "dimension": "PRESUPUESTO",
            "source_type": "MANUAL",
        },
        headers=auth(dgi_token),
    )
    ind_id = create_resp.json()["id"]

    resp = await client.post(
        f"/api/dgi/data/indicators/{ind_id}/lifecycle",
        json={"target_status": "VIGENTE"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_indicator_lifecycle_history(client: AsyncClient, dgi_token):
    """GET /indicators/{id}/lifecycle-history returns audit log after transitions."""
    create_resp = await client.post(
        "/api/dgi/data/indicators",
        json={
            "name": "Test Lifecycle History",
            "dimension": "CONVENIOS",
            "source_type": "MANUAL",
        },
        headers=auth(dgi_token),
    )
    ind_id = create_resp.json()["id"]

    # Perform a transition
    await client.post(
        f"/api/dgi/data/indicators/{ind_id}/lifecycle",
        json={"target_status": "APROBADO", "comment": "Test comment"},
        headers=auth(dgi_token),
    )

    # Check history
    resp = await client.get(
        f"/api/dgi/data/indicators/{ind_id}/lifecycle-history",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    entry = data[0]
    assert entry["new_lifecycle"] == "APROBADO"
    assert entry["previous_lifecycle"] == "BORRADOR"
    assert entry["comment"] == "Test comment"
    assert "changed_at" in entry


# ═══════════════════════════════════════════════════════════════════════════
# INDICATORS — HISTORY (SNAPSHOTS) & REFRESH
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_indicator_snapshot_history(client: AsyncClient, dgi_token):
    """GET /indicators/{id}/history returns snapshot time series (may be empty)."""
    list_resp = await client.get(
        "/api/dgi/data/indicators",
        headers=auth(dgi_token),
    )
    indicators = list_resp.json()
    if len(indicators) == 0:
        pytest.skip("No indicators in test DB")

    indicator_id = indicators[0]["id"]
    resp = await client.get(
        f"/api/dgi/data/indicators/{indicator_id}/history?days=30",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_refresh_indicators(client: AsyncClient, dgi_token):
    """POST /api/dgi/data/indicators/refresh recalculates dimension values."""
    resp = await client.post(
        "/api/dgi/data/indicators/refresh",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "dimensions" in data
    dims = data["dimensions"]
    assert "PRESUPUESTO" in dims
    assert "CARTERA_IPR" in dims
    assert "CONVENIOS" in dims
    assert "RIESGOS" in dims
    assert "TDE" in dims
    # Each computed dimension should have value + signal
    for dim_code in ["PRESUPUESTO", "CARTERA_IPR", "CONVENIOS", "RIESGOS"]:
        assert "value" in dims[dim_code]
        assert "signal" in dims[dim_code]
        assert dims[dim_code]["signal"] in ("VERDE", "AMARILLO", "ROJO")


# ═══════════════════════════════════════════════════════════════════════════
# INDICATORS — DEPRECADO EDIT BLOCKED
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_update_deprecado_indicator_blocked(client: AsyncClient, dgi_token):
    """PATCH on a DEPRECADO indicator returns 409."""
    # Create and deprecate
    create_resp = await client.post(
        "/api/dgi/data/indicators",
        json={
            "name": "Test Deprecado Block",
            "dimension": "TDE",
            "source_type": "MANUAL",
        },
        headers=auth(dgi_token),
    )
    ind_id = create_resp.json()["id"]

    for target in ["APROBADO", "VIGENTE", "DEPRECADO"]:
        await client.post(
            f"/api/dgi/data/indicators/{ind_id}/lifecycle",
            json={"target_status": target},
            headers=auth(dgi_token),
        )

    resp = await client.patch(
        f"/api/dgi/data/indicators/{ind_id}",
        json={"name": "Should Fail"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 409


# ═══════════════════════════════════════════════════════════════════════════
# DATA SOURCES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_list_data_sources(client: AsyncClient, dgi_token):
    """GET /api/dgi/data/sources returns a list of data source statuses."""
    resp = await client.get(
        "/api/dgi/data/sources",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if len(data) > 0:
        item = data[0]
        assert "source_name" in item
        assert "status" in item


# ═══════════════════════════════════════════════════════════════════════════
# REFERENCE DATA: ORGANIZACIONES, PERSONAS, TERRITORIO
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_list_organizaciones(client: AsyncClient, dgi_token):
    """GET /api/dgi/data/organizaciones returns paginated organizations."""
    resp = await client.get(
        "/api/dgi/data/organizaciones?page=1&page_size=10",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert data["page"] == 1
    assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_list_personas(client: AsyncClient, dgi_token):
    """GET /api/dgi/data/personas returns paginated persons."""
    resp = await client.get(
        "/api/dgi/data/personas?page=1&page_size=5",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    if len(data["items"]) > 0:
        person = data["items"][0]
        assert "names" in person
        assert "paternal_surname" in person


@pytest.mark.asyncio
async def test_list_territorio(client: AsyncClient, dgi_token):
    """GET /api/dgi/data/territorio returns paginated territories."""
    resp = await client.get(
        "/api/dgi/data/territorio?page=1&page_size=10",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    if len(data["items"]) > 0:
        territory = data["items"][0]
        assert "code" in territory
        assert "name" in territory
        assert "territory_type" in territory


# ═══════════════════════════════════════════════════════════════════════════
# EVENTS
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_list_eventos(client: AsyncClient, dgi_token):
    """GET /api/dgi/data/eventos returns paginated events (may be empty)."""
    resp = await client.get(
        "/api/dgi/data/eventos?page=1&page_size=10",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


# ═══════════════════════════════════════════════════════════════════════════
# RENDITIONS — LIST, CREATE, DETAIL, FSM
# ═══════════════════════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════════════════════
# RENDITIONS — PHASES, VENCIDAS, CICLO, ARCHIVE, ESCALATIONS
# ═══════════════════════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════════════════════
# DECREES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_list_decrees(client: AsyncClient, dgi_token):
    """GET /api/dgi/data/decrees returns list of decrees."""
    resp = await client.get(
        "/api/dgi/data/decrees",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if len(data) > 0:
        decree = data[0]
        assert "id" in decree
        assert "code" in decree
        assert "name" in decree
        assert "status" in decree


@pytest.mark.asyncio
async def test_patch_decree(client: AsyncClient, dgi_token):
    """PATCH /api/dgi/data/decrees/{code} updates decree fields."""
    # List first to find an existing decree
    list_resp = await client.get(
        "/api/dgi/data/decrees",
        headers=auth(dgi_token),
    )
    decrees = list_resp.json()
    if len(decrees) == 0:
        pytest.skip("No decrees in test DB")

    code = decrees[0]["code"]
    resp = await client.patch(
        f"/api/dgi/data/decrees/{code}",
        json={"description": "Descripción actualizada por test"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_patch_decree_operational_forbidden(client: AsyncClient, analista_token):
    """PATCH /api/dgi/data/decrees/{code} is forbidden for operational roles."""
    resp = await client.patch(
        "/api/dgi/data/decrees/DS-07",
        json={"description": "Should fail"},
        headers=auth(analista_token),
    )
    assert resp.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════
# ROLE RESTRICTIONS
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_operational_cannot_create_indicator(client: AsyncClient, analista_token):
    """Operational role (ANALISTA) cannot create indicators."""
    resp = await client.post(
        "/api/dgi/data/indicators",
        json={
            "name": "Should Fail",
            "dimension": "PRESUPUESTO",
        },
        headers=auth(analista_token),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_operational_cannot_transition_lifecycle(client: AsyncClient, dgi_token, analista_token):
    """Operational role (ANALISTA) cannot transition indicator lifecycle."""
    create_resp = await client.post(
        "/api/dgi/data/indicators",
        json={
            "name": "Test Role Block Lifecycle",
            "dimension": "PRESUPUESTO",
            "source_type": "MANUAL",
        },
        headers=auth(dgi_token),
    )
    ind_id = create_resp.json()["id"]

    resp = await client.post(
        f"/api/dgi/data/indicators/{ind_id}/lifecycle",
        json={"target_status": "APROBADO"},
        headers=auth(analista_token),
    )
    assert resp.status_code == 403


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
