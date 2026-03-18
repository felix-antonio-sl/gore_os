"""Tests for agreement lifecycle and installments."""
import uuid
import pytest
from datetime import date, timedelta
from sqlalchemy import text
from tests.conftest import auth


async def _create_agreement(client, token, catalog, **overrides):
    payload = {
        "agreement_type_id": catalog["agreement_type_id"],
        "state_id": catalog["agreement_state_borrador_id"],
        "total_amount": 50000000,
        "valid_from": str(date.today()),
        "valid_to": str(date.today() + timedelta(days=365)),
        **overrides,
    }
    resp = await client.post("/api/convenios", json=payload, headers=auth(token))
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_create_agreement(client, regional_token, catalog):
    """Create agreement with auto-generated number."""
    data = await _create_agreement(client, regional_token, catalog)
    assert "id" in data
    assert data.get("agreement_number", "").startswith("AGR-")


async def test_patch_state(client, regional_token, catalog):
    """Update agreement state BORRADOR → EN_NEGOCIACION (valid transition)."""
    data = await _create_agreement(client, regional_token, catalog)
    resp = await client.patch(
        f"/api/convenios/{data['id']}",
        json={"state_id": catalog["agreement_state_en_negociacion_id"]},
        headers=auth(regional_token),
    )
    assert resp.status_code == 200


async def test_add_installment(client, regional_token, catalog):
    """Add installment to agreement."""
    data = await _create_agreement(client, regional_token, catalog)
    resp = await client.post(
        f"/api/convenios/{data['id']}/cuotas",
        json={
            "installment_number": 1,
            "amount": 10000000,
            "due_date": str(date.today() + timedelta(days=90)),
            "payment_status_id": catalog["payment_status_pendiente_id"],
        },
        headers=auth(regional_token),
    )
    assert resp.status_code == 201


async def test_duplicate_installment_number(client, regional_token, catalog):
    """Duplicate installment_number on same agreement returns error."""
    data = await _create_agreement(client, regional_token, catalog)
    cuota = {
        "installment_number": 1,
        "amount": 10000000,
        "due_date": str(date.today() + timedelta(days=90)),
        "payment_status_id": catalog["payment_status_pendiente_id"],
    }
    await client.post(f"/api/convenios/{data['id']}/cuotas", json=cuota, headers=auth(regional_token))

    resp = await client.post(
        f"/api/convenios/{data['id']}/cuotas",
        json=cuota,
        headers=auth(regional_token),
    )
    # Should fail with 409 or 500 (unique constraint)
    assert resp.status_code in (409, 500)


async def test_days_to_expiry_vigente(client, regional_token, catalog):
    """VIGENTE agreement with future valid_to shows positive days."""
    data = await _create_agreement(
        client, regional_token, catalog,
        state_id=catalog["agreement_state_vigente_id"],
        valid_to=str(date.today() + timedelta(days=60)),
    )
    detail = await client.get(f"/api/convenios/{data['id']}", headers=auth(regional_token))
    body = detail.json()
    assert body["days_to_expiry"] is not None
    assert body["days_to_expiry"] > 0


async def test_days_to_expiry_borrador_null(client, regional_token, catalog):
    """BORRADOR agreement has no days_to_expiry (null)."""
    data = await _create_agreement(client, regional_token, catalog)
    detail = await client.get(f"/api/convenios/{data['id']}", headers=auth(regional_token))
    assert detail.json()["days_to_expiry"] is None


