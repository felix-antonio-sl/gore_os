# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GORE_OS is an institutional operating system for the Regional Government of Ñuble (GORE), Chile. It serves two user populations on a shared PostgreSQL database:

- **Operativa** (ADMIN_SISTEMA, ADMIN_REGIONAL, JEFE_DIVISION, ENCARGADO): Manage IPR crisis — commitments, problems, alerts, budget programs, agreements. Replaces Excel workflows.
- **DGI** (JEFE_DGI, ESP_CONTROL_GESTION, ESP_PROCESOS, ESP_TD): Monitor institutional indicators (real-time from DB), analyze data, generate auto-populated reports, manage improvement initiatives.

One app, two navigation experiences. Single login → role detection → routing to appropriate sidebar/dashboard.

## Quick Start

```bash
# The goreos_db container typically already runs on visor_model_default network.
# Start API + Web (assumes goreos_db is already running):
docker compose up -d api web

# Start everything including standalone PostgreSQL:
docker compose --profile standalone up -d

# Verify services:
curl http://localhost:8000/api/health     # API
curl -I http://localhost:3000             # Web (307 redirect to /login)

# Load demo data (budget programs + agreements with DEMO- prefix):
docker exec -i goreos_db psql -U goreos -d goreos_model \
  < model/model_goreos/sql/goreos_seed_demo_ciclo2.sql

# Remove demo data (only DEMO- records, real data untouched):
docker exec -i goreos_db psql -U goreos -d goreos_model \
  < model/model_goreos/sql/goreos_unseed_demo_ciclo2.sql

# Refresh DGI indicators from real DB aggregates:
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -d "username=jefe.dgi@goreos.cl&password=admin123" \
  -H "Content-Type: application/x-www-form-urlencoded" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
curl -s -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/dgi/data/indicators/refresh

# Database shell:
docker exec goreos_db psql -U goreos -d goreos_model

# View logs:
docker compose logs -f api
docker compose logs -f web
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────────┐
│  Next.js 16  │────▶│  FastAPI      │────▶│  PostgreSQL 16       │
│  :3000       │     │  :8000       │     │  goreos_db           │
│  web/        │     │  api/        │     │  visor_model_default │
└─────────────┘     └──────────────┘     └──────────────────────┘
```

### Backend (`api/`)

- **Framework**: FastAPI + uvicorn (hot-reload via volume mount)
- **DB**: SQLAlchemy async + asyncpg. Raw SQL via `text()` — no ORM models, queries use `db.execute(text("..."), params).mappings()`
- **Auth**: JWT (python-jose) + bcrypt. OAuth2PasswordBearer. Token in `Authorization: Bearer` header.
- **Schemas**: Pydantic v2 in `api/app/schemas/`
- **Config**: pydantic-settings in `api/app/core/config.py`, reads env vars

Key files:
- `api/app/main.py` — app factory, router registration
- `api/app/core/deps.py` — `CurrentUser` dependency (extracts user dict from JWT)
- `api/app/core/security.py` — `OPERATIONAL_ROLES` / `DGI_ROLES` sets, password hashing, JWT
- `api/app/routers/` — 15 routers (auth, ipr, compromisos, problemas, alertas, dashboard, catalogs, presupuesto, convenios, admin, reuniones, dgi_cockpit, dgi_initiatives, dgi_data, dgi_reports)

API conventions:
- All routes prefixed `/api/` (e.g., `/api/ipr`, `/api/dgi/cockpit`)
- Paginated endpoints return `{items, total, page, page_size, total_pages}`
- DGI list endpoints return plain arrays (not paginated)
- Dashboard endpoint (`GET /api/dashboard`) is role-aware: dispatches to different queries per role
- DGI cockpit endpoint (`GET /api/dgi/cockpit`) returns different response shapes per DGI role
- PATCH endpoints use allowlisted column names — field names in Pydantic update models must match DB columns exactly
- Person table columns: `names`, `paternal_surname` (NOT `nombre`, `apellido_paterno`)
- User table FK: `system_role_id` (NOT `role_id`)

### Frontend (`web/`)

- **Framework**: Next.js 16 (App Router, Turbopack), TypeScript, TailwindCSS v4
- **Components**: shadcn/ui (Radix UI) — installed in `web/src/components/ui/`
- **Icons**: lucide-react
- **State**: React Context (`useAuth`) + URL params (`useSearchParams`) for filters

