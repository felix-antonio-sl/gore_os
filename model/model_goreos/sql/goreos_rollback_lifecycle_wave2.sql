-- ============================================================================
-- Rollback: Lifecycle Wave 2 — Remove modifications + report periodicity
-- ============================================================================

BEGIN;

DROP TRIGGER IF EXISTS trg_modification_state_transition ON core.ipr_modification;
DROP TABLE IF EXISTS core.ipr_modification;

DELETE FROM ref.category WHERE scheme = 'modification_type';
DELETE FROM ref.category WHERE scheme = 'modification_status';

-- Remove report_frequency_days from sla_days
UPDATE core.financing_track SET sla_days = sla_days - 'report_frequency_days'
WHERE sla_days ? 'report_frequency_days';

DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_lifecycle_wave2.sql';

COMMIT;
