BEGIN;
DROP INDEX IF EXISTS core.idx_rendition_escalation_rendition;
DROP INDEX IF EXISTS core.idx_rendition_archived;
DROP TABLE IF EXISTS core.rendition_escalation;
ALTER TABLE core.rendition DROP COLUMN IF EXISTS archived_at;
DROP TABLE IF EXISTS core.rendition_phase;
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_sisrec_8phase.sql';
COMMIT;
