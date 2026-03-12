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
- `core/audit.py` — `record_event()` functor de observación U: Crisis → txn.event
- `routers/` — 28 routers: auth, ipr, compromisos, problemas, alertas, dashboard, catalogs, presupuesto, convenios, admin (24 endpoints), reuniones (+ 2 crisis→decision bridge), search, dgi_cockpit, dgi_initiatives (+ 5 DMAIC + 1 lean-metrics), dgi_data, dgi_reports, dgi_cartera, dgi_processes (22 + 2 analytics endpoints), dgi_bottleneck (7 endpoints), actos (5 + 7-step FSM), core_sessions (9 + voting + F3→F4), dgi_coordination (10 + 1 calendar endpoint), dgi_escalation (7 endpoints: 4-level protocol + FSM + stats + cross-pop read), dgi_services (12 endpoints: catalog + requests + SLAs + dashboard), dgi_td_sessions (6 endpoints: TD committee sessions + topics), risk (8 endpoints: CRUD + FSM + summary + matrix + check-alerts), command_center (2 endpoints: summary + timeline)

Conventions: `/api/` prefix. Paginated → `{items, total, page, page_size, total_pages}`. DGI lists → plain arrays (initiatives: optional pagination via `?page=1&page_size=N`). Dashboard/cockpit → role-aware responses. PATCH → allowlisted columns matching DB names. Person columns: `names`, `paternal_surname` (NOT `nombre`/`apellido_paterno`). User FK: `system_role_id` (NOT `role_id`).

### Frontend (`web/`)

Next.js 16 (App Router, Turbopack), TypeScript, TailwindCSS v4, shadcn/ui (Radix), lucide-react. State: React Context (`useAuth`) + `useSearchParams`.

- `lib/api.ts` — `ApiClient` singleton (`get/post/patch/delete<T>`). Token in localStorage (`goreos_token`). Auto-redirect on 401. Auto-extracts `.detail` from FastAPI errors. `delete()` handles 204.
- `lib/auth.tsx` — `AuthProvider`, `useAuth()` → `{user, loading, login, logout}`
- `lib/format.ts` — `formatDate`, `formatDateTime`, `formatDateTimeShort`, `formatDateLong`, `formatCLP`, `formatCurrency` (es-CL). **All 21 files import from here — never define local format functions.**
- `types/index.ts` — all interfaces. `User.population` (`"operativa"|"dgi"`) drives routing.
- `components/sidebar.tsx` — Semantic sections (5-7 per population) via `NavSection` (collapsible, localStorage-persisted). Operativa: Comando, Gestión IPR, Finanzas, Institucional, Mi Trabajo, Administración. DGI: Monitoreo, Mejora Continua, Coordinación, Análisis.
- `components/combobox-async.tsx` — server-side searchable select (debounce 300ms, `shouldFilter={false}`). Use for 500+ option fields. Props: `value`, `onChange`, `searchFn`, `placeholder`.
- `components/page-header.tsx` — shared header (`title`, `description?`, `actions?`, `breadcrumbs?`, `accentColor?`). **All list pages must use this.** Domain accents: indigo(IPR), amber(compromisos), emerald(finanzas), violet(institucional), rose(riesgos), cyan(DGI), teal(servicios).
- `components/empty-state.tsx` — `compact` for tabs/inline, normal for full-page. **All empty states must use this.**
- `components/confirm-dialog.tsx` — AlertDialog for destructive actions. **Always use for delete/revert.** Props: `open`, `onOpenChange`, `title`, `description`, `onConfirm`, `variant?`, `confirmLabel?`, `cancelLabel?`, `loading?`.
- `app/(app)/layout.tsx` — AppShell wrapper for authenticated routes
- `app/(app)/dashboard/page.tsx` — unified entry → `<CommandCenter />` for ALL 16 roles
- `components/breadcrumb.tsx` — navigable breadcrumbs, used in 18 detail/create pages
- `components/page-guard.tsx` — wrapper: auth check + role gate + loading skeleton + error state
- `components/progress-cell.tsx` — inline progress bar (green ≥70%, amber ≥40%, red <40%)
- `components/deadline-cell.tsx` — date + semáforo color (red overdue, amber ≤7d)
- `components/detail-page-layout.tsx` — opt-in wrapper: breadcrumbs + hero + stepper + transition panel
- `hooks/use-tab-param.ts` — sync Radix Tabs value with `?tab=` URL search param

### Database

**120 tables across 4 schemas** (92 core + 5 meta + 3 ref + 20 txn partitions):

| Schema | Purpose |
|--------|---------|
| `meta` | Role/Process/Entity/Story atoms (5) |
| `ref`  | Controlled vocabularies: `ref.category(scheme, code, label)` — 81 schemes + `ref.operational_commitment_type` |
| `core` | Business entities — 80 tables (IPR, Agreement, Budget, User, DGI, compliance, parametric, coordination, lifecycle) |
| `txn`  | Event sourcing (partitioned) |

**Category Pattern**: each FK → exactly ONE scheme (Categorical Univocity). **100% coverage**: 98 CHECK constraints + 19 state transition triggers + 6 history/timing triggers. 105 schemes. 0 unprotected FK→ref.category. Check before creating: `SELECT DISTINCT scheme FROM ref.category ORDER BY scheme;`

