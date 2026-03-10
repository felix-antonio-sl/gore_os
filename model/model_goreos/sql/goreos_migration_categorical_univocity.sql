-- =============================================================================
-- GORE_OS — MIGRACIÓN: UNIVOCIDAD CATEGORIAL COMPLETA
-- =============================================================================
-- Archivo: goreos_migration_categorical_univocity.sql
-- Fecha: 2026-03-09
-- Autor: Auditoría Categorial v6
-- Dependencias: goreos_ddl.sql, goreos_triggers_remediation.sql
-- =============================================================================
--
-- REMEDIACIÓN COMPLETA — Resumen de 10 hallazgos auditados:
--
-- R-01 (HIGH)   31 CHECK constraints para FK→ref.category sin validación
-- R-02 (MEDIUM) Extensión de fn_validate_ipr_schemes (+5 columnas)
-- R-03 (LOW)    Documentación de plan de consolidación de triggers
-- B-01 (MEDIUM) YA RESUELTO — trg_agreement_state_transition en wave1
-- B-03 (LOW)    Gate typing (fix en ipr.py, no en DDL)
-- S-01 (MEDIUM) DDL circular deps documentado (ver ADR-007)
-- S-02 (LOW)    ref.operational_commitment_type NO es redundante (types≠states)
-- D-01 (MEDIUM) Orphan tables documentadas (ver ADR-007)
-- D-02 (LOW)    YA EXISTE — ADR-002-raw-sql.md
-- D-03 (LOW)    Codegen recommendation (ver ADR-007)
--
-- =============================================================================

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════════
-- DATA FIX: Corregir scheme huérfano 'budget_program_type' → 'program_type'
-- ═══════════════════════════════════════════════════════════════════════════
-- El scheme 'budget_program_type' no se usa en ningún código (0 refs en API/frontend).
-- 2 budget_program rows apuntan a SUBVENCION_8PCT bajo scheme incorrecto.
-- Fix: reclasificar al scheme canónico 'program_type'.

UPDATE ref.category
SET scheme = 'program_type'
WHERE scheme = 'budget_program_type'
  AND code = 'SUBVENCION_8PCT';

-- ═══════════════════════════════════════════════════════════════════════════
-- R-01: CHECK CONSTRAINTS PARA UNIVOCIDAD CATEGORIAL
-- ═══════════════════════════════════════════════════════════════════════════
-- Patrón: col IS NULL OR fn_validate_category_scheme(col, 'scheme')
-- Cada FK→ref.category debe apuntar a exactamente 1 scheme (Categorical Univocity)

-- ─── core.organization ───
ALTER TABLE core.organization
  DROP CONSTRAINT IF EXISTS chk_org_type_scheme,
  ADD CONSTRAINT chk_org_type_scheme
  CHECK (org_type_id IS NULL OR fn_validate_category_scheme(org_type_id, 'org_type'));

-- ─── core.person ───
ALTER TABLE core.person
  DROP CONSTRAINT IF EXISTS chk_person_type_scheme,
  ADD CONSTRAINT chk_person_type_scheme
  CHECK (person_type_id IS NULL OR fn_validate_category_scheme(person_type_id, 'person_type'));

-- ─── core."user" ───
ALTER TABLE core."user"
  DROP CONSTRAINT IF EXISTS chk_system_role_scheme,
  ADD CONSTRAINT chk_system_role_scheme
  CHECK (system_role_id IS NULL OR fn_validate_category_scheme(system_role_id, 'system_role'));

-- ─── core.territory ───
ALTER TABLE core.territory
  DROP CONSTRAINT IF EXISTS chk_territory_type_scheme,
  ADD CONSTRAINT chk_territory_type_scheme
  CHECK (territory_type_id IS NULL OR fn_validate_category_scheme(territory_type_id, 'territory_type'));

-- ─── core.budget_program ───
ALTER TABLE core.budget_program
  DROP CONSTRAINT IF EXISTS chk_program_type_scheme,
  ADD CONSTRAINT chk_program_type_scheme
  CHECK (program_type_id IS NULL OR fn_validate_category_scheme(program_type_id, 'program_type'));

