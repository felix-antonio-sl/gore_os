-- ============================================================================
-- Rollback Wave 7: Evaluation Assignment model (Poly-Switch)
-- Reverses: goreos_migration_wave7_evaluation.sql
-- ============================================================================

BEGIN;

DROP TABLE IF EXISTS core.evaluation_assignment CASCADE;

DELETE FROM ref.category WHERE scheme = 'evaluator_type';

COMMIT;
