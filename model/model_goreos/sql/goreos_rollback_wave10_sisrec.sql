-- Rollback Wave 10: SISREC Multi-Role Workflow
BEGIN;

-- Drop trigger and function
DROP TRIGGER IF EXISTS trg_rendition_history ON core.rendition;
DROP FUNCTION IF EXISTS fn_rendition_history();

-- Drop history table
DROP TABLE IF EXISTS core.rendition_history;

-- Drop amount column
ALTER TABLE core.rendition DROP COLUMN IF EXISTS amount;

-- Remove new states
DELETE FROM ref.category WHERE scheme = 'rendition_state' AND code IN ('EN_REVISION_RTF', 'VISADA_RTF', 'EN_REVISION_UCR');

-- Restore original sort_order for existing states
UPDATE ref.category SET sort_order = 2 WHERE scheme = 'rendition_state' AND code = 'EN_REVISION';
UPDATE ref.category SET sort_order = 3 WHERE scheme = 'rendition_state' AND code = 'OBSERVADA';
UPDATE ref.category SET sort_order = 4 WHERE scheme = 'rendition_state' AND code = 'APROBADA';
UPDATE ref.category SET sort_order = 5 WHERE scheme = 'rendition_state' AND code = 'RECHAZADA';

-- Restore EN_REVISION description
UPDATE ref.category SET
    description = 'gnubd:_AccountabilityState_InReview - En proceso de revisión técnica'
WHERE scheme = 'rendition_state' AND code = 'EN_REVISION';

-- Remove migration record
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_wave10_sisrec.sql';

COMMIT;
