-- Rollback: goreos_rollback_new_roles.sql
BEGIN;

DELETE FROM core."user" WHERE email IN (
    'analista.dipir@goreos.cl', 'analista.diplade@goreos.cl',
    'rtf.daf@goreos.cl', 'juridico@goreos.cl'
);
DELETE FROM core.person WHERE id IN (
    'a0000001-0000-0000-0000-000000000010',
    'a0000001-0000-0000-0000-000000000011',
    'a0000001-0000-0000-0000-000000000012',
    'a0000001-0000-0000-0000-000000000013'
);
DELETE FROM ref.category WHERE scheme = 'system_role'
    AND code IN ('ANALISTA', 'RTF', 'ASESOR_JURIDICO');
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_new_roles.sql';

COMMIT;
