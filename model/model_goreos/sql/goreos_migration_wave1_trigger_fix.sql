-- =============================================================================
-- GORE_OS Wave 1 — Fix fn_validate_state_transition (status_id → dynamic)
-- =============================================================================
-- Bug: La función hardcodeaba OLD.status_id / NEW.status_id, pero las tablas
--       usan columnas distintas: state_id (agreement, commitment, act, file),
--       status_id (ipr, work_item), payment_status_id (installment).
-- Fix:  Usar TG_ARGV[0] para recibir el nombre de columna desde cada trigger.
--       EXECUTE format() + ($1).%I accede dinámicamente a la columna correcta.
-- =============================================================================

BEGIN;

-- 1. Reemplazar la función con acceso dinámico a columna
CREATE OR REPLACE FUNCTION fn_validate_state_transition()
RETURNS TRIGGER AS $$
DECLARE
    v_col  TEXT := COALESCE(TG_ARGV[0], 'state_id');
    v_old_id UUID;
    v_new_id UUID;
    v_old_code VARCHAR(32);
    v_new_code VARCHAR(32);
    v_valid_transitions JSONB;
BEGIN
    -- Extraer IDs dinámicamente según la columna del trigger
    EXECUTE format('SELECT ($1).%I, ($2).%I', v_col, v_col)
        INTO v_old_id, v_new_id
        USING OLD, NEW;

    -- Si no hay cambio de estado, no validar transición
    IF v_old_id IS NOT DISTINCT FROM v_new_id THEN
        RETURN NEW;
    END IF;

    -- Obtener código del estado anterior
    SELECT code INTO v_old_code
    FROM ref.category WHERE id = v_old_id;

    -- Obtener código del nuevo estado
    SELECT code INTO v_new_code
    FROM ref.category WHERE id = v_new_id;

    -- Obtener transiciones válidas del estado anterior
    SELECT valid_transitions INTO v_valid_transitions
    FROM ref.category WHERE id = v_old_id;

    -- Si hay transiciones definidas, validar (incluye [] como estado terminal)
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
'Valida transiciones de estado usando TG_ARGV[0] como nombre de columna (default: state_id)';

-- 2. Recrear triggers pasando el nombre de columna como argumento

-- IPR: usa status_id
DROP TRIGGER IF EXISTS trg_ipr_state_transition ON core.ipr;
CREATE TRIGGER trg_ipr_state_transition
    BEFORE UPDATE OF status_id ON core.ipr
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition('status_id');

-- Work Item: usa status_id (tabla puede no existir aún en producción)
DO $$ BEGIN
    DROP TRIGGER IF EXISTS trg_work_item_state_transition ON core.work_item;
    CREATE TRIGGER trg_work_item_state_transition
        BEFORE UPDATE OF status_id ON core.work_item
        FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition('status_id');
EXCEPTION WHEN undefined_table THEN
    RAISE NOTICE 'core.work_item no existe — trigger omitido';
END $$;

-- Operational Commitment: usa state_id
-- NOTA: NO se crea el trigger aquí. Requiere endpoint /iniciar (PENDIENTE→EN_PROGRESO)
-- que aún no existe. Se creará en wave futura junto con el endpoint.
-- DROP TRIGGER IF EXISTS trg_commitment_state_transition ON core.operational_commitment;
-- CREATE TRIGGER trg_commitment_state_transition
--     BEFORE UPDATE OF state_id ON core.operational_commitment
--     FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition('state_id');

-- Agreement: usa state_id
DROP TRIGGER IF EXISTS trg_agreement_state_transition ON core.agreement;
CREATE TRIGGER trg_agreement_state_transition
    BEFORE UPDATE OF state_id ON core.agreement
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition('state_id');

-- Administrative Act: usa state_id
DROP TRIGGER IF EXISTS trg_act_state_transition ON core.administrative_act;
CREATE TRIGGER trg_act_state_transition
    BEFORE UPDATE OF state_id ON core.administrative_act
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition('state_id');

-- Agreement Installment: usa payment_status_id
DROP TRIGGER IF EXISTS trg_installment_payment_transition ON core.agreement_installment;
CREATE TRIGGER trg_installment_payment_transition
    BEFORE UPDATE OF payment_status_id ON core.agreement_installment
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition('payment_status_id');

-- Electronic File: usa status_id (no state_id como decía remediation.sql)
DROP TRIGGER IF EXISTS trg_file_status_transition ON core.electronic_file;
CREATE TRIGGER trg_file_status_transition
    BEFORE UPDATE OF status_id ON core.electronic_file
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition('status_id');

COMMIT;

DO $$ BEGIN RAISE NOTICE 'Wave 1: fn_validate_state_transition fixed — dynamic column via TG_ARGV[0]'; END $$;