Key patterns:
- `web/src/lib/api.ts` — singleton `ApiClient` with `get<T>()`, `post<T>()`, `patch<T>()`. Token in localStorage (`goreos_token`). Auto-redirect to `/login` on 401. On error, extracts `.detail` from FastAPI JSON error bodies automatically.
- `web/src/lib/auth.tsx` — `AuthProvider` context, `useAuth()` hook returns `{user, loading, login, logout}`
- `web/src/types/index.ts` — all TypeScript interfaces. `User.population` (`"operativa" | "dgi"`) drives sidebar/dashboard routing.
- `web/src/components/sidebar.tsx` — conditional nav: `operationalNav` (8 items: Inicio, IPR, Compromisos, Problemas, Alertas, Presupuesto, Convenios, Reuniones) + role-specific items (Mi División for JEFE_DIVISION, Mis Compromisos for ENCARGADO) + `adminOnlyNav` (Usuarios, Divisiones for ADMIN_SISTEMA) vs `dgiNav` (5 items) based on `user.population`
- `web/src/app/(app)/layout.tsx` — AppShell wrapper for authenticated routes
- `web/src/app/(app)/dashboard/page.tsx` — detects population, renders operational dashboard or DGI cockpit component per role
- `web/src/components/combobox-async.tsx` — reusable searchable select with server-side search (debounce 300ms, `shouldFilter={false}`). Use for any field with 500+ options (e.g., IPR Asociada). Props: `value`, `onChange`, `searchFn(query) → Promise<ComboboxOption[]>`, `placeholder`.

### Database

**77 tables across 4 schemas** (71 original + 6 DGI):

| Schema | Purpose |
|--------|---------|
| `meta` | Role/Process/Entity/Story atoms (10 tables) |
| `ref`  | Controlled vocabularies via `ref.category` — 90+ schemes + `ref.operational_commitment_type` |
| `core` | Business entities: IPR, Agreement, Budget, User, plus operational (commitment, problem, alert) and DGI (indicator, initiative, report, bpmn_model, committee_session, data_source_status) |
| `txn`  | Event sourcing (partitioned) |

**Category Pattern**: `ref.category(scheme, code, label)` — each FK column points to exactly ONE scheme (Categorical Univocity). Before creating new schemes, check existing ones: `SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;`

**DGI schemes**: `dgi_initiative_status`, `dgi_indicator_dimension`, `dgi_signal`, `dgi_report_type`, `dgi_report_status`, `dgi_bpmn_status`, `dgi_dmaic_phase`, `dgi_session_status`, `dgi_alert_status`, `dgi_decree_status`, `dgi_source_status`

**Budget schemes** (Ciclo 2): `budget_item` (14), `budget_allocation` (15), `program_type` (5), `budget_commitment_status` (5). Pre-existing: `budget_subtitle` (8), `funding_source` (11), `payment_status` (5), `agreement_type` (6), `agreement_state` (10 with transitions), `cgr_outcome` (7).

### Docker Networking

`goreos_db` runs on the `visor_model_default` Docker network (external, shared with other projects). The `docker-compose.yml` declares this as external. Services `api` and `web` connect to this network to reach `goreos_db`.

## Test Users

All passwords: `admin123`

| Email | Role | Population |
|-------|------|------------|
| `regional@goreos.cl` | ADMIN_REGIONAL | operativa |
| `jefe.daf@goreos.cl` | JEFE_DIVISION | operativa |
| `encargado.daf@goreos.cl` | ENCARGADO | operativa |
| `jefe.dgi@goreos.cl` | JEFE_DGI | dgi |
| `control.gestion@goreos.cl` | ESP_CONTROL_GESTION | dgi |
| `procesos@goreos.cl` | ESP_PROCESOS | dgi |
| `td@goreos.cl` | ESP_TD | dgi |
| `admin@goreos.cl` | ADMIN_SISTEMA | operativa |

## Common Commands

```bash
# Database
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT COUNT(*) FROM core.ipr;"
docker exec goreos_db psql -U goreos -d goreos_model -c "SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;"

# API test (login + authenticated request)
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -d "username=regional@goreos.cl&password=admin123" \
  -H "Content-Type: application/x-www-form-urlencoded" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/dashboard | python3 -m json.tool

# Frontend type check + build
cd web && npx next build

# Frontend lint
cd web && npx eslint src/

# API docs (Swagger UI)
open http://localhost:8000/api/docs
```