**Schemes**: DGI (19): `dgi_initiative_status`, `dgi_indicator_dimension`, `dgi_signal`, `dgi_report_type`, `dgi_report_status`, `dgi_bpmn_status`, `dgi_dmaic_phase`, `dgi_session_status`, `dgi_alert_status`, `dgi_decree_status`, `dgi_source_status`, `dgi_ar_decision_type`(4), `dgi_ar_decision_status`(3), `dgi_escalation_level`(4), `dgi_escalation_status`(4), `dgi_service_status`(3), `dgi_request_status`(6), `dgi_sla_product_type`(7), `dgi_interaction_type`(6). Governance (3): `session_type`, `vote_option`, `quorum_type`. Budget (10): `budget_item`(14), `budget_allocation`(15), `program_type`(5), `budget_commitment_status`(5), `budget_subtitle`(8), `funding_source`(11), `payment_status`(5), `agreement_type`(6), `agreement_state`(13 w/transitions incl. EN_REVISION_FINANCIERA, VISADO_INTERNO, TDR_PENDIENTE), `cgr_outcome`(7).

**Org types**: `org_type` (14). Internal: GORE(1), DIVISION(8), DEPARTAMENTO(6), UNIDAD(8), STAFF_UNIT(7), ADVISORY_BODY(3). External: MUNICIPALIDAD, SERVICIO, MINISTERIO, UNIVERSIDAD, ONG, EMPRESA, ORG_COMUNITARIA, COMUNITARIA. Hierarchy 3-level via `parent_id`: GORE-NUBLE → Divisions → Departamentos → Unidades.

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

**568 integration tests (565 pass + 3 skip)** against real PostgreSQL (`goreos_test`). No mocks.

```bash
./scripts/setup_test_db.sh                                          # Setup test DB
docker compose exec api pytest -v                                   # Full suite
docker compose exec api pytest tests/test_compromisos.py -v         # Single module
docker compose exec api pytest tests/test_auth.py::test_login_success -v  # Single test
docker compose exec api pip install pytest pytest-asyncio httpx     # Install deps (if rebuilt)
```

42 modules: test_auth(12), test_compromisos(16), test_presupuesto(10), test_initiatives(7), test_problemas(8), test_convenios(12), test_dashboard(6), test_security_readonly(12), test_ipr_children(14), test_ipr_lifecycle(6), test_actos(12), test_admin(11), test_reuniones(11), test_search(4), test_catalogs(8), test_core_sessions(10), test_rendiciones(5), test_polyswitch(14), test_alertas(6), test_dgi_cockpit(6), test_dgi_reports(4), test_dgi_cartera(12), test_concurrency(5), test_sisrec(27), test_thresholds(18), test_track_enforcement(32), test_track_rules(18), test_ciclo24(22), test_sisrec_8phase(12), test_parametric(13), test_admissibility(13), test_c33_certification(11), test_dmaic(24), test_coordination(35), test_risk(19), test_command_center(9), test_parentesco(10), test_new_roles(21), test_ipr_bifurcation(18), test_modifications(12), test_closure(14), test_lifecycle_slas(12).

**Test DB** (`scripts/setup_test_db.sh`): `pg_dump --schema-only` from `goreos_model` + `COPY ref.category` + territory + test users. Never apply `goreos_ddl.sql` directly (circular deps). Test users live in `goreos_seed_users.sql`.

**conftest.py**: fresh `AsyncSession` per test, overrides `get_db`, real JWT for 8 roles (admin, regional, jefe, encargado, dgi, analista, rtf, juridico). `catalog` fixture pre-fetches common IDs.

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

- **IPR → satellites**: 16 tabs (Compromisos, Problemas, Alertas, Convenios, CDPs, Avances, Partes, Territorio, Hitos, Resoluciones, Evaluación, Parentesco, Admisibilidad, Modificaciones, Cierre, Ex-Post) — self-contained components in `tab-*.tsx`.
- **Satellites → IPR**: Drawers show clickable `ipr_codigo_bip` → `/ipr/{id}`. Pattern: include `ipr_id` in schema+SQL, use `text-blue-600 hover:underline`, close drawer before navigating.
- **IPR list filters**: `?assignee_id=X` for all roles.

### DGI Layer

