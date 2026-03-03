# ADR-005: Integration Tests Against Real PostgreSQL

**Status**: Accepted
**Date**: 2026-03-03
**Deciders**: GORE_OS development team

## Context

GORE_OS uses raw SQL via `text()` — there is no ORM model layer to mock. The business logic is tightly coupled to PostgreSQL features: triggers, generated columns, partitioned tables, advisory locks, JSONB operations, and `ref.category` scheme constraints. Unit tests with mocked DB sessions would not catch SQL syntax errors, schema mismatches, or trigger misfires.

## Decision

All integration tests run against a real PostgreSQL instance (`goreos_test` DB), cloned from `goreos_model` via `pg_dump --schema-only`. No mocks. Tests use `httpx.AsyncClient` with `ASGITransport` to hit the actual FastAPI application with the test DB wired in via `app.dependency_overrides[get_db]`.

## Test infrastructure

- **Test DB setup**: `scripts/setup_test_db.sh` — clones schema, copies `ref.category` rows via COPY, seeds territory and test users.
- **Session scope**: Each test gets a fresh `AsyncSession` (function-scoped) to avoid state leakage.
- **Auth**: Real JWT tokens generated with `create_access_token` for 5 roles (admin, regional, jefe, encargado, dgi).
- **Catalog fixture**: Pre-fetches commonly needed IDs (commitment types, agreement states, etc.) to avoid boilerplate in each test.

## Current coverage

169 tests across 18 modules (167 pass + 1 skip + 1 known fail). Covers auth, all CRUD modules, state machines, role restrictions, and concurrent code generation.

## Trade-offs

- **Slower than unit tests**: Each test hits a real DB. Full suite runs in ~30–60s inside the container.
- **Requires goreos_test DB**: Must run `setup_test_db.sh` before first run or after schema changes.
- **Known issue**: `test_initiatives::test_move_to_en_curso` may fail if the test DB accumulates 5+ EN_CURSO initiatives from prior runs. Clean with `DELETE FROM core.dgi_initiative WHERE deleted_at IS NULL` on `goreos_test`.
