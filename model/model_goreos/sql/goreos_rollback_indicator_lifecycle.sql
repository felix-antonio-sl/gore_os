-- ============================================================================
-- Rollback: Indicator Lifecycle Management
-- ============================================================================

BEGIN;

DROP TABLE IF EXISTS core.dgi_indicator_lifecycle_history;

ALTER TABLE core.dgi_indicator DROP CONSTRAINT IF EXISTS chk_dgi_indicator_lifecycle;
ALTER TABLE core.dgi_indicator DROP CONSTRAINT IF EXISTS chk_dgi_indicator_source_type;
ALTER TABLE core.dgi_indicator DROP COLUMN IF EXISTS formula;
ALTER TABLE core.dgi_indicator DROP COLUMN IF EXISTS frequency;
ALTER TABLE core.dgi_indicator DROP COLUMN IF EXISTS source_type;
ALTER TABLE core.dgi_indicator DROP COLUMN IF EXISTS lifecycle_status_id;

DELETE FROM ref.category WHERE scheme = 'dgi_indicator_lifecycle';

DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_indicator_lifecycle.sql';

COMMIT;
