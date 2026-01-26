-- ============================================================================
-- GORE_OS v2.0 - INDEXES
-- ============================================================================
-- Archivo: goreos_indexes.sql
-- Descripción: Índices optimizados para Competency Questions frecuentes
-- Generado: 2026-01-26
-- ============================================================================
-- Principios de Indexación:
-- 1. Índices compuestos para queries frecuentes (CQs del dominio)
-- 2. Índices parciales para estados activos (reducir tamaño)
-- 3. Índices GIN para búsquedas JSONB y arrays
-- 4. Índices BRIN para columnas temporales (alto volumen)
-- ============================================================================

-- ============================================================================
--    SCHEMA: ref - ÍNDICES DATOS DE REFERENCIA
-- ============================================================================

-- ref.category: Búsqueda por scheme (query más frecuente)
CREATE INDEX IF NOT EXISTS idx_category_scheme ON ref.category(scheme);
CREATE INDEX IF NOT EXISTS idx_category_scheme_code ON ref.category(scheme, code);
CREATE INDEX IF NOT EXISTS idx_category_parent ON ref.category(parent_code) WHERE parent_code IS NOT NULL;

-- ref.actor: Búsqueda por código y tipo
CREATE INDEX IF NOT EXISTS idx_actor_code ON ref.actor(code);
CREATE INDEX IF NOT EXISTS idx_actor_internal ON ref.actor(is_internal);

-- ============================================================================
--    SCHEMA: core - ÍNDICES IPR (Iniciativas de Inversión)
-- ============================================================================

-- CQ: "¿Cuáles son las IPR en fase F4 del mecanismo FRIL?"
CREATE INDEX IF NOT EXISTS idx_ipr_phase_mechanism ON core.ipr(mcd_phase_id, mechanism_id);

-- CQ: "¿Qué IPR tienen estado 'EN_EJECUCION'?"
CREATE INDEX IF NOT EXISTS idx_ipr_status ON core.ipr(status_id);

-- CQ: "¿Cuál es el avance financiero de IPRs por año?"
CREATE INDEX IF NOT EXISTS idx_ipr_year ON core.ipr(EXTRACT(YEAR FROM created_at));

-- CQ: "¿Qué IPR están asignadas al usuario X?"
CREATE INDEX IF NOT EXISTS idx_ipr_assignee ON core.ipr(assignee_id) WHERE assignee_id IS NOT NULL;

-- CQ: "¿Qué IPR tienen problemas abiertos?"
CREATE INDEX IF NOT EXISTS idx_ipr_problems ON core.ipr(has_open_problems) WHERE has_open_problems = TRUE;

-- CQ: "¿Qué IPR tienen nivel de alerta CRITICO?"
CREATE INDEX IF NOT EXISTS idx_ipr_alert ON core.ipr(alert_level_id) WHERE alert_level_id IS NOT NULL;

-- Índice para búsqueda por código BIP
CREATE UNIQUE INDEX IF NOT EXISTS idx_ipr_bip ON core.ipr(codigo_bip) WHERE codigo_bip IS NOT NULL;

-- Índice para búsqueda por naturaleza (proyecto, programa, etc.)
CREATE INDEX IF NOT EXISTS idx_ipr_nature ON core.ipr(ipr_nature_id);

-- Índice compuesto para dashboard de inversiones
CREATE INDEX IF NOT EXISTS idx_ipr_dashboard ON core.ipr(status_id, mcd_phase_id, ipr_nature_id, funding_source_id);

-- ============================================================================
--    SCHEMA: core - ÍNDICES CONVENIOS Y ACTOS
-- ============================================================================

-- CQ: "¿Qué convenios vencen en los próximos 30 días?"
-- NOTA: Índices parciales no pueden usar subqueries, usar expresión simple
CREATE INDEX IF NOT EXISTS idx_agreement_valid_to ON core.agreement(valid_to) WHERE valid_to IS NOT NULL;

-- CQ: "¿Qué convenios tiene la entidad dadora/receptora X?"
CREATE INDEX IF NOT EXISTS idx_agreement_giver ON core.agreement(giver_id);
CREATE INDEX IF NOT EXISTS idx_agreement_receiver ON core.agreement(receiver_id);

-- CQ: "¿Qué convenios están vinculados a la IPR X?"
CREATE INDEX IF NOT EXISTS idx_agreement_ipr ON core.agreement(ipr_id) WHERE ipr_id IS NOT NULL;

-- Índice para convenios por estado
CREATE INDEX IF NOT EXISTS idx_agreement_state ON core.agreement(state_id);

-- CQ: "¿Qué cuotas de convenio están vencidas?"
CREATE INDEX IF NOT EXISTS idx_installment_due ON core.agreement_installment(due_date, payment_status_id);

