-- goreos_rollback_budget_program_code.sql
-- Removes program_code_id from core.budget_program

BEGIN;

ALTER TABLE core.budget_program DROP COLUMN IF EXISTS program_code_id;

DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_budget_program_code.sql';

COMMIT;
