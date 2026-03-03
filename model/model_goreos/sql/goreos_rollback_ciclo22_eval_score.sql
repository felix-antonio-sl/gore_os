-- ============================================================================
-- Rollback: Ciclo 22 — remove numeric_score from evaluation_assignment
-- ============================================================================

BEGIN;

ALTER TABLE core.evaluation_assignment DROP COLUMN IF EXISTS numeric_score;

DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_ciclo22_eval_score.sql';

COMMIT;
