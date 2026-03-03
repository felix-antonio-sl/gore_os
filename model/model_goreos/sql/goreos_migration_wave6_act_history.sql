BEGIN;

CREATE TABLE IF NOT EXISTS core.administrative_act_history (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    act_id            UUID NOT NULL REFERENCES core.administrative_act(id) ON DELETE CASCADE,
    previous_state_id UUID REFERENCES ref.category(id),
    new_state_id      UUID NOT NULL REFERENCES ref.category(id),
    changed_by_id     UUID NOT NULL REFERENCES core.user(id),
    comment           TEXT,
    changed_at        TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_act_history_act ON core.administrative_act_history(act_id);
COMMENT ON TABLE core.administrative_act_history IS 'Historial de cambios de estado de actos administrativos';

CREATE OR REPLACE FUNCTION fn_act_history()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.state_id IS DISTINCT FROM NEW.state_id THEN
        INSERT INTO core.administrative_act_history (
            act_id, previous_state_id, new_state_id, changed_by_id
        ) VALUES (
            NEW.id, OLD.state_id, NEW.state_id,
            COALESCE(NEW.updated_by_id, NEW.created_by_id)
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_act_history ON core.administrative_act;
CREATE TRIGGER trg_act_history
    AFTER UPDATE ON core.administrative_act
    FOR EACH ROW EXECUTE FUNCTION fn_act_history();

COMMIT;
DO $$ BEGIN RAISE NOTICE 'Wave 6: core.administrative_act_history + trigger created'; END $$;
