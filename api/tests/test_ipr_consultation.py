"""IPR consultation, archived writers and surviving work with synthetic records."""
import uuid
from datetime import date, timedelta

import pytest
import pytest_asyncio
from sqlalchemy import text

from app.core.audit import record_event
from app.main import create_app
from tests.conftest import auth

pytestmark = pytest.mark.asyncio
READ_RECORDS = [
    "historial", "track-info", "cdps", "avances", "partes", "territorio", "hitos",
    "evaluaciones", "parentesco", "admisibilidad", "certificacion-tecnica",
    "modificaciones", "cierre", "evaluacion-expost",
]


async def category(db, scheme, code=None):
    return str((await db.execute(text("""
        SELECT id FROM ref.category WHERE scheme = :scheme
        AND (CAST(:code AS text) IS NULL OR code = :code) ORDER BY code LIMIT 1
    """), {"scheme": scheme, "code": code})).scalar_one())


async def snapshot(db, ipr_id):
    return dict((await db.execute(text("""
        SELECT name, status_id, mcd_phase_id, phase_entered_at, assignee_id, sponsor_division_id
        FROM core.ipr WHERE id = CAST(:id AS uuid)
    """), {"id": ipr_id})).mappings().one())


@pytest_asyncio.fixture
async def record(db, catalog):
    owner = catalog["users"]["rtf.daf@goreos.cl"]
    ipr_id = str((await db.execute(text("""
        INSERT INTO core.ipr (codigo_bip, name, ipr_nature, status_id, mcd_phase_id,
                              mechanism_id, assignee_id, sponsor_division_id)
        VALUES (:code, 'Expediente histórico sintético', 'PROYECTO', CAST(:state AS uuid),
                CAST(:phase AS uuid), CAST(:mechanism AS uuid), CAST(:owner AS uuid),
                CAST(:division AS uuid)) RETURNING id
    """), {"code": "R5-" + uuid.uuid4().hex[:12], "state": await category(db, "ipr_state", "EN_EJECUCION"),
           "phase": await category(db, "mcd_phase", "F4"), "mechanism": await category(db, "mechanism", "C33"),
           "owner": owner["id"], "division": owner["division_id"]})).scalar_one())
    await db.commit()
    yield ipr_id
    await db.rollback()
    # All data belongs to the isolated test database. FK dependents are removed first.
    for table in ("alert",):
        await db.execute(text(f"DELETE FROM core.{table} WHERE subject_type = 'core.ipr' AND subject_id = CAST(:id AS uuid)"), {"id": ipr_id})
    await db.execute(text("DELETE FROM txn.event WHERE subject_type = 'core.ipr' AND subject_id = CAST(:id AS uuid)"), {"id": ipr_id})
    await db.execute(text("DELETE FROM core.rendition_history WHERE rendition_id IN (SELECT id FROM core.rendition WHERE ipr_id = CAST(:id AS uuid))"), {"id": ipr_id})
    await db.execute(text("DELETE FROM core.rendition WHERE ipr_id = CAST(:id AS uuid)"), {"id": ipr_id})
    await db.execute(text("DELETE FROM core.agreement_history WHERE agreement_id IN (SELECT id FROM core.agreement WHERE ipr_id = CAST(:id AS uuid))"), {"id": ipr_id})
    await db.execute(text("DELETE FROM core.agreement WHERE ipr_id = CAST(:id AS uuid)"), {"id": ipr_id})
    await db.execute(text("DELETE FROM core.budget_commitment WHERE ipr_id = CAST(:id AS uuid)"), {"id": ipr_id})
    await db.execute(text("DELETE FROM core.budget_program WHERE code = :code"), {"code": "R5-" + ipr_id.replace("-", "")[:24]})
    for table in ("operational_commitment", "ipr_problem", "progress_report", "admissibility_check",
                  "kinship_declaration", "ipr_modification", "ipr_closure", "ipr_expost_evaluation"):
        await db.execute(text(f"DELETE FROM core.{table} WHERE ipr_id = CAST(:id AS uuid)"), {"id": ipr_id})
    await db.execute(text("DELETE FROM core.ipr WHERE id = CAST(:id AS uuid)"), {"id": ipr_id})
    await db.commit()


