-- Rollback Wave 8: Remove financing_track table
BEGIN;
DROP TABLE IF EXISTS core.financing_track;
COMMIT;
