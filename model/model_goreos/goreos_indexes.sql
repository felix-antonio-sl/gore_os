-- =============================================================================
-- GORE_OS v3.0 - INDEXES
-- =============================================================================
-- Archivo: goreos_indexes_v3.sql
-- Descripción: Índices optimizados para el modelo v3 con UUID y particionamiento
-- Generado: 2026-01-26
-- Dependencias: goreos_ddl_v3.sql
-- =============================================================================
-- Principios de Indexación:
-- 1. Índices compuestos para queries frecuentes (CQs del dominio)
-- 2. Índices parciales para registros activos (WHERE deleted_at IS NULL)
-- 3. Índices GIN para búsquedas JSONB y arrays
-- 4. Índices en particiones heredan de la tabla padre
-- =============================================================================

-- =============================================================================
--    SCHEMA: meta - ÍNDICES ATOMOS FUNDAMENTALES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_role_agent_type ON meta.role(agent_type);
CREATE INDEX IF NOT EXISTS idx_role_active ON meta.role(id) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_process_layer ON meta.process(layer);
CREATE INDEX IF NOT EXISTS idx_process_active ON meta.process(id) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_entity_domain ON meta.entity(domain);
CREATE INDEX IF NOT EXISTS idx_entity_active ON meta.entity(id) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_story_domain ON meta.story(domain);
CREATE INDEX IF NOT EXISTS idx_story_role ON meta.story(role_id);
CREATE INDEX IF NOT EXISTS idx_story_process ON meta.story(process_id);
CREATE INDEX IF NOT EXISTS idx_story_status ON meta.story(status);
CREATE INDEX IF NOT EXISTS idx_story_active ON meta.story(id) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_story_entity_story ON meta.story_entity(story_id);
CREATE INDEX IF NOT EXISTS idx_story_entity_entity ON meta.story_entity(entity_id);

-- =============================================================================
--    SCHEMA: ref - ÍNDICES DATOS DE REFERENCIA
-- =============================================================================

-- ref.category: Ya tiene índices en DDL
-- Índices adicionales para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_category_parent ON ref.category(parent_id) WHERE parent_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_category_active ON ref.category(id) WHERE deleted_at IS NULL;

-- ref.actor: Índices para tipos de actor
CREATE INDEX IF NOT EXISTS idx_actor_code ON ref.actor(code);
CREATE INDEX IF NOT EXISTS idx_actor_internal ON ref.actor(is_internal);
CREATE INDEX IF NOT EXISTS idx_actor_active ON ref.actor(id) WHERE deleted_at IS NULL;

-- =============================================================================
--    SCHEMA: core - ÍNDICES IPR (Iniciativas de Inversión)
-- =============================================================================

-- CQ: "¿Cuáles son las IPR en fase F4 del mecanismo FRIL?"
CREATE INDEX IF NOT EXISTS idx_ipr_phase_mechanism ON core.ipr(mcd_phase_id, mechanism_id);

-- CQ: "¿Qué IPR tienen estado 'EN_EJECUCION'?"
-- Ya existe idx_ipr_status en DDL

-- CQ: "¿Cuál es el avance financiero de IPRs por año?"
CREATE INDEX IF NOT EXISTS idx_ipr_year ON core.ipr(EXTRACT(YEAR FROM created_at));

-- CQ: "¿Qué IPR están asignadas al usuario X?"
CREATE INDEX IF NOT EXISTS idx_ipr_assignee ON core.ipr(assignee_id) WHERE assignee_id IS NOT NULL;

-- CQ: "¿Qué IPR tienen problemas abiertos?"
CREATE INDEX IF NOT EXISTS idx_ipr_problems ON core.ipr(has_open_problems) WHERE has_open_problems = TRUE;

-- CQ: "¿Qué IPR tienen nivel de alerta CRITICO?"
CREATE INDEX IF NOT EXISTS idx_ipr_alert ON core.ipr(alert_level_id) WHERE alert_level_id IS NOT NULL;

-- Índice para búsqueda por código BIP
CREATE UNIQUE INDEX IF NOT EXISTS idx_ipr_bip ON core.ipr(codigo_bip);

-- Índice para IPRs activas
CREATE INDEX IF NOT EXISTS idx_ipr_active ON core.ipr(id) WHERE deleted_at IS NULL;

-- =============================================================================
--    SCHEMA: core - ÍNDICES CONVENIOS
-- =============================================================================

-- CQ: "¿Qué convenios vencen en los próximos 30 días?"
CREATE INDEX IF NOT EXISTS idx_agreement_valid_to ON core.agreement(valid_to) WHERE valid_to IS NOT NULL;

-- CQ: "¿Qué convenios tiene la entidad dadora/receptora X?"
CREATE INDEX IF NOT EXISTS idx_agreement_giver ON core.agreement(giver_id);
CREATE INDEX IF NOT EXISTS idx_agreement_receiver ON core.agreement(receiver_id);