- **rendition** (SISREC): 8 states PENDIENTE→EN_REVISION_RTF→VISADA_RTF→EN_REVISION_UCR→APROBADA/RECHAZADA + OBSERVADA loop. Role-based: operativa initiates/resubmits, DGI visas/approves/rejects. `rendition_history` trigger audit. SLA: RTF 7d, VISADA_RTF 1d, UCR 2d, OBSERVADA 15d. `phase_entered_at` (SLA-accurate, only resets on transitions). `responsible_id` FK→`core.user`. `GET /rendiciones/{id}/ciclo` (timeline). CGR target: 14d. Art. 18: `convenios.py` checks renditions on cuota payments. `amount` field. NO `code` column — use `LEFT(r.id::text, 8)`. Use `COALESCE(r.phase_entered_at, r.updated_at)` in queries.
- **dgi_cartera**: Unified IPR view with aggregated data + health signal (VERDE/AMARILLO/ROJO) via `_compute_health_signal()`. 3 endpoints: `GET /dgi/cartera` (paginated, post-filter), `GET /dgi/cartera/resumen`, `GET /dgi/cartera/cuotas-vencidas`. Cockpit drill-down via `/cartera?health_signal=`.
- **dgi_indicator**: 5 dimensions (PRESUPUESTO, CARTERA_IPR, CONVENIOS, TDE, RIESGOS) × signal (VERDE/AMARILLO/ROJO). Refresh: `POST /api/dgi/data/indicators/refresh` (4/5; TDE static). Idempotent.
- **dgi_initiative**: Kanban, WIP limits server-side (EN_CURSO:5, REVISION:2). `POST /move` → 409 if limit. Response includes `responsible_id` + `responsible_name`.
- **dgi_report**: 4 types (FLASH, SEMANAL, MENSUAL, TEMATICO) × 6 auto-populated sections. User edits in `metadata` JSONB via atomic `jsonb_set` (not read-modify-write). Sections: resumen, tabla_indicadores, alertas, avance_dgi, decisiones, prioridades.
- **dgi_decree**: Ley 21.180 compliance tracking (DS7-DS12). `core.dgi_decree(code, name, status_id, deadline)`. CHECK on `dgi_decree_status` scheme (VIGENTE/PARCIAL/PENDIENTE). `GET /api/dgi/data/decrees`, `PATCH /api/dgi/data/decrees/{code}` (body: `DecreeUpdate`). Cockpit ESP_TD derives `normative_alerts` + `velocity` from decree deadlines + TDE indicators.
- **dgi_ar_decision**: AR coordination decisions (PRIORIDAD/RECURSO/ESCALAMIENTO/ESTRATEGIA). FSM: PENDIENTE→EN_EJECUCION→COMPLETADA. CRUD + prep view. `dgi_coordination.py`.
- **dgi_escalation**: 4-level escalation protocol (NIVEL_1..4). FSM: ABIERTO→EN_GESTION→RESUELTO→CERRADO. Auto-code `ESC-{year}-{seq:04d}`, auto-alert creation, deadline semáforo. `dgi_escalation.py`.
- **dgi_service**: Service catalog (areas: CG/MP/TD/KC). Status: ACTIVO/SUSPENDIDO/DESCONTINUADO. Visible to all populations. `dgi_services.py`.
- **dgi_service_request**: Service requests with FSM: RECIBIDA→EN_EVALUACION→ACEPTADA→EN_EJECUCION→COMPLETADA|RECHAZADA. Auto-code `REQ-{year}-{seq:04d}`, timing triggers, satisfaction feedback. Any user creates, DGI manages.
- **dgi_sla**: SLA definitions per service×product_type. 7 product types (INFORME_FLASH..SOPORTE_TD). Dashboard: completion %, MTTR, breaches.
- **dgi_division_interaction**: Interaction log with divisions. JSONB: participants, topics, agreements. Matrix view: last/next interaction per division.
- **dgi_td_sessions**: TD Committee sessions via `core.session` tables (committee `COMITE-TD`, auto-created). 6 endpoints: list/create/detail/action + topics CRUD. No voting/quorum — operational committee. FSM: PROGRAMADA→EN_CURSO→FINALIZADA. DGI_ROLES only.
- **calendar** (consolidated): `GET /api/dgi/coordination/calendar` — UNION ALL across 5 sources (TD sessions, interactions, AR decisions, escalations, SLA breaches). Params: `from`, `to`, `type`. Returns `CalendarEvent[]` with severity semáforo.
- **risk** (Wave E): Cross-population risk register. `risk.py` (8 endpoints). FSM: IDENTIFICADO→EN_EVALUACION→EN_MITIGACION→MITIGADO→CERRADO (+ ACEPTADO path). Advisory-locked code gen `RSK-{seq:04d}`. Auto-alert creation for ALTA/MUY_ALTA probability. Subject polymorphic (core.ipr, core.dgi_process). Role scoping: ENCARGADO→own IPRs, JEFE_DIVISION→division IPRs, DGI/ADMIN→all.
- **command_center** (Wave E): Consolidated crisis dashboard. `command_center.py` (2 endpoints). Summary: 6 parallel queries (escalations, alerts, risks, AR decisions, meetings, SLA breaches). Timeline: UNION ALL of 5 sources with category filter + pagination. Roles: ADMIN_REGIONAL, GOBERNADOR, ADMIN_SISTEMA, JEFE_DGI.
- **audit trail** (Wave E): `core/audit.py` `record_event()` populates `txn.event`. 10 event_type codes. 15 integration points across 5 routers (risk, escalation, alertas, coordination, reuniones). Graceful degradation on unknown event_type codes.

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

