-- Ciclo 23: SNI Level Configuration + SEREMI evaluator type
-- Creates core.sni_level_config table for SNI proporcionalidad rules (HΩ-11)
-- and adds SEREMI evaluator type code.

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. SNI Level Configuration table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS core.sni_level_config (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level_number INTEGER NOT NULL UNIQUE,
    label       TEXT NOT NULL,
    min_utm     NUMERIC(12,2) NOT NULL DEFAULT 0,
    max_utm     NUMERIC(12,2),  -- NULL means no upper bound
    evaluator_code TEXT NOT NULL,
    requires_external_eval BOOLEAN NOT NULL DEFAULT FALSE,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE core.sni_level_config IS 'SNI proporcionalidad: evaluation levels by project amount (HΩ-11)';

-- ---------------------------------------------------------------------------
-- 2. Seed 4 SNI levels
-- ---------------------------------------------------------------------------
INSERT INTO core.sni_level_config (level_number, label, min_utm, max_utm, evaluator_code, requires_external_eval)
VALUES
    (0, 'Nivel 0 — Evaluación GORE', 0, 1500, 'GORE_DAE', FALSE),
    (1, 'Nivel 1 — Evaluación SEREMI', 1500, 5000, 'SEREMI', TRUE),
    (2, 'Nivel 2 — Evaluación MDSF', 5000, 25000, 'MDSF', TRUE),
    (3, 'Nivel 3 — Evaluación MDSF (mega)', 25000, NULL, 'MDSF', TRUE)
ON CONFLICT (level_number) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 3. Add SEREMI evaluator type to ref.category
-- ---------------------------------------------------------------------------
INSERT INTO ref.category (scheme, code, label, sort_order)
VALUES ('evaluator_type', 'SEREMI', 'SEREMI Sectorial', 9)
ON CONFLICT (scheme, code) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 4. Register migration
-- ---------------------------------------------------------------------------
INSERT INTO core.schema_migration (filename)
VALUES ('goreos_migration_ciclo23_sni_levels.sql')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