-- CQ: "¿Qué convenios están vinculados a la IPR X?"
-- Ya existe idx_agreement_ipr en DDL

-- Índice para convenios activos
CREATE INDEX IF NOT EXISTS idx_agreement_active ON core.agreement(id) WHERE deleted_at IS NULL;

-- CQ: "¿Qué cuotas de convenio están vencidas?"
CREATE INDEX IF NOT EXISTS idx_installment_due ON core.agreement_installment(due_date, payment_status_id);
CREATE INDEX IF NOT EXISTS idx_installment_agreement ON core.agreement_installment(agreement_id);

-- =============================================================================
--    SCHEMA: core - ÍNDICES WORK ITEMS
-- =============================================================================

-- CQ: "¿Qué ítems de trabajo tiene asignados el usuario X?"
-- Ya existe idx_work_item_assignee en DDL

-- CQ: "¿Qué ítems de trabajo están vencidos?"
CREATE INDEX IF NOT EXISTS idx_workitem_due_active ON core.work_item(due_date)
    WHERE due_date IS NOT NULL AND deleted_at IS NULL;

-- CQ: "¿Qué ítems están bloqueados?"
CREATE INDEX IF NOT EXISTS idx_workitem_blocked ON core.work_item(updated_at)
    WHERE blocked_by_item_id IS NOT NULL;

-- CQ: "¿Qué ítems tiene la división X pendientes?"
CREATE INDEX IF NOT EXISTS idx_workitem_division ON core.work_item(division_id, status_id);

-- Índice para jerarquía de ítems
CREATE INDEX IF NOT EXISTS idx_workitem_parent ON core.work_item(parent_id) WHERE parent_id IS NOT NULL;

-- Índice para ítems activos
CREATE INDEX IF NOT EXISTS idx_workitem_active ON core.work_item(id) WHERE deleted_at IS NULL;

-- Índice para trazabilidad Story->WorkItem
-- Ya existe idx_work_item_story en DDL

-- Índice para trazabilidad Commitment->WorkItem
-- Ya existe idx_work_item_commitment en DDL

-- Índice GIN para tags
CREATE INDEX IF NOT EXISTS idx_workitem_tags ON core.work_item USING GIN(tags);

-- =============================================================================
--    SCHEMA: core - ÍNDICES PROBLEMAS Y ALERTAS
-- =============================================================================

-- CQ: "¿Qué problemas abiertos hay por IPR?"
-- Ya existe idx_ipr_problem_ipr y idx_ipr_problem_state en DDL

-- CQ: "¿Qué problemas no tienen trabajo asociado?"
CREATE INDEX IF NOT EXISTS idx_problem_unresolved ON core.ipr_problem(detected_at)
    WHERE resolved_at IS NULL AND deleted_at IS NULL;

-- CQ: "¿Qué alertas están sin atender por tipo?"
CREATE INDEX IF NOT EXISTS idx_alert_unattended ON core.alert(alert_type_id, severity_id)
    WHERE attended_at IS NULL;

-- CQ: "¿Qué alertas corresponden a la entidad X?"
-- Ya existe idx_alert_subject en DDL

-- =============================================================================
--    SCHEMA: core - ÍNDICES PRESUPUESTO Y FINANZAS
-- =============================================================================

-- CQ: "¿Cuál es el saldo disponible por programa presupuestario?"
-- Ya existe idx_budget_program_year en DDL

-- CQ: "¿Qué compromisos presupuestarios tiene la IPR X?"
CREATE INDEX IF NOT EXISTS idx_budget_commitment_ipr ON core.budget_commitment(ipr_id) WHERE ipr_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_budget_commitment_agreement ON core.budget_commitment(agreement_id) WHERE agreement_id IS NOT NULL;

-- CQ: "¿Qué compromisos presupuestarios están vigentes?"
CREATE INDEX IF NOT EXISTS idx_budget_commitment_number ON core.budget_commitment(commitment_number);
CREATE INDEX IF NOT EXISTS idx_budget_commitment_program ON core.budget_commitment(budget_program_id);

-- =============================================================================
--    SCHEMA: core - ÍNDICES ORGANIZACIÓN Y PERSONAS
-- =============================================================================

-- CQ: "¿Qué personas trabajan en la organización X?"
CREATE INDEX IF NOT EXISTS idx_person_org ON core.person(organization_id);
CREATE INDEX IF NOT EXISTS idx_person_active ON core.person(id) WHERE deleted_at IS NULL AND is_active = TRUE;

-- CQ: "¿Qué usuarios están activos?"
CREATE INDEX IF NOT EXISTS idx_user_active ON core.user(is_active, system_role_id)
    WHERE is_active = TRUE AND deleted_at IS NULL;

-- Índice para búsqueda por email (ya existe UNIQUE en DDL)

