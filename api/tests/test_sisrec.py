"""Tests para SISREC Multi-Role Workflow (Ciclo 19).

Covers:
- Full state machine: PENDIENTE → EN_REVISION_RTF → VISADA_RTF → EN_REVISION_UCR → APROBADA/RECHAZADA
- Observation loop: EN_REVISION_RTF/UCR → OBSERVADA → EN_REVISION_RTF
- Role-based authorization per transition
- History audit trail with comments
- SLA overdue detection
- Amount field CRUD
- Art. 18 CGR gap fix (paid_amount/paid_at)
"""
import uuid
import pytest
from sqlalchemy import text
from tests.conftest import auth


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _age_rendicion(db, rid: str, interval: str) -> None:
    """Age a rendicion's phase_entered_at and updated_at by the given interval."""
    await db.execute(text("ALTER TABLE core.rendition DISABLE TRIGGER trg_rendition_updated_at"))
    await db.execute(
        text(f"UPDATE core.rendition SET updated_at = NOW() - INTERVAL '{interval}', "
             f"phase_entered_at = NOW() - INTERVAL '{interval}' WHERE id = :id"),
        {"id": rid},
    )
    await db.execute(text("ALTER TABLE core.rendition ENABLE TRIGGER trg_rendition_updated_at"))
    await db.commit()

async def _ensure_ipr(db) -> str:
    """Get or create a test IPR."""
    r = await db.execute(text("SELECT id FROM core.ipr LIMIT 1"))
    row = r.scalar()
    if row:
        return str(row)
    code = f"T-SISREC-{uuid.uuid4().hex[:8].upper()}"
    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (codigo_bip, name, ipr_nature, created_at, updated_at)
            VALUES (:code, 'Test IPR SISREC', 'PROYECTO', NOW(), NOW())
            RETURNING id
        """),
        {"code": code},
    )).mappings().first()
    await db.commit()
    return str(row["id"])


async def _get_state_id(db, code: str) -> str:
    r = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = :code"),
        {"code": code},
    )
    return str(r.scalar())


async def _create_rendicion(client, token, db, amount=None) -> str:
    """Create a rendicion in PENDIENTE and return its ID."""
    ipr_id = await _ensure_ipr(db)
    payload = {"ipr_id": ipr_id}
    if amount is not None:
        payload["amount"] = amount
    resp = await client.post("/api/dgi/data/rendiciones", json=payload, headers=auth(token))
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def _transition(client, token, rendicion_id: str, target_code: str, db, comment=None) -> int:
    """PATCH a rendicion to a target state code. Returns status code."""
    state_id = await _get_state_id(db, target_code)
    payload = {"state_id": state_id}
    if comment:
        payload["comment"] = comment
    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rendicion_id}",
        json=payload,
        headers=auth(token),
    )
    return resp.status_code


# ---------------------------------------------------------------------------
# State Machine: valid transitions
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pendiente_to_en_revision_rtf(client, dgi_token, db):
    """PENDIENTE → EN_REVISION_RTF: valid."""
    rid = await _create_rendicion(client, dgi_token, db)
    status = await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    assert status == 200


@pytest.mark.asyncio
async def test_en_revision_rtf_to_visada_rtf(client, dgi_token, db):
    """EN_REVISION_RTF → VISADA_RTF: DGI visa."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    status = await _transition(client, dgi_token, rid, "VISADA_RTF", db)
    assert status == 200


@pytest.mark.asyncio
async def test_visada_rtf_to_en_revision_ucr(client, dgi_token, db):
    """VISADA_RTF → EN_REVISION_UCR: send to UCR."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _transition(client, dgi_token, rid, "VISADA_RTF", db)
    status = await _transition(client, dgi_token, rid, "EN_REVISION_UCR", db)
    assert status == 200


@pytest.mark.asyncio
async def test_en_revision_ucr_to_aprobada(client, dgi_token, db):
    """Full happy path: PENDIENTE → ... → APROBADA."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _transition(client, dgi_token, rid, "VISADA_RTF", db)
    await _transition(client, dgi_token, rid, "EN_REVISION_UCR", db)
    status = await _transition(client, dgi_token, rid, "APROBADA", db)
    assert status == 200


