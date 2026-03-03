-- Rollback Ciclo 24 Wave 1: Remove tender_deadline_days from FRIL thresholds

UPDATE core.financing_track
SET thresholds = thresholds - 'tender_deadline_days',
    updated_at = NOW()
WHERE code = 'FRIL';