async def test_consultation_returns_registered_phase_and_responsible(client, regional_token, db, record):
    before = await snapshot(db, record)
    detail = await client.get(f"/api/ipr/{record}", headers=auth(regional_token))
    assert detail.status_code == 200
    data = detail.json()
    assert data["status"] == "EN_EJECUCION" and data["mcd_phase"] == "F4"
    assert data["assignee_id"] == str(before["assignee_id"])
    assert data["assignee_name"] and data["sponsor_division_name"]
    assert "current_actor" not in data
    assert await snapshot(db, record) == before


@pytest.mark.parametrize("section", READ_RECORDS)
async def test_historical_reads_respect_ipr_scope(client, regional_token, rtf_token, analista_token, record, section):
    route = f"/api/ipr/{record}/{section}"
    for token in (regional_token, rtf_token):
        response = await client.get(route, headers=auth(token))
        assert response.status_code == 200, response.text
    denied = await client.get(route, headers=auth(analista_token))
    assert denied.status_code == 403


@pytest.mark.parametrize("role_fixture", ["admin_token", "regional_token", "gobernador_token", "analista_token", "consejero_token"])
async def test_no_role_can_write_an_ipr(client, role_fixture, record, db, admin_token, regional_token, gobernador_token, analista_token, consejero_token):
    token = {"admin_token": admin_token, "regional_token": regional_token, "gobernador_token": gobernador_token,
             "analista_token": analista_token, "consejero_token": consejero_token}[role_fixture]
    before = await snapshot(db, record)
    for method, path in [
        ("post", "/api/ipr"), ("patch", f"/api/ipr/{record}"),
        ("post", f"/api/ipr/{record}/avances"), ("post", f"/api/ipr/{record}/evaluaciones"),
        ("post", f"/api/ipr/{record}/admisibilidad/{uuid.uuid4()}/verificar"),
        ("post", f"/api/ipr/{record}/cierre"), ("patch", f"/api/ipr/{record}/modificaciones/{uuid.uuid4()}"),
    ]:
        response = await getattr(client, method)(path, headers=auth(token), json={"name": "Must not change", "status_id": str(uuid.uuid4())})
        assert response.status_code in (404, 405), (path, response.text)
    assert await snapshot(db, record) == before


async def test_autonomous_routes_are_not_registered():
    routes = create_app().routes
    ipr_routes = [r for r in routes if r.path.startswith("/api/ipr")]
    assert ipr_routes and all(r.methods == {"GET"} for r in ipr_routes)
    assert all(not r.path.startswith(("/api/core-sessions", "/api/presupuesto")) for r in routes)
    assert all(not r.path.endswith(("/transiciones", "/readiness", "/track-summary")) for r in ipr_routes)


