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
- `routers/` — 19 routers: auth, ipr, compromisos, problemas, alertas, dashboard, catalogs, presupuesto, convenios, admin (24 endpoints), reuniones, search, dgi_cockpit, dgi_initiatives, dgi_data, dgi_reports, dgi_cartera, actos (5 + 7-step FSM), core_sessions (9 + voting + F3→F4)

Conventions: `/api/` prefix. Paginated → `{items, total, page, page_size, total_pages}`. DGI lists → plain arrays (initiatives: optional pagination via `?page=1&page_size=N`). Dashboard/cockpit → role-aware responses. PATCH → allowlisted columns matching DB names. Person columns: `names`, `paternal_surname` (NOT `nombre`/`apellido_paterno`). User FK: `system_role_id` (NOT `role_id`).

### Frontend (`web/`)

Next.js 16 (App Router, Turbopack), TypeScript, TailwindCSS v4, shadcn/ui (Radix), lucide-react. State: React Context (`useAuth`) + `useSearchParams`.

- `lib/api.ts` — `ApiClient` singleton (`get/post/patch/delete<T>`). Token in localStorage (`goreos_token`). Auto-redirect on 401. Auto-extracts `.detail` from FastAPI errors. `delete()` handles 204.
- `lib/auth.tsx` — `AuthProvider`, `useAuth()` → `{user, loading, login, logout}`
- `lib/format.ts` — `formatDate`, `formatDateTime`, `formatDateTimeShort`, `formatDateLong`, `formatCLP`, `formatCurrency` (es-CL). **All 21 files import from here — never define local format functions.**
- `types/index.ts` — all interfaces. `User.population` (`"operativa"|"dgi"`) drives routing.
- `components/sidebar.tsx` — `operationalNav` (10) + role-specific (Mi División/Mis Compromisos) + `adminOnlyNav` (Usuarios, Divisiones, Umbrales, Niveles SNI) vs `dgiNav` (7) by population
- `components/combobox-async.tsx` — server-side searchable select (debounce 300ms, `shouldFilter={false}`). Use for 500+ option fields. Props: `value`, `onChange`, `searchFn`, `placeholder`.
- `components/page-header.tsx` — shared header (`title`, `description?`, `actions?`). **All list pages must use this.**
- `components/empty-state.tsx` — `compact` for tabs/inline, normal for full-page. **All empty states must use this.**
- `components/confirm-dialog.tsx` — AlertDialog for destructive actions. **Always use for delete/revert.** Props: `open`, `onOpenChange`, `title`, `description`, `onConfirm`, `variant?`, `confirmLabel?`, `cancelLabel?`, `loading?`.
- `app/(app)/layout.tsx` — AppShell wrapper for authenticated routes
- `app/(app)/dashboard/page.tsx` — detects population → operational dashboard or DGI cockpit

### Database

**99 tables across 4 schemas** (79 logical + 20 txn partitions):

| Schema | Purpose |
|--------|---------|
| `meta` | Role/Process/Entity/Story atoms (5) |
| `ref`  | Controlled vocabularies: `ref.category(scheme, code, label)` — 81 schemes + `ref.operational_commitment_type` |
| `core` | Business entities — 71 tables (IPR, Agreement, Budget, User, DGI, compliance, parametric) |
| `txn`  | Event sourcing (partitioned) |

**Category Pattern**: each FK → exactly ONE scheme (Categorical Univocity). Enforced by 86 CHECK constraints (`fn_validate_category_scheme`) + 8 state transition triggers + 4 history triggers. 81 schemes. Only 6 FKs deferred (need new schemes: vehicle, risk prob/status, inventory status, planning instrument). Check before creating: `SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;`

**Schemes**: DGI (11): `dgi_initiative_status`, `dgi_indicator_dimension`, `dgi_signal`, `dgi_report_type`, `dgi_report_status`, `dgi_bpmn_status`, `dgi_dmaic_phase`, `dgi_session_status`, `dgi_alert_status`, `dgi_decree_status`, `dgi_source_status`. Governance (3): `session_type`, `vote_option`, `quorum_type`. Budget (10): `budget_item`(14), `budget_allocation`(15), `program_type`(5), `budget_commitment_status`(5), `budget_subtitle`(8), `funding_source`(11), `payment_status`(5), `agreement_type`(6), `agreement_state`(13 w/transitions incl. EN_REVISION_FINANCIERA, VISADO_INTERNO, TDR_PENDIENTE), `cgr_outcome`(7).

