-- =============================================================================
-- GORE_OS v3.0 - TRIGGERS Y FUNCIONES
-- =============================================================================
-- Archivo: goreos_triggers.sql
-- Descripción: Triggers de auditoría, soft delete y event sourcing
-- Generado: 2026-01-26
-- Dependencias: goreos_ddl_v3.sql (debe ejecutarse primero)
-- =============================================================================

-- =============================================================================
-- FUNCIÓN: Auditoría automática a txn.event
-- CRIT-005 FIX: actor_id ahora es consistente con core.user (no ref.actor)
-- app.current_user_id contiene UUID de core.user, compatible con txn.event.actor_id
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_audit_to_event()
RETURNS TRIGGER AS $$
DECLARE
    v_event_type_id UUID;
    v_user_id UUID;
    v_data JSONB;
BEGIN
    -- Obtener event_type según la operación
    SELECT id INTO v_event_type_id
    FROM ref.category
    WHERE scheme = 'event_type' AND code = 'STATE_TRANSITION';

    -- Determinar el usuario actor (del contexto de sesión si existe)
    -- CRIT-005: app.current_user_id es UUID de core.user, consistente con txn.event.actor_id
    v_user_id := current_setting('app.current_user_id', true)::UUID;

    -- Construir datos del evento
    v_data := jsonb_build_object(
        'table', TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
        'operation', TG_OP
    );

    IF TG_OP = 'UPDATE' THEN
        v_data := v_data || jsonb_build_object(
            'old', to_jsonb(OLD),
            'new', to_jsonb(NEW)
        );
    ELSIF TG_OP = 'INSERT' THEN
        v_data := v_data || jsonb_build_object('new', to_jsonb(NEW));
    ELSIF TG_OP = 'DELETE' THEN
        v_data := v_data || jsonb_build_object('old', to_jsonb(OLD));
    END IF;

    -- Insertar evento (solo si hay event_type)
    IF v_event_type_id IS NOT NULL THEN
        INSERT INTO txn.event (event_type_id, subject_type, subject_id, actor_id, data, created_by_id)
        VALUES (
            v_event_type_id,
            TG_TABLE_NAME,
            COALESCE(NEW.id, OLD.id),
            v_user_id,
            v_data,
            v_user_id
        );
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_audit_to_event() IS
'Registra cambios en txn.event para tablas críticas (event sourcing)';