~276 endpoints, 577 tests, 43 modules, 31 gate functions. 55 frontend pages, ~35 shared components. HΩ: 15/15. Parametric: 6/6. Budget classifier: 6/6. Categorical Univocity: 98 CHECKs + 19 state triggers + 6 history/timing triggers (**100% FK coverage, 0 unprotected**). FSM DB-enforced: 19 entities. 105 schemes. Schema truth: `goreos_ddl_production.sql` (pg_dump). All migrations have rollbacks. Audit trail: `txn.event` populated via `record_event()` in 5 routers (15 integration points). UX: structural refactoring (6 phases) + visual refresh (3 layers) complete. **Gap**: 0 external integrations (ClaveÚnica, PISEE, BIP, SIGFE, CGR).

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
9. **Alert INSERT**: `core.alert` requires `alert_type_id` (NOT NULL). Use scheme `alert_type` (13 codes: CUOTA_VENCIDA, PLAZO_LEGAL, RIESGO_ALTO, etc.). All batch alert-creation endpoints must include it.
10. **asyncpg date params**: asyncpg rejects date strings like `'2026-03-11'`. Parse with `date.fromisoformat(val)` before passing to `db.execute()`. Same for `timestamptz` — use `datetime` objects.
11. **ipr_party columns**: NO `person_id` column — uses `organization_id` + `party_role_id` + `contact_person` (text). ITO assignment via `party_role_id` FK to `ipr_party_role` scheme code `ITO`.
12. **DB trigger errors → HTTP 409**: FSM triggers raise `RaiseError` on invalid transitions. Catch `DBAPIError`, check `"Transición de estado inválida"` in `str(e)`, return 409 with `str(e.orig)`. Always `await db.rollback()` before raising.
13. **schema_migration table**: Columns are `(id, filename, applied_at, checksum, applied_by)`. Use `INSERT INTO core.schema_migration (filename, applied_at) VALUES ('goreos_migration_X.sql', NOW()) ON CONFLICT (filename) DO NOTHING;`. NOT `version`/`description`.

### API Patterns

14. **PATCH allowlist**: Validate columns against explicit allowlist. Pydantic field names must match DB columns exactly.
15. **Role restriction**: Use `_require_roles(user, ...)` inside endpoint body. Do NOT use `require_roles()` as default param — conflicts with `CurrentUser` (`Annotated[dict, Depends()]`).
16. **DGI initiatives pagination**: Optional `page`+`page_size`. With `page`→paginated response. Without→plain array. **Never change default** — Kanban depends on it.
17. **Error messages**: `ApiClient` auto-extracts `.detail` from FastAPI errors. Backend `HTTPException(detail="...")` reaches frontend as clean text.
18. **Cross-entity navigation**: Include FK `ipr_id` in schema+SQL. UI: `<button onClick={...}>{codigo_bip}</button>` + `text-blue-600 hover:underline`. Close drawer before navigating.

### Operational

19. **Docker network**: `goreos_db` on `visor_model_default` (external). Don't create separate postgres unless `--profile standalone`.
20. **After code changes**: Always `docker compose restart api` — hot-reload may miss new files/imports.
21. **Large datasets**: `core.ipr` 3,600+ rows, `core.organization` 3,300+. Never use `<Select>`. Use `ComboboxAsync` (server-side: `GET /api/catalogs/iprs?search=TERM`). Divisions catalog (`GET /api/catalogs/divisions`) returns ~9 entries only (DIVISION+GORE type). After confrontation migration, many orgs reclassified to STAFF_UNIT/DEPARTAMENTO/UNIDAD/ADVISORY_BODY — intentionally excluded.
22. **Catalog endpoints**: `GET /api/catalogs/organizations?search=TERM` (ComboboxAsync), `GET /api/catalogs/territories` (25, no search needed). Territory: `territory_type_id` FK (NOT `territory_level`).
23. **ETL runtime**: Scripts run inside API container. CSVs via `docker cp` first. Uses `goreos_db` not `localhost`.
24. **PARTES CSV quirks**: Some files have garbage row 0. Use `read_csv(path, skip_rows=1)`. Always inspect headers.

### Domain-specific Rules

