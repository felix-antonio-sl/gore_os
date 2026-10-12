"""Cross-domain inbox journeys, identity and authority against real PostgreSQL."""
import uuid

import pytest
from sqlalchemy import text
from tests.conftest import auth
from app.core.security import create_access_token

pytestmark = pytest.mark.asyncio


async def category(db, scheme, code):
    return str((await db.execute(text(
        "SELECT id FROM ref.category WHERE scheme = :scheme AND code = :code"
    ), {"scheme": scheme, "code": code})).scalar_one())


async def person(db, email):
    return str((await db.execute(text('SELECT id FROM core."user" WHERE email = :email'), {"email": email})).scalar_one())


@pytest.fixture(autouse=True)
async def cleanup_journey_data(db):
    yield
    await db.execute(text("DELETE FROM core.alert WHERE message LIKE 'R4-%'"))
    await db.execute(text("DELETE FROM core.risk WHERE name LIKE 'R4-%'"))
    await db.execute(text("DELETE FROM core.agreement_history WHERE agreement_id IN (SELECT id FROM core.agreement WHERE agreement_number LIKE 'R4-%')"))
    await db.execute(text("DELETE FROM core.agreement WHERE agreement_number LIKE 'R4-%'"))
    await db.execute(text("DELETE FROM core.ipr WHERE codigo_bip LIKE 'R4-%'"))
    await db.execute(text("DELETE FROM core.dgi_process WHERE code LIKE 'R4-%'"))
    await db.execute(text("DELETE FROM core.dgi_sla WHERE service_id IN (SELECT id FROM core.dgi_service WHERE name LIKE 'R4-%')"))
    await db.execute(text("DELETE FROM core.dgi_service_request WHERE description LIKE 'R4-%'"))
    await db.execute(text("DELETE FROM core.dgi_service WHERE name LIKE 'R4-%'"))
    await db.commit()


async def seed_ipr(db, owner):
    return str((await db.execute(text("""
        INSERT INTO core.ipr (codigo_bip, name, ipr_nature, assignee_id)
        VALUES (:code, 'R4-Synthetic IPR', 'PROYECTO', CAST(:owner AS uuid)) RETURNING id
    """), {"code": 'R4-' + uuid.uuid4().hex[:10], "owner": owner})).scalar_one())


async def seed_alert(db, ipr):
    return str((await db.execute(text("""
        INSERT INTO core.alert (alert_type_id, severity_id, subject_type, subject_id, message)
        VALUES (CAST(:kind AS uuid), CAST(:severity AS uuid), 'core.ipr', CAST(:ipr AS uuid), 'R4-Same attention message')
        RETURNING id
    """), {"kind": await category(db, 'alert_type', 'TRABAJO_VENCIDO'),
           "severity": await category(db, 'alert_level', 'CRITICO'), "ipr": ipr})).scalar_one())


async def seed_request(db, client, dgi_token, requester, days, age_hours):
    service = await client.post('/api/dgi/services', headers=auth(dgi_token), json={
        'name': 'R4-Service-' + uuid.uuid4().hex[:8], 'area': 'CG', 'sla_days': days,
    })
    assert service.status_code == 201, service.text
    sid = service.json()['id']
    # Different product contracts are not the service request's deadline.
    product_ids = (await db.execute(text("SELECT id FROM ref.category WHERE scheme = 'dgi_sla_product_type' ORDER BY code LIMIT 2"))).scalars().all()
    assert len(product_ids) == 2
    for pid, product_days in zip(product_ids, [1, 99]):
        await db.execute(text("INSERT INTO core.dgi_sla (service_id, product_type_id, target_days) VALUES (CAST(:sid AS uuid), :pid, :days)"), {'sid': sid, 'pid': pid, 'days': product_days})
    rid = str((await db.execute(text("""
        INSERT INTO core.dgi_service_request (code, service_id, requester_id, description, status_id, created_at)
        VALUES (:code, CAST(:sid AS uuid), CAST(:requester AS uuid), 'R4-Synthetic request',
            CAST(:state AS uuid), NOW() - CAST(:hours AS double precision) * INTERVAL '1 hour') RETURNING id
    """), {'code': 'R4-' + uuid.uuid4().hex[:8], 'sid': sid, 'requester': requester,
           'state': await category(db, 'dgi_request_status', 'RECIBIDA'), 'hours': age_hours})).scalar_one())
    # Keep this transaction open: NOW() is the same clock for the boundary case and GETs.
    return rid


