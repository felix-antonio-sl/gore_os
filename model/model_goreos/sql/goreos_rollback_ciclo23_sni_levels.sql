-- Rollback Ciclo 23: SNI Level Configuration + SEREMI evaluator type

BEGIN;

-- Remove migration record
DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_ciclo23_sni_levels.sql';

-- Remove SEREMI evaluator type
DELETE FROM ref.category
WHERE scheme = 'evaluator_type' AND code = 'SEREMI';

-- Drop SNI level config table
DROP TABLE IF EXISTS core.sni_level_config;

COMMIT;
