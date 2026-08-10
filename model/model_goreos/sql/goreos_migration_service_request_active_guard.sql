-- =============================================================================
-- GORE_OS — solo servicios activos admiten nuevas solicitudes
-- =============================================================================

BEGIN;

CREATE OR REPLACE FUNCTION core.trg_service_request_active_service_fn()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM core.dgi_service service
        JOIN ref.category service_status
          ON service_status.id = service.status_id
         AND service_status.scheme = 'dgi_service_status'
        WHERE service.id = NEW.service_id
          AND service.deleted_at IS NULL
          AND service_status.code = 'ACTIVO'
    ) THEN
        RAISE EXCEPTION USING
            ERRCODE = '23514',
            MESSAGE = 'core.dgi_service_request requires an active service';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_service_request_active_service
    ON core.dgi_service_request;
CREATE TRIGGER trg_service_request_active_service
BEFORE INSERT OR UPDATE OF service_id ON core.dgi_service_request
FOR EACH ROW
EXECUTE FUNCTION core.trg_service_request_active_service_fn();

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_service_request_active_guard.sql', 'codex')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
