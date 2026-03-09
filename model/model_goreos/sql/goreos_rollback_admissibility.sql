BEGIN;

-- ============================================================
-- Rollback: Admissibility Sub-states (PRE_ADMISIBLE)
-- Reverses goreos_migration_admissibility.sql
-- ============================================================

-- 1. Drop operational tables (order: child first)
DROP TABLE IF EXISTS core.admissibility_check;
DROP TABLE IF EXISTS core.admissibility_item;

-- 2. Restore original EN_REVISION transitions (direct to ADMISIBLE)
UPDATE ref.category
SET valid_transitions = '["ADMISIBLE", "INADMISIBLE"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_REVISION';

-- 3. Remove PRE_ADMISIBLE state
DELETE FROM ref.category
WHERE scheme = 'ipr_state' AND code = 'PRE_ADMISIBLE';

-- 4. Restore original sort_order (shift back down)
UPDATE ref.category
SET sort_order = sort_order - 1
WHERE scheme = 'ipr_state'
  AND sort_order >= 4;

-- 5. Remove migration record
DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_admissibility.sql';

COMMIT;
