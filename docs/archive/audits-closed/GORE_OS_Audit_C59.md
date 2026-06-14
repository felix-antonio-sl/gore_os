# GORE_OS — Auditoría Exhaustiva C59

**Fecha**: 2026-03-22 | **Versión**: 1.0 | **Sesión**: C59
**Auditores**: 4 agentes paralelos (backend, frontend, database, cross-cutting)
**Hallazgos**: 121 totales (10 CRITICO, 32 ALTO, 51 MEDIO, 28 BAJO)

---

## Resumen Ejecutivo

| Dominio | CRITICO | ALTO | MEDIO | BAJO | Total |
|---------|:-------:|:----:|:-----:|:----:|:-----:|
| Backend (29 routers, ~26K líneas) | 4 | 10 | 17 | 11 | 42 |
| Frontend (60 pages, 61 components, ~38K líneas) | 2 | 9 | 15 | 7 | 33 |
| Database (117 tables, 148 CHECKs, 88 triggers) | 4 | 8 | 10 | 4 | 26 |
| Cross-cutting (backend ↔ frontend) | 0 | 5 | 9 | 6 | 20 |
| **TOTAL** | **10** | **32** | **51** | **28** | **121** |

---

## Top 10 — Bugs Live en Producción

| # | Issue | Archivo | Fix |
|---|-------|---------|-----|
| 1 | Scheme `administrative_act_step` no existe → pendientes firma GOBERNADOR = 0 | dashboard.py:469 | Cambiar a `act_state` |
| 2 | Change-password URL sin `/api` → 404 | header.tsx:66 | Agregar `/api` prefix |
| 3 | Riesgos catalogs query params → dropdowns vacíos | riesgos/page.tsx:82-84 | Cambiar a path params |
| 4 | ConvenioDetail rendition counts stripped por Pydantic → Art.18 nunca muestra | schemas/convenio.py:50 | Agregar campos al schema |
| 5 | DashboardAlert sin alert_type_label → heading blank | schemas/dashboard.py:23 | Agregar campos + SQL |
| 6 | Cockpit JEFE_DGI links `/rendiciones` → 404 | cockpit-jefe-dgi.tsx:122,128,373 | Cambiar a `/datos?dominio=rendiciones` |
| 7 | 0 error boundaries → crash = pantalla blanca | Sin error.tsx | Crear error.tsx |
| 8 | 80+ `.catch(() => {})` → dropdowns vacíos sin feedback | 37 archivos | Agregar error states |
| 9 | IDOR detail endpoints → cualquier user lee cualquier IPR | ipr.py:2573 | Agregar scope check |
| 10 | 234 FKs sin index + document/budget sin indexes | DB | CREATE INDEX |

---

## A1. BACKEND (42 hallazgos)

### CRITICO (4)

#### B-C1. SQL injection pattern en auth.py
- **Archivo**: `api/app/routers/auth.py:54`
- **Issue**: `lock_clause = f"... INTERVAL '{_LOCKOUT_MINUTES} minutes'"` interpolado en `text()`. Constante hoy, pero patrón peligroso.
- **Fix**: Usar parámetro `:lockout_interval * INTERVAL '1 minute'`

#### B-C2. Admin reset-password sin validación de fuerza
- **Archivo**: `api/app/schemas/admin.py:31`
- **Issue**: `ResetPasswordBody.new_password` sin `min_length`. `UserCreate.password` igual.
- **Fix**: Agregar `Field(min_length=8)` a ambos

#### B-C3. JWT sin claims iss/aud
- **Archivo**: `api/app/core/security.py:36-40`
- **Issue**: Token solo tiene `sub` y `exp`. Sin `iss`, `aud`, `iat`. Expiry 8h es generoso.
- **Fix**: Agregar claims, considerar reducir expiry a 60-120 min

#### B-C4. DB password hardcoded como default
- **Archivo**: `api/app/core/config.py:9-12`
- **Issue**: `DB_PASSWORD: str = "goreos_2026"` sin validator para producción (a diferencia del JWT secret).
- **Fix**: Agregar `model_validator` que rechace default cuando `ENV != "development"`

### ALTO (10)

#### B-A1. Bare `except Exception` en 14 routers
- **Archivos**: actos.py:480, compromisos.py:352, problemas.py:246, convenios.py:600, admin.py (6), core_sessions.py (2), reuniones.py:259
- **Fix**: Catch `DBAPIError`/`SQLAlchemyError` específicamente

#### B-A2. Silent exception swallowing en ipr.py evaluaciones
- **Archivo**: `ipr.py:2550-2552`
- **Issue**: `except Exception: evaluations = []` — silencioso
- **Fix**: Catch `ProgrammingError` específico, log warning

