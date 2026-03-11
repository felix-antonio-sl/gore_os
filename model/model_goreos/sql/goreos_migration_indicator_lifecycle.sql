-- ============================================================================
-- Migration: Indicator Lifecycle Management (CG-001..009)
-- Extends dgi_indicator with formula, frequency, source_type, lifecycle FSM.
-- Creates dgi_indicator_lifecycle_history for audit.
-- Backfills existing 11 indicators to VIGENTE.
-- ============================================================================

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. NEW SCHEME: dgi_indicator_lifecycle
-- ═══════════════════════════════════════════════════════════════════════════

INSERT INTO ref.category (scheme, code, label) VALUES
  ('dgi_indicator_lifecycle', 'BORRADOR',  'Borrador'),
  ('dgi_indicator_lifecycle', 'APROBADO',  'Aprobado'),
  ('dgi_indicator_lifecycle', 'VIGENTE',   'Vigente'),
  ('dgi_indicator_lifecycle', 'DEPRECADO', 'Deprecado')
ON CONFLICT (scheme, code) DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════
-- 2. ALTER dgi_indicator: add lifecycle columns
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE core.dgi_indicator
  ADD COLUMN IF NOT EXISTS formula TEXT,
  ADD COLUMN IF NOT EXISTS frequency VARCHAR(20),
  ADD COLUMN IF NOT EXISTS source_type VARCHAR(20) DEFAULT 'AUTO',
  ADD COLUMN IF NOT EXISTS lifecycle_status_id UUID REFERENCES ref.category(id);

-- CHECK on source_type
DO $$ BEGIN
  ALTER TABLE core.dgi_indicator
    ADD CONSTRAINT chk_dgi_indicator_source_type
    CHECK (source_type IN ('AUTO', 'MANUAL', 'EXTERNAL'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- CHECK on lifecycle_status_id (Categorical Univocity)
DO $$ BEGIN
  ALTER TABLE core.dgi_indicator
    ADD CONSTRAINT chk_dgi_indicator_lifecycle
    CHECK (lifecycle_status_id IS NULL OR fn_validate_category_scheme(lifecycle_status_id, 'dgi_indicator_lifecycle'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Backfill existing indicators to VIGENTE
UPDATE core.dgi_indicator
SET lifecycle_status_id = (
  SELECT id FROM ref.category
  WHERE scheme = 'dgi_indicator_lifecycle' AND code = 'VIGENTE'
)
WHERE lifecycle_status_id IS NULL;

-- Set source_type for TDE indicators to MANUAL (they're not auto-computed)
UPDATE core.dgi_indicator
SET source_type = 'MANUAL'
WHERE id IN (
  SELECT i.id FROM core.dgi_indicator i
  JOIN ref.category dim ON dim.id = i.dimension_id
  WHERE dim.code = 'TDE'
);

CREATE INDEX IF NOT EXISTS idx_dgi_indicator_lifecycle ON core.dgi_indicator(lifecycle_status_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- 3. AUDIT TABLE: dgi_indicator_lifecycle_history
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS core.dgi_indicator_lifecycle_history (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  indicator_id          UUID NOT NULL REFERENCES core.dgi_indicator(id) ON DELETE CASCADE,
  previous_lifecycle_id UUID REFERENCES ref.category(id),
  new_lifecycle_id      UUID NOT NULL REFERENCES ref.category(id),
  changed_by_id         UUID REFERENCES core."user"(id),
  comment               TEXT,
  changed_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_dgi_indicator_lifecycle_history_ind
  ON core.dgi_indicator_lifecycle_history(indicator_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- 4. REGISTER MIGRATION
-- ═══════════════════════════════════════════════════════════════════════════

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_indicator_lifecycle.sql', 'claude-code')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
