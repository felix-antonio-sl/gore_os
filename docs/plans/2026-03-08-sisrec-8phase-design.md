# TP-06 + HΩ-14 SISREC 8-Phase CGR — Design Document

**Date**: 2026-03-08
**Status**: Approved
**HΩ Finding**: HΩ-14 (último HΩ parcial → 15/15)

## Goal

Complete the formal CGR Res. 30 rendition cycle with 8-phase parametric table, external phase metadata timestamps, archived_at for phase 8, escalation tracking with alert generation, and enhanced ciclo endpoint.

## Regulatory Basis

- **Resolución N°30/2015 CGR**: 8-phase institutional rendition cycle
- Phases 1-3: External (executor prepares, certifies, signs)
- Phase 4: Reception at GORE
- Phases 5-7: Internal review (RTF 7d, DAF 1d, UCR 2d)
- Phase 8: Archive/closure

## Architecture

- **TP-06 parametric table**: `core.rendition_phase` (8 seed rows, immutable)
- **External phases**: Metadata timestamps in `core.rendition.metadata` JSONB (not formal states)
- **Phase 8**: `archived_at` timestamp on `core.rendition` (not a new state — APROBADA remains terminal)
- **Escalation**: `core.rendition_escalation` table + auto-generated `core.alert` entries
- **No automated reasignment**: System informs, human acts

## Data Model

### New table: `core.rendition_phase` (8 rows, seed-only)

```sql
CREATE TABLE core.rendition_phase (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ordinal           INT NOT NULL UNIQUE CHECK (ordinal BETWEEN 1 AND 8),
    code              VARCHAR(32) NOT NULL UNIQUE,
    name              TEXT NOT NULL,
    responsible_role  TEXT NOT NULL,
    sla_days          INT NOT NULL,
    escalation_action TEXT,
    is_internal       BOOLEAN NOT NULL DEFAULT true
);
```

Seed: PREPARACION_EJECUTOR(15d), CERTIFICACION(3d), FIRMA_ENCARGADO(1d), RECEPCION_GORE(2d), REVISION_RTF(7d), APROBACION_DAF(1d), CONTABILIZACION_UCR(2d), ARCHIVO_CIERRE(1d).

### New column: `core.rendition.archived_at`

```sql
ALTER TABLE core.rendition ADD COLUMN IF NOT EXISTS archived_at TIMESTAMPTZ;
```

### New table: `core.rendition_escalation`

```sql
CREATE TABLE core.rendition_escalation (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rendition_id     UUID NOT NULL REFERENCES core.rendition(id),
    phase_id         UUID NOT NULL REFERENCES core.rendition_phase(id),
    escalation_level INT NOT NULL CHECK (escalation_level BETWEEN 1 AND 3),
    detected_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    alert_id         UUID REFERENCES core.alert(id),
    resolved_at      TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Levels: 1 = notification (1x SLA), 2 = delegation (1.5x SLA), 3 = executive (2x SLA).

### Metadata timestamps (external phases)

```json
{
  "fase1_preparacion_at": "ISO timestamp",
  "fase2_certificacion_at": "ISO timestamp",
  "fase3_firma_at": "ISO timestamp"
}
```

## API Endpoints (4 new)

| Method | Route | Description | Auth |
|--------|-------|-------------|------|
| GET | `/api/dgi/data/rendiciones/fases` | List 8 phase definitions | Any authenticated |
| PATCH | `/api/dgi/data/rendiciones/{id}/archivar` | Set archived_at | DGI_ROLES |
| GET | `/api/dgi/data/rendiciones/{id}/escalamientos` | List escalations | Any authenticated |
| POST | `/api/dgi/data/rendiciones/check-escalations` | Detect overdue, create escalations + alerts | DGI_ROLES |

## Enhanced ciclo endpoint

`GET /api/dgi/data/rendiciones/{id}/ciclo` — adds TP-06 phase definitions with status (completada/en_curso/pendiente/no_aplica) based on history + metadata timestamps + current state.

## Escalation logic

For each rendition in reviewable state:
1. Map state → TP-06 phase (EN_REVISION_RTF→5, VISADA_RTF→6, EN_REVISION_UCR→7)
2. Calculate days_in_state from phase_entered_at
3. Check multipliers: Level 1 (1x SLA), Level 2 (1.5x SLA), Level 3 (2x SLA)
4. If exceeded and no existing escalation at that level → create escalation + alert

## Decisions

1. **External phases**: Metadata timestamps, not formal states
2. **Phase 8**: `archived_at` timestamp, not new state (APROBADA stays terminal)
3. **Escalation**: Register + generate alerts, no auto-reasignment
4. **TP-06**: Seed-only table (like TP-05), 8 immutable rows
5. **State machine**: No changes to existing 6 states / 7 transitions