25. **Demo data**: `DEMO-` prefix in code/number fields. Never mix with real data.
26. **Report section edits**: Atomic `jsonb_set` in `metadata` (not read-modify-write). Auto-populated content regenerated on each GET; only user edits persist.
27. **Reuniones**: Uses existing DDL tables. Crisis committee `COMITE-CRISIS` auto-created on first use. `core_sessions.py` handles CORE sessions (committee `CONSEJO-REGIONAL`, auto-created).
28. **Dashboard**: Unified Centro de Comando Personal for ALL roles. `GET /dashboard/action-items` (computed coproduct: commitments, alerts, decisions, escalations, SLA breaches, risks — role-scoped). Existing endpoints: `/dashboard` (base), `/dashboard/ejecutivo` (ADMIN), `/dashboard/mi-division` (JEFE_DIVISION), `/dashboard/mis-compromisos` (ENCARGADO). Module selection by `role_code`: ENCARGADO→MyProgress, JEFE_DIVISION→MyTeam, JEFE_DGI→DgiTeam, PANORAMA→KPIs+semáforo. DGI cockpits still accessible via sidebar (Monitoreo section).
29. **Admin module**: `usuarios` CRUD+toggle/reset, `divisiones`, `financing-tracks`, `thresholds`, `sni-levels`, `budget-program-codes`, `admissibility-items`. All ADMIN_SISTEMA only.
30. **CDP endpoint**: `GET /api/presupuesto/cdps-por-ipr/{ipr_id}` → `list[BudgetCommitmentItem]`. Route BEFORE `/{presupuesto_id}` to avoid path conflicts.
31. **Convenio installments**: `POST /cuotas` requires `installment_number`, `amount`, `due_date`, `payment_status_id`. `PATCH /cuotas/{id}` accepts `payment_status_id`, `paid_at`, `paid_amount`, `payment_reference`. Inline forms in drawer.
32. **Bulk cuotas**: `POST /api/convenios/{id}/cuotas/bulk` → `BulkCuotaRequest(total_amount, num_installments, start_date, frequency_months=1)`. Remainder on first. Route BEFORE `/{id}/cuotas`. `_add_months()` uses `calendar.monthrange`.
33. **CDP creation**: `POST /api/presupuesto/{id}/cdps` → advisory-locked `CDP-{year}-{seq:04d}`. Validates `amount ≤ current - committed`. Auto EMITIDO. Schema: `BudgetCommitmentCreate(amount, description?, ipr_id?, agreement_id?)`.
34. **Confrontation migration**: `goreos_migration_confrontacion.sql` (data-only, idempotent). Expanded org_type(+2), reclassified 16 orgs, 3-level hierarchy, +3 agreement states, +5 roles, soft-deleted 6 dupes. Rollback: `goreos_rollback_confrontacion.sql`.
35. **Responsive Radix portals**: `DrawerPanel` (Sheet) renders via portals — CSS `display:none` on parent won't hide it. Use `window.matchMedia` + `isMobile` state. Ref: `/datos/page.tsx`.

### CORE Sessions & Governance

36. **CORE sessions**: Committee `CONSEJO-REGIONAL`. Quorum: SIMPLE=9/16, CALIFICADA=11/16. Gate F3→F4: IPRs >7,000 UTM require CORE approval.
37. **Security**: SecurityHeadersMiddleware (4 headers), brute-force lockout (5 attempts→15 min, HTTP 429), JWT secret validation rejects default key when `ENV != "development"`.

### Financing Tracks & Gates

38. **Financing tracks**: `core.financing_track` replaces hardcoded config. Admin CRUD via `/api/admin/financing-tracks`. `_get_track_config()` from DB. All thresholds DB-parametric via `thresholds` JSONB. Pattern: `.get("key", fallback)`.
39. **Track enforcement**: `_check_track_amount_gates()` reads JSONB. Keys: `max_utm`, `min_clp`, `puntaje_min` (F2→F3), `cgr_res30_utm`, `licitacion_max_days` (F3→F4), `sisrec_mandatory_utm` (F4→F5), `core_approval`. `_get_ipr_monto()` reads `metadata->>'monto_total'`.
40. **Financial thresholds**: `core.financial_threshold` (10 rows: 4 UTM + 5 glosa% + UTM_VALUE). Helpers: `_get_utm_value()`, `_get_threshold()`, `_check_utm_threshold()`.
41. **Glosa rules**: `check_glosa_rules(ipr_id, db)` → 5 limits + `_check_glosa03_prohibition()` (FNDR→PERSONAL blocked). At F3→F4.
42. **Budget classifier**: 6 levels complete. List accepts `item`, `allocation`, `program_type`, `program_code` filters. Level 3 via `budget_program_code` scheme + admin CRUD.
43. **Track gate functions** (all in `ipr.py` via `_evaluate_phase_gates()`):
    - FRIL: `_check_fril_max_per_comuna` (F0→F1, max 5, A2/A3 exempt), `_check_fril_fraccionamiento` (F1→F2, ±90d), `_check_fril_tender_deadline` (F3→F4)
    - SNI: `_check_sni_proporcionalidad` (F1→F2, 4 levels by UTM), `_check_rs_vigencia` (F3→F4, expiry per `rs_validity_years`)
    - C33: `_check_c33_conservation` (F1→F2, informational)
    - SUBV8: `_check_pagare_notarial` (F2→F3, ≥100%+≥18mo), `_check_directorio_certificate` (F2→F3), `_check_morosos_sisrec` (F3→F4+F4→F5), `_check_ranking_persistence` (F2→F3, informational)
    - ALL: `_check_evaluation_type_match` (F2→F3, informational), `_check_glosa06_single_purpose` (F1→F2), `_check_glosa06_direct_executor` (F1→F2, GORE-NUBLE EJECUTOR for GLOSA06)
    - TRANSFER: `check_glosa07_transfer_limits` (F3→F4, 5% caps via `_GLOSA07_LIMITS` in presupuesto.py)

### Evaluation & Compliance

