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
- `api/app/main.py` — app factory, router registration, middleware setup
- `api/app/core/deps.py` — `CurrentUser` dependency (extracts user dict from JWT)
- `api/app/core/security.py` — `OPERATIONAL_ROLES` / `DGI_ROLES` sets, password hashing, JWT
- `api/app/middleware/security.py` — `SecurityHeadersMiddleware` (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy)
- `api/app/routers/` — 19 routers (auth, ipr, compromisos, problemas, alertas, dashboard, catalogs, presupuesto, convenios, admin, reuniones, search, dgi_cockpit, dgi_initiatives, dgi_data, dgi_reports, dgi_cartera, actos, core_sessions)
- `api/app/routers/admin.py` — 18 endpoints: usuarios CRUD + toggle/reset + divisiones CRUD + financing-tracks CRUD + thresholds CRUD + sni-levels CRUD
- `api/app/routers/actos.py` — 5 endpoints: administrative acts CRUD + 7-step state machine + auto-resolution creation
- `api/app/routers/core_sessions.py` — 9 endpoints: CORE sessions CRUD + voting + lifecycle gate F3→F4

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
- `web/src/components/sidebar.tsx` — conditional nav: `operationalNav` (10 items: Inicio, IPR, Compromisos, Problemas, Alertas, Presupuesto, Convenios, Reuniones, Actos, Sesiones CORE) + role-specific items (Mi División for JEFE_DIVISION, Mis Compromisos for ENCARGADO) + `adminOnlyNav` (Usuarios, Divisiones, Umbrales, Niveles SNI for ADMIN_SISTEMA) vs `dgiNav` (7 items: Home, Cartera, Alertas, Rendiciones, Tablero, Datos, Informes) based on `user.population`
- `web/src/app/(app)/layout.tsx` — AppShell wrapper for authenticated routes
- `web/src/app/(app)/dashboard/page.tsx` — detects population, renders operational dashboard or DGI cockpit component per role
- `web/src/lib/format.ts` — shared formatting utilities (es-CL locale): `formatDate`, `formatDateTime`, `formatDateTimeShort`, `formatDateLong`, `formatCLP`, `formatCurrency`. All 21 frontend files import from here — never define local format functions.
- `web/src/components/combobox-async.tsx` — reusable searchable select with server-side search (debounce 300ms, `shouldFilter={false}`). Use for any field with 500+ options (e.g., IPR Asociada). Props: `value`, `onChange`, `searchFn(query) → Promise<ComboboxOption[]>`, `placeholder`.

### Database

**83 tables across 4 schemas** (63 logical + 20 txn partitions):

| Schema | Purpose |
|--------|---------|
| `meta` | Role/Process/Entity/Story atoms (5 tables) |
| `ref`  | Controlled vocabularies via `ref.category` — 93+ schemes + `ref.operational_commitment_type` |
| `core` | Business entities: IPR, Agreement, Budget, User, plus operational (commitment, problem, alert), DGI (indicator, initiative, report, bpmn_model, committee_session, data_source_status), and infrastructure (`financing_track`, `schema_migration`) |
| `txn`  | Event sourcing (partitioned) |

**Category Pattern**: `ref.category(scheme, code, label)` — each FK column points to exactly ONE scheme (Categorical Univocity). Before creating new schemes, check existing ones: `SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;`

**DGI schemes**: `dgi_initiative_status`, `dgi_indicator_dimension`, `dgi_signal`, `dgi_report_type`, `dgi_report_status`, `dgi_bpmn_status`, `dgi_dmaic_phase`, `dgi_session_status`, `dgi_alert_status`, `dgi_decree_status`, `dgi_source_status`

**Governance schemes** (Wave 5): `session_type` (ORDINARIA, EXTRAORDINARIA), `vote_option` (A_FAVOR, EN_CONTRA, ABSTENCION), `quorum_type` (SIMPLE, CALIFICADA)

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

**322 integration tests (318 pass + 4 skip)** against real PostgreSQL (`goreos_test` DB). No mocks — tests exercise real SQL, JWT auth, and business logic.

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

Test modules (28): `test_auth` (12), `test_compromisos` (16), `test_presupuesto` (10), `test_initiatives` (7), `test_problemas` (8), `test_convenios` (12), `test_dashboard` (6), `test_security_readonly` (12), `test_ipr_children` (14), `test_ipr_lifecycle` (6), `test_actos` (12), `test_admin` (11), `test_reuniones` (11), `test_search` (4), `test_catalogs` (8), `test_core_sessions` (10), `test_rendiciones` (5), `test_polyswitch` (14), `test_alertas` (6), `test_dgi_cockpit` (4), `test_dgi_reports` (4), `test_dgi_cartera` (12), `test_concurrency` (5), `test_sisrec` (23), `test_thresholds` (18), `test_track_enforcement` (32), `test_track_rules` (18), `test_ciclo24` (22).

