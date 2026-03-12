-- ============================================================================
-- Rollback: Lifecycle Wave 1 — Restore original valid_transitions
-- ============================================================================

BEGIN;

-- Remove new states
DELETE FROM ref.category WHERE scheme = 'ipr_state' AND code = 'TERMINADO_ANTICIPADAMENTE';
DELETE FROM ref.category WHERE scheme = 'ipr_state' AND code = 'CONTRATO_FIRMADO';

-- Restore original valid_transitions
UPDATE ref.category SET valid_transitions = '["FORMALIZADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_FORMALIZACION';

UPDATE ref.category SET valid_transitions = '["EN_OBRA"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'ADJUDICADO';

UPDATE ref.category SET valid_transitions = '["EN_LICITACION"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'AD';

UPDATE ref.category SET valid_transitions = '["EN_RENDICION", "SUSPENDIDO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_EJECUCION';

UPDATE ref.category SET valid_transitions = '["RECEPCION_PROVISORIA", "SUSPENDIDO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_OBRA';

UPDATE ref.category SET valid_transitions = '["EN_EJECUCION", "EN_OBRA", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'SUSPENDIDO';

UPDATE ref.category SET valid_transitions = '["ADJUDICADO", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_LICITACION';

UPDATE ref.category SET valid_transitions = '["RECEPCION_DEFINITIVA"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'RECEPCION_PROVISORIA';

UPDATE ref.category SET valid_transitions = '["EN_RENDICION", "CERRADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'RECEPCION_DEFINITIVA';

UPDATE ref.category SET valid_transitions = '["CERRADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_RENDICION';

UPDATE ref.category SET valid_transitions = '["EN_EJECUCION"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'FORMALIZADO';

UPDATE ref.category SET valid_transitions = '["EN_FORMALIZACION"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'CDP_EMITIDO';

UPDATE ref.category SET valid_transitions = '["RS", "FI", "FC", "OT", "RF", "ITF", "AT", "AD"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_EVALUACION';

DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_lifecycle_wave1.sql';

COMMIT;
