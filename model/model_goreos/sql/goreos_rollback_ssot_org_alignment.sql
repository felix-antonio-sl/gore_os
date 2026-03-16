-- ============================================================================
-- Rollback: SSOT Organizational Alignment
-- WARNING: This rollback restores ENCARGADO and legacy org codes.
--          Only use if the migration caused issues.
-- ============================================================================

BEGIN;

-- 1. Restore ENCARGADO role
UPDATE ref.category
SET is_active = true, description = 'Ejecuta trabajo, actualiza avances, reporta problemas'
WHERE scheme = 'system_role' AND code = 'ENCARGADO';

-- 2. Restore DIDECO organization
UPDATE core.organization
SET deleted_at = NULL
WHERE code = 'DIDECO';

-- 3. Remove migration record
DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_ssot_org_alignment.sql';

COMMIT;
