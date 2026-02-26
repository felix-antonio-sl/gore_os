# Backend Test Suite — Design Document

> Date: 2026-02-26
> Scope: Backend API integration tests (FastAPI + PostgreSQL)
> Status: Approved

---

## 1. Goal

Add the first automated test suite to GORE_OS. Covers the backend API only (FastAPI endpoints) using integration tests against a real PostgreSQL database. Prioritizes state machines, financial calculations, role-based access, and WIP limits.

## 2. Technology Stack

| Tool | Purpose |
|------|---------|
| pytest | Test runner |
| pytest-asyncio | Async test support (all endpoints are async) |
| httpx | AsyncClient for ASGI transport (no real HTTP server needed) |

**Execution**: `docker compose exec api pytest -v` — runs inside the API container.

## 3. Database Strategy

- **Test database**: `goreos_test` created from `goreos_model` schema (same DDL + seed data)
- **Isolation**: Each test function runs inside a transaction that rolls back on teardown
- **No residue**: Tests never commit — the DB stays clean between runs
- **Setup**: One-time `CREATE DATABASE goreos_test` + apply DDL + seed on first run

### Why not mock the DB?

The backend is 100% raw SQL (`text()` queries). There is no ORM layer to unit-test. The SQL queries ARE the business logic. Mocking the DB would test nothing meaningful.

## 4. Auth Strategy

Use real JWT tokens generated with `create_access_token()` from `security.py`. The test users (admin@goreos.cl, regional@goreos.cl, etc.) already exist in the seeded DB. Test fixtures provide pre-built `httpx.AsyncClient` instances authenticated as each role.

No mocking of `get_current_user` — the full auth pipeline is exercised.

## 5. Test Architecture

```
api/
├── tests/
│   ├── conftest.py          # Fixtures: test engine, session override, auth clients
│   ├── test_auth.py         # Login flow + token validation (5 tests)
│   ├── test_compromisos.py  # Commitment state machine (12 tests)
│   ├── test_problemas.py    # Problem state transitions (8 tests)
│   ├── test_convenios.py    # Agreement lifecycle + installments (10 tests)
│   ├── test_presupuesto.py  # Budget calculations (8 tests)
│   ├── test_initiatives.py  # Kanban WIP limits (7 tests)
│   └── test_dashboard.py    # Role dispatch + KPI aggregations (6 tests)
├── pytest.ini               # pytest config (asyncio_mode = auto)
└── requirements.txt         # + pytest, pytest-asyncio, httpx
```

## 6. conftest.py Design

### Key Fixtures

```python
# Engine pointing to goreos_test
@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine("postgresql+asyncpg://goreos:goreos_2026@goreos_db:5432/goreos_test")
    yield engine
    await engine.dispose()

# Session with rollback per test
@pytest.fixture
async def db_session(test_engine):
    conn = await test_engine.connect()
    txn = await conn.begin()
    session = AsyncSession(bind=conn)
    yield session
    await txn.rollback()
    await conn.close()

# Override FastAPI dependencies
@pytest.fixture
async def client(db_session):
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

# Auth helpers — one per role
@pytest.fixture
def admin_token(db_session):
    # Query user id for admin@goreos.cl, generate JWT
    ...

@pytest.fixture
async def admin_client(client, admin_token):
    client.headers["Authorization"] = f"Bearer {admin_token}"
    return client
```

### Dependency Override Pattern

FastAPI's `app.dependency_overrides[get_db]` replaces the real DB session with the test session (which rolls back). This means every endpoint uses the test transaction.

## 7. Test Modules — Detailed

### 7.1 test_auth.py (5 tests)

| Test | Behavior |
|------|----------|
| `test_login_success` | Valid credentials → 200 + access_token + user data |
| `test_login_wrong_password` | → 401 |
| `test_login_inactive_user` | → 401 (user.is_active = false) |
| `test_protected_endpoint_no_token` | GET /api/dashboard without header → 401 |
| `test_protected_endpoint_expired_token` | Manually expired JWT → 401 |

### 7.2 test_compromisos.py (12 tests)

**State machine tests:**

| Test | Scenario | Expected |
|------|----------|----------|
| `test_create_commitment` | POST /api/compromisos with valid data | 201 + auto-generated OC-XXXXX code |
| `test_complete_as_responsible` | Responsible user completes own | 200, completed_at set |
| `test_complete_as_admin` | Admin completes any | 200 |
| `test_complete_already_verified` | Complete a VERIFICADO commitment | 409 |
| `test_verify_as_jefe_own_division` | JEFE verifies in own division | 200, verified_at set |
| `test_verify_cross_division` | JEFE verifies other division | 403 |
| `test_verify_from_pendiente` | Verify without completing first | 409 |
| `test_devolver_from_completado` | Return COMPLETADO to EN_PROGRESO | 200, completed_at cleared |
| `test_devolver_from_pendiente` | Return PENDIENTE | 409 |
| `test_devolver_requires_observations` | Devolver without observations | 422 |
| `test_encargado_sees_only_own` | ENCARGADO list filters to responsible_id | Only own commitments |
| `test_history_recorded` | After state change, commitment_history has entry | History row exists |