ALTER TABLE core.budget_program
  DROP CONSTRAINT IF EXISTS chk_subtitle_scheme,
  ADD CONSTRAINT chk_subtitle_scheme
  CHECK (subtitle_id IS NULL OR fn_validate_category_scheme(subtitle_id, 'budget_subtitle'));

-- ─── core.budget_call ─── SKIP: table not materialized in DB

-- ─── core.budget_commitment ───
ALTER TABLE core.budget_commitment
  DROP CONSTRAINT IF EXISTS chk_commitment_type_scheme,
  ADD CONSTRAINT chk_commitment_type_scheme
  CHECK (commitment_type_id IS NULL OR fn_validate_category_scheme(commitment_type_id, 'commitment_type'));

ALTER TABLE core.budget_commitment
  DROP CONSTRAINT IF EXISTS chk_budget_commit_status_scheme,
  ADD CONSTRAINT chk_budget_commit_status_scheme
  CHECK (status_id IS NULL OR fn_validate_category_scheme(status_id, 'budget_commitment_status'));

-- ─── core.ipr ───
ALTER TABLE core.ipr
  DROP CONSTRAINT IF EXISTS chk_ipr_type_scheme,
  ADD CONSTRAINT chk_ipr_type_scheme
  CHECK (ipr_type_id IS NULL OR fn_validate_category_scheme(ipr_type_id, 'ipr_type'));

ALTER TABLE core.ipr
  DROP CONSTRAINT IF EXISTS chk_funding_source_scheme,
  ADD CONSTRAINT chk_funding_source_scheme
  CHECK (funding_source_id IS NULL OR fn_validate_category_scheme(funding_source_id, 'funding_source'));

ALTER TABLE core.ipr
  DROP CONSTRAINT IF EXISTS chk_investment_sector_scheme,
  ADD CONSTRAINT chk_investment_sector_scheme
  CHECK (investment_sector_id IS NULL OR fn_validate_category_scheme(investment_sector_id, 'investment_sector'));

ALTER TABLE core.ipr
  DROP CONSTRAINT IF EXISTS chk_fund_category_scheme,
  ADD CONSTRAINT chk_fund_category_scheme
  CHECK (fund_category_id IS NULL OR fn_validate_category_scheme(fund_category_id, 'fondo_8pct'));

ALTER TABLE core.ipr
  DROP CONSTRAINT IF EXISTS chk_resolution_type_scheme,
  ADD CONSTRAINT chk_resolution_type_scheme
  CHECK (resolution_type_id IS NULL OR fn_validate_category_scheme(resolution_type_id, 'resolution_type'));

-- ─── core.ipr_problem ───
ALTER TABLE core.ipr_problem
  DROP CONSTRAINT IF EXISTS chk_problem_type_scheme,
  ADD CONSTRAINT chk_problem_type_scheme
  CHECK (problem_type_id IS NULL OR fn_validate_category_scheme(problem_type_id, 'problem_type'));

ALTER TABLE core.ipr_problem
  DROP CONSTRAINT IF EXISTS chk_problem_impact_scheme,
  ADD CONSTRAINT chk_problem_impact_scheme
  CHECK (impact_id IS NULL OR fn_validate_category_scheme(impact_id, 'problem_impact'));

ALTER TABLE core.ipr_problem
  DROP CONSTRAINT IF EXISTS chk_problem_state_scheme,
  ADD CONSTRAINT chk_problem_state_scheme
  CHECK (state_id IS NULL OR fn_validate_category_scheme(state_id, 'problem_state'));

-- ─── core.administrative_act ───
ALTER TABLE core.administrative_act
  DROP CONSTRAINT IF EXISTS chk_act_type_scheme,
  ADD CONSTRAINT chk_act_type_scheme
  CHECK (act_type_id IS NULL OR fn_validate_category_scheme(act_type_id, 'act_type'));

-- ─── core.resolution ───
ALTER TABLE core.resolution
  DROP CONSTRAINT IF EXISTS chk_res_type_scheme,
  ADD CONSTRAINT chk_res_type_scheme
  CHECK (resolution_type_id IS NULL OR fn_validate_category_scheme(resolution_type_id, 'resolution_type'));

