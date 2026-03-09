# Clasificador Presupuestario Nivel 5 — Programa DIPRES

**Date**: 2026-03-08
**Status**: Approved

## Goal

Add the 5th level of the Chilean DIPRES budget classifier (Programa presupuestario) to complete the 5/6 hierarchy. Level 6 (Asignacion) is already covered by `budget_allocation`.

## Context

GORE_OS implements 4 of 6 DIPRES budget classification levels:

| Level | Name | Implementation | Status |
|:-----:|------|---------------|:------:|
| 1 | Partida | Institutional constant (GORE Nuble) | CONSTANT |
| 2 | Capitulo | Institutional constant (Cap 82) | CONSTANT |
| 3 | Subtitulo | `budget_subtitle` scheme (8 codes) | DONE |
| 4 | Item | `budget_item` scheme (14 codes) | DONE |
| **5** | **Programa** | **Not modeled** | **GAP** |
| 6 | Asignacion | `budget_allocation` scheme (15 codes) | DONE |

Additionally, `program_type` (5 codes: FNDR, IRAL, FRIL, etc.) is a separate **orthogonal dimension** — it represents the financing mechanism, NOT the DIPRES program code. Both coexist as independent FKs on `core.budget_program`.

## Decisions

1. **Orthogonal dimensions**: `program_code_id` (new, DIPRES) coexists with `program_type_id` (existing, mechanism). Not hierarchical.
2. **No seed data**: Empty scheme, admin creates codes via CRUD. No hardcoded DIPRES program codes.
3. **Nullable FK**: Existing budget_programs keep `program_code_id = NULL` until admin assigns.
4. **Frontend: column only, no filter**: Show "Programa" in table + detail. Filter UI deferred until real data exists.
5. **Informational only**: No gate functions, glosa rules, or enforcement depends on this field.

## Data Model

```sql
-- New scheme in ref.category
-- Codes TBD by ADMIN_SISTEMA (e.g., "01"="Funcionamiento", "02"="Inversion Regional")

-- New FK on existing table
ALTER TABLE core.budget_program
  ADD COLUMN program_code_id UUID REFERENCES ref.category(id);
```

## Admin CRUD (3 endpoints)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/admin/budget-program-codes` | List all program codes |
| POST | `/api/admin/budget-program-codes` | Create program code |
| PATCH | `/api/admin/budget-program-codes/{id}` | Update program code |

Schema: `code` (VARCHAR UNIQUE), `label` (TEXT), `sort_order` (INT). Restricted to ADMIN_SISTEMA.

## API Changes (presupuesto.py)

- `GET /api/presupuesto` — add `?program_code=X` filter param (code match)
- `POST /api/presupuesto` — accept optional `program_code_id` in PresupuestoCreate
- `PATCH /api/presupuesto/{id}` — add `program_code_id` to field allowlist
- Response: add `program_code_label` to PresupuestoListItem (LEFT JOIN ref.category)

## Frontend Changes

- `/presupuesto/page.tsx` — add "Programa" column in DataTable (after Subtitulo)
- Detail drawer — show `program_code_label` alongside item_label and allocation_label
- No filter Select (deferred)

## Tests (~5)

- Admin CRUD: create, list, update program code
- Filter: `?program_code=X` returns filtered results
- Create: budget_program with program_code_id links correctly
