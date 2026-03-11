-- =============================================================================
-- GORE_OS — ROLLBACK: Parametrize hardcoded gate thresholds
-- =============================================================================
-- Reverts: goreos_migration_parametrize_thresholds.sql
-- Removes the 7 JSONB keys added to financing_track.thresholds.
-- =============================================================================

BEGIN;

-- FRIL: remove fril_sibling_days
UPDATE core.financing_track
SET thresholds = thresholds - 'fril_sibling_days'
WHERE code = 'FRIL' AND thresholds ? 'fril_sibling_days';

-- FRIL: remove fril_max_per_territory
UPDATE core.financing_track
SET thresholds = thresholds - 'fril_max_per_territory'
WHERE code = 'FRIL' AND thresholds ? 'fril_max_per_territory';

-- SUBV8: remove pagare_validity_months
UPDATE core.financing_track
SET thresholds = thresholds - 'pagare_validity_months'
WHERE code = 'SUBV8' AND thresholds ? 'pagare_validity_months';

-- SUBV8: remove pagare_coverage_pct
UPDATE core.financing_track
SET thresholds = thresholds - 'pagare_coverage_pct'
WHERE code = 'SUBV8' AND thresholds ? 'pagare_coverage_pct';

-- SUBV8: remove directorio_max_days
UPDATE core.financing_track
SET thresholds = thresholds - 'directorio_max_days'
WHERE code = 'SUBV8' AND thresholds ? 'directorio_max_days';

-- TRANSFER: remove glosa07_admin_max_pct
UPDATE core.financing_track
SET thresholds = thresholds - 'glosa07_admin_max_pct'
WHERE code = 'TRANSFER' AND thresholds ? 'glosa07_admin_max_pct';

-- TRANSFER: remove glosa07_honorarios_max_pct
UPDATE core.financing_track
SET thresholds = thresholds - 'glosa07_honorarios_max_pct'
WHERE code = 'TRANSFER' AND thresholds ? 'glosa07_honorarios_max_pct';

-- Remove migration record
DELETE FROM core.schema_migration
WHERE filename = 'goreos_migration_parametrize_thresholds.sql';

COMMIT;