ALTER TABLE core.resolution
  DROP CONSTRAINT IF EXISTS chk_res_subtype_scheme,
  ADD CONSTRAINT chk_res_subtype_scheme
  CHECK (resolution_subtype_id IS NULL OR fn_validate_category_scheme(resolution_subtype_id, 'resolution_subtype'));

-- ─── core.agreement ───
ALTER TABLE core.agreement
  DROP CONSTRAINT IF EXISTS chk_agreement_cgr_outcome_scheme,
  ADD CONSTRAINT chk_agreement_cgr_outcome_scheme
  CHECK (cgr_outcome_id IS NULL OR fn_validate_category_scheme(cgr_outcome_id, 'cgr_outcome'));

-- ─── core.agreement_installment ───
ALTER TABLE core.agreement_installment
  DROP CONSTRAINT IF EXISTS chk_payment_status_scheme,
  ADD CONSTRAINT chk_payment_status_scheme
  CHECK (payment_status_id IS NULL OR fn_validate_category_scheme(payment_status_id, 'payment_status'));

-- ─── core.committee ───
ALTER TABLE core.committee
  DROP CONSTRAINT IF EXISTS chk_committee_type_scheme,
  ADD CONSTRAINT chk_committee_type_scheme
  CHECK (committee_type_id IS NULL OR fn_validate_category_scheme(committee_type_id, 'committee_type'));

-- ─── core.committee_member ───
ALTER TABLE core.committee_member
  DROP CONSTRAINT IF EXISTS chk_role_in_committee_scheme,
  ADD CONSTRAINT chk_role_in_committee_scheme
  CHECK (role_in_committee_id IS NULL OR fn_validate_category_scheme(role_in_committee_id, 'role_in_committee'));

-- ─── core.session ───
ALTER TABLE core.session
  DROP CONSTRAINT IF EXISTS chk_session_type_scheme,
  ADD CONSTRAINT chk_session_type_scheme
  CHECK (session_type_id IS NULL OR fn_validate_category_scheme(session_type_id, 'session_type'));

-- ─── core.alert ───
ALTER TABLE core.alert
  DROP CONSTRAINT IF EXISTS chk_alert_type_scheme,
  ADD CONSTRAINT chk_alert_type_scheme
  CHECK (alert_type_id IS NULL OR fn_validate_category_scheme(alert_type_id, 'alert_type'));

-- ─── core.legal_document ───
ALTER TABLE core.legal_document
  DROP CONSTRAINT IF EXISTS chk_doc_type_scheme,
  ADD CONSTRAINT chk_doc_type_scheme
  CHECK (doc_type_id IS NULL OR fn_validate_category_scheme(doc_type_id, 'document_type'));

-- ─── core.electronic_file ─── SKIP: document_type_id column not materialized

-- ─── core.rendition ───
ALTER TABLE core.rendition
  DROP CONSTRAINT IF EXISTS chk_rendition_state_scheme,
  ADD CONSTRAINT chk_rendition_state_scheme
  CHECK (state_id IS NULL OR fn_validate_category_scheme(state_id, 'rendition_state'));

-- ─── core.dgi_indicator_snapshot ───
ALTER TABLE core.dgi_indicator_snapshot
  DROP CONSTRAINT IF EXISTS chk_dgi_signal_scheme,
  ADD CONSTRAINT chk_dgi_signal_scheme
  CHECK (signal_id IS NULL OR fn_validate_category_scheme(signal_id, 'dgi_signal'));

-- ─── core.commitment_history ───
ALTER TABLE core.commitment_history
  DROP CONSTRAINT IF EXISTS chk_commit_hist_prev_scheme,
  ADD CONSTRAINT chk_commit_hist_prev_scheme
  CHECK (previous_state_id IS NULL OR fn_validate_category_scheme(previous_state_id, 'commitment_state'));

ALTER TABLE core.commitment_history
  DROP CONSTRAINT IF EXISTS chk_commit_hist_new_scheme,
  ADD CONSTRAINT chk_commit_hist_new_scheme
  CHECK (new_state_id IS NULL OR fn_validate_category_scheme(new_state_id, 'commitment_state'));

-- ─── core.work_item_history ─── SKIP: table not materialized in DB

-- ─── txn.event ───
ALTER TABLE txn.event
  DROP CONSTRAINT IF EXISTS chk_event_type_scheme,
  ADD CONSTRAINT chk_event_type_scheme
  CHECK (event_type_id IS NULL OR fn_validate_category_scheme(event_type_id, 'event_type'));

