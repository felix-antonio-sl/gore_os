# Certificación Técnica C33 — Design

**Date**: 2026-03-09
**Status**: Approved

## Goal

Add technical certification workflow for C33 (Circular 33) IPRs: SERVIU certifies building projects, MOP certifies road projects. Blocking gate at F1→F2. Parametric categories via `ref.category`.

## Context

C33 IPRs require a favorable technical report from SERVIU (edificación) or MOP (vialidad) before entering MDSF evaluation. Currently the DDL has `informe_tecnico_favorable` (BOOLEAN) and `categoria_c33` (VARCHAR) columns but neither is used. The audit marks "Certificación técnica" as RED.

## Decisions

1. **DB-parametric categories**: New scheme `categoria_c33` in `ref.category` with metadata `certifier_org_code`. Admin can add future categories without code changes.
2. **No new DDL table**: Reuse existing `core.ipr.informe_tecnico_favorable` (BOOLEAN) + `metadata` JSONB fields with `cert_` prefix for traceability.
3. **Blocking gate F1→F2**: `_check_c33_technical_certification()` blocks if IPR is C33 and certification is missing/unfavorable.
4. **3 endpoints**: GET status, POST solicitar, PATCH resolver.
5. **Role-escalated permissions**: JEFE_DIVISION+ can request, ADMIN_REGIONAL/ADMIN_SISTEMA can resolve.
6. **Frontend in existing tab**: Section in "Evaluación" tab (#11), no new tab.

## Data Model

### Scheme `categoria_c33`

```sql
INSERT INTO ref.category (scheme, code, label, metadata) VALUES
('categoria_c33', 'EDIFICACION', 'Edificación', '{"certifier_org_code": "SERVIU"}'),
('categoria_c33', 'VIALIDAD',    'Vialidad',    '{"certifier_org_code": "MOP"}');
```

### Existing columns in `core.ipr`

| Column | Type | Purpose |
|--------|------|---------|
| `categoria_c33` | VARCHAR(32) | Category code from scheme |
| `informe_tecnico_favorable` | BOOLEAN | null=not requested, true=favorable, false=unfavorable |

### Metadata JSONB fields (cert_ prefix)

```json
{
  "cert_requested_at": "2026-03-09T14:30:00Z",
  "cert_requested_by_id": "uuid",
  "cert_requested_by_name": "Juan Pérez",
  "cert_certifier_org": "SERVIU",
  "cert_resolved_at": "2026-03-15T10:00:00Z",
  "cert_resolved_by_id": "uuid",
  "cert_resolved_by_name": "María González",
  "cert_document_reference": "ORD. N° 1234/2026",
  "cert_notes": "Informe favorable con observaciones menores"
}
```

## Gate

### `_check_c33_technical_certification()` — F1→F2, blocking

1. Only evaluates if IPR mechanism is C33
2. `categoria_c33` is NULL → blocks "Asignar categoría C33"
3. `informe_tecnico_favorable` is NULL → blocks "Certificación pendiente — solicitar a {org}"
4. `informe_tecnico_favorable` is false → blocks "Certificación desfavorable de {org}"
5. `informe_tecnico_favorable` is true → passes

## Endpoints

| Method | Route | Min Role | Description |
|--------|-------|----------|-------------|
| GET | `/api/ipr/{id}/certificacion-tecnica` | Any authenticated | Current status |
| POST | `/api/ipr/{id}/certificacion-tecnica/solicitar` | JEFE_DIVISION+ | Register request, returns certifier org |
| PATCH | `/api/ipr/{id}/certificacion-tecnica` | ADMIN_REGIONAL, ADMIN_SISTEMA | Register result |

### POST solicitar validations
- IPR must be in F1 phase (EN_REVISION, PRE_ADMISIBLE, or ADMISIBLE)
- `categoria_c33` must be assigned
- Cannot re-request if result already registered (409)

### PATCH resolver validations
- Request must exist (`cert_requested_at` in metadata)
- Cannot re-resolve if result exists (409)

### PATCH resolver body
```json
{
  "favorable": true,
  "document_reference": "ORD. N° 1234/2026",
  "notes": "Optional notes"
}
```

### categoria_c33 assignment
Via standard `PATCH /api/ipr/{id}` with `{"categoria_c33": "EDIFICACION"}`. Already in DDL, add to `_IPR_FIELD_ALLOWLIST` if needed.

## Tests (~8)

1. GET certificacion-tecnica — empty state
2. POST solicitar — JEFE_DIVISION success, returns certifier org
3. POST solicitar without categoria_c33 — 409
4. POST solicitar wrong role — ENCARGADO → 403
5. PATCH resolver favorable — ADMIN_REGIONAL success
6. PATCH resolver without prior request — 409
7. PATCH resolver wrong role — JEFE_DIVISION → 403
8. Gate F1→F2 blocking — C33 without certification → 409

## Frontend

Section in existing "Evaluación" tab (#11), visible only for C33 IPRs:
- Status badge: "Sin solicitar" / "Solicitada a SERVIU" / "Favorable" / "Desfavorable"
- "Solicitar Certificación" button (JEFE_DIVISION+)
- "Registrar Resultado" button (ADMIN_REGIONAL+) with inline form
- Detail: who requested, when, who resolved, document reference

## Migration

Single file `goreos_migration_c33_certification.sql`:
- Insert scheme `categoria_c33` with 2 codes + certifier metadata
- Ensure `categoria_c33` in IPR field allowlist
- Self-register in `core.schema_migration`
