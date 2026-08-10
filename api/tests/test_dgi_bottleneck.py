"""
Integration tests for DGI Bottleneck Detection & Investigation router.

13 tests covering:
- Scan detection endpoint (1)
- Summary endpoint (1)
- Investigation CRUD: create, list, detail, delete (4)
- Investigation FSM: full chain, direct close, and API/DB invalid transitions (4)
- Field update via PATCH (1)
- Role restrictions for non-DGI and read-only DGI roles (2)
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth


# ═══════════════════════════════════════════════════════════════════════════
# SCAN & SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_scan_detection(client: AsyncClient, esp_control_token):
    """Scan endpoint returns 200 with findings array."""
    resp = await client.get(
        "/api/dgi/data/bottlenecks/scan",
        params={"threshold_acumulacion": 1},
        headers=auth(esp_control_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Each finding should have required keys
    for finding in data:
        assert "finding_type" in finding
        assert finding["finding_type"] in ("ACUMULACION", "CICLO_TIEMPO", "PRESUPUESTO")
        assert "severity" in finding
        assert "detection_value" in finding
        assert "detection_threshold" in finding


@pytest.mark.asyncio
async def test_summary_endpoint(client: AsyncClient, dgi_token):
    """Summary endpoint returns aggregated structure."""
    resp = await client.get(
        "/api/dgi/data/bottlenecks/summary",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_active" in data
    assert "by_status" in data
    assert "by_division" in data
    assert "critical_count" in data
    assert isinstance(data["by_status"], list)
    assert isinstance(data["by_division"], list)


# ═══════════════════════════════════════════════════════════════════════════
# INVESTIGATION CRUD
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_investigation_create(client: AsyncClient, esp_control_token):
    """ESP_CONTROL_GESTION can create a bottleneck investigation."""
    resp = await client.post(
        "/api/dgi/data/bottlenecks",
        json={
            "detection_type": "ACUMULACION",
            "detection_value": 25.0,
            "detection_threshold": 10.0,
            "problem": "Acumulacion de compromisos pendientes en division",
        },
        headers=auth(esp_control_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"].startswith("BN-")
    assert data["status"] == "DETECTADO"
    assert data["detection_type"] == "ACUMULACION"
    assert data["problem"] == "Acumulacion de compromisos pendientes en division"


@pytest.mark.asyncio
async def test_investigation_list(client: AsyncClient, dgi_token, esp_control_token):
    """List investigations with pagination."""
    # Create one first
    await client.post(
        "/api/dgi/data/bottlenecks",
        json={
            "detection_type": "CICLO_TIEMPO",
            "detection_value": 45.0,
            "detection_threshold": 30.0,
            "problem": "Ciclo de tiempo excesivo",
        },
        headers=auth(esp_control_token),
    )

    resp = await client.get(
        "/api/dgi/data/bottlenecks",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_investigation_detail(client: AsyncClient, dgi_token, esp_control_token):
    """Get full investigation detail."""
    create_resp = await client.post(
        "/api/dgi/data/bottlenecks",
        json={
            "detection_type": "PRESUPUESTO",
            "detection_value": 15.5,
            "detection_threshold": 40.0,
            "problem": "Baja ejecucion presupuestaria",
        },
        headers=auth(esp_control_token),
    )
    inv_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/dgi/data/bottlenecks/{inv_id}",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == inv_id
    assert data["status"] == "DETECTADO"
    assert data["detection_type"] == "PRESUPUESTO"
    # Detail fields present
    assert "verification" in data
    assert "root_cause_analysis" in data
    assert "proposal" in data
    assert "communication" in data
    assert "follow_up" in data


@pytest.mark.asyncio
async def test_investigation_delete(client: AsyncClient, esp_control_token):
    """Soft-delete a bottleneck investigation."""
    create_resp = await client.post(
        "/api/dgi/data/bottlenecks",
        json={
            "detection_type": "ACUMULACION",
            "detection_value": 20.0,
            "detection_threshold": 10.0,
            "problem": "To delete",
        },
        headers=auth(esp_control_token),
    )
    inv_id = create_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/dgi/data/bottlenecks/{inv_id}",
        headers=auth(esp_control_token),
    )
    assert del_resp.status_code == 204

    # Verify it's gone from list
    get_resp = await client.get(
        f"/api/dgi/data/bottlenecks/{inv_id}",
        headers=auth(esp_control_token),
    )
    assert get_resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════
# INVESTIGATION FSM
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_investigation_fsm_full_chain(client: AsyncClient, esp_control_token):
    """Full FSM chain: DETECTADO -> VERIFICADO -> ANALIZADO -> PROPUESTO -> IMPLEMENTADO -> CERRADO."""
    create_resp = await client.post(
        "/api/dgi/data/bottlenecks",
        json={
            "detection_type": "ACUMULACION",
            "detection_value": 30.0,
            "detection_threshold": 10.0,
            "problem": "FSM chain test",
        },
        headers=auth(esp_control_token),
    )
    assert create_resp.status_code == 201
    inv_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "DETECTADO"

    # DETECTADO -> VERIFICADO
    r1 = await client.patch(
        f"/api/dgi/data/bottlenecks/{inv_id}",
        json={"status": "VERIFICADO", "verification": "Confirmado en terreno"},
        headers=auth(esp_control_token),
    )
    assert r1.status_code == 200
    assert r1.json()["status"] == "VERIFICADO"
    assert r1.json()["verification"] == "Confirmado en terreno"

    # VERIFICADO -> ANALIZADO
    r2 = await client.patch(
        f"/api/dgi/data/bottlenecks/{inv_id}",
        json={"status": "ANALIZADO", "root_cause_analysis": "Falta de personal"},
        headers=auth(esp_control_token),
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "ANALIZADO"
    assert r2.json()["root_cause_analysis"] == "Falta de personal"

    # ANALIZADO -> PROPUESTO
    r3 = await client.patch(
        f"/api/dgi/data/bottlenecks/{inv_id}",
        json={"status": "PROPUESTO", "proposal": "Reasignar recursos"},
        headers=auth(esp_control_token),
    )
    assert r3.status_code == 200
    assert r3.json()["status"] == "PROPUESTO"
    assert r3.json()["proposal"] == "Reasignar recursos"

    # PROPUESTO -> IMPLEMENTADO
    r4 = await client.patch(
        f"/api/dgi/data/bottlenecks/{inv_id}",
        json={"status": "IMPLEMENTADO", "communication": "Notificado a division"},
        headers=auth(esp_control_token),
    )
    assert r4.status_code == 200
    assert r4.json()["status"] == "IMPLEMENTADO"

    # IMPLEMENTADO -> CERRADO
    r5 = await client.patch(
        f"/api/dgi/data/bottlenecks/{inv_id}",
        json={"status": "CERRADO", "follow_up": "Sin seguimiento adicional"},
        headers=auth(esp_control_token),
    )
    assert r5.status_code == 200
    assert r5.json()["status"] == "CERRADO"
    assert r5.json()["closed_at"] is not None


@pytest.mark.asyncio
async def test_investigation_fsm_invalid_transition(client: AsyncClient, esp_control_token):
    """Invalid FSM transition returns 422."""
    create_resp = await client.post(
        "/api/dgi/data/bottlenecks",
        json={
            "detection_type": "CICLO_TIEMPO",
            "detection_value": 50.0,
            "detection_threshold": 30.0,
            "problem": "Invalid FSM test",
        },
        headers=auth(esp_control_token),
    )
    inv_id = create_resp.json()["id"]

    # DETECTADO -> ANALIZADO (invalid, must go through VERIFICADO)
    resp = await client.patch(
        f"/api/dgi/data/bottlenecks/{inv_id}",
        json={"status": "ANALIZADO"},
        headers=auth(esp_control_token),
    )
    assert resp.status_code == 422
    assert "Transición inválida" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_investigation_fsm_is_enforced_by_db(
    client: AsyncClient,
    esp_control_token,
    db: AsyncSession,
):
    """A direct write cannot bypass the canonical bottleneck FSM."""
    create_resp = await client.post(
        "/api/dgi/data/bottlenecks",
        json={
            "detection_type": "ACUMULACION",
            "detection_value": 30.0,
            "detection_threshold": 10.0,
            "problem": "DB authority test",
        },
        headers=auth(esp_control_token),
    )
    assert create_resp.status_code == 201
    investigation_id = create_resp.json()["id"]

    try:
        with pytest.raises(DBAPIError) as exc_info:
            await db.execute(
                text("""
                    UPDATE core.dgi_bottleneck_investigation
                    SET status_id = (
                        SELECT id FROM ref.category
                        WHERE scheme = 'dgi_bottleneck_status'
                          AND code = 'ANALIZADO'
                    )
                    WHERE id = :id
                """),
                {"id": investigation_id},
            )
    finally:
        await db.rollback()

    assert "Transición de estado inválida" in str(exc_info.value.orig)


@pytest.mark.asyncio
async def test_investigation_fsm_skip_to_cerrado(client: AsyncClient, esp_control_token):
    """Any state can jump directly to CERRADO."""
    create_resp = await client.post(
        "/api/dgi/data/bottlenecks",
        json={
            "detection_type": "ACUMULACION",
            "detection_value": 12.0,
            "detection_threshold": 10.0,
            "problem": "Skip to cerrado test",
        },
        headers=auth(esp_control_token),
    )
    inv_id = create_resp.json()["id"]

    # DETECTADO -> CERRADO (shortcut)
    resp = await client.patch(
        f"/api/dgi/data/bottlenecks/{inv_id}",
        json={"status": "CERRADO"},
        headers=auth(esp_control_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "CERRADO"
    assert resp.json()["closed_at"] is not None


# ═══════════════════════════════════════════════════════════════════════════
# FIELD UPDATE
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_investigation_update_fields(client: AsyncClient, esp_control_token):
    """Update allowlisted fields without status change."""
    create_resp = await client.post(
        "/api/dgi/data/bottlenecks",
        json={
            "detection_type": "PRESUPUESTO",
            "detection_value": 18.0,
            "detection_threshold": 40.0,
            "problem": "Original problem",
        },
        headers=auth(esp_control_token),
    )
    inv_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/dgi/data/bottlenecks/{inv_id}",
        json={"problem": "Updated problem description"},
        headers=auth(esp_control_token),
    )
    assert resp.status_code == 200
    assert resp.json()["problem"] == "Updated problem description"
    # Status should remain unchanged
    assert resp.json()["status"] == "DETECTADO"


# ═══════════════════════════════════════════════════════════════════════════
# ROLE RESTRICTIONS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_analista_cannot_access_bottlenecks(client: AsyncClient, analista_token):
    """Operational roles (ANALISTA) cannot access bottleneck endpoints."""
    # Scan
    resp_scan = await client.get(
        "/api/dgi/data/bottlenecks/scan",
        headers=auth(analista_token),
    )
    assert resp_scan.status_code == 403

    # List
    resp_list = await client.get(
        "/api/dgi/data/bottlenecks",
        headers=auth(analista_token),
    )
    assert resp_list.status_code == 403

    # Create
    resp_create = await client.post(
        "/api/dgi/data/bottlenecks",
        json={
            "detection_type": "ACUMULACION",
            "detection_value": 10.0,
            "detection_threshold": 5.0,
            "problem": "Should fail",
        },
        headers=auth(analista_token),
    )
    assert resp_create.status_code == 403


@pytest.mark.asyncio
async def test_esp_procesos_can_read_but_not_write(client: AsyncClient, esp_procesos_token, esp_control_token):
    """ESP_PROCESOS can read (DGI role) but cannot create investigations (write restricted)."""
    # Create one with write-capable role first
    create_resp = await client.post(
        "/api/dgi/data/bottlenecks",
        json={
            "detection_type": "ACUMULACION",
            "detection_value": 14.0,
            "detection_threshold": 10.0,
            "problem": "Read-only test",
        },
        headers=auth(esp_control_token),
    )
    inv_id = create_resp.json()["id"]

    # ESP_PROCESOS can read
    resp_list = await client.get(
        "/api/dgi/data/bottlenecks",
        headers=auth(esp_procesos_token),
    )
    assert resp_list.status_code == 200

    resp_detail = await client.get(
        f"/api/dgi/data/bottlenecks/{inv_id}",
        headers=auth(esp_procesos_token),
    )
    assert resp_detail.status_code == 200

    # ESP_PROCESOS cannot create
    resp_create = await client.post(
        "/api/dgi/data/bottlenecks",
        json={
            "detection_type": "ACUMULACION",
            "detection_value": 10.0,
            "detection_threshold": 5.0,
            "problem": "Should fail",
        },
        headers=auth(esp_procesos_token),
    )
    assert resp_create.status_code == 403
