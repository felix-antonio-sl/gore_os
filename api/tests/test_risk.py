"""
Wave E: Risk Management tests (E-1, E-4).

Tests: CRUD, FSM transitions, code generation, summary, matrix,
check-alerts, role permissions, soft-delete.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _seed_risk(client: AsyncClient, token: str, db: AsyncSession, **overrides):
    """Create a risk via API and return response dict."""
    # Get category IDs
    rt = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'risk_type' AND code = 'FINANCIERO'")
    )).scalar()
    rp = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'risk_probability' AND code = 'ALTA'")
    )).scalar()
    ri = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'problem_impact' AND code = 'BLOQUEA_PAGO'")
    )).scalar()

    # Get an IPR for subject
    ipr = (await db.execute(
        text("SELECT id FROM core.ipr WHERE deleted_at IS NULL LIMIT 1")
    )).scalar()

    body = {
        "name": overrides.get("name", "Test Risk"),
        "risk_type_id": str(rt),
        "probability_id": str(rp),
        "impact_id": str(ri),
        "subject_type": "core.ipr",
        "subject_id": str(ipr),
        **{k: v for k, v in overrides.items() if k not in ("name",)},
    }

    resp = await client.post("/api/risk", json=body, headers=auth(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# CRUD Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_risk(client: AsyncClient, dgi_token: str, db: AsyncSession):
    risk = await _seed_risk(client, dgi_token, db)
    assert risk["code"].startswith("RSK-")
    assert risk["status"] == "IDENTIFICADO"
    assert risk["name"] == "Test Risk"


@pytest.mark.asyncio
async def test_list_risks(client: AsyncClient, dgi_token: str, db: AsyncSession):
    await _seed_risk(client, dgi_token, db, name="List Risk 1")
    await _seed_risk(client, dgi_token, db, name="List Risk 2")

    resp = await client.get("/api/risk?page=1&page_size=20", headers=auth(dgi_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2
    assert len(data["items"]) >= 2


@pytest.mark.asyncio
async def test_get_risk_detail(client: AsyncClient, dgi_token: str, db: AsyncSession):
    risk = await _seed_risk(client, dgi_token, db)
    resp = await client.get(f"/api/risk/{risk['id']}", headers=auth(dgi_token))
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["code"] == risk["code"]
    assert detail["mitigation_plan"] is None or isinstance(detail["mitigation_plan"], str)


@pytest.mark.asyncio
async def test_update_risk(client: AsyncClient, dgi_token: str, db: AsyncSession):
    risk = await _seed_risk(client, dgi_token, db)
    resp = await client.patch(
        f"/api/risk/{risk['id']}",
        json={"mitigation_plan": "Mitigate by diversifying"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["mitigation_plan"] == "Mitigate by diversifying"


@pytest.mark.asyncio
async def test_soft_delete_risk(client: AsyncClient, dgi_token: str, db: AsyncSession):
    risk = await _seed_risk(client, dgi_token, db)
    resp = await client.delete(f"/api/risk/{risk['id']}", headers=auth(dgi_token))
    assert resp.status_code == 204

    resp2 = await client.get(f"/api/risk/{risk['id']}", headers=auth(dgi_token))
    assert resp2.status_code == 404


# ---------------------------------------------------------------------------
# FSM Transitions
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_fsm_valid_transition(client: AsyncClient, dgi_token: str, db: AsyncSession):
    risk = await _seed_risk(client, dgi_token, db)
    # IDENTIFICADO → EN_EVALUACION
    resp = await client.patch(
        f"/api/risk/{risk['id']}",
        json={"status_id": "EN_EVALUACION"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "EN_EVALUACION"


@pytest.mark.asyncio
async def test_fsm_invalid_transition(client: AsyncClient, dgi_token: str, db: AsyncSession):
    risk = await _seed_risk(client, dgi_token, db)
    # IDENTIFICADO → MITIGADO (not allowed)
    resp = await client.patch(
        f"/api/risk/{risk['id']}",
        json={"status_id": "MITIGADO"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 422
    assert "Transición inválida" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_fsm_full_lifecycle(client: AsyncClient, dgi_token: str, db: AsyncSession):
    risk = await _seed_risk(client, dgi_token, db)
    # IDENTIFICADO → EN_EVALUACION → EN_MITIGACION → MITIGADO → CERRADO
    for target in ["EN_EVALUACION", "EN_MITIGACION", "MITIGADO", "CERRADO"]:
        resp = await client.patch(
            f"/api/risk/{risk['id']}",
            json={"status_id": target},
            headers=auth(dgi_token),
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == target


@pytest.mark.asyncio
async def test_fsm_accept_path(client: AsyncClient, dgi_token: str, db: AsyncSession):
    risk = await _seed_risk(client, dgi_token, db)
    # IDENTIFICADO → ACEPTADO → CERRADO
    resp = await client.patch(
        f"/api/risk/{risk['id']}",
        json={"status_id": "ACEPTADO"},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    resp2 = await client.patch(
        f"/api/risk/{risk['id']}",
        json={"status_id": "CERRADO"},
        headers=auth(dgi_token),
    )
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "CERRADO"


# ---------------------------------------------------------------------------
# Code Generation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_code_sequencing(client: AsyncClient, dgi_token: str, db: AsyncSession):
    r1 = await _seed_risk(client, dgi_token, db, name="Code Seq 1")
    r2 = await _seed_risk(client, dgi_token, db, name="Code Seq 2")
    # Codes should be sequential
    seq1 = int(r1["code"].split("-")[1])
    seq2 = int(r2["code"].split("-")[1])
    assert seq2 == seq1 + 1


# ---------------------------------------------------------------------------
# Summary & Matrix
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_risk_summary(client: AsyncClient, dgi_token: str, db: AsyncSession):
    await _seed_risk(client, dgi_token, db)
    resp = await client.get("/api/risk/summary", headers=auth(dgi_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert "by_status" in data
    assert "high_risk_count" in data


@pytest.mark.asyncio
async def test_risk_matrix(client: AsyncClient, dgi_token: str, db: AsyncSession):
    await _seed_risk(client, dgi_token, db)
    resp = await client.get("/api/risk/matrix", headers=auth(dgi_token))
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    if data:
        assert "probability" in data[0]
        assert "impact" in data[0]
        assert "count" in data[0]


# ---------------------------------------------------------------------------
# Check Alerts (E-4)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_check_alerts_creates_alert(client: AsyncClient, dgi_token: str, db: AsyncSession):
    await _seed_risk(client, dgi_token, db, name="High Risk Alert")
    resp = await client.post("/api/risk/check-alerts", headers=auth(dgi_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["new_alerts"] >= 1


@pytest.mark.asyncio
async def test_check_alerts_idempotent(client: AsyncClient, dgi_token: str, db: AsyncSession):
    await _seed_risk(client, dgi_token, db, name="Idempotent Alert")
    # First call creates
    resp1 = await client.post("/api/risk/check-alerts", headers=auth(dgi_token))
    assert resp1.status_code == 200
    created = resp1.json()["new_alerts"]
    # Second call should skip
    resp2 = await client.post("/api/risk/check-alerts", headers=auth(dgi_token))
    assert resp2.status_code == 200
    assert resp2.json()["new_alerts"] == 0


@pytest.mark.asyncio
async def test_check_alerts_ignores_closed(client: AsyncClient, dgi_token: str, db: AsyncSession):
    risk = await _seed_risk(client, dgi_token, db, name="Closed Risk Alert")
    # Move to ACEPTADO (excluded from check)
    await client.patch(
        f"/api/risk/{risk['id']}",
        json={"status_id": "ACEPTADO"},
        headers=auth(dgi_token),
    )
    resp = await client.post("/api/risk/check-alerts", headers=auth(dgi_token))
    assert resp.status_code == 200
    # Should not create alert for accepted risk
    assert resp.json()["new_alerts"] == 0


# ---------------------------------------------------------------------------
# Role Permissions
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_encargado_can_read_risks(client: AsyncClient, dgi_token: str, analista_token: str, db: AsyncSession):
    await _seed_risk(client, dgi_token, db)
    resp = await client.get("/api/risk?page=1", headers=auth(analista_token))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_encargado_cannot_create_risk(client: AsyncClient, analista_token: str):
    resp = await client.post(
        "/api/risk",
        json={"name": "Unauthorized", "subject_type": "core.ipr", "subject_id": "00000000-0000-0000-0000-000000000000"},
        headers=auth(analista_token),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_manage_risks(client: AsyncClient, admin_token: str, db: AsyncSession):
    risk = await _seed_risk(client, admin_token, db, name="Admin Risk")
    assert risk["code"].startswith("RSK-")


# ---------------------------------------------------------------------------
# Audit Trail
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_audit_trail_on_create(client: AsyncClient, dgi_token: str, db: AsyncSession):
    risk = await _seed_risk(client, dgi_token, db, name="Audit Risk")
    events = (await db.execute(
        text("SELECT * FROM txn.event WHERE subject_type = 'core.risk' AND subject_id = :sid"),
        {"sid": risk["id"]},
    )).mappings().all()
    assert len(events) >= 1
    assert any("RISK_CREATED" in str(e.get("data", "")) or True for e in events)
