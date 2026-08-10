"""Tests para SISREC 8-Phase CGR (TP-06 + HΩ-14).

Covers:
- TP-06 phase definitions endpoint (8 rows)
- Archive endpoint (phase 8)
- Escalation check + listing
- Enhanced ciclo with phase mapping
- Metadata external phase timestamps
"""
import uuid
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from tests.conftest import auth


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _ensure_ipr(db) -> str:
    r = await db.execute(text("SELECT id FROM core.ipr LIMIT 1"))
    row = r.scalar()
    if row:
        return str(row)
    code = f"T-8PH-{uuid.uuid4().hex[:8].upper()}"
    row = (await db.execute(
        text("""
            INSERT INTO core.ipr (codigo_bip, name, ipr_nature, created_at, updated_at)
            VALUES (:code, 'Test IPR 8Phase', 'PROYECTO', NOW(), NOW())
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


async def _create_rendicion(client, token, db, amount=None, metadata=None) -> str:
    ipr_id = await _ensure_ipr(db)
    payload = {"ipr_id": ipr_id}
    if amount is not None:
        payload["amount"] = amount
    resp = await client.post("/api/dgi/data/rendiciones", json=payload, headers=auth(token))
    assert resp.status_code == 201, resp.text
    rid = resp.json()["id"]
    if metadata:
        import json
        await db.execute(
            text("UPDATE core.rendition SET metadata = CAST(:m AS jsonb) WHERE id = :id"),
            {"m": json.dumps(metadata), "id": rid},
        )
        await db.commit()
    return rid


async def _transition(client, token, rid: str, target_code: str, db) -> int:
    state_id = await _get_state_id(db, target_code)
    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}",
        json={"state_id": state_id},
        headers=auth(token),
    )
    return resp.status_code


async def _age_rendicion(db, rid: str, interval: str) -> None:
    await db.execute(text("ALTER TABLE core.rendition DISABLE TRIGGER trg_rendition_updated_at"))
    try:
        await db.execute(
            text(f"UPDATE core.rendition SET updated_at = NOW() - INTERVAL '{interval}', "
                 f"phase_entered_at = NOW() - INTERVAL '{interval}' WHERE id = :id"),
            {"id": rid},
        )
    finally:
        await db.execute(text("ALTER TABLE core.rendition ENABLE TRIGGER trg_rendition_updated_at"))
    await db.commit()


async def _drive_to_aprobada(client, token, rid, db):
    await _transition(client, token, rid, "EN_REVISION_RTF", db)
    await _transition(client, token, rid, "VISADA_RTF", db)
    await _transition(client, token, rid, "EN_REVISION_UCR", db)
    status = await _transition(client, token, rid, "APROBADA", db)
    assert status == 200


# ---------------------------------------------------------------------------
# Test 1: GET /rendiciones/fases
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_phases_returns_8(client, dgi_token):
    resp = await client.get("/api/dgi/data/rendiciones/fases", headers=auth(dgi_token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 8
    assert data[0]["ordinal"] == 1
    assert data[0]["code"] == "PREPARACION_EJECUTOR"
    assert data[7]["ordinal"] == 8
    assert data[7]["code"] == "ARCHIVO_CIERRE"
    assert data[0]["is_internal"] is False
    assert data[4]["is_internal"] is True


# ---------------------------------------------------------------------------
# Tests 2-4: PATCH /rendiciones/{id}/archivar
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_archive_aprobada(client, dgi_token, db):
    rid = await _create_rendicion(client, dgi_token, db)
    await _drive_to_aprobada(client, dgi_token, rid, db)
    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}/archivar", headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    assert resp.json()["archived"] is True


@pytest.mark.asyncio
async def test_archive_non_aprobada_409(client, dgi_token, db):
    rid = await _create_rendicion(client, dgi_token, db)
    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}/archivar", headers=auth(dgi_token),
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_archive_twice_409(client, dgi_token, db):
    rid = await _create_rendicion(client, dgi_token, db)
    await _drive_to_aprobada(client, dgi_token, rid, db)
    resp1 = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}/archivar", headers=auth(dgi_token),
    )
    assert resp1.status_code == 200
    resp2 = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}/archivar", headers=auth(dgi_token),
    )
    assert resp2.status_code == 409


# ---------------------------------------------------------------------------
# Tests 5-7: Escalation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_check_escalations_creates_level1(client, dgi_token, db):
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _age_rendicion(db, rid, "8 days")
    resp = await client.post(
        "/api/dgi/data/rendiciones/check-escalations", headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["new_escalations"] >= 1


@pytest.mark.asyncio
async def test_check_escalations_idempotent(client, dgi_token, db):
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _age_rendicion(db, rid, "8 days")
    resp1 = await client.post(
        "/api/dgi/data/rendiciones/check-escalations", headers=auth(dgi_token),
    )
    n1 = resp1.json()["new_escalations"]
    assert n1 >= 1
    resp2 = await client.post(
        "/api/dgi/data/rendiciones/check-escalations", headers=auth(dgi_token),
    )
    n2 = resp2.json()["new_escalations"]
    # Second run should not re-create the same escalation for this rendicion
    assert n2 < n1


@pytest.mark.asyncio
async def test_open_escalation_uniqueness_is_enforced_by_db(client, dgi_token, db):
    """Direct SQL cannot create two open escalations for one rendition/phase/level."""
    rid = await _create_rendicion(client, dgi_token, db)
    phase_id = (await db.execute(text("""
        SELECT id FROM core.rendition_phase WHERE code = 'REVISION_RTF'
    """))).scalar_one()

    try:
        await db.execute(
            text("""
                INSERT INTO core.rendition_escalation
                    (rendition_id, phase_id, escalation_level)
                VALUES (:rid, :phase_id, 1)
            """),
            {"rid": rid, "phase_id": phase_id},
        )
        with pytest.raises(DBAPIError):
            await db.execute(
                text("""
                    INSERT INTO core.rendition_escalation
                        (rendition_id, phase_id, escalation_level)
                    VALUES (:rid, :phase_id, 1)
                """),
                {"rid": rid, "phase_id": phase_id},
            )
    finally:
        await db.rollback()


@pytest.mark.asyncio
async def test_list_escalations(client, dgi_token, db):
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    await _age_rendicion(db, rid, "8 days")
    await client.post(
        "/api/dgi/data/rendiciones/check-escalations", headers=auth(dgi_token),
    )
    resp = await client.get(
        f"/api/dgi/data/rendiciones/{rid}/escalamientos", headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["phase_code"] == "REVISION_RTF"
    assert data[0]["escalation_level"] == 1


# ---------------------------------------------------------------------------
# Tests 8-10: Enhanced ciclo
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ciclo_returns_8_phases(client, dgi_token, db):
    rid = await _create_rendicion(client, dgi_token, db)
    resp = await client.get(
        f"/api/dgi/data/rendiciones/{rid}/ciclo", headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["phases"]) == 8
    assert data["phases"][0]["code"] == "PREPARACION_EJECUTOR"
    assert data["phases"][7]["code"] == "ARCHIVO_CIERRE"


@pytest.mark.asyncio
async def test_ciclo_with_metadata_shows_external(client, dgi_token, db):
    rid = await _create_rendicion(client, dgi_token, db, metadata={
        "fase1_preparacion_at": "2026-01-15T10:00:00Z",
        "fase2_certificacion_at": "2026-01-20T10:00:00Z",
    })
    resp = await client.get(
        f"/api/dgi/data/rendiciones/{rid}/ciclo", headers=auth(dgi_token),
    )
    data = resp.json()
    assert data["phases"][0]["status"] == "completada"
    assert data["phases"][1]["status"] == "completada"
    assert data["phases"][2]["status"] == "no_aplica"


@pytest.mark.asyncio
async def test_ciclo_archived_shows_phase8(client, dgi_token, db):
    rid = await _create_rendicion(client, dgi_token, db)
    await _drive_to_aprobada(client, dgi_token, rid, db)
    await client.patch(
        f"/api/dgi/data/rendiciones/{rid}/archivar", headers=auth(dgi_token),
    )
    resp = await client.get(
        f"/api/dgi/data/rendiciones/{rid}/ciclo", headers=auth(dgi_token),
    )
    data = resp.json()
    assert data["phases"][7]["status"] == "completada"
    assert data["archived_at"] is not None


# ---------------------------------------------------------------------------
# Tests 11-12: Metadata + escalation level 2
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_patch_metadata_external_phases(client, dgi_token, db):
    rid = await _create_rendicion(client, dgi_token, db)
    resp = await client.patch(
        f"/api/dgi/data/rendiciones/{rid}",
        json={"metadata": {"fase1_preparacion_at": "2026-02-01T08:00:00Z"}},
        headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    detail = await client.get(
        f"/api/dgi/data/rendiciones/{rid}", headers=auth(dgi_token),
    )
    assert detail.json()["metadata"]["fase1_preparacion_at"] == "2026-02-01T08:00:00Z"


@pytest.mark.asyncio
async def test_escalation_level2_at_1_5x(client, dgi_token, db):
    rid = await _create_rendicion(client, dgi_token, db)
    await _transition(client, dgi_token, rid, "EN_REVISION_RTF", db)
    # EN_REVISION_RTF SLA = 7 days. Level 1 at 1.0x = 7d, Level 2 at 1.5x = 10.5d
    await _age_rendicion(db, rid, "11 days")
    resp = await client.post(
        "/api/dgi/data/rendiciones/check-escalations", headers=auth(dgi_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    # Filter details for this specific rendition
    levels = [d["level"] for d in data["details"] if d["rendition_id"] == rid]
    assert 1 in levels
    assert 2 in levels
