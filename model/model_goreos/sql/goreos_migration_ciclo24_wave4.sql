-- Ciclo 24 Wave 4: SUBV8 documentary requirement thresholds (HΩ-03, HΩ-04)

UPDATE core.financing_track
SET thresholds = thresholds || '{"pagare_validity_months": 18, "directorio_max_days": 60}'::jsonb,
    updated_at = NOW()
WHERE code = 'SUBV8';
