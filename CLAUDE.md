# CLAUDE.md

## Project Overview

GORE_OS: institutional OS for GORE Ñuble (Chile). Two populations on shared PostgreSQL:

- **Operativa** (ADMIN_SISTEMA, ADMIN_REGIONAL, JEFE_DIVISION, ENCARGADO): IPR crisis — commitments, problems, alerts, budgets, agreements.
- **DGI** (JEFE_DGI, ESP_CONTROL_GESTION, ESP_PROCESOS, ESP_TD): Indicators, data analysis, auto-reports, improvement initiatives.

Single login → role detection → routing to appropriate sidebar/dashboard.

## Quick Start

```bash
docker compose up -d api web                       # Start (assumes goreos_db running)
docker compose --profile standalone up -d           # With standalone PostgreSQL
curl http://localhost:8000/api/health               # Verify API
curl -I http://localhost:3000                       # Verify Web (307→/login)

# Demo data (DEMO- prefix)
docker exec -i goreos_db psql -U goreos -d goreos_model < model/model_goreos/sql/goreos_seed_demo_ciclo2.sql    # Load
docker exec -i goreos_db psql -U goreos -d goreos_model < model/model_goreos/sql/goreos_unseed_demo_ciclo2.sql  # Remove

# DGI indicator refresh
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -d "username=jefe.dgi@goreos.cl&password=admin123" \
  -H "Content-Type: application/x-www-form-urlencoded" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
curl -s -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/dgi/data/indicators/refresh

docker exec goreos_db psql -U goreos -d goreos_model    # DB shell
docker compose logs -f api                               # Logs
cd web && npx next build                                 # Frontend build
cd web && npx eslint src/                                # Frontend lint
./scripts/run_migrations.sh [container] [db]             # Migrations (default: goreos_db goreos_model)
open http://localhost:8000/api/docs                       # Swagger UI
```

## Architecture

Next.js 16 (:3000, `web/`) → FastAPI (:8000, `api/`) → PostgreSQL 16 (`goreos_db`, network `visor_model_default` external)

### Backend (`api/`)

FastAPI + uvicorn (hot-reload). SQLAlchemy async + asyncpg — **raw SQL via `text()`, no ORM**: `db.execute(text("..."), params).mappings()`. JWT (python-jose) + bcrypt. Pydantic v2 (`api/app/schemas/`). Config: pydantic-settings (`api/app/core/config.py`).

Key files:
- `main.py` — app factory, router registration, middleware
- `core/deps.py` — `CurrentUser` dependency (user dict from JWT)
- `core/security.py` — `OPERATIONAL_ROLES`/`DGI_ROLES` sets, hashing, JWT
- `middleware/security.py` — `SecurityHeadersMiddleware` (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection, Referrer-Policy)
- `core/audit.py` — `record_event()` → txn.event (10 event_type codes, 15 integration points across 5 routers)
- `routers/` — 28 routers, ~282 endpoints. Notable: actos (7-step FSM), core_sessions (voting + F3→F4), dgi_services (12 endpoints, static paths BEFORE `/{service_id}`), risk (8 endpoints), command_center (2 endpoints)

Conventions: `/api/` prefix. Paginated → `{items, total, page, page_size, total_pages}`. DGI lists → plain arrays (initiatives: optional pagination via `?page=1&page_size=N`). Dashboard/cockpit → role-aware. PATCH → allowlisted columns matching DB names. Person columns: `names`, `paternal_surname` (NOT `nombre`/`apellido_paterno`). User FK: `system_role_id` (NOT `role_id`).

### Frontend (`web/`)

Next.js 16 (App Router, Turbopack), TypeScript, TailwindCSS v4, shadcn/ui (Radix), lucide-react. State: React Context (`useAuth`) + `useSearchParams`.

