-- =============================================================================
-- ROLLBACK: FSM Enforcement
-- =============================================================================

BEGIN;

-- Drop triggers
DROP TRIGGER IF EXISTS trg_commitment_history ON core.operational_commitment;
DROP TRIGGER IF EXISTS trg_commitment_state_transition ON core.operational_commitment;
DROP TRIGGER IF EXISTS trg_rendition_state_transition ON core.rendition;
DROP TRIGGER IF EXISTS trg_problem_state_transition ON core.ipr_problem;

-- Clear valid_transitions for rendition_state
UPDATE ref.category SET valid_transitions = NULL
WHERE scheme = 'rendition_state';

-- Clear valid_transitions for problem_state
UPDATE ref.category SET valid_transitions = NULL
WHERE scheme = 'problem_state';

-- Remove migration record
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_fsm_enforcement.sql';

COMMIT;
