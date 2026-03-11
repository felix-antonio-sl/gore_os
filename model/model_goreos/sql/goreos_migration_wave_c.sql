-- Wave C Migration: DMAIC structured improvement + Lean metrics
-- Adds started_at/completed_at columns to dgi_initiative
-- Plus trigger to auto-set timestamps on status transitions

BEGIN;

-- Track migration
INSERT INTO core.schema_migration (filename)
VALUES ('goreos_migration_wave_c.sql')
ON CONFLICT (filename) DO NOTHING;

-- 1. Add timing columns for lean metrics (lead time, cycle time)
ALTER TABLE core.dgi_initiative
  ADD COLUMN IF NOT EXISTS started_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ;

COMMENT ON COLUMN core.dgi_initiative.started_at IS 'Auto-set on first move to EN_CURSO (cycle time start)';
COMMENT ON COLUMN core.dgi_initiative.completed_at IS 'Auto-set on move to COMPLETADA (cycle/lead time end)';

-- 2. Trigger: auto-set started_at on first EN_CURSO, completed_at on COMPLETADA
CREATE OR REPLACE FUNCTION core.trg_initiative_timing_fn()
RETURNS TRIGGER AS $$
DECLARE
    new_status_code TEXT;
BEGIN
    -- Only fire on status_id change
    IF NEW.status_id IS DISTINCT FROM OLD.status_id THEN
        SELECT code INTO new_status_code
        FROM ref.category
        WHERE id = NEW.status_id AND scheme = 'dgi_initiative_status';

        -- First move to EN_CURSO: set started_at
        IF new_status_code = 'EN_CURSO' AND OLD.started_at IS NULL THEN
            NEW.started_at := NOW();
        END IF;

        -- Move to COMPLETADO: set completed_at
        IF new_status_code = 'COMPLETADO' THEN
            NEW.completed_at := NOW();
        END IF;

        -- Move away from COMPLETADO: clear completed_at
        IF new_status_code != 'COMPLETADO' AND OLD.completed_at IS NOT NULL THEN
            NEW.completed_at := NULL;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_initiative_timing ON core.dgi_initiative;
CREATE TRIGGER trg_initiative_timing
    BEFORE UPDATE ON core.dgi_initiative
    FOR EACH ROW
    EXECUTE FUNCTION core.trg_initiative_timing_fn();

COMMIT;