- `lib/api.ts` — `ApiClient` singleton (`get/post/patch/delete<T>`). Token in localStorage (`goreos_token`). Auto-redirect on 401. Auto-extracts `.detail` from FastAPI errors. `delete()` handles 204.
- `lib/auth.tsx` — `AuthProvider`, `useAuth()` → `{user, loading, login, logout}`
- `lib/format.ts` — `formatDate`, `formatDateTime`, `formatDateTimeShort`, `formatDateLong`, `formatCLP`, `formatCurrency` (es-CL). **All files import from here — never define local format functions.**
- `types/index.ts` — all interfaces. `User.population` (`"operativa"|"dgi"`) drives routing.
- `components/sidebar.tsx` — 5-7 collapsible `NavSection` per population (localStorage-persisted). Cross-population: Servicios visible in operativa.
- `components/combobox-async.tsx` — server-side searchable select (debounce 300ms, `shouldFilter={false}`). **Use for 500+ option fields.** Props: `value`, `onChange`, `searchFn`, `placeholder`.
- `components/page-header.tsx` — shared header (`title`, `description?`, `actions?`, `breadcrumbs?`, `accentColor?`). **All list pages must use this.** Domain accents: indigo(IPR), amber(compromisos), emerald(finanzas), violet(institucional), rose(riesgos), cyan(DGI), teal(servicios).
- `components/empty-state.tsx` — `compact` for tabs/inline, normal for full-page. **All empty states must use this.**
- `components/confirm-dialog.tsx` — AlertDialog for destructive actions. **Always use for delete/revert.**
- `components/page-guard.tsx` — wrapper: auth check + role gate + loading skeleton + error state
- `components/breadcrumb.tsx` — navigable breadcrumbs, used in 18 detail/create pages
- `components/progress-cell.tsx` — inline progress bar (green ≥70%, amber ≥40%, red <40%)
- `components/deadline-cell.tsx` — date + semáforo color (red overdue, amber ≤7d)
- `components/detail-page-layout.tsx` — opt-in wrapper: breadcrumbs + hero + stepper + transition panel
- `hooks/use-tab-param.ts` — sync Radix Tabs value with `?tab=` URL search param

### Database

**120 tables across 4 schemas** (92 core + 5 meta + 3 ref + 20 txn partitions):

| Schema | Purpose |
|--------|---------|
| `meta` | Role/Process/Entity/Story atoms (5) |
| `ref`  | Controlled vocabularies: `ref.category(scheme, code, label)` — 105 schemes + `ref.operational_commitment_type` |
| `core` | Business entities — 80 tables |
| `txn`  | Event sourcing (partitioned) |

**Category Pattern**: each FK → exactly ONE scheme (Categorical Univocity). **100% coverage**: 98 CHECK constraints + 19 state transition triggers + 6 history/timing triggers. 0 unprotected FK→ref.category. Check before creating: `SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;`

**Org types** (14): Internal: GORE(1), DIVISION(8), DEPARTAMENTO(6), UNIDAD(8), STAFF_UNIT(7), ADVISORY_BODY(3). External: MUNICIPALIDAD, SERVICIO, MINISTERIO, UNIVERSIDAD, ONG, EMPRESA, ORG_COMUNITARIA, COMUNITARIA. Hierarchy 3-level via `parent_id`.

**System roles** (16): GOBERNADOR(0), ADMIN_SISTEMA(1), ADMIN_REGIONAL(2), JEFE_DIVISION(3), ENCARGADO(4), JEFE_DGI(5), ESP_CONTROL_GESTION(6), ESP_PROCESOS(7), ESP_TD(8), CONSEJERO_REGIONAL(9), SECRETARIO_EJECUTIVO(10), JEFE_DEPARTAMENTO(11), JEFE_UNIDAD(12), ANALISTA(13), RTF(14), ASESOR_JURIDICO(15).

## Test Users

All passwords: `admin123`. All `@goreos.cl`.

| Email | Role | Pop | Div |
|-------|------|-----|-----|
| admin | ADMIN_SISTEMA | op | — |
| regional | ADMIN_REGIONAL | op | — |
| gobernador | GOBERNADOR | op | — |
| secretario.core | SECRETARIO_EJECUTIVO | op | — |
| consejero1, consejero2 | CONSEJERO_REGIONAL | op | — |
| analista.dipir | ANALISTA | op | DIPIR |
| analista.diplade | ANALISTA | op | DIPLADE |
| rtf.daf | RTF | op | DAF |
| juridico | ASESOR_JURIDICO | op | — |
| jefe.daf | JEFE_DIVISION | op | DAF |
| jefe.dideso | JEFE_DIVISION | op | DIDESO |
| jefe.difoi | JEFE_DIVISION | op | DIFOI |
| jefe.diiap | JEFE_DIVISION | op | DIIAP |
| jefe.dipir | JEFE_DIVISION | op | DIPIR |
| jefe.diplade | JEFE_DIVISION | op | DIPLADE |
| jefe.dit | JEFE_DIVISION | op | DIT |
| jefe.finanzas | JEFE_DEPARTAMENTO | op | DAF |
| jefe.ucr | JEFE_UNIDAD | op | DAF |
| encargado.daf | ENCARGADO | op | DAF |
| jefe.dgi | JEFE_DGI | dgi | DIDECO |
| control.gestion | ESP_CONTROL_GESTION | dgi | DIDECO |
| procesos | ESP_PROCESOS | dgi | DIDECO |
| td | ESP_TD | dgi | DIDECO |

