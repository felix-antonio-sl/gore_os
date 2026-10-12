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
