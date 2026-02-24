# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GORE_OS is an institutional operating system for the Regional Government of Ñuble (GORE), Chile. It serves two user populations on a shared PostgreSQL database:

- **Operativa** (ADMIN_SISTEMA, ADMIN_REGIONAL, JEFE_DIVISION, ENCARGADO): Manage IPR crisis — commitments, problems, alerts. Replaces Excel workflows.
- **DGI** (JEFE_DGI, ESP_CONTROL_GESTION, ESP_PROCESOS, ESP_TD): Monitor institutional indicators, analyze data, generate reports, manage improvement initiatives.

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

# Database shell:
docker exec goreos_db psql -U goreos -d goreos_model

# View logs:
docker compose logs -f api
docker compose logs -f web

# Rebuild after code changes (volumes mount source, so usually auto-reload):
docker compose build api && docker compose up -d api
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
- `api/app/routers/` — 11 routers (auth, ipr, compromisos, problemas, alertas, dashboard, catalogs, dgi_cockpit, dgi_initiatives, dgi_data, dgi_reports)

API conventions:
- All routes prefixed `/api/` (e.g., `/api/ipr`, `/api/dgi/cockpit`)
- Paginated endpoints return `{items, total, page, page_size, total_pages}`
- DGI list endpoints return plain arrays (not paginated)
- Dashboard endpoint (`GET /api/dashboard`) is role-aware: dispatches to different queries per role
- DGI cockpit endpoint (`GET /api/dgi/cockpit`) returns different response shapes per DGI role
- Person table columns: `names`, `paternal_surname` (NOT `nombre`, `apellido_paterno`)
- User table FK: `system_role_id` (NOT `role_id`)

### Frontend (`web/`)

- **Framework**: Next.js 16 (App Router, Turbopack), TypeScript, TailwindCSS v4
- **Components**: shadcn/ui (Radix UI) — installed in `web/src/components/ui/`
- **Icons**: lucide-react
- **State**: React Context (`useAuth`) + URL params (`useSearchParams`) for filters

Key patterns:
- `web/src/lib/api.ts` — singleton `ApiClient` with `get<T>()`, `post<T>()`, `patch<T>()`. Token in localStorage (`goreos_token`). Auto-redirect to `/login` on 401.
- `web/src/lib/auth.tsx` — `AuthProvider` context, `useAuth()` hook returns `{user, loading, login, logout}`
- `web/src/types/index.ts` — all TypeScript interfaces. `User.population` (`"operativa" | "dgi"`) drives sidebar/dashboard routing.
- `web/src/components/sidebar.tsx` — conditional nav: `operationalNav` vs `dgiNav` based on `user.population`
- `web/src/app/(app)/layout.tsx` — AppShell wrapper for authenticated routes
- `web/src/app/(app)/dashboard/page.tsx` — detects population, renders operational dashboard or DGI cockpit component per role

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

# Frontend lint
cd web && npx eslint src/

# API docs (Swagger UI)
open http://localhost:8000/api/docs
```

## Domain Model

Central entity: **IPR (Intervención Pública Regional)** — polymorphic (7 types: INFRAESTRUCTURA, EQUIPAMIENTO, TRANSFERENCIA, PROGRAMA_SOCIAL, PROGRAMA_8PCT, CONSERVACION, ESTUDIO).

Operational layer:
- **operational_commitment**: Tasks with due dates, state machine (PENDIENTE → EN_PROGRESO → COMPLETADO → VERIFICADO), tracked via `commitment_history`
- **ipr_problem**: Issues detected on IPRs (ABIERTO → EN_GESTION → RESUELTO), typed (TECNICO, FINANCIERO, LEGAL, etc.)
- **alert**: System-generated warnings with severity (CRITICO, ALTO, ATENCION, INFO), can be attended/resolved

DGI layer:
- **dgi_indicator**: Institutional semaphore (5 dimensions: PRESUPUESTO, CARTERA_IPR, CONVENIOS, TDE, RIESGOS) with signal (VERDE/AMARILLO/ROJO)
- **dgi_initiative**: Kanban board with WIP limits, optional DMAIC phases
- **dgi_report**: Institutional reports (FLASH, SEMANAL, MENSUAL, TEMATICO)

## Key References

- `model/model_goreos/sql/goreos_ddl.sql` — DDL (77 tables), ontological mappings in lines 21-37
- `model/model_goreos/sql/goreos_seed.sql` — 90+ category schemes
- `model/model_goreos/docs/GOREOS_ERD_v3.md` — ERD + data dictionary
- `model/GLOSARIO.yml` — 244 ontological terms (Gist 14.0 + GNUB + TDE)
- `docs/plans/2026-02-24-dgi-ui-ux-design.md` — DGI UI/UX design document
- `architecture/Omega_GORE_OS_Definition_v3.0.0.md` — system specification

## Critical Rules

1. **Categorical Univocity**: Each FK column → exactly 1 `ref.category` scheme. Never mix dimensions.
2. **Person columns**: Use `names` and `paternal_surname` (NOT `nombre`/`apellido_paterno`). User FK: `system_role_id` (NOT `role_id`).
3. **API consistency**: Operational endpoints use POST for state changes (e.g., `POST /compromisos/{id}/completar`). DGI list endpoints return plain arrays. Paginated endpoints return `{items, total, page, page_size, total_pages}`.
4. **Alert subject_type**: Stored as `'core.ipr'` in DB (fully qualified), not `'ipr'`.
5. **Docker network**: `goreos_db` is on `visor_model_default` (external). Don't create a separate postgres service unless using `--profile standalone`.
6. **No ORM models**: Backend uses raw SQL with `text()` from SQLAlchemy. All queries go through `db.execute(text("..."), params).mappings()`.
