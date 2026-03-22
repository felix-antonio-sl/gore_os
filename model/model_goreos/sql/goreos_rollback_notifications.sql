-- Rollback: Remove core.notification table and sample data

BEGIN;

DROP TABLE IF EXISTS core.notification CASCADE;

DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_notifications.sql';

COMMIT;
