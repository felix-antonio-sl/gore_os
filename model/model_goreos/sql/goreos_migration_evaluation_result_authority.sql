-- =============================================================================
-- GORE_OS — result_id como autoridad única del dictamen de evaluación
-- =============================================================================

BEGIN;

-- Preserve legacy rows that only populated the denormalized code. Unknown codes
-- require adjudication instead of being discarded or guessed.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM core.evaluation_assignment ea
        LEFT JOIN ref.category c
          ON c.scheme = 'evaluation_result'
         AND c.code = ea.result_code
        WHERE ea.result_id IS NULL
          AND ea.result_code IS NOT NULL
          AND c.id IS NULL
    ) THEN
        RAISE EXCEPTION
            'Cannot enforce evaluation result authority: unknown legacy result_code requires adjudication';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM core.evaluation_assignment ea
        JOIN ref.category c ON c.id = ea.result_id
        WHERE c.scheme <> 'evaluation_result'
    ) THEN
        RAISE EXCEPTION
            'Cannot enforce evaluation result authority: result_id outside evaluation_result requires adjudication';
    END IF;
END $$;

UPDATE core.evaluation_assignment ea
SET result_id = c.id
FROM ref.category c
WHERE ea.result_id IS NULL
  AND ea.result_code IS NOT NULL
  AND c.scheme = 'evaluation_result'
  AND c.code = ea.result_code;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM core.evaluation_assignment
        WHERE completed_at IS NOT NULL
          AND result_id IS NULL
    ) THEN
        RAISE EXCEPTION
            'Cannot enforce evaluation result authority: completed evaluation without result requires adjudication';
    END IF;
END $$;

UPDATE core.evaluation_assignment ea
SET result_code = c.code
FROM ref.category c
WHERE c.id = ea.result_id
  AND ea.result_code IS DISTINCT FROM c.code;

ALTER TABLE core.evaluation_assignment
    DROP CONSTRAINT IF EXISTS chk_evaluation_result_scheme;
ALTER TABLE core.evaluation_assignment
    ADD CONSTRAINT chk_evaluation_result_scheme
    CHECK (result_id IS NULL OR public.fn_validate_category_scheme(result_id, 'evaluation_result'));

ALTER TABLE core.evaluation_assignment
    DROP CONSTRAINT IF EXISTS chk_evaluation_completion_result;
ALTER TABLE core.evaluation_assignment
    ADD CONSTRAINT chk_evaluation_completion_result
    CHECK (completed_at IS NULL OR result_id IS NOT NULL);

ALTER TABLE core.evaluation_assignment
    DROP CONSTRAINT IF EXISTS chk_evaluation_result_code_presence;
ALTER TABLE core.evaluation_assignment
    ADD CONSTRAINT chk_evaluation_result_code_presence
    CHECK ((result_id IS NULL) = (result_code IS NULL));

CREATE OR REPLACE FUNCTION core.trg_evaluation_assignment_result_guard_fn()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    canonical_result_code VARCHAR(10);
BEGIN
    IF NEW.completed_at IS NOT NULL AND NEW.result_id IS NULL THEN
        RAISE EXCEPTION USING
            ERRCODE = '23514',
            MESSAGE = 'core.evaluation_assignment cannot complete without result_id';
    END IF;

    IF NEW.result_id IS NULL THEN
        NEW.result_code := NULL;
        RETURN NEW;
    END IF;

    SELECT code
    INTO canonical_result_code
    FROM ref.category
    WHERE id = NEW.result_id
      AND scheme = 'evaluation_result';

    IF NOT FOUND THEN
        RAISE EXCEPTION USING
            ERRCODE = '23514',
            MESSAGE = 'core.evaluation_assignment result_id must belong to evaluation_result';
    END IF;

    NEW.result_code := canonical_result_code;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_evaluation_assignment_result_guard
    ON core.evaluation_assignment;
CREATE TRIGGER trg_evaluation_assignment_result_guard
BEFORE INSERT OR UPDATE ON core.evaluation_assignment
FOR EACH ROW
EXECUTE FUNCTION core.trg_evaluation_assignment_result_guard_fn();

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_evaluation_result_authority.sql', 'codex')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