## Testing

**610 integration tests (47 modules)** against real PostgreSQL (`goreos_test`). No mocks.

```bash
./scripts/setup_test_db.sh                                          # Setup test DB
docker compose exec api pytest -v                                   # Full suite
docker compose exec api pytest tests/test_compromisos.py -v         # Single module
docker compose exec api pytest tests/test_auth.py::test_login_success -v  # Single test
docker compose exec api pip install pytest pytest-asyncio httpx     # Install deps (if rebuilt)
```

**Test DB** (`scripts/setup_test_db.sh`): `pg_dump --schema-only` from `goreos_model` + `COPY ref.category` + territory + test users. Never apply `goreos_ddl.sql` directly (circular deps). Test users live in `goreos_seed_users.sql`.

**conftest.py**: fresh `AsyncSession` per test, overrides `get_db`, real JWT for 8 roles (admin, regional, jefe, encargado, dgi, analista, rtf, juridico). `catalog` fixture pre-fetches common IDs.

**Known issues** (test data pollution):
- `test_initiatives::test_move_to_en_curso` — WIP limit. Clean: `DELETE FROM core.dgi_initiative WHERE deleted_at IS NULL;`
- `test_sisrec::test_vencidas_endpoint` — stale renditions. Clean: `DELETE FROM core.rendition WHERE created_at > '2026-01-01';`

DGI schemes NOT in `goreos_seed.sql` — only in `goreos_model`, copied to `goreos_test` via COPY. Insert new DGI schemes into production first.

## Domain Model

Central: **IPR** — polymorphic (8 types: INFRAESTRUCTURA, EQUIPAMIENTO, CONSERVACION, TRANSFERENCIA, SUBSIDIO, ESTUDIO, PROGRAMA_SOCIAL, PROGRAMA_8PCT).

### Operational Layer

- **operational_commitment**: PENDIENTE→EN_PROGRESO→COMPLETADO→VERIFICADO. `commitment_history`. CRUD `/compromisos/nuevo` + inline `IprCompromisoDrawer`.
- **ipr_problem**: ABIERTO→EN_GESTION→RESUELTO|CERRADO_SIN_RESOLVER. Typed (TECNICO, FINANCIERO, LEGAL…).
- **alert**: Severity CRITICO/ALTO/ATENCION/INFO. `subject_type` polymorphic (`core.ipr`, `core.operational_commitment`, `core.ipr_problem`, `core.agreement`).
- **budget_program**: Per division, fiscal year. Execution chain: initial→current→committed→accrued→paid. Related: `budget_carryover`, `budget_commitment` (CDPs). CDPs by IPR: `GET /api/presupuesto/cdps-por-ipr/{ipr_id}`.
- **agreement**: 13-state FSM (BORRADOR→…→VIGENTE/TDR_PENDIENTE→VENCIDO/TERMINADO/RESCILIADO). `agreement_installment` (CRUD inline). Orphan filter: `?orphan=true`.
- **progress_report**: Per IPR. `POST/GET /api/ipr/{id}/avances`. Auto-incremented `report_number`.
- **ipr_party**: 9 roles. UNIQUE `uq_ipr_party_role`. NO `person_id` — uses `organization_id` + `party_role_id` + `contact_person`.
- **ipr_territory**: 4 impact types. UNIQUE `uq_ipr_territory_impact`. `territory_type_id` FK (NOT `territory_level`).
- **ipr_milestone**: 13 types, planned/actual dates, auto `deviation_days` (GENERATED).
- **administrative_act**: DECRETO/RESOLUCION/DECRETO_ALCALDICIO. 7-step FSM. `signer_id` FK→`meta.role` (NOT `core.person`). Split PATCH allowlist. DB trigger validates transitions.
- **crisis_meeting**: `core.committee`+`core.session`+`core.crisis_meeting`+`core.minute`+`core.session_agreement`. FSM: PROGRAMADA→EN_CURSO→FINALIZADA. Crisis committee `COMITE-CRISIS` auto-created.

