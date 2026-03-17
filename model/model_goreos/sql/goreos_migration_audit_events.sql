-- Migration: Add auth audit event_type codes
-- Required by: auth.py record_event() calls for login/password tracking

BEGIN;

-- New event_type codes for authentication audit trail
INSERT INTO ref.category (scheme, code, label, description, sort_order)
VALUES
    ('event_type', 'LOGIN', 'Login Exitoso', 'Inicio de sesión exitoso', 20),
    ('event_type', 'LOGIN_FAILED', 'Login Fallido', 'Intento de inicio de sesión fallido', 21),
    ('event_type', 'PASSWORD_CHANGED', 'Cambio de Contraseña', 'Contraseña de usuario modificada', 22)
ON CONFLICT (scheme, code) DO NOTHING;

-- Register migration
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_audit_events.sql', md5('audit_events_login_password'), 'claude')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
