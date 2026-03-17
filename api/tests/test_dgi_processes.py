"""
Integration tests for DGI Process Catalog (/api/dgi/processes/).

24 tests covering:
- Process CRUD: create, list, get detail, update, delete (5)
- Process FSM: valid transitions, invalid transition, suspend/resume (4)
- Code generation: auto-incremented PROC-NNNN (1)
- Satellite — Actors: create, list, delete (3)
- Satellite — Rules: create, list, delete, duplicate 409 (4)
- Satellite — Metrics: create, list, delete (3)
- Satellite — Pain Points: create, list (2)
- Satellite — Opportunities: create, list, update, soft-delete (4)
- Progress dashboard (1)
- Impact/Effort matrix (1)
- Metrics comparison (before/after) (1)
- Role restrictions: operational tokens get 403 (2)

Fixtures: dgi_token (JEFE_DGI), esp_procesos_token, analista_token, admin_token
Cleanup: conftest.py cleanup_test_artifacts deletes satellites then processes.
"""

import pytest
from httpx import AsyncClient
from tests.conftest import auth


# ═══════════════════════════════════════════════════════════════════════════
# PROCESS CRUD
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_create_process(client: AsyncClient, dgi_token):
    """DGI can create a process with auto-generated code."""
    resp = await client.post(
        "/api/dgi/processes",
        json={
            "name": "Gestión de Convenios",
            "description": "Proceso end-to-end de convenios",
            "scope": "DAF + Jurídica",
            "criticality": "ALTA",
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"].startswith("PROC-")
    assert data["name"] == "Gestión de Convenios"
    assert data["status"] == "IDENTIFICADO"
    assert data["criticality"] == "ALTA"


@pytest.mark.asyncio
async def test_list_processes(client: AsyncClient, dgi_token):
    """List processes returns paginated structure."""
    # Create one first
    await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso para listar"},
        headers=auth(dgi_token),
    )
    resp = await client.get(
        "/api/dgi/processes",
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
async def test_list_processes_search_filter(client: AsyncClient, dgi_token):
    """Search filter works on name/code."""
    await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Único Buscable XYZ"},
        headers=auth(dgi_token),
    )
    resp = await client.get(
        "/api/dgi/processes",
        params={"search": "Buscable XYZ"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any("Buscable XYZ" in item["name"] for item in data["items"])


@pytest.mark.asyncio
async def test_get_process_detail(client: AsyncClient, dgi_token):
    """Get process detail includes timestamps and bpmn_models."""
    create_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Detalle"},
        headers=auth(dgi_token),
    )
    proc_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/dgi/processes/{proc_id}",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == proc_id
    assert data["name"] == "Proceso Detalle"
    assert "created_at" in data
    assert "updated_at" in data
    assert "bpmn_models" in data
    assert isinstance(data["bpmn_models"], list)


@pytest.mark.asyncio
async def test_update_process(client: AsyncClient, dgi_token):
    """PATCH updates process fields."""
    create_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Original"},
        headers=auth(dgi_token),
    )
    proc_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/dgi/processes/{proc_id}",
        json={
            "name": "Proceso Actualizado",
            "description": "Nueva descripción",
            "criticality": "BAJA",
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Proceso Actualizado"
    assert data["description"] == "Nueva descripción"
    assert data["criticality"] == "BAJA"


@pytest.mark.asyncio
async def test_delete_process(client: AsyncClient, dgi_token):
    """Soft-delete a process."""
    create_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso a Eliminar"},
        headers=auth(dgi_token),
    )
    proc_id = create_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/dgi/processes/{proc_id}",
        headers=auth(dgi_token),
    )
    assert del_resp.status_code == 204

    # Should not appear in detail
    get_resp = await client.get(
        f"/api/dgi/processes/{proc_id}",
        headers=auth(dgi_token),
    )
    assert get_resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════
# PROCESS FSM
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_process_fsm_happy_path(client: AsyncClient, dgi_token):
    """Full FSM path: IDENTIFICADO -> EN_LEVANTAMIENTO -> MODELADO -> VALIDADO -> PUBLICADO."""
    create_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso FSM Feliz"},
        headers=auth(dgi_token),
    )
    proc_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "IDENTIFICADO"

    for target in ["EN_LEVANTAMIENTO", "MODELADO", "VALIDADO", "PUBLICADO"]:
        resp = await client.patch(
            f"/api/dgi/processes/{proc_id}",
            json={"status": target},
            headers=auth(dgi_token),
        )
        assert resp.status_code == 200, f"Failed transition to {target}: {resp.text}"
        assert resp.json()["status"] == target