### Cross-entity Navigation

- **IPR → satellites**: 16 tabs in `tab-*.tsx` (Compromisos, Problemas, Alertas, Convenios, CDPs, Avances, Partes, Territorio, Hitos, Resoluciones, Evaluación, Parentesco, Admisibilidad, Modificaciones, Cierre, Ex-Post).
- **Satellites → IPR**: Drawers show clickable `ipr_codigo_bip` → `/ipr/{id}`. Pattern: include `ipr_id` in schema+SQL, `text-blue-600 hover:underline`, close drawer before navigating.

### DGI Layer

- **SISREC renditions**: 8-state FSM. SLA: RTF 7d, VISADA_RTF 1d, UCR 2d, OBSERVADA 15d. `phase_entered_at` for SLA clock. NO `code` column — use `LEFT(r.id::text, 8)`. `COALESCE(phase_entered_at, updated_at)` in queries. Art. 18: `convenios.py` checks renditions on cuota payments.
- **DGI Data**: `dgi_indicator` (5 dimensions, lifecycle VIGENTE/DEPRECADO/ARCHIVADO/PROPUESTO, refresh idempotent), `dgi_cartera` (IPR portfolio + health VERDE/AMARILLO/ROJO), `dgi_report` (4 types, atomic `jsonb_set`), `dgi_decree` (DS7-DS12, Ley 21.180).
- **DGI Improvement**: `dgi_initiative` (Kanban, WIP EN_CURSO:5/REVISION:2, `sort_order` @dnd-kit, DMAIC `jsonb_set`, **5th phase=VERIFY not CONTROL**, `trg_initiative_timing`), `dgi_process` (hub + 6 satellites, bridges Process→Opportunity→Initiative), `dgi_bottleneck_investigation` (6-state, 3 detection queries).
- **DGI Coordination**: `dgi_ar_decision` (4 types, `source_session_id` crisis bridge), `dgi_escalation` (4 levels, auto-code ESC-YYYY-NNNN, auto-alert), `dgi_service`+`dgi_service_request`+`dgi_sla` (catalog visible all populations, any user creates requests, DGI manages), `dgi_td_sessions` (COMITE-TD, no voting), `calendar` (UNION ALL 5 sources).
- **Cross-cutting**: `risk` (6-state FSM, RSK-NNNN, auto-alert ALTA/MUY_ALTA, role scoping: ENCARGADO→own, JEFE→division, ADMIN→all), `command_center` (6 parallel queries + timeline, 4 admin/exec roles).

## Demo Data

`DEMO-` prefix in all codes. Seeds: `goreos_seed_demo_ciclo2.sql`, `goreos_seed_demo_wave_b.sql`, `goreos_seed_demo_wave_e.sql`. Unseed scripts remove DEMO- only. FKs use subqueries (not hardcoded UUIDs).

## ETL Pipeline

6 scripts in `api/scripts/etl/`: `enrich_persons`, `load_documents`, `load_admin_acts`, `enrich_agreements`, `load_fril`, `load_modifications`, `load_idis`. All `--dry-run`, `--limit N`, `--verbose`. Idempotent. Run inside API container after `docker cp` CSVs.

## Key References

- **Schema**: `model/model_goreos/sql/goreos_ddl.sql`, `goreos_seed.sql`, `model/model_goreos/docs/GOREOS_ERD_v3.md`, `model/GLOSARIO.yml` (244 terms)
- **Spec**: `architecture/Omega_GORE_OS_Definition_v3.0.0.md`, `docs/GORE_OS_Audit_v2.0.md` (472 CQs, 15 HΩ)
- **Migrations**: `goreos_migration_*.sql` + `goreos_rollback_*.sql`. Tracked in `core.schema_migration`. Runner: `scripts/run_migrations.sh`.
- **Docs**: `docs/ONBOARDING.md`, `docs/GORE_OS_Testing_Ciclo3.md`, `docs/ETL_ARCHITECTURE_v1.0.md`, `docs/adr/` (8 ADRs)

## Critical Rules

### DB Naming & Schema

