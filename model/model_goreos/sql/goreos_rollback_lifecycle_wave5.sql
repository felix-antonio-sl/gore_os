-- goreos_rollback_lifecycle_wave5.sql
-- Rollback Wave 5: Role-based transition permissions

BEGIN;

-- Revert FRIL overrides
UPDATE core.financing_track
SET role_permissions = '{}'::jsonb
WHERE code = 'FRIL';

-- Remove FRIL vigencia from sla_days
UPDATE core.financing_track
SET sla_days = sla_days - 'rs_validity_days'
WHERE code = 'FRIL';

-- Drop role_permissions column
ALTER TABLE core.financing_track DROP COLUMN IF EXISTS role_permissions;

-- Remove SUPERVISOR_GORE party role
DELETE FROM ref.category
WHERE scheme = 'ipr_party_role' AND code = 'SUPERVISOR_GORE';

-- Remove migration record
DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_lifecycle_wave5.sql';

COMMIT;