**Org types**: `org_type` (14). Internal: GORE(1), DIVISION(8), DEPARTAMENTO(6), UNIDAD(8), STAFF_UNIT(7), ADVISORY_BODY(3). External: MUNICIPALIDAD, SERVICIO, MINISTERIO, UNIVERSIDAD, ONG, EMPRESA, ORG_COMUNITARIA, COMUNITARIA. Hierarchy 3-level via `parent_id`: GORE-NUBLE → Divisions → Departamentos → Unidades.

**System roles** (13): GOBERNADOR(0), ADMIN_SISTEMA(1), ADMIN_REGIONAL(2), JEFE_DIVISION(3), ENCARGADO(4), JEFE_DGI(5), ESP_CONTROL_GESTION(6), ESP_PROCESOS(7), ESP_TD(8), CONSEJERO_REGIONAL(9), SECRETARIO_EJECUTIVO(10), JEFE_DEPARTAMENTO(11), JEFE_UNIDAD(12).

## Test Users

All passwords: `admin123`. All `@goreos.cl`.

| Email | Role | Pop | Div |
|-------|------|-----|-----|
| admin | ADMIN_SISTEMA | op | — |
| regional | ADMIN_REGIONAL | op | — |
| gobernador | GOBERNADOR | op | — |
| secretario.core | SECRETARIO_EJECUTIVO | op | — |
| consejero1, consejero2 | CONSEJERO_REGIONAL | op | — |
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

**393 integration tests (388 pass + 5 skip)** against real PostgreSQL (`goreos_test`). No mocks.

```bash
./scripts/setup_test_db.sh                                          # Setup test DB
docker compose exec api pytest -v                                   # Full suite
docker compose exec api pytest tests/test_compromisos.py -v         # Single module
docker compose exec api pytest tests/test_auth.py::test_login_success -v  # Single test
docker compose exec api pip install pytest pytest-asyncio httpx     # Install deps (if rebuilt)
```

32 modules: test_auth(12), test_compromisos(16), test_presupuesto(10), test_initiatives(7), test_problemas(8), test_convenios(12), test_dashboard(6), test_security_readonly(12), test_ipr_children(14), test_ipr_lifecycle(6), test_actos(12), test_admin(11), test_reuniones(11), test_search(4), test_catalogs(8), test_core_sessions(10), test_rendiciones(5), test_polyswitch(14), test_alertas(6), test_dgi_cockpit(4), test_dgi_reports(4), test_dgi_cartera(12), test_concurrency(5), test_sisrec(27), test_thresholds(18), test_track_enforcement(32), test_track_rules(18), test_ciclo24(22), test_sisrec_8phase(12), test_parametric(13), test_admissibility(13), test_c33_certification(11).

**Test DB** (`scripts/setup_test_db.sh`): `pg_dump --schema-only` from `goreos_model` + `COPY ref.category` + territory + test users. Never apply `goreos_ddl.sql` directly (circular deps). Test users live in `goreos_seed_users.sql`.

**conftest.py**: fresh `AsyncSession` per test, overrides `get_db`, real JWT for 5 roles (admin, regional, jefe, encargado, dgi). `catalog` fixture pre-fetches common IDs.

**Known issues** (test data pollution):
- `test_initiatives::test_move_to_en_curso` — WIP limit. Clean: `DELETE FROM core.dgi_initiative WHERE deleted_at IS NULL;`
- `test_sisrec::test_vencidas_endpoint` — stale renditions. Clean: `DELETE FROM core.rendition WHERE created_at > '2026-01-01';`

DGI schemes (e.g., `dgi_initiative_status`) NOT in `goreos_seed.sql` — only in `goreos_model`, copied to `goreos_test` via COPY. Insert new DGI schemes into production first.

## Domain Model

Central: **IPR** — polymorphic (8 types: INFRAESTRUCTURA, EQUIPAMIENTO, CONSERVACION, TRANSFERENCIA, SUBSIDIO, ESTUDIO, PROGRAMA_SOCIAL, PROGRAMA_8PCT).

### Operational Layer

