-- Wave 10: SISREC Multi-Role Workflow
-- Date: 2026-03-03
-- Purpose: Expand rendition state machine (RTF→DAF→UCR), add amount column,
--          rendition_history table + audit trigger.
-- Reversible: YES (see goreos_rollback_wave10_sisrec.sql)
-- Idempotent: YES (ON CONFLICT / IF NOT EXISTS / IF EXISTS guards)

BEGIN;

-- ---------------------------------------------------------------------------
-- A1: New rendition_state codes + reorder existing
-- ---------------------------------------------------------------------------
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('rendition_state', 'EN_REVISION_RTF', 'En Revisión RTF', 'Revisión técnica por Referente Técnico Financiero', 2),
('rendition_state', 'VISADA_RTF',      'Visada RTF',      'Rendición visada por RTF, pendiente envío a UCR', 3),
('rendition_state', 'EN_REVISION_UCR', 'En Revisión UCR', 'Revisión final por Unidad de Control de Rendiciones', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

-- Update sort_order for existing states (OBSERVADA, APROBADA, RECHAZADA)
UPDATE ref.category SET sort_order = 5 WHERE scheme = 'rendition_state' AND code = 'OBSERVADA';
UPDATE ref.category SET sort_order = 6 WHERE scheme = 'rendition_state' AND code = 'APROBADA';
UPDATE ref.category SET sort_order = 7 WHERE scheme = 'rendition_state' AND code = 'RECHAZADA';

-- Deprecate legacy EN_REVISION (freeze, no transitions)
UPDATE ref.category SET sort_order = 99,
    description = 'DEPRECADO: reemplazado por EN_REVISION_RTF/EN_REVISION_UCR'
WHERE scheme = 'rendition_state' AND code = 'EN_REVISION';


-- ---------------------------------------------------------------------------
-- A2: Amount column on core.rendition
-- ---------------------------------------------------------------------------
ALTER TABLE core.rendition ADD COLUMN IF NOT EXISTS amount NUMERIC(18,2);
COMMENT ON COLUMN core.rendition.amount IS 'Monto rendido en la rendición';


-- ---------------------------------------------------------------------------
-- A3: Rendition history table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS core.rendition_history (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rendition_id      UUID NOT NULL REFERENCES core.rendition(id) ON DELETE CASCADE,
    previous_state_id UUID REFERENCES ref.category(id),
    new_state_id      UUID NOT NULL REFERENCES ref.category(id),
    changed_by_id     UUID NOT NULL REFERENCES core.user(id),
    comment           TEXT,
    changed_at        TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_rendition_history_rendition ON core.rendition_history(rendition_id);
COMMENT ON TABLE core.rendition_history IS 'Historial de cambios de estado de rendiciones (SISREC)';


-- ---------------------------------------------------------------------------
-- A4: Trigger fn_rendition_history + trg_rendition_history
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_rendition_history()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.state_id IS DISTINCT FROM NEW.state_id THEN
        INSERT INTO core.rendition_history (
            rendition_id, previous_state_id, new_state_id, changed_by_id
        ) VALUES (
            NEW.id, OLD.state_id, NEW.state_id,
            COALESCE(NEW.updated_by_id, NEW.created_by_id)
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_rendition_history ON core.rendition;
CREATE TRIGGER trg_rendition_history
    AFTER UPDATE ON core.rendition
    FOR EACH ROW EXECUTE FUNCTION fn_rendition_history();


-- ---------------------------------------------------------------------------
-- A5: Register in schema_migration
-- ---------------------------------------------------------------------------
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_wave10_sisrec.sql', 'manual', 'wave10_self_register')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
DO $$ BEGIN RAISE NOTICE 'Wave 10: SISREC multi-role workflow (3 states + amount + history table + trigger)'; END $$;
