-- =============================================================================
-- GORE_OS v3.0 - TRIGGERS DE REMEDIACIÓN CATEGORIAL
-- =============================================================================
-- Archivo: goreos_triggers_remediation.sql
-- Descripción: Triggers para remediar hallazgos de auditoría categorial
-- Fecha: 2026-01-27
-- Dependencias: goreos_ddl.sql, goreos_triggers.sql, goreos_seed.sql
-- Referencia: Auditoría Categorial Consolidada
-- =============================================================================

-- =============================================================================
-- P0-2: TRIGGERS DE VALIDACIÓN DE TRANSICIONES DE ESTADO
-- =============================================================================
-- Hallazgo CPL-001 / CAT-005: Activar fn_validate_state_transition()
-- para tablas con máquinas de estado

-- IPR: transiciones de estado operativo
DROP TRIGGER IF EXISTS trg_ipr_state_transition ON core.ipr;
CREATE TRIGGER trg_ipr_state_transition
    BEFORE UPDATE OF status_id ON core.ipr
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();

COMMENT ON TRIGGER trg_ipr_state_transition ON core.ipr IS
'CPL-001 FIX: Valida transiciones de estado según valid_transitions en ref.category';

-- Work Item: transiciones de estado de trabajo
DROP TRIGGER IF EXISTS trg_work_item_state_transition ON core.work_item;
CREATE TRIGGER trg_work_item_state_transition
    BEFORE UPDATE OF status_id ON core.work_item
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();

COMMENT ON TRIGGER trg_work_item_state_transition ON core.work_item IS
'CPL-001 FIX: Valida transiciones de estado según valid_transitions en ref.category';

-- Operational Commitment: transiciones de estado de compromiso
DROP TRIGGER IF EXISTS trg_commitment_state_transition ON core.operational_commitment;
CREATE TRIGGER trg_commitment_state_transition
    BEFORE UPDATE OF state_id ON core.operational_commitment
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();

COMMENT ON TRIGGER trg_commitment_state_transition ON core.operational_commitment IS
'CPL-001 FIX: Valida transiciones de estado según valid_transitions en ref.category';

-- Agreement: transiciones de estado de convenio
DROP TRIGGER IF EXISTS trg_agreement_state_transition ON core.agreement;
CREATE TRIGGER trg_agreement_state_transition
    BEFORE UPDATE OF state_id ON core.agreement
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();

COMMENT ON TRIGGER trg_agreement_state_transition ON core.agreement IS
'CPL-001 FIX: Valida transiciones de estado según valid_transitions en ref.category';

-- Administrative Act: transiciones de estado de acto administrativo
DROP TRIGGER IF EXISTS trg_act_state_transition ON core.administrative_act;
CREATE TRIGGER trg_act_state_transition
    BEFORE UPDATE OF state_id ON core.administrative_act
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();

COMMENT ON TRIGGER trg_act_state_transition ON core.administrative_act IS
'CPL-001 FIX: Valida transiciones de estado según valid_transitions en ref.category';

-- Agreement Installment: transiciones de payment_status
DROP TRIGGER IF EXISTS trg_installment_payment_transition ON core.agreement_installment;
CREATE TRIGGER trg_installment_payment_transition
    BEFORE UPDATE OF payment_status_id ON core.agreement_installment
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();

COMMENT ON TRIGGER trg_installment_payment_transition ON core.agreement_installment IS
'CAT-005 FIX: Valida transiciones de payment_status según valid_transitions';

-- Electronic File: transiciones de file_status
DROP TRIGGER IF EXISTS trg_file_status_transition ON core.electronic_file;
CREATE TRIGGER trg_file_status_transition
    BEFORE UPDATE OF state_id ON core.electronic_file
    FOR EACH ROW EXECUTE FUNCTION fn_validate_state_transition();

COMMENT ON TRIGGER trg_file_status_transition ON core.electronic_file IS
'CAT-005 FIX: Valida transiciones de file_status según valid_transitions';

-- =============================================================================
-- P0-3: TRIGGERS DE VALIDACIÓN DE SCHEME EN FKs A ref.category
-- =============================================================================
-- Hallazgo REF-001 / CAT-003: Validar que FKs a ref.category pertenecen
-- al scheme correcto usando fn_validate_category_scheme()

