-- Rollback: Remove auth audit event_type codes

BEGIN;

DELETE FROM ref.category
WHERE scheme = 'event_type'
  AND code IN ('LOGIN', 'LOGIN_FAILED', 'PASSWORD_CHANGED');

DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_audit_events.sql';

COMMIT;