@pytest.mark.asyncio
async def test_process_fsm_invalid_transition(client: AsyncClient, dgi_token):
    """Invalid FSM transition returns 400."""
    create_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso FSM Inválido"},
        headers=auth(dgi_token),
    )
    proc_id = create_resp.json()["id"]

    # IDENTIFICADO -> PUBLICADO is invalid (must go through intermediate states)
    resp = await client.patch(
        f"/api/dgi/processes/{proc_id}",
        json={"status": "PUBLICADO"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 400
    assert "Transición inválida" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_process_fsm_suspend_and_resume(client: AsyncClient, dgi_token):
    """Process can be suspended from any state and resumed to IDENTIFICADO."""
    create_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Suspender"},
        headers=auth(dgi_token),
    )
    proc_id = create_resp.json()["id"]

    # Move to EN_LEVANTAMIENTO
    await client.patch(
        f"/api/dgi/processes/{proc_id}",
        json={"status": "EN_LEVANTAMIENTO"},
        headers=auth(dgi_token),
    )

    # Suspend
    resp = await client.patch(
        f"/api/dgi/processes/{proc_id}",
        json={"status": "SUSPENDIDO"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "SUSPENDIDO"

    # Resume to IDENTIFICADO
    resp2 = await client.patch(
        f"/api/dgi/processes/{proc_id}",
        json={"status": "IDENTIFICADO"},
        headers=auth(dgi_token),
    )
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "IDENTIFICADO"


@pytest.mark.asyncio
async def test_process_fsm_backward_transition(client: AsyncClient, dgi_token):
    """FSM allows backward transitions (e.g., MODELADO -> EN_LEVANTAMIENTO)."""
    create_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Retroceso"},
        headers=auth(dgi_token),
    )
    proc_id = create_resp.json()["id"]

    # Forward: IDENTIFICADO -> EN_LEVANTAMIENTO -> MODELADO
    await client.patch(
        f"/api/dgi/processes/{proc_id}",
        json={"status": "EN_LEVANTAMIENTO"},
        headers=auth(dgi_token),
    )
    await client.patch(
        f"/api/dgi/processes/{proc_id}",
        json={"status": "MODELADO"},
        headers=auth(dgi_token),
    )

    # Backward: MODELADO -> EN_LEVANTAMIENTO
    resp = await client.patch(
        f"/api/dgi/processes/{proc_id}",
        json={"status": "EN_LEVANTAMIENTO"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "EN_LEVANTAMIENTO"


# ═══════════════════════════════════════════════════════════════════════════
# CODE GENERATION
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_process_code_sequential(client: AsyncClient, dgi_token):
    """Process codes are sequential (PROC-NNNN)."""
    resp1 = await client.post(
        "/api/dgi/processes",
        json={"name": "Código Seq 1"},
        headers=auth(dgi_token),
    )
    resp2 = await client.post(
        "/api/dgi/processes",
        json={"name": "Código Seq 2"},
        headers=auth(dgi_token),
    )
    code1 = resp1.json()["code"]
    code2 = resp2.json()["code"]
    seq1 = int(code1.split("-")[1])
    seq2 = int(code2.split("-")[1])
    assert seq2 == seq1 + 1


# ═══════════════════════════════════════════════════════════════════════════
# SATELLITE: ACTORS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_actor_create(client: AsyncClient, dgi_token):
    """Create an actor for a process."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso con Actores"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    resp = await client.post(
        f"/api/dgi/processes/{proc_id}/actors",
        json={
            "actor_type": "ROL",
            "actor_name": "Jefe de División",
            "lane_label": "Aprobador",
            "description": "Aprueba el resultado final",
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["actor_type"] == "ROL"
    assert data["actor_name"] == "Jefe de División"
    assert data["lane_label"] == "Aprobador"


@pytest.mark.asyncio
async def test_actor_list(client: AsyncClient, dgi_token):
    """List actors of a process."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Listar Actores"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    await client.post(
        f"/api/dgi/processes/{proc_id}/actors",
        json={"actor_type": "SISTEMA", "actor_name": "SIGFE"},
        headers=auth(dgi_token),
    )
    await client.post(
        f"/api/dgi/processes/{proc_id}/actors",
        json={"actor_type": "DIVISION", "actor_name": "DAF"},
        headers=auth(dgi_token),
    )

    resp = await client.get(
        f"/api/dgi/processes/{proc_id}/actors",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


@pytest.mark.asyncio
async def test_actor_delete(client: AsyncClient, dgi_token):
    """Delete an actor from a process."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Eliminar Actor"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    actor_resp = await client.post(
        f"/api/dgi/processes/{proc_id}/actors",
        json={"actor_type": "ROL", "actor_name": "Temporal"},
        headers=auth(dgi_token),
    )
    actor_id = actor_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/dgi/processes/{proc_id}/actors/{actor_id}",
        headers=auth(dgi_token),
    )
    assert del_resp.status_code == 204

    # Verify removed
    list_resp = await client.get(
        f"/api/dgi/processes/{proc_id}/actors",
        headers=auth(dgi_token),
    )
    actor_ids = [a["id"] for a in list_resp.json()]
    assert actor_id not in actor_ids


# ═══════════════════════════════════════════════════════════════════════════
# SATELLITE: RULES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_rule_create(client: AsyncClient, esp_procesos_token):
    """ESP_PROCESOS can create a rule for a process."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso con Reglas"},
        headers=auth(esp_procesos_token),
    )
    proc_id = proc_resp.json()["id"]

    resp = await client.post(
        f"/api/dgi/processes/{proc_id}/rules",
        json={
            "code": "RN-001",
            "description": "Monto > 5000 UTM requiere resolución exenta",
            "rule_type": "VALIDACION",
        },
        headers=auth(esp_procesos_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == "RN-001"
    assert data["rule_type"] == "VALIDACION"


@pytest.mark.asyncio
async def test_rule_list(client: AsyncClient, dgi_token):
    """List rules of a process."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Listar Reglas"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    await client.post(
        f"/api/dgi/processes/{proc_id}/rules",
        json={"code": "RN-010", "description": "Regla test", "rule_type": "VALIDACION"},
        headers=auth(dgi_token),
    )

    resp = await client.get(
        f"/api/dgi/processes/{proc_id}/rules",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_rule_duplicate_409(client: AsyncClient, dgi_token):
    """Duplicate rule code in same process returns 409."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Regla Duplicada"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    await client.post(
        f"/api/dgi/processes/{proc_id}/rules",
        json={"code": "RN-DUP", "description": "Primera", "rule_type": "VALIDACION"},
        headers=auth(dgi_token),
    )

    resp = await client.post(
        f"/api/dgi/processes/{proc_id}/rules",
        json={"code": "RN-DUP", "description": "Segunda", "rule_type": "VALIDACION"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_rule_delete(client: AsyncClient, dgi_token):
    """Delete a rule from a process."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Eliminar Regla"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    rule_resp = await client.post(
        f"/api/dgi/processes/{proc_id}/rules",
        json={"code": "RN-DEL", "description": "A eliminar", "rule_type": "VALIDACION"},
        headers=auth(dgi_token),
    )
    rule_id = rule_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/dgi/processes/{proc_id}/rules/{rule_id}",
        headers=auth(dgi_token),
    )
    assert del_resp.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════
# SATELLITE: METRICS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_metric_create(client: AsyncClient, dgi_token):
    """Create a metric for a process."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso con Métricas"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    resp = await client.post(
        f"/api/dgi/processes/{proc_id}/metrics",
        json={
            "name": "Tiempo de ciclo",
            "value": 15.5,
            "unit": "días",
            "measurement_type": "BASELINE",
            "source": "Medición manual",
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Tiempo de ciclo"
    assert data["value"] == 15.5
    assert data["unit"] == "días"
    assert data["measurement_type"] == "BASELINE"


@pytest.mark.asyncio
async def test_metric_list(client: AsyncClient, dgi_token):
    """List metrics of a process."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Listar Métricas"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    await client.post(
        f"/api/dgi/processes/{proc_id}/metrics",
        json={"name": "Throughput", "value": 100, "unit": "req/mes"},
        headers=auth(dgi_token),
    )

    resp = await client.get(
        f"/api/dgi/processes/{proc_id}/metrics",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_metric_delete(client: AsyncClient, dgi_token):
    """Delete a metric from a process."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Eliminar Métrica"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    metric_resp = await client.post(
        f"/api/dgi/processes/{proc_id}/metrics",
        json={"name": "Métrica temporal", "value": 42},
        headers=auth(dgi_token),
    )
    metric_id = metric_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/dgi/processes/{proc_id}/metrics/{metric_id}",
        headers=auth(dgi_token),
    )
    assert del_resp.status_code == 204


# ═══════════════════════════════════════════════════════════════════════════
# SATELLITE: PAIN POINTS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_pain_point_create(client: AsyncClient, dgi_token):
    """Create a pain point for a process."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso con Dolor"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    resp = await client.post(
        f"/api/dgi/processes/{proc_id}/pain-points",
        json={
            "description": "Demora excesiva en aprobación de VB",
            "impact": "ALTO",
            "bpmn_stage": "Revisión jurídica",
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["description"] == "Demora excesiva en aprobación de VB"
    assert data["impact"] == "ALTO"
    assert data["bpmn_stage"] == "Revisión jurídica"


@pytest.mark.asyncio
async def test_pain_point_list(client: AsyncClient, dgi_token):
    """List pain points of a process."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Listar Dolores"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    await client.post(
        f"/api/dgi/processes/{proc_id}/pain-points",
        json={"description": "Dolor 1", "impact": "MEDIO"},
        headers=auth(dgi_token),
    )
    await client.post(
        f"/api/dgi/processes/{proc_id}/pain-points",
        json={"description": "Dolor 2", "impact": "BAJO"},
        headers=auth(dgi_token),
    )

    resp = await client.get(
        f"/api/dgi/processes/{proc_id}/pain-points",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


# ═══════════════════════════════════════════════════════════════════════════
# SATELLITE: IMPROVEMENT OPPORTUNITIES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_opportunity_create(client: AsyncClient, dgi_token):
    """Create an improvement opportunity for a process."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso con Oportunidades"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    resp = await client.post(
        f"/api/dgi/processes/{proc_id}/opportunities",
        json={
            "dimension": "AUTOMATIZACION",
            "description": "Automatizar notificaciones de vencimiento",
            "impact": "ALTO",
            "effort": "MEDIO",
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["dimension"] == "AUTOMATIZACION"
    assert data["impact"] == "ALTO"
    assert data["effort"] == "MEDIO"
    assert data["status"] == "PROPUESTA"
    assert data["initiative_id"] is None


@pytest.mark.asyncio
async def test_opportunity_list(client: AsyncClient, dgi_token):
    """List improvement opportunities of a process."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Listar Oportunidades"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    await client.post(
        f"/api/dgi/processes/{proc_id}/opportunities",
        json={"dimension": "DUPLICACION", "description": "Opp 1", "impact": "MEDIO", "effort": "BAJO"},
        headers=auth(dgi_token),
    )

    resp = await client.get(
        f"/api/dgi/processes/{proc_id}/opportunities",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_opportunity_update(client: AsyncClient, dgi_token):
    """Update opportunity status via PATCH."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Actualizar Oportunidad"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    opp_resp = await client.post(
        f"/api/dgi/processes/{proc_id}/opportunities",
        json={"dimension": "ESPERAS", "description": "Opp actualizable", "impact": "BAJO", "effort": "BAJO"},
        headers=auth(dgi_token),
    )
    opp_id = opp_resp.json()["id"]

    resp = await client.patch(
        f"/api/dgi/processes/{proc_id}/opportunities/{opp_id}",
        json={"status": "VALIDADA"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "VALIDADA"


@pytest.mark.asyncio
async def test_opportunity_soft_delete(client: AsyncClient, dgi_token):
    """Soft-delete an improvement opportunity."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Eliminar Oportunidad"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    opp_resp = await client.post(
        f"/api/dgi/processes/{proc_id}/opportunities",
        json={"dimension": "ERRORES", "description": "A eliminar", "impact": "BAJO", "effort": "ALTO"},
        headers=auth(dgi_token),
    )
    opp_id = opp_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/dgi/processes/{proc_id}/opportunities/{opp_id}",
        headers=auth(dgi_token),
    )
    assert del_resp.status_code == 204

    # Verify it no longer appears in the list (soft-deleted)
    list_resp = await client.get(
        f"/api/dgi/processes/{proc_id}/opportunities",
        headers=auth(dgi_token),
    )
    opp_ids = [o["id"] for o in list_resp.json()]
    assert opp_id not in opp_ids


# ═══════════════════════════════════════════════════════════════════════════
# PROGRESS DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_progress_dashboard(client: AsyncClient, dgi_token):
    """Progress dashboard returns division breakdown."""
    # Create a process so there is at least some data
    await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso para Dashboard"},
        headers=auth(dgi_token),
    )

    resp = await client.get(
        "/api/dgi/processes/progress",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    item = data[0]
    assert "division_name" in item
    assert "total" in item
    assert "identificado" in item
    assert "publicado" in item


# ═══════════════════════════════════════════════════════════════════════════
# IMPACT/EFFORT MATRIX
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_impact_effort_matrix(client: AsyncClient, dgi_token):
    """Impact/effort matrix returns 3x3 grid (9 cells)."""
    # Create process + opportunity with impact/effort
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Matriz"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    await client.post(
        f"/api/dgi/processes/{proc_id}/opportunities",
        json={"dimension": "AUTOMATIZACION", "description": "Celda test", "impact": "ALTO", "effort": "BAJO"},
        headers=auth(dgi_token),
    )

    resp = await client.get(
        "/api/dgi/processes/impact-effort",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 9  # 3x3 grid
    # Verify all combinations present
    combos = {(cell["impact"], cell["effort"]) for cell in data}
    assert ("ALTO", "BAJO") in combos
    assert ("BAJO", "ALTO") in combos
    assert ("MEDIO", "MEDIO") in combos
    # At least one cell should have our opportunity
    alto_bajo = [c for c in data if c["impact"] == "ALTO" and c["effort"] == "BAJO"]
    assert len(alto_bajo) == 1
    assert alto_bajo[0]["count"] >= 1


# ═══════════════════════════════════════════════════════════════════════════
# METRICS COMPARISON (BEFORE/AFTER)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_metrics_comparison(client: AsyncClient, dgi_token):
    """Metrics comparison groups BASELINE vs POST_MEJORA and computes delta."""
    proc_resp = await client.post(
        "/api/dgi/processes",
        json={"name": "Proceso Comparación"},
        headers=auth(dgi_token),
    )
    proc_id = proc_resp.json()["id"]

    # Create baseline metric
    await client.post(
        f"/api/dgi/processes/{proc_id}/metrics",
        json={"name": "Tiempo de ciclo", "value": 20.0, "unit": "días", "measurement_type": "BASELINE"},
        headers=auth(dgi_token),
    )
    # Create post-improvement metric
    await client.post(
        f"/api/dgi/processes/{proc_id}/metrics",
        json={"name": "Tiempo de ciclo", "value": 12.0, "unit": "días", "measurement_type": "POST_MEJORA"},
        headers=auth(dgi_token),
    )

    resp = await client.get(
        f"/api/dgi/processes/{proc_id}/metrics/comparison",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    comparison = data[0]
    assert comparison["name"] == "Tiempo de ciclo"
    assert comparison["baseline_value"] == 20.0
    assert comparison["post_mejora_value"] == 12.0
    assert comparison["delta"] == -8.0
    assert comparison["unit"] == "días"


# ═══════════════════════════════════════════════════════════════════════════
# ROLE RESTRICTIONS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_operational_cannot_create_process(client: AsyncClient, analista_token):
    """Operational roles (ANALISTA) cannot create processes."""
    resp = await client.post(
        "/api/dgi/processes",
        json={"name": "No debería crearse"},
        headers=auth(analista_token),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_operational_cannot_list_processes(client: AsyncClient, admin_token):
    """Non-DGI admin roles cannot list processes."""
    resp = await client.get(
        "/api/dgi/processes",
        headers=auth(admin_token),
    )
    assert resp.status_code == 403
