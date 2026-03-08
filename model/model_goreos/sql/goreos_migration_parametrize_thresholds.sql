-- Parametrize hardcoded gate thresholds into financing_track.thresholds JSONB
-- Moves 7 values from hardcoded Python to DB-configurable
BEGIN;

-- FRIL: fraccionamiento sibling detection window (±90 days)
UPDATE core.financing_track
SET thresholds = COALESCE(thresholds, '{}'::jsonb) || '{"fril_sibling_days": 90}'::jsonb
WHERE code = 'FRIL';

-- FRIL: max projects per territory per fiscal year
UPDATE core.financing_track
SET thresholds = COALESCE(thresholds, '{}'::jsonb) || '{"fril_max_per_territory": 5}'::jsonb
WHERE code = 'FRIL';

-- SUBV8: pagaré minimum validity period (months)
UPDATE core.financing_track
SET thresholds = COALESCE(thresholds, '{}'::jsonb) || '{"pagare_validity_months": 18}'::jsonb
WHERE code = 'SUBV8';

-- SUBV8: pagaré coverage requirement (% of monto total)
UPDATE core.financing_track
SET thresholds = COALESCE(thresholds, '{}'::jsonb) || '{"pagare_coverage_pct": 100}'::jsonb
WHERE code = 'SUBV8';

-- SUBV8: board certificate maximum age (days)
UPDATE core.financing_track
SET thresholds = COALESCE(thresholds, '{}'::jsonb) || '{"directorio_max_days": 60}'::jsonb
WHERE code = 'SUBV8';

-- TRANSFER: Glosa 07 administrative expense cap (%)
UPDATE core.financing_track
SET thresholds = COALESCE(thresholds, '{}'::jsonb) || '{"glosa07_admin_max_pct": 5.0}'::jsonb
WHERE code = 'TRANSFER';

-- TRANSFER: Glosa 07 honorarios cap (%)
UPDATE core.financing_track
SET thresholds = COALESCE(thresholds, '{}'::jsonb) || '{"glosa07_honorarios_max_pct": 5.0}'::jsonb
WHERE code = 'TRANSFER';

-- Self-register
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_parametrize_thresholds.sql', 'manual', 'parametrize_thresholds')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
