-- =============================================================================
-- GORE_OS — ROLLBACK: DGI indicator snapshot
-- =============================================================================
-- Reverts: goreos_migration_indicator_snapshot.sql
-- Drops index and table for dgi_indicator_snapshot.
-- =============================================================================

BEGIN;

-- 1. Drop index (also removed by table drop, explicit for clarity)
DROP INDEX IF EXISTS core.idx_indicator_snapshot_lookup;

-- 2. Drop table
DROP TABLE IF EXISTS core.dgi_indicator_snapshot CASCADE;

-- 3. Remove migration record
DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_indicator_snapshot.sql';

COMMIT;
