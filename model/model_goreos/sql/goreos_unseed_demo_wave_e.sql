-- =============================================================================
-- GORE_OS — Remove Demo Data Wave E
-- =============================================================================
-- Removes ONLY DEMO- records from Wave E tables.
-- Safe to run multiple times.
-- =============================================================================

BEGIN;

-- Remove demo risks
DELETE FROM core.risk WHERE code LIKE 'DEMO-%';

-- Remove demo audit events (if any were created via API on demo data)
DELETE FROM txn.event
WHERE subject_type = 'core.risk'
  AND subject_id IN (SELECT id FROM core.risk WHERE code LIKE 'DEMO-%');

COMMIT;

-- Verificación:
-- SELECT COUNT(*) FROM core.risk WHERE code LIKE 'DEMO-%';  -- 0
