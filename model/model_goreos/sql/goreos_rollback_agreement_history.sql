-- =============================================================================
-- GORE_OS — ROLLBACK: Agreement state history tracking
-- =============================================================================
-- Reverts: goreos_migration_agreement_history.sql
-- Drops trigger, function, index, and table for agreement_history.
-- =============================================================================

BEGIN;

-- 1. Drop trigger on core.agreement
DROP TRIGGER IF EXISTS trg_agreement_history ON core.agreement;

-- 2. Drop trigger function
DROP FUNCTION IF EXISTS fn_agreement_history();

-- 3. Drop index (CASCADE covers it via table drop, but explicit for clarity)
DROP INDEX IF EXISTS core.idx_agreement_history_agreement;

-- 4. Drop table
DROP TABLE IF EXISTS core.agreement_history CASCADE;

-- 5. Remove migration record
DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_agreement_history.sql';

COMMIT;