-- Función auxiliar para validar scheme en múltiples columnas
CREATE OR REPLACE FUNCTION fn_validate_ipr_schemes()
RETURNS TRIGGER AS $$
BEGIN
    -- Validar mcd_phase_id
    IF NEW.mcd_phase_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.mcd_phase_id, 'mcd_phase') THEN
            RAISE EXCEPTION 'mcd_phase_id debe pertenecer al scheme "mcd_phase"';
        END IF;
    END IF;

    -- Validar status_id
    IF NEW.status_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.status_id, 'ipr_state') THEN
            RAISE EXCEPTION 'status_id debe pertenecer al scheme "ipr_state"';
        END IF;
    END IF;

    -- Validar mechanism_id
    IF NEW.mechanism_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.mechanism_id, 'mechanism') THEN
            RAISE EXCEPTION 'mechanism_id debe pertenecer al scheme "mechanism"';
        END IF;
    END IF;

    -- Validar budget_subtitle_id
    IF NEW.budget_subtitle_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.budget_subtitle_id, 'budget_subtitle') THEN
            RAISE EXCEPTION 'budget_subtitle_id debe pertenecer al scheme "budget_subtitle"';
        END IF;
    END IF;

    -- Validar alert_level_id
    IF NEW.alert_level_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.alert_level_id, 'alert_level') THEN
            RAISE EXCEPTION 'alert_level_id debe pertenecer al scheme "alert_level"';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_validate_ipr_schemes() IS
'REF-001 FIX: Valida que todos los FKs a ref.category en core.ipr usen el scheme correcto';

DROP TRIGGER IF EXISTS trg_ipr_validate_schemes ON core.ipr;
CREATE TRIGGER trg_ipr_validate_schemes
    BEFORE INSERT OR UPDATE ON core.ipr
    FOR EACH ROW EXECUTE FUNCTION fn_validate_ipr_schemes();

-- Work Item: validar schemes
CREATE OR REPLACE FUNCTION fn_validate_work_item_schemes()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.status_id, 'work_item_status') THEN
            RAISE EXCEPTION 'status_id debe pertenecer al scheme "work_item_status"';
        END IF;
    END IF;

    IF NEW.priority_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.priority_id, 'work_item_priority') THEN
            RAISE EXCEPTION 'priority_id debe pertenecer al scheme "work_item_priority"';
        END IF;
    END IF;

    IF NEW.origin_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.origin_id, 'work_item_origin') THEN
            RAISE EXCEPTION 'origin_id debe pertenecer al scheme "work_item_origin"';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_work_item_validate_schemes ON core.work_item;
CREATE TRIGGER trg_work_item_validate_schemes
    BEFORE INSERT OR UPDATE ON core.work_item
    FOR EACH ROW EXECUTE FUNCTION fn_validate_work_item_schemes();

-- Agreement: validar schemes
CREATE OR REPLACE FUNCTION fn_validate_agreement_schemes()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.agreement_type_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.agreement_type_id, 'agreement_type') THEN
            RAISE EXCEPTION 'agreement_type_id debe pertenecer al scheme "agreement_type"';
        END IF;
    END IF;

    IF NEW.state_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.state_id, 'agreement_state') THEN
            RAISE EXCEPTION 'state_id debe pertenecer al scheme "agreement_state"';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_agreement_validate_schemes ON core.agreement;
CREATE TRIGGER trg_agreement_validate_schemes
    BEFORE INSERT OR UPDATE ON core.agreement
    FOR EACH ROW EXECUTE FUNCTION fn_validate_agreement_schemes();

-- Operational Commitment: validar schemes
CREATE OR REPLACE FUNCTION fn_validate_commitment_schemes()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.state_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.state_id, 'commitment_state') THEN
            RAISE EXCEPTION 'state_id debe pertenecer al scheme "commitment_state"';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_commitment_validate_schemes ON core.operational_commitment;
CREATE TRIGGER trg_commitment_validate_schemes
    BEFORE INSERT OR UPDATE ON core.operational_commitment
    FOR EACH ROW EXECUTE FUNCTION fn_validate_commitment_schemes();

-- =============================================================================
-- P1-3: TRIGGER DE SINCRONIZACIÓN parent_code -> parent_id
-- =============================================================================
-- Hallazgo STR-001 / CAT-002: Mantener conmutatividad entre parent_code y parent_id

CREATE OR REPLACE FUNCTION fn_sync_category_parent()
RETURNS TRIGGER AS $$
BEGIN
    -- Si se especifica parent_code, resolver parent_id
    IF NEW.parent_code IS NOT NULL THEN
        SELECT id INTO NEW.parent_id
        FROM ref.category
        WHERE scheme = NEW.scheme
          AND code = NEW.parent_code;

        IF NEW.parent_id IS NULL THEN
            RAISE EXCEPTION 'parent_code "%" no encontrado en scheme "%"', NEW.parent_code, NEW.scheme;
        END IF;
    ELSE
        -- Si no hay parent_code, limpiar parent_id
        NEW.parent_id := NULL;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_sync_category_parent() IS
