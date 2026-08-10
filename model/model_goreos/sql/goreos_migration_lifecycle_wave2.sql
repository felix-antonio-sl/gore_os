-- ============================================================================
-- Migration: Lifecycle Wave 2 — IPR Modifications + Report Periodicity
-- Date: 2026-03-11
-- Description:
--   2A. New table: core.ipr_modification (formal change requests during F4)
--   2B. New schemes: modification_type (5 codes), modification_status (4 codes FSM)
--   2C. CHECK constraints + FSM trigger
--   2D. Report periodicity: sla_days.report_frequency_days on financing_track
-- ============================================================================

BEGIN;

-- ============================================================================
-- 2A. Schemes
-- ============================================================================

-- modification_type: 5 types of formal IPR modifications
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
    ('modification_type', 'PRESUPUESTO', 'Presupuesto', 'Cambio en monto o distribución presupuestaria', 1),
    ('modification_type', 'PLAZO', 'Plazo', 'Extensión o reducción de plazo de ejecución', 2),
    ('modification_type', 'ALCANCE', 'Alcance', 'Cambio en alcance técnico o geográfico', 3),
    ('modification_type', 'EJECUTOR', 'Ejecutor', 'Cambio de entidad ejecutora', 4),
    ('modification_type', 'TECNICO', 'Técnico', 'Modificación técnica de especificaciones', 5)
ON CONFLICT (scheme, code) DO NOTHING;

-- modification_status: FSM with 4 states
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
    ('modification_status', 'SOLICITADA', 'Solicitada', 'Modificación ingresada, pendiente de revisión', 1),
    ('modification_status', 'EN_REVISION', 'En Revisión', 'Modificación siendo evaluada', 2),
    ('modification_status', 'APROBADA', 'Aprobada', 'Modificación aprobada', 3),
    ('modification_status', 'RECHAZADA', 'Rechazada', 'Modificación rechazada', 4)
ON CONFLICT (scheme, code) DO NOTHING;

-- Valid transitions for modification_status FSM
UPDATE ref.category SET valid_transitions = '["EN_REVISION", "RECHAZADA"]'::jsonb
WHERE scheme = 'modification_status' AND code = 'SOLICITADA';

UPDATE ref.category SET valid_transitions = '["APROBADA", "RECHAZADA"]'::jsonb
WHERE scheme = 'modification_status' AND code = 'EN_REVISION';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'modification_status' AND code IN ('APROBADA', 'RECHAZADA');

-- ============================================================================
-- 2B. Table: core.ipr_modification
-- ============================================================================

CREATE TABLE IF NOT EXISTS core.ipr_modification (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id UUID NOT NULL REFERENCES core.ipr(id),
    code VARCHAR(20) NOT NULL,
    modification_type_id UUID NOT NULL REFERENCES ref.category(id),
    status_id UUID NOT NULL REFERENCES ref.category(id),
    description TEXT NOT NULL,
    justification TEXT,
    field_changed VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    amount_delta NUMERIC(18, 2),
    requested_by_id UUID NOT NULL REFERENCES core."user"(id),
    approved_by_id UUID REFERENCES core."user"(id),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    CONSTRAINT chk_ipr_mod_type_scheme
        CHECK (fn_validate_category_scheme(modification_type_id, 'modification_type')),
    CONSTRAINT chk_ipr_mod_status_scheme
        CHECK (fn_validate_category_scheme(status_id, 'modification_status'))
);

CREATE INDEX IF NOT EXISTS idx_ipr_modification_ipr ON core.ipr_modification(ipr_id);
CREATE INDEX IF NOT EXISTS idx_ipr_modification_status ON core.ipr_modification(status_id);

-- FSM trigger for modification_status
DROP TRIGGER IF EXISTS trg_modification_state_transition ON core.ipr_modification;
CREATE TRIGGER trg_modification_state_transition
    BEFORE UPDATE OF status_id ON core.ipr_modification
    FOR EACH ROW
    EXECUTE FUNCTION fn_validate_state_transition('status_id');

-- ============================================================================
-- 2C. Report periodicity in sla_days
-- ============================================================================

UPDATE core.financing_track SET sla_days = COALESCE(sla_days, '{}'::jsonb) || '{"report_frequency_days": 30}'::jsonb
WHERE code = 'FRIL';

UPDATE core.financing_track SET sla_days = COALESCE(sla_days, '{}'::jsonb) || '{"report_frequency_days": 90}'::jsonb
WHERE code = 'SNI';

UPDATE core.financing_track SET sla_days = COALESCE(sla_days, '{}'::jsonb) || '{"report_frequency_days": 90}'::jsonb
WHERE code = 'C33';

UPDATE core.financing_track SET sla_days = COALESCE(sla_days, '{}'::jsonb) || '{"report_frequency_days": 30}'::jsonb
WHERE code = 'SUBV8';

UPDATE core.financing_track SET sla_days = COALESCE(sla_days, '{}'::jsonb) || '{"report_frequency_days": 60}'::jsonb
WHERE code = 'GLOSA06';

UPDATE core.financing_track SET sla_days = COALESCE(sla_days, '{}'::jsonb) || '{"report_frequency_days": 60}'::jsonb
WHERE code = 'TRANSFER';

UPDATE core.financing_track SET sla_days = COALESCE(sla_days, '{}'::jsonb) || '{"report_frequency_days": 30}'::jsonb
WHERE code = 'FRPD';

-- ============================================================================
-- Track migration
-- ============================================================================
INSERT INTO core.schema_migration (filename, applied_at)
VALUES ('goreos_migration_lifecycle_wave2.sql', NOW())
ON CONFLICT (filename) DO NOTHING;

COMMIT;