#### B-A3. N+1 en check-payment-slas
- **Archivo**: `convenios.py:467-512`
- **Issue**: 2 queries por cada convenio VIGENTE
- **Fix**: Bulk INSERT con NOT EXISTS

#### B-A4. N+1 en _evaluate_phase_gates
- **Archivo**: `ipr.py:1534-1815`
- **Issue**: 15-20 queries por transición, `/readiness` multiplica por destinos
- **Fix**: Consolidar gate checks en 2-3 CTEs

#### B-A5. N+1 correlated subqueries en convenios list
- **Archivo**: `convenios.py:314-315`
- **Issue**: 2 subqueries por fila para installment counts
- **Fix**: Lateral join o CTE pre-aggregate

#### B-A6. IDOR en IPR detail — sin scope check
- **Archivo**: `ipr.py:2573-2702`
- **Issue**: `GET /api/ipr/{id}` accesible a cualquier user autenticado, sin verificar relación
- **Fix**: Agregar scope check como en list

#### B-A7. Global search sin role scope
- **Archivo**: `search.py:11-74`
- **Issue**: Busca en IPR/compromisos/personas sin filtro de rol
- **Fix**: Agregar scope filters matching list endpoints

#### B-A8. Cuota PATCH sin allowlist
- **Archivo**: `convenios.py:1007-1032`
- **Issue**: `model_dump(exclude_none=True)` sin filtrar columnas
- **Fix**: Agregar `_CUOTA_ALLOWLIST`

#### B-A9. ipr.py 5,507 líneas — god module
- **Archivo**: `ipr.py`
- **Fix**: Split en ipr_gates.py, ipr_satellites.py, ipr_lifecycle.py, ipr_crud.py

#### B-A10. Mechanism queries repetidos 10+ veces en gates
- **Archivo**: `ipr.py:546-1505`
- **Fix**: Fetch mechanism una vez y pasar a cada gate function

### MEDIO (17)

#### B-M1. `_require_roles` duplicado en 10 routers
- **Fix**: Usar shared utility o deps.py `require_roles`

#### B-M2. `_get_utm_value` duplicado en 3 routers
- **Fix**: Extraer a `core/financial.py`

#### B-M3. Missing LIMIT en catalogs
- **Fix**: Agregar LIMIT 500

#### B-M4. N+1 SUBJECT_LABEL_SUBQUERY en alertas
- **Archivo**: `alertas.py:37-56`
- **Fix**: Usar LEFT JOINs

#### B-M5. dgi_cockpit exception swallowing
- **Fix**: Log exception, incluir error indicator

#### B-M6. Paginación inconsistente (PaginatedResponse vs dict)
- **Fix**: Estandarizar a PaginatedResponse

#### B-M7. Problemas list sin scope para PERSONAL_SCOPE_ROLES
- **Fix**: Agregar filtro como compromisos

#### B-M8. Dead code auth.py:52
- **Fix**: Remover línea

#### B-M9. Missing deleted_at en ipr_closure query
- **Archivo**: `ipr.py:2931-2938`
- **Fix**: Agregar `AND deleted_at IS NULL`

#### B-M10. get_compromiso retorna .model_dump()
- **Fix**: Retornar model instance con response_model

#### B-M11. IPR list filter usa stored mcd_phase_id vs derived
- **Fix**: Derivar fase desde status en list query

#### B-M12. audit.py silently drops unknown event_types
- **Fix**: Log warning

#### B-M13. Optional import inconsistente
- **Fix**: Usar `X | None` everywhere

#### B-M14. Missing deleted_at en algunos DGI queries
- **Fix**: Agregar filtros

#### B-M15. Batch SLA check_fril_max_per_comuna N+1 per territory
- **Fix**: Single query con GROUP BY

#### B-M16. Inconsistent HTTP status on action endpoints
- **Fix**: Estandarizar

#### B-M17. Alertas sin scope para PERSONAL_SCOPE_ROLES
- **Fix**: Agregar filtro

### BAJO (11)

- Magic number 67_294 UTM en 4 archivos → named constant
- Unused imports (JSONResponse, select)
- `_add_months` reimplementado → dateutil
- Duplicate comment SLA
- DELETE para undo action (semántica REST)
- Dead `if page_size else 0` branch
- UUID parameter casting inconsistente
- dgi_cockpit refresh all-or-nothing

---

## A2. FRONTEND (33 hallazgos)

### CRITICO (2)

#### F-C1. 0 error boundaries
- **Issue**: Sin `error.tsx` en toda la app. Crash = pantalla blanca.
- **Fix**: Crear `app/(app)/error.tsx` mínimo

