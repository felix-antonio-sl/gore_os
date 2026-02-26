-- Migration: Agreement state history tracking
-- Mirrors the commitment_history pattern for agreement state transitions.

CREATE TABLE IF NOT EXISTS core.agreement_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agreement_id UUID REFERENCES core.agreement(id) ON DELETE CASCADE NOT NULL,
    previous_state_id UUID REFERENCES ref.category(id),
    new_state_id UUID REFERENCES ref.category(id) NOT NULL,
    changed_by_id UUID REFERENCES core."user"(id) NOT NULL,
    comment TEXT,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agreement_history_agreement
    ON core.agreement_history(agreement_id);

CREATE OR REPLACE FUNCTION fn_agreement_history() RETURNS TRIGGER AS $$
BEGIN
    IF OLD.state_id IS DISTINCT FROM NEW.state_id THEN
        INSERT INTO core.agreement_history (
            agreement_id, previous_state_id, new_state_id, changed_by_id
        ) VALUES (
            NEW.id, OLD.state_id, NEW.state_id,
            COALESCE(NEW.updated_by_id, NEW.created_by_id)
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_agreement_history ON core.agreement;
CREATE TRIGGER trg_agreement_history
    AFTER UPDATE ON core.agreement
    FOR EACH ROW
    EXECUTE FUNCTION fn_agreement_history();