@pytest.mark.parametrize('days,age_hours,overdue', [(2, 47.5, False), (2, 48, False), (2, 48.5, True), (None, 240, False)])
async def test_service_deadline_agrees_between_inbox_and_request(
    db, client, dgi_token, regional_token, days, age_hours, overdue,
):
    requester = await person(db, 'regional@goreos.cl')
    rid = await seed_request(db, client, dgi_token, requester, days, age_hours)
    detail = await client.get(f'/api/dgi/services/requests/{rid}', headers=auth(regional_token))
    assert detail.status_code == 200, detail.text
    assert detail.json()['sla_days'] == days
    assert detail.json()['is_overdue'] is overdue
    inbox = await client.get('/api/dashboard/action-items', headers=auth(regional_token))
    assert inbox.status_code == 200, inbox.text
    items = [item for item in inbox.json()['items'] if item['category'] == 'SLA' and item['id'] == rid]
    assert len(items) == int(overdue)
    if overdue:
        assert items[0]['action_route'] == f'/servicios/solicitudes/{rid}'
        assert items[0]['subtitle'].endswith(f'/ {days}d')


async def test_request_attention_never_grants_foreign_request_reading(db, client, dgi_token, regional_token, secretario_token):
    rid = await seed_request(db, client, dgi_token, await person(db, 'regional@goreos.cl'), 2, 49)
    denied = await client.get(f'/api/dgi/services/requests/{rid}', headers=auth(secretario_token))
    assert denied.status_code == 403
    inbox = await client.get('/api/dashboard/action-items', headers=auth(secretario_token))
    assert rid not in {item['id'] for item in inbox.json()['items']}
    dgi_detail = await client.get(f'/api/dgi/services/requests/{rid}', headers=auth(dgi_token))
    assert dgi_detail.json()['allowed_statuses']
    readonly = await client.get(f'/api/dgi/services/requests/{rid}', headers=auth(regional_token))
    assert readonly.json()['allowed_statuses'] == []


@pytest.mark.parametrize('email,role', [
    ('analista.dipir@goreos.cl', 'ANALISTA'),
    ('jefe.daf@goreos.cl', 'JEFE_DIVISION'),
])
async def test_personal_and_division_request_attention_is_owner_scoped(db, client, dgi_token, email, role):
    owner = await person(db, email)
    token = create_access_token({'sub': owner, 'role': role})
    own = await seed_request(db, client, dgi_token, owner, 2, 49)
    foreign = await seed_request(db, client, dgi_token, await person(db, 'regional@goreos.cl'), 2, 49)
    detail = await client.get(f'/api/dgi/services/requests/{own}', headers=auth(token))
    assert detail.status_code == 200 and detail.json()['is_overdue']
    inbox = await client.get('/api/dashboard/action-items', headers=auth(token))
    assert inbox.status_code == 200, inbox.text
    ids = {item['id'] for item in inbox.json()['items'] if item['category'] == 'SLA'}
    assert own in ids and foreign not in ids
    denied = await client.get(f'/api/dgi/services/requests/{foreign}', headers=auth(token))
    assert denied.status_code == 403


