-- =============================================================================
-- GORE_OS — ROLLBACK: Kinship declaration (HΩ-02)
-- =============================================================================
-- Reverts: goreos_migration_parentesco.sql
-- Drops index and kinship_declaration table.
-- =============================================================================

BEGIN;

-- 1. Drop index
DROP INDEX IF EXISTS core.idx_kinship_declaration_ipr;

-- 2. Drop table
DROP TABLE IF EXISTS core.kinship_declaration CASCADE;

-- 3. Remove migration record
DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_parentesco.sql';

COMMIT;
