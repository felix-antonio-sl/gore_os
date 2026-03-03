-- Rollback Ciclo 24 Wave 4: Remove SUBV8 documentary thresholds

UPDATE core.financing_track
SET thresholds = thresholds - 'pagare_validity_months' - 'directorio_max_days',
    updated_at = NOW()
WHERE code = 'SUBV8';
