-- ============================================================================
-- GORE_OS Rollback: Ciclo 20+21 — Financial Thresholds
-- Fecha: 2026-03-03
-- ============================================================================

BEGIN;

DROP TABLE IF EXISTS core.financial_threshold CASCADE;

DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_ciclo20_thresholds.sql';

COMMIT;
