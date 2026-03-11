-- Wave B Migration: Coordinación Institucional, Escalamiento, Servicios, SLAs
-- 7 new tables, 8 new schemes

BEGIN;

-- Track migration
INSERT INTO core.schema_migration (filename)
VALUES ('goreos_migration_wave_b.sql')
ON CONFLICT (filename) DO NOTHING;

-- ══════════════ NEW SCHEMES ══════════════

-- 1. AR Decision Types
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_ar_decision_type', 'PRIORIDAD', 'Prioridad', 'Decisión de priorización', 1),
('dgi_ar_decision_type', 'RECURSO', 'Recurso', 'Asignación de recursos', 2),
('dgi_ar_decision_type', 'ESCALAMIENTO', 'Escalamiento', 'Decisión de escalamiento', 3),
('dgi_ar_decision_type', 'ESTRATEGIA', 'Estrategia', 'Decisión estratégica', 4)
ON CONFLICT DO NOTHING;

-- 2. AR Decision Status
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_ar_decision_status', 'PENDIENTE', 'Pendiente', 'Decisión pendiente de ejecución', 1),
('dgi_ar_decision_status', 'EN_EJECUCION', 'En Ejecución', 'Decisión en proceso de implementación', 2),
('dgi_ar_decision_status', 'COMPLETADA', 'Completada', 'Decisión completada', 3)
ON CONFLICT DO NOTHING;

-- 3. Escalation Levels
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_escalation_level', 'NIVEL_1', 'Nivel 1', 'Jefe DGI — resolución en 4h', 1),
('dgi_escalation_level', 'NIVEL_2', 'Nivel 2', 'Administrador Regional — resolución en 24h', 2),
('dgi_escalation_level', 'NIVEL_3', 'Nivel 3', 'Administrador Regional + Mesa — resolución en 48h', 3),
('dgi_escalation_level', 'NIVEL_4', 'Nivel 4', 'Gobernador — según urgencia', 4)
ON CONFLICT DO NOTHING;

-- 4. Escalation Status
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_escalation_status', 'ABIERTO', 'Abierto', 'Escalamiento registrado', 1),
('dgi_escalation_status', 'EN_GESTION', 'En Gestión', 'Escalamiento siendo gestionado', 2),
('dgi_escalation_status', 'RESUELTO', 'Resuelto', 'Escalamiento resuelto', 3),
('dgi_escalation_status', 'CERRADO', 'Cerrado', 'Escalamiento cerrado', 4)
ON CONFLICT DO NOTHING;

-- 5. Service Status
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_service_status', 'ACTIVO', 'Activo', 'Servicio disponible', 1),
('dgi_service_status', 'SUSPENDIDO', 'Suspendido', 'Servicio temporalmente suspendido', 2),
('dgi_service_status', 'DESCONTINUADO', 'Descontinuado', 'Servicio descontinuado', 3)
ON CONFLICT DO NOTHING;

-- 6. Request Status
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_request_status', 'RECIBIDA', 'Recibida', 'Solicitud recibida', 1),
('dgi_request_status', 'EN_EVALUACION', 'En Evaluación', 'Solicitud siendo evaluada', 2),
('dgi_request_status', 'ACEPTADA', 'Aceptada', 'Solicitud aceptada', 3),
('dgi_request_status', 'EN_EJECUCION', 'En Ejecución', 'Solicitud en ejecución', 4),
('dgi_request_status', 'COMPLETADA', 'Completada', 'Solicitud completada', 5),
('dgi_request_status', 'RECHAZADA', 'Rechazada', 'Solicitud rechazada', 6)
ON CONFLICT DO NOTHING;

-- 7. Interaction Types
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_interaction_type', 'PRESUPUESTO', 'Presupuesto', 'Interacción sobre temas presupuestarios', 1),
('dgi_interaction_type', 'CARTERA', 'Cartera', 'Interacción sobre cartera de proyectos', 2),
('dgi_interaction_type', 'JURIDICO', 'Jurídico', 'Interacción sobre temas jurídicos', 3),
('dgi_interaction_type', 'TECNOLOGIA', 'Tecnología', 'Interacción sobre temas tecnológicos', 4),
('dgi_interaction_type', 'PROCESO', 'Proceso', 'Interacción sobre procesos', 5),
('dgi_interaction_type', 'GENERAL', 'General', 'Interacción general', 6)
ON CONFLICT DO NOTHING;

