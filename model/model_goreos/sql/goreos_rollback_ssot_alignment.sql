BEGIN;

-- Reverse H-05: ENVIADO_CGR → TRAMITADO
UPDATE ref.category SET code = 'TRAMITADO', label = 'Tramitado'
WHERE scheme = 'act_state' AND code = 'ENVIADO_CGR';

UPDATE ref.category SET valid_transitions = REPLACE(valid_transitions::text, 'ENVIADO_CGR', 'TRAMITADO')::jsonb
WHERE scheme = 'act_state' AND valid_transitions::text LIKE '%ENVIADO_CGR%';

-- Reverse H-06: Remove OBSERVADO
DELETE FROM ref.category WHERE scheme = 'act_state' AND code = 'OBSERVADO';

-- Reverse H-04: Remove FORMALIZADO
DELETE FROM ref.category WHERE scheme = 'agreement_state' AND code = 'FORMALIZADO';

-- Reverse H-07: Remove APROBADA_PARCIALMENTE
DELETE FROM ref.category WHERE scheme = 'rendition_state' AND code = 'APROBADA_PARCIALMENTE';

-- Remove migration record
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_ssot_alignment.sql';

COMMIT;
