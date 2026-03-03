-- ============================================================================
-- Ciclo 22: Track-Specific Enforcement — numeric_score for evaluation_assignment
-- ============================================================================
-- Adds numeric_score column to core.evaluation_assignment for FRPD puntaje gate
-- Run: docker exec -i goreos_db psql -U goreos -d goreos_model < model/model_goreos/sql/goreos_migration_ciclo22_eval_score.sql
-- ============================================================================

BEGIN;

-- Add numeric_score column (nullable — not all mechanisms require a score)
ALTER TABLE core.evaluation_assignment
    ADD COLUMN IF NOT EXISTS numeric_score NUMERIC(5,2);

COMMENT ON COLUMN core.evaluation_assignment.numeric_score IS
    'Numeric evaluation score (0-100). Used by FRPD puntaje_min gate at F2→F3.';

-- Register migration
INSERT INTO core.schema_migration (filename)
VALUES ('goreos_migration_ciclo22_eval_score.sql')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