-- 8. SLA Product Types
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_sla_product_type', 'INFORME_FLASH', 'Informe Flash', 'Informe flash de contingencia', 1),
('dgi_sla_product_type', 'INFORME_SEMANAL', 'Informe Semanal', 'Informe semanal de gestión', 2),
('dgi_sla_product_type', 'INFORME_MENSUAL', 'Informe Mensual', 'Informe mensual de gestión', 3),
('dgi_sla_product_type', 'LEVANTAMIENTO_PROCESO', 'Levantamiento de Proceso', 'Levantamiento y modelado de proceso', 4),
('dgi_sla_product_type', 'ANALISIS_INDICADOR', 'Análisis de Indicador', 'Análisis de indicador de gestión', 5),
('dgi_sla_product_type', 'EVALUACION_CARTERA', 'Evaluación de Cartera', 'Evaluación de cartera IPR', 6),
('dgi_sla_product_type', 'SOPORTE_TD', 'Soporte TD', 'Soporte en transformación digital', 7)
ON CONFLICT DO NOTHING;

-- ══════════════ TABLES ══════════════

-- Cadena 1: AR Coordination
CREATE TABLE IF NOT EXISTS core.dgi_ar_decision (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    description TEXT NOT NULL,
    decision_type_id UUID NOT NULL REFERENCES ref.category(id),
    status_id UUID NOT NULL REFERENCES ref.category(id),
    due_date DATE,
    context TEXT,
    responsible_id UUID REFERENCES core."user"(id),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by_id UUID REFERENCES core."user"(id),
    deleted_at TIMESTAMPTZ,
    CONSTRAINT chk_ar_decision_type CHECK (fn_validate_category_scheme(decision_type_id, 'dgi_ar_decision_type')),
    CONSTRAINT chk_ar_decision_status CHECK (fn_validate_category_scheme(status_id, 'dgi_ar_decision_status'))
);

