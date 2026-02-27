-- Rollback: Revert core.rendition coproduct migration
-- Date: 2026-02-27
-- WARNING: Cannot re-add NOT NULL if NULLs exist in agreement_id/renderer_id.
--          Run cleanup queries first if needed.

BEGIN;

-- 1. Drop CHECK constraint
ALTER TABLE core.rendition DROP CONSTRAINT IF EXISTS chk_rendition_link;

-- 2. Drop index
DROP INDEX IF EXISTS core.idx_rendition_ipr;

-- 3. Drop ipr_id column
ALTER TABLE core.rendition DROP COLUMN IF EXISTS ipr_id;

-- 4. Re-add NOT NULL constraints (only safe if no NULLs exist)
-- Uncomment after verifying: SELECT COUNT(*) FROM core.rendition WHERE agreement_id IS NULL;
-- ALTER TABLE core.rendition ALTER COLUMN agreement_id SET NOT NULL;
-- ALTER TABLE core.rendition ALTER COLUMN renderer_id SET NOT NULL;

COMMIT;