-- Índice para resoluciones por IPR
CREATE INDEX IF NOT EXISTS idx_resolution_ipr ON core.resolution(ipr_id) WHERE ipr_id IS NOT NULL;

-- Índice para resoluciones por tipo
CREATE INDEX IF NOT EXISTS idx_resolution_type ON core.resolution(resolution_type_id);

-- ============================================================================
--    SCHEMA: core - ÍNDICES WORK ITEMS (GESTIÓN OPERATIVA)
-- ============================================================================

-- CQ: "¿Qué ítems de trabajo tiene asignados el usuario X?"
CREATE INDEX IF NOT EXISTS idx_workitem_assignee ON core.work_item(assignee_id, status_id);

-- CQ: "¿Qué ítems de trabajo están vencidos?"
-- NOTA: Índices parciales no pueden usar subqueries
CREATE INDEX IF NOT EXISTS idx_workitem_due ON core.work_item(due_date) WHERE due_date IS NOT NULL;

-- CQ: "¿Qué ítems están bloqueados por más de 7 días?"
CREATE INDEX IF NOT EXISTS idx_workitem_blocked ON core.work_item(updated_at)
    WHERE blocked_by_item_id IS NOT NULL;

-- CQ: "¿Qué ítems tiene la división X pendientes?"
CREATE INDEX IF NOT EXISTS idx_workitem_division ON core.work_item(division_id, status_id);

-- Índice para jerarquía de ítems
CREATE INDEX IF NOT EXISTS idx_workitem_parent ON core.work_item(parent_id) WHERE parent_id IS NOT NULL;

-- Índice para búsqueda por código
CREATE UNIQUE INDEX IF NOT EXISTS idx_workitem_code ON core.work_item(code);

-- Índice para vinculación a entidades (polimórfico)
CREATE INDEX IF NOT EXISTS idx_workitem_ipr ON core.work_item(ipr_id) WHERE ipr_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_workitem_agreement ON core.work_item(agreement_id) WHERE agreement_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_workitem_problem ON core.work_item(problem_id) WHERE problem_id IS NOT NULL;

-- Índice GIN para tags
CREATE INDEX IF NOT EXISTS idx_workitem_tags ON core.work_item USING GIN(tags);

-- HIGH-005: Índice para trazabilidad Story->WorkItem
CREATE INDEX IF NOT EXISTS idx_workitem_story ON core.work_item(story_id) WHERE story_id IS NOT NULL;

-- ============================================================================
--    SCHEMA: core - ÍNDICES PROBLEMAS Y ALERTAS
-- ============================================================================

-- CQ: "¿Qué problemas abiertos hay por IPR?"
CREATE INDEX IF NOT EXISTS idx_problem_ipr ON core.ipr_problem(ipr_id, state_id);

-- CQ: "¿Qué problemas no tienen trabajo asociado?"
CREATE INDEX IF NOT EXISTS idx_problem_unmanaged ON core.ipr_problem(detected_at)
    WHERE resolved_at IS NULL;

-- CQ: "¿Qué alertas están sin atender por tipo?"
CREATE INDEX IF NOT EXISTS idx_alert_type_unattended ON core.alert(alert_type_id, severity_id)
    WHERE attended_at IS NULL;

-- CQ: "¿Qué alertas corresponden a la entidad X?"
CREATE INDEX IF NOT EXISTS idx_alert_target ON core.alert(target_type, target_id)
    WHERE target_type IS NOT NULL;

-- ============================================================================
--    SCHEMA: core - ÍNDICES PRESUPUESTO Y FINANZAS
-- ============================================================================

-- CQ: "¿Cuál es el saldo disponible por programa presupuestario?"
CREATE INDEX IF NOT EXISTS idx_budget_program_year ON core.budget_program(fiscal_year);

-- CQ: "¿Qué compromisos presupuestarios tiene la IPR X?"
CREATE INDEX IF NOT EXISTS idx_budget_commitment_ipr ON core.budget_commitment(ipr_id);

-- CQ: "¿Qué compromisos presupuestarios están vigentes?"
CREATE INDEX IF NOT EXISTS idx_budget_commitment_number ON core.budget_commitment(commitment_number);

-- ============================================================================
--    SCHEMA: core - ÍNDICES ORGANIZACIÓN Y PERSONAS
-- ============================================================================

-- CQ: "¿Qué personas trabajan en la división X?"
CREATE INDEX IF NOT EXISTS idx_person_org ON core.person(organization_id);

-- CQ: "¿Qué usuarios están activos?"
CREATE INDEX IF NOT EXISTS idx_user_active ON core.user(is_active, system_role_id)
    WHERE is_active = TRUE;

-- Índice para búsqueda por email
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_email ON core.user(email);

