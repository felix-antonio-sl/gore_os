-- =============================================================================
-- GORE_OS Wave 1 ROLLBACK — Restore original fn_validate_state_transition
-- =============================================================================
-- Reverts to the original hardcoded status_id version.
-- WARNING: This re-introduces the bug for tables using state_id.
-- =============================================================================

BEGIN;

-- 1. Restore original function with hardcoded status_id
CREATE OR REPLACE FUNCTION fn_validate_state_transition()
RETURNS TRIGGER AS $$
DECLARE
    v_valid_transitions JSONB;
    v_old_code VARCHAR(32);
    v_new_code VARCHAR(32);
BEGIN
    IF OLD.status_id IS NOT DISTINCT FROM NEW.status_id THEN
        RETURN NEW;
    END IF;

    SELECT code INTO v_old_code
    FROM ref.category WHERE id = OLD.status_id;

    SELECT code INTO v_new_code
    FROM ref.category WHERE id = NEW.status_id;

    SELECT valid_transitions INTO v_valid_transitions
    FROM ref.category WHERE id = OLD.status_id;

    IF v_valid_transitions IS NOT NULL THEN
        IF NOT (v_valid_transitions ? v_new_code) THEN
            RAISE EXCEPTION 'Transición de estado inválida: % -> %. Transiciones válidas: %',
                v_old_code, v_new_code, v_valid_transitions;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_validate_state_transition() IS
'Valida que las transiciones de estado estén en valid_transitions';

-- 2. Recreate triggers without TG_ARGV arguments (original form)
DROP TRIGGER IF EXISTS trg_ipr_state_transition ON core.ipr;
CREATE TRIGGER trg_ipr_state_transition
    BEFORE UPDATE OF status_id ON core.ipr
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();

DO $$ BEGIN
    DROP TRIGGER IF EXISTS trg_work_item_state_transition ON core.work_item;
    CREATE TRIGGER trg_work_item_state_transition
        BEFORE UPDATE OF status_id ON core.work_item
        FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();
EXCEPTION WHEN undefined_table THEN
    RAISE NOTICE 'core.work_item no existe — trigger omitido';
END $$;

DROP TRIGGER IF EXISTS trg_commitment_state_transition ON core.operational_commitment;
CREATE TRIGGER trg_commitment_state_transition
    BEFORE UPDATE OF state_id ON core.operational_commitment
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();

DROP TRIGGER IF EXISTS trg_agreement_state_transition ON core.agreement;
CREATE TRIGGER trg_agreement_state_transition
    BEFORE UPDATE OF state_id ON core.agreement
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();

DROP TRIGGER IF EXISTS trg_act_state_transition ON core.administrative_act;
CREATE TRIGGER trg_act_state_transition
    BEFORE UPDATE OF state_id ON core.administrative_act
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();

DROP TRIGGER IF EXISTS trg_installment_payment_transition ON core.agreement_installment;
CREATE TRIGGER trg_installment_payment_transition
    BEFORE UPDATE OF payment_status_id ON core.agreement_installment
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();

DROP TRIGGER IF EXISTS trg_file_status_transition ON core.electronic_file;
CREATE TRIGGER trg_file_status_transition
    BEFORE UPDATE OF status_id ON core.electronic_file
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();

COMMIT;

DO $$ BEGIN RAISE NOTICE 'Wave 1 ROLLBACK: fn_validate_state_transition restored to original (status_id hardcoded)'; END $$;