-- =============================================================================
-- FUNCIÓN: Soft Delete
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_soft_delete()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id UUID;
BEGIN
    -- Obtener usuario del contexto
    v_user_id := current_setting('app.current_user_id', true)::UUID;

    -- En lugar de DELETE, marcamos como eliminado
    EXECUTE format('
        UPDATE %I.%I
        SET deleted_at = now(),
            deleted_by_id = $1,
            updated_at = now(),
            updated_by_id = $1
        WHERE id = $2
    ', TG_TABLE_SCHEMA, TG_TABLE_NAME)
    USING v_user_id, OLD.id;

    -- Retornar NULL cancela el DELETE original
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_soft_delete() IS
'Convierte DELETE en soft delete (marca deleted_at en lugar de eliminar)';

-- =============================================================================
-- FUNCIÓN: Validar transiciones de estado
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_validate_state_transition()
RETURNS TRIGGER AS $$
DECLARE
    v_valid_transitions JSONB;
    v_old_code VARCHAR(32);
    v_new_code VARCHAR(32);
BEGIN
    -- Obtener código del estado anterior
    SELECT code INTO v_old_code
    FROM ref.category WHERE id = OLD.status_id;

    -- Obtener código del nuevo estado
    SELECT code INTO v_new_code
    FROM ref.category WHERE id = NEW.status_id;

    -- Obtener transiciones válidas del estado anterior
    SELECT valid_transitions INTO v_valid_transitions
    FROM ref.category WHERE id = OLD.status_id;

    -- Si hay transiciones definidas, validar
    IF v_valid_transitions IS NOT NULL AND v_valid_transitions != '[]'::jsonb THEN
        IF NOT v_valid_transitions ? v_new_code THEN
            RAISE EXCEPTION 'Transición de estado inválida: % -> %. Transiciones válidas: %',
                v_old_code, v_new_code, v_valid_transitions;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_validate_state_transition() IS
'Valida que las transiciones de estado estén en valid_transitions';

-- =============================================================================
-- FUNCIÓN: Registrar historial de work_item
-- CRIT-003 FIX: Evitar uso de OLD en INSERT (OLD no existe en INSERT)
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_work_item_history()
RETURNS TRIGGER AS $$
DECLARE
    v_event_type_id UUID;
    v_event_code VARCHAR(32);
    v_previous_status_id UUID;
    v_previous_assignee_id UUID;
BEGIN
    -- Determinar tipo de evento
    IF TG_OP = 'INSERT' THEN
        v_event_code := 'CREATED';
        -- En INSERT, OLD no existe, usar NULL para valores previos
        v_previous_status_id := NULL;
        v_previous_assignee_id := NULL;
    ELSE
        -- En UPDATE, OLD existe y podemos usarlo
        v_previous_status_id := OLD.status_id;
        v_previous_assignee_id := OLD.assignee_id;

        IF OLD.status_id IS DISTINCT FROM NEW.status_id THEN
            v_event_code := 'STATUS_CHANGE';
        ELSIF OLD.assignee_id IS DISTINCT FROM NEW.assignee_id THEN
            v_event_code := 'REASSIGNED';
        ELSIF OLD.blocked_by_item_id IS NULL AND NEW.blocked_by_item_id IS NOT NULL THEN
            v_event_code := 'BLOCKED';
        ELSIF OLD.blocked_by_item_id IS NOT NULL AND NEW.blocked_by_item_id IS NULL THEN
            v_event_code := 'UNBLOCKED';
        ELSIF NEW.verified_at IS NOT NULL AND OLD.verified_at IS NULL THEN
            v_event_code := 'VERIFIED';
        ELSE
            -- No registrar si no hay cambio significativo
            RETURN NEW;
        END IF;
    END IF;

    -- Obtener ID del tipo de evento
    SELECT id INTO v_event_type_id
    FROM ref.category
    WHERE scheme = 'work_item_event' AND code = v_event_code;

    IF v_event_type_id IS NOT NULL THEN
        INSERT INTO core.work_item_history (
            work_item_id,
            event_type_id,
            previous_status_id,
            new_status_id,
            previous_assignee_id,
            new_assignee_id,
            performed_by_id
        ) VALUES (
            NEW.id,
            v_event_type_id,
            v_previous_status_id,
            NEW.status_id,
            v_previous_assignee_id,
            NEW.assignee_id,
            COALESCE(NEW.updated_by_id, NEW.created_by_id)
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_work_item_history() IS
'Registra cambios de work_item en work_item_history';

-- =============================================================================
-- FUNCIÓN: Registrar historial de commitment
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_commitment_history()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.state_id IS DISTINCT FROM NEW.state_id THEN
        INSERT INTO core.commitment_history (
            commitment_id,
            previous_state_id,
            new_state_id,
            changed_by_id
        ) VALUES (
            NEW.id,
            OLD.state_id,
            NEW.state_id,
            COALESCE(NEW.updated_by_id, NEW.created_by_id)
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_commitment_history() IS
'Registra cambios de estado en commitment_history';

-- =============================================================================
-- FUNCIÓN: Actualizar has_open_problems en IPR
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_update_ipr_problems_flag()
RETURNS TRIGGER AS $$
BEGIN
    -- Actualizar flag en IPR relacionada
    IF TG_OP = 'DELETE' THEN
        UPDATE core.ipr SET
            has_open_problems = EXISTS (
                SELECT 1 FROM core.ipr_problem
                WHERE ipr_id = OLD.ipr_id
                AND resolved_at IS NULL
                AND deleted_at IS NULL
            ),
            updated_at = now()
        WHERE id = OLD.ipr_id;
        RETURN OLD;
    ELSE
        UPDATE core.ipr SET
            has_open_problems = EXISTS (
                SELECT 1 FROM core.ipr_problem
                WHERE ipr_id = NEW.ipr_id
                AND resolved_at IS NULL
                AND deleted_at IS NULL
            ),
            updated_at = now()
        WHERE id = NEW.ipr_id;
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_update_ipr_problems_flag() IS
'Mantiene actualizado has_open_problems en core.ipr';

-- =============================================================================
-- FUNCIÓN: Generar código automático
-- HIGH-007 FIX: Ahora thread-safe usando advisory lock
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_generate_code(
    p_prefix VARCHAR(10),
    p_table_name VARCHAR(64)
) RETURNS VARCHAR(20) AS $$
DECLARE
    v_year INTEGER;
    v_seq INTEGER;
    v_lock_key BIGINT;
BEGIN
    v_year := EXTRACT(YEAR FROM CURRENT_DATE);

    -- HIGH-007 FIX: Generar clave única de lock basada en prefix, tabla y año
    -- hashtext retorna un entero que usamos como lock key
    v_lock_key := hashtext(p_prefix || '|' || p_table_name || '|' || v_year::TEXT);

    -- Adquirir advisory lock de transacción (se libera automáticamente al commit/rollback)
    PERFORM pg_advisory_xact_lock(v_lock_key);

    -- Obtener siguiente secuencia (ahora protegido por lock)
    EXECUTE format('
        SELECT COALESCE(MAX(CAST(SUBSTRING(code FROM ''[0-9]+$'') AS INTEGER)), 0) + 1
        FROM %I
        WHERE code LIKE $1
    ', p_table_name)
    INTO v_seq
    USING p_prefix || '-' || v_year || '-%';

    RETURN p_prefix || '-' || v_year || '-' || LPAD(v_seq::TEXT, 5, '0');
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_generate_code(VARCHAR, VARCHAR) IS
'Genera código secuencial thread-safe: PREFIX-YYYY-NNNNN (usa advisory lock)';

-- =============================================================================
-- FUNCIÓN: Inicializar y mantener current_amount en budget_program
-- MED-003 FIX: Campo calculado sin trigger de mantenimiento
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_budget_program_current_amount()
RETURNS TRIGGER AS $$
BEGIN
    -- En INSERT: inicializar current_amount = initial_amount si no se especifica
    IF TG_OP = 'INSERT' THEN
        IF NEW.current_amount IS NULL THEN
            NEW.current_amount := NEW.initial_amount;
        END IF;
    END IF;

    -- En UPDATE: si cambia initial_amount y current_amount no fue modificado explícitamente,
    -- ajustar current_amount proporcionalmente
    IF TG_OP = 'UPDATE' THEN
        IF OLD.initial_amount IS DISTINCT FROM NEW.initial_amount THEN
            -- Si current_amount no cambió en este UPDATE, ajustarlo
            IF OLD.current_amount IS NOT DISTINCT FROM NEW.current_amount THEN
                NEW.current_amount := NEW.current_amount + (NEW.initial_amount - OLD.initial_amount);
            END IF;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_budget_program_current_amount() IS
'Mantiene current_amount sincronizado con initial_amount. Modificaciones adicionales via txn.magnitude.';

-- =============================================================================
-- CREAR TRIGGERS
-- =============================================================================

-- Trigger para historial de work_item
DROP TRIGGER IF EXISTS trg_work_item_history ON core.work_item;
CREATE TRIGGER trg_work_item_history
    AFTER INSERT OR UPDATE ON core.work_item
    FOR EACH ROW EXECUTE FUNCTION fn_work_item_history();

-- Trigger para historial de commitment
DROP TRIGGER IF EXISTS trg_commitment_history ON core.operational_commitment;
CREATE TRIGGER trg_commitment_history
    AFTER UPDATE ON core.operational_commitment
    FOR EACH ROW EXECUTE FUNCTION fn_commitment_history();

-- Trigger para actualizar has_open_problems en IPR
DROP TRIGGER IF EXISTS trg_ipr_problem_flag ON core.ipr_problem;
CREATE TRIGGER trg_ipr_problem_flag
    AFTER INSERT OR UPDATE OR DELETE ON core.ipr_problem
    FOR EACH ROW EXECUTE FUNCTION fn_update_ipr_problems_flag();

-- MED-003 FIX: Trigger para mantener current_amount en budget_program
DROP TRIGGER IF EXISTS trg_budget_program_current ON core.budget_program;
CREATE TRIGGER trg_budget_program_current
    BEFORE INSERT OR UPDATE ON core.budget_program
    FOR EACH ROW EXECUTE FUNCTION fn_budget_program_current_amount();

-- =============================================================================
-- TRIGGERS DE AUDITORÍA A EVENT (OPCIONAL - Descomentar si se necesita)
-- =============================================================================

/*
-- Auditoría de IPR a txn.event
CREATE TRIGGER trg_ipr_audit
    AFTER INSERT OR UPDATE ON core.ipr
    FOR EACH ROW EXECUTE FUNCTION fn_audit_to_event();

-- Auditoría de Agreement a txn.event
CREATE TRIGGER trg_agreement_audit
    AFTER INSERT OR UPDATE ON core.agreement
    FOR EACH ROW EXECUTE FUNCTION fn_audit_to_event();

-- Auditoría de Budget Commitment a txn.event
CREATE TRIGGER trg_budget_commitment_audit
    AFTER INSERT OR UPDATE ON core.budget_commitment
    FOR EACH ROW EXECUTE FUNCTION fn_audit_to_event();
*/

-- =============================================================================
-- TRIGGERS DE SOFT DELETE (OPCIONAL - Descomentar si se necesita)
-- CRIT-004 FIX: INSTEAD OF solo funciona en VIEWs, usar BEFORE DELETE en tablas
-- =============================================================================

/*
-- Soft delete para IPR (usar BEFORE DELETE, no INSTEAD OF)
CREATE TRIGGER trg_ipr_soft_delete
    BEFORE DELETE ON core.ipr
    FOR EACH ROW EXECUTE FUNCTION fn_soft_delete();

-- Soft delete para Agreement (usar BEFORE DELETE, no INSTEAD OF)
CREATE TRIGGER trg_agreement_soft_delete
    BEFORE DELETE ON core.agreement
    FOR EACH ROW EXECUTE FUNCTION fn_soft_delete();
*/

-- =============================================================================
-- HELPERS DE SESIÓN
-- =============================================================================

-- Función para establecer usuario actual (llamar desde aplicación)
CREATE OR REPLACE FUNCTION set_current_user(p_user_id UUID)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_user_id', p_user_id::TEXT, false);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION set_current_user(UUID) IS
'Establece el usuario actual para auditoría. Llamar al inicio de cada request.';

-- Función para obtener usuario actual
CREATE OR REPLACE FUNCTION get_current_user()
RETURNS UUID AS $$
BEGIN
    RETURN current_setting('app.current_user_id', true)::UUID;
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_current_user() IS
'Obtiene el usuario actual del contexto de sesión';

-- =============================================================================
-- FIN TRIGGERS
-- =============================================================================
-- Funciones: 8
-- Triggers activos: 3 (work_item_history, commitment_history, ipr_problem_flag)
-- Triggers opcionales: 5 (audit, soft_delete)
-- =============================================================================

DO $$ BEGIN RAISE NOTICE 'GORE_OS Triggers v3.0 cargados correctamente'; END $$;
