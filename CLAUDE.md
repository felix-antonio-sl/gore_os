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
- `api/app/routers/` — 16 routers (auth, ipr, compromisos, problemas, alertas, dashboard, catalogs, presupuesto, convenios, admin, reuniones, search, dgi_cockpit, dgi_initiatives, dgi_data, dgi_reports)

API conventions:
- All routes prefixed `/api/` (e.g., `/api/ipr`, `/api/dgi/cockpit`)
- Paginated endpoints return `{items, total, page, page_size, total_pages}`
- DGI list endpoints return plain arrays by default; `GET /api/dgi/initiatives` supports optional pagination via `?page=1&page_size=N` (omit for backward-compatible plain array)
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

**78 tables across 4 schemas** (58 logical + 20 txn partitions):

| Schema | Purpose |
|--------|---------|
| `meta` | Role/Process/Entity/Story atoms (5 tables) |
| `ref`  | Controlled vocabularies via `ref.category` — 90+ schemes + `ref.operational_commitment_type` |
| `core` | Business entities: IPR, Agreement, Budget, User, plus operational (commitment, problem, alert) and DGI (indicator, initiative, report, bpmn_model, committee_session, data_source_status) |
| `txn`  | Event sourcing (partitioned) |

**Category Pattern**: `ref.category(scheme, code, label)` — each FK column points to exactly ONE scheme (Categorical Univocity). Before creating new schemes, check existing ones: `SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;`

**DGI schemes**: `dgi_initiative_status`, `dgi_indicator_dimension`, `dgi_signal`, `dgi_report_type`, `dgi_report_status`, `dgi_bpmn_status`, `dgi_dmaic_phase`, `dgi_session_status`, `dgi_alert_status`, `dgi_decree_status`, `dgi_source_status`

**Budget schemes** (Ciclo 2): `budget_item` (14), `budget_allocation` (15), `program_type` (5), `budget_commitment_status` (5). Pre-existing: `budget_subtitle` (8), `funding_source` (11), `payment_status` (5), `agreement_type` (6), `agreement_state` (13 with transitions — includes EN_REVISION_FINANCIERA, VISADO_INTERNO, TDR_PENDIENTE), `cgr_outcome` (7).

**Organization types**: `org_type` scheme has 14 codes. Internal GORE orgs use 6: GORE (1), DIVISION (8), DEPARTAMENTO (6), UNIDAD (8), STAFF_UNIT (7), ADVISORY_BODY (3). External orgs use: MUNICIPALIDAD, SERVICIO, MINISTERIO, UNIVERSIDAD, ONG, EMPRESA, ORG_COMUNITARIA, COMUNITARIA.

**Organization hierarchy**: 3-level depth via `parent_id` endofunctor: GORE-NUBLE → Divisions → Departamentos → Unidades. Example: GORE-NUBLE → DAF → FINANZAS → UCR.

**System roles**: `system_role` scheme has 13 codes: GOBERNADOR (0), ADMIN_SISTEMA (1), ADMIN_REGIONAL (2), JEFE_DIVISION (3), ENCARGADO (4), JEFE_DGI (5), ESP_CONTROL_GESTION (6), ESP_PROCESOS (7), ESP_TD (8), CONSEJERO_REGIONAL (9), SECRETARIO_EJECUTIVO (10), JEFE_DEPARTAMENTO (11), JEFE_UNIDAD (12).

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

## Testing

**86 integration tests** against real PostgreSQL (`goreos_test` DB). No mocks — tests exercise real SQL, JWT auth, and business logic.

```bash
# Setup test DB (first time or to reset):
./scripts/setup_test_db.sh

# Run full suite inside API container:
docker compose exec api pytest -v

# Run single module:
docker compose exec api pytest tests/test_compromisos.py -v

# Run single test:
docker compose exec api pytest tests/test_auth.py::test_login_success -v

# Install test deps in container (if container was rebuilt):
docker compose exec api pip install pytest pytest-asyncio httpx
```