1. **Categorical Univocity**: Each FK→1 `ref.category` scheme. Never mix. 100% CHECK coverage.
2. **Column naming traps**: Person: `names`, `paternal_surname` (NOT `nombre`/`apellido_paterno`). User FK: `system_role_id` (NOT `role_id`). Org: `org_type_id` (NOT `organization_type_id`), NO `is_active` → `deleted_at IS NULL`. ipr_party: NO `person_id` → uses `organization_id` + `party_role_id` + `contact_person`. ITO via code `ITO`.
3. **Alerts**: `subject_type` fully-qualified (`'core.ipr'`, etc.). `alert_type_id` NOT NULL (scheme `alert_type`, 13 codes).
4. **UNIQUE constraints**: `ipr_party`→`uq_ipr_party_role`, `ipr_territory`→`uq_ipr_territory_impact`.
5. **asyncpg**: NO `:param::jsonb` → `CAST(:param AS jsonb)`. Rejects date strings → parse with `date.fromisoformat()`. Use `datetime` for `timestamptz`.
6. **Advisory locks**: All code generators: `pg_advisory_xact_lock(hashtext('entity_code'))` before `SELECT MAX(...)`.
7. **DDL**: Never apply `goreos_ddl.sql` to fresh DB — `pg_dump --schema-only` from `goreos_model`.
8. **DB trigger errors → HTTP 409**: Catch `DBAPIError`, check `"Transición de estado inválida"`, `await db.rollback()`, return 409.
9. **schema_migration**: Columns `(id, filename, applied_at, checksum, applied_by)`. `ON CONFLICT (filename) DO NOTHING`. NOT `version`/`description`.

### API Patterns

10. **PATCH allowlist**: Validate columns against explicit allowlist. Pydantic field names must match DB columns exactly.
11. **Role restriction**: Use `_require_roles(user, ...)` inside endpoint body. Do NOT use as default param — conflicts with `CurrentUser`.
12. **DGI initiatives pagination**: Optional `page`+`page_size`. With→paginated. Without→plain array. **Never change** — Kanban depends on it.
13. **Error messages**: `ApiClient` auto-extracts `.detail`. Backend `HTTPException(detail="...")` reaches frontend as clean text.
14. **Cross-entity navigation**: Include FK `ipr_id` in schema+SQL. UI: clickable `codigo_bip`, `text-blue-600 hover:underline`. Close drawer before navigating.
15. **Route ordering**: Static paths BEFORE `/{id}` routes (CDPs, bulk cuotas, cartera-por-division, dgi_services static endpoints).

### Operational

16. **Docker**: `goreos_db` on `visor_model_default` (external). Always `docker compose restart api` after code changes — hot-reload may miss new files.
17. **Large datasets**: `core.ipr` 3,600+, `core.organization` 3,300+. Never use `<Select>` — use `ComboboxAsync`. Divisions catalog ~9 entries only.
18. **Catalogs**: `organizations?search=TERM` (ComboboxAsync), `territories` (25, no search). Territory: `territory_type_id` (NOT `territory_level`).
19. **ETL**: Scripts run inside API container. CSVs via `docker cp`. See `traps_and_patterns.md` for CSV quirks.

### Domain-specific Rules

20. **Demo data**: `DEMO-` prefix in code/number fields. Never mix with real data.
21. **JSONB edits**: Atomic `jsonb_set` in `metadata` (not read-modify-write). Reports, DMAIC, decrees all use this pattern.
22. **Reuniones**: Auto-created committees: `COMITE-CRISIS`, `CONSEJO-REGIONAL`, `COMITE-TD`.
23. **Dashboard**: Unified Centro de Comando for ALL 16 roles. `GET /dashboard/action-items` (coproduct: 6 sources, role-scoped). Modules: MyProgress/MyTeam/DgiTeam/KPIs by role archetype.
24. **Admin module**: `usuarios`, `divisiones`, `financing-tracks`, `thresholds`, `sni-levels`, `budget-program-codes`, `admissibility-items`. ADMIN_SISTEMA only.
25. **CDPs + Cuotas**: CDP creation advisory-locked `CDP-{year}-{seq:04d}`, validates `amount ≤ current - committed`. Cuota bulk via `POST /cuotas/bulk`. Installments require `installment_number`, `amount`, `due_date`, `payment_status_id`.

### CORE Sessions & Governance

26. **CORE sessions**: Committee `CONSEJO-REGIONAL`. Quorum: SIMPLE=9/16, CALIFICADA=11/16. Gate F3→F4: IPRs >7,000 UTM require CORE approval.
27. **Security**: SecurityHeadersMiddleware (4 headers), brute-force lockout (5 attempts→15 min, 429), JWT secret rejects default key when `ENV != "development"`.

### Financing Tracks & Gates