- **operational_commitment**: PENDIENTE→EN_PROGRESO→COMPLETADO→VERIFICADO. `commitment_history`. CRUD at `/compromisos/nuevo` + inline via `IprCompromisoDrawer`. Drawer shows clickable IPR link.
- **ipr_problem**: ABIERTO→EN_GESTION→RESUELTO|CERRADO_SIN_RESOLVER. Typed (TECNICO, FINANCIERO, LEGAL…). CRUD at `/problemas/nuevo` + inline via `IprProblemaDrawer`. State timeline + clickable IPR link.
- **alert**: Severity CRITICO/ALTO/ATENCION/INFO. `AlertCard.onViewSubject` navigates to any `subject_type` (`core.ipr`, `core.operational_commitment`, `core.ipr_problem`, `core.agreement`).
- **budget_program**: Per division, fiscal year. Execution: initial→current→committed→accrued→paid. Related: `budget_carryover`, `budget_commitment` (CDPs). CDPs by IPR: `GET /api/presupuesto/cdps-por-ipr/{ipr_id}`. Filterable by `division_id`.
- **agreement**: 13-state FSM (BORRADOR→EN_NEGOCIACION→EN_REVISION_JURIDICA→EN_REVISION_FINANCIERA→VISADO_INTERNO→FIRMADO_GORE→FIRMADO_CONTRAPARTE→VIGENTE/TDR_PENDIENTE→VENCIDO/TERMINADO/RESCILIADO). `agreement_installment` (CRUD inline in drawer). Orphan filter: `?orphan=true`.
- **progress_report**: Per IPR. `POST/GET /api/ipr/{id}/avances`. Auto-incremented `report_number`.
- **ipr_party**: 9 roles (POSTULANTE…MANDATARIO). `GET/POST/DELETE /api/ipr/{id}/partes`. UNIQUE `uq_ipr_party_role`. Admin-only write.
- **ipr_territory**: 4 impact types. `GET/POST/DELETE /api/ipr/{id}/territorio`. UNIQUE `uq_ipr_territory_impact`. Admin-only write.
- **ipr_milestone**: 13 types, planned/actual dates, auto `deviation_days` (GENERATED). `GET/POST/PATCH /api/ipr/{id}/hitos`. Admin-only write.
- **administrative_act**: DECRETO/RESOLUCION/DECRETO_ALCALDICIO. 7-step FSM: BORRADOR→EN_REVISION→VISADO→FIRMADO→ENVIADO_CGR→OBSERVADO/TOMADO_RAZON + ANULADO cross-cutting. Auto-creates `core.resolution` for RESOLUCION. `signer_id` FK→`meta.role` (NOT `core.person`). Split PATCH allowlist (`_ACT_FIELD_ALLOWLIST` + `_RES_FIELDS`). DB trigger validates transitions.
- **crisis_meeting**: Uses `core.committee`+`core.session`+`core.crisis_meeting`+`core.minute`+`core.session_agreement`. PROGRAMADA→EN_CURSO→FINALIZADA. Auto-suggestions from critical alerts/overdue commitments/open problems. BIP badges link to IPR.

### Cross-entity Navigation

- **IPR → satellites**: 13 tabs (Compromisos, Problemas, Alertas, Convenios, CDPs, Avances, Partes, Territorio, Hitos, Resoluciones, Evaluación, Parentesco, Admisibilidad) — self-contained components in `tab-*.tsx`.
- **Satellites → IPR**: Drawers show clickable `ipr_codigo_bip` → `/ipr/{id}`. Pattern: include `ipr_id` in schema+SQL, use `text-blue-600 hover:underline`, close drawer before navigating.
- **IPR list filters**: `?assignee_id=X` for all roles.

### DGI Layer