async def test_equal_alert_messages_preserve_identity_and_independent_attendance(db, client, analista_token):
    owner = await person(db, 'analista.dipir@goreos.cl')
    first = await seed_alert(db, await seed_ipr(db, owner))
    second = await seed_alert(db, await seed_ipr(db, owner))
    inbox = await client.get('/api/dashboard/action-items', headers=auth(analista_token))
    items = {item['id']: item for item in inbox.json()['items']}
    assert {first, second} <= items.keys()
    for aid in [first, second]:
        assert items[aid]['action_route'] == f'/alertas?id={aid}'
    response = await client.post(f'/api/alertas/{first}/atender', headers=auth(analista_token), json={'action_taken': 'Synthetic attention'})
    assert response.status_code == 200, response.text
    attended = (await db.execute(text('SELECT id, attended_at FROM core.alert WHERE id IN (CAST(:one AS uuid), CAST(:two AS uuid))'), {'one': first, 'two': second})).mappings().all()
    dates = {str(row['id']): row['attended_at'] for row in attended}
    assert dates[first] is not None and dates[second] is None
    refreshed = await client.get('/api/dashboard/action-items', headers=auth(analista_token))
    refreshed_items = {item['id']: item for item in refreshed.json()['items']}
    assert {first, second} <= refreshed_items.keys()
    assert refreshed_items[first]['state'] == 'ATENDIDA'
    assert refreshed_items[second]['state'] == 'SIN_RESOLVER'


async def test_alert_attendance_cannot_bypass_assignment(db, client, analista_token):
    foreign = await seed_alert(db, await seed_ipr(db, await person(db, 'rtf.daf@goreos.cl')))
    listed = await client.get(f'/api/alertas?alerta_id={foreign}', headers=auth(analista_token))
    assert listed.json()['items'] == []
    denied = await client.post(f'/api/alertas/{foreign}/atender', headers=auth(analista_token), json={})
    assert denied.status_code == 404
    assert (await db.execute(text('SELECT attended_at FROM core.alert WHERE id = CAST(:id AS uuid)'), {'id': foreign})).scalar_one() is None


async def test_signature_feed_uses_the_stored_transition_category(db, client, regional_token):
    # No VISADO_INTERNAMENTE category exists in the canonical seeded catalog.
    state = await category(db, 'agreement_state', 'EN_REVISION_JURIDICA')
    kind = str((await db.execute(text("SELECT id FROM ref.category WHERE scheme = 'agreement_type' LIMIT 1"))).scalar_one())
    aid = str((await db.execute(text("""
        INSERT INTO core.agreement (agreement_number, agreement_type_id, state_id, total_amount)
        VALUES (:number, CAST(:kind AS uuid), CAST(:state AS uuid), 100) RETURNING id
    """), {'number': 'R4-' + uuid.uuid4().hex[:8], 'kind': kind, 'state': state})).scalar_one())
    inbox = await client.get('/api/dashboard/action-items', headers=auth(regional_token))
    item = next(item for item in inbox.json()['items'] if item['id'] == aid)
    assert item['category'] == 'FIRMA' and item['state'] == 'EN_REVISION_JURIDICA'
    assert item['action_route'] == f'/convenios?id={aid}'
    transitions = await client.get(f'/api/convenios/{aid}/transiciones', headers=auth(regional_token))
    signing = next(item for item in transitions.json() if item['code'] == 'FIRMADO_GORE')
    assert not signing.get('blocked')
    changed = await client.patch(f'/api/convenios/{aid}', headers=auth(regional_token), json={'state_id': signing['id']})
    assert changed.status_code == 200, changed.text
    detail = await client.get(f'/api/convenios/{aid}', headers=auth(regional_token))
    assert detail.json()['state'] == 'FIRMADO_GORE' and detail.json()['history']
    refreshed = await client.get('/api/dashboard/action-items', headers=auth(regional_token))
    assert aid not in {item['id'] for item in refreshed.json()['items']}


