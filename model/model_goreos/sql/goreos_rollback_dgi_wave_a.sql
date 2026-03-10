-- ============================================================================
-- Rollback: DGI Wave A
-- ============================================================================

BEGIN;

DROP TABLE IF EXISTS core.dgi_decree;

DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_dgi_wave_a.sql';

COMMIT;
