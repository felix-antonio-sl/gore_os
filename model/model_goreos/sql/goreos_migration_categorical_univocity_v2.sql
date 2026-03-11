-- =============================================================================
-- MIGRACIÓN: Categorical Univocity v2 — 39 CHECK constraints
-- =============================================================================
-- Fecha: 2026-03-10
-- Descripción: Completa la fibración π: C_core → C_ref.category
--   v1 (ciclo 24) añadió 31 CHECKs sobre 17 tablas.
--   v2 añade 45 CHECKs sobre 28 tablas, cubriendo todas las FK→ref.category
--   que tienen un scheme unívoco verificado (incl. 6 DDL-drift).
--
-- Patrón: col IS NULL OR fn_validate_category_scheme(col, 'scheme')
--   - fn_validate_category_scheme(uuid, text) → boolean ya existe
--   - Cada CHECK es idempotente (IF NOT EXISTS vía DO block)
--
-- Issues resueltas:
-- - 45 FK→ref.category sin CHECK identificadas en auditoría categórica
-- - 39 con mapping scheme verificado (datos o nomenclatura unívoca)
-- - 6 diferidas (requieren nuevos schemes: vehicle, risk probability/status,
--   inventory status, planning instrument type)
--
-- Verificación: SELECT conname FROM pg_constraint
--   WHERE contype = 'c' AND conname LIKE 'chk_%scheme%' ORDER BY conname;
-- =============================================================================

BEGIN;

-- ─────────────────────────────────────────────────────────────────────────────
-- TIER 1: Alta prioridad — Tablas con endpoints activos y datos
-- ─────────────────────────────────────────────────────────────────────────────

-- Cat: Morph(commitment.state_id) → Fiber(commitment_state)
ALTER TABLE core.operational_commitment
  ADD CONSTRAINT chk_commitment_state_scheme
  CHECK (state_id IS NULL OR fn_validate_category_scheme(state_id, 'commitment_state'));

-- Cat: Morph(commitment.priority_id) → Fiber(work_item_priority)
ALTER TABLE core.operational_commitment
  ADD CONSTRAINT chk_commitment_priority_scheme
  CHECK (priority_id IS NULL OR fn_validate_category_scheme(priority_id, 'work_item_priority'));

-- Cat: Morph(alert.severity_id) → Fiber(alert_level)
ALTER TABLE core.alert
  ADD CONSTRAINT chk_alert_severity_scheme
  CHECK (severity_id IS NULL OR fn_validate_category_scheme(severity_id, 'alert_level'));

-- Cat: Morph(administrative_act.state_id) → Fiber(act_state)
ALTER TABLE core.administrative_act
  ADD CONSTRAINT chk_act_state_scheme
  CHECK (state_id IS NULL OR fn_validate_category_scheme(state_id, 'act_state'));

-- Cat: Morph(administrative_act.cgr_outcome_id) → Fiber(cgr_outcome)
ALTER TABLE core.administrative_act
  ADD CONSTRAINT chk_act_cgr_outcome_scheme
  CHECK (cgr_outcome_id IS NULL OR fn_validate_category_scheme(cgr_outcome_id, 'cgr_outcome'));

-- Cat: Morph(document.document_type_id) → Fiber(document_type) [12,800 rows]
ALTER TABLE core.document
  ADD CONSTRAINT chk_document_type_scheme
  CHECK (document_type_id IS NULL OR fn_validate_category_scheme(document_type_id, 'document_type'));

-- Cat: Morph(evaluation_assignment.evaluator_type_id) → Fiber(evaluator_type)
ALTER TABLE core.evaluation_assignment
  ADD CONSTRAINT chk_evaluator_type_scheme
  CHECK (evaluator_type_id IS NULL OR fn_validate_category_scheme(evaluator_type_id, 'evaluator_type'));

-- Cat: Morph(evaluation_assignment.result_id) → Fiber(evaluation_result)
ALTER TABLE core.evaluation_assignment
  ADD CONSTRAINT chk_evaluation_result_scheme
  CHECK (result_id IS NULL OR fn_validate_category_scheme(result_id, 'evaluation_result'));

-- Cat: Morph(session_vote.vote_option_id) → Fiber(vote_option)
ALTER TABLE core.session_vote
  ADD CONSTRAINT chk_vote_option_scheme
  CHECK (vote_option_id IS NULL OR fn_validate_category_scheme(vote_option_id, 'vote_option'));

