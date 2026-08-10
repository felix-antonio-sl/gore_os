-- =============================================================================
-- GORE_OS — autoridad PostgreSQL del ciclo de oportunidades de mejora DGI
-- =============================================================================

BEGIN;

CREATE OR REPLACE FUNCTION core.trg_dgi_opportunity_status_transition_fn()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status IS NOT DISTINCT FROM OLD.status THEN
        RETURN NEW;
    END IF;

    IF NOT (
        (OLD.status = 'PROPUESTA' AND NEW.status IN ('VALIDADA', 'DESCARTADA'))
        OR (OLD.status = 'VALIDADA' AND NEW.status IN ('EN_EJECUCION', 'DESCARTADA'))
        OR (OLD.status = 'EN_EJECUCION' AND NEW.status = 'IMPLEMENTADA')
    ) THEN
        RAISE EXCEPTION USING
            ERRCODE = '23514',
            MESSAGE = format(
                'Transición de oportunidad inválida: %s → %s',
                OLD.status,
                NEW.status
            );
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_dgi_opportunity_status_transition
    ON core.dgi_improvement_opportunity;
CREATE TRIGGER trg_dgi_opportunity_status_transition
BEFORE UPDATE OF status ON core.dgi_improvement_opportunity
FOR EACH ROW
EXECUTE FUNCTION core.trg_dgi_opportunity_status_transition_fn();

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_opportunity_fsm.sql', 'codex')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