## Domain Model

Central entity: **IPR (Intervención Pública Regional)** — polymorphic (7 types: INFRAESTRUCTURA, EQUIPAMIENTO, TRANSFERENCIA, PROGRAMA_SOCIAL, PROGRAMA_8PCT, CONSERVACION, ESTUDIO).

Operational layer:
- **operational_commitment**: Tasks with due dates, state machine (PENDIENTE → EN_PROGRESO → COMPLETADO → VERIFICADO), tracked via `commitment_history`. Full CRUD: create form at `/compromisos/nuevo`, state actions in drawer.
- **ipr_problem**: Issues detected on IPRs (ABIERTO → EN_GESTION → RESUELTO | CERRADO_SIN_RESOLVER), typed (TECNICO, FINANCIERO, LEGAL, etc.). Full CRUD: create form at `/problemas/nuevo`, resolve/close in drawer via PATCH with `state_id`.
- **alert**: System-generated warnings with severity (CRITICO, ALTO, ATENCION, INFO), can be attended/resolved
- **budget_program**: Fiscal year budget programs per division with execution tracking (initial → current → committed → accrued → paid). Related: `budget_carryover` (year-over-year), `budget_commitment` (CDPs linked to IPRs/agreements)
- **agreement**: Institutional agreements (MANDATO, TRANSFERENCIA, COLABORACION, etc.) with state machine (BORRADOR → VIGENTE → VENCIDO/TERMINADO). Related: `agreement_installment` (payment schedule with status tracking)
- **progress_report**: Periodic physical/financial progress reports per IPR. Create via `POST /api/ipr/{id}/avances`, list via `GET /api/ipr/{id}/avances`. Auto-incremented `report_number`.
- **crisis_meeting**: Crisis meetings module using existing `core.committee` + `core.session` + `core.crisis_meeting` + `core.minute` + `core.session_agreement` tables. Full lifecycle: PROGRAMADA → EN_CURSO → FINALIZADA. Auto-suggestions from critical alerts, overdue commitments, open problems.

DGI layer:
- **dgi_indicator**: Institutional semaphore (5 dimensions: PRESUPUESTO, CARTERA_IPR, CONVENIOS, TDE, RIESGOS) with signal (VERDE/AMARILLO/ROJO). Values computed from real DB aggregates via `POST /api/dgi/data/indicators/refresh` (4/5 dimensions; TDE is static)
- **dgi_initiative**: Kanban board with WIP limits enforced server-side (EN_CURSO: 5, REVISION: 2). `POST /api/dgi/initiatives/{id}/move` raises HTTP 409 if limit reached. `InitiativeItem` response includes both `responsible_id` (UUID) and `responsible_name` (string) for pre-populating edit forms.
- **dgi_report**: Institutional reports (FLASH, SEMANAL, MENSUAL, TEMATICO) with 6 auto-populated sections from real data. User edits stored in `metadata` JSONB via atomic `jsonb_set`. Sections: resumen, tabla_indicadores, alertas, avance_dgi, decisiones, prioridades.

## Demo Data Strategy

Demo data uses prefix `DEMO-` in codes/numbers for clear identification:
- `goreos_seed_demo_ciclo2.sql` — structural schemes (permanent) + demo records (removable)
- `goreos_unseed_demo_ciclo2.sql` — deletes only `DEMO-` records, real data untouched
- FKs to real data use subqueries (e.g., `SELECT id FROM core.organization WHERE code='DAF'`), not hardcoded UUIDs
- Demo budget programs: DEMO-BP-001..006 (3 divisions, varied execution 30%-80%)
- Demo agreements: DEMO-AGR-001..004 (2 VIGENTE, 1 EN_MODIFICACION, 1 VENCIDO, with installments)
- Demo CDPs: DEMO-CDP-001..008 (linked to real IPRs)

## Key References

