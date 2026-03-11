-- =============================================================================
-- GORE_OS — ROLLBACK: Bottleneck Detection & Investigation (CG-019..023)
-- =============================================================================
-- Reverts: goreos_migration_bottleneck.sql
-- Drops investigation table, then removes status scheme from ref.category.
-- =============================================================================

BEGIN;

-- 1. Drop indexes
DROP INDEX IF EXISTS core.idx_dgi_bottleneck_status;
DROP INDEX IF EXISTS core.idx_dgi_bottleneck_division;

-- 2. Drop investigation table
DROP TABLE IF EXISTS core.dgi_bottleneck_investigation CASCADE;

-- 3. Remove bottleneck status scheme
DELETE FROM ref.category WHERE scheme = 'dgi_bottleneck_status';

-- 4. Remove migration record
DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_bottleneck.sql';

COMMIT;