44. **Evaluation**: `numeric_score` NUMERIC(5,2) on `evaluation_assignment`. `rank_position`, `rank_total`, `convocatoria_code`. `core.sni_level_config` (4 levels, admin CRUD).
45. **Kinship (HΩ-02)**: `core.kinship_declaration` UNIQUE(ipr_id, person_id, declaration_type). CRUD via `/api/ipr/{id}/parentesco`. Gate `_check_kinship_declarations()` at F1→F2 for SUBV8 only. Authority roles: GOBERNADOR, CONSEJERO_REGIONAL, SECRETARIO_EJECUTIVO, ADMIN_REGIONAL, JEFE_DIVISION. Person search: `GET /api/catalogs/persons?search=`.
46. **Admissibility**: PRE_ADMISIBLE between EN_REVISION and ADMISIBLE. `core.admissibility_item` (parametric/track) + `core.admissibility_check` (per IPR). Gate blocks PRE_ADMISIBLE→ADMISIBLE until all verified. Admin CRUD: `/api/admin/admissibility-items`. IPR: `GET/POST/DELETE /api/ipr/{id}/admisibilidad`. Role-restricted to `responsible_role` or ADMIN_SISTEMA.
47. **C33 certification**: `categoria_c33` scheme (EDIFICACION→SERVIU, VIALIDAD→MOP). Cert data in `core.ipr.metadata` with `cert_` prefix. Gate blocks F1→F2. `GET/POST/PATCH /api/ipr/{id}/certificacion-tecnica`. JEFE_DIVISION+ request, ADMIN_REGIONAL/ADMIN_SISTEMA resolve.
48. **Budget cycle (TP-05)**: `core.budget_cycle_milestone` (17 seed) + `core.budget_cycle_tracking`. 5 endpoints: `GET /ciclo/hitos`, `POST /ciclo/{year}`, `GET /ciclo/{year}`, `GET /ciclo/{year}/resumen`, `PATCH /ciclo/tracking/{id}`. States: PENDIENTE/EN_CURSO/COMPLETADO/OMITIDO. Frontend: `/presupuesto/ciclo`. Sidebar: "Ciclo Ppto."
49. **SISREC 8-Phase CGR (TP-06)**: `core.rendition_phase` (8 seed). External phases 1-3 as metadata JSONB timestamps. Phase 8 via `archived_at`. Escalation: `core.rendition_escalation` (3 levels: 1x, 1.5x, 2x SLA). `_STATE_TO_PHASE_CODE` mapping. `POST /rendiciones/check-escalations` batch-detects overdue → alerts.
50. **Parametric tables (TP-02/04)**: `core.subv8_fund` (7) + `core.subv8_fund_ceiling` (~22, functional UNIQUE via `COALESCE(area, '')`). `core.fril_category` (12 A1-D3, `is_exempt_commune_limit` for A2/A3). Admin CRUD: 8 subv8 + 3 FRIL + routing query `GET /financing-tracks/routing?ipr_id=X`.

### UI Rules