### 7.3 test_problemas.py (8 tests)

| Test | Scenario | Expected |
|------|----------|----------|
| `test_create_problem` | POST with valid data | 201, state = ABIERTO, code = PR-XXXXX |
| `test_patch_to_en_gestion` | PATCH state_id to EN_GESTION | 200 |
| `test_resolve_sets_metadata` | PATCH state to RESUELTO | resolved_by_id + resolved_at auto-set |
| `test_patch_invalid_state` | PATCH with non-existent UUID | 422 or 500 |
| `test_patch_solution_only` | PATCH only proposed_solution | 200, state unchanged |
| `test_jefe_sees_own_division_iprs` | JEFE_DIVISION filter | Only problems on own-division IPRs |
| `test_days_open_calculation` | Problem created today | days_open = 0 |
| `test_search_filter` | Search by description fragment | Matching results returned |

### 7.4 test_convenios.py (10 tests)

| Test | Scenario | Expected |
|------|----------|----------|
| `test_create_agreement` | POST with valid data | 201, auto-generated AGR-YYYY-XXXXX |
| `test_create_with_manual_number` | POST with agreement_number | Uses provided number |
| `test_patch_state` | Update state_id to VIGENTE | 200 |
| `test_patch_allowlist` | PATCH with non-allowed field | Field ignored, no error |
| `test_add_installment` | POST cuota with number 1 | 201 |
| `test_duplicate_installment_number` | POST cuota with existing number | 409 (UNIQUE constraint) |
| `test_update_installment` | PATCH cuota payment_status | 200 |
| `test_days_to_expiry_vigente` | Agreement VIGENTE with future valid_to | Positive days |
| `test_days_to_expiry_null` | Agreement with no valid_to | days_remaining = null |
| `test_list_ordering` | Multiple agreements, different states | VIGENTE first, then by expiry |

### 7.5 test_presupuesto.py (8 tests)

| Test | Scenario | Expected |
|------|----------|----------|
| `test_create_budget_program` | POST with amounts | 201, committed/accrued/paid = 0 |
| `test_duplicate_code_fiscal_year` | Same code + fiscal_year | 409 |
| `test_same_code_different_year` | Same code, different fiscal_year | 201 |
| `test_execution_calculation` | paid=700k, current=1M | execution_pct = 70.0 |
| `test_execution_zero_current` | current=0 | execution_pct = 0.0 (not division error) |
| `test_paid_exceeds_current` | paid=1.5M, current=1M | execution_pct = 150.0 (allowed) |
| `test_jefe_only_own_division` | JEFE patches other division's program | 403 |
| `test_resumen_by_division` | GET resumen?group_by=division | Aggregated sums per division |

### 7.6 test_initiatives.py (7 tests)

| Test | Scenario | Expected |
|------|----------|----------|
| `test_create_initiative` | POST basic data | 201, code = INI-XXXX, status = BACKLOG |
| `test_move_to_en_curso` | Move from BACKLOG | 200, status updated |
| `test_wip_limit_en_curso` | Move 6th initiative to EN_CURSO | 409 with WIP message |
| `test_wip_limit_revision` | Move 3rd initiative to REVISION | 409 |
| `test_move_to_completado` | No WIP limit | 200 |
| `test_move_noop` | Move EN_CURSO → EN_CURSO | 200 (no error) |
| `test_create_with_en_curso_status` | Create directly in EN_CURSO | 201 (no WIP check on create) |

### 7.7 test_dashboard.py (6 tests)

| Test | Scenario | Expected |
|------|----------|----------|
| `test_admin_dashboard` | GET /api/dashboard as ADMIN_REGIONAL | 200 with 7 KPIs |
| `test_jefe_dashboard` | GET /api/dashboard as JEFE_DIVISION | 200 with division-scoped KPIs |
| `test_encargado_dashboard` | GET /api/dashboard as ENCARGADO | 200 with personal KPIs |
| `test_mi_division_endpoint` | GET /api/dashboard/mi-division as JEFE | 200 with team load |
| `test_mis_compromisos_endpoint` | GET /api/dashboard/mis-compromisos as ENCARGADO | 200 with 3 groups |
| `test_chart_data` | GET /api/dashboard/chart-data | 200 with 3 chart datasets |

## 8. Test Database Setup Script

```sql
-- Run once to create test DB (from goreos_db container)
CREATE DATABASE goreos_test TEMPLATE goreos_model;
```

This clones the full schema + seed data. Tests use rollback transactions so the DB never mutates.

## 9. Execution

```bash
# Run all tests
docker compose exec api pytest -v

# Run specific module
docker compose exec api pytest tests/test_compromisos.py -v

# Run with coverage
docker compose exec api pytest --cov=app --cov-report=term-missing
```

## 10. Summary

| Metric | Value |
|--------|-------|
| Total tests | ~56 |
| Test modules | 7 |
| Dependencies added | 3 (pytest, pytest-asyncio, httpx) |
| DB strategy | Real PostgreSQL with transaction rollback |
| Auth strategy | Real JWT tokens, real user lookup |
| Execution | Inside Docker container |
| Estimated implementation | 7 files + config |