Test modules: `test_auth` (8), `test_compromisos` (14), `test_presupuesto` (8), `test_initiatives` (7), `test_problemas` (8), `test_convenios` (7), `test_dashboard` (6), `test_security_readonly` (12), `test_ipr_children` (14).

**Test DB setup** (`scripts/setup_test_db.sh`): clones schema via `pg_dump --schema-only` from `goreos_model`, copies all `ref.category` rows via `COPY`, seeds territory + test users. The DDL file has circular dependencies (functions defined after tables that use them), so never apply `goreos_ddl.sql` directly to a fresh DB — always use `pg_dump` from production.

**Test architecture**: `conftest.py` creates a fresh `AsyncSession` per test against `goreos_test`, overrides `get_db` dependency, generates real JWT tokens for 5 roles (admin, regional, jefe, encargado, dgi). The `catalog` fixture pre-fetches common IDs (commitment types, problem types, agreement states, etc.).

**Known issue**: `test_convenios::test_patch_state` is marked `xfail` — trigger `fn_validate_state_transition` references `OLD.status_id` but the column is `state_id`.

**DGI category schemes** (e.g., `dgi_initiative_status`) are NOT in `goreos_seed.sql` — they only exist in `goreos_model` and are copied to `goreos_test` via `COPY ref.category`. If adding new DGI schemes, insert them into production first.

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

Central entity: **IPR (Intervención Pública Regional)** — polymorphic (8 types: INFRAESTRUCTURA, EQUIPAMIENTO, CONSERVACION, TRANSFERENCIA, SUBSIDIO, ESTUDIO, PROGRAMA_SOCIAL, PROGRAMA_8PCT).

Operational layer:
- **operational_commitment**: Tasks with due dates, state machine (PENDIENTE → EN_PROGRESO → COMPLETADO → VERIFICADO), tracked via `commitment_history`. Full CRUD: create form at `/compromisos/nuevo`, inline creation from IPR detail via `IprCompromisoDrawer`, state actions in drawer. Drawer shows clickable IPR link (navigates to `/ipr/{id}`).
- **ipr_problem**: Issues detected on IPRs (ABIERTO → EN_GESTION → RESUELTO | CERRADO_SIN_RESOLVER), typed (TECNICO, FINANCIERO, LEGAL, etc.). Full CRUD: create form at `/problemas/nuevo`, inline creation from IPR detail via `IprProblemaDrawer`, resolve/close in drawer via PATCH with `state_id`. Drawer shows state timeline (detected → en gestión → resolved) and clickable IPR link.
- **alert**: System-generated warnings with severity (CRITICO, ALTO, ATENCION, INFO), can be attended/resolved. `AlertCard` supports `onViewSubject` callback for navigation to any subject_type (`core.ipr`, `core.operational_commitment`, `core.ipr_problem`, `core.agreement`).
- **budget_program**: Fiscal year budget programs per division with execution tracking (initial → current → committed → accrued → paid). Related: `budget_carryover` (year-over-year), `budget_commitment` (CDPs linked to IPRs/agreements). CDPs queryable by IPR via `GET /api/presupuesto/cdps-por-ipr/{ipr_id}`. Presupuesto list filterable by `division_id` in both backend and frontend.
- **agreement**: Institutional agreements (MANDATO, TRANSFERENCIA, COLABORACION, etc.) with 13-state machine (BORRADOR → EN_NEGOCIACION → EN_REVISION_JURIDICA → EN_REVISION_FINANCIERA → VISADO_INTERNO → FIRMADO_GORE → FIRMADO_CONTRAPARTE → VIGENTE/TDR_PENDIENTE → VENCIDO/TERMINADO/RESCILIADO). Related: `agreement_installment` (payment schedule with status tracking — full CRUD: create via inline form in drawer, register payment inline). Drawer shows clickable IPR link. Orphan filter: `GET /api/convenios?orphan=true` returns conventions without linked IPR.
- **progress_report**: Periodic physical/financial progress reports per IPR. Create via `POST /api/ipr/{id}/avances`, list via `GET /api/ipr/{id}/avances`. Auto-incremented `report_number`.
- **ipr_party**: Organizations with typed roles (9 roles: POSTULANTE, FORMULADOR, EJECUTOR, COFINANCIADOR, UNIDAD_TECNICA, FISCALIZADOR, BENEFICIARIO, MANDANTE, MANDATARIO). CRUD via `GET/POST /api/ipr/{id}/partes`, `DELETE /api/ipr/{id}/partes/{party_id}`. UNIQUE constraint `uq_ipr_party_role` on (ipr_id, organization_id, party_role_id). Admin-only write.
- **ipr_territory**: Territory associations with impact types (4: UBICACION, IMPACTO_DIRECTO, IMPACTO_INDIRECTO, ZONA_INFLUENCIA). CRUD via `GET/POST /api/ipr/{id}/territorio`, `DELETE /api/ipr/{id}/territorio/{id}`. UNIQUE constraint `uq_ipr_territory_impact`. Admin-only write.
- **ipr_milestone**: Project lifecycle milestones (13 types) with planned/actual dates and auto-computed `deviation_days` (GENERATED column). CRUD via `GET/POST /api/ipr/{id}/hitos`, `PATCH /api/ipr/{id}/hitos/{id}` (mark completed). Admin-only write.
- **crisis_meeting**: Crisis meetings module using existing `core.committee` + `core.session` + `core.crisis_meeting` + `core.minute` + `core.session_agreement` tables. Full lifecycle: PROGRAMADA → EN_CURSO → FINALIZADA. Auto-suggestions from critical alerts, overdue commitments, open problems. Topic BIP badges are clickable links to IPR detail.

