-- goreos_migration_budget_program_code.sql
-- Adds program_code_id FK to core.budget_program (DIPRES Level 5)

BEGIN;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'core' AND table_name = 'budget_program' AND column_name = 'program_code_id'
  ) THEN
    ALTER TABLE core.budget_program
      ADD COLUMN program_code_id UUID REFERENCES ref.category(id);
  END IF;

  -- Categorical univocity CHECK (consistent with item_id, allocation_id)
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE table_schema = 'core' AND table_name = 'budget_program' AND constraint_name = 'chk_program_code_scheme'
  ) THEN
    ALTER TABLE core.budget_program ADD CONSTRAINT chk_program_code_scheme
      CHECK (program_code_id IS NULL OR fn_validate_category_scheme(program_code_id, 'budget_program_code'));
  END IF;
END $$;

-- Self-register migration
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_budget_program_code.sql', 'manual', 'budget_program_code_self_register')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