@pytest.mark.asyncio
async def test_en_revision_ucr_to_rechazada(client, dgi_token, db):
    """EN_REVISION_UCR → RECHAZADA: terminal state."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _transition(client, dgi_token, rid, "VISADA_RTF", db)
    await _transition(client, dgi_token, rid, "EN_REVISION_UCR", db)
    status = await _transition(client, dgi_token, rid, "RECHAZADA", db)
    assert status == 200


@pytest.mark.asyncio
async def test_observation_loop(client, dgi_token, regional_token, db):
    """EN_REVISION_RTF → OBSERVADA → EN_REVISION_RTF: observation loop."""
    rid = await _create_rendicion(client, regional_token, db)
    await _transition(client, regional_token, rid, "EN_REVISION_RTF", db)
    # DGI observa
    status = await _transition(client, dgi_token, rid, "OBSERVADA", db)
    assert status == 200
    # Operativa reenvía
    status = await _transition(client, regional_token, rid, "EN_REVISION_RTF", db)
    assert status == 200


@pytest.mark.asyncio
async def test_ucr_observation_loop(client, dgi_token, regional_token, db):
    """EN_REVISION_UCR → OBSERVADA → EN_REVISION_RTF: UCR observation loop."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _transition(client, dgi_token, rid, "VISADA_RTF", db)
    await _transition(client, dgi_token, rid, "EN_REVISION_UCR", db)
    # UCR observa
    status = await _transition(client, dgi_token, rid, "OBSERVADA", db)
    assert status == 200
    # Reenvío a RTF
    status = await _transition(client, regional_token, rid, "EN_REVISION_RTF", db)
    assert status == 200


@pytest.mark.asyncio
async def test_invalid_transition_aprobada_terminal(client, dgi_token, db):
    """APROBADA is terminal — cannot transition further."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _transition(client, dgi_token, rid, "VISADA_RTF", db)
    await _transition(client, dgi_token, rid, "EN_REVISION_UCR", db)
    await _transition(client, dgi_token, rid, "APROBADA", db)
    # Try to go from APROBADA → EN_REVISION_RTF
    status = await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    assert status == 409


# ---------------------------------------------------------------------------
# Role restrictions
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_operativa_can_initiate_revision(client, regional_token, db):
    """Operativa (ADMIN_REGIONAL) can initiate PENDIENTE → EN_REVISION_RTF."""
    rid = await _create_rendicion(client, regional_token, db)
    status = await _transition(client, regional_token, rid, "EN_REVISION_RTF", db)
    assert status == 200


@pytest.mark.asyncio
async def test_operativa_cannot_visa_rtf(client, regional_token, dgi_token, db):
    """Operativa cannot execute EN_REVISION_RTF → VISADA_RTF (DGI only)."""
    rid = await _create_rendicion(client, regional_token, db)
    await _transition(client, regional_token, rid, "EN_REVISION_RTF", db)
    # Operativa tries to visa
    status = await _transition(client, regional_token, rid, "VISADA_RTF", db)
    assert status == 403


@pytest.mark.asyncio
async def test_operativa_cannot_approve(client, regional_token, dgi_token, db):
    """Operativa cannot approve at UCR level."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _transition(client, dgi_token, rid, "VISADA_RTF", db)
    await _transition(client, dgi_token, rid, "EN_REVISION_UCR", db)
    # Operativa tries to approve
    status = await _transition(client, regional_token, rid, "APROBADA", db)
    assert status == 403