**Test DB setup** (`scripts/setup_test_db.sh`): clones schema via `pg_dump --schema-only` from `goreos_model`, copies all `ref.category` rows via `COPY`, seeds territory + test users. The DDL file has circular dependencies (functions defined after tables that use them), so never apply `goreos_ddl.sql` directly to a fresh DB — always use `pg_dump` from production.

**Test architecture**: `conftest.py` creates a fresh `AsyncSession` per test against `goreos_test`, overrides `get_db` dependency, generates real JWT tokens for 5 roles (admin, regional, jefe, encargado, dgi). The `catalog` fixture pre-fetches common IDs (commitment types, problem types, agreement states, etc.).

**Known issues** (test data pollution — tests don't fully isolate inserted rows):
- `test_initiatives::test_move_to_en_curso` may fail if test DB has accumulated 5+ EN_CURSO initiatives from prior runs (WIP limit 5). Clean with `DELETE FROM core.dgi_initiative WHERE deleted_at IS NULL;` on `goreos_test`.
- `test_sisrec::test_vencidas_endpoint` may fail when stale renditions accumulate in `goreos_test`. Clean with `DELETE FROM core.rendition WHERE created_at > '2026-01-01';` on `goreos_test`.

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

# Run DDL migrations
./scripts/run_migrations.sh [container] [db]  # default: goreos_db goreos_model

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
- **administrative_act**: Institutional acts (DECRETO, RESOLUCION, DECRETO_ALCALDICIO) with 7-step state machine (BORRADOR→EN_REVISION→VISADO→FIRMADO→ENVIADO_CGR→OBSERVADO/TOMADO_RAZON + ANULADO). CRUD via `GET/POST/PATCH /api/actos`, transitions via `GET /api/actos/{id}/transiciones`. Auto-creates `core.resolution` for RESOLUCION type. `signer_id` FK → `meta.role`. CGR tracking via `cgr_number`, `cgr_date`, `cgr_outcome_id`. "Resoluciones" tab in IPR detail shows resolutions linked to IPR.
- **crisis_meeting**: Crisis meetings module using existing `core.committee` + `core.session` + `core.crisis_meeting` + `core.minute` + `core.session_agreement` tables. Full lifecycle: PROGRAMADA → EN_CURSO → FINALIZADA. Auto-suggestions from critical alerts, overdue commitments, open problems. Topic BIP badges are clickable links to IPR detail.

Cross-entity navigation (bidirectional):
- **IPR → satellites**: IPR detail page has 11 tabs: Compromisos, Problemas, Alertas, Convenios, CDPs, Avances, Partes, Territorio, Hitos, Resoluciones, Evaluación — each loads filtered data lazily via extracted tab components
- **Satellites → IPR**: Drawers in compromisos, problemas, convenios, presupuesto pages show clickable `ipr_codigo_bip` that navigates to `/ipr/{id}`. Reunion topic BIP badges also link to IPR.
- **IPR list filters**: `?assignee_id=X` filters by assigned user (available for all roles)

DGI layer:
- **rendition**: Rendiciones de cuentas with multi-role state machine (SISREC). 8 states: PENDIENTE → EN_REVISION_RTF → VISADA_RTF → EN_REVISION_UCR → APROBADA/RECHAZADA, with OBSERVADA loop. Role-based transitions: operativa can initiate/resubmit, DGI can visa/approve/reject. History audit trail via `core.rendition_history` + trigger. SLA: 7d RTF, 2d UCR. `GET /api/dgi/data/rendiciones/vencidas` for overdue. `amount` field for rendered amount.
- **dgi_cartera**: DGI portfolio control — unified view of all IPRs with aggregated data (progress, CDPs, agreements, installments, resolutions, problems, alerts, commitments). Health signal computation (VERDE/AMARILLO/ROJO) via `_compute_health_signal()`. 3 endpoints: `GET /api/dgi/cartera` (paginated with health_signal post-filter), `GET /api/dgi/cartera/resumen` (summary cards), `GET /api/dgi/cartera/cuotas-vencidas` (overdue installments cross-portfolio). Cockpit drill-down: CARTERA_IPR semáforo card links to `/cartera?health_signal=`.
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

6 scripts in `api/scripts/etl/` for ingesting legacy CSV/XLSX → `core.*` tables. All support `--dry-run`, `--limit N`, `--verbose`. Idempotent.

```bash
# Run inside API container (copy CSVs first via docker cp):
docker compose exec api python -m scripts.etl.<module> --dry-run
```

Modules: `enrich_persons` (Phase 1), `load_documents` (Phase 2), `load_admin_acts` (Phase 2C), `enrich_agreements` (Phase 3), `load_fril` (Phase 4), `load_modifications` (Phase 5), `load_idis` (Phase 6). Architecture: `docs/ETL_ARCHITECTURE_v1.0.md`.

## Key References

**Core schema**: `model/model_goreos/sql/goreos_ddl.sql` (DDL), `goreos_seed.sql` (90+ schemes), `model/model_goreos/docs/GOREOS_ERD_v3.md` (ERD + data dictionary), `model/GLOSARIO.yml` (244 ontological terms)

**Specification**: `architecture/Omega_GORE_OS_Definition_v3.0.0.md`, `docs/GORE_OS_Audit_v2.0.md` (472 CQs, 15 HΩ findings)

**Migrations**: All in `model/model_goreos/sql/goreos_migration_*.sql` with matching `goreos_rollback_*.sql`. Tracked in `core.schema_migration`. Runner: `scripts/run_migrations.sh`.

**Docs**: `docs/ONBOARDING.md`, `docs/GORE_OS_Testing_Ciclo3.md`, `docs/ETL_ARCHITECTURE_v1.0.md`, `docs/adr/` (6 ADRs)

## Known Gaps & Coverage

**Coverage**: ~134 API endpoints, 322 tests (318 pass + 4 skip), 28 modules, 17 gate functions in `ipr.py`. HΩ findings: 12/15 implemented, 1 partial, 2 pending. Full audit: `docs/GORE_OS_Audit_v2.0.md`.

**Open gaps**:
- HΩ-02 Parentesco 8% (kinship disqualification — not started)
- HΩ-14 SISREC ciclo completo 13-14d (partial — only RTF 7d + UCR 2d of 8 phases)
- HΩ-15 Budget Cycle Timeline T-1→T→T+1 (not started)
- 3/9 track thresholds pending, 2/8 glosas pending, budget classifier 4/6 levels
- 0 external integrations (ClaveÚnica, PISEE, BIP, SIGFE, CGR)
- 5 system roles with 0 users, IPR `sponsor_division_id`/`assignee_id` = 0% populated

## Critical Rules

1. **Categorical Univocity**: Each FK column → exactly 1 `ref.category` scheme. Never mix dimensions.
2. **Person columns**: Use `names` and `paternal_surname` (NOT `nombre`/`apellido_paterno`). User FK: `system_role_id` (NOT `role_id`).
3. **API consistency**: Operational endpoints use POST for state changes (e.g., `POST /compromisos/{id}/completar`). DGI list endpoints return plain arrays. Paginated endpoints return `{items, total, page, page_size, total_pages}`.
4. **Alert subject_type**: DB stores fully-qualified names: `'core.ipr'`, `'core.operational_commitment'`, `'core.ipr_problem'`, `'core.organization'`. Always use the `core.` prefix in SQL — never the short form.
5. **Docker network**: `goreos_db` is on `visor_model_default` (external). Don't create a separate postgres service unless using `--profile standalone`.
6. **No ORM models**: Backend uses raw SQL with `text()` from SQLAlchemy. All queries go through `db.execute(text("..."), params).mappings()`.
7. **PATCH allowlist**: PATCH endpoints must validate column names against an explicit allowlist. Field names in Pydantic update models must match DB column names exactly.
8. **Demo data convention**: All demo records use `DEMO-` prefix in code/number fields. Never mix demo data with real data. Use `goreos_unseed_demo_ciclo2.sql` to clean.
9. **DGI indicator refresh**: Run `POST /api/dgi/data/indicators/refresh` to recompute semaphore values from real data. Idempotent. TDE dimension has no real data source yet.
10. **Report section edits**: Stored atomically in `metadata` JSONB using `jsonb_set` (not read-modify-write). Auto-populated content is regenerated on each GET; only user edits persist.
11. **Organization table**: `core.organization` does NOT have `is_active` column. Use `deleted_at IS NULL` to check if active. The type FK column is `org_type_id` (NOT `organization_type_id`).
12. **Role restriction pattern**: Use a helper function `_require_roles(user, ...)` called inside the endpoint body. Do NOT use `require_roles()` from `deps.py` as a default parameter value — it conflicts with `CurrentUser` (which is `Annotated[dict, Depends()]`).
13. **Reuniones module**: Uses existing DDL tables (`core.committee`, `core.session`, `core.crisis_meeting`, `core.minute`, `core.session_agreement`, `core.agenda_item_context`). No DDL migration needed. A dedicated crisis committee (code `COMITE-CRISIS`) is auto-created on first use. Sibling module: `core_sessions.py` handles CORE ordinary sessions with voting.
14. **Dashboard endpoints**: Role-specific dashboards: `GET /api/dashboard` (base, role-aware), `GET /api/dashboard/ejecutivo` (ADMIN with division breakdown), `GET /api/dashboard/mi-division` (JEFE_DIVISION team load), `GET /api/dashboard/mis-compromisos` (ENCARGADO grouped commitments).
15. **Admin module**: `GET/POST/PATCH /api/admin/usuarios`, `POST /api/admin/usuarios/{id}/toggle-activo`, `POST /api/admin/usuarios/{id}/reset-password`, `GET/POST/PATCH /api/admin/divisiones`, `GET/POST/PATCH /api/admin/financing-tracks`, `GET/POST/PATCH /api/admin/thresholds`, `GET/POST/PATCH /api/admin/sni-levels`. All restricted to ADMIN_SISTEMA.
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
29. **asyncpg type cast syntax**: In raw SQL with `text()` + asyncpg, do NOT use `:param::jsonb` — asyncpg confuses `::` with parameter syntax. Use `CAST(:param AS jsonb)` instead.
30. **ETL scripts runtime**: ETL scripts run inside the API container (`docker compose exec api python -m scripts.etl.<module>`). CSVs must be copied to the container first via `docker cp`. Scripts use the container's DB_HOST (`goreos_db`), not `localhost`.
31. **PARTES CSV structural quirks**: Some source files have a garbage first row instead of headers (RECIBIDOS row 0 = `"ENROCADO"`, OFICIOS INTERNOS row 0 = `"}"`). Use `read_csv(path, skip_rows=1)` for these. Always inspect headers before mapping columns.
32. **Actos administrativos**: 7-step state machine: BORRADOR→EN_REVISION→VISADO→FIRMADO→ENVIADO_CGR→OBSERVADO/TOMADO_RAZON + ANULADO cross-cutting. Split PATCH allowlist (`_ACT_FIELD_ALLOWLIST` + `_RES_FIELDS`). Auto-creates `core.resolution` for RESOLUCION type. `signer_id` FK → `meta.role` (NOT `core.person`). DB trigger validates transitions — ensure ANULADO in `valid_transitions` for all non-terminal states.
33. **IPR detail page**: 11 tabs (Compromisos, Problemas, Alertas, Convenios, CDPs, Avances, Partes, Territorio, Hitos, Resoluciones, Evaluación). 10 tab components in `web/src/app/(app)/ipr/components/tab-*.tsx` — self-contained with own state/fetch. Main page (~640 lines) retains hero, stepper, transitions, edit/assignee drawers.
34. **Shared format utilities**: All date/currency formatting MUST use `import { formatDate, formatCLP, ... } from "@/lib/format"`. Never define local format functions.
35. **Advisory locks on code generators**: All sequential code generators use `pg_advisory_xact_lock(hashtext('entity_code'))` before `SELECT MAX(...)` to prevent race conditions.
36. **CORE sessions**: `core_sessions.py` uses committee `CONSEJO-REGIONAL` (auto-created). Quorum: SIMPLE=9/16, CALIFICADA=11/16. Gate F3→F4: IPRs >7.000 UTM require CORE approval.
37. **Security**: `SecurityHeadersMiddleware` (4 headers), brute-force lockout (5 attempts → 15 min lock, HTTP 429), JWT secret validation rejects default key when `ENV != "development"`.
38. **Financing tracks**: `core.financing_track` table replaces hardcoded `TRACK_CONFIG` dict. Admin CRUD via `/api/admin/financing-tracks`. `_get_track_config()` loads from DB with caching.
39. **Migration tracking**: `core.schema_migration` table. Runner: `./scripts/run_migrations.sh [container] [db]`. New migrations must be registered in the script.
40. **SISREC workflow**: 8-state rendition machine with role-based transitions. `_RENDICION_TRANSITIONS` + `_RENDICION_TRANSITION_ROLES` maps. Operativa initiates/resubmits, DGI visas/approves/rejects. `core.rendition_history` trigger for audit. SLA 4 states: RTF 7d, VISADA_RTF 1d, UCR 2d, OBSERVADA 15d. `GET /rendiciones/{id}/ciclo` returns phase timeline with per-phase SLA tracking. Art. 18: `convenios.py` checks renditions on cuota payment updates.
41. **Financial thresholds**: `core.financial_threshold` (10 rows: 4 UTM + 5 glosa% + UTM_VALUE). Helpers: `_get_utm_value(db)`, `_get_threshold(code, db)`, `_check_utm_threshold(ipr_id, code, db)`.
42. **Glosa rules**: `check_glosa_rules(ipr_id, db)` evaluates 5 glosa limits + `_check_glosa03_prohibition()` blocks FNDR→PERSONAL. Integrated at F3→F4.
43. **Budget classifier 4-level**: List endpoint accepts `item`, `allocation`, `program_type` filters. Levels 1-2 (Partida, Capítulo) are institutional constants.
44. **Track enforcement framework**: `_check_track_amount_gates()` reads `financing_track.thresholds` JSONB. Supports: `max_utm`, `min_clp`, `puntaje_min` (F2→F3), `cgr_res30_utm`, `licitacion_max_days` (F3→F4), `sisrec_mandatory_utm` (F4→F5), `core_approval` (overrides universal CORE). `_get_ipr_monto()` reads `metadata->>'monto_total'`.
45. **Evaluation schema**: `numeric_score` NUMERIC(5,2) on `evaluation_assignment` (FRPD puntaje gate). `rank_position`, `rank_total`, `convocatoria_code` for competitive mechanisms. `core.sni_level_config` (4 levels, admin CRUD via `/api/admin/sni-levels`).
46. **Track gate functions** (all in `ipr.py`, called by `_evaluate_phase_gates()`):
    - **FRIL**: `_check_fril_max_per_comuna` (F0→F1, max 5/territory, A2/A3 exempt), `_check_fril_fraccionamiento` (F1→F2, same executor+territory+±90d), `_check_fril_tender_deadline` (F3→F4, LICITACION milestone within deadline)
    - **SNI**: `_check_sni_proporcionalidad` (F1→F2, 4 eval levels by UTM), `_check_rs_vigencia` (F3→F4, eval expiry per `rs_validity_years`)
    - **C33**: `_check_c33_conservation` (F1→F2, conservation/reposition ratio, informational)
    - **SUBV8**: `_check_pagare_notarial` (F2→F3, ≥100% monto, ≥18mo), `_check_directorio_certificate` (F2→F3, cert freshness), `_check_morosos_sisrec` (F3→F4+F4→F5, executor overdue renditions), `_check_ranking_persistence` (F2→F3, informational)
    - **ALL**: `_check_evaluation_type_match` (F2→F3, informational), `_check_glosa06_single_purpose` (F1→F2, single MML purpose)
47. **CDP creation**: `POST /api/presupuesto/{id}/cdps` creates a budget commitment with advisory-locked sequential number (`CDP-{year}-{seq:04d}`). Validates `amount ≤ available balance` (current - committed). Auto-sets status to EMITIDO. Updates `committed_amount` on the program. Schema: `BudgetCommitmentCreate(amount, description?, ipr_id?, agreement_id?)`.
48. **Bulk cuotas**: `POST /api/convenios/{id}/cuotas/bulk` generates N installments. Schema: `BulkCuotaRequest(total_amount, num_installments, start_date, frequency_months=1)`. Distributes evenly with remainder on first cuota. Auto-increments from max existing `installment_number`. Route registered BEFORE `/{id}/cuotas` to avoid path conflicts. `_add_months()` helper uses `calendar.monthrange` for end-of-month safety.
49. **Rendition table schema**: `core.rendition` DDL has only `agreement_id` (NOT NULL), `renderer_id` (NOT NULL), `state_id`, `period_start/end`, `submitted_at`. Columns `amount` and `ipr_id` were added by migrations (`wave10_sisrec`, `rendition_coproduct`). Table has NO `code` column — use `LEFT(r.id::text, 8)` for display identifiers.
50. **Responsive with Radix portals**: `DrawerPanel` (Radix Sheet) renders via portals outside the DOM tree — CSS `display:none` on parent does NOT prevent the Sheet from opening. Use `window.matchMedia` with `isMobile` state to conditionally render the Sheet component. See `/datos/page.tsx` for reference.
