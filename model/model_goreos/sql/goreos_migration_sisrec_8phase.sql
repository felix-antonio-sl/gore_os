-- TP-06 + HΩ-14: 8-Phase CGR rendition cycle
-- Creates: core.rendition_phase (8 seed rows), core.rendition_escalation
-- Alters: core.rendition (adds archived_at)
BEGIN;

-- T1: Parametric table TP-06 — 8 CGR rendition phases (seed-only, immutable)
CREATE TABLE IF NOT EXISTS core.rendition_phase (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ordinal    INT NOT NULL UNIQUE CHECK (ordinal BETWEEN 1 AND 8),
    code       VARCHAR(32) NOT NULL UNIQUE,
    name       TEXT NOT NULL,
    responsible_role TEXT NOT NULL,
    sla_days   INT NOT NULL,
    escalation_action TEXT,
    is_internal BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- T2: Seed 8 phases
INSERT INTO core.rendition_phase (ordinal, code, name, responsible_role, sla_days, escalation_action, is_internal)
VALUES
    (1, 'PREPARACION_EJECUTOR', 'Preparación Ejecutor',           'EJECUTOR',               15, 'Notificar ejecutor',         false),
    (2, 'CERTIFICACION',        'Certificación',                   'EJECUTOR',                3, 'Notificar ejecutor',         false),
    (3, 'FIRMA_ENCARGADO',      'Firma Encargado',                 'ENCARGADO_RENDICION',     1, 'Notificar encargado',        false),
    (4, 'RECEPCION_GORE',       'Recepción GORE',                  'OFICINA_PARTES',          2, 'Notificar Of. Partes',       true),
    (5, 'REVISION_RTF',         'Revisión RTF',                    'RTF',                     7, 'Escalar a Jefe RTF',         true),
    (6, 'APROBACION_DAF',       'Aprobación DAF',                  'DAF',                     1, 'Escalar a Jefe DAF',         true),
    (7, 'CONTABILIZACION_UCR',  'Contabilización UCR',             'UCR',                     2, 'Escalar a Jefe UCR',         true),
    (8, 'ARCHIVO_CIERRE',       'Archivo y Cierre',                'ARCHIVO',                 1, 'Notificar responsable',      true)
ON CONFLICT (ordinal) DO NOTHING;

-- T3: archived_at on rendition (phase 8 — not a new state)
ALTER TABLE core.rendition ADD COLUMN IF NOT EXISTS archived_at TIMESTAMPTZ;

-- T4: Escalation tracking table
CREATE TABLE IF NOT EXISTS core.rendition_escalation (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rendition_id     UUID NOT NULL REFERENCES core.rendition(id),
    phase_id         UUID NOT NULL REFERENCES core.rendition_phase(id),
    escalation_level INT NOT NULL CHECK (escalation_level BETWEEN 1 AND 3),
    detected_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    alert_id         UUID REFERENCES core.alert(id),
    resolved_at      TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- T5: Index for rendition escalation lookups
CREATE INDEX IF NOT EXISTS idx_rendition_escalation_rendition
    ON core.rendition_escalation(rendition_id);

-- T6: Index for archived_at queries
CREATE INDEX IF NOT EXISTS idx_rendition_archived
    ON core.rendition(archived_at)
    WHERE archived_at IS NOT NULL AND deleted_at IS NULL;

-- T7: Self-register migration
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_sisrec_8phase.sql', 'manual', 'sisrec_8phase_self_register')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
