-- Rollback Wave B: Coordinación Institucional, Escalamiento, Servicios, SLAs

BEGIN;

-- Drop triggers
DROP TRIGGER IF EXISTS trg_ar_decision_state_transition ON core.dgi_ar_decision;
DROP TRIGGER IF EXISTS trg_request_timing ON core.dgi_service_request;
DROP TRIGGER IF EXISTS trg_request_state_transition ON core.dgi_service_request;
DROP TRIGGER IF EXISTS trg_escalation_state_transition ON core.dgi_escalation;

-- Drop trigger functions
DROP FUNCTION IF EXISTS core.trg_ar_decision_state_transition_fn();
DROP FUNCTION IF EXISTS core.trg_request_timing_fn();
DROP FUNCTION IF EXISTS core.trg_request_state_transition_fn();
DROP FUNCTION IF EXISTS core.trg_escalation_state_transition_fn();

-- Drop tables (reverse dependency order)
DROP TABLE IF EXISTS core.dgi_division_interaction;
DROP TABLE IF EXISTS core.dgi_sla;
DROP TABLE IF EXISTS core.dgi_service_request;
DROP TABLE IF EXISTS core.dgi_service;
DROP TABLE IF EXISTS core.dgi_escalation;
DROP TABLE IF EXISTS core.dgi_ar_decision;

-- Remove schemes
DELETE FROM ref.category WHERE scheme IN (
    'dgi_ar_decision_type',
    'dgi_ar_decision_status',
    'dgi_escalation_level',
    'dgi_escalation_status',
    'dgi_service_status',
    'dgi_request_status',
    'dgi_interaction_type',
    'dgi_sla_product_type'
);

-- Remove migration tracking
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_wave_b.sql';

COMMIT;