'STR-001 FIX: Mantiene parent_id sincronizado con parent_code en ref.category';

DROP TRIGGER IF EXISTS trg_category_sync_parent ON ref.category;
CREATE TRIGGER trg_category_sync_parent
    BEFORE INSERT OR UPDATE OF parent_code ON ref.category
    FOR EACH ROW EXECUTE FUNCTION fn_sync_category_parent();

-- =============================================================================
-- MEJORAS ADICIONALES (BEH-002): Capa defensiva para app.current_user_id
-- =============================================================================

-- Función mejorada para obtener usuario con validación
CREATE OR REPLACE FUNCTION get_current_user_safe()
RETURNS UUID AS $$
DECLARE
    v_user_id_text TEXT;
    v_user_id UUID;
BEGIN
    -- Obtener valor como texto
    v_user_id_text := current_setting('app.current_user_id', true);

    IF v_user_id_text IS NULL OR v_user_id_text = '' THEN
        RETURN NULL;
    END IF;

    -- Intentar convertir a UUID con manejo de error
    BEGIN
        v_user_id := v_user_id_text::UUID;
        RETURN v_user_id;
    EXCEPTION WHEN OTHERS THEN
        RAISE WARNING 'app.current_user_id contiene valor no-UUID: "%". Retornando NULL.', v_user_id_text;
        RETURN NULL;
    END;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_current_user_safe() IS
'BEH-002 FIX: Versión defensiva de get_current_user() con validación de formato UUID';

-- =============================================================================
-- MEJORAS ADICIONALES: CHECKs básicos (L-001, L-004)
-- =============================================================================

-- Prevenir auto-referencia en work_item
ALTER TABLE core.work_item
DROP CONSTRAINT IF EXISTS chk_work_item_no_self_parent,
ADD CONSTRAINT chk_work_item_no_self_parent
CHECK (parent_id IS NULL OR parent_id != id);

ALTER TABLE core.work_item
DROP CONSTRAINT IF EXISTS chk_work_item_no_self_block,
ADD CONSTRAINT chk_work_item_no_self_block
CHECK (blocked_by_item_id IS NULL OR blocked_by_item_id != id);

COMMENT ON CONSTRAINT chk_work_item_no_self_parent ON core.work_item IS
'CAT-008 FIX: Previene auto-referencia en parent_id';

COMMENT ON CONSTRAINT chk_work_item_no_self_block ON core.work_item IS
'CAT-008 FIX: Previene auto-referencia en blocked_by_item_id';

-- Validar tipo de metadata JSONB
ALTER TABLE ref.category
DROP CONSTRAINT IF EXISTS chk_category_metadata_object,
ADD CONSTRAINT chk_category_metadata_object
CHECK (metadata IS NULL OR jsonb_typeof(metadata) = 'object');

COMMENT ON CONSTRAINT chk_category_metadata_object ON ref.category IS
'STR-003 FIX: Garantiza que metadata sea objeto JSON, no array o primitivo';

-- =============================================================================
-- PRO-001: VALIDACIÓN DE ATRIBUTOS POR MECANISMO EN core.ipr_mechanism
-- =============================================================================
-- Hallazgo PRO-001 / Auditoría v5: Validar que atributos específicos de cada
-- mecanismo estén presentes según el mechanism_id de core.ipr
-- Coproducto controlado: SNI, C33, FRIL, GLOSA06, TRANSFER, SUBV8, FRPD

CREATE OR REPLACE FUNCTION fn_validate_mechanism_attrs()
RETURNS TRIGGER AS $$
DECLARE
    v_mechanism_code VARCHAR;