- **rendition** (SISREC): 8 states PENDIENTE→EN_REVISION_RTF→VISADA_RTF→EN_REVISION_UCR→APROBADA/RECHAZADA + OBSERVADA loop. Role-based: operativa initiates/resubmits, DGI visas/approves/rejects. `rendition_history` trigger audit. SLA: RTF 7d, VISADA_RTF 1d, UCR 2d, OBSERVADA 15d. `phase_entered_at` (SLA-accurate, only resets on transitions). `responsible_id` FK→`core.user`. `GET /rendiciones/{id}/ciclo` (timeline). CGR target: 14d. Art. 18: `convenios.py` checks renditions on cuota payments. `amount` field. NO `code` column — use `LEFT(r.id::text, 8)`. Use `COALESCE(r.phase_entered_at, r.updated_at)` in queries.
- **dgi_cartera**: Unified IPR view with aggregated data + health signal (VERDE/AMARILLO/ROJO) via `_compute_health_signal()`. 3 endpoints: `GET /dgi/cartera` (paginated, post-filter), `GET /dgi/cartera/resumen`, `GET /dgi/cartera/cuotas-vencidas`. Cockpit drill-down via `/cartera?health_signal=`.
- **dgi_indicator**: 5 dimensions (PRESUPUESTO, CARTERA_IPR, CONVENIOS, TDE, RIESGOS) × signal (VERDE/AMARILLO/ROJO). Refresh: `POST /api/dgi/data/indicators/refresh` (4/5; TDE static). Idempotent.
- **dgi_initiative**: Kanban, WIP limits server-side (EN_CURSO:5, REVISION:2). `POST /move` → 409 if limit. Response includes `responsible_id` + `responsible_name`.
- **dgi_report**: 4 types (FLASH, SEMANAL, MENSUAL, TEMATICO) × 6 auto-populated sections. User edits in `metadata` JSONB via atomic `jsonb_set` (not read-modify-write). Sections: resumen, tabla_indicadores, alertas, avance_dgi, decisiones, prioridades.
- **dgi_decree**: Ley 21.180 compliance tracking (DS7-DS12). `core.dgi_decree(code, name, status_id, deadline)`. CHECK on `dgi_decree_status` scheme (VIGENTE/PARCIAL/PENDIENTE). `GET /api/dgi/data/decrees`, `PATCH /api/dgi/data/decrees/{code}` (body: `DecreeUpdate`). Cockpit ESP_TD derives `normative_alerts` + `velocity` from decree deadlines + TDE indicators.

## Demo Data

`DEMO-` prefix in all codes. `goreos_seed_demo_ciclo2.sql` (load) / `goreos_unseed_demo_ciclo2.sql` (remove only DEMO- records). FKs use subqueries (not hardcoded UUIDs). Demo: BP-001..006 (3 divs, 30-80% exec), AGR-001..004 (mixed states + installments), CDP-001..008 (linked to real IPRs).

## ETL Pipeline

6 scripts in `api/scripts/etl/`: `enrich_persons`, `load_documents`, `load_admin_acts`, `enrich_agreements`, `load_fril`, `load_modifications`, `load_idis`. All `--dry-run`, `--limit N`, `--verbose`. Idempotent. Run inside API container after `docker cp` CSVs. Arch: `docs/ETL_ARCHITECTURE_v1.0.md`.

## Key References

- **Schema**: `model/model_goreos/sql/goreos_ddl.sql`, `goreos_seed.sql` (90+ schemes), `model/model_goreos/docs/GOREOS_ERD_v3.md`, `model/GLOSARIO.yml` (244 terms)
- **Spec**: `architecture/Omega_GORE_OS_Definition_v3.0.0.md`, `docs/GORE_OS_Audit_v2.0.md` (472 CQs, 15 HΩ)
- **Migrations**: `goreos_migration_*.sql` + `goreos_rollback_*.sql`. Tracked in `core.schema_migration`. Runner: `scripts/run_migrations.sh`.
- **Docs**: `docs/ONBOARDING.md`, `docs/GORE_OS_Testing_Ciclo3.md`, `docs/ETL_ARCHITECTURE_v1.0.md`, `docs/adr/` (7 ADRs)

## Coverage

~171 endpoints, 400 tests, 32 modules, 22 gate functions. HΩ: 15/15. Parametric: 6/6. Budget classifier: 6/6. Categorical Univocity: 86 CHECKs + 8 state triggers + 4 history triggers (6 FKs deferred). FSM DB-enforced: 8/23 entities. Schema truth: `goreos_ddl_production.sql` (pg_dump). Audit: `docs/GORE_OS_Audit_v3.0.md`. **Gap**: 0 external integrations (ClaveÚnica, PISEE, BIP, SIGFE, CGR).

## Critical Rules

### DB Naming & Schema

