-- Ciclo 24 Wave 1: FRIL tender deadline threshold
-- HΩ-08: Add tender_deadline_days to FRIL track thresholds

UPDATE core.financing_track
SET thresholds = thresholds || '{"tender_deadline_days": 90}'::jsonb,
    updated_at = NOW()
WHERE code = 'FRIL';
