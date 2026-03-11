-- =============================================================================
-- MIGRACIÓN: FSM Enforcement — Coalgebras con invariantes DB
-- =============================================================================
-- Fecha: 2026-03-10
-- Descripción: Cierra las brechas de enforcement de máquinas de estado:
--
--   1. Poblar valid_transitions para rendition_state (8 códigos)
--   2. Poblar valid_transitions para problem_state (4 códigos)
--   3. Crear trigger trg_commitment_history (función existe, trigger faltante)
--   4. Crear trigger trg_commitment_state_transition (valid_transitions existe)
--   5. Crear trigger trg_rendition_state_transition (tras poblar transitions)
--   6. Crear trigger trg_problem_state_transition (tras poblar transitions)
--
-- Patrón coalgebraico: c: State → F(State)
--   valid_transitions JSONB define F(s) = conjunto de estados alcanzables
--   fn_validate_state_transition verifica que NEW.state ∈ F(OLD.state)
--
-- Pre-requisito: fn_validate_state_transition y fn_commitment_history existen
-- =============================================================================

BEGIN;

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. RENDITION STATE: Poblar valid_transitions desde _RENDICION_TRANSITIONS
--    Fuente: dgi_data.py línea 1304-1311
-- ─────────────────────────────────────────────────────────────────────────────

UPDATE ref.category SET valid_transitions = '["EN_REVISION_RTF"]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'PENDIENTE';

UPDATE ref.category SET valid_transitions = '["OBSERVADA", "VISADA_RTF"]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'EN_REVISION_RTF';

UPDATE ref.category SET valid_transitions = '["EN_REVISION_UCR"]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'VISADA_RTF';

UPDATE ref.category SET valid_transitions = '["OBSERVADA", "APROBADA", "RECHAZADA"]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'EN_REVISION_UCR';

UPDATE ref.category SET valid_transitions = '["EN_REVISION_RTF"]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'OBSERVADA';

-- Terminal states
UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'APROBADA';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'RECHAZADA';

-- Deprecated state (sort_order=99): block all transitions
UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'rendition_state' AND code = 'EN_REVISION';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. PROBLEM STATE: Define FSM transitions
--    ABIERTO → EN_GESTION, CERRADO_SIN_RESOLVER
--    EN_GESTION → RESUELTO, CERRADO_SIN_RESOLVER
--    RESUELTO, CERRADO_SIN_RESOLVER → terminal
-- ─────────────────────────────────────────────────────────────────────────────

UPDATE ref.category SET valid_transitions = '["EN_GESTION", "RESUELTO", "CERRADO_SIN_RESOLVER"]'::jsonb
WHERE scheme = 'problem_state' AND code = 'ABIERTO';

UPDATE ref.category SET valid_transitions = '["RESUELTO", "CERRADO_SIN_RESOLVER"]'::jsonb
WHERE scheme = 'problem_state' AND code = 'EN_GESTION';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'problem_state' AND code = 'RESUELTO';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'problem_state' AND code = 'CERRADO_SIN_RESOLVER';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2b. COMMITMENT STATE: Relax transitions to match endpoint behavior
--     /completar allows PENDIENTE→COMPLETADO (quick-complete)
--     /devolver allows late VENCIDO→COMPLETADO recovery
-- ─────────────────────────────────────────────────────────────────────────────

UPDATE ref.category SET valid_transitions = '["EN_PROGRESO", "COMPLETADO", "CANCELADO", "VENCIDO"]'::jsonb
WHERE scheme = 'commitment_state' AND code = 'PENDIENTE';

UPDATE ref.category SET valid_transitions = '["EN_PROGRESO", "COMPLETADO"]'::jsonb
WHERE scheme = 'commitment_state' AND code = 'VENCIDO';

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. COMMITMENT HISTORY TRIGGER: Función existe, trigger nunca creado
--    fn_commitment_history() inserta en core.commitment_history cuando
--    state_id cambia. Bug: 0 rows en commitment_history actualmente.
-- ─────────────────────────────────────────────────────────────────────────────

DROP TRIGGER IF EXISTS trg_commitment_history ON core.operational_commitment;

CREATE TRIGGER trg_commitment_history
    BEFORE UPDATE ON core.operational_commitment
    FOR EACH ROW
    EXECUTE FUNCTION fn_commitment_history();

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. COMMITMENT STATE TRANSITION TRIGGER
--    valid_transitions ya definidos en ref.category para commitment_state
-- ─────────────────────────────────────────────────────────────────────────────

DROP TRIGGER IF EXISTS trg_commitment_state_transition ON core.operational_commitment;

CREATE TRIGGER trg_commitment_state_transition
    BEFORE UPDATE ON core.operational_commitment
    FOR EACH ROW
    EXECUTE FUNCTION fn_validate_state_transition('state_id');

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. RENDITION STATE TRANSITION TRIGGER
--    valid_transitions recién poblados arriba
-- ─────────────────────────────────────────────────────────────────────────────

DROP TRIGGER IF EXISTS trg_rendition_state_transition ON core.rendition;

CREATE TRIGGER trg_rendition_state_transition
    BEFORE UPDATE ON core.rendition
    FOR EACH ROW
    EXECUTE FUNCTION fn_validate_state_transition('state_id');

-- ─────────────────────────────────────────────────────────────────────────────
-- 6. PROBLEM STATE TRANSITION TRIGGER
--    valid_transitions recién poblados arriba
-- ─────────────────────────────────────────────────────────────────────────────

DROP TRIGGER IF EXISTS trg_problem_state_transition ON core.ipr_problem;

CREATE TRIGGER trg_problem_state_transition
    BEFORE UPDATE ON core.ipr_problem
    FOR EACH ROW
    EXECUTE FUNCTION fn_validate_state_transition('state_id');

-- ─────────────────────────────────────────────────────────────────────────────
-- REGISTRO
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO core.schema_migration (filename, applied_by)
VALUES (
  'goreos_migration_fsm_enforcement.sql',
  'claude-categorical-audit'
)
ON CONFLICT DO NOTHING;

COMMIT;
