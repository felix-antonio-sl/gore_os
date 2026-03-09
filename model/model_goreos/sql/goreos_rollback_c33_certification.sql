-- goreos_rollback_c33_certification.sql
BEGIN;

DELETE FROM ref.category WHERE scheme = 'categoria_c33';
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_c33_certification.sql';

COMMIT;
