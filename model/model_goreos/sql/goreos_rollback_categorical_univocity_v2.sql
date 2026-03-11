-- =============================================================================
-- ROLLBACK: Categorical Univocity v2 — Drop 39 CHECK constraints
-- =============================================================================

BEGIN;

-- Tier 1: Active endpoint tables
ALTER TABLE core.operational_commitment DROP CONSTRAINT IF EXISTS chk_commitment_state_scheme;
ALTER TABLE core.operational_commitment DROP CONSTRAINT IF EXISTS chk_commitment_priority_scheme;
ALTER TABLE core.alert DROP CONSTRAINT IF EXISTS chk_alert_severity_scheme;
ALTER TABLE core.administrative_act DROP CONSTRAINT IF EXISTS chk_act_state_scheme;
ALTER TABLE core.administrative_act DROP CONSTRAINT IF EXISTS chk_act_cgr_outcome_scheme;
ALTER TABLE core.document DROP CONSTRAINT IF EXISTS chk_document_type_scheme;
ALTER TABLE core.evaluation_assignment DROP CONSTRAINT IF EXISTS chk_evaluator_type_scheme;
ALTER TABLE core.evaluation_assignment DROP CONSTRAINT IF EXISTS chk_evaluation_result_scheme;
ALTER TABLE core.session_vote DROP CONSTRAINT IF EXISTS chk_vote_option_scheme;
ALTER TABLE core.person DROP CONSTRAINT IF EXISTS chk_qualification_scheme;

-- Tier 2: DGI tables
ALTER TABLE core.dgi_initiative DROP CONSTRAINT IF EXISTS chk_dgi_initiative_status_scheme;
ALTER TABLE core.dgi_initiative DROP CONSTRAINT IF EXISTS chk_dgi_initiative_dmaic_scheme;
ALTER TABLE core.dgi_indicator DROP CONSTRAINT IF EXISTS chk_dgi_indicator_dimension_scheme;
ALTER TABLE core.dgi_indicator DROP CONSTRAINT IF EXISTS chk_dgi_indicator_signal_scheme;
ALTER TABLE core.dgi_report DROP CONSTRAINT IF EXISTS chk_dgi_report_type_scheme;
ALTER TABLE core.dgi_report DROP CONSTRAINT IF EXISTS chk_dgi_report_status_scheme;
ALTER TABLE core.dgi_bpmn_model DROP CONSTRAINT IF EXISTS chk_dgi_bpmn_status_scheme;
ALTER TABLE core.dgi_committee_session DROP CONSTRAINT IF EXISTS chk_dgi_session_status_scheme;
ALTER TABLE core.dgi_data_source_status DROP CONSTRAINT IF EXISTS chk_dgi_source_status_scheme;

-- Tier 3: History tables
ALTER TABLE core.rendition_history DROP CONSTRAINT IF EXISTS chk_rendition_hist_new_scheme;
ALTER TABLE core.rendition_history DROP CONSTRAINT IF EXISTS chk_rendition_hist_prev_scheme;
ALTER TABLE core.agreement_history DROP CONSTRAINT IF EXISTS chk_agreement_hist_new_scheme;
ALTER TABLE core.agreement_history DROP CONSTRAINT IF EXISTS chk_agreement_hist_prev_scheme;
ALTER TABLE core.administrative_act_history DROP CONSTRAINT IF EXISTS chk_act_hist_new_scheme;
ALTER TABLE core.administrative_act_history DROP CONSTRAINT IF EXISTS chk_act_hist_prev_scheme;

-- Tier 4: Scaffold tables
ALTER TABLE core.electronic_file DROP CONSTRAINT IF EXISTS chk_file_status_scheme;
ALTER TABLE core.digital_platform DROP CONSTRAINT IF EXISTS chk_platform_type_scheme;
ALTER TABLE core.administrative_procedure DROP CONSTRAINT IF EXISTS chk_adm_proc_type_scheme;
ALTER TABLE core.administrative_procedure DROP CONSTRAINT IF EXISTS chk_adm_proc_state_scheme;
ALTER TABLE core.procedure DROP CONSTRAINT IF EXISTS chk_procedure_type_scheme;
ALTER TABLE core.fund_program DROP CONSTRAINT IF EXISTS chk_fund_source_scheme;
ALTER TABLE core.fund_program DROP CONSTRAINT IF EXISTS chk_fund_state_scheme;
ALTER TABLE core.inventory_item DROP CONSTRAINT IF EXISTS chk_inventory_type_scheme;
ALTER TABLE core.risk DROP CONSTRAINT IF EXISTS chk_risk_type_scheme;
ALTER TABLE core.risk DROP CONSTRAINT IF EXISTS chk_risk_impact_scheme;
ALTER TABLE core.territorial_indicator DROP CONSTRAINT IF EXISTS chk_terr_indicator_type_scheme;
ALTER TABLE core.territorial_indicator DROP CONSTRAINT IF EXISTS chk_terr_indicator_unit_scheme;
ALTER TABLE core.session_agreement DROP CONSTRAINT IF EXISTS chk_session_agreement_status_scheme;
ALTER TABLE core.legal_mandate DROP CONSTRAINT IF EXISTS chk_legal_mandate_applies_scheme;

-- Tier 5: DDL-drift
ALTER TABLE core.agreement DROP CONSTRAINT IF EXISTS chk_agreement_type_scheme;
ALTER TABLE core.agreement DROP CONSTRAINT IF EXISTS chk_agreement_state_scheme;
ALTER TABLE core.ipr DROP CONSTRAINT IF EXISTS chk_alert_level_scheme;
ALTER TABLE core.ipr_milestone DROP CONSTRAINT IF EXISTS chk_milestone_type_scheme;
ALTER TABLE core.ipr_party DROP CONSTRAINT IF EXISTS chk_party_role_scheme;
ALTER TABLE core.ipr_territory DROP CONSTRAINT IF EXISTS chk_territory_impact_scheme;

-- Remove migration record
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_categorical_univocity_v2.sql';

COMMIT;
