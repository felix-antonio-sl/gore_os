-- Rollback: goreos_migration_aspect_consolidation.sql
BEGIN;

ALTER TABLE txn.magnitude DROP CONSTRAINT IF EXISTS chk_magnitude_aspect_scheme;

UPDATE ref.category
SET scheme = 'magnitude_aspect'
WHERE scheme = 'aspect'
  AND code IN ('BUDGET_AMOUNT', 'COMMITTED_AMOUNT', 'EXECUTED_AMOUNT', 'TRANSFER_AMOUNT');

DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_aspect_consolidation.sql';

COMMIT;
DO $$ BEGIN RAISE NOTICE 'Rollback aspect_consolidation completado'; END $$;