1. **Categorical Univocity**: Each FK→1 `ref.category` scheme. Never mix. See `goreos_migration_categorical_univocity.sql`.
2. **Person columns**: `names`, `paternal_surname` (NOT `nombre`/`apellido_paterno`). User FK: `system_role_id` (NOT `role_id`).
3. **Alert subject_type**: Fully-qualified in SQL: `'core.ipr'`, `'core.operational_commitment'`, etc. Always use `core.` prefix.
4. **Organization table**: NO `is_active` column — use `deleted_at IS NULL`. Type FK: `org_type_id` (NOT `organization_type_id`).
5. **UNIQUE constraints**: `ipr_party`→`uq_ipr_party_role`, `ipr_territory`→`uq_ipr_territory_impact`. Check these names in duplicate error handling.
6. **asyncpg casts**: NO `:param::jsonb` — use `CAST(:param AS jsonb)`.
7. **Advisory locks**: All code generators use `pg_advisory_xact_lock(hashtext('entity_code'))` before `SELECT MAX(...)`.
8. **DDL circular deps**: Never apply `goreos_ddl.sql` to fresh DB — use `pg_dump --schema-only` from `goreos_model`.

### API Patterns

9. **PATCH allowlist**: Validate columns against explicit allowlist. Pydantic field names must match DB columns exactly.
10. **Role restriction**: Use `_require_roles(user, ...)` inside endpoint body. Do NOT use `require_roles()` as default param — conflicts with `CurrentUser` (`Annotated[dict, Depends()]`).
11. **DGI initiatives pagination**: Optional `page`+`page_size`. With `page`→paginated response. Without→plain array. **Never change default** — Kanban depends on it.
12. **Error messages**: `ApiClient` auto-extracts `.detail` from FastAPI errors. Backend `HTTPException(detail="...")` reaches frontend as clean text.
13. **Cross-entity navigation**: Include FK `ipr_id` in schema+SQL. UI: `<button onClick={...}>{codigo_bip}</button>` + `text-blue-600 hover:underline`. Close drawer before navigating.

### Operational

14. **Docker network**: `goreos_db` on `visor_model_default` (external). Don't create separate postgres unless `--profile standalone`.
15. **After code changes**: Always `docker compose restart api` — hot-reload may miss new files/imports.
16. **Large datasets**: `core.ipr` 3,600+ rows, `core.organization` 3,300+. Never use `<Select>`. Use `ComboboxAsync` (server-side: `GET /api/catalogs/iprs?search=TERM`). Divisions catalog (`GET /api/catalogs/divisions`) returns ~9 entries only (DIVISION+GORE type). After confrontation migration, many orgs reclassified to STAFF_UNIT/DEPARTAMENTO/UNIDAD/ADVISORY_BODY — intentionally excluded.
17. **Catalog endpoints**: `GET /api/catalogs/organizations?search=TERM` (ComboboxAsync), `GET /api/catalogs/territories` (25, no search needed). Territory: `territory_type_id` FK (NOT `territory_level`).
18. **ETL runtime**: Scripts run inside API container. CSVs via `docker cp` first. Uses `goreos_db` not `localhost`.
19. **PARTES CSV quirks**: Some files have garbage row 0. Use `read_csv(path, skip_rows=1)`. Always inspect headers.

### Domain-specific Rules

