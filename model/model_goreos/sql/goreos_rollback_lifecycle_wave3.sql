-- ============================================================================
-- Rollback: Lifecycle Wave 3 — Remove closure + ex-post + F5 states
-- ============================================================================

BEGIN;

DROP TABLE IF EXISTS core.ipr_expost_evaluation;
DROP TABLE IF EXISTS core.ipr_closure;

DELETE FROM ref.category WHERE scheme = 'expost_eval_type';
DELETE FROM ref.category WHERE scheme = 'expost_rating';

DELETE FROM ref.category WHERE scheme = 'ipr_state' AND code = 'RENDICION_APROBADA';
DELETE FROM ref.category WHERE scheme = 'ipr_state' AND code = 'EN_CIERRE_ADMINISTRATIVO';

-- Restore EN_RENDICION transitions (from Wave 1)
UPDATE ref.category SET valid_transitions = '["CERRADO", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_RENDICION';

DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_lifecycle_wave3.sql';

COMMIT;