51. **Shared components (Wave 2)**: All list pages → `PageHeader`. All empty states → `EmptyState`. All destructive actions → `ConfirmDialog`. 25 components in `web/src/components/`.
52. **Identity (Wave 1)**: GORE Ñuble branding. OKLCH palette (GOREAZUL #031B5F, GORECELESTE #196AB0). 3 fonts: Plus Jakarta Sans (body), Roboto Slab (headings, auto h1/h2), JetBrains Mono (mono). Dark sidebar always. Theme toggle with FOUC-prevention in `layout.tsx`. `GoreMark` SVG.
53. **Motion (Wave 3)**: CSS-only fade-ins via tw-animate-css 1.4.0. Classes: `animate-in fade-in duration-{200,300}`. Stagger: `delay-{75,150,200,300}` + `fill-mode-both`. `prefers-reduced-motion` in globals.css. Applied: PageHeader, Dashboard KPIs (stagger), DataTable, Login (sequential). NOT: sidebar, DrawerPanel/Sheet (Radix-animated), skeletons.
54. **IPR detail**: 16 tabs in `tab-*.tsx` — self-contained (13 original + tab-modificaciones + tab-cierre + tab-evaluacion-expost). Main page uses extracted components (IprHeroCard, IprPhaseStepper, IprTransitionPanel). Tab Cierre: single-record pattern (UNIQUE per IPR), create/sign flow, phase-gated to F5 states.
55. **Process Catalog (DGI)**: `/procesos` list (FilterBar status/criticality/search, DataTable 7 cols, DrawerPanel create) + `/procesos/[id]` detail (hero, 6-state FSM `PROCESS_FSM`, edit drawer, 5 tabs: actors, rules, metrics, pain-points, opportunities). All tabs accept `canEdit` prop. `tab-opportunities.tsx` bridges Process→Opportunity→Initiative (MP-013). API: `GET/POST /api/dgi/processes`, `PATCH /api/dgi/processes/{id}`, 5 satellite CRUD endpoints per process.
56. **Bottleneck Detection (DGI)**: `/cuellos-de-botella` (scan cards + DataTable investigations) + `[id]` detail (linear 6-state FSM, 6 phase-gated textarea fields). `isFieldEditable()` excludes CERRADO. API: `GET /api/dgi/data/bottlenecks/scan`, `GET/POST /api/dgi/data/bottlenecks`, `PATCH /api/dgi/data/bottlenecks/{id}`.
57. **Indicator Enhancement (DGI)**: `indicadores.tsx` domain config. 5 DGI dimensions (PRESUPUESTO/CARTERA_IPR/CONVENIOS/TDE/RIESGOS). Lifecycle filter+columns. `NuevoIndicadorAction` (JEFE_DGI). Manual value entry (MANUAL/EXTERNAL + VIGENTE). Lifecycle transitions with ConfirmDialog for Deprecar.
58. **DMAIC Structured Improvement (Wave C)**: `/tablero/[id]` detail page with 5-phase stepper (DEFINE/MEASURE/ANALYZE/IMPROVE/VERIFY). DMAIC content stored in `dgi_initiative.metadata` JSONB via atomic `jsonb_set`. Phase-gated editing (same pattern as bottleneck). Gate validation (informational). API: `GET/PATCH /api/dgi/initiatives/{id}/dmaic/{phase}`, `POST /dmaic/transition`, `GET /dmaic/history`. Lean metrics panel on `/tablero`: throughput, lead/cycle time, WIP, aging. `GET /api/dgi/initiatives/lean-metrics`. DB: `started_at`/`completed_at` auto-set by `trg_initiative_timing` trigger.
59. **Process Analytics (Wave C)**: `/procesos/progreso` dashboard (process status by division + DMAIC pipeline KPIs). `tab-metrics.tsx` "Comparar" toggle (BASELINE↔POST_MEJORA). `tab-opportunities.tsx` "Matriz" toggle (3×3 impact/effort grid, Quick Wins highlight). API: `GET /api/dgi/processes/impact-effort`, `GET /api/dgi/processes/{id}/metrics/comparison`. KanbanCard: `agingDays` badge (green <7d, amber 7-14d, red >14d), click→detail navigation.
60. **Coordination (Wave B)**: `/coordinacion` 2 tabs: "Preparación AR" (3 KPI cards from cockpit data) + "Decisiones AR" (DataTable CRUD). `/coordinacion/divisiones` matrix view (color-coded last interaction, create drawer). API: `GET /api/dgi/coordination/ar/prep`, CRUD decisions + interactions.
61. **Escalation Protocol (Wave B)**: `/escalamiento` list (status filter tabs, DataTable, create drawer with level select) + `/escalamiento/[id]` detail (hero, 4-state FSM stepper, editable textareas gated by state, deadline countdown). Cockpit card: "Escalamientos Activos" with level badges.
62. **Service Catalog (Wave B)**: `/servicios` card grid (area filter CG/MP/TD/KC, create JEFE_DGI only) + `/servicios/[id]` detail (3 tabs: Info, SLAs inline, Requests DataTable). `/servicios/solicitar` form (all populations). Cockpit card: "SLA Cumplimiento" with semáforo. API: 12 endpoints covering catalog, requests FSM, SLAs, dashboard.
63. **TD Committee (Wave D)**: `/comite-td` list (DataTable, status filters, create drawer) + detail panel inline (topics with agreements, add topic, iniciar/finalizar actions). `dgi_td_sessions.py` thin wrapper over `core.session` tables (committee `COMITE-TD`). No voting/quorum.
64. **Consolidated Calendar (Wave D)**: `/calendario` agenda view (date range, type filter chips, cards grouped by date with severity semáforo). UNION ALL over 5 sources: sessions, interactions, decisions, escalations, SLAs. API: `GET /api/dgi/coordination/calendar`.
65. **Demo Data Wave B**: `goreos_seed_demo_wave_b.sql` (3 AR decisions, 3 escalations, 4 services, 3 SLAs, 4 requests, 3 interactions). `goreos_unseed_demo_wave_b.sql` removes DEMO- records only.
66. **Risk Register (Wave E)**: `/riesgos` list (status filter tabs, DataTable, create drawer with risk type/probability/impact selects + ComboboxAsync for subject, risk matrix toggle). `/riesgos/[id]` detail (hero card, 6-state FSM stepper, mitigation plan textarea gated by state, transition buttons with ConfirmDialog, subject link navigation). API: `risk.py` 8 endpoints.
67. **Centro de Mando (Wave E)**: `/centro-de-mando` 3×2 KPI grid with semáforo (green/amber/red thresholds) + timeline section. Cards: Escalamientos, Alertas, Riesgos, Decisiones, Reuniones, SLA Vencidos — each clickable drill-down. Roles: ADMIN_REGIONAL, GOBERNADOR, ADMIN_SISTEMA, JEFE_DGI. Sidebar: both populations.
68. **Crisis→Decision Bridge (Wave E)**: `POST /api/reuniones/{id}/decisiones` creates AR decision linked via `source_session_id`. `GET /api/reuniones/{id}/decisiones` lists decisions from meeting.
69. **Demo Data Wave E**: `goreos_seed_demo_wave_e.sql` (5 DEMO-RSK risks, mixed statuses/types). `goreos_unseed_demo_wave_e.sql` removes DEMO- records only.

### Structural Refactoring + Visual Refresh (C38)

70. **Sidebar Semántico**: 5-7 collapsible `NavSection` per population (replaces 17-item flat list). State persisted in `localStorage`. Cross-population: Servicios visible in operativa. `components/nav-section.tsx` + `components/ui/collapsible.tsx`.
71. **Breadcrumbs**: `components/breadcrumb.tsx` + `lib/breadcrumbs.ts`. `buildBreadcrumbs(pathname, entityLabel?)`. 18 detail/create pages. Coexists with back arrow.
72. **PageGuard**: `components/page-guard.tsx` — `allowedRoles?`, `allowedPopulations?`, `skeleton?`. 7 pages adopted (admin, centro-de-mando, comité-td, calendario). Opt-in for rest.
73. **URL Tabs**: `hooks/use-tab-param.ts` — sync Radix Tabs with `?tab=` search param. IPR detail 15 tabs bookmarkable. `router.replace(pathname + "?" + params, { scroll: false })`.
74. **Dashboard Decomposition**: `page.tsx` 479→13 lines. Extracted: `operational-dashboard.tsx` (~280 lines), `dgi-cockpit-router.tsx` (~40), `executive-breakdown.tsx` (~60). Now routes to unified `CommandCenter`.
75. **Drawer Unification**: Sheet raw → DrawerPanel in 5 pages (escalamiento, riesgos, servicios, coordinación, comité-td). ADR: `docs/adr/008-create-pattern-drawer-vs-page.md`.
76. **Centro de Comando Personal**: `GET /api/dashboard/action-items` — computed coproduct of 6 sources (commitments, alerts, AR decisions, escalations, SLA breaches, risks). Priority: `SEV*5 + TEMP` total order. Role scoping: 16 roles in 5 groups. Frontend: `command-center.tsx` orchestrator + `attention-strip.tsx` (urgent cards) + 4 conditional modules (MyProgress, MyTeam, DgiTeam, KPIs).
77. **Table Enrichment**: `progress-cell.tsx` (inline bar, green/amber/red), `deadline-cell.tsx` (date + semáforo), `trend-indicator.tsx` (↑↓→). Integrated in presupuesto, compromisos, convenios, escalamiento.
78. **Domain Color Accents**: `PageHeader.accentColor` prop → 3px left border. 7 domains: indigo(IPR), amber(compromisos), emerald(finanzas), violet(institucional), rose(riesgos), cyan(DGI), teal(servicios). Applied to 15 list pages. Tailwind static `ACCENT_BORDER` mapping (no dynamic classes).
79. **DetailPageLayout**: `components/detail-page-layout.tsx` — opt-in wrapper: breadcrumbs, hero slot, display-only stepper (phase colors), transition panel slot.
80. **IPR StatusBadge Colors**: `status-badge.tsx` expanded with 32 IPR states, phase-based color coding (F0=slate, F1=blue, F2=cyan, F3=purple, F4=green, F5=gray). Cierre tab added to IPR detail (16th tab).

### IPR Lifecycle (C37)

81. **IPR states (32 total)**: 28 original + 4 new (TERMINADO_ANTICIPADAMENTE, CONTRATO_FIRMADO, RENDICION_APROBADA, EN_CIERRE_ADMINISTRATIVO). `STATUS_PHASE_FIBER` dict maps all 32 to phases. Nature-aware gates: PROYECTO bifurcates EN_FORMALIZACION→EN_LICITACION→ADJUDICADO→CONTRATO_FIRMADO→EN_OBRA; PROGRAMA goes EN_FORMALIZACION→FORMALIZADO→EN_EJECUCION. ANULADO+TERMINADO_ANTICIPADAMENTE cross-cutting from most non-terminal states.
82. **IPR modifications**: `core.ipr_modification` table. Code: `MOD-{year}-{seq:04d}` (advisory lock). FSM: SOLICITADA→EN_REVISION→APROBADA/RECHAZADA (DB trigger enforced). 5 types: PRESUPUESTO, PLAZO, ALCANCE, EJECUTOR, TECNICO. Endpoints: `GET/POST /api/ipr/{id}/modificaciones`, `PATCH /api/ipr/{id}/modificaciones/{mod_id}`. WRITE_OPERATIONAL_ROLES create, ADMIN_REGIONAL+ approve/reject. Gate `_check_pending_modifications()` informational at F4→F5.
83. **IPR closure**: `core.ipr_closure` (UNIQUE per IPR). Fields: closure_date, physical/financial_completion, final_amount, signed_by_id/signed_at. Gate `_check_closure_requirements()` blocks EN_CIERRE_ADMINISTRATIVO→CERRADO without signed closure. `core.ipr_expost_evaluation` (multiple per IPR, post-CERRADO). 4 dimension scores + overall_rating. 3 eval types: SIMPLIFICADA, PROFUNDIDAD, IMPACTO.
84. **ITO gate + SLAs**: ITO (Inspector Técnico de Obra) via `ipr_party_role` scheme. Gate `_check_ito_assigned()` blocks EN_LICITACION→ADJUDICADO for PROYECTO without ITO party. `phase_entered_at` column + trigger `trg_ipr_phase_entered` auto-updates on status change. Evaluation SLA via `sla_days.evaluation_max_days` in `financing_track`. Batch endpoints: `POST /api/ipr/check-report-compliance`, `POST /api/ipr/check-evaluation-slas`.
