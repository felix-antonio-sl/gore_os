-- =============================================================================
-- GORE_OS — ROLLBACK: Budget Cycle Timeline (TP-05)
-- =============================================================================
-- Reverts: goreos_migration_budget_cycle.sql
-- Drops tracking table (depends on milestone), then milestone table.
-- =============================================================================

BEGIN;

-- 1. Drop index on tracking table
DROP INDEX IF EXISTS core.idx_bct_fiscal_year;

-- 2. Drop tracking table first (has FK to milestone)
DROP TABLE IF EXISTS core.budget_cycle_tracking CASCADE;

-- 3. Drop milestone table (includes seeded data)
DROP TABLE IF EXISTS core.budget_cycle_milestone CASCADE;

-- 4. Remove migration record
DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_budget_cycle.sql';

COMMIT;
