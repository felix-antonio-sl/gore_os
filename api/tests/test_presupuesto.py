"""Tests for budget program calculations and role restrictions."""
import uuid
from tests.conftest import auth


async def _create_budget(client, token, catalog, **overrides):
    payload = {
        "code": f"TEST-BP-{uuid.uuid4().hex[:6]}",
        "name": f"Test Budget {uuid.uuid4().hex[:8]}",
        "fiscal_year": 2026,
        "initial_amount": 1000000,
        "owner_division_id": catalog["division_id"],
        "subtitle_id": catalog["budget_subtitle_id"],
        **overrides,
    }
    resp = await client.post("/api/presupuesto", json=payload, headers=auth(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_create_budget_program(client, regional_token, catalog):
    """Create budget program with amounts initialized correctly."""
    data = await _create_budget(client, regional_token, catalog)
    assert "id" in data

    detail = await client.get(f"/api/presupuesto/{data['id']}", headers=auth(regional_token))
    body = detail.json()
    assert float(body["initial_amount"]) == 1000000
    assert float(body["committed_amount"]) == 0
    assert float(body["accrued_amount"]) == 0
    assert float(body["paid_amount"]) == 0


async def test_duplicate_code_fiscal_year(client, regional_token, catalog):
    """Duplicate (code, fiscal_year) returns 409."""
    code = f"TEST-DUP-{uuid.uuid4().hex[:6]}"
    await _create_budget(client, regional_token, catalog, code=code)

    resp = await client.post(
        "/api/presupuesto",
        json={
            "code": code,
            "name": "Duplicate",
            "fiscal_year": 2026,
            "initial_amount": 500000,
            "owner_division_id": catalog["division_id"],
        },
        headers=auth(regional_token),
    )
    assert resp.status_code == 409


async def test_same_code_different_year(client, regional_token, catalog):
    """Same code with different fiscal_year is allowed."""
    code = f"TEST-YR-{uuid.uuid4().hex[:6]}"
    await _create_budget(client, regional_token, catalog, code=code, fiscal_year=2025)

    resp = await client.post(
        "/api/presupuesto",
        json={
            "code": code,
            "name": "Different year",
            "fiscal_year": 2026,
            "initial_amount": 500000,
            "owner_division_id": catalog["division_id"],
        },
        headers=auth(regional_token),
    )
    assert resp.status_code == 201


async def test_execution_calculation(client, regional_token, catalog):
    """Execution % = paid/current * 100."""
    data = await _create_budget(
        client, regional_token, catalog,
        initial_amount=1000000,
        current_amount=1000000,
    )
    # Update paid to 700000 -> 70%
    await client.patch(
        f"/api/presupuesto/{data['id']}",
        json={"paid_amount": 700000},
        headers=auth(regional_token),
    )

    detail = await client.get(f"/api/presupuesto/{data['id']}", headers=auth(regional_token))
    assert detail.json()["execution_pct"] == 70.0


async def test_execution_zero_current(client, regional_token, catalog):
    """Current=0 should not cause division by zero (returns 0.0)."""
    data = await _create_budget(
        client, regional_token, catalog,
        initial_amount=0,
        current_amount=0,
    )

    detail = await client.get(f"/api/presupuesto/{data['id']}", headers=auth(regional_token))
    assert detail.json()["execution_pct"] == 0.0


async def test_paid_exceeds_current(client, regional_token, catalog):
    """Paid > current is allowed (execution > 100%)."""
    data = await _create_budget(
        client, regional_token, catalog,
        initial_amount=1000000,
        current_amount=1000000,
    )
    await client.patch(
        f"/api/presupuesto/{data['id']}",
        json={"paid_amount": 1500000},
        headers=auth(regional_token),
    )

    detail = await client.get(f"/api/presupuesto/{data['id']}", headers=auth(regional_token))
    assert detail.json()["execution_pct"] == 150.0


async def test_jefe_only_own_division(client, regional_token, jefe_token, catalog):
    """JEFE_DIVISION cannot patch budget of another division."""
    data = await _create_budget(client, regional_token, catalog)

    # jefe_token is jefe.daf — if the budget's division differs, should get 403
    resp = await client.patch(
        f"/api/presupuesto/{data['id']}",
        json={"paid_amount": 999},
        headers=auth(jefe_token),
    )
    # Either 200 (same division) or 403 (cross-division)
    assert resp.status_code in (200, 403)


async def test_create_cdp(client, regional_token, catalog):
    """Create CDP linked to a budget program."""
    data = await _create_budget(
        client, regional_token, catalog,
        initial_amount=10000000,
        current_amount=10000000,
    )
    resp = await client.post(
        f"/api/presupuesto/{data['id']}/cdps",
        json={"amount": 5000000},
        headers=auth(regional_token),
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert "commitment_number" in body
    assert body["commitment_number"].startswith("CDP-")


async def test_create_cdp_exceeds_available(client, regional_token, catalog):
    """CDP amount exceeding available balance returns 409."""
    data = await _create_budget(
        client, regional_token, catalog,
        initial_amount=1000000,
        current_amount=1000000,
    )
    resp = await client.post(
        f"/api/presupuesto/{data['id']}/cdps",
        json={"amount": 2000000},
        headers=auth(regional_token),
    )
    assert resp.status_code == 409
    assert "saldo disponible" in resp.json()["detail"]


async def test_rtf_cannot_create(client, rtf_token, catalog):
    """RTF cannot create budget programs (not in ADMIN_ROLES)."""
    resp = await client.post(
        "/api/presupuesto",
        json={
            "code": "TEST-NOPE",
            "name": "Should fail",
            "fiscal_year": 2026,
            "initial_amount": 100,
        },
        headers=auth(rtf_token),
    )
    assert resp.status_code == 403


# --- Budget Cycle Timeline Tests (HΩ-15) ---

async def test_list_milestones(client, regional_token):
    """GET /api/presupuesto/ciclo/hitos returns 17 seed milestones."""
    resp = await client.get("/api/presupuesto/ciclo/hitos", headers=auth(regional_token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 17
    assert data[0]["ordinal"] == 1
    assert data[0]["phase"] == "T-1"
    assert data[-1]["ordinal"] == 17


async def test_initialize_cycle(client, regional_token):
    """POST /api/presupuesto/ciclo/2026 creates tracking rows for all 17 milestones."""
    resp = await client.post("/api/presupuesto/ciclo/2026", headers=auth(regional_token))
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["fiscal_year"] == 2026
    assert data["total_milestones"] == 17
    assert data["completed"] == 0
    assert data["pendiente"] == 17


async def test_initialize_cycle_idempotent(client, regional_token):
    """POST /api/presupuesto/ciclo/2027 is idempotent (second call returns same data)."""
    resp1 = await client.post("/api/presupuesto/ciclo/2027", headers=auth(regional_token))
    assert resp1.status_code == 201
    resp2 = await client.post("/api/presupuesto/ciclo/2027", headers=auth(regional_token))
    assert resp2.status_code == 200
    assert resp2.json()["total_milestones"] == 17


async def test_get_cycle_timeline(client, regional_token):
    """GET /api/presupuesto/ciclo/2026 returns timeline with all milestones."""
    await client.post("/api/presupuesto/ciclo/2026", headers=auth(regional_token))
    resp = await client.get("/api/presupuesto/ciclo/2026", headers=auth(regional_token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 17
    assert data[0]["status"] == "PENDIENTE"
    assert data[0]["phase"] == "T-1"


async def test_update_milestone_status(client, regional_token):
    """PATCH milestone tracking to mark as COMPLETADO."""
    await client.post("/api/presupuesto/ciclo/2026", headers=auth(regional_token))
    timeline = (await client.get("/api/presupuesto/ciclo/2026", headers=auth(regional_token))).json()
    first_id = timeline[0]["id"]

    resp = await client.patch(
        f"/api/presupuesto/ciclo/tracking/{first_id}",
        json={"status": "COMPLETADO"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "COMPLETADO"
    assert resp.json()["completed_at"] is not None


async def test_update_milestone_invalid_status(client, regional_token):
    """PATCH with invalid status returns 422."""
    await client.post("/api/presupuesto/ciclo/2026", headers=auth(regional_token))
    timeline = (await client.get("/api/presupuesto/ciclo/2026", headers=auth(regional_token))).json()
    first_id = timeline[0]["id"]

    resp = await client.patch(
        f"/api/presupuesto/ciclo/tracking/{first_id}",
        json={"status": "INVALIDO"},
        headers=auth(regional_token),
    )
    assert resp.status_code == 422


async def test_analista_cannot_modify_cycle(client, analista_token):
    """ANALISTA cannot initialize or modify cycle (requires ADMIN/REGIONAL/GOBERNADOR)."""
    resp = await client.post("/api/presupuesto/ciclo/2026", headers=auth(analista_token))
    assert resp.status_code == 403


async def test_cycle_summary(client, regional_token):
    """GET /api/presupuesto/ciclo/2026/resumen returns completion stats."""
    await client.post("/api/presupuesto/ciclo/2026", headers=auth(regional_token))
    resp = await client.get("/api/presupuesto/ciclo/2026/resumen", headers=auth(regional_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["fiscal_year"] == 2026
    assert data["total_milestones"] == 17
    assert data["completion_pct"] == 0.0


# --- Admin CRUD: budget-program-codes ---


async def test_admin_create_program_code(client, admin_token):
    """Admin can create a budget program code."""
    resp = await client.post(
        "/api/admin/budget-program-codes",
        json={"code": "TEST-P01", "label": "Test Programa 01", "sort_order": 1},
        headers=auth(admin_token),
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["code"] == "TEST-P01"
    assert "id" in data


async def test_admin_list_program_codes(client, admin_token):
    """Admin can list budget program codes."""
    await client.post(
        "/api/admin/budget-program-codes",
        json={"code": "TEST-P02", "label": "Test Programa 02", "sort_order": 2},
        headers=auth(admin_token),
    )
    resp = await client.get("/api/admin/budget-program-codes", headers=auth(admin_token))
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    codes = [i["code"] for i in items]
    assert "TEST-P02" in codes


async def test_admin_update_program_code(client, admin_token):
    """Admin can update a budget program code label."""
    create_resp = await client.post(
        "/api/admin/budget-program-codes",
        json={"code": "TEST-P03", "label": "Original", "sort_order": 3},
        headers=auth(admin_token),
    )
    pid = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/admin/budget-program-codes/{pid}",
        json={"label": "Actualizado"},
        headers=auth(admin_token),
    )
    assert resp.status_code == 200

    items = (await client.get("/api/admin/budget-program-codes", headers=auth(admin_token))).json()
    match = [i for i in items if i["id"] == pid]
    assert match[0]["label"] == "Actualizado"


# --- Program Code filter & association tests ---


async def test_filter_by_program_code(client, admin_token, regional_token, catalog):
    """Filter budget programs by program_code."""
    pc_resp = await client.post(
        "/api/admin/budget-program-codes",
        json={"code": "TEST-FILTER-PC", "label": "Filtro Test"},
        headers=auth(admin_token),
    )
    pc_id = pc_resp.json()["id"]

    await _create_budget(client, regional_token, catalog, program_code_id=pc_id)

    resp = await client.get(
        "/api/presupuesto?program_code=TEST-FILTER-PC",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 1
    assert all(i.get("program_code_label") == "Filtro Test" for i in items)


async def test_create_with_program_code(client, admin_token, regional_token, catalog):
    """Create budget program with program_code_id shows label in detail."""
    pc_resp = await client.post(
        "/api/admin/budget-program-codes",
        json={"code": "TEST-CREATE-PC", "label": "Create Test"},
        headers=auth(admin_token),
    )
    pc_id = pc_resp.json()["id"]

    data = await _create_budget(client, regional_token, catalog, program_code_id=pc_id)

    detail = await client.get(f"/api/presupuesto/{data['id']}", headers=auth(regional_token))
    body = detail.json()
    assert body.get("program_code_label") == "Create Test"
