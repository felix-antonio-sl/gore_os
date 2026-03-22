-- Migration: SSOT alignment — rename TRAMITADO→ENVIADO_CGR, add OBSERVADO, FORMALIZADO, APROBADA_PARCIALMENTE
-- Applied: 2026-03-22

BEGIN;

-- H-05: Rename TRAMITADO → ENVIADO_CGR in act_state
UPDATE ref.category SET code = 'ENVIADO_CGR', label = 'Enviado a CGR'
WHERE scheme = 'act_state' AND code = 'TRAMITADO';

-- Update valid_transitions references
UPDATE ref.category SET valid_transitions = REPLACE(valid_transitions::text, 'TRAMITADO', 'ENVIADO_CGR')::jsonb
WHERE scheme = 'act_state' AND valid_transitions::text LIKE '%TRAMITADO%';

-- H-06: Add OBSERVADO state for CGR objections
INSERT INTO ref.category (scheme, code, label, sort_order)
VALUES ('act_state', 'OBSERVADO', 'Observado por CGR', 6)
ON CONFLICT (scheme, code) DO NOTHING;

-- Update valid_transitions: ENVIADO_CGR can go to TOMADO_RAZON, RECHAZADO_CGR, OBSERVADO, or ANULADO
UPDATE ref.category SET valid_transitions = '["TOMADO_RAZON", "RECHAZADO_CGR", "OBSERVADO", "ANULADO"]'::jsonb
WHERE scheme = 'act_state' AND code = 'ENVIADO_CGR';

-- OBSERVADO can go back to ENVIADO_CGR (resubmission) or ANULADO
UPDATE ref.category SET valid_transitions = '["ENVIADO_CGR", "ANULADO"]'::jsonb
WHERE scheme = 'act_state' AND code = 'OBSERVADO';

-- H-04: Add FORMALIZADO state for agreements
INSERT INTO ref.category (scheme, code, label, sort_order)
VALUES ('agreement_state', 'FORMALIZADO', 'Formalizado', 9)
ON CONFLICT (scheme, code) DO NOTHING;

-- Update valid_transitions: TDR_PENDIENTE → FORMALIZADO (instead of direct to VIGENTE)
UPDATE ref.category SET valid_transitions = '["FORMALIZADO", "ANULADO"]'::jsonb
WHERE scheme = 'agreement_state' AND code = 'TDR_PENDIENTE';

-- FORMALIZADO → VIGENTE
UPDATE ref.category SET valid_transitions = '["VIGENTE", "ANULADO"]'::jsonb
WHERE scheme = 'agreement_state' AND code = 'FORMALIZADO';

-- H-07: Add APROBADA_PARCIALMENTE state for renditions
INSERT INTO ref.category (scheme, code, label, sort_order)
VALUES ('rendition_state', 'APROBADA_PARCIALMENTE', 'Aprobada Parcialmente', 7)
ON CONFLICT (scheme, code) DO NOTHING;

-- Update valid_transitions: EN_REVISION_UCR can also go to APROBADA_PARCIALMENTE
UPDATE ref.category SET valid_transitions = '["APROBADA", "RECHAZADA", "OBSERVADA", "APROBADA_PARCIALMENTE"]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'EN_REVISION_UCR';

-- APROBADA_PARCIALMENTE is terminal (like APROBADA)
UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'APROBADA_PARCIALMENTE';

-- Record migration
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_ssot_alignment.sql', md5('ssot-alignment-h04-h05-h06-h07'), 'claude-c60')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
