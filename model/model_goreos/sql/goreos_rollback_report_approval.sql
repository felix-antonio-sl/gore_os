-- =============================================================================
-- GORE_OS — ROLLBACK: DGI report approval workflow status
-- =============================================================================
-- Reverts: goreos_migration_report_approval.sql
-- Deletes the EN_REVISION status from ref.category.
-- =============================================================================

BEGIN;

-- 1. Delete the seeded category row
DELETE FROM ref.category
WHERE scheme = 'dgi_report_status'
  AND code = 'EN_REVISION';

-- 2. Remove migration record
DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_report_approval.sql';

COMMIT;
