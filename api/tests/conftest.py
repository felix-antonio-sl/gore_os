"""
Shared fixtures for GORE_OS backend integration tests.

Strategy:
- Test DB: goreos_test (created by scripts/setup_test_db.sh)
- Auth: Real JWT tokens with real user IDs from seeded DB
- Session: Each test gets a fresh session, commits are real
- Run: docker compose exec api pytest -v
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from app.main import create_app
from app.core.database import get_db
from app.core.security import create_access_token


TEST_DB_URL = "postgresql+asyncpg://goreos:goreos_2026@goreos_db:5432/goreos_test"


# ---------------------------------------------------------------------------
# Engine & session (function-scoped to avoid event loop conflicts)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def db():
    """Fresh DB engine + session per test (avoids cross-loop issues)."""
    engine = create_async_engine(TEST_DB_URL, echo=False, pool_pre_ping=True)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def cleanup_test_artifacts(db: AsyncSession):
    """Remove persistent artifacts created by stateful integration tests."""
    # Clean escalation test data (before rendition-related cleanup to avoid FK issues)
    await db.execute(text("DELETE FROM core.rendition_escalation"))
    await db.execute(
        text("""
            DELETE FROM core.kinship_declaration
            WHERE ipr_id IN (
                SELECT id FROM core.ipr WHERE codigo_bip LIKE 'KIN-%'
            )
        """)
    )
    await db.execute(text("DELETE FROM core.ipr WHERE codigo_bip LIKE 'KIN-%'"))
    await db.execute(
        text("""
            DELETE FROM core.ipr_territory
            WHERE ipr_id IN (
                SELECT id FROM core.ipr WHERE codigo_bip LIKE 'TRULE-%'
            )
        """)
    )
    await db.execute(
        text("""
            DELETE FROM core.evaluation_assignment
            WHERE ipr_id IN (
                SELECT id FROM core.ipr WHERE codigo_bip LIKE 'TRULE-%'
            )
        """)
    )
    await db.execute(text("DELETE FROM core.ipr WHERE codigo_bip LIKE 'TRULE-%'"))
    await db.execute(
        text("DELETE FROM core.dgi_initiative WHERE name LIKE 'Test Initiative %'")
    )
    await db.execute(text("DELETE FROM core.budget_cycle_tracking WHERE fiscal_year IN (2025, 2026, 2027)"))
    # Admissibility cleanup
    await db.execute(text(
        "DELETE FROM core.admissibility_check WHERE item_id IN "
        "(SELECT id FROM core.admissibility_item WHERE code LIKE 'TEST-%')"
    ))
    await db.execute(text(
        "DELETE FROM core.admissibility_item WHERE code LIKE 'TEST-%'"
    ))
    await db.execute(text(
        "DELETE FROM core.ipr WHERE codigo_bip LIKE 'ADM-%'"
    ))
    # Clean C33 certification test IPRs
    await db.execute(text("DELETE FROM core.ipr WHERE codigo_bip LIKE 'C33-%'"))
    # Clean parametric test data
    await db.execute(text("DELETE FROM core.subv8_fund_ceiling WHERE notes LIKE 'TEST-%'"))
    await db.execute(text("DELETE FROM core.subv8_fund WHERE code LIKE 'TEST-%'"))
    await db.execute(text("DELETE FROM core.fril_category WHERE code LIKE 'T%' AND LENGTH(code) > 2"))
    # Wave E cleanup
    await db.execute(text("DELETE FROM core.risk"))
    await db.execute(text("DELETE FROM txn.event"))
    # Wave B cleanup (order matters for FK constraints)
    await db.execute(text("DELETE FROM core.dgi_service_request"))
    await db.execute(text("DELETE FROM core.dgi_sla"))
    await db.execute(text("DELETE FROM core.dgi_service"))
    await db.execute(text("DELETE FROM core.dgi_escalation"))
    await db.execute(text("DELETE FROM core.dgi_ar_decision"))
    await db.execute(text("DELETE FROM core.dgi_division_interaction"))
    await db.execute(text("""
        UPDATE core.budget_program SET program_code_id = NULL
        WHERE program_code_id IN (
            SELECT id FROM ref.category WHERE scheme = 'budget_program_code' AND code LIKE 'TEST-%'
        )
    """))
    await db.execute(text("DELETE FROM ref.category WHERE scheme = 'budget_program_code' AND code LIKE 'TEST-%'"))
    await db.commit()


# ---------------------------------------------------------------------------
# FastAPI test client with DB override
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client(db):
    """httpx AsyncClient that uses the test DB."""
    async def _override_get_db():
        yield db

    app = create_app()
    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# Auth token fixtures — one per role
# ---------------------------------------------------------------------------

async def _get_user_id(db: AsyncSession, email: str) -> str:
    result = await db.execute(
        text('SELECT id FROM core."user" WHERE email = :email'),
        {"email": email},
    )
    row = result.mappings().first()
    assert row, f"Test user {email} not found in goreos_test. Run scripts/setup_test_db.sh"
    return str(row["id"])


@pytest_asyncio.fixture
async def admin_token(db):
    uid = await _get_user_id(db, "admin@goreos.cl")
    return create_access_token({"sub": uid, "role": "ADMIN_SISTEMA"})


@pytest_asyncio.fixture
async def regional_token(db):
    uid = await _get_user_id(db, "regional@goreos.cl")
    return create_access_token({"sub": uid, "role": "ADMIN_REGIONAL"})


@pytest_asyncio.fixture
async def jefe_token(db):
    uid = await _get_user_id(db, "jefe.daf@goreos.cl")
    return create_access_token({"sub": uid, "role": "JEFE_DIVISION"})


@pytest_asyncio.fixture
async def encargado_token(db):
    uid = await _get_user_id(db, "encargado.daf@goreos.cl")
    return create_access_token({"sub": uid, "role": "ENCARGADO"})


@pytest_asyncio.fixture
async def dgi_token(db):
    uid = await _get_user_id(db, "jefe.dgi@goreos.cl")
    return create_access_token({"sub": uid, "role": "JEFE_DGI"})


@pytest_asyncio.fixture
async def consejero_token(db):
    uid = await _get_user_id(db, "consejero@goreos.cl")
    return create_access_token({"sub": uid, "role": "CONSEJERO_REGIONAL"})


# ---------------------------------------------------------------------------
# Auth header helpers
# ---------------------------------------------------------------------------

def auth(token: str) -> dict:
    """Returns Authorization header dict."""
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Catalog helpers — pre-fetch IDs needed for test data creation
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def catalog(db):
    """Pre-fetched catalog IDs for creating test data."""
    # Commitment type
    ct = await db.execute(text("SELECT id FROM ref.operational_commitment_type LIMIT 1"))
    commitment_type_id = str(ct.scalar())

    # Problem type
    pt = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'problem_type' LIMIT 1")
    )
    problem_type_id = str(pt.scalar())

    # Agreement type
    at_ = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'agreement_type' LIMIT 1")
    )
    agreement_type_id = str(at_.scalar())

    # Agreement state BORRADOR
    ast_ = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'agreement_state' AND code = 'BORRADOR'")
    )
    agreement_state_borrador_id = str(ast_.scalar())

    # Agreement state EN_NEGOCIACION
    asn = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'agreement_state' AND code = 'EN_NEGOCIACION'")
    )
    agreement_state_en_negociacion_id = str(asn.scalar())

    # Agreement state VIGENTE
    asv = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'agreement_state' AND code = 'VIGENTE'")
    )
    agreement_state_vigente_id = str(asv.scalar())

    # Payment status PENDIENTE
    ps = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'payment_status' AND code = 'PENDIENTE'")
    )
    payment_status_pendiente_id = str(ps.scalar())

    # Budget subtitle
    bs = await db.execute(
        text("SELECT id FROM ref.category WHERE scheme = 'budget_subtitle' LIMIT 1")
    )
    budget_subtitle_id = str(bs.scalar())

    # Users with division info
    users = {}
    for email in [
        "admin@goreos.cl", "regional@goreos.cl",
        "jefe.daf@goreos.cl", "encargado.daf@goreos.cl",
        "jefe.dgi@goreos.cl",
    ]:
        result = await db.execute(
            text('SELECT id, division_id FROM core."user" WHERE email = :e'),
            {"e": email},
        )
        row = result.mappings().first()
        users[email] = {
            "id": str(row["id"]),
            "division_id": str(row["division_id"]) if row["division_id"] else None,
        }

    # A division
    div = await db.execute(
        text("""
            SELECT o.id FROM core.organization o
            JOIN ref.category c ON o.org_type_id = c.id
            WHERE c.code = 'DIVISION' AND o.deleted_at IS NULL LIMIT 1
        """)
    )
    division_id = str(div.scalar())

    return {
        "commitment_type_id": commitment_type_id,
        "problem_type_id": problem_type_id,
        "agreement_type_id": agreement_type_id,
        "agreement_state_borrador_id": agreement_state_borrador_id,
        "agreement_state_en_negociacion_id": agreement_state_en_negociacion_id,
        "agreement_state_vigente_id": agreement_state_vigente_id,
        "payment_status_pendiente_id": payment_status_pendiente_id,
        "budget_subtitle_id": budget_subtitle_id,
        "users": users,
        "division_id": division_id,
    }