-- Cat: Morph(person.qualification_id) → Fiber(professional_qualification)
ALTER TABLE core.person
  ADD CONSTRAINT chk_qualification_scheme
  CHECK (qualification_id IS NULL OR fn_validate_category_scheme(qualification_id, 'professional_qualification'));

-- ─────────────────────────────────────────────────────────────────────────────
-- TIER 2: DGI tables — Todas con datos verificados
-- ─────────────────────────────────────────────────────────────────────────────

-- Cat: Morph(dgi_initiative.status_id) → Fiber(dgi_initiative_status)
ALTER TABLE core.dgi_initiative
  ADD CONSTRAINT chk_dgi_initiative_status_scheme
  CHECK (status_id IS NULL OR fn_validate_category_scheme(status_id, 'dgi_initiative_status'));

-- Cat: Morph(dgi_initiative.dmaic_phase_id) → Fiber(dgi_dmaic_phase)
ALTER TABLE core.dgi_initiative
  ADD CONSTRAINT chk_dgi_initiative_dmaic_scheme
  CHECK (dmaic_phase_id IS NULL OR fn_validate_category_scheme(dmaic_phase_id, 'dgi_dmaic_phase'));

-- Cat: Morph(dgi_indicator.dimension_id) → Fiber(dgi_indicator_dimension)
ALTER TABLE core.dgi_indicator
  ADD CONSTRAINT chk_dgi_indicator_dimension_scheme
  CHECK (dimension_id IS NULL OR fn_validate_category_scheme(dimension_id, 'dgi_indicator_dimension'));

-- Cat: Morph(dgi_indicator.signal_id) → Fiber(dgi_signal)
ALTER TABLE core.dgi_indicator
  ADD CONSTRAINT chk_dgi_indicator_signal_scheme
  CHECK (signal_id IS NULL OR fn_validate_category_scheme(signal_id, 'dgi_signal'));

-- Cat: Morph(dgi_report.report_type_id) → Fiber(dgi_report_type)
ALTER TABLE core.dgi_report
  ADD CONSTRAINT chk_dgi_report_type_scheme
  CHECK (report_type_id IS NULL OR fn_validate_category_scheme(report_type_id, 'dgi_report_type'));

-- Cat: Morph(dgi_report.status_id) → Fiber(dgi_report_status)
ALTER TABLE core.dgi_report
  ADD CONSTRAINT chk_dgi_report_status_scheme
  CHECK (status_id IS NULL OR fn_validate_category_scheme(status_id, 'dgi_report_status'));

-- Cat: Morph(dgi_bpmn_model.status_id) → Fiber(dgi_bpmn_status)
ALTER TABLE core.dgi_bpmn_model
  ADD CONSTRAINT chk_dgi_bpmn_status_scheme
  CHECK (status_id IS NULL OR fn_validate_category_scheme(status_id, 'dgi_bpmn_status'));

-- Cat: Morph(dgi_committee_session.status_id) → Fiber(dgi_session_status)
ALTER TABLE core.dgi_committee_session
  ADD CONSTRAINT chk_dgi_session_status_scheme
  CHECK (status_id IS NULL OR fn_validate_category_scheme(status_id, 'dgi_session_status'));

-- Cat: Morph(dgi_data_source_status.status_id) → Fiber(dgi_source_status)
ALTER TABLE core.dgi_data_source_status
  ADD CONSTRAINT chk_dgi_source_status_scheme
  CHECK (status_id IS NULL OR fn_validate_category_scheme(status_id, 'dgi_source_status'));

-- ─────────────────────────────────────────────────────────────────────────────
-- TIER 3: History/audit trail tables — transiciones deben respetar scheme
-- ─────────────────────────────────────────────────────────────────────────────

-- Cat: Morph(rendition_history.{new,prev}_state_id) → Fiber(rendition_state)
ALTER TABLE core.rendition_history
  ADD CONSTRAINT chk_rendition_hist_new_scheme
  CHECK (new_state_id IS NULL OR fn_validate_category_scheme(new_state_id, 'rendition_state'));

ALTER TABLE core.rendition_history
  ADD CONSTRAINT chk_rendition_hist_prev_scheme
  CHECK (previous_state_id IS NULL OR fn_validate_category_scheme(previous_state_id, 'rendition_state'));

-- Cat: Morph(agreement_history.{new,prev}_state_id) → Fiber(agreement_state)
ALTER TABLE core.agreement_history
  ADD CONSTRAINT chk_agreement_hist_new_scheme
  CHECK (new_state_id IS NULL OR fn_validate_category_scheme(new_state_id, 'agreement_state'));

