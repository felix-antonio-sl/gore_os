-- ============================================================================
-- Migration: Lifecycle Wave 4 — SLAs + ITO + Gates Menores
-- Date: 2026-03-11
-- Description:
--   4A. Add phase_entered_at column + trigger on core.ipr
--   4B. Evaluation SLAs in financing_track.sla_days
--   4C. ITO role in ipr_party_role scheme
-- ============================================================================

BEGIN;

-- ============================================================================
-- 4A. phase_entered_at: track time in current state for SLA monitoring
-- ============================================================================

ALTER TABLE core.ipr ADD COLUMN IF NOT EXISTS phase_entered_at TIMESTAMPTZ;

-- Set initial value for existing IPRs
UPDATE core.ipr SET phase_entered_at = updated_at WHERE phase_entered_at IS NULL;

-- Trigger: auto-update on status_id change
CREATE OR REPLACE FUNCTION fn_ipr_phase_entered()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status_id IS DISTINCT FROM NEW.status_id THEN
        NEW.phase_entered_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ipr_phase_entered ON core.ipr;
CREATE TRIGGER trg_ipr_phase_entered
    BEFORE UPDATE OF status_id ON core.ipr
    FOR EACH ROW EXECUTE FUNCTION fn_ipr_phase_entered();

-- ============================================================================
-- 4B. Evaluation SLA days in financing_track
-- ============================================================================

UPDATE core.financing_track SET sla_days = COALESCE(sla_days, '{}'::jsonb) || '{"evaluation_max_days": 45}'::jsonb
WHERE code = 'FRIL';

UPDATE core.financing_track SET sla_days = COALESCE(sla_days, '{}'::jsonb) || '{"evaluation_max_days": 60}'::jsonb
WHERE code = 'SNI';

UPDATE core.financing_track SET sla_days = COALESCE(sla_days, '{}'::jsonb) || '{"evaluation_max_days": 30}'::jsonb
WHERE code = 'C33';

UPDATE core.financing_track SET sla_days = COALESCE(sla_days, '{}'::jsonb) || '{"evaluation_max_days": 90}'::jsonb
WHERE code = 'GLOSA06';

UPDATE core.financing_track SET sla_days = COALESCE(sla_days, '{}'::jsonb) || '{"evaluation_max_days": 90}'::jsonb
WHERE code = 'TRANSFER';

UPDATE core.financing_track SET sla_days = COALESCE(sla_days, '{}'::jsonb) || '{"evaluation_max_days": 90}'::jsonb
WHERE code = 'SUBV8';

UPDATE core.financing_track SET sla_days = COALESCE(sla_days, '{}'::jsonb) || '{"evaluation_max_days": 60}'::jsonb
WHERE code = 'FRPD';

-- ============================================================================
-- 4C. ITO party role
-- ============================================================================

INSERT INTO ref.category (scheme, code, label, description, sort_order)
VALUES ('ipr_party_role', 'ITO', 'Inspector Técnico de Obra',
        'Responsable de inspección técnica durante ejecución de obra', 10)
ON CONFLICT (scheme, code) DO NOTHING;

-- ============================================================================
-- Track migration
-- ============================================================================
INSERT INTO core.schema_migration (filename, applied_at)
VALUES ('goreos_migration_lifecycle_wave4.sql', NOW())
ON CONFLICT (filename) DO NOTHING;

COMMIT;
