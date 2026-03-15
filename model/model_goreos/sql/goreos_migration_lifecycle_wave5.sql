-- goreos_migration_lifecycle_wave5.sql
-- Wave 5: Role-based transition permissions
-- Pullback categórico: Permission = Phase_Boundary ×_Track Role
--
-- Changes:
--   5A. role_permissions JSONB on financing_track (track overrides)
--   5B. SUPERVISOR_GORE party role
--   5C. Seed FRIL track overrides (3 boundary keys)
--   5D. FRIL vigencia 90 days in sla_days

BEGIN;

-- 5A. Add role_permissions column to financing_track
ALTER TABLE core.financing_track
ADD COLUMN IF NOT EXISTS role_permissions JSONB DEFAULT '{}'::jsonb NOT NULL;

COMMENT ON COLUMN core.financing_track.role_permissions IS
    'Track-specific role overrides per boundary key. '
    'Keys: boundary names (e.g. register_eval_result). '
    'Values: role code arrays. Empty {} means use universal defaults.';

-- 5B. SUPERVISOR_GORE party role
INSERT INTO ref.category (scheme, code, label, description, sort_order)
VALUES ('ipr_party_role', 'SUPERVISOR_GORE', 'Supervisor GORE',
        'Responsable de supervisión técnica GORE durante ejecución — aprueba estados de pago y autoriza modificaciones de obra',
        11)
ON CONFLICT (scheme, code) DO NOTHING;

-- 5C. Seed FRIL track overrides
-- FRIL: JEFE_DIVISION can register eval results (DIPIR evaluates internally)
-- FRIL: GOBERNADOR signs financing resolution (formalization)
-- FRIL: Licitación managed by municipality, GORE only registers (no JEFE_DIVISION)
UPDATE core.financing_track
SET role_permissions = '{
    "register_eval_result": ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "ANALISTA", "JEFE_DIVISION"],
    "formalization": ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "JEFE_DIVISION"],
    "licitacion_flow": ["ADMIN_SISTEMA", "ADMIN_REGIONAL", "GOBERNADOR", "ANALISTA"]
}'::jsonb
WHERE code = 'FRIL';

-- 5D. FRIL vigencia: 90 days for evaluation result validity
-- (SNI uses rs_validity_years=3; FRIL has shorter window)
UPDATE core.financing_track
SET sla_days = sla_days || '{"rs_validity_days": 90}'::jsonb
WHERE code = 'FRIL';

-- Schema migration tracking
INSERT INTO core.schema_migration (filename, applied_at)
VALUES ('goreos_migration_lifecycle_wave5.sql', NOW())
ON CONFLICT (filename) DO NOTHING;

COMMIT;
