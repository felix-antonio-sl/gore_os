-- ============================================================================
-- Rollback: Restore DIIAP division (if needed)
-- ============================================================================

BEGIN;

-- 1. Restore DIIAP organization
UPDATE core.organization
SET deleted_at = NULL
WHERE code = 'DIIAP';

-- 2. Remove migration record
DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_remove_diiap.sql';

COMMIT;