Cross-entity navigation (bidirectional):
- **IPR → satellites**: IPR detail page has 9 tabs: Compromisos, Problemas, Alertas, Convenios, CDPs, Avances, Partes, Territorio, Hitos — each loads filtered data lazily
- **Satellites → IPR**: Drawers in compromisos, problemas, convenios, presupuesto pages show clickable `ipr_codigo_bip` that navigates to `/ipr/{id}`. Reunion topic BIP badges also link to IPR.
- **IPR list filters**: `?assignee_id=X` filters by assigned user (available for all roles)

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

## ETL Pipeline

Scripts in `api/scripts/etl/` for ingesting legacy CSV/XLSX data into `core.*` tables.

```bash
# Run inside API container:
docker compose exec api python -m scripts.etl.enrich_persons --dry-run
docker compose exec api python -m scripts.etl.enrich_persons --nomina /app/data/etl/funcionarios/NOMINA.xlsx
docker compose exec api python -m scripts.etl.enrich_persons --rut-only --nomina /path/to/NOMINA.xlsx

# Copy data files to container first:
docker cp /local/path/file.csv goreos_api:/app/data/etl/funcionarios/
```

Key modules:
- `api/scripts/etl/common.py` — shared utilities: DB session, CSV reader (auto-encoding/delimiter, `skip_rows` param), name parser, FK resolvers with cache, RUT normalizer, batch commit, stats tracking
- `api/scripts/etl/enrich_persons.py` — Phase 1: enrich `core.person` from Funcionarios CSVs (metadata) + NOMINA xlsx (RUT)
- `api/scripts/etl/load_documents.py` — Phase 2: load PARTES CSVs → `core.document` (~10.5K docs)
- `api/scripts/etl/load_admin_acts.py` — Phase 2C: project documents → `core.administrative_act` + `core.resolution` + `core.rendition`. Rendition linking uses coproduct: IPR BIP code (primary, 52%) or crosswalk→agreement (0.25%). 1,234 renditions materialized.
- `api/scripts/etl/enrich_agreements.py` — Phase 3: enrich `core.agreement` from 3 CONVENIOS CSVs (536 rows). Updates CGR outcome, technical referent, signed date + rich metadata. 476 agreements enriched.
- `api/scripts/etl/load_fril.py` — Phase 4: FRIL CSVs (173 rows) → `core.ipr_territory` (UBICACION). Includes TREHUACO→Treguaco alias.
- `api/scripts/etl/load_modifications.py` — Phase 5: 24 budget modification CSVs → `txn.event` (MODIFICACION). Custom positional parser for institutional-header CSVs. 211 events.
- `api/scripts/etl/load_idis.py` — Phase 6: IDIS ANÁLISIS.csv (2,605 rows) → `core.ipr_territory` + `core.ipr_party` (UNIDAD_TECNICA, FORMULADOR). 2,383 records. Only uses ANÁLISIS — CONSOLIDADO/MASTER have corruption.

