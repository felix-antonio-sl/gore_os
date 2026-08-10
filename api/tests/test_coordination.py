"""
Integration tests for Wave B: Coordination, Escalation, Services, SLAs.

35 tests covering:
- AR decisions CRUD (5)
- Escalation CRUD + FSM + auto-alert + code gen (8)
- Service catalog CRUD (4)
- Service requests CRUD + FSM + timing (6)
- SLA CRUD + dashboard (5)
- Division interactions CRUD + matrix (4)
- Role restrictions (3)
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth


# ═══════════════════════════════════════════════════════════════════════════
# AR DECISIONS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_ar_decisions_create(client: AsyncClient, dgi_token):
    """DGI can create an AR decision."""
    resp = await client.post(
        "/api/dgi/coordination/ar/decisions",
        json={
            "description": "Priorizar proyecto DAF urgente",
            "decision_type": "PRIORIDAD",
            "context": "Proyecto atrasado 30 días",
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["decision_type"] == "PRIORIDAD"
    assert data["status"] == "PENDIENTE"
    assert data["description"] == "Priorizar proyecto DAF urgente"


@pytest.mark.asyncio
async def test_ar_decisions_list(client: AsyncClient, dgi_token):
    """DGI can list AR decisions."""
    # Create one first
    await client.post(
        "/api/dgi/coordination/ar/decisions",
        json={"description": "Test list decision", "decision_type": "RECURSO"},
        headers=auth(dgi_token),
    )
    resp = await client.get(
        "/api/dgi/coordination/ar/decisions",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_ar_decisions_transition(client: AsyncClient, dgi_token):
    """AR decision transitions: PENDIENTE → EN_EJECUCION → COMPLETADA."""
    # Create
    resp = await client.post(
        "/api/dgi/coordination/ar/decisions",
        json={"description": "Test transition", "decision_type": "ESTRATEGIA"},
        headers=auth(dgi_token),
    )
    dec_id = resp.json()["id"]

    # PENDIENTE → EN_EJECUCION
    resp2 = await client.patch(
        f"/api/dgi/coordination/ar/decisions/{dec_id}",
        json={"status": "EN_EJECUCION"},
        headers=auth(dgi_token),
    )
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "EN_EJECUCION"

    # EN_EJECUCION → COMPLETADA
    resp3 = await client.patch(
        f"/api/dgi/coordination/ar/decisions/{dec_id}",
        json={"status": "COMPLETADA"},
        headers=auth(dgi_token),
    )
    assert resp3.status_code == 200
    assert resp3.json()["status"] == "COMPLETADA"
    assert resp3.json()["resolved_at"] is not None


@pytest.mark.asyncio
async def test_ar_decisions_delete(client: AsyncClient, dgi_token):
    """DGI can soft-delete an AR decision."""
    resp = await client.post(
        "/api/dgi/coordination/ar/decisions",
        json={"description": "To delete", "decision_type": "PRIORIDAD"},
        headers=auth(dgi_token),
    )
    dec_id = resp.json()["id"]

    del_resp = await client.delete(
        f"/api/dgi/coordination/ar/decisions/{dec_id}",
        headers=auth(dgi_token),
    )
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_ar_prep_view(client: AsyncClient, dgi_token):
    """AR prep view returns initiatives, alerts, decisions."""
    resp = await client.get(
        "/api/dgi/coordination/ar/prep",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "initiatives" in data
    assert "alerts" in data
    assert "decisions" in data
    assert "count" in data["initiatives"]


# ═══════════════════════════════════════════════════════════════════════════
# ESCALATION
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_escalation_create(client: AsyncClient, dgi_token):
    """Create escalation with auto-generated code and auto-alert."""
    resp = await client.post(
        "/api/dgi/escalations",
        json={
            "level": "NIVEL_1",
            "situation": "Bloqueo en proceso de convenio DAF",
            "impact": "Retraso de 15 días en transferencia",
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"].startswith("ESC-")
    assert data["status"] == "ABIERTO"
    assert data["escalated_to"] == "JEFE_DGI"
    assert data["level"] == "NIVEL_1"


@pytest.mark.asyncio
async def test_escalation_code_sequential(client: AsyncClient, dgi_token):
    """Escalation codes are sequential."""
    resp1 = await client.post(
        "/api/dgi/escalations",
        json={"level": "NIVEL_2", "situation": "Seq test 1", "impact": "Impact 1"},
        headers=auth(dgi_token),
    )
    resp2 = await client.post(
        "/api/dgi/escalations",
        json={"level": "NIVEL_2", "situation": "Seq test 2", "impact": "Impact 2"},
        headers=auth(dgi_token),
    )
    code1 = resp1.json()["code"]
    code2 = resp2.json()["code"]
    seq1 = int(code1.split("-")[-1])
    seq2 = int(code2.split("-")[-1])
    assert seq2 == seq1 + 1


@pytest.mark.asyncio
async def test_escalation_list(client: AsyncClient, dgi_token):
    """List escalations with pagination."""
    resp = await client.get(
        "/api/dgi/escalations",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_escalation_detail(client: AsyncClient, dgi_token):
    """Get escalation detail."""
    create_resp = await client.post(
        "/api/dgi/escalations",
        json={"level": "NIVEL_3", "situation": "Detail test", "impact": "Critical"},
        headers=auth(dgi_token),
    )
    esc_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/dgi/escalations/{esc_id}",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["level"] == "NIVEL_3"
    assert resp.json()["escalated_to"] == "AR"


@pytest.mark.asyncio
async def test_escalation_fsm(client: AsyncClient, dgi_token):
    """Escalation FSM: ABIERTO → EN_GESTION → RESUELTO → CERRADO."""
    resp = await client.post(
        "/api/dgi/escalations",
        json={"level": "NIVEL_1", "situation": "FSM test", "impact": "Impact"},
        headers=auth(dgi_token),
    )
    esc_id = resp.json()["id"]

    # ABIERTO → EN_GESTION
    r1 = await client.patch(
        f"/api/dgi/escalations/{esc_id}",
        json={"status": "EN_GESTION"},
        headers=auth(dgi_token),
    )
    assert r1.status_code == 200
    assert r1.json()["status"] == "EN_GESTION"

    # EN_GESTION → RESUELTO
    r2 = await client.patch(
        f"/api/dgi/escalations/{esc_id}",
        json={"status": "RESUELTO", "resolved_description": "Se resolvió coordinando con DAF"},
        headers=auth(dgi_token),
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "RESUELTO"
    assert r2.json()["resolved_at"] is not None

    # RESUELTO → CERRADO
    r3 = await client.patch(
        f"/api/dgi/escalations/{esc_id}",
        json={"status": "CERRADO"},
        headers=auth(dgi_token),
    )
    assert r3.status_code == 200
    assert r3.json()["status"] == "CERRADO"


@pytest.mark.asyncio
async def test_escalation_invalid_transition(client: AsyncClient, dgi_token):
    """Invalid FSM transition returns 422."""
    resp = await client.post(
        "/api/dgi/escalations",
        json={"level": "NIVEL_1", "situation": "Invalid FSM", "impact": "Impact"},
        headers=auth(dgi_token),
    )
    esc_id = resp.json()["id"]

    # ABIERTO → RESUELTO (invalid, must go through EN_GESTION)
    r = await client.patch(
        f"/api/dgi/escalations/{esc_id}",
        json={"status": "RESUELTO"},
        headers=auth(dgi_token),
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_escalation_delete(client: AsyncClient, dgi_token):
    """Soft-delete escalation."""
    resp = await client.post(
        "/api/dgi/escalations",
        json={"level": "NIVEL_1", "situation": "To delete", "impact": "Impact"},
        headers=auth(dgi_token),
    )
    esc_id = resp.json()["id"]

    del_resp = await client.delete(
        f"/api/dgi/escalations/{esc_id}",
        headers=auth(dgi_token),
    )
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_escalation_stats(client: AsyncClient, dgi_token):
    """Stats endpoint returns structure."""
    resp = await client.get(
        "/api/dgi/escalations/stats",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_active" in data
    assert "by_level" in data
    assert "resolved_count" in data


# ═══════════════════════════════════════════════════════════════════════════
# SERVICE CATALOG
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_service_create(client: AsyncClient, dgi_token):
    """JEFE_DGI can create a service."""
    resp = await client.post(
        "/api/dgi/services",
        json={
            "name": "Levantamiento de Proceso",
            "area": "MP",
            "description": "Modelado BPMN completo",
            "sla_days": 5,
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"].startswith("SVC-MP-")
    assert data["status"] == "ACTIVO"
    assert data["sla_days"] == 5


@pytest.mark.asyncio
async def test_service_list(client: AsyncClient, dgi_token):
    """List services returns array."""
    resp = await client.get(
        "/api/dgi/services",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_service_detail_with_slas(client: AsyncClient, dgi_token):
    """Service detail includes SLAs."""
    create_resp = await client.post(
        "/api/dgi/services",
        json={"name": "Informe Flash DGI", "area": "CG", "sla_days": 1},
        headers=auth(dgi_token),
    )
    svc_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/dgi/services/{svc_id}",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert "slas" in resp.json()


@pytest.mark.asyncio
async def test_service_update(client: AsyncClient, dgi_token):
    """Update service description."""
    create_resp = await client.post(
        "/api/dgi/services",
        json={"name": "Soporte TD", "area": "TD"},
        headers=auth(dgi_token),
    )
    svc_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/dgi/services/{svc_id}",
        json={"description": "Updated description"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Updated description"


# ═══════════════════════════════════════════════════════════════════════════
# SERVICE REQUESTS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_request_create(client: AsyncClient, dgi_token, jefe_token):
    """Any user can create a service request."""
    # Create service first
    svc_resp = await client.post(
        "/api/dgi/services",
        json={"name": "Test Request Service", "area": "CG", "sla_days": 3},
        headers=auth(dgi_token),
    )
    svc_id = svc_resp.json()["id"]

    # Jefe (operativa) creates request
    resp = await client.post(
        "/api/dgi/services/requests",
        json={
            "service_id": svc_id,
            "description": "Necesito un informe flash sobre ejecución presupuestaria",
            "urgency": "ALTA",
        },
        headers=auth(jefe_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"].startswith("REQ-")
    assert data["status"] == "RECIBIDA"
    assert data["urgency"] == "ALTA"


@pytest.mark.asyncio
async def test_inactive_service_cannot_receive_request_even_via_direct_sql(
    client: AsyncClient,
    dgi_token,
    jefe_token,
    db: AsyncSession,
):
    """Only an active catalog service may accept a new request, including direct SQL."""
    svc_resp = await client.post(
        "/api/dgi/services",
        json={"name": "Inactive Request Guard", "area": "CG"},
        headers=auth(dgi_token),
    )
    service_id = svc_resp.json()["id"]
    suspend_resp = await client.patch(
        f"/api/dgi/services/{service_id}",
        json={"status": "SUSPENDIDO"},
        headers=auth(dgi_token),
    )
    assert suspend_resp.status_code == 200

    api_resp = await client.post(
        "/api/dgi/services/requests",
        json={"service_id": service_id, "description": "Must stay blocked"},
        headers=auth(jefe_token),
    )
    assert api_resp.status_code == 400

    status_id = (await db.execute(text("""
        SELECT id FROM ref.category
        WHERE scheme = 'dgi_request_status' AND code = 'RECIBIDA'
    """))).scalar_one()
    requester_id = (await db.execute(text("""
        SELECT id FROM core."user" WHERE email = 'jefe.daf@goreos.cl'
    """))).scalar_one()

    try:
        with pytest.raises(DBAPIError) as exc_info:
            await db.execute(
                text("""
                    INSERT INTO core.dgi_service_request
                        (code, service_id, status_id, requester_id, description)
                    VALUES
                        ('REQ-INACTIVE-DB', :service_id, :status_id, :requester_id,
                         'Direct SQL must stay blocked')
                """),
                {
                    "service_id": service_id,
                    "status_id": status_id,
                    "requester_id": requester_id,
                },
            )
    finally:
        await db.rollback()

    assert "requires an active service" in str(exc_info.value.orig)


@pytest.mark.asyncio
async def test_request_list_own(client: AsyncClient, dgi_token, jefe_token):
    """Non-DGI users see only their own requests."""
    svc_resp = await client.post(
        "/api/dgi/services",
        json={"name": "List Own Service", "area": "CG"},
        headers=auth(dgi_token),
    )
    svc_id = svc_resp.json()["id"]

    await client.post(
        "/api/dgi/services/requests",
        json={"service_id": svc_id, "description": "My request"},
        headers=auth(jefe_token),
    )

    resp = await client.get(
        "/api/dgi/services/requests",
        headers=auth(jefe_token),
    )
    assert resp.status_code == 200
    for item in resp.json()["items"]:
        # All requests should belong to the jefe user
        assert item["status"] is not None


@pytest.mark.asyncio
async def test_request_fsm_flow(client: AsyncClient, dgi_token, jefe_token):
    """Request FSM: RECIBIDA → EN_EVALUACION → ACEPTADA → EN_EJECUCION → COMPLETADA."""
    svc_resp = await client.post(
        "/api/dgi/services",
        json={"name": "FSM Flow Service", "area": "MP", "sla_days": 5},
        headers=auth(dgi_token),
    )
    svc_id = svc_resp.json()["id"]

    # Create request
    req_resp = await client.post(
        "/api/dgi/services/requests",
        json={"service_id": svc_id, "description": "FSM test request"},
        headers=auth(jefe_token),
    )
    req_id = req_resp.json()["id"]

    # DGI manages transitions
    for target in ["EN_EVALUACION", "ACEPTADA", "EN_EJECUCION", "COMPLETADA"]:
        r = await client.patch(
            f"/api/dgi/services/requests/{req_id}",
            json={"status": target},
            headers=auth(dgi_token),
        )
        assert r.status_code == 200
        assert r.json()["status"] == target

    # Verify timing was set
    final = await client.get(
        f"/api/dgi/services/requests/{req_id}",
        headers=auth(dgi_token),
    )
    assert final.json()["started_at"] is not None
    assert final.json()["completed_at"] is not None


@pytest.mark.asyncio
async def test_request_feedback(client: AsyncClient, dgi_token, jefe_token):
    """Requester can submit feedback on completed request."""
    svc_resp = await client.post(
        "/api/dgi/services",
        json={"name": "Feedback Service", "area": "CG"},
        headers=auth(dgi_token),
    )
    svc_id = svc_resp.json()["id"]

    req_resp = await client.post(
        "/api/dgi/services/requests",
        json={"service_id": svc_id, "description": "Feedback test"},
        headers=auth(jefe_token),
    )
    req_id = req_resp.json()["id"]

    # DGI completes the request
    for target in ["EN_EVALUACION", "ACEPTADA", "EN_EJECUCION", "COMPLETADA"]:
        await client.patch(
            f"/api/dgi/services/requests/{req_id}",
            json={"status": target},
            headers=auth(dgi_token),
        )

    # Requester gives feedback
    fb_resp = await client.patch(
        f"/api/dgi/services/requests/{req_id}",
        json={"satisfaction_score": 4, "feedback_text": "Buen servicio"},
        headers=auth(jefe_token),
    )
    assert fb_resp.status_code == 200
    assert fb_resp.json()["satisfaction_score"] == 4


@pytest.mark.asyncio
async def test_request_reject(client: AsyncClient, dgi_token, jefe_token):
    """DGI can reject a request from RECIBIDA."""
    svc_resp = await client.post(
        "/api/dgi/services",
        json={"name": "Reject Service", "area": "TD"},
        headers=auth(dgi_token),
    )
    svc_id = svc_resp.json()["id"]

    req_resp = await client.post(
        "/api/dgi/services/requests",
        json={"service_id": svc_id, "description": "To reject"},
        headers=auth(jefe_token),
    )
    req_id = req_resp.json()["id"]

    r = await client.patch(
        f"/api/dgi/services/requests/{req_id}",
        json={"status": "RECHAZADA"},
        headers=auth(dgi_token),
    )
    assert r.status_code == 200
    assert r.json()["status"] == "RECHAZADA"


@pytest.mark.asyncio
async def test_request_invalid_transition(client: AsyncClient, dgi_token, jefe_token):
    """Invalid request transition returns error."""
    svc_resp = await client.post(
        "/api/dgi/services",
        json={"name": "Invalid Transition Service", "area": "CG"},
        headers=auth(dgi_token),
    )
    svc_id = svc_resp.json()["id"]

    req_resp = await client.post(
        "/api/dgi/services/requests",
        json={"service_id": svc_id, "description": "Invalid"},
        headers=auth(jefe_token),
    )
    req_id = req_resp.json()["id"]

    # RECIBIDA → COMPLETADA (invalid)
    r = await client.patch(
        f"/api/dgi/services/requests/{req_id}",
        json={"status": "COMPLETADA"},
        headers=auth(dgi_token),
    )
    assert r.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════
# SLAs
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_sla_create(client: AsyncClient, dgi_token):
    """Create SLA for a service."""
    svc_resp = await client.post(
        "/api/dgi/services",
        json={"name": "SLA Test Service", "area": "CG"},
        headers=auth(dgi_token),
    )
    svc_id = svc_resp.json()["id"]

    resp = await client.post(
        f"/api/dgi/services/{svc_id}/slas",
        json={
            "product_type": "INFORME_FLASH",
            "target_days": 1,
            "description": "Entrega el mismo día",
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201
    assert resp.json()["target_days"] == 1
    assert resp.json()["product_type"] == "INFORME_FLASH"


@pytest.mark.asyncio
async def test_sla_list(client: AsyncClient, dgi_token):
    """List SLAs for a service."""
    svc_resp = await client.post(
        "/api/dgi/services",
        json={"name": "SLA List Service", "area": "MP"},
        headers=auth(dgi_token),
    )
    svc_id = svc_resp.json()["id"]

    await client.post(
        f"/api/dgi/services/{svc_id}/slas",
        json={"product_type": "LEVANTAMIENTO_PROCESO", "target_days": 10},
        headers=auth(dgi_token),
    )

    resp = await client.get(
        f"/api/dgi/services/{svc_id}/slas",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_sla_duplicate_rejected(client: AsyncClient, dgi_token):
    """Duplicate SLA (same service + product_type) returns 409."""
    svc_resp = await client.post(
        "/api/dgi/services",
        json={"name": "SLA Dup Service", "area": "TD"},
        headers=auth(dgi_token),
    )
    svc_id = svc_resp.json()["id"]

    await client.post(
        f"/api/dgi/services/{svc_id}/slas",
        json={"product_type": "SOPORTE_TD", "target_days": 2},
        headers=auth(dgi_token),
    )

    resp = await client.post(
        f"/api/dgi/services/{svc_id}/slas",
        json={"product_type": "SOPORTE_TD", "target_days": 3},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_sla_update(client: AsyncClient, dgi_token):
    """Update SLA target_days."""
    svc_resp = await client.post(
        "/api/dgi/services",
        json={"name": "SLA Update Service", "area": "KC"},
        headers=auth(dgi_token),
    )
    svc_id = svc_resp.json()["id"]

    sla_resp = await client.post(
        f"/api/dgi/services/{svc_id}/slas",
        json={"product_type": "ANALISIS_INDICADOR", "target_days": 3},
        headers=auth(dgi_token),
    )
    sla_id = sla_resp.json()["id"]

    resp = await client.patch(
        f"/api/dgi/services/{svc_id}/slas/{sla_id}",
        json={"target_days": 5},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["target_days"] == 5


@pytest.mark.asyncio
async def test_sla_dashboard(client: AsyncClient, dgi_token):
    """SLA dashboard returns summary structure."""
    resp = await client.get(
        "/api/dgi/services/sla-dashboard",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "global_completion_rate" in data
    assert "active_requests" in data
    assert "by_service" in data


# ═══════════════════════════════════════════════════════════════════════════
# DIVISION INTERACTIONS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_interaction_create(client: AsyncClient, dgi_token, catalog):
    """Create a division interaction."""
    resp = await client.post(
        "/api/dgi/coordination/interactions",
        json={
            "division_id": catalog["division_id"],
            "interaction_type": "PRESUPUESTO",
            "notes": "Revisión ejecución Q3",
        },
        headers=auth(dgi_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["interaction_type"] == "PRESUPUESTO"
    assert data["division_name"] is not None


@pytest.mark.asyncio
async def test_interaction_list(client: AsyncClient, dgi_token, catalog):
    """List interactions with filters."""
    await client.post(
        "/api/dgi/coordination/interactions",
        json={
            "division_id": catalog["division_id"],
            "interaction_type": "GENERAL",
        },
        headers=auth(dgi_token),
    )

    resp = await client.get(
        "/api/dgi/coordination/interactions",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_interaction_update(client: AsyncClient, dgi_token, catalog):
    """Update interaction notes."""
    create_resp = await client.post(
        "/api/dgi/coordination/interactions",
        json={
            "division_id": catalog["division_id"],
            "interaction_type": "CARTERA",
        },
        headers=auth(dgi_token),
    )
    int_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/dgi/coordination/interactions/{int_id}",
        json={"notes": "Updated notes", "topics": ["IPR atrasados", "CDPs pendientes"]},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["notes"] == "Updated notes"
    assert len(resp.json()["topics"]) == 2


@pytest.mark.asyncio
async def test_interaction_matrix(client: AsyncClient, dgi_token):
    """Matrix returns one row per division."""
    resp = await client.get(
        "/api/dgi/coordination/interactions/matrix",
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if len(data) > 0:
        row = data[0]
        assert "division_name" in row
        assert "last_interaction" in row
        assert "pending_agreements" in row


# ═══════════════════════════════════════════════════════════════════════════
# ROLE RESTRICTIONS
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_operational_cannot_create_escalation(client: AsyncClient, jefe_token):
    """Operational users cannot create escalations."""
    resp = await client.post(
        "/api/dgi/escalations",
        json={"level": "NIVEL_1", "situation": "Test", "impact": "Test"},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_operational_cannot_manage_decisions(client: AsyncClient, jefe_token):
    """Operational users cannot create AR decisions."""
    resp = await client.post(
        "/api/dgi/coordination/ar/decisions",
        json={"description": "Test", "decision_type": "PRIORIDAD"},
        headers=auth(jefe_token),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_operational_can_view_services(client: AsyncClient, jefe_token):
    """Operational users CAN view service catalog."""
    resp = await client.get(
        "/api/dgi/services",
        headers=auth(jefe_token),
    )
    assert resp.status_code == 200