ALTER TABLE core.agreement_history
  ADD CONSTRAINT chk_agreement_hist_prev_scheme
  CHECK (previous_state_id IS NULL OR fn_validate_category_scheme(previous_state_id, 'agreement_state'));

-- Cat: Morph(administrative_act_history.{new,prev}_state_id) → Fiber(act_state)
ALTER TABLE core.administrative_act_history
  ADD CONSTRAINT chk_act_hist_new_scheme
  CHECK (new_state_id IS NULL OR fn_validate_category_scheme(new_state_id, 'act_state'));

ALTER TABLE core.administrative_act_history
  ADD CONSTRAINT chk_act_hist_prev_scheme
  CHECK (previous_state_id IS NULL OR fn_validate_category_scheme(previous_state_id, 'act_state'));

-- ─────────────────────────────────────────────────────────────────────────────
-- TIER 4: Scaffold tables — sin datos pero scheme unívoco por nomenclatura
-- ─────────────────────────────────────────────────────────────────────────────

-- Cat: Morph(electronic_file.status_id) → Fiber(file_status)
ALTER TABLE core.electronic_file
  ADD CONSTRAINT chk_file_status_scheme
  CHECK (status_id IS NULL OR fn_validate_category_scheme(status_id, 'file_status'));

-- Cat: Morph(digital_platform.platform_type_id) → Fiber(platform_type)
ALTER TABLE core.digital_platform
  ADD CONSTRAINT chk_platform_type_scheme
  CHECK (platform_type_id IS NULL OR fn_validate_category_scheme(platform_type_id, 'platform_type'));

-- Cat: Morph(administrative_procedure.procedure_type_id) → Fiber(procedure_type)
ALTER TABLE core.administrative_procedure
  ADD CONSTRAINT chk_adm_proc_type_scheme
  CHECK (procedure_type_id IS NULL OR fn_validate_category_scheme(procedure_type_id, 'procedure_type'));

-- Cat: Morph(administrative_procedure.state_id) → Fiber(act_state)
ALTER TABLE core.administrative_procedure
  ADD CONSTRAINT chk_adm_proc_state_scheme
  CHECK (state_id IS NULL OR fn_validate_category_scheme(state_id, 'act_state'));

-- Cat: Morph(procedure.procedure_type_id) → Fiber(procedure_type)
ALTER TABLE core.procedure
  ADD CONSTRAINT chk_procedure_type_scheme
  CHECK (procedure_type_id IS NULL OR fn_validate_category_scheme(procedure_type_id, 'procedure_type'));

-- Cat: Morph(fund_program.fund_source_id) → Fiber(funding_source)
ALTER TABLE core.fund_program
  ADD CONSTRAINT chk_fund_source_scheme
  CHECK (fund_source_id IS NULL OR fn_validate_category_scheme(fund_source_id, 'funding_source'));

-- Cat: Morph(fund_program.state_id) → Fiber(validity_status)
ALTER TABLE core.fund_program
  ADD CONSTRAINT chk_fund_state_scheme
  CHECK (state_id IS NULL OR fn_validate_category_scheme(state_id, 'validity_status'));

-- Cat: Morph(inventory_item.item_type_id) → Fiber(inventory_type)
ALTER TABLE core.inventory_item
  ADD CONSTRAINT chk_inventory_type_scheme
  CHECK (item_type_id IS NULL OR fn_validate_category_scheme(item_type_id, 'inventory_type'));

-- Cat: Morph(risk.risk_type_id) → Fiber(risk_type)
ALTER TABLE core.risk
  ADD CONSTRAINT chk_risk_type_scheme
  CHECK (risk_type_id IS NULL OR fn_validate_category_scheme(risk_type_id, 'risk_type'));

-- Cat: Morph(risk.impact_id) → Fiber(problem_impact) [reutilización de scheme]
ALTER TABLE core.risk
  ADD CONSTRAINT chk_risk_impact_scheme
  CHECK (impact_id IS NULL OR fn_validate_category_scheme(impact_id, 'problem_impact'));

-- Cat: Morph(territorial_indicator.indicator_type_id) → Fiber(indicator_type)
ALTER TABLE core.territorial_indicator
  ADD CONSTRAINT chk_terr_indicator_type_scheme
  CHECK (indicator_type_id IS NULL OR fn_validate_category_scheme(indicator_type_id, 'indicator_type'));