#### F-C2. 80+ `.catch(() => {})` silenciosos
- **Issue**: Catalog fetches swallow ALL errors. Dropdowns vacíos sin feedback.
- **Fix**: Shared `useCatalog` hook con retry y error display

### ALTO (9)

#### F-A1. convenios/page.tsx 972 líneas
- **Fix**: Extraer ConvenioDrawer, CuotaForm, BulkCuotaForm, PaymentDialog

#### F-A2. Auth localStorage sin integridad
- **Issue**: `goreos_user` editable en devtools → escalación de rol frontend
- **Fix**: Decodear JWT para extraer rol, o validar contra `/api/auth/me`

#### F-A3. Change-password path sin `/api`
- **Archivo**: `header.tsx:66`
- **Fix**: Cambiar a `/api/auth/change-password`

#### F-A4. 5 pages sin PageHeader (tablero, datos, informes, mis-compromisos, mi-division)
- **Fix**: Agregar PageHeader con accentColor

#### F-A5. Inline Intl.NumberFormat en 2 archivos
- **Archivos**: ipr-convenio-drawer.tsx:158, tab-convenios.tsx:57
- **Fix**: Usar `formatCLP` de lib/format.ts

#### F-A6. 19 eslint-disable exhaustive-deps
- **Fix**: useCallback con deps correctos

#### F-A7. `@dnd-kit` sin lazy-load
- **Archivo**: tablero/page.tsx
- **Fix**: `next/dynamic` para lazy-load

#### F-A8. api.login() untyped (returns `any`)
- **Fix**: Definir LoginResponse interface

#### F-A9. api.fetch() calls res.json() en 204
- **Fix**: Check `res.status === 204` antes de parsear

### MEDIO (15)

- DataTable `unknown[]` sin generics
- `useSearchParams` sin Suspense en 20 pages
- Parallel API calls sin AbortController
- loadTransitions stale closure
- No request deduplication (catalogs fetch on every mount)
- Users fetched en `<Select>` en vez de ComboboxAsync
- Alert severity dots sin text labels (a11y)
- Alertas page sin accentColor
- Notification delete button invisible (parent sin `group` class)
- Acentos faltantes en notification-panel copy
- Roles hardcoded en 15+ locations → centralizar en lib/permissions.ts
- PageGuard solo en 10/60 pages
- toLocaleDateString en vez de formatDate
- All 60 pages son "use client" (0 server components)
- Cartera sin virtualización (mitigado por paginación)

### BAJO (7)

- `params.id as string` unchecked
- UserOption duplicado en 6+ files
- ExpostEvalItem definido local en vez de types/
- IPR sticky header raw mechanism code
- IPR sticky header raw mcd_phase code
- `STATUS_TO_PHASE` dead code violando rule 38

---

## A3. DATABASE (26 hallazgos)

### CRITICO (4)

#### D-C1. `administrative_act_step` scheme no existe
- **Archivo**: `dashboard.py:469`
- **Issue**: Pendientes firma GOBERNADOR siempre retorna 0
- **Fix**: Cambiar a `act_state`

#### D-C2. 234 FKs sin indexes
- **Fix**: CREATE INDEX en FKs de tablas >1000 rows (prioridad)

#### D-C3. document tabla sin index en ipr_id (12,800 rows, 868 seq_scans)
- **Fix**: `CREATE INDEX idx_document_ipr ON core.document(ipr_id) WHERE ipr_id IS NOT NULL`

#### D-C4. budget_program sin index en division (25,767 rows)
- **Fix**: `CREATE INDEX idx_budget_program_division ON core.budget_program(owner_division_id)`

### ALTO (8)

- 5 history tables vacías (triggers no disparan)
- resolution 96% sin IPR link (ETL gap)
- ipr.investment_sector_id 94% NULL
- ipr.executor_id 56% NULL (redundante con ipr_party)
- ipr_territory UNIQUE no soft-delete aware
- 9 FSM tables sin transition trigger
- ipr.formulator_id 100% NULL (redundante)
- pg_stat stale (ANALYZE nunca corrió en 58 tablas)

### MEDIO (10)

- 18 schemes orphan sin CHECK constraint
- 9 duplicate CHECK constraints en DGI tables
- 29 tables sin deleted_at
- 9 tables sin created_at
- agreement.cgr_outcome_id 78% NULL
- person.email 52% NULL
- 2 redundant GIN indexes en ipr.metadata
- ipr_state tiene 3 non-state codes mezclados
- rendition.agreement_id 95% NULL
- ipr_party 23K seq_scans vs 5K idx_scans

### BAJO (4)

- 23 scaffold tables vacías
- meta schema sin usar (4/5 tables = 0 rows)
- budget_commitment 20% dead tuples
- Migrations OK (51/51 match)

---