async def test_readonly_signature_has_no_executable_transition(db, client, regional_token, consejero_token, catalog):
    created = await client.post('/api/convenios', headers=auth(regional_token), json={
        'agreement_number': 'R4-' + uuid.uuid4().hex[:8], 'agreement_type_id': catalog['agreement_type_id'],
        'state_id': catalog['agreement_state_borrador_id'], 'total_amount': 100,
    })
    assert created.status_code == 201, created.text
    readonly = await client.get(f"/api/convenios/{created.json()['id']}/transiciones", headers=auth(consejero_token))
    assert readonly.json() == []


async def test_risk_detail_respects_the_same_assignment_as_its_list(db, client, dgi_token, analista_token):
    ipr = await seed_ipr(db, await person(db, 'rtf.daf@goreos.cl'))
    created = await client.post('/api/risk', headers=auth(dgi_token), json={
        'name': 'R4-Foreign risk', 'subject_type': 'core.ipr', 'subject_id': ipr,
        'risk_type_id': await category(db, 'risk_type', 'OPERACIONAL'),
        'probability_id': await category(db, 'risk_probability', 'ALTA'),
        'impact_id': await category(db, 'problem_impact', 'BLOQUEA_PAGO'),
    })
    assert created.status_code == 201, created.text
    rid = created.json()['id']
    denied = await client.get(f'/api/risk/{rid}', headers=auth(analista_token))
    assert denied.status_code == 404
    allowed = await client.get(f'/api/risk/{rid}', headers=auth(dgi_token))
    assert allowed.status_code == 200 and allowed.json()['allowed_statuses']


async def test_personal_risk_attention_matches_its_reader_scope(db, client, dgi_token, analista_token):
    risks = []
    for email in ['analista.dipir@goreos.cl', 'rtf.daf@goreos.cl']:
        ipr = await seed_ipr(db, await person(db, email))
        response = await client.post('/api/risk', headers=auth(dgi_token), json={
            'name': 'R4-Scoped risk', 'subject_type': 'core.ipr', 'subject_id': ipr,
            'probability_id': await category(db, 'risk_probability', 'ALTA'),
            'impact_id': await category(db, 'problem_impact', 'BLOQUEA_PAGO'),
        })
        assert response.status_code == 201, response.text
        risks.append(response.json()['id'])
    reader = await client.get(f'/api/risk/{risks[0]}', headers=auth(analista_token))
    assert reader.status_code == 200 and reader.json()['allowed_statuses'] == []
    inbox = await client.get('/api/dashboard/action-items', headers=auth(analista_token))
    ids = {item['id'] for item in inbox.json()['items'] if item['category'] == 'RIESGO'}
    assert risks[0] in ids and risks[1] not in ids


async def test_process_reader_requires_an_accessible_related_risk(db, client, dgi_token, consejero_token):
    pid = str((await db.execute(text("""
        INSERT INTO core.dgi_process (code, name, status_id)
        VALUES (:code, 'R4-Related process', CAST(:state AS uuid)) RETURNING id
    """), {'code': 'R4-' + uuid.uuid4().hex[:8], 'state': await category(db, 'dgi_process_status', 'IDENTIFICADO')})).scalar_one())
    denied = await client.get(f'/api/dgi/processes/{pid}', headers=auth(consejero_token))
    assert denied.status_code == 404
    created = await client.post('/api/risk', headers=auth(dgi_token), json={
        'name': 'R4-Process risk', 'subject_type': 'core.dgi_process', 'subject_id': pid,
        'risk_type_id': await category(db, 'risk_type', 'OPERACIONAL'),
        'probability_id': await category(db, 'risk_probability', 'ALTA'),
        'impact_id': await category(db, 'problem_impact', 'BLOQUEA_PAGO'),
    })
    assert created.status_code == 201, created.text
    allowed = await client.get(f'/api/dgi/processes/{pid}', headers=auth(consejero_token))
    assert allowed.status_code == 200 and allowed.json()['name'] == 'R4-Related process'
    update = await client.patch(f'/api/dgi/processes/{pid}', headers=auth(dgi_token), json={'name': 'Mutation forbidden'})
    assert update.status_code == 405