@pytest.mark.asyncio
async def test_encargado_can_resubmit_observed(client, encargado_token, dgi_token, db):
    """ENCARGADO can re-submit OBSERVADA → EN_REVISION_RTF."""
    rid = await _create_rendicion(client, encargado_token, db)
    await _transition(client, encargado_token, rid, "EN_REVISION_RTF", db)
    await _transition(client, dgi_token, rid, "OBSERVADA", db)
    # Encargado reenvía
    status = await _transition(client, encargado_token, rid, "EN_REVISION_RTF", db)
    assert status == 200


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_history_entry_created(client, dgi_token, db):
    """Transitioning creates a history entry via trigger."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    # Fetch detail with history
    resp = await client.get(f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token))
    assert resp.status_code == 200
    detail = resp.json()
    assert len(detail["history"]) >= 1
    entry = detail["history"][0]
    assert entry["new_state"] == "EN_REVISION_RTF"
    assert entry["previous_state"] == "PENDIENTE"


@pytest.mark.asyncio
async def test_history_comment_stored(client, dgi_token, db):
    """Comment is stored in the most recent history entry."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db, comment="Revisión urgente")
    resp = await client.get(f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token))
    detail = resp.json()
    entry = detail["history"][0]
    assert entry["comment"] == "Revisión urgente"


# ---------------------------------------------------------------------------
# SLA
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sla_overdue_flag(client, dgi_token, db):
    """A rendicion in EN_REVISION_RTF for >7 days should be overdue (via detail endpoint)."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _age_rendicion(db, rid, "8 days")
    # Now check via API
    resp = await client.get(f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token))
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["days_in_state"] is not None
    assert detail["days_in_state"] > 7, f"days_in_state = {detail['days_in_state']}"
    assert detail["is_overdue"] is True


@pytest.mark.asyncio
async def test_vencidas_endpoint(client, dgi_token, db):
    """GET /rendiciones/vencidas returns overdue renditions."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _age_rendicion(db, rid, "10 days")
    # Use max page_size to avoid stale renditions from prior runs pushing ours off page 1
    resp = await client.get("/api/dgi/data/rendiciones/vencidas?page_size=100", headers=auth(dgi_token))
    assert resp.status_code == 200
    items = resp.json()["items"]
    ids = [i["id"] for i in items]
    assert rid in ids


# ---------------------------------------------------------------------------
# Amount + Art. 18
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_amount_on_create(client, dgi_token, db):
    """Amount field persists on create and appears in detail."""
    rid = await _create_rendicion(client, dgi_token, db, amount=5000000.50)
    resp = await client.get(f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token))
    assert resp.status_code == 200
    assert resp.json()["amount"] == 5000000.50


@pytest.mark.asyncio
async def test_amount_update_via_patch(client, dgi_token, db):
    """PATCH with amount updates the rendicion."""
    rid = await _create_rendicion(client, dgi_token, db)
    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}",
        json={"amount": 1234567.89},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    detail_resp = await client.get(f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token))
    assert detail_resp.json()["amount"] == 1234567.89


# ---------------------------------------------------------------------------
# SLA extended (4 reviewable states) + Ciclo endpoint
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sla_days_in_detail(client, dgi_token, db):
    """Detail response includes sla_days for current state."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    resp = await client.get(f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token))
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["sla_days"] == 7  # EN_REVISION_RTF SLA


@pytest.mark.asyncio
async def test_visada_rtf_overdue(client, dgi_token, db):
    """VISADA_RTF with >1 day is overdue (new SLA state)."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _transition(client, dgi_token, rid, "VISADA_RTF", db)
    await _age_rendicion(db, rid, "2 days")
    resp = await client.get(f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token))
    assert resp.status_code == 200
    detail = resp.json()
    assert detail["sla_days"] == 1
    assert detail["is_overdue"] is True


@pytest.mark.asyncio
async def test_observada_overdue(client, dgi_token, regional_token, db):
    """OBSERVADA with >15 days is overdue (new SLA state)."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _transition(client, dgi_token, rid, "OBSERVADA", db)
    await _age_rendicion(db, rid, "16 days")
    resp = await client.get(f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token))
    assert resp.status_code == 200
    assert resp.json()["is_overdue"] is True
    assert resp.json()["sla_days"] == 15


@pytest.mark.asyncio
async def test_vencidas_includes_visada_rtf(client, dgi_token, db):
    """Vencidas endpoint now captures VISADA_RTF overdue renditions."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _transition(client, dgi_token, rid, "VISADA_RTF", db)
    await _age_rendicion(db, rid, "3 days")
    resp = await client.get("/api/dgi/data/rendiciones/vencidas?page_size=100", headers=auth(dgi_token))
    assert resp.status_code == 200
    ids = [i["id"] for i in resp.json()["items"]]
    assert rid in ids


