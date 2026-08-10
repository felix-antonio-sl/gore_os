-- =============================================================================
-- GORE_OS — testigos obligatorios para hitos presupuestarios completados
-- =============================================================================

BEGIN;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM core.budget_cycle_tracking
        WHERE status = 'COMPLETADO'
          AND (completed_at IS NULL OR completed_by_id IS NULL)
    ) THEN
        RAISE EXCEPTION
            'Cannot enforce budget completion witnesses: completed milestone requires adjudication';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM core.budget_cycle_tracking
        WHERE status <> 'COMPLETADO'
          AND (completed_at IS NOT NULL OR completed_by_id IS NOT NULL)
    ) THEN
        RAISE EXCEPTION
            'Cannot enforce budget completion witnesses: stale witness requires adjudication';
    END IF;
END $$;

ALTER TABLE core.budget_cycle_tracking
    DROP CONSTRAINT IF EXISTS chk_budget_cycle_completion_witness;
ALTER TABLE core.budget_cycle_tracking
    ADD CONSTRAINT chk_budget_cycle_completion_witness
    CHECK (
        (status = 'COMPLETADO'
         AND completed_at IS NOT NULL
         AND completed_by_id IS NOT NULL)
        OR
        (status <> 'COMPLETADO'
         AND completed_at IS NULL
         AND completed_by_id IS NULL)
    );

CREATE OR REPLACE FUNCTION core.trg_budget_cycle_completion_guard_fn()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status = 'COMPLETADO' THEN
        IF NEW.completed_at IS NULL OR NEW.completed_by_id IS NULL THEN
            RAISE EXCEPTION USING
                ERRCODE = '23514',
                MESSAGE = 'COMPLETADO requires completed_at and completed_by_id';
        END IF;
    ELSIF NEW.completed_at IS NOT NULL OR NEW.completed_by_id IS NOT NULL THEN
        RAISE EXCEPTION USING
            ERRCODE = '23514',
            MESSAGE = 'non-completed budget milestone must clear completion witnesses';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_budget_cycle_completion_guard
    ON core.budget_cycle_tracking;
CREATE TRIGGER trg_budget_cycle_completion_guard
BEFORE INSERT OR UPDATE ON core.budget_cycle_tracking
FOR EACH ROW
EXECUTE FUNCTION core.trg_budget_cycle_completion_guard_fn();

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_budget_cycle_completion_authority.sql', 'codex')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