28. **Track system**: `core.financing_track` (DB-parametric via `thresholds` JSONB, `.get("key", fallback)`). Admin CRUD `/api/admin/financing-tracks`. `core.financial_threshold` (10 rows: 4 UTM + 5 glosa% + UTM_VALUE). Use `_get_utm_value(db)`, never hardcode. Budget classifier: 6 levels, level 3 via `budget_program_code` scheme.
29. **31 gate functions** (all in `ipr.py` via `_evaluate_phase_gates()`): FRIL (max/comuna, fraccionamiento, tender), SNI (proporcionalidad, RS vigencia), C33 (conservation, certification), SUBV8 (pagaré, directorio, morosos, ranking), TRANSFER (glosa07 5% caps), ALL (evaluation match, glosa06 single-purpose/executor, kinship). Glosa rules: `check_glosa_rules()` at F3→F4.

### Evaluation & Compliance

30. **Evaluation**: `numeric_score` NUMERIC(5,2) on `evaluation_assignment`. `_EVAL_LABELS` dict maps eval-result codes (RS→"Rec. Satisfactoria", etc.) for display. `core.sni_level_config` (4 levels, admin CRUD).
31. **Admissibility**: PRE_ADMISIBLE→ADMISIBLE gate requires all `admissibility_check` verified. **`admissibility_check` has NO `deleted_at`**. Kinship gate at F1→F2 for SUBV8 only. C33 certification blocks F1→F2.
32. **Parametric tables**: `subv8_fund` (7), `subv8_fund_ceiling` (~22, functional UNIQUE via `COALESCE(area, '')`), `fril_category` (12, A2/A3 exempt), `budget_cycle_milestone` (17), `rendition_phase` (8). Admin CRUD for all. Routing: `GET /financing-tracks/routing?ipr_id=X`.
33. **SISREC CGR**: 8 phases. External phases 1-3 as metadata JSONB. Escalation: 3 levels (1x/1.5x/2x SLA). `POST /rendiciones/check-escalations` batch → alerts.

### UI Conventions

34. **Mandatory components**: All list pages → `PageHeader` (with `accentColor`). All empty states → `EmptyState`. All destructive actions → `ConfirmDialog`. All 500+ option selects → `ComboboxAsync`.
35. **Identity**: OKLCH palette (GOREAZUL #031B5F, GORECELESTE #196AB0). 3 fonts: Plus Jakarta Sans, Roboto Slab, JetBrains Mono. Dark sidebar. CSS-only fade-ins via tw-animate-css. `prefers-reduced-motion` in globals.css.
36. **IPR detail**: 16 tabs in `tab-*.tsx` (self-contained, grouped in 4 categories via TAB_GROUPS). Main: IprHeroCard, IprPhaseStepper, IprHistorySection, IprTransitionPanel (inline gate overview + feedforward effects). No ReadinessCard — gates live in TransitionPanel. `StatusBadge` 32 states, phase-based colors.
37. **Component API**: `DrawerPanel` uses `onClose` (not `onOpenChange`). `EmptyState` uses `title` (not `message`). `api.patch` requires 2 args. `PageGuard`: `allowedRoles?`, `allowedPopulations?`. `use-tab-param.ts` syncs tabs with `?tab=` URL param.

### IPR Lifecycle

38. **32 states + derived phase**: `STATUS_PHASE_FIBER` maps all states to phases. The `GET /api/ipr/{id}` endpoint returns `mcd_phase` **derived from status** (not from stored `mcd_phase_id`) to prevent data inconsistencies. Frontend MUST use `ipr.mcd_phase` as-is — never re-derive or read stored phase. Nature-aware: PROYECTO bifurcates EN_FORMALIZACION→licitación→obra; PROGRAMA→formalizado→ejecución. `_EVAL_LABELS` enriches F2 eval-result codes for display. **Labels must be human-readable Spanish — no raw codes or acronyms in UI.**
39. **IPR modifications + closure**: `ipr_modification` (MOD-YYYY-NNNN, trigger-enforced FSM). `ipr_closure` (UNIQUE per IPR, signed closure gate). `ipr_expost_evaluation` (post-CERRADO, 4 dimensions).
40. **ITO gate + SLAs**: Blocks EN_LICITACION→ADJUDICADO for PROYECTO without ITO. `phase_entered_at` auto-updates via trigger. Readiness endpoint (`/readiness`) evaluates all gates + same-phase custom gates. Batch: `check-report-compliance`, `check-evaluation-slas`.