-- CQ: "¿Qué organizaciones hay por tipo?"
CREATE INDEX IF NOT EXISTS idx_org_type ON core.organization(org_type_id);

-- ============================================================================
--    SCHEMA: core - ÍNDICES TERRITORIO
-- ============================================================================

-- CQ: "¿Qué comunas pertenecen a la provincia X?"
CREATE INDEX IF NOT EXISTS idx_territory_parent ON core.territory(parent_id, territory_type_id);

-- Índice para búsqueda por código CUT
CREATE UNIQUE INDEX IF NOT EXISTS idx_territory_code ON core.territory(code);

-- ============================================================================
--    SCHEMA: core - ÍNDICES SESIONES Y ACUERDOS
-- ============================================================================

-- CQ: "¿Qué sesiones hay programadas para el comité X?"
CREATE INDEX IF NOT EXISTS idx_session_committee ON core.session(committee_id, scheduled_at);

-- CQ: "¿Qué acuerdos de sesión están pendientes de cumplimiento?"
CREATE INDEX IF NOT EXISTS idx_session_agreement_pending ON core.session_agreement(status_id, due_date);

-- ============================================================================
--    SCHEMA: txn - ÍNDICES EVENTOS (EVENT SOURCING)
-- ============================================================================

-- CQ: "¿Qué eventos ocurrieron en la entidad X?"
CREATE INDEX IF NOT EXISTS idx_event_subject ON txn.event(subject_type, subject_id);

-- CQ: "¿Qué eventos de tipo X ocurrieron en el período Y?"
CREATE INDEX IF NOT EXISTS idx_event_type_time ON txn.event(event_type_id, occurred_at);

-- Índice BRIN para alta cardinalidad temporal (eficiente para rangos)
CREATE INDEX IF NOT EXISTS idx_event_occurred_brin ON txn.event USING BRIN(occurred_at);

-- Índice GIN para búsqueda en data JSONB
CREATE INDEX IF NOT EXISTS idx_event_data ON txn.event USING GIN(data jsonb_path_ops);

-- ============================================================================
--    SCHEMA: txn - ÍNDICES MAGNITUDES
-- ============================================================================

-- CQ: "¿Cuál es la magnitud X de la entidad Y en el período Z?"
CREATE INDEX IF NOT EXISTS idx_magnitude_subject_aspect ON txn.magnitude(subject_type, subject_id, aspect_id);

-- Índice para búsqueda por fecha de medición
CREATE INDEX IF NOT EXISTS idx_magnitude_as_of ON txn.magnitude(as_of_date);

-- ============================================================================
--    SCHEMA: meta - ÍNDICES HISTORIAS Y PROCESOS
-- ============================================================================

-- CQ: "¿Qué historias de usuario corresponden al dominio X?"
CREATE INDEX IF NOT EXISTS idx_story_domain ON meta.story(domain);

-- CQ: "¿Qué entidades participan en la historia X?"
CREATE INDEX IF NOT EXISTS idx_story_entity_story ON meta.story_entity(story_id);
CREATE INDEX IF NOT EXISTS idx_story_entity_entity ON meta.story_entity(entity_id);

-- CQ: "¿Qué roles son HAIC (Human-AI Collaboration)?"
CREATE INDEX IF NOT EXISTS idx_role_agent_type ON meta.role(agent_type);

-- ============================================================================
--    ÍNDICES FULL-TEXT SEARCH (opcional, para búsquedas de texto)
-- ============================================================================

-- Búsqueda full-text en IPR (solo name, no tiene description)
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

-- ============================================================================
--    ÍNDICES JSONB METADATA (para extensibilidad)
-- ============================================================================

-- Índices GIN para campos metadata en tablas principales
CREATE INDEX IF NOT EXISTS idx_ipr_metadata ON core.ipr USING GIN(metadata jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_agreement_metadata ON core.agreement USING GIN(metadata jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_workitem_metadata ON core.work_item USING GIN(metadata jsonb_path_ops);
-- NOTA: txn.event no tiene columna metadata, solo data (ya indexada arriba)

-- ============================================================================
--    ESTADÍSTICAS Y MANTENIMIENTO
-- ============================================================================

-- Actualizar estadísticas después de carga masiva
-- ANALYZE core.ipr;
-- ANALYZE core.agreement;
-- ANALYZE core.work_item;
-- ANALYZE txn.event;

-- ============================================================================
--    FIN ÍNDICES
-- ============================================================================
-- Total índices creados: ~75
-- Tipos:
--   - B-tree: Búsquedas exactas y rangos
--   - GIN: Arrays, JSONB, Full-text
--   - BRIN: Columnas temporales de alto volumen
--   - Parciales: Filtros frecuentes (is_active, estados específicos)
-- ============================================================================