@pytest.mark.asyncio
async def test_ciclo_endpoint(client, dgi_token, db):
    """Ciclo endpoint returns phase timeline with SLA info."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _transition(client, dgi_token, rid, "VISADA_RTF", db)
    resp = await client.get(f"/api/dgi/data/rendiciones/{rid}/ciclo", headers=auth(dgi_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_state"] == "VISADA_RTF"
    assert len(data["phases"]) == 3  # PENDIENTE, EN_REVISION_RTF, VISADA_RTF
    # Check phase structure
    pendiente = data["phases"][0]
    assert pendiente["phase_code"] == "PENDIENTE"
    assert pendiente["exited_at"] is not None
    assert pendiente["sla_days"] is None  # PENDIENTE has no SLA
    rtf = data["phases"][1]
    assert rtf["phase_code"] == "EN_REVISION_RTF"
    assert rtf["sla_days"] == 7
    visada = data["phases"][2]
    assert visada["phase_code"] == "VISADA_RTF"
    assert visada["sla_days"] == 1
    assert visada["exited_at"] is None  # current phase


# ---------------------------------------------------------------------------
# Wave 2: Phase tracking + responsible assignment + cycle target
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_phase_entered_at_set_on_transition(client, dgi_token, db):
    """phase_entered_at is set on creation and updated on each transition."""
    rid = await _create_rendicion(client, dgi_token, db)
    resp = await client.get(f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token))
    detail = resp.json()
    assert detail["phase_entered_at"] is not None
    first_ts = detail["phase_entered_at"]
    # Transition to EN_REVISION_RTF
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    resp2 = await client.get(f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token))
    detail2 = resp2.json()
    assert detail2["phase_entered_at"] is not None
    assert detail2["phase_entered_at"] >= first_ts


@pytest.mark.asyncio
async def test_responsible_id_assignment(client, dgi_token, db):
    """Assigning responsible_id via PATCH persists and appears in detail."""
    rid = await _create_rendicion(client, dgi_token, db)
    # Get a valid user ID (the DGI user)
    user_row = (await db.execute(
        text('SELECT id FROM core."user" WHERE email = :email'),
        {"email": "jefe.dgi@goreos.cl"},
    )).mappings().first()
    user_id = str(user_row["id"])
    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}",
        json={"responsible_id": user_id},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    detail_resp = await client.get(f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token))
    detail = detail_resp.json()
    assert detail["responsible_id"] == user_id
    assert detail["responsible_name"] is not None


@pytest.mark.asyncio
async def test_phase_entered_at_not_reset_by_amount_update(client, dgi_token, db):
    """Updating amount does NOT reset phase_entered_at (only state transitions do)."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    # Age phase_entered_at
    await _age_rendicion(db, rid, "5 days")
    # Update amount (non-state field)
    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}",
        json={"amount": 999999.99},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    # days_in_state should still reflect the aged phase_entered_at, not NOW()
    detail_resp = await client.get(f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token))
    detail = detail_resp.json()
    assert detail["days_in_state"] > 4, f"days_in_state = {detail['days_in_state']} (should be ~5)"


@pytest.mark.asyncio
async def test_cycle_overdue_flag(client, dgi_token, db):
    """total_cycle_days and cycle_overdue track CGR 14-day institutional target."""
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    # Age created_at to exceed 14-day cycle target
    await db.execute(
        text("UPDATE core.rendition SET created_at = NOW() - INTERVAL '15 days' WHERE id = :id"),
        {"id": rid},
    )
    await db.commit()
    resp = await client.get(f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token))
    detail = resp.json()
    assert detail["total_cycle_days"] > 14
    assert detail["cycle_overdue"] is True
