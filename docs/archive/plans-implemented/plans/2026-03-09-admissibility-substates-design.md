# Admisibilidad Sub-estados — PRE_ADMISIBLE Checklist

**Date**: 2026-03-09
**Status**: Approved

## Goal

Add a track-specific admissibility checklist to F1 phase, with a new PRE_ADMISIBLE sub-state. Multiple roles verify checklist items progressively before an authorized user declares the IPR admissible.

## Context

GORE_OS IPR lifecycle phase F1 is currently a simple binary: `EN_REVISION → ADMISIBLE | INADMISIBLE`. In practice, admissibility is a multi-step verification process where different roles check different requirements. There is no visibility into progress, no audit trail of who verified what, and no track-specific differentiation.

Current F1 state machine:
```
EN_REVISION → ADMISIBLE | INADMISIBLE
```

Target F1 state machine:
```
EN_REVISION → PRE_ADMISIBLE | INADMISIBLE
PRE_ADMISIBLE → ADMISIBLE | INADMISIBLE
```

## Decisions

1. **New sub-state PRE_ADMISIBLE**: Explicit lifecycle state between EN_REVISION and ADMISIBLE. Consistent with GORE_OS state machine model.
2. **DB-parametric checklist**: New table `core.admissibility_item` per financing track. Admin creates/edits items via CRUD — no hardcoded checklists.
3. **Multi-role verification**: Each checklist item has a `responsible_role`. Only that role can verify it. Audit trail via `admissibility_check` table.
4. **Manual declaration**: Checklist completion is necessary but not sufficient — an authorized user must explicitly trigger PRE_ADMISIBLE → ADMISIBLE.
5. **No auto-population of check rows**: When IPR enters PRE_ADMISIBLE, checklist items are read from `admissibility_item` by track. Check rows are created only when someone verifies.
6. **No seed data**: Admin creates checklist items per track. Empty by default.
7. **Existing F1→F2 gates unchanged**: The 7 gates at ADMISIBLE → EN_EVALUACION remain as-is.

## Data Model

### New state

```sql
-- Add PRE_ADMISIBLE to ipr_state scheme
INSERT INTO ref.category (scheme, code, label, sort_order)
VALUES ('ipr_state', 'PRE_ADMISIBLE', 'Pre-admisible (verificación en curso)', 5);

-- Update valid_transitions
-- EN_REVISION: remove ADMISIBLE, add PRE_ADMISIBLE
-- PRE_ADMISIBLE: can go to ADMISIBLE or INADMISIBLE
```

### New tables

```sql
CREATE TABLE core.admissibility_item (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  financing_track_id UUID NOT NULL REFERENCES core.financing_track(id),
  code VARCHAR(50) NOT NULL,
  label TEXT NOT NULL,
  description TEXT,
  responsible_role VARCHAR(50) NOT NULL,
  sort_order INT DEFAULT 0,
  is_required BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ,
  UNIQUE(financing_track_id, code)
);

CREATE TABLE core.admissibility_check (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ipr_id UUID NOT NULL REFERENCES core.ipr(id),
  item_id UUID NOT NULL REFERENCES core.admissibility_item(id),
  verified_by_id UUID NOT NULL REFERENCES core."user"(id),
  verified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(ipr_id, item_id)
);

CREATE INDEX idx_admissibility_check_ipr ON core.admissibility_check(ipr_id);
```

## Gates

### EN_REVISION → PRE_ADMISIBLE
- `mechanism_required`: financing mechanism assigned (existing gate, relocated)
- `_check_fril_max_per_comuna()`: max 5 FRIL per territory (existing gate, relocated)

### PRE_ADMISIBLE → ADMISIBLE
- `checklist_complete`: all items with `is_required = true` for the IPR's track have corresponding `admissibility_check` rows
- If incomplete → HTTP 409 with list of pending items and responsible roles

### PRE_ADMISIBLE → INADMISIBLE
- No gate — always allowed (reviewer can reject at any point)

## Admin CRUD (3 endpoints)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/admin/admissibility-items?track_id=X` | List items for a track |
| POST | `/api/admin/admissibility-items` | Create item |
| PATCH | `/api/admin/admissibility-items/{id}` | Update item |

Restricted to ADMIN_SISTEMA. Fields: code, label, description, responsible_role, sort_order, is_required.

## IPR Checklist Endpoints (3 endpoints)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/ipr/{id}/admisibilidad` | Checklist with verification status |
| POST | `/api/ipr/{id}/admisibilidad/{item_id}/verificar` | Mark item verified (role-restricted) |
| DELETE | `/api/ipr/{id}/admisibilidad/{item_id}/verificar` | Unmark verification |

### GET response shape

```json
{
  "track_code": "FRIL",
  "total_items": 5,
  "verified_count": 3,
  "pending_count": 2,
  "items": [
    {
      "item_id": "uuid",
      "code": "DOC_LEGAL",
      "label": "Documentación legal completa",
      "responsible_role": "JEFE_DIVISION",
      "is_required": true,
      "verified": true,
      "verified_by": "María González",
      "verified_at": "2026-03-09T14:30:00Z",
      "notes": null
    }
  ]
}
```

### Role check on POST verificar

Validates `user.system_role == item.responsible_role`. Mismatch → 403 "Solo {role} puede verificar este ítem". ADMIN_SISTEMA can verify any item.

## Frontend

- IPR detail tab "Admisibilidad" (#13) — visible when IPR is PRE_ADMISIBLE
- Progress bar header: "3/5 verificados"
- Item list with role badge, verification status, "Verificar" button (role-gated)
- "Declarar Admisible" button at bottom (disabled until checklist complete)
- No filter in IPR list (deferred)
- No notifications (deferred)

## Tests (~10)

1. Admin CRUD: create, list, update admissibility items
2. GET checklist for IPR in PRE_ADMISIBLE
3. POST verify item (correct role → 200)
4. POST verify item (wrong role → 403)
5. DELETE unverify item
6. Transition EN_REVISION → PRE_ADMISIBLE (mechanism required)
7. Transition PRE_ADMISIBLE → ADMISIBLE blocked (incomplete checklist → 409)
8. Transition PRE_ADMISIBLE → ADMISIBLE allowed (complete checklist)
9. Transition PRE_ADMISIBLE → INADMISIBLE (always allowed)
10. ADMIN_SISTEMA can verify any item regardless of responsible_role
