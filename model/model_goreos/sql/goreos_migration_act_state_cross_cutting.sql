-- Make ANULADO reachable from every non-terminal administrative-act state.
-- The database remains the sole authority for allowed state transitions.

BEGIN;

UPDATE ref.category
SET valid_transitions = COALESCE(valid_transitions, '[]'::jsonb) || '["ANULADO"]'::jsonb
WHERE scheme = 'act_state'
  AND code NOT IN ('TOMADO_RAZON', 'RECHAZADO_CGR', 'ANULADO')
  AND NOT COALESCE(valid_transitions, '[]'::jsonb) ? 'ANULADO';

UPDATE ref.category
SET valid_transitions = '[]'::jsonb
WHERE scheme = 'act_state'
  AND code IN ('TOMADO_RAZON', 'RECHAZADO_CGR', 'ANULADO');

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM ref.category
        WHERE scheme = 'act_state'
          AND code NOT IN ('TOMADO_RAZON', 'RECHAZADO_CGR', 'ANULADO')
          AND NOT COALESCE(valid_transitions, '[]'::jsonb) ? 'ANULADO'
    ) THEN
        RAISE EXCEPTION 'act_state ANULADO must be reachable from every non-terminal state';
    END IF;
END $$;

COMMIT;