All scripts support `--dry-run`, `--limit N`, `--verbose`. Idempotent (JSONB merge, ON CONFLICT, skip-if-exists).

```bash
# Phase 2: load PARTES documents
docker cp docs/legacy/etl/sources/partes/originales/ goreos_api:/app/data/etl/partes/
docker compose exec api python -m scripts.etl.load_documents --dry-run
docker compose exec api python -m scripts.etl.load_documents --source RECIBIDOS  # single source
docker compose exec api python -m scripts.etl.load_documents                      # all sources
```

CSV sources live in `docs/legacy/etl/sources/` (8 domains, 14K+ records). Architecture doc: `docs/ETL_ARCHITECTURE_v1.0.md`.

## Key References

- `model/model_goreos/sql/goreos_ddl.sql` — DDL (78 tables), ontological mappings in lines 21-37
- `model/model_goreos/sql/goreos_seed.sql` — 90+ category schemes
- `model/model_goreos/sql/goreos_seed_demo_ciclo2.sql` — demo data for budget + agreements
- `model/model_goreos/sql/goreos_migration_confrontacion.sql` — categorical data migration (org types, hierarchy, agreement states, roles, legacy cleanup)
- `model/model_goreos/sql/goreos_rollback_confrontacion.sql` — rollback for above migration
- `model/model_goreos/sql/goreos_migration_rendition_coproduct.sql` — relax rendition FKs: nullable agreement_id/renderer_id, add ipr_id FK, CHECK (agreement OR ipr)
- `model/model_goreos/sql/goreos_rollback_rendition_coproduct.sql` — rollback for rendition coproduct migration
- `model/model_goreos/docs/GOREOS_ERD_v3.md` — ERD + data dictionary
- `model/GLOSARIO.yml` — 244 ontological terms (Gist 14.0 + GNUB + TDE)
- `docs/plans/2026-02-24-dgi-ui-ux-design.md` — DGI UI/UX design document
- `docs/GORE_OS_Testing_Ciclo3.md` — Testing document with all features, credentials, and test cases
- `architecture/Omega_GORE_OS_Definition_v3.0.0.md` — system specification
- `docs/ETL_ARCHITECTURE_v1.0.md` — ETL pipeline design (8 domains, execution order, mappings)
- `model/model_goreos/sql/goreos_seed_etl_phase2.sql` — seed `document_channel` scheme (prerequisite for Phase 2)

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
17. **Large dataset selects**: `core.ipr` has 3,600+ rows, `core.organization` has 3,300+ rows. Never load all records into a `<Select>`. Use `ComboboxAsync` for IPR fields (server-side search via `GET /api/catalogs/iprs?search=TERM`). For divisions, `GET /api/catalogs/divisions` returns only ~9 entries (DIVISION + GORE type) — any query that joins `core.organization` without filtering `org_type_id` will return all organizations. Note: after the confrontation migration, many internal orgs were reclassified to STAFF_UNIT, DEPARTAMENTO, UNIDAD, ADVISORY_BODY — these are intentionally excluded from the divisions catalog.
18. **API error messages**: `ApiClient` in `api.ts` automatically extracts `.detail` from FastAPI JSON error responses. Backend `HTTPException(detail="...")` strings reach frontend `catch (err)` blocks as clean text — no need to parse JSON in component code.
19. **DDL circular dependencies**: `goreos_ddl.sql` defines `fn_validate_category_scheme` AFTER the tables that use it in CHECK constraints, and `core.person` references `core.position` which is defined later. Never apply DDL directly to a fresh database — use `pg_dump --schema-only` from `goreos_model` instead.
20. **Test user seed**: Test users (person + user records) are NOT in any standard seed SQL file. They live in `model/model_goreos/sql/goreos_seed_users.sql` (uses subqueries for FK resolution). The setup script `scripts/setup_test_db.sh` handles the full test DB creation.
21. **Confrontation migration**: `goreos_migration_confrontacion.sql` is a data-only migration (no DDL changes). It expanded org_type (2 new), reclassified 16 orgs, built 3-level hierarchy, added 3 agreement states, added 5 system roles, and soft-deleted 6 legacy duplicates. Rollback via `goreos_rollback_confrontacion.sql`. Both are idempotent (ON CONFLICT / WHERE guards).
22. **Cross-entity navigation pattern**: When a list item references another entity (e.g., `ipr_codigo_bip` in compromisos), always include the FK `ipr_id` in both the Pydantic schema and the SQL SELECT so the frontend can build a clickable link. The standard UI pattern is `<button onClick={() => router.push('/ipr/${id}')}>{codigo_bip}</button>` with `text-blue-600 hover:underline` styling. Close the drawer first (`setSelectedId(null)`) before navigating.
23. **CDPs by IPR endpoint**: `GET /api/presupuesto/cdps-por-ipr/{ipr_id}` returns `list[BudgetCommitmentItem]` — all budget commitments linked to an IPR. This route is defined BEFORE `/{presupuesto_id}` in the router to avoid path conflicts.
24. **Convenio installment CRUD**: `POST /api/convenios/{id}/cuotas` requires `installment_number`, `amount`, `due_date`, `payment_status_id`. `PATCH /api/convenios/{id}/cuotas/{cuota_id}` accepts `payment_status_id`, `paid_at`, `paid_amount`, `payment_reference`. Frontend uses inline forms within the convenio drawer (no separate page).
25. **DGI initiatives pagination**: `GET /api/dgi/initiatives` accepts optional `page` + `page_size` params. When `page` is provided, returns `{items, total, page, page_size, total_pages}`. When omitted, returns plain array for backward compatibility. Never change the default (unpaginated) behavior — existing DGI Kanban board depends on it.
26. **Catalog endpoints**: `GET /api/catalogs/organizations?search=TERM` for org search (uses `ComboboxAsync`), `GET /api/catalogs/territories` for all 25 territories (small dataset, no search needed). Territory table uses `territory_type_id` FK to `ref.category`, NOT a `territory_level` column.
27. **UNIQUE constraint names in DDL**: `ipr_party` uses `uq_ipr_party_role`, `ipr_territory` uses `uq_ipr_territory_impact`. When catching duplicate errors in FastAPI, check for these exact names in the exception string.
28. **ApiClient.delete()**: The `api.ts` singleton now has a `delete(path)` method for HTTP DELETE. It handles 204 No Content responses correctly (no JSON parsing). Use `await api.delete('/api/...')`.
29. **IPR detail page size**: The page is ~1,200+ lines with 9 tabs. If adding more tabs, consider extracting each tab content to a separate component file.
30. **asyncpg type cast syntax**: In raw SQL with `text()` + asyncpg, do NOT use `:param::jsonb` — asyncpg confuses `::` with parameter syntax. Use `CAST(:param AS jsonb)` instead. Same applies to any type cast after a named parameter.
31. **ETL scripts runtime**: ETL scripts run inside the API container (`docker compose exec api python -m scripts.etl.<module>`). CSVs must be copied to the container first via `docker cp`. Scripts use the container's DB_HOST (`goreos_db`), not `localhost`.
32. **PARTES CSV structural quirks**: Some source files have a garbage first row instead of headers (RECIBIDOS row 0 = `"ENROCADO"`, OFICIOS INTERNOS row 0 = `"}"`). Use `read_csv(path, skip_rows=1)` for these. MEMOS and MEMOS INTERNOS have an unnamed first column (empty string key) — skip it. Always inspect headers before mapping columns from a new PARTES source.
