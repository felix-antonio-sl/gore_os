# Repository Guidelines

## Habla con el usuario en español

## Project Structure & Module Organization
- `model/model_goreos/`: core PostgreSQL model (`sql/` for DDL, seeds, migrations; `docs/` for model docs).
- `api/`: FastAPI backend.
  - `api/app/`: routers, schemas, services, config.
  - `api/tests/`: pytest suite (`test_*.py`).
  - `api/scripts/etl/`: ETL utilities and loaders (for example `enrich_persons.py`, `load_documents.py`).
- `web/`: Next.js 16 frontend (`src/app`, `src/components`, `src/lib`).
- `docs/` and `architecture/`: plans, audits, ADR-style references.

## Build, Test, and Development Commands
- `docker compose up -d api web`: run backend + frontend against `goreos_db`.
- `docker compose --profile standalone up -d`: run full stack including Postgres/PgAdmin.
- `docker compose exec api pytest`: run backend tests.
- `docker compose exec api python -m scripts.etl.load_documents --dry-run`: ETL dry-run.
- `cd web && npm run dev`: run frontend locally.
- `cd web && npm run lint`: run ESLint.
- `cd web && npm run build`: production build check.

## Coding Style & Naming Conventions
- Python: PEP 8, 4-space indentation, `snake_case` for functions/files, explicit typing when practical.
- TypeScript/React: existing style is 2-space indentation, `PascalCase` components, `camelCase` variables/functions.
- Tests: `test_*.py` filenames and `test_*` functions (enforced by `api/pytest.ini`).
- Keep SQL idempotent where possible (`ON CONFLICT DO NOTHING`) and use parameterized queries.

## Testing Guidelines
- Framework: `pytest` + `pytest-asyncio` for backend integration tests.
- Minimum expectation: run impacted test modules before commit; run full `pytest` for router/schema changes.
- Prefer deterministic tests with fixtures from `api/tests/conftest.py`.

## Commit & Pull Request Guidelines
- Follow Conventional Commit style seen in history: `feat(...)`, `fix(...)`, `docs(...)`, `test(...)`, `chore(...)`.
- Use scoped subjects when useful (example: `feat(etl): add load_documents.py`).
- PRs should include:
  - clear summary and rationale,
  - affected paths/modules,
  - verification evidence (test output, query results, or screenshots for UI),
  - migration/seed notes when DB changes are included.

## Security & Configuration Tips
- Do not commit real secrets; use `.env.example` as template.
- Default local DB target is `goreos_db` (`DB_HOST=goreos_db`, `DB_NAME=goreos_model`).
- Avoid committing raw source datasets unless explicitly required for reproducibility.
