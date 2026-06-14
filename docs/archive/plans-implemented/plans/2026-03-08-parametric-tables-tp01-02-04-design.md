# TP-01/02/04 Parametric Tables — Design Document

**Date**: 2026-03-08
**Status**: Approved

## Goal

Complete the 3 remaining parametric tables: TP-01 evaluator routing query, TP-02 Subvención 8% fund distribution with per-institution ceilings, and TP-04 FRIL category taxonomy with exemptions. All with admin CRUD.

## TP-01: Track Evaluation Routing (completar)

### Current State
`core.financing_track` exists with 7 seed rows and admin CRUD (`GET/POST/PATCH /api/admin/financing-tracks`). Missing: query endpoint to resolve IPR → evaluator.

### New Endpoint
`GET /api/admin/financing-tracks/routing?ipr_id=X` — resolves the IPR's financing track and returns evaluator info: `{track_code, track_label, evaluator_code, evaluator_label, favorable_products, sla_days}`. Informational only, no enforcement.

### Logic
1. Read IPR's `financing_track_id` (FK on `core.ipr`)
2. If NULL, try to infer from `ipr_nature` + metadata
3. Return track's evaluator fields from `core.financing_track`

## TP-02: Subvención 8% Fund Distribution

### Data Model

```sql
core.subv8_fund (7 rows)
├─ id UUID PK
├─ code VARCHAR(32) UNIQUE
├─ name TEXT
├─ budget_regular NUMERIC
├─ budget_special NUMERIC
├─ budget_total NUMERIC
├─ is_exclusive BOOLEAN DEFAULT false
├─ sort_order INT
├─ is_active BOOLEAN DEFAULT true
├─ created_at, updated_at TIMESTAMPTZ

core.subv8_fund_ceiling (~30 rows)
├─ id UUID PK
├─ fund_id UUID FK → subv8_fund
├─ institution_type VARCHAR(64)
├─ area VARCHAR(64)
├─ max_amount NUMERIC
├─ notes TEXT
├─ UNIQUE(fund_id, institution_type, area)
├─ created_at, updated_at TIMESTAMPTZ
```

### Seed Data (7 Funds)

| Code | Name | Budget Regular (M$) | Budget Special (M$) | Exclusive |
|------|------|:---:|:---:|:---:|
| CULTURA | Fondo de Cultura | 330.000 | 270.000 | No |
| SOCIAL | Fondo Social e Inclusión | 500.000 | — | No |
| GENERO | Fondo de Equidad de Género | 400.000 | — | No |
| DEPORTE | Fondo de Deporte | 800.000 | 200.000 | No |
| ADULTO_MAYOR | Fondo para Personas Mayores | 400.000 | — | Yes |
| MEDIO_AMBIENTE | Fondo de Medio Ambiente | 400.000 | — | No |
| SEGURIDAD | Fondo de Seguridad Ciudadana | 1.550.000 | — | No |

### Seed Data (Ceilings — representative subset)

| Fund | Institution Type | Area | Max CLP |
|------|-----------------|------|--------:|
| CULTURA | CORPORACION | general | 5.000.000 |
| CULTURA | ORG_CULTURAL | general | 3.500.000 |
| CULTURA | ORG_COMUNITARIA | general | 2.500.000 |
| CULTURA | PRODUCTORA | cine | 60.000.000 |
| CULTURA | PRODUCTORA | festival | 20.000.000 |
| SOCIAL | CORPORACION | general | 5.500.000 |
| SOCIAL | ORG_TERRITORIAL | general | 3.500.000 |
| SOCIAL | RESIDENCIA_MEJOR_NINEZ | exclusivo | 10.000.000 |
| GENERO | ORG_TERRITORIAL | general | 3.500.000 |
| GENERO | CORPORACION | autonomia_mujer | 6.500.000 |
| DEPORTE | ASOCIACION_REGIONAL | general | 10.000.000 |
| DEPORTE | ASOCIACION_COMUNAL | general | 6.000.000 |
| DEPORTE | UNIVERSIDAD | general | 4.000.000 |
| DEPORTE | CLUB_DEPORTIVO | general | 1.800.000 |
| DEPORTE | CORPORACION | organizacion_promocion | 30.000.000 |
| ADULTO_MAYOR | ALL | general | 2.500.000 |
| MEDIO_AMBIENTE | CORPORACION | general | 6.500.000 |
| MEDIO_AMBIENTE | ORG_TERRITORIAL | general | 3.500.000 |
| MEDIO_AMBIENTE | COMITE_APR | paneles_solares | 6.000.000 |
| MEDIO_AMBIENTE | CORPORACION | sendero_sustentable | 25.000.000 |
| SEGURIDAD | ORG_TERRITORIAL | general | 5.500.000 |