-- ─── txn.magnitude ─── SKIP: aspect_id uses 2 schemes ('aspect' + 'magnitude_aspect')
-- Requires data consolidation before constraint can be applied (4,449 rows affected)


-- ═══════════════════════════════════════════════════════════════════════════
-- R-02: EXTENSIÓN DE fn_validate_ipr_schemes (+5 columnas)
-- ═══════════════════════════════════════════════════════════════════════════
-- Columnas previamente validadas por trigger: mcd_phase_id, status_id,
-- mechanism_id, budget_subtitle_id, alert_level_id
-- Columnas añadidas: ipr_type_id, funding_source_id, investment_sector_id,
-- fund_category_id, resolution_type_id

CREATE OR REPLACE FUNCTION fn_validate_ipr_schemes()
RETURNS TRIGGER AS $$
BEGIN
    -- ── Columnas existentes ──

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

    -- ── Columnas añadidas (R-02) ──

    IF NEW.ipr_type_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.ipr_type_id, 'ipr_type') THEN
            RAISE EXCEPTION 'ipr_type_id debe pertenecer al scheme "ipr_type"';
        END IF;
    END IF;

    IF NEW.funding_source_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.funding_source_id, 'funding_source') THEN
            RAISE EXCEPTION 'funding_source_id debe pertenecer al scheme "funding_source"';
        END IF;
    END IF;

    IF NEW.investment_sector_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.investment_sector_id, 'investment_sector') THEN
            RAISE EXCEPTION 'investment_sector_id debe pertenecer al scheme "investment_sector"';
        END IF;
    END IF;

    IF NEW.fund_category_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.fund_category_id, 'fondo_8pct') THEN
            RAISE EXCEPTION 'fund_category_id debe pertenecer al scheme "fondo_8pct"';
        END IF;
    END IF;

    IF NEW.resolution_type_id IS NOT NULL THEN
        IF NOT fn_validate_category_scheme(NEW.resolution_type_id, 'resolution_type') THEN
            RAISE EXCEPTION 'resolution_type_id debe pertenecer al scheme "resolution_type"';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_validate_ipr_schemes() IS
'R-01/R-02 FIX: Valida 10 FK→ref.category en core.ipr (5 originales + 5 añadidos en migración categorical_univocity)';

-- El trigger trg_ipr_validate_schemes ya existe en goreos_triggers_remediation.sql
-- y se reutiliza automáticamente con la función actualizada.


-- ═══════════════════════════════════════════════════════════════════════════
-- DOCUMENTACIÓN INLINE — HALLAZGOS CERRADOS
-- ═══════════════════════════════════════════════════════════════════════════
--
-- B-01 (MEDIUM): trg_agreement_state_transition YA EXISTE
--   → Creado en goreos_migration_wave1_trigger_fix.sql (líneas 88-91)
--   → Recreado en goreos_triggers_remediation.sql (líneas 44-51)
--   → No requiere acción adicional.
--
-- S-02 (LOW): ref.operational_commitment_type NO es redundante
--   → Tabla dedicada (tiene default_days INT), distinta de ref.category
--     scheme='commitment_type' que contiene ESTADOS (PENDIENTE, EN_PROGRESO...)
--   → Types ≠ States: dominios semánticos distintos.
--
-- D-02 (LOW): ADR No-ORM
--   → Ya documentado en docs/adr/ADR-002-raw-sql.md (2026-03-03)
--
-- R-03 (LOW): Plan de consolidación de triggers
--   → Actualmente hay 4 funciones fn_validate_*_schemes() (ipr, work_item,
--     agreement, commitment). Un refactor futuro podría consolidarlas en
--     fn_validate_entity_schemes(TG_TABLE_NAME) con un mapping interno.
--   → Prioridad baja — las funciones separadas funcionan correctamente.
--
-- ═══════════════════════════════════════════════════════════════════════════

COMMIT;

DO $$ BEGIN
    RAISE NOTICE 'GORE_OS Migración categorical_univocity aplicada: 31 CHECK constraints + 1 data fix + fn_validate_ipr_schemes extendida (10 columnas)';
END $$;
