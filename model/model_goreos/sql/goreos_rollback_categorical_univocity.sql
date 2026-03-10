-- =============================================================================
-- GORE_OS — ROLLBACK: UNIVOCIDAD CATEGORIAL
-- =============================================================================
-- Revierte goreos_migration_categorical_univocity.sql
-- =============================================================================

BEGIN;

-- ─── DROP CHECK CONSTRAINTS ───
ALTER TABLE core.organization DROP CONSTRAINT IF EXISTS chk_org_type_scheme;
ALTER TABLE core.person DROP CONSTRAINT IF EXISTS chk_person_type_scheme;
ALTER TABLE core."user" DROP CONSTRAINT IF EXISTS chk_system_role_scheme;
ALTER TABLE core.territory DROP CONSTRAINT IF EXISTS chk_territory_type_scheme;
ALTER TABLE core.budget_program DROP CONSTRAINT IF EXISTS chk_program_type_scheme;
ALTER TABLE core.budget_program DROP CONSTRAINT IF EXISTS chk_subtitle_scheme;
ALTER TABLE core.budget_commitment DROP CONSTRAINT IF EXISTS chk_commitment_type_scheme;
ALTER TABLE core.budget_commitment DROP CONSTRAINT IF EXISTS chk_budget_commit_status_scheme;
ALTER TABLE core.ipr DROP CONSTRAINT IF EXISTS chk_ipr_type_scheme;
ALTER TABLE core.ipr DROP CONSTRAINT IF EXISTS chk_funding_source_scheme;
ALTER TABLE core.ipr DROP CONSTRAINT IF EXISTS chk_investment_sector_scheme;
ALTER TABLE core.ipr DROP CONSTRAINT IF EXISTS chk_fund_category_scheme;
ALTER TABLE core.ipr DROP CONSTRAINT IF EXISTS chk_resolution_type_scheme;
ALTER TABLE core.ipr_problem DROP CONSTRAINT IF EXISTS chk_problem_type_scheme;
ALTER TABLE core.ipr_problem DROP CONSTRAINT IF EXISTS chk_problem_impact_scheme;
ALTER TABLE core.ipr_problem DROP CONSTRAINT IF EXISTS chk_problem_state_scheme;
ALTER TABLE core.administrative_act DROP CONSTRAINT IF EXISTS chk_act_type_scheme;
ALTER TABLE core.resolution DROP CONSTRAINT IF EXISTS chk_res_type_scheme;
ALTER TABLE core.resolution DROP CONSTRAINT IF EXISTS chk_res_subtype_scheme;
ALTER TABLE core.agreement DROP CONSTRAINT IF EXISTS chk_agreement_cgr_outcome_scheme;
ALTER TABLE core.agreement_installment DROP CONSTRAINT IF EXISTS chk_payment_status_scheme;
ALTER TABLE core.committee DROP CONSTRAINT IF EXISTS chk_committee_type_scheme;
ALTER TABLE core.committee_member DROP CONSTRAINT IF EXISTS chk_role_in_committee_scheme;
ALTER TABLE core.session DROP CONSTRAINT IF EXISTS chk_session_type_scheme;
ALTER TABLE core.alert DROP CONSTRAINT IF EXISTS chk_alert_type_scheme;
ALTER TABLE core.legal_document DROP CONSTRAINT IF EXISTS chk_doc_type_scheme;
ALTER TABLE core.rendition DROP CONSTRAINT IF EXISTS chk_rendition_state_scheme;
ALTER TABLE core.dgi_indicator_snapshot DROP CONSTRAINT IF EXISTS chk_dgi_signal_scheme;
ALTER TABLE core.commitment_history DROP CONSTRAINT IF EXISTS chk_commit_hist_prev_scheme;
ALTER TABLE core.commitment_history DROP CONSTRAINT IF EXISTS chk_commit_hist_new_scheme;
ALTER TABLE txn.event DROP CONSTRAINT IF EXISTS chk_event_type_scheme;

-- ─── RESTORE fn_validate_ipr_schemes (5 columns original) ───
CREATE OR REPLACE FUNCTION fn_validate_ipr_schemes()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.mcd_phase_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.mcd_phase_id, 'mcd_phase') THEN
            RAISE EXCEPTION 'mcd_phase_id debe pertenecer al scheme "mcd_phase"';
        END IF;
    END IF;
    IF NEW.status_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.status_id, 'ipr_state') THEN
            RAISE EXCEPTION 'status_id debe pertenecer al scheme "ipr_state"';
        END IF;
    END IF;
    IF NEW.mechanism_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.mechanism_id, 'mechanism') THEN
            RAISE EXCEPTION 'mechanism_id debe pertenecer al scheme "mechanism"';
        END IF;
    END IF;
    IF NEW.budget_subtitle_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.budget_subtitle_id, 'budget_subtitle') THEN
            RAISE EXCEPTION 'budget_subtitle_id debe pertenecer al scheme "budget_subtitle"';
        END IF;
    END IF;
    IF NEW.alert_level_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.alert_level_id, 'alert_level') THEN
            RAISE EXCEPTION 'alert_level_id debe pertenecer al scheme "alert_level"';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ─── Remove from schema_migration ───
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_categorical_univocity.sql';

COMMIT;

DO $$ BEGIN RAISE NOTICE 'GORE_OS Rollback categorical_univocity completado'; END $$;
