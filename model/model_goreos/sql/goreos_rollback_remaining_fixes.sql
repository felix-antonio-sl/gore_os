-- =============================================================================
-- ROLLBACK: Remaining Fixes
-- =============================================================================

BEGIN;

-- Part 3: Drop FSM triggers
DROP TRIGGER IF EXISTS trg_dgi_initiative_status_transition ON core.dgi_initiative;
DROP TRIGGER IF EXISTS trg_dgi_report_status_transition ON core.dgi_report;
DROP TRIGGER IF EXISTS trg_dgi_bpmn_status_transition ON core.dgi_bpmn_model;
DROP TRIGGER IF EXISTS trg_dgi_session_status_transition ON core.dgi_committee_session;
DROP TRIGGER IF EXISTS trg_budget_commitment_status_transition ON core.budget_commitment;
DROP TRIGGER IF EXISTS trg_risk_status_transition ON core.risk;

-- Clear valid_transitions for newly populated schemes
UPDATE ref.category SET valid_transitions = NULL WHERE scheme IN (
  'dgi_initiative_status', 'dgi_report_status', 'dgi_bpmn_status',
  'dgi_session_status', 'dgi_alert_status', 'budget_commitment_status',
  'risk_status'
);

-- Part 2: Restore original UNIQUE constraint on ipr_party
DROP INDEX IF EXISTS core.uq_ipr_party_role;
ALTER TABLE core.ipr_party
  ADD CONSTRAINT uq_ipr_party_role UNIQUE (ipr_id, organization_id, party_role_id);

-- Part 1: Drop CHECK constraints
ALTER TABLE core.vehicle DROP CONSTRAINT IF EXISTS chk_vehicle_type_scheme;
ALTER TABLE core.vehicle DROP CONSTRAINT IF EXISTS chk_fuel_type_scheme;
ALTER TABLE core.risk DROP CONSTRAINT IF EXISTS chk_risk_probability_scheme;
ALTER TABLE core.risk DROP CONSTRAINT IF EXISTS chk_risk_status_scheme;
ALTER TABLE core.inventory_item DROP CONSTRAINT IF EXISTS chk_asset_status_scheme;
ALTER TABLE core.planning_instrument DROP CONSTRAINT IF EXISTS chk_instrument_type_scheme;

-- Delete new schemes
DELETE FROM ref.category WHERE scheme IN (
  'vehicle_type', 'fuel_type', 'risk_probability', 'risk_status',
  'asset_status', 'instrument_type'
);

-- Delete CANCELADA if added to dgi_session_status
DELETE FROM ref.category WHERE scheme = 'dgi_session_status' AND code = 'CANCELADA';

-- Remove migration record
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_remaining_fixes.sql';

COMMIT;