async def test_list_paginated(client, regional_token):
    """Agreement list returns paginated response."""
    resp = await client.get("/api/convenios", headers=auth(regional_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "total" in body


async def _create_test_ipr(db) -> str:
    """Insert a minimal test IPR and return its id."""
    code = f"T-{uuid.uuid4().hex[:12].upper()}"
    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (codigo_bip, name, ipr_nature, created_at, updated_at)
            VALUES (:code, 'Test IPR Art 18', 'PROYECTO', NOW(), NOW())
            RETURNING id
        """),
        {"code": code},
    )).mappings().first()
    await db.commit()
    return str(row["id"])


async def test_bulk_cuotas(client, regional_token, catalog):
    """Bulk generate 6 monthly installments."""
    data = await _create_agreement(client, regional_token, catalog)
    resp = await client.post(
        f"/api/convenios/{data['id']}/cuotas/bulk",
        json={
            "total_amount": 12000000,
            "num_installments": 6,
            "start_date": str(date.today()),
            "frequency_months": 1,
        },
        headers=auth(regional_token),
    )
    assert resp.status_code == 201, resp.text
    cuotas = resp.json()
    assert len(cuotas) == 6
    # First cuota gets remainder: 12000000 // 6 = 2000000, remainder = 0
    assert cuotas[0]["amount"] == 2000000
    # All cuotas have sequential numbers
    numbers = [c["installment_number"] for c in cuotas]
    assert numbers == [1, 2, 3, 4, 5, 6]


async def test_bulk_cuotas_after_existing(client, regional_token, catalog):
    """Bulk cuotas auto-increment from existing installment numbers."""
    data = await _create_agreement(client, regional_token, catalog)
    # Create one cuota first
    await client.post(
        f"/api/convenios/{data['id']}/cuotas",
        json={
            "installment_number": 1,
            "amount": 5000000,
            "due_date": str(date.today() + timedelta(days=30)),
            "payment_status_id": catalog["payment_status_pendiente_id"],
        },
        headers=auth(regional_token),
    )
    # Bulk create 3 more
    resp = await client.post(
        f"/api/convenios/{data['id']}/cuotas/bulk",
        json={
            "total_amount": 9000000,
            "num_installments": 3,
            "start_date": str(date.today() + timedelta(days=60)),
            "frequency_months": 1,
        },
        headers=auth(regional_token),
    )
    assert resp.status_code == 201
    cuotas = resp.json()
    assert len(cuotas) == 3
    assert cuotas[0]["installment_number"] == 2  # starts after existing #1


async def test_add_cuota_blocked_by_pending_rendition(client, regional_token, catalog, db):
    """Art. 18 CGR: POST cuotas blocked when agreement has pending renditions."""
    ipr_id = await _create_test_ipr(db)

    # Create agreement linked to this IPR
    data = await _create_agreement(client, regional_token, catalog, ipr_id=ipr_id)
    agreement_id = data["id"]

    # Get the PENDIENTE rendition state id
    pending_state = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'PENDIENTE'")
    )).scalar()
    assert pending_state, "rendition_state PENDIENTE not found"

    renderer_id = (await db.execute(
        text("SELECT id FROM core.organization WHERE deleted_at IS NULL LIMIT 1")
    )).scalar()

    # Insert a PENDIENTE rendition linked to the agreement + IPR
    await db.execute(
        text("""
            INSERT INTO core.rendition (agreement_id, renderer_id, ipr_id, state_id, created_at, updated_at)
            VALUES (:agreement_id, :renderer_id, :ipr_id, :state_id, NOW(), NOW())
        """),
        {"agreement_id": agreement_id, "renderer_id": str(renderer_id), "ipr_id": ipr_id, "state_id": str(pending_state)},
    )
    await db.commit()

    # POST cuota should be blocked
    resp = await client.post(
        f"/api/convenios/{agreement_id}/cuotas",
        json={
            "installment_number": 1,
            "amount": 5000000,
            "due_date": str(date.today() + timedelta(days=90)),
            "payment_status_id": catalog["payment_status_pendiente_id"],
        },
        headers=auth(regional_token),
    )
    assert resp.status_code == 409
    assert "Art. 18" in resp.json()["detail"]


async def test_art18_error_includes_rendition_detail(client, regional_token, catalog, db):
    """Art. 18 CGR: error 409 includes rendition code and status in detail message."""
    ipr_id = await _create_test_ipr(db)
    data = await _create_agreement(client, regional_token, catalog, ipr_id=ipr_id)
    agreement_id = data["id"]

    pending_state = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'PENDIENTE'")
    )).scalar()
    assert pending_state

    # Insert a rendition — rendition table has no code column, uses agreement_id FK
    # Must also provide renderer_id (NOT NULL)
    renderer_id = (await db.execute(
        text("SELECT id FROM core.organization WHERE deleted_at IS NULL LIMIT 1")
    )).scalar()
    assert renderer_id, "No organization found for renderer_id"

    await db.execute(
        text("""
            INSERT INTO core.rendition (agreement_id, renderer_id, ipr_id, state_id, amount, created_at, updated_at)
            VALUES (:agreement_id, :renderer_id, :ipr_id, :state_id, 5000000, NOW(), NOW())
        """),
        {"agreement_id": agreement_id, "renderer_id": str(renderer_id), "ipr_id": ipr_id, "state_id": str(pending_state)},
    )
    await db.commit()

    resp = await client.post(
        f"/api/convenios/{agreement_id}/cuotas",
        json={
            "installment_number": 1,
            "amount": 5000000,
            "due_date": str(date.today() + timedelta(days=90)),
            "payment_status_id": catalog["payment_status_pendiente_id"],
        },
        headers=auth(regional_token),
    )
    assert resp.status_code == 409
    detail_msg = resp.json()["detail"]
    assert "Art. 18" in detail_msg
    # Should contain truncated rendition ID and status label
    assert "Pendiente" in detail_msg or "pendiente" in detail_msg.lower()


async def test_add_cuota_allowed_when_renditions_approved(client, regional_token, catalog, db):
    """POST cuotas succeeds when all renditions are APROBADA."""
    ipr_id = await _create_test_ipr(db)

    # Create agreement linked to this IPR
    data = await _create_agreement(client, regional_token, catalog, ipr_id=ipr_id)
    agreement_id = data["id"]

    # Get the APROBADA rendition state id
    approved_state = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'APROBADA'")
    )).scalar()
    assert approved_state, "rendition_state APROBADA not found"

    renderer_id = (await db.execute(
        text("SELECT id FROM core.organization WHERE deleted_at IS NULL LIMIT 1")
    )).scalar()

    # Insert an APROBADA rendition linked to the agreement + IPR
    await db.execute(
        text("""
            INSERT INTO core.rendition (agreement_id, renderer_id, ipr_id, state_id, created_at, updated_at)
            VALUES (:agreement_id, :renderer_id, :ipr_id, :state_id, NOW(), NOW())
        """),
        {"agreement_id": agreement_id, "renderer_id": str(renderer_id), "ipr_id": ipr_id, "state_id": str(approved_state)},
    )
    await db.commit()

    # POST cuota should succeed
    resp = await client.post(
        f"/api/convenios/{agreement_id}/cuotas",
        json={
            "installment_number": 1,
            "amount": 5000000,
            "due_date": str(date.today() + timedelta(days=90)),
            "payment_status_id": catalog["payment_status_pendiente_id"],
        },
        headers=auth(regional_token),
    )
    assert resp.status_code == 201


# ---------------------------------------------------------------------------
# Resumen endpoint
# ---------------------------------------------------------------------------


async def test_convenios_resumen(client, regional_token, catalog):
    """GET /api/convenios/resumen returns aggregate stats."""
    # Ensure at least one agreement exists
    await _create_agreement(client, regional_token, catalog)
    resp = await client.get("/api/convenios/resumen", headers=auth(regional_token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert "by_state" in body
    assert isinstance(body["by_state"], list)
    assert "expiring_30d" in body
    assert "expiring_90d" in body
    assert "without_ipr" in body


async def test_convenios_resumen_expiring(client, regional_token, catalog):
    """Resumen counts expiring-in-30d agreements correctly."""
    # Create one VIGENTE agreement expiring in 15 days
    await _create_agreement(
        client, regional_token, catalog,
        state_id=catalog["agreement_state_vigente_id"],
        valid_to=str(date.today() + timedelta(days=15)),
    )
    resp = await client.get("/api/convenios/resumen", headers=auth(regional_token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["expiring_30d"] >= 1
    assert body["expiring_90d"] >= 1


# ---------------------------------------------------------------------------
# Detail includes renditions
# ---------------------------------------------------------------------------


async def test_detail_includes_renditions(client, regional_token, catalog, db):
    """GET /api/convenios/{id} includes renditions array."""
    ipr_id = await _create_test_ipr(db)
    data = await _create_agreement(client, regional_token, catalog, ipr_id=ipr_id)
    agreement_id = data["id"]

    # Insert a rendition
    pending_state = (await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' AND code = 'INGRESADA'")
    )).scalar()
    if not pending_state:
        pending_state = (await db.execute(
            text("SELECT id FROM ref.category WHERE scheme = 'rendition_state' LIMIT 1")
        )).scalar()
    renderer_id = (await db.execute(
        text("SELECT id FROM core.organization WHERE deleted_at IS NULL LIMIT 1")
    )).scalar()

    await db.execute(
        text("""
            INSERT INTO core.rendition (agreement_id, renderer_id, ipr_id, state_id, amount, created_at, updated_at)
            VALUES (:agreement_id, :renderer_id, :ipr_id, :state_id, 3000000, NOW(), NOW())
        """),
        {"agreement_id": agreement_id, "renderer_id": str(renderer_id), "ipr_id": ipr_id, "state_id": str(pending_state)},
    )
    await db.commit()

    resp = await client.get(f"/api/convenios/{agreement_id}", headers=auth(regional_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "renditions" in body
    assert len(body["renditions"]) >= 1
    rend = body["renditions"][0]
    assert "short_id" in rend
    assert "state" in rend
    assert "state_label" in rend
    assert float(rend["amount"]) == 3000000


async def test_detail_no_renditions_empty_array(client, regional_token, catalog):
    """Detail with no renditions returns empty array."""
    data = await _create_agreement(client, regional_token, catalog)
    resp = await client.get(f"/api/convenios/{data['id']}", headers=auth(regional_token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["renditions"] == []


# ---------------------------------------------------------------------------
# Payment SLA check
# ---------------------------------------------------------------------------


async def test_check_payment_slas(client, admin_token):
    """POST /api/convenios/check-payment-slas returns checked + alerts_created."""
    resp = await client.post("/api/convenios/check-payment-slas", headers=auth(admin_token))
    assert resp.status_code == 200
    body = resp.json()
    assert "checked" in body
    assert "alerts_created" in body
    assert body["checked"] >= 0