async def test_existing_history_progress_and_cdp_remain_readable(client, regional_token, db, record, catalog):
    owner = catalog["users"]["rtf.daf@goreos.cl"]["id"]
    state = await category(db, "ipr_state", "EN_EJECUCION")
    await record_event(db, "STATE_TRANSITION", "core.ipr", record, owner,
                       {"old_status_id": state, "new_status_id": state, "comment": "Antecedente sintético preservado"})
    await db.execute(text("""
        INSERT INTO core.progress_report (ipr_id, report_number, report_date, description, reported_by_id)
        VALUES (CAST(:id AS uuid), 1, CURRENT_DATE, 'Informe histórico sintético', CAST(:owner AS uuid))
    """), {"id": record, "owner": owner})
    budget = (await db.execute(text("""
        INSERT INTO core.budget_program (code, name, fiscal_year, initial_amount, current_amount)
        VALUES (:code, 'Programa histórico sintético', 2026, 1000, 1000) RETURNING id
    """), {"code": "R5-" + record.replace("-", "")[:24]})).scalar_one()
    number = "CDP-HIST-" + record.replace("-", "")[:16]
    await db.execute(text("""
        INSERT INTO core.budget_commitment (commitment_number, budget_program_id, ipr_id, amount, issued_at, status_id)
        VALUES (:number, :budget, CAST(:ipr AS uuid), 100, CURRENT_DATE, CAST(:state AS uuid))
    """), {"number": number, "budget": budget, "ipr": record, "state": await category(db, "budget_commitment_status")})
    await db.commit()
    before = await snapshot(db, record)
    for section, field, expected in [
        ("historial", "comment", "Antecedente sintético preservado"),
        ("avances", "description", "Informe histórico sintético"),
        ("cdps", "commitment_number", number),
    ]:
        response = await client.get(f"/api/ipr/{record}/{section}", headers=auth(regional_token))
        assert response.status_code == 200 and response.json()[0][field] == expected
    assert await snapshot(db, record) == before


async def test_five_related_actions_leave_parent_phase_and_assignment_unchanged(
    client, regional_token, rtf_token, db, record, catalog,
):
    before = await snapshot(db, record)
    owner = catalog["users"]["rtf.daf@goreos.cl"]["id"]
    commitment = await client.post("/api/compromisos", headers=auth(regional_token), json={
        "ipr_id": record, "description": "R5-Compromiso sintético", "commitment_type_id": catalog["commitment_type_id"],
        "responsible_id": owner, "due_date": str(date.today() + timedelta(days=1)),
    })
    assert commitment.status_code == 201, commitment.text
    completed = await client.post(f"/api/compromisos/{commitment.json()['id']}/completar", headers=auth(rtf_token), json={})
    assert completed.status_code == 200, completed.text
    problem = await client.post("/api/problemas", headers=auth(regional_token), json={
        "ipr_id": record, "problem_type_id": catalog["problem_type_id"], "description": "R5-Problema sintético",
    })
    assert problem.status_code == 201, problem.text
    resolved = await client.patch(f"/api/problemas/{problem.json()['id']}", headers=auth(regional_token), json={
        "state_id": await category(db, "problem_state", "RESUELTO"), "solution_applied": "Resuelto en pruebas",
    })
    assert resolved.status_code == 200, resolved.text
    alert = str((await db.execute(text("""
        INSERT INTO core.alert (alert_type_id, severity_id, subject_type, subject_id, message)
        VALUES (CAST(:kind AS uuid), CAST(:severity AS uuid), 'core.ipr', CAST(:ipr AS uuid), 'R5-Alerta sintética') RETURNING id
    """), {"kind": await category(db, "alert_type"), "severity": await category(db, "alert_level", "CRITICO"), "ipr": record})).scalar_one())
    await db.commit()
    attended = await client.post(f"/api/alertas/{alert}/atender", headers=auth(regional_token), json={"action_taken": "Atendida en pruebas"})
    assert attended.status_code == 200, attended.text
    agreement = await client.post("/api/convenios", headers=auth(regional_token), json={
        "ipr_id": record, "agreement_type_id": catalog["agreement_type_id"], "state_id": catalog["agreement_state_borrador_id"], "total_amount": 100,
    })
    assert agreement.status_code == 201, agreement.text
    changed = await client.patch(f"/api/convenios/{agreement.json()['id']}", headers=auth(regional_token), json={"state_id": catalog["agreement_state_en_negociacion_id"]})
    assert changed.status_code == 200, changed.text
    rendition = await client.post("/api/dgi/data/rendiciones", headers=auth(regional_token), json={"ipr_id": record, "amount": 100})
    assert rendition.status_code == 201, rendition.text
    assert await snapshot(db, record) == before