- `model/model_goreos/sql/goreos_ddl.sql` — DDL (77 tables), ontological mappings in lines 21-37
- `model/model_goreos/sql/goreos_seed.sql` — 90+ category schemes
- `model/model_goreos/sql/goreos_seed_demo_ciclo2.sql` — demo data for budget + agreements
- `model/model_goreos/docs/GOREOS_ERD_v3.md` — ERD + data dictionary
- `model/GLOSARIO.yml` — 244 ontological terms (Gist 14.0 + GNUB + TDE)
- `docs/plans/2026-02-24-dgi-ui-ux-design.md` — DGI UI/UX design document
- `docs/GORE_OS_Testing_Ciclo3.md` — Testing document with all features, credentials, and test cases
- `architecture/Omega_GORE_OS_Definition_v3.0.0.md` — system specification

## Critical Rules

1. **Categorical Univocity**: Each FK column → exactly 1 `ref.category` scheme. Never mix dimensions.
2. **Person columns**: Use `names` and `paternal_surname` (NOT `nombre`/`apellido_paterno`). User FK: `system_role_id` (NOT `role_id`).
3. **API consistency**: Operational endpoints use POST for state changes (e.g., `POST /compromisos/{id}/completar`). DGI list endpoints return plain arrays. Paginated endpoints return `{items, total, page, page_size, total_pages}`.
4. **Alert subject_type**: Stored as `'core.ipr'` in DB (fully qualified), not `'ipr'`. Always use `'core.ipr'` in all SQL queries.
5. **Docker network**: `goreos_db` is on `visor_model_default` (external). Don't create a separate postgres service unless using `--profile standalone`.
6. **No ORM models**: Backend uses raw SQL with `text()` from SQLAlchemy. All queries go through `db.execute(text("..."), params).mappings()`.
7. **PATCH allowlist**: PATCH endpoints must validate column names against an explicit allowlist. Field names in Pydantic update models must match DB column names exactly.
8. **Demo data convention**: All demo records use `DEMO-` prefix in code/number fields. Never mix demo data with real data. Use `goreos_unseed_demo_ciclo2.sql` to clean.
9. **DGI indicator refresh**: Run `POST /api/dgi/data/indicators/refresh` to recompute semaphore values from real data. Idempotent. TDE dimension has no real data source yet.
10. **Report section edits**: Stored atomically in `metadata` JSONB using `jsonb_set` (not read-modify-write). Auto-populated content is regenerated on each GET; only user edits persist.
11. **Organization table**: `core.organization` does NOT have `is_active` column. Use `deleted_at IS NULL` to check if active. The type FK column is `org_type_id` (NOT `organization_type_id`).
12. **Role restriction pattern**: Use a helper function `_require_roles(user, ...)` called inside the endpoint body. Do NOT use `require_roles()` from `deps.py` as a default parameter value — it conflicts with `CurrentUser` (which is `Annotated[dict, Depends()]`).
13. **Reuniones module**: Uses existing DDL tables (`core.committee`, `core.session`, `core.crisis_meeting`, `core.minute`, `core.session_agreement`, `core.agenda_item_context`). No DDL migration needed. A dedicated crisis committee (code `COMITE-CRISIS`) is auto-created on first use.
14. **Dashboard endpoints**: Role-specific dashboards: `GET /api/dashboard` (base, role-aware), `GET /api/dashboard/ejecutivo` (ADMIN with division breakdown), `GET /api/dashboard/mi-division` (JEFE_DIVISION team load), `GET /api/dashboard/mis-compromisos` (ENCARGADO grouped commitments).
15. **Admin module**: `GET/POST/PATCH /api/admin/usuarios`, `POST /api/admin/usuarios/{id}/toggle-activo`, `POST /api/admin/usuarios/{id}/reset-password`, `GET/POST/PATCH /api/admin/divisiones`. All restricted to ADMIN_SISTEMA.
16. **After code changes**: Always restart API container (`docker compose restart api`) — uvicorn hot-reload may not catch new files/imports.
17. **Large dataset selects**: `core.ipr` has 3,600+ rows, `core.organization` has 3,300+ rows. Never load all records into a `<Select>`. Use `ComboboxAsync` for IPR fields (server-side search via `GET /api/catalogs/iprs?search=TERM`). For divisions, `GET /api/catalogs/divisions` returns only ~31 real divisions (DIVISION + GORE type) — any query that joins `core.organization` without filtering `org_type_id` will return all organizations.
18. **API error messages**: `ApiClient` in `api.ts` automatically extracts `.detail` from FastAPI JSON error responses. Backend `HTTPException(detail="...")` strings reach frontend `catch (err)` blocks as clean text — no need to parse JSON in component code.