-- Cadena 2: Escalation Protocol
CREATE TABLE IF NOT EXISTS core.dgi_escalation (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    level_id UUID NOT NULL REFERENCES ref.category(id),
    status_id UUID NOT NULL REFERENCES ref.category(id),
    situation TEXT NOT NULL,
    impact TEXT NOT NULL,
    options JSONB DEFAULT '[]',
    recommendation TEXT,
    deadline TIMESTAMPTZ,
    subject_type VARCHAR(64),
    subject_id UUID,
    escalated_to VARCHAR(32),
    resolved_description TEXT,
    alert_id UUID REFERENCES core.alert(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by_id UUID REFERENCES core."user"(id),
    resolved_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ,
    CONSTRAINT chk_escalation_level CHECK (fn_validate_category_scheme(level_id, 'dgi_escalation_level')),
    CONSTRAINT chk_escalation_status CHECK (fn_validate_category_scheme(status_id, 'dgi_escalation_status'))
);

-- Cadena 3: Service Catalog
CREATE TABLE IF NOT EXISTS core.dgi_service (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    area VARCHAR(4) NOT NULL,
    status_id UUID NOT NULL REFERENCES ref.category(id),
    sla_days INTEGER,
    how_to_request TEXT,
    deliverables TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by_id UUID REFERENCES core."user"(id),
    deleted_at TIMESTAMPTZ,
    CONSTRAINT chk_service_status CHECK (fn_validate_category_scheme(status_id, 'dgi_service_status'))
);

CREATE TABLE IF NOT EXISTS core.dgi_service_request (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    service_id UUID NOT NULL REFERENCES core.dgi_service(id),
    status_id UUID NOT NULL REFERENCES ref.category(id),
    requester_id UUID NOT NULL REFERENCES core."user"(id),
    division_id UUID REFERENCES core.organization(id),
    description TEXT NOT NULL,
    urgency VARCHAR(8) DEFAULT 'NORMAL',
    assigned_to_id UUID REFERENCES core."user"(id),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    satisfaction_score INTEGER,
    feedback_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by_id UUID REFERENCES core."user"(id),
    deleted_at TIMESTAMPTZ,
    CONSTRAINT chk_request_status CHECK (fn_validate_category_scheme(status_id, 'dgi_request_status')),
    CONSTRAINT chk_satisfaction_range CHECK (satisfaction_score IS NULL OR satisfaction_score BETWEEN 1 AND 5)
);

-- Cadena 3b: SLA Definitions
CREATE TABLE IF NOT EXISTS core.dgi_sla (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    service_id UUID NOT NULL REFERENCES core.dgi_service(id),
    product_type_id UUID NOT NULL REFERENCES ref.category(id),
    description TEXT,
    target_days INTEGER NOT NULL,
    target_hour TIME,
    priority INTEGER DEFAULT 0,
    applies_to JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    CONSTRAINT chk_sla_product_type CHECK (fn_validate_category_scheme(product_type_id, 'dgi_sla_product_type')),
    CONSTRAINT chk_target_days_positive CHECK (target_days > 0),
    UNIQUE(service_id, product_type_id)
);

-- Cadena 4: Division Interactions
CREATE TABLE IF NOT EXISTS core.dgi_division_interaction (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    division_id UUID NOT NULL REFERENCES core.organization(id),
    interaction_type_id UUID NOT NULL REFERENCES ref.category(id),
    interaction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    participants JSONB DEFAULT '[]',
    topics JSONB DEFAULT '[]',
    agreements JSONB DEFAULT '[]',
    next_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by_id UUID REFERENCES core."user"(id),
    deleted_at TIMESTAMPTZ,
    CONSTRAINT chk_interaction_type CHECK (fn_validate_category_scheme(interaction_type_id, 'dgi_interaction_type'))
);

-- ══════════════ FSM TRIGGERS ══════════════

-- Escalation FSM: ABIERTO → EN_GESTION → RESUELTO → CERRADO
INSERT INTO ref.category (scheme, code, label, sort_order)
SELECT 'dgi_escalation_status', code, label, sort_order
FROM (VALUES
    ('ABIERTO', 'Abierto', 1),
    ('EN_GESTION', 'En Gestión', 2),
    ('RESUELTO', 'Resuelto', 3),
    ('CERRADO', 'Cerrado', 4)
) AS v(code, label, sort_order)
WHERE NOT EXISTS (
    SELECT 1 FROM ref.category WHERE scheme = 'dgi_escalation_status' AND code = v.code
);

-- Valid transitions for escalation status
UPDATE ref.category SET valid_transitions = '["EN_GESTION", "CERRADO"]'
WHERE scheme = 'dgi_escalation_status' AND code = 'ABIERTO';
UPDATE ref.category SET valid_transitions = '["RESUELTO", "CERRADO"]'
WHERE scheme = 'dgi_escalation_status' AND code = 'EN_GESTION';
UPDATE ref.category SET valid_transitions = '["CERRADO"]'
WHERE scheme = 'dgi_escalation_status' AND code = 'RESUELTO';
UPDATE ref.category SET valid_transitions = '[]'
WHERE scheme = 'dgi_escalation_status' AND code = 'CERRADO';

-- Request FSM: RECIBIDA → EN_EVALUACION → ACEPTADA → EN_EJECUCION → COMPLETADA|RECHAZADA
UPDATE ref.category SET valid_transitions = '["EN_EVALUACION", "RECHAZADA"]'
WHERE scheme = 'dgi_request_status' AND code = 'RECIBIDA';
UPDATE ref.category SET valid_transitions = '["ACEPTADA", "RECHAZADA"]'
WHERE scheme = 'dgi_request_status' AND code = 'EN_EVALUACION';
UPDATE ref.category SET valid_transitions = '["EN_EJECUCION"]'
WHERE scheme = 'dgi_request_status' AND code = 'ACEPTADA';
UPDATE ref.category SET valid_transitions = '["COMPLETADA"]'
WHERE scheme = 'dgi_request_status' AND code = 'EN_EJECUCION';
UPDATE ref.category SET valid_transitions = '[]'
WHERE scheme = 'dgi_request_status' AND code = 'COMPLETADA';
UPDATE ref.category SET valid_transitions = '[]'
WHERE scheme = 'dgi_request_status' AND code = 'RECHAZADA';

-- AR Decision FSM
UPDATE ref.category SET valid_transitions = '["EN_EJECUCION"]'
WHERE scheme = 'dgi_ar_decision_status' AND code = 'PENDIENTE';
UPDATE ref.category SET valid_transitions = '["COMPLETADA"]'
WHERE scheme = 'dgi_ar_decision_status' AND code = 'EN_EJECUCION';
UPDATE ref.category SET valid_transitions = '[]'
WHERE scheme = 'dgi_ar_decision_status' AND code = 'COMPLETADA';

-- Escalation state transition trigger
CREATE OR REPLACE FUNCTION core.trg_escalation_state_transition_fn()
RETURNS TRIGGER AS $$
DECLARE
    old_code TEXT;
    new_code TEXT;
    allowed JSONB;
BEGIN
    IF NEW.status_id IS DISTINCT FROM OLD.status_id THEN
        SELECT code, COALESCE(valid_transitions, '[]'::jsonb)
        INTO old_code, allowed
        FROM ref.category WHERE id = OLD.status_id AND scheme = 'dgi_escalation_status';

        SELECT code INTO new_code
        FROM ref.category WHERE id = NEW.status_id AND scheme = 'dgi_escalation_status';

        IF NOT allowed ? new_code THEN
            RAISE EXCEPTION 'Transición inválida de escalamiento: % → %', old_code, new_code;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_escalation_state_transition ON core.dgi_escalation;
CREATE TRIGGER trg_escalation_state_transition
    BEFORE UPDATE ON core.dgi_escalation
    FOR EACH ROW
    EXECUTE FUNCTION core.trg_escalation_state_transition_fn();

-- Request state transition trigger
CREATE OR REPLACE FUNCTION core.trg_request_state_transition_fn()
RETURNS TRIGGER AS $$
DECLARE
    old_code TEXT;
    new_code TEXT;
    allowed JSONB;
BEGIN
    IF NEW.status_id IS DISTINCT FROM OLD.status_id THEN
        SELECT code, COALESCE(valid_transitions, '[]'::jsonb)
        INTO old_code, allowed
        FROM ref.category WHERE id = OLD.status_id AND scheme = 'dgi_request_status';

        SELECT code INTO new_code
        FROM ref.category WHERE id = NEW.status_id AND scheme = 'dgi_request_status';

        IF NOT allowed ? new_code THEN
            RAISE EXCEPTION 'Transición inválida de solicitud: % → %', old_code, new_code;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_request_state_transition ON core.dgi_service_request;
CREATE TRIGGER trg_request_state_transition
    BEFORE UPDATE ON core.dgi_service_request
    FOR EACH ROW
    EXECUTE FUNCTION core.trg_request_state_transition_fn();

-- Request timing trigger: auto-set started_at / completed_at
CREATE OR REPLACE FUNCTION core.trg_request_timing_fn()
RETURNS TRIGGER AS $$
DECLARE
    new_code TEXT;
BEGIN
    IF NEW.status_id IS DISTINCT FROM OLD.status_id THEN
        SELECT code INTO new_code
        FROM ref.category WHERE id = NEW.status_id AND scheme = 'dgi_request_status';

        IF new_code = 'EN_EJECUCION' AND OLD.started_at IS NULL THEN
            NEW.started_at := NOW();
        END IF;

        IF new_code = 'COMPLETADA' THEN
            NEW.completed_at := NOW();
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_request_timing ON core.dgi_service_request;
CREATE TRIGGER trg_request_timing
    BEFORE UPDATE ON core.dgi_service_request
    FOR EACH ROW
    EXECUTE FUNCTION core.trg_request_timing_fn();

-- AR Decision state transition trigger
CREATE OR REPLACE FUNCTION core.trg_ar_decision_state_transition_fn()
RETURNS TRIGGER AS $$
DECLARE
    old_code TEXT;
    new_code TEXT;
    allowed JSONB;
BEGIN
    IF NEW.status_id IS DISTINCT FROM OLD.status_id THEN
        SELECT code, COALESCE(valid_transitions, '[]'::jsonb)
        INTO old_code, allowed
        FROM ref.category WHERE id = OLD.status_id AND scheme = 'dgi_ar_decision_status';

        SELECT code INTO new_code
        FROM ref.category WHERE id = NEW.status_id AND scheme = 'dgi_ar_decision_status';

        IF NOT allowed ? new_code THEN
            RAISE EXCEPTION 'Transición inválida de decisión AR: % → %', old_code, new_code;
        END IF;

        -- Auto-set resolved_at on COMPLETADA
        IF new_code = 'COMPLETADA' THEN
            NEW.resolved_at := NOW();
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ar_decision_state_transition ON core.dgi_ar_decision;
CREATE TRIGGER trg_ar_decision_state_transition
    BEFORE UPDATE ON core.dgi_ar_decision
    FOR EACH ROW
    EXECUTE FUNCTION core.trg_ar_decision_state_transition_fn();

COMMIT;