20. **Demo data**: `DEMO-` prefix in code/number fields. Never mix with real data.
21. **Report section edits**: Atomic `jsonb_set` in `metadata` (not read-modify-write). Auto-populated content regenerated on each GET; only user edits persist.
22. **Reuniones**: Uses existing DDL tables. Crisis committee `COMITE-CRISIS` auto-created on first use. `core_sessions.py` handles CORE sessions (committee `CONSEJO-REGIONAL`, auto-created).
23. **Dashboard**: Role-specific: `GET /dashboard` (base), `/dashboard/ejecutivo` (ADMIN, division breakdown), `/dashboard/mi-division` (JEFE_DIVISION), `/dashboard/mis-compromisos` (ENCARGADO).
24. **Admin module**: `usuarios` CRUD+toggle/reset, `divisiones`, `financing-tracks`, `thresholds`, `sni-levels`, `budget-program-codes`, `admissibility-items`. All ADMIN_SISTEMA only.
25. **CDP endpoint**: `GET /api/presupuesto/cdps-por-ipr/{ipr_id}` → `list[BudgetCommitmentItem]`. Route BEFORE `/{presupuesto_id}` to avoid path conflicts.
26. **Convenio installments**: `POST /cuotas` requires `installment_number`, `amount`, `due_date`, `payment_status_id`. `PATCH /cuotas/{id}` accepts `payment_status_id`, `paid_at`, `paid_amount`, `payment_reference`. Inline forms in drawer.
27. **Bulk cuotas**: `POST /api/convenios/{id}/cuotas/bulk` → `BulkCuotaRequest(total_amount, num_installments, start_date, frequency_months=1)`. Remainder on first. Route BEFORE `/{id}/cuotas`. `_add_months()` uses `calendar.monthrange`.
28. **CDP creation**: `POST /api/presupuesto/{id}/cdps` → advisory-locked `CDP-{year}-{seq:04d}`. Validates `amount ≤ current - committed`. Auto EMITIDO. Schema: `BudgetCommitmentCreate(amount, description?, ipr_id?, agreement_id?)`.
29. **Confrontation migration**: `goreos_migration_confrontacion.sql` (data-only, idempotent). Expanded org_type(+2), reclassified 16 orgs, 3-level hierarchy, +3 agreement states, +5 roles, soft-deleted 6 dupes. Rollback: `goreos_rollback_confrontacion.sql`.
30. **Responsive Radix portals**: `DrawerPanel` (Sheet) renders via portals — CSS `display:none` on parent won't hide it. Use `window.matchMedia` + `isMobile` state. Ref: `/datos/page.tsx`.

### CORE Sessions & Governance

31. **CORE sessions**: Committee `CONSEJO-REGIONAL`. Quorum: SIMPLE=9/16, CALIFICADA=11/16. Gate F3→F4: IPRs >7,000 UTM require CORE approval.
32. **Security**: SecurityHeadersMiddleware (4 headers), brute-force lockout (5 attempts→15 min, HTTP 429), JWT secret validation rejects default key when `ENV != "development"`.

### Financing Tracks & Gates

33. **Financing tracks**: `core.financing_track` replaces hardcoded config. Admin CRUD via `/api/admin/financing-tracks`. `_get_track_config()` from DB. All thresholds DB-parametric via `thresholds` JSONB. Pattern: `.get("key", fallback)`.
34. **Track enforcement**: `_check_track_amount_gates()` reads JSONB. Keys: `max_utm`, `min_clp`, `puntaje_min` (F2→F3), `cgr_res30_utm`, `licitacion_max_days` (F3→F4), `sisrec_mandatory_utm` (F4→F5), `core_approval`. `_get_ipr_monto()` reads `metadata->>'monto_total'`.
35. **Financial thresholds**: `core.financial_threshold` (10 rows: 4 UTM + 5 glosa% + UTM_VALUE). Helpers: `_get_utm_value()`, `_get_threshold()`, `_check_utm_threshold()`.
36. **Glosa rules**: `check_glosa_rules(ipr_id, db)` → 5 limits + `_check_glosa03_prohibition()` (FNDR→PERSONAL blocked). At F3→F4.
37. **Budget classifier**: 6 levels complete. List accepts `item`, `allocation`, `program_type`, `program_code` filters. Level 3 via `budget_program_code` scheme + admin CRUD.
38. **Track gate functions** (all in `ipr.py` via `_evaluate_phase_gates()`):
    - FRIL: `_check_fril_max_per_comuna` (F0→F1, max 5, A2/A3 exempt), `_check_fril_fraccionamiento` (F1→F2, ±90d), `_check_fril_tender_deadline` (F3→F4)
    - SNI: `_check_sni_proporcionalidad` (F1→F2, 4 levels by UTM), `_check_rs_vigencia` (F3→F4, expiry per `rs_validity_years`)
    - C33: `_check_c33_conservation` (F1→F2, informational)
    - SUBV8: `_check_pagare_notarial` (F2→F3, ≥100%+≥18mo), `_check_directorio_certificate` (F2→F3), `_check_morosos_sisrec` (F3→F4+F4→F5), `_check_ranking_persistence` (F2→F3, informational)
    - ALL: `_check_evaluation_type_match` (F2→F3, informational), `_check_glosa06_single_purpose` (F1→F2), `_check_glosa06_direct_executor` (F1→F2, GORE-NUBLE EJECUTOR for GLOSA06)
    - TRANSFER: `check_glosa07_transfer_limits` (F3→F4, 5% caps via `_GLOSA07_LIMITS` in presupuesto.py)

