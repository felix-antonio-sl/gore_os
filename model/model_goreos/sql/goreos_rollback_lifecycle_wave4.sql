-- ============================================================================
-- Rollback: Lifecycle Wave 4 — Remove SLAs + ITO + phase_entered_at
-- ============================================================================

BEGIN;

DROP TRIGGER IF EXISTS trg_ipr_phase_entered ON core.ipr;
DROP FUNCTION IF EXISTS fn_ipr_phase_entered();
ALTER TABLE core.ipr DROP COLUMN IF EXISTS phase_entered_at;

-- Remove evaluation SLA from sla_days
UPDATE core.financing_track SET sla_days = sla_days - 'evaluation_max_days'
WHERE sla_days ? 'evaluation_max_days';

-- Remove ITO party role
DELETE FROM ref.category WHERE scheme = 'ipr_party_role' AND code = 'ITO';

DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_lifecycle_wave4.sql';

COMMIT;
