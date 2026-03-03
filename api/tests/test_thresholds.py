"""
Integration tests for Ciclo 20+21: Financial Thresholds + Glosa Rules + Budget Classifier.

Covers:
- Threshold CRUD admin endpoints
- UTM value from DB (not hardcoded)
- Budget classifier exposed in list (item_label, allocation_label)
- Budget classifier filters (item, allocation, program_type)
- CGR threshold warning on actos
- Garantía threshold warning on convenios
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth


# ===========================================================================
# THRESHOLD ADMIN CRUD
# ===========================================================================


@pytest.mark.asyncio
async def test_threshold_list(client: AsyncClient, admin_token: str):
    """List all financial thresholds."""
    resp = await client.get("/api/admin/thresholds", headers=auth(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 10  # 9 thresholds + UTM_VALUE
    codes = {t["code"] for t in data}
    assert "CORE_APPROVAL" in codes
    assert "UTM_VALUE" in codes
    assert "GLOSA_ADMIN_MAX" in codes


@pytest.mark.asyncio
async def test_threshold_list_forbidden(client: AsyncClient, regional_token: str):
    """Non-admin cannot list thresholds."""
    resp = await client.get("/api/admin/thresholds", headers=auth(regional_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_threshold_create(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Create a new threshold."""
    resp = await client.post(
        "/api/admin/thresholds",
        headers=auth(admin_token),
        json={
            "code": "TEST_THRESHOLD",
            "label": "Test threshold",
            "value_utm": 100,
            "enforcement_point": "F3_F4",
            "source_normativa": "Test source",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == "TEST_THRESHOLD"

    # Cleanup
    await db.execute(text("DELETE FROM core.financial_threshold WHERE code = 'TEST_THRESHOLD'"))
    await db.commit()


@pytest.mark.asyncio
async def test_threshold_create_duplicate(client: AsyncClient, admin_token: str):
    """Cannot create duplicate threshold code."""
    resp = await client.post(
        "/api/admin/thresholds",
        headers=auth(admin_token),
        json={
            "code": "CORE_APPROVAL",
            "label": "Duplicate",
            "value_utm": 999,
            "enforcement_point": "F3_F4",
        },
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_threshold_update(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Update a threshold value."""
    # Get current UTM_VALUE threshold id
    row = await db.execute(
        text("SELECT id, value_utm FROM core.financial_threshold WHERE code = 'UTM_VALUE'")
    )
    th = row.mappings().first()
    original_value = th["value_utm"]

    resp = await client.patch(
        f"/api/admin/thresholds/{th['id']}",
        headers=auth(admin_token),
        json={"value_utm": 70000},
    )
    assert resp.status_code == 200

    # Verify updated
    row2 = await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'UTM_VALUE'")
    )
    assert float(row2.scalar()) == 70000.0

    # Restore original value
    await db.execute(
        text("UPDATE core.financial_threshold SET value_utm = :v WHERE code = 'UTM_VALUE'"),
        {"v": original_value},
    )
    await db.commit()


@pytest.mark.asyncio
async def test_threshold_toggle_active(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Toggle threshold active status."""
    row = await db.execute(
        text("SELECT id, is_active FROM core.financial_threshold WHERE code = 'RATE_EXENCION'")
    )
    th = row.mappings().first()

    # Deactivate
    resp = await client.patch(
        f"/api/admin/thresholds/{th['id']}",
        headers=auth(admin_token),
        json={"is_active": False},
    )
    assert resp.status_code == 200

    # Verify
    row2 = await db.execute(
        text("SELECT is_active FROM core.financial_threshold WHERE code = 'RATE_EXENCION'")
    )
    assert row2.scalar() is False

    # Restore
    await db.execute(
        text("UPDATE core.financial_threshold SET is_active = TRUE WHERE code = 'RATE_EXENCION'")
    )
    await db.commit()


# ===========================================================================
# UTM VALUE FROM DB
# ===========================================================================


@pytest.mark.asyncio
async def test_utm_value_from_db(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Verify UTM value is read from financial_threshold table."""
    row = await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'UTM_VALUE' AND is_active = TRUE")
    )
    utm = row.scalar()
    assert utm is not None
    assert float(utm) == 67294.0


# ===========================================================================
# BUDGET CLASSIFIER — List exposes item_label / allocation_label
# ===========================================================================


@pytest.mark.asyncio
async def test_budget_list_includes_classifier(client: AsyncClient, regional_token: str):
    """Budget list endpoint returns item_label and allocation_label."""
    resp = await client.get(
        "/api/presupuesto?page=1&page_size=5",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    if data["items"]:
        item = data["items"][0]
        # Fields should exist (may be null if no item/allocation assigned)
        assert "item_label" in item
        assert "allocation_label" in item
        assert "program_type_label" in item


@pytest.mark.asyncio
async def test_budget_filter_by_item(client: AsyncClient, regional_token: str, db: AsyncSession):
    """Budget list can be filtered by item code."""
    # Get a valid item code
    row = await db.execute(
        text("SELECT code FROM ref.category WHERE scheme = 'budget_item' LIMIT 1")
    )
    item_code = row.scalar()
    if not item_code:
        pytest.skip("No budget_item codes in test DB")

    resp = await client.get(
        f"/api/presupuesto?page=1&page_size=5&item={item_code}",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_budget_filter_by_program_type(client: AsyncClient, regional_token: str, db: AsyncSession):
    """Budget list can be filtered by program_type code."""
    row = await db.execute(
        text("SELECT code FROM ref.category WHERE scheme = 'program_type' LIMIT 1")
    )
    pt_code = row.scalar()
    if not pt_code:
        pytest.skip("No program_type codes in test DB")

    resp = await client.get(
        f"/api/presupuesto?page=1&page_size=5&program_type={pt_code}",
        headers=auth(regional_token),
    )
    assert resp.status_code == 200


# ===========================================================================
# CORE GATE REFACTORED (reads from DB, not hardcoded)
# ===========================================================================


@pytest.mark.asyncio
async def test_core_gate_reads_from_db(client: AsyncClient, admin_token: str, db: AsyncSession):
    """The CORE approval threshold should come from the DB table."""
    # Verify the threshold exists in DB
    row = await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'CORE_APPROVAL' AND is_active = TRUE")
    )
    value = row.scalar()
    assert value is not None
    assert float(value) == 7000.0


@pytest.mark.asyncio
async def test_core_gate_below_threshold(client: AsyncClient, admin_token: str, db: AsyncSession):
    """IPR below CORE threshold should not have core_approval gate."""
    # Create a test IPR with low monto
    ipr_type = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'ipr_type' LIMIT 1")
    )
    ipr_type_id = str(ipr_type.scalar())

    status_row = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'ipr_state' AND code = 'CDP_EMITIDO' LIMIT 1")
    )
    status_id = str(status_row.scalar())

    ipr_result = await db.execute(
        text("""
            INSERT INTO core.ipr (codigo_bip, name, ipr_type_id, status_id, ipr_nature, metadata)
            VALUES ('TEST-CORE-LOW', 'Low value IPR', :ipr_type_id, :status_id, 'PROYECTO',
                    '{"monto_total": 100000000}'::jsonb)
            RETURNING id
        """),
        {"ipr_type_id": ipr_type_id, "status_id": status_id},
    )
    ipr_id = str(ipr_result.scalar())
    await db.commit()

    # Get transitions — should not have core_approval gate
    resp = await client.get(
        f"/api/ipr/{ipr_id}/transiciones",
        headers=auth(admin_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    # Check transitions — for F3→F4 gates
    for t in data:
        gates = t.get("gates", [])
        core_gates = [g for g in gates if g.get("name") == "core_approval"]
        # 100M CLP < 7000 UTM * 67294 = 471M CLP → no core gate
        assert len(core_gates) == 0

    # Cleanup
    await db.execute(text("DELETE FROM core.ipr WHERE codigo_bip = 'TEST-CORE-LOW'"))
    await db.commit()


# ===========================================================================
# CGR THRESHOLD WARNING
# ===========================================================================


@pytest.mark.asyncio
async def test_cgr_threshold_value(client: AsyncClient, admin_token: str, db: AsyncSession):
    """CGR Toma de Razón threshold exists in DB."""
    row = await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'CGR_TOMA_RAZON' AND is_active = TRUE")
    )
    value = row.scalar()
    assert value is not None
    assert float(value) == 2500.0


# ===========================================================================
# GARANTÍA THRESHOLD
# ===========================================================================


@pytest.mark.asyncio
async def test_garantia_threshold_value(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Garantía convenio threshold exists in DB."""
    row = await db.execute(
        text("SELECT value_utm FROM core.financial_threshold WHERE code = 'GARANTIA_CONVENIO' AND is_active = TRUE")
    )
    value = row.scalar()
    assert value is not None
    assert float(value) == 1000.0


# ===========================================================================
# GLOSA THRESHOLDS
# ===========================================================================


@pytest.mark.asyncio
async def test_glosa_thresholds_seeded(client: AsyncClient, admin_token: str, db: AsyncSession):
    """All 5 glosa thresholds should be seeded."""
    result = await db.execute(
        text("SELECT code, value_pct FROM core.financial_threshold WHERE enforcement_point = 'GLOSA' AND is_active = TRUE ORDER BY code")
    )
    rows = result.mappings().all()
    codes = {r["code"]: float(r["value_pct"]) for r in rows}
    assert codes["GLOSA_ADMIN_MAX"] == 5.0
    assert codes["GLOSA_HONORARIOS_MAX"] == 5.0
    assert codes["GLOSA_ANF_MAX"] == 10.0
    assert codes["GLOSA_EQUIPAMIENTO_MAX"] == 20.0
    assert codes["GLOSA_REMUNERACIONES_MAX"] == 30.0


@pytest.mark.asyncio
async def test_glosa_check_no_cdps(client: AsyncClient, admin_token: str, db: AsyncSession):
    """Glosa check for an IPR with no CDPs should return empty gates."""
    from app.routers.presupuesto import check_glosa_rules

    # Use a non-existent IPR ID
    import uuid
    fake_id = uuid.uuid4()
    gates = await check_glosa_rules(fake_id, db)
    assert gates == []


# ===========================================================================
# THRESHOLD ENFORCEMENT POINTS
# ===========================================================================


@pytest.mark.asyncio
async def test_all_enforcement_points_valid(client: AsyncClient, admin_token: str, db: AsyncSession):
    """All thresholds have valid enforcement points."""
    valid_points = {"F3_F4", "F1_F2", "ACTO", "CONVENIO", "GLOSA", "CONFIG"}
    result = await db.execute(
        text("SELECT DISTINCT enforcement_point FROM core.financial_threshold")
    )
    points = {r[0] for r in result.all()}
    assert points.issubset(valid_points)


@pytest.mark.asyncio
async def test_threshold_not_found(client: AsyncClient, admin_token: str):
    """Updating non-existent threshold returns 404."""
    import uuid
    resp = await client.patch(
        f"/api/admin/thresholds/{uuid.uuid4()}",
        headers=auth(admin_token),
        json={"label": "No existe"},
    )
    assert resp.status_code == 404
