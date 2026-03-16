-- ============================================================================
-- Migration: Remove spurious DIIAP division
-- Date: 2026-03-15
-- Reason: DIIAP does not exist in SSOT organica. GORE Ñuble has 6 canonical
--         divisions: DIPLADE, DIPIR, DIDESO, DIFOI, DIT, DAF.
--         DIIAP was erroneously seeded in goreos_seed_territory.sql.
-- ============================================================================

BEGIN;

-- 1. Delete user referencing DIIAP
DELETE FROM core."user"
WHERE email = 'jefe.diiap@goreos.cl';

-- 2. Delete person created for DIIAP chief (if exists, from migration_roles_assignees)
DELETE FROM core.person
WHERE id NOT IN (SELECT person_id FROM core."user" WHERE person_id IS NOT NULL)
  AND rut = '22.222.223-8';

-- 3. Reassign any IPRs that reference DIIAP as sponsor_division to DIT
UPDATE core.ipr
SET sponsor_division_id = (SELECT id FROM core.organization WHERE code = 'DIT' LIMIT 1)
WHERE sponsor_division_id = (SELECT id FROM core.organization WHERE code = 'DIIAP' LIMIT 1);

-- 4. Reassign any budget_programs owned by DIIAP to DIT
UPDATE core.budget_program
SET owner_division_id = (SELECT id FROM core.organization WHERE code = 'DIT' LIMIT 1)
WHERE owner_division_id = (SELECT id FROM core.organization WHERE code = 'DIIAP' LIMIT 1);

-- 5. Reassign any agreements referencing DIIAP to DIT
UPDATE core.agreement
SET giver_id = (SELECT id FROM core.organization WHERE code = 'DIT' LIMIT 1)
WHERE giver_id = (SELECT id FROM core.organization WHERE code = 'DIIAP' LIMIT 1);

UPDATE core.agreement
SET receiver_id = (SELECT id FROM core.organization WHERE code = 'DIT' LIMIT 1)
WHERE receiver_id = (SELECT id FROM core.organization WHERE code = 'DIIAP' LIMIT 1);

-- 6. Reassign any ipr_party referencing DIIAP to DIT
UPDATE core.ipr_party
SET organization_id = (SELECT id FROM core.organization WHERE code = 'DIT' LIMIT 1)
WHERE organization_id = (SELECT id FROM core.organization WHERE code = 'DIIAP' LIMIT 1);

-- 7. Soft-delete the DIIAP organization (preserve for audit trail)
UPDATE core.organization
SET deleted_at = NOW()
WHERE code = 'DIIAP' AND deleted_at IS NULL;

-- 8. Record migration
INSERT INTO core.schema_migration (filename, applied_at, checksum, applied_by)
VALUES ('goreos_migration_remove_diiap.sql', NOW(), md5('remove-diiap-spurious'), 'claude')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
