-- =============================================================================
-- GORE_OS — estado DB-authoritative de acuerdos de sesión
-- =============================================================================

BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM ref.category
        WHERE scheme = 'commitment_state'
          AND code = 'PENDIENTE'
    ) THEN
        RAISE EXCEPTION
            'Cannot enforce session agreement status: commitment_state/PENDIENTE is missing';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM core.session_agreement sa
        JOIN ref.category c ON c.id = sa.status_id
        WHERE c.scheme <> 'commitment_state'
    ) THEN
        RAISE EXCEPTION
            'Cannot enforce session agreement status: existing status requires adjudication';
    END IF;
END $$;

UPDATE core.session_agreement
SET status_id = (
    SELECT id
    FROM ref.category
    WHERE scheme = 'commitment_state'
      AND code = 'PENDIENTE'
)
WHERE status_id IS NULL;

ALTER TABLE core.session_agreement
    ALTER COLUMN status_id SET NOT NULL;

ALTER TABLE core.session_agreement
    DROP CONSTRAINT IF EXISTS chk_session_agreement_status_scheme;
ALTER TABLE core.session_agreement
    ADD CONSTRAINT chk_session_agreement_status_scheme
    CHECK (public.fn_validate_category_scheme(status_id, 'commitment_state'));

CREATE OR REPLACE FUNCTION core.trg_session_agreement_status_default_fn()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status_id IS NULL THEN
        SELECT id
        INTO NEW.status_id
        FROM ref.category
        WHERE scheme = 'commitment_state'
          AND code = 'PENDIENTE';

        IF NEW.status_id IS NULL THEN
            RAISE EXCEPTION USING
                ERRCODE = '23514',
                MESSAGE = 'commitment_state/PENDIENTE is required for session agreements';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_session_agreement_status_default
    ON core.session_agreement;
CREATE TRIGGER trg_session_agreement_status_default
BEFORE INSERT ON core.session_agreement
FOR EACH ROW
EXECUTE FUNCTION core.trg_session_agreement_status_default_fn();

DROP TRIGGER IF EXISTS trg_session_agreement_status_transition
    ON core.session_agreement;
CREATE TRIGGER trg_session_agreement_status_transition
BEFORE UPDATE OF status_id ON core.session_agreement
FOR EACH ROW
EXECUTE FUNCTION public.fn_validate_state_transition('status_id');

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_session_agreement_status_authority.sql', 'codex')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