### Evaluation & Compliance

39. **Evaluation**: `numeric_score` NUMERIC(5,2) on `evaluation_assignment`. `rank_position`, `rank_total`, `convocatoria_code`. `core.sni_level_config` (4 levels, admin CRUD).
40. **Kinship (HΩ-02)**: `core.kinship_declaration` UNIQUE(ipr_id, person_id, declaration_type). CRUD via `/api/ipr/{id}/parentesco`. Gate `_check_kinship_declarations()` at F1→F2 for SUBV8 only. Authority roles: GOBERNADOR, CONSEJERO_REGIONAL, SECRETARIO_EJECUTIVO, ADMIN_REGIONAL, JEFE_DIVISION. Person search: `GET /api/catalogs/persons?search=`.
41. **Admissibility**: PRE_ADMISIBLE between EN_REVISION and ADMISIBLE. `core.admissibility_item` (parametric/track) + `core.admissibility_check` (per IPR). Gate blocks PRE_ADMISIBLE→ADMISIBLE until all verified. Admin CRUD: `/api/admin/admissibility-items`. IPR: `GET/POST/DELETE /api/ipr/{id}/admisibilidad`. Role-restricted to `responsible_role` or ADMIN_SISTEMA.
42. **C33 certification**: `categoria_c33` scheme (EDIFICACION→SERVIU, VIALIDAD→MOP). Cert data in `core.ipr.metadata` with `cert_` prefix. Gate blocks F1→F2. `GET/POST/PATCH /api/ipr/{id}/certificacion-tecnica`. JEFE_DIVISION+ request, ADMIN_REGIONAL/ADMIN_SISTEMA resolve.
43. **Budget cycle (TP-05)**: `core.budget_cycle_milestone` (17 seed) + `core.budget_cycle_tracking`. 5 endpoints: `GET /ciclo/hitos`, `POST /ciclo/{year}`, `GET /ciclo/{year}`, `GET /ciclo/{year}/resumen`, `PATCH /ciclo/tracking/{id}`. States: PENDIENTE/EN_CURSO/COMPLETADO/OMITIDO. Frontend: `/presupuesto/ciclo`. Sidebar: "Ciclo Ppto."
44. **SISREC 8-Phase CGR (TP-06)**: `core.rendition_phase` (8 seed). External phases 1-3 as metadata JSONB timestamps. Phase 8 via `archived_at`. Escalation: `core.rendition_escalation` (3 levels: 1x, 1.5x, 2x SLA). `_STATE_TO_PHASE_CODE` mapping. `POST /rendiciones/check-escalations` batch-detects overdue → alerts.
45. **Parametric tables (TP-02/04)**: `core.subv8_fund` (7) + `core.subv8_fund_ceiling` (~22, functional UNIQUE via `COALESCE(area, '')`). `core.fril_category` (12 A1-D3, `is_exempt_commune_limit` for A2/A3). Admin CRUD: 8 subv8 + 3 FRIL + routing query `GET /financing-tracks/routing?ipr_id=X`.

### UI Rules

46. **Shared components (Wave 2)**: All list pages → `PageHeader`. All empty states → `EmptyState`. All destructive actions → `ConfirmDialog`. 25 components in `web/src/components/`.
47. **Identity (Wave 1)**: GORE Ñuble branding. OKLCH palette (GOREAZUL #031B5F, GORECELESTE #196AB0). 3 fonts: Plus Jakarta Sans (body), Roboto Slab (headings, auto h1/h2), JetBrains Mono (mono). Dark sidebar always. Theme toggle with FOUC-prevention in `layout.tsx`. `GoreMark` SVG.
48. **Motion (Wave 3)**: CSS-only fade-ins via tw-animate-css 1.4.0. Classes: `animate-in fade-in duration-{200,300}`. Stagger: `delay-{75,150,200,300}` + `fill-mode-both`. `prefers-reduced-motion` in globals.css. Applied: PageHeader, Dashboard KPIs (stagger), DataTable, Login (sequential). NOT: sidebar, DrawerPanel/Sheet (Radix-animated), skeletons.
49. **IPR detail**: 13 tabs in `tab-*.tsx` — self-contained. Main page (~650 lines) retains hero, stepper, transitions, edit/assignee drawers.
