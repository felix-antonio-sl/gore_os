# GORE_OS — Developer Onboarding

## Architecture Overview

```
┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│   Next.js 16          │────▶│   FastAPI             │────▶│   PostgreSQL 16      │
│   :3000  (web/)       │     │   :8000  (api/)       │     │   goreos_db          │
│   App Router + TS     │     │   SQLAlchemy async    │     │   80 tables, 4 schemas│
└──────────────────────┘     └──────────────────────┘     └──────────────────────┘
```

Two user populations share one database:
- **Operativa** (ADMIN_SISTEMA, ADMIN_REGIONAL, JEFE_DIVISION, ENCARGADO): manage IPRs, commitments, problems, alerts, budget, agreements.
- **DGI** (JEFE_DGI, ESP_CONTROL_GESTION, ESP_PROCESOS, ESP_TD): monitor indicators, manage improvement initiatives, generate reports.

Single login → role detection → role-specific sidebar and dashboard.

---

## Local Setup in 5 Minutes

```bash
# 1. Start services (assumes goreos_db is already running on visor_model_default network)
docker compose up -d api web

# 2. Verify services
curl http://localhost:8000/api/health     # → {"status": "ok"}
curl -I http://localhost:3000             # → 307 redirect to /login

# 3. Browse API docs
open http://localhost:8000/api/docs

# 4. Log in with a test user (see table below)
# All passwords: admin123
```

### Test Users

| Email | Role | Population |
|-------|------|------------|
| `admin@goreos.cl` | ADMIN_SISTEMA | operativa |
| `regional@goreos.cl` | ADMIN_REGIONAL | operativa |
| `jefe.daf@goreos.cl` | JEFE_DIVISION | operativa |
| `encargado.daf@goreos.cl` | ENCARGADO | operativa |
| `jefe.dgi@goreos.cl` | JEFE_DGI | dgi |
| `control.gestion@goreos.cl` | ESP_CONTROL_GESTION | dgi |
| `procesos@goreos.cl` | ESP_PROCESOS | dgi |
| `td@goreos.cl` | ESP_TD | dgi |

---

## Key Patterns

### 1. Raw SQL — no ORM
All DB queries use SQLAlchemy `text()` directly. No ORM model classes.

```python
rows = await db.execute(
    text("SELECT id, name FROM core.ipr WHERE deleted_at IS NULL LIMIT :lim"),
    {"lim": 10},
)
items = rows.mappings().all()
```

See ADR-002 for the rationale.

### 2. Controlled vocabularies — ref.category
All FK lookup columns point to `ref.category(scheme, code, label)`. The `scheme` discriminator identifies which vocabulary the FK belongs to. Never mix schemes on a single FK column (Categorical Univocity rule).

```sql
-- Correct: join with scheme filter
JOIN ref.category sev ON sev.id = a.severity_id AND sev.scheme = 'alert_severity'

-- Also valid: filter in WHERE
JOIN ref.category sev ON sev.id = a.severity_id
WHERE sev.scheme = 'alert_severity' AND sev.code = 'CRITICO'
```

See ADR-004 for the rationale.

### 3. Role-based access
Role is embedded in the JWT and re-read from the DB on each request via `CurrentUser` in `api/app/core/deps.py`. Use the `_require_roles(user, *roles)` helper inside endpoint bodies — do NOT use `require_roles()` as a default parameter value.

```python
def _require_roles(user: dict, *roles: str) -> None:
    if user["role_code"] not in roles:
        raise HTTPException(status_code=403, detail="Sin permisos suficientes")
```

### 4. Shared format utilities (frontend)
All date and currency formatting must use `import { formatDate, formatCLP } from "@/lib/format"`. Never define local format functions in page or component files.

### 5. Large dataset selects
`core.ipr` has 3,600+ rows, `core.organization` has 3,300+ rows. Never load all rows into a `<Select>`. Use `ComboboxAsync` with server-side search (e.g., `GET /api/catalogs/iprs?search=TERM`).

---

## How to Add a New Feature

Follow this sequence:

1. **Schema** — Add/modify tables in `model/model_goreos/sql/` as a migration SQL file (e.g., `goreos_migration_waveN_feature.sql`). Add a rollback file.
2. **Pydantic schemas** — Create `api/app/schemas/feature.py` with request/response models.
3. **Router** — Create `api/app/routers/feature.py`. Register it in `api/app/main.py`.
4. **Test** — Create `api/tests/test_feature.py`. Rebuild test DB if schema changed.
5. **Frontend types** — Add TypeScript interfaces to `web/src/types/index.ts`.
6. **Frontend page/component** — Create page under `web/src/app/(app)/feature/`. Use `ApiClient` from `web/src/lib/api.ts` for all HTTP calls.
7. **Sidebar** — Add nav item to `web/src/components/sidebar.tsx` if needed.

After any backend changes, restart the API container:
```bash
docker compose restart api
```

---

## How to Run Migrations

```bash
# Apply a migration to production DB
./scripts/run_migrations.sh model/model_goreos/sql/goreos_migration_waveN_feature.sql

# Roll back
./scripts/run_migrations.sh model/model_goreos/sql/goreos_rollback_waveN_feature.sql

# Rebuild test DB after schema changes
./scripts/setup_test_db.sh
```

---

## Testing Quick Reference

```bash
# Setup test DB (first time or after schema change)
./scripts/setup_test_db.sh

# Run full suite
docker compose exec api pytest -v

# Run a single module
docker compose exec api pytest tests/test_compromisos.py -v

# Run a single test
docker compose exec api pytest tests/test_auth.py::test_login_success -v
```

Current coverage: **169 tests** (167 pass + 1 skip + 1 known fail) across 18 modules.

For test patterns and available fixtures, see `api/tests/conftest.py` and ADR-005.
