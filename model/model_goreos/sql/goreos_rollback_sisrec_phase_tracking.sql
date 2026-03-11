-- =============================================================================
-- GORE_OS — ROLLBACK: SISREC phase tracking columns
-- =============================================================================
-- Reverts: goreos_migration_sisrec_phase_tracking.sql
-- Drops phase_entered_at and responsible_id columns from core.rendition,
-- plus the responsible index.
-- =============================================================================

BEGIN;

-- 1. Drop index on responsible_id
DROP INDEX IF EXISTS core.idx_rendition_responsible;

-- 2. Drop columns added by migration
ALTER TABLE core.rendition DROP COLUMN IF EXISTS phase_entered_at;
ALTER TABLE core.rendition DROP COLUMN IF EXISTS responsible_id;

-- 3. Remove migration record
DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_sisrec_phase_tracking.sql';

COMMIT;