-- CQ: "¿Qué organizaciones hay por tipo?"
CREATE INDEX IF NOT EXISTS idx_org_type ON core.organization(org_type_id);
CREATE INDEX IF NOT EXISTS idx_org_parent ON core.organization(parent_id);
CREATE INDEX IF NOT EXISTS idx_org_active ON core.organization(id) WHERE deleted_at IS NULL;

-- =============================================================================
--    SCHEMA: core - ÍNDICES TERRITORIO
-- =============================================================================

-- CQ: "¿Qué comunas pertenecen a la provincia X?"
CREATE INDEX IF NOT EXISTS idx_territory_parent ON core.territory(parent_id, territory_type_id);

-- Índice para búsqueda por código CUT (ya existe UNIQUE en DDL)

-- =============================================================================
--    SCHEMA: core - ÍNDICES SESIONES Y ACUERDOS
-- =============================================================================

-- CQ: "¿Qué sesiones hay programadas para el comité X?"
CREATE INDEX IF NOT EXISTS idx_session_committee ON core.session(committee_id, scheduled_at);

-- CQ: "¿Qué acuerdos de sesión están pendientes de cumplimiento?"
CREATE INDEX IF NOT EXISTS idx_session_agreement_pending ON core.session_agreement(status_id, due_date);

-- =============================================================================
--    SCHEMA: core - ÍNDICES COMPROMISOS OPERATIVOS
-- =============================================================================

-- Ya existen idx_commitment_responsible, idx_commitment_state, idx_commitment_due en DDL

-- Índice para trazabilidad commitment->problem
CREATE INDEX IF NOT EXISTS idx_commitment_problem ON core.operational_commitment(problem_id) WHERE problem_id IS NOT NULL;

-- Índice para trazabilidad commitment->session
CREATE INDEX IF NOT EXISTS idx_commitment_session ON core.operational_commitment(session_id) WHERE session_id IS NOT NULL;

-- =============================================================================
--    SCHEMA: txn - ÍNDICES EVENTOS (PARTICIONADOS)
-- =============================================================================
-- Nota: Los índices en tablas particionadas se crean automáticamente en cada partición

-- Índices principales ya están en DDL:
-- idx_event_subject, idx_event_type, idx_event_occurred, idx_event_actor

-- Índice adicional para auditoría
CREATE INDEX IF NOT EXISTS idx_event_created_by ON txn.event(created_by_id) WHERE created_by_id IS NOT NULL;

-- =============================================================================
--    SCHEMA: txn - ÍNDICES MAGNITUDES (PARTICIONADOS)
-- =============================================================================

-- Índices principales ya están en DDL:
-- idx_magnitude_subject, idx_magnitude_aspect, idx_magnitude_date

-- =============================================================================
--    ÍNDICES FULL-TEXT SEARCH
-- =============================================================================

-- Búsqueda full-text en IPR
CREATE INDEX IF NOT EXISTS idx_ipr_fts ON core.ipr USING GIN(
    to_tsvector('spanish', COALESCE(name, ''))
);

-- Búsqueda full-text en work_item
CREATE INDEX IF NOT EXISTS idx_workitem_fts ON core.work_item USING GIN(
    to_tsvector('spanish', COALESCE(title, '') || ' ' || COALESCE(description, ''))
);

-- Búsqueda full-text en problemas
CREATE INDEX IF NOT EXISTS idx_problem_fts ON core.ipr_problem USING GIN(
    to_tsvector('spanish', COALESCE(description, '') || ' ' || COALESCE(solution_applied, ''))
);

-- =============================================================================
--    ÍNDICES JSONB METADATA
-- =============================================================================

-- Índices GIN para campos metadata en tablas principales
CREATE INDEX IF NOT EXISTS idx_ipr_metadata ON core.ipr USING GIN(metadata jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_agreement_metadata ON core.agreement USING GIN(metadata jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_workitem_metadata ON core.work_item USING GIN(metadata jsonb_path_ops);

-- =============================================================================
--    ESTADÍSTICAS
-- =============================================================================

-- Actualizar estadísticas después de carga masiva (ejecutar manualmente)
-- ANALYZE core.ipr;
-- ANALYZE core.agreement;
-- ANALYZE core.work_item;
-- ANALYZE txn.event;
-- ANALYZE txn.magnitude;

-- =============================================================================
--    FIN ÍNDICES v3.0
-- =============================================================================
-- Total índices creados: ~60
-- Tipos:
--   - B-tree: Búsquedas exactas y rangos
--   - GIN: Arrays, JSONB, Full-text
--   - Parciales: Filtros frecuentes (deleted_at IS NULL, is_active)
-- Nota: Índices en tablas particionadas se heredan automáticamente
-- =============================================================================

DO $$ BEGIN RAISE NOTICE 'GORE_OS Indexes v3.0 cargados correctamente'; END $$;
