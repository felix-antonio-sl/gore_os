-- =============================================================================
-- GORE_OS — ROLLBACK: Roles y Assignees
-- =============================================================================
-- Reverts: goreos_migration_roles_assignees.sql
-- 1. NULLs out assignee_id and sponsor_division_id on core.ipr
-- 2. Deletes created users (by email)
-- 3. Deletes created persons (by rut)
-- =============================================================================

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. NULL out assignee_id for IPRs assigned by this migration
-- ═══════════════════════════════════════════════════════════════════════════
-- Revert assignee_id where the assignee is one of the users we created
UPDATE core.ipr
SET assignee_id = NULL
WHERE assignee_id IN (
    SELECT id FROM core."user"
    WHERE email IN (
        'jefe.dideso@goreos.cl', 'jefe.difoi@goreos.cl',
        'jefe.dipir@goreos.cl',
        'jefe.diplade@goreos.cl', 'jefe.dit@goreos.cl'
    )
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 2. NULL out sponsor_division_id populated by this migration
-- ═══════════════════════════════════════════════════════════════════════════
UPDATE core.ipr
SET sponsor_division_id = NULL
WHERE sponsor_division_id IS NOT NULL;

-- ═══════════════════════════════════════════════════════════════════════════
-- 3. Delete created users (12 total: 6 roles + 6 jefes de división)
-- ═══════════════════════════════════════════════════════════════════════════
DELETE FROM core."user"
WHERE email IN (
    'gobernador@goreos.cl',
    'secretario.core@goreos.cl',
    'consejero1@goreos.cl',
    'consejero2@goreos.cl',
    'jefe.finanzas@goreos.cl',
    'jefe.ucr@goreos.cl',
    'jefe.dideso@goreos.cl',
    'jefe.difoi@goreos.cl',
    'jefe.dipir@goreos.cl',
    'jefe.diplade@goreos.cl',
    'jefe.dit@goreos.cl'
);

-- ═══════════════════════════════════════════════════════════════════════════
-- 4. Delete created persons (12 total: 6 institutional + 6 division chiefs)
-- ═══════════════════════════════════════════════════════════════════════════
DELETE FROM core.person
WHERE rut IN (
    '11.111.111-1', '11.111.112-K', '11.111.113-8',
    '11.111.114-6', '11.111.115-4', '11.111.116-2',
    '22.222.221-1', '22.222.222-K', '22.222.223-8',
    '22.222.224-6', '22.222.225-4', '22.222.226-2'
);

-- 5. Remove migration record
DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_roles_assignees.sql';

COMMIT;

DO $$ BEGIN
    RAISE NOTICE 'GORE_OS Rollback roles_assignees: assignee_id/sponsor_division_id NULLed, 12 users + 12 persons deleted';
END $$;
