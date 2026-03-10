-- =============================================================================
-- GORE_OS — MIGRACIÓN: CONSOLIDACIÓN SCHEME aspect
-- =============================================================================
-- Archivo: goreos_migration_aspect_consolidation.sql
-- Fecha: 2026-03-09
-- Dependencia: goreos_migration_categorical_univocity.sql
-- =============================================================================
-- El scheme 'magnitude_aspect' (4 códigos, 953 rows en txn.magnitude) es un
-- sub-vocabulario del scheme 'aspect' (18 códigos, 3,496 rows). Consolidar
-- ambos en 'aspect' y agregar CHECK constraint.
-- =============================================================================

BEGIN;

-- ═══ Consolidar scheme: magnitude_aspect → aspect ═══
UPDATE ref.category
SET scheme = 'aspect'
WHERE scheme = 'magnitude_aspect';
-- Afecta 4 rows: BUDGET_AMOUNT, COMMITTED_AMOUNT, EXECUTED_AMOUNT, TRANSFER_AMOUNT
-- Los FKs en txn.magnitude referencian por UUID → no se rompen.

-- ═══ CHECK constraint en txn.magnitude ═══
ALTER TABLE txn.magnitude
  DROP CONSTRAINT IF EXISTS chk_magnitude_aspect_scheme,
  ADD CONSTRAINT chk_magnitude_aspect_scheme
  CHECK (aspect_id IS NULL OR fn_validate_category_scheme(aspect_id, 'aspect'));

COMMIT;

DO $$ BEGIN
    RAISE NOTICE 'GORE_OS Migración aspect_consolidation aplicada: 1 scheme consolidado + 1 CHECK constraint';
END $$;