BEGIN
    -- Obtener código del mecanismo desde core.ipr
    SELECT c.code INTO v_mechanism_code
    FROM core.ipr i
    JOIN ref.category c ON i.mechanism_id = c.id
    WHERE i.id = NEW.ipr_id;

    IF v_mechanism_code IS NULL THEN
        RAISE EXCEPTION 'IPR % no tiene mechanism_id asignado', NEW.ipr_id;
    END IF;

    -- Validar atributos requeridos por mecanismo
    CASE v_mechanism_code
        WHEN 'SNI' THEN
            -- SNI requiere: rate_mdsf, etapa_bip
            IF NEW.rate_mdsf IS NULL THEN
                RAISE EXCEPTION 'Mecanismo SNI requiere rate_mdsf (RS, FI, FC, OT)';
            END IF;
            -- Validar valores permitidos de rate
            IF NEW.rate_mdsf NOT IN ('RS', 'FI', 'FC', 'OT') THEN
                RAISE EXCEPTION 'rate_mdsf debe ser RS, FI, FC u OT para SNI';
            END IF;

        WHEN 'C33' THEN
            -- C33 requiere: categoria_c33
            IF NEW.categoria_c33 IS NULL THEN
                RAISE EXCEPTION 'Mecanismo C33 requiere categoria_c33';
            END IF;

        WHEN 'FRIL' THEN
            -- FRIL requiere: tipo_fril, cumple_norma_5k_utm
            IF NEW.tipo_fril IS NULL THEN
                RAISE EXCEPTION 'Mecanismo FRIL requiere tipo_fril';
            END IF;
            IF NEW.cumple_norma_5k_utm IS NULL THEN
                RAISE EXCEPTION 'Mecanismo FRIL requiere cumple_norma_5k_utm';
            END IF;

        WHEN 'GLOSA06' THEN
            -- Glosa06 requiere: fase_eval_central
            IF NEW.fase_eval_central IS NULL THEN
                RAISE EXCEPTION 'Mecanismo GLOSA06 requiere fase_eval_central';
            END IF;

        WHEN 'TRANSFER' THEN
            -- Transfer: sin atributos obligatorios específicos
            NULL;

        WHEN 'SUBV8' THEN
            -- Subv8 requiere: puntaje_evaluacion
            IF NEW.puntaje_evaluacion IS NULL THEN
                RAISE EXCEPTION 'Mecanismo SUBV8 requiere puntaje_evaluacion';
            END IF;

        WHEN 'FRPD' THEN
            -- FRPD requiere: eje_fomento
            IF NEW.eje_fomento IS NULL THEN
                RAISE EXCEPTION 'Mecanismo FRPD requiere eje_fomento';
            END IF;

        ELSE
            RAISE EXCEPTION 'Mecanismo desconocido: %', v_mechanism_code;
    END CASE;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_validate_mechanism_attrs() IS
'PRO-001 FIX (Auditoría v5): Valida atributos requeridos según mecanismo de la IPR.
Garantiza coproducto disjunto (SNI, C33, FRIL, GLOSA06, TRANSFER, SUBV8, FRPD).';

DROP TRIGGER IF EXISTS trg_mechanism_validate_attrs ON core.ipr_mechanism;
CREATE TRIGGER trg_mechanism_validate_attrs
    BEFORE INSERT OR UPDATE ON core.ipr_mechanism
    FOR EACH ROW EXECUTE FUNCTION fn_validate_mechanism_attrs();

COMMENT ON TRIGGER trg_mechanism_validate_attrs ON core.ipr_mechanism IS
'PRO-001 FIX: Valida atributos específicos por mecanismo para garantizar coproducto controlado';

-- =============================================================================
-- PRO-002: CHECK DE COHERENCIA DE MONTOS EN agreement_installment
-- =============================================================================
-- Hallazgo PRO-002 / Auditoría v5: paid_amount <= amount

ALTER TABLE core.agreement_installment
DROP CONSTRAINT IF EXISTS chk_paid_lte_amount,
ADD CONSTRAINT chk_paid_lte_amount
CHECK (paid_amount IS NULL OR paid_amount <= amount);

COMMENT ON CONSTRAINT chk_paid_lte_amount ON core.agreement_installment IS
'PRO-002 FIX (Auditoría v5): Garantiza que el monto pagado no exceda el monto de la cuota';

-- =============================================================================
-- FIN TRIGGERS DE REMEDIACIÓN
-- =============================================================================
-- Triggers de transiciones: 7 (ipr, work_item, commitment, agreement, act, installment, file)
-- Triggers de validación scheme: 4 (ipr, work_item, agreement, commitment)
-- Triggers de sincronización: 1 (category parent)
-- Triggers de coproducto: 1 (mechanism_attrs) -- NUEVO v5
-- Funciones defensivas: 1 (get_current_user_safe)
-- Constraints CHECK: 4 (self-reference x2, metadata type, paid_amount) -- +1 v5
-- =============================================================================

DO $$ BEGIN RAISE NOTICE 'GORE_OS Triggers de Remediación Categorial v3.0 + v5 aplicados correctamente'; END $$;
