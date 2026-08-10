-- =============================================================================
-- GORE_OS — core.session como autoridad única del lifecycle de reuniones
-- =============================================================================

BEGIN;

-- Preserve the most complete valid timeline before enforcing a single source.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM core.session s
        LEFT JOIN core.crisis_meeting cm ON cm.session_id = s.id
        WHERE COALESCE(s.ended_at, cm.finished_at) IS NOT NULL
          AND (
              COALESCE(s.started_at, cm.started_at) IS NULL
              OR COALESCE(s.ended_at, cm.finished_at)
                 < COALESCE(s.started_at, cm.started_at)
          )
    ) THEN
        RAISE EXCEPTION
            'Cannot enforce session lifecycle: existing timestamps require adjudication';
    END IF;
END $$;

UPDATE core.session s
SET started_at = COALESCE(s.started_at, cm.started_at),
    ended_at = COALESCE(s.ended_at, cm.finished_at)
FROM core.crisis_meeting cm
WHERE cm.session_id = s.id
  AND (
      s.started_at IS DISTINCT FROM COALESCE(s.started_at, cm.started_at)
      OR s.ended_at IS DISTINCT FROM COALESCE(s.ended_at, cm.finished_at)
  );

UPDATE core.crisis_meeting cm
SET started_at = s.started_at,
    finished_at = s.ended_at,
    updated_at = NOW()
FROM core.session s
WHERE s.id = cm.session_id
  AND (
      cm.started_at IS DISTINCT FROM s.started_at
      OR cm.finished_at IS DISTINCT FROM s.ended_at
  );

ALTER TABLE core.session
    DROP CONSTRAINT IF EXISTS chk_session_lifecycle_order;
ALTER TABLE core.session
    ADD CONSTRAINT chk_session_lifecycle_order
    CHECK (ended_at IS NULL OR (started_at IS NOT NULL AND ended_at >= started_at));

ALTER TABLE core.crisis_meeting
    DROP CONSTRAINT IF EXISTS chk_crisis_meeting_lifecycle_order;
ALTER TABLE core.crisis_meeting
    ADD CONSTRAINT chk_crisis_meeting_lifecycle_order
    CHECK (finished_at IS NULL OR (started_at IS NOT NULL AND finished_at >= started_at));

CREATE OR REPLACE FUNCTION core.trg_session_lifecycle_guard_fn()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.ended_at IS NOT NULL AND NEW.started_at IS NULL THEN
        RAISE EXCEPTION USING
            ERRCODE = '23514',
            MESSAGE = 'core.session cannot finish before it starts';
    END IF;

    IF NEW.ended_at IS NOT NULL AND NEW.ended_at < NEW.started_at THEN
        RAISE EXCEPTION USING
            ERRCODE = '23514',
            MESSAGE = 'core.session ended_at cannot precede started_at';
    END IF;

    IF TG_OP = 'UPDATE' THEN
        IF OLD.started_at IS NOT NULL
           AND NEW.started_at IS DISTINCT FROM OLD.started_at THEN
            RAISE EXCEPTION USING
                ERRCODE = '23514',
                MESSAGE = 'core.session started_at is immutable once set';
        END IF;

        IF OLD.ended_at IS NOT NULL
           AND NEW.ended_at IS DISTINCT FROM OLD.ended_at THEN
            RAISE EXCEPTION USING
                ERRCODE = '23514',
                MESSAGE = 'core.session ended_at is immutable once set';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION core.trg_session_lifecycle_sync_fn()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.started_at IS DISTINCT FROM OLD.started_at
       OR NEW.ended_at IS DISTINCT FROM OLD.ended_at THEN
        UPDATE core.crisis_meeting
        SET started_at = NEW.started_at,
            finished_at = NEW.ended_at,
            updated_at = NOW()
        WHERE session_id = NEW.id
          AND (started_at IS DISTINCT FROM NEW.started_at
               OR finished_at IS DISTINCT FROM NEW.ended_at);
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION core.trg_crisis_meeting_lifecycle_guard_fn()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    parent_started_at TIMESTAMPTZ;
    parent_ended_at TIMESTAMPTZ;
BEGIN
    SELECT started_at, ended_at
    INTO parent_started_at, parent_ended_at
    FROM core.session
    WHERE id = NEW.session_id;

    IF NOT FOUND THEN
        RETURN NEW;
    END IF;

    IF TG_OP = 'INSERT' THEN
        NEW.started_at := parent_started_at;
        NEW.finished_at := parent_ended_at;
        RETURN NEW;
    END IF;

    IF NEW.started_at IS DISTINCT FROM parent_started_at
       OR NEW.finished_at IS DISTINCT FROM parent_ended_at THEN
        RAISE EXCEPTION USING
            ERRCODE = '23514',
            MESSAGE = 'core.crisis_meeting lifecycle is derived from core.session';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_session_lifecycle_guard ON core.session;
CREATE TRIGGER trg_session_lifecycle_guard
BEFORE INSERT OR UPDATE ON core.session
FOR EACH ROW
EXECUTE FUNCTION core.trg_session_lifecycle_guard_fn();

DROP TRIGGER IF EXISTS trg_session_lifecycle_sync ON core.session;
CREATE TRIGGER trg_session_lifecycle_sync
AFTER UPDATE OF started_at, ended_at ON core.session
FOR EACH ROW
EXECUTE FUNCTION core.trg_session_lifecycle_sync_fn();

DROP TRIGGER IF EXISTS trg_crisis_meeting_lifecycle_guard ON core.crisis_meeting;
CREATE TRIGGER trg_crisis_meeting_lifecycle_guard
BEFORE INSERT OR UPDATE ON core.crisis_meeting
FOR EACH ROW
EXECUTE FUNCTION core.trg_crisis_meeting_lifecycle_guard_fn();

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_session_lifecycle_authority.sql', 'codex')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