## A4. CROSS-CUTTING (20 hallazgos)

### ALTO (5)

#### X-A1. Change-password URL rota
- **Backend**: `POST /api/auth/change-password`
- **Frontend**: `api.post("/auth/change-password", ...)` — sin `/api`
- **Fix**: Agregar prefix

#### X-A2. Riesgos catalogs query→path params
- **Backend**: `GET /api/catalogs/categories/{scheme}` (path)
- **Frontend**: `?scheme=risk_type` (query)
- **Fix**: Cambiar a path params

#### X-A3. ConvenioDetail rendition counts stripped
- **Backend**: Computa pending_renditions/blocked_renditions pero Pydantic los stripea
- **Fix**: Agregar campos al schema ConvenioDetail

#### X-A4. DashboardAlert heading blank
- **Backend**: DashboardAlert solo tiene 6 campos, falta alert_type_label/subject_label
- **Fix**: Agregar campos al schema + SQL

#### X-A5. Cockpit links `/rendiciones` → 404
- **Frontend**: cockpit-jefe-dgi.tsx usa `/rendiciones`, no existe
- **Fix**: Cambiar a `/datos?dominio=rendiciones`

### MEDIO (9)

- WRITE_OPERATIONAL_ROLES mismatch frontend/backend
- Centro de Mando visible a ESP_* pero 403
- IprDetail TS tiene phantom fields (description, start_date, end_date, total_budget nunca vienen del API)
- DashboardData types usan interfaces equivocadas
- Login swallows lockout message (siempre "Credenciales inválidas")
- English error "Tracking entry not found"
- Technical 500 expone "modification_status SOLICITADA no encontrado"
- CockpitControlGestion missing bottleneck_summary en TS
- ImprovementOpportunity nullability mismatch

### BAJO (6)

- 7 batch SLA endpoints sin frontend callers
- 4 admin parametric CRUD sin pages
- STATUS_TO_PHASE dead code violando rule 38
- RiskDetail.updated_at nullability mismatch
- DGIIndicator lifecycle_status union incompleto
- ExPost create usa `body: dict` sin Pydantic model

---

## Plan de Remediación Propuesto

### Sprint 1 — Bugs Live (inmediato)
1. Scheme `act_state` fix (dashboard.py)
2. Change-password URL prefix
3. Riesgos catalog path params
4. ConvenioDetail schema fields
5. DashboardAlert schema + SQL
6. Cockpit `/rendiciones` → `/datos?dominio=rendiciones`
7. Error boundary (`error.tsx`)
8. Notification panel `group` class fix
9. DB indexes prioritarios (document, budget_program)
10. `ANALYZE` full

### Sprint 2 — Seguridad
1. IDOR scope check en detail endpoints
2. Search scope filtering
3. Admin password validation
4. JWT claims (iss/aud)
5. DB password validator producción
6. Auth.py SQL parameterization
7. Cuota PATCH allowlist

### Sprint 3 — Performance
1. N+1 gate evaluation consolidation
2. N+1 convenio SLA check
3. N+1 alertas SUBJECT_LABEL
4. Correlated subqueries convenios list
5. Mechanism query deduplication

### Sprint 4 — Code Quality
1. ipr.py split (5,500→4 modules)
2. Shared utilities (_require_roles, _get_utm_value)
3. Frontend permissions centralization
4. DataTable generics
5. convenios/page.tsx decomposition
6. PageGuard en restricted pages
7. Silent .catch cleanup (top 20)

### Sprint 5 — Data Quality
1. ETL backfill: executor_id, formulator_id, investment_sector_id
2. Resolution IPR/agreement linking
3. Agreement CGR/amount backfill
4. FSM triggers para 9 tables pendientes
5. ipr_territory UNIQUE soft-delete aware

---

## Handoff Notes

**Estado al cierre de C59**:
- Master: `b8956ba`, clean, pushed
- Tests: 730 collected, 55 modules
- Build frontend: clean
- Docker: api + web + goreos_db running
- Seed realista cargado (DEMO-R-*)
- Notification system: increment 1 complete (plumbing), increment 2 pending (auto-create)

**Archivos clave para remediación**:
- Backend entry: `api/app/routers/ipr.py` (5,507 lines — biggest file)
- Frontend entry: `web/src/app/(app)/convenios/page.tsx` (972 lines — biggest page)
- Schema types: `web/src/types/index.ts` (needs sync with Pydantic schemas)
- Role sets: `api/app/core/security.py` ↔ `web/src/types/index.ts` (must match)
- Test plan: `docs/GORE_OS_Testing_Manual_v1.0.md` (25 users, ~420 steps)

**Prioridad absoluta**: Sprint 1 items 1-6 son bugs live que afectan features en producción.
