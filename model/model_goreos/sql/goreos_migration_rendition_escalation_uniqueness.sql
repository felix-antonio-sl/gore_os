-- =============================================================================
-- GORE_OS — idempotencia atómica de escalaciones SISREC abiertas
-- =============================================================================

BEGIN;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM core.rendition_escalation
        WHERE resolved_at IS NULL
        GROUP BY rendition_id, phase_id, escalation_level
        HAVING count(*) > 1
    ) THEN
        RAISE EXCEPTION
            'Cannot enforce open rendition escalation uniqueness: duplicates require adjudication';
    END IF;
END $$;

CREATE UNIQUE INDEX IF NOT EXISTS uq_rendition_escalation_open
    ON core.rendition_escalation (rendition_id, phase_id, escalation_level)
    WHERE resolved_at IS NULL;

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_rendition_escalation_uniqueness.sql', 'codex')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