### Admin CRUD Endpoints (8)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/admin/subv8-funds` | List funds |
| POST | `/api/admin/subv8-funds` | Create fund |
| PATCH | `/api/admin/subv8-funds/{id}` | Update fund |
| GET | `/api/admin/subv8-funds/{id}/ceilings` | List ceilings for fund |
| POST | `/api/admin/subv8-funds/{id}/ceilings` | Create ceiling |
| PATCH | `/api/admin/subv8-fund-ceilings/{id}` | Update ceiling |
| DELETE | `/api/admin/subv8-fund-ceilings/{id}` | Delete ceiling |
| GET | `/api/admin/subv8-fund-ceilings` | List all ceilings (flat) |

## TP-04: FRIL Category Taxonomy

### Data Model

```sql
core.fril_category (12 rows)
├─ id UUID PK
├─ code VARCHAR(3) UNIQUE
├─ name TEXT
├─ group_code VARCHAR(1)
├─ group_name TEXT
├─ description TEXT
├─ examples TEXT
├─ max_utm NUMERIC(12,2)
├─ is_exempt_commune_limit BOOLEAN DEFAULT false
├─ is_active BOOLEAN DEFAULT true
├─ sort_order INT
├─ created_at, updated_at TIMESTAMPTZ
```

### Seed Data (12 Categories)

| Code | Name | Group | Max UTM | Exempt Commune Limit |
|------|------|:-----:|:-------:|:---:|
| A1 | Integración Rural | A - Desarrollo Territorial | 4545 | No |
| A2 | Acceso al Agua | A - Desarrollo Territorial | 4545 | Yes |
| A3 | Vial | A - Desarrollo Territorial | 4545 | Yes |
| B1 | Edificación Pública | B - Servicios | 4545 | No |
| B2 | Gestión de Riesgos | B - Servicios | 4545 | No |
| B3 | Seguridad | B - Servicios | 4545 | No |
| C1 | Inclusión | C - Desarrollo Social y Económico | 4545 | No |
| C2 | Género | C - Desarrollo Social y Económico | 4545 | No |
| C3 | Turismo | C - Desarrollo Social y Económico | 4545 | No |
| D1 | Deportes | D - Medio Ambiente | 4545 | No |
| D2 | Áreas Verdes | D - Medio Ambiente | 4545 | No |
| D3 | Sustentabilidad | D - Medio Ambiente | 4545 | No |

### Admin CRUD Endpoints (3)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/admin/fril-categories` | List categories |
| POST | `/api/admin/fril-categories` | Create category |
| PATCH | `/api/admin/fril-categories/{id}` | Update category |

### Gate Refactor

`_check_fril_max_per_comuna()` in `ipr.py` — replace hardcoded `("A2", "A3")` with DB query to `core.fril_category WHERE is_exempt_commune_limit = true`.

## Decisions

1. **TP-01**: Query-only endpoint, no enforcement
2. **TP-02**: Two-table model (fund + ceilings) for relational queries
3. **TP-04**: Single table, all 12 categories with same max_utm initially (future differentiation ready)
4. **All 3**: Admin CRUD (GET/POST/PATCH), restricted to ADMIN_SISTEMA
5. **Gate refactor**: Only `_check_fril_max_per_comuna()` updated for TP-04
6. **No new gates**: TP-02 fund ceilings are informational (no IPR gate validates against them yet)