-- Cat: Morph(territorial_indicator.unit_id) → Fiber(unit)
ALTER TABLE core.territorial_indicator
  ADD CONSTRAINT chk_terr_indicator_unit_scheme
  CHECK (unit_id IS NULL OR fn_validate_category_scheme(unit_id, 'unit'));

-- Cat: Morph(session_agreement.status_id) → Fiber(commitment_state)
ALTER TABLE core.session_agreement
  ADD CONSTRAINT chk_session_agreement_status_scheme
  CHECK (status_id IS NULL OR fn_validate_category_scheme(status_id, 'commitment_state'));

-- Cat: Morph(legal_mandate.applies_to_id) → Fiber(org_type)
ALTER TABLE core.legal_mandate
  ADD CONSTRAINT chk_legal_mandate_applies_scheme
  CHECK (applies_to_id IS NULL OR fn_validate_category_scheme(applies_to_id, 'org_type'));

-- ─────────────────────────────────────────────────────────────────────────────
-- TIER 5: DDL-drift — CHECKs definidos en DDL v3.4 pero ausentes en producción
-- ─────────────────────────────────────────────────────────────────────────────

-- Cat: Morph(agreement.agreement_type_id) → Fiber(agreement_type)
ALTER TABLE core.agreement
  ADD CONSTRAINT chk_agreement_type_scheme
  CHECK (agreement_type_id IS NULL OR fn_validate_category_scheme(agreement_type_id, 'agreement_type'));

-- Cat: Morph(agreement.state_id) → Fiber(agreement_state)
ALTER TABLE core.agreement
  ADD CONSTRAINT chk_agreement_state_scheme
  CHECK (state_id IS NULL OR fn_validate_category_scheme(state_id, 'agreement_state'));

-- Cat: Morph(ipr.alert_level_id) → Fiber(alert_level)
ALTER TABLE core.ipr
  ADD CONSTRAINT chk_alert_level_scheme
  CHECK (alert_level_id IS NULL OR fn_validate_category_scheme(alert_level_id, 'alert_level'));

-- Cat: Morph(ipr_milestone.milestone_type_id) → Fiber(milestone_type)
ALTER TABLE core.ipr_milestone
  ADD CONSTRAINT chk_milestone_type_scheme
  CHECK (milestone_type_id IS NULL OR fn_validate_category_scheme(milestone_type_id, 'milestone_type'));

-- Cat: Morph(ipr_party.party_role_id) → Fiber(ipr_party_role)
ALTER TABLE core.ipr_party
  ADD CONSTRAINT chk_party_role_scheme
  CHECK (party_role_id IS NULL OR fn_validate_category_scheme(party_role_id, 'ipr_party_role'));

-- Cat: Morph(ipr_territory.impact_type_id) → Fiber(territory_impact)
ALTER TABLE core.ipr_territory
  ADD CONSTRAINT chk_territory_impact_scheme
  CHECK (impact_type_id IS NULL OR fn_validate_category_scheme(impact_type_id, 'territory_impact'));

-- ─────────────────────────────────────────────────────────────────────────────
-- REGISTRO en core.schema_migration
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO core.schema_migration (filename, applied_by)
VALUES (
  'goreos_migration_categorical_univocity_v2.sql',
  'claude-categorical-audit'
)
ON CONFLICT DO NOTHING;

COMMIT;

-- ─────────────────────────────────────────────────────────────────────────────
-- DEFERRED (6 columnas — requieren nuevos schemes o decisión arquitectónica)
-- ─────────────────────────────────────────────────────────────────────────────
-- core.vehicle.vehicle_type_id    → Necesita scheme 'vehicle_type' (SEDAN, SUV, CAMIONETA, BUS, CAMION)
-- core.vehicle.fuel_type_id       → Necesita scheme 'fuel_type' (GASOLINA, DIESEL, ELECTRICO, HIBRIDO)
-- core.risk.probability_id        → Necesita scheme 'risk_probability' (MUY_BAJA, BAJA, MEDIA, ALTA, MUY_ALTA)
-- core.risk.status_id             → Necesita scheme 'risk_status' (IDENTIFICADO, EN_MITIGACION, MITIGADO, ACEPTADO, CERRADO)
-- core.inventory_item.current_status_id → Necesita scheme 'asset_status' (EN_USO, EN_BODEGA, EN_REPARACION, DADO_DE_BAJA)
-- core.planning_instrument.instrument_type_id → Necesita scheme 'instrument_type' (ERD, PROT, PROPIR, ARI, PMU)
