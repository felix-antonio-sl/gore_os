-- ============================================================================
-- Migration: DGI Process as Entity
-- Categorical basis: Promote dgi_bpmn_model.process_name (terminal attribute)
-- to dgi_process (composable object with 5 satellite morphisms).
--
-- Objects created:
--   dgi_process              — institutional process catalog
--   dgi_process_actor        — roles/systems participating in process
--   dgi_process_rule         — business rules not visible in BPMN diagram
--   dgi_process_metric       — baseline and post-improvement measurements
--   dgi_process_pain_point   — reported pain points for improvement analysis
--   dgi_improvement_opportunity — span Process ← Opportunity → Initiative
--
-- Morphism refactored:
--   dgi_bpmn_model.process_name (VARCHAR) → dgi_bpmn_model.process_id (FK)
--   dgi_bpmn_model.division_id DROPPED (derived via process.division_id)
--   dgi_bpmn_model.bpmn_type added (AS_IS / TO_BE coproduct)
--
-- Schemes added:
--   dgi_process_status (6 codes) — process lifecycle FSM
--   dgi_bpmn_type (2 codes) — AS_IS / TO_BE classification
--
-- Categorical Univocity:
--   9 missing CHECKs on pre-existing DGI tables (debt repair)
--   + 2 CHECKs on new tables
--
-- Path equations verified:
--   bpmn_model.process_id → process.division_id  (single path to organization)
--   opportunity.process_id ≠ opportunity.initiative.division_id  (intentional non-commutativity)
--
-- Idempotent: uses IF NOT EXISTS / ON CONFLICT throughout.
-- Rollback: goreos_rollback_dgi_process_entity.sql
-- ============================================================================

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. NEW SCHEMES in ref.category
-- ═══════════════════════════════════════════════════════════════════════════

INSERT INTO ref.category (scheme, code, label) VALUES
  -- Process lifecycle FSM
  ('dgi_process_status', 'IDENTIFICADO',      'Identificado'),
  ('dgi_process_status', 'EN_LEVANTAMIENTO',  'En Levantamiento'),
  ('dgi_process_status', 'MODELADO',          'Modelado'),
  ('dgi_process_status', 'VALIDADO',          'Validado'),
  ('dgi_process_status', 'PUBLICADO',         'Publicado'),
  ('dgi_process_status', 'SUSPENDIDO',        'Suspendido'),
  -- BPMN model type (AS_IS/TO_BE coproduct)
  ('dgi_bpmn_type', 'AS_IS', 'Estado Actual'),
  ('dgi_bpmn_type', 'TO_BE', 'Estado Futuro')
ON CONFLICT (scheme, code) DO NOTHING;


-- ═══════════════════════════════════════════════════════════════════════════
-- 2. CORE TABLE: dgi_process
-- Categorical role: Hub object with 6+ morphisms. Institutional process catalog.
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS core.dgi_process (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code           VARCHAR(20) UNIQUE,
  name           VARCHAR(200) NOT NULL,
  description    TEXT,
  scope          TEXT,                                          -- alcance del proceso
  division_id    UUID REFERENCES core.organization(id),         -- morphism → Organization
  owner_id       UUID REFERENCES core."user"(id),               -- morphism → User (dueño funcional)
  status_id      UUID NOT NULL,                                 -- morphism → ref.category (dgi_process_status)
  criticality    VARCHAR(10) DEFAULT 'MEDIA'
                 CHECK (criticality IN ('ALTA', 'MEDIA', 'BAJA')),
  -- Audit columns (standard GORE_OS pattern)
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by_id  UUID,
  updated_by_id  UUID,
  deleted_at     TIMESTAMPTZ,
  deleted_by_id  UUID,
  metadata       JSONB DEFAULT '{}'::jsonb,
  -- Categorical Univocity
  CONSTRAINT chk_dgi_process_status
    CHECK (fn_validate_category_scheme(status_id, 'dgi_process_status'))
);

CREATE INDEX IF NOT EXISTS idx_dgi_process_division ON core.dgi_process(division_id);
CREATE INDEX IF NOT EXISTS idx_dgi_process_status   ON core.dgi_process(status_id);
CREATE INDEX IF NOT EXISTS idx_dgi_process_owner    ON core.dgi_process(owner_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- 3. SATELLITE: dgi_process_actor
-- Categorical role: Morphism Process → Actor (roles/systems in swimlanes)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS core.dgi_process_actor (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  process_id  UUID NOT NULL REFERENCES core.dgi_process(id) ON DELETE CASCADE,
  actor_type  VARCHAR(20) NOT NULL CHECK (actor_type IN ('ROL', 'SISTEMA', 'DIVISION')),
  actor_name  VARCHAR(200) NOT NULL,
  lane_label  VARCHAR(100),                     -- BPMN swimlane label
  description TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_dgi_process_actor_process ON core.dgi_process_actor(process_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- 4. SATELLITE: dgi_process_rule
-- Categorical role: Morphism Process → Rule (business logic not in diagram)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS core.dgi_process_rule (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  process_id  UUID NOT NULL REFERENCES core.dgi_process(id) ON DELETE CASCADE,
  code        VARCHAR(20) NOT NULL,
  description TEXT NOT NULL,
  rule_type   VARCHAR(20) NOT NULL CHECK (rule_type IN ('VALIDACION', 'DECISION', 'CALCULO', 'RESTRICCION')),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (process_id, code)
);

CREATE INDEX IF NOT EXISTS idx_dgi_process_rule_process ON core.dgi_process_rule(process_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- 5. SATELLITE: dgi_process_metric
-- Categorical role: Morphism Process → Metric (baseline and post-improvement)
-- Enables before/after comparison (MP-018)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS core.dgi_process_metric (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  process_id       UUID NOT NULL REFERENCES core.dgi_process(id) ON DELETE CASCADE,
  name             VARCHAR(200) NOT NULL,
  value            NUMERIC,
  unit             VARCHAR(30),                  -- días, horas, %, count
  measured_at      DATE NOT NULL DEFAULT CURRENT_DATE,
  measurement_type VARCHAR(20) NOT NULL DEFAULT 'BASELINE'
                   CHECK (measurement_type IN ('BASELINE', 'POST_MEJORA', 'PERIODICA')),
  source           TEXT,                          -- how was this measured
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by_id    UUID
);

CREATE INDEX IF NOT EXISTS idx_dgi_process_metric_process ON core.dgi_process_metric(process_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- 6. SATELLITE: dgi_process_pain_point
-- Categorical role: Morphism Process → PainPoint (improvement analysis input)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS core.dgi_process_pain_point (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  process_id     UUID NOT NULL REFERENCES core.dgi_process(id) ON DELETE CASCADE,
  description    TEXT NOT NULL,
  impact         VARCHAR(10) NOT NULL CHECK (impact IN ('ALTO', 'MEDIO', 'BAJO')),
  bpmn_stage     VARCHAR(100),                   -- stage in BPMN diagram where pain occurs
  reported_by_id UUID REFERENCES core."user"(id),
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_dgi_process_pain_point_process ON core.dgi_process_pain_point(process_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- 7. SPAN: dgi_improvement_opportunity
-- Categorical role: Span Process ← Opportunity → Initiative
-- Bridges process analysis to DGI Kanban execution.
-- initiative_id is NULLABLE: not every opportunity generates an initiative.
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS core.dgi_improvement_opportunity (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  process_id     UUID NOT NULL REFERENCES core.dgi_process(id) ON DELETE CASCADE,
  initiative_id  UUID REFERENCES core.dgi_initiative(id) ON DELETE SET NULL,
  dimension      VARCHAR(30) NOT NULL
                 CHECK (dimension IN ('VALOR', 'DUPLICACION', 'ESPERAS', 'MOVIMIENTOS', 'ERRORES', 'AUTOMATIZACION')),
  description    TEXT NOT NULL,
  impact         VARCHAR(10) NOT NULL CHECK (impact IN ('ALTO', 'MEDIO', 'BAJO')),
  effort         VARCHAR(10) NOT NULL CHECK (effort IN ('ALTO', 'MEDIO', 'BAJO')),
  status         VARCHAR(20) NOT NULL DEFAULT 'PROPUESTA'
                 CHECK (status IN ('PROPUESTA', 'VALIDADA', 'EN_EJECUCION', 'IMPLEMENTADA', 'DESCARTADA')),
  -- Audit
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by_id  UUID,
  deleted_at     TIMESTAMPTZ,
  metadata       JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_dgi_opportunity_process    ON core.dgi_improvement_opportunity(process_id);
CREATE INDEX IF NOT EXISTS idx_dgi_opportunity_initiative ON core.dgi_improvement_opportunity(initiative_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- 8. REFACTOR: dgi_bpmn_model — process_name → process_id
-- Path equation: bpmn.process_id → process.division_id (single path)
-- Drops redundant bpmn.division_id to enforce diagram commutativity.
-- ═══════════════════════════════════════════════════════════════════════════

-- 8a. Seed dgi_process from existing BPMN process_name values
INSERT INTO core.dgi_process (code, name, status_id, metadata)
SELECT
  'PROC-' || LPAD(ROW_NUMBER() OVER (ORDER BY b.process_name)::text, 4, '0'),
  b.process_name,
  (SELECT id FROM ref.category WHERE scheme = 'dgi_process_status' AND code = 'MODELADO'),
  jsonb_build_object('migrated_from', 'dgi_bpmn_model', 'original_division_id', b.division_id::text)
FROM (SELECT DISTINCT process_name, division_id FROM core.dgi_bpmn_model WHERE deleted_at IS NULL) b
WHERE NOT EXISTS (
  SELECT 1 FROM core.dgi_process p WHERE p.name = b.process_name
);

-- 8b. Backfill division_id from original BPMN data
UPDATE core.dgi_process p
SET division_id = (p.metadata->>'original_division_id')::uuid
WHERE p.metadata->>'original_division_id' IS NOT NULL
  AND p.metadata->>'original_division_id' != ''
  AND p.division_id IS NULL;

-- 8c. Add process_id FK to dgi_bpmn_model
ALTER TABLE core.dgi_bpmn_model
  ADD COLUMN IF NOT EXISTS process_id UUID REFERENCES core.dgi_process(id);

-- 8d. Add bpmn_type column (AS_IS/TO_BE coproduct)
ALTER TABLE core.dgi_bpmn_model
  ADD COLUMN IF NOT EXISTS bpmn_type_id UUID;

-- Set default bpmn_type to AS_IS for existing models
UPDATE core.dgi_bpmn_model
SET bpmn_type_id = (SELECT id FROM ref.category WHERE scheme = 'dgi_bpmn_type' AND code = 'AS_IS')
WHERE bpmn_type_id IS NULL;

-- 8e. Populate process_id from process_name → dgi_process.name
UPDATE core.dgi_bpmn_model b
SET process_id = p.id
FROM core.dgi_process p
WHERE p.name = b.process_name
  AND b.process_id IS NULL;

-- 8f. Drop redundant division_id (path factors through process.division_id)
-- Safety: only drop if all models have process_id populated
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM core.dgi_bpmn_model WHERE process_id IS NULL AND deleted_at IS NULL
  ) THEN
    ALTER TABLE core.dgi_bpmn_model DROP COLUMN IF EXISTS division_id;
    ALTER TABLE core.dgi_bpmn_model DROP COLUMN IF EXISTS process_name;
    -- Make process_id NOT NULL now that all rows are populated
    ALTER TABLE core.dgi_bpmn_model ALTER COLUMN process_id SET NOT NULL;
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_dgi_bpmn_model_process ON core.dgi_bpmn_model(process_id);


-- ═══════════════════════════════════════════════════════════════════════════
-- 9. CATEGORICAL UNIVOCITY DEBT REPAIR
-- 9 missing CHECKs on pre-existing DGI tables + 1 new on bpmn_type
-- ═══════════════════════════════════════════════════════════════════════════

-- dgi_indicator.dimension_id
DO $$ BEGIN
  ALTER TABLE core.dgi_indicator
    ADD CONSTRAINT chk_dgi_indicator_dimension
    CHECK (fn_validate_category_scheme(dimension_id, 'dgi_indicator_dimension'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- dgi_indicator.signal_id (nullable)
DO $$ BEGIN
  ALTER TABLE core.dgi_indicator
    ADD CONSTRAINT chk_dgi_indicator_signal
    CHECK (signal_id IS NULL OR fn_validate_category_scheme(signal_id, 'dgi_signal'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- dgi_initiative.status_id
DO $$ BEGIN
  ALTER TABLE core.dgi_initiative
    ADD CONSTRAINT chk_dgi_initiative_status
    CHECK (fn_validate_category_scheme(status_id, 'dgi_initiative_status'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- dgi_initiative.dmaic_phase_id (nullable)
DO $$ BEGIN
  ALTER TABLE core.dgi_initiative
    ADD CONSTRAINT chk_dgi_initiative_dmaic_phase
    CHECK (dmaic_phase_id IS NULL OR fn_validate_category_scheme(dmaic_phase_id, 'dgi_dmaic_phase'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- dgi_bpmn_model.status_id
DO $$ BEGIN
  ALTER TABLE core.dgi_bpmn_model
    ADD CONSTRAINT chk_dgi_bpmn_model_status
    CHECK (fn_validate_category_scheme(status_id, 'dgi_bpmn_status'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- dgi_bpmn_model.bpmn_type_id (nullable during migration)
DO $$ BEGIN
  ALTER TABLE core.dgi_bpmn_model
    ADD CONSTRAINT chk_dgi_bpmn_model_type
    CHECK (bpmn_type_id IS NULL OR fn_validate_category_scheme(bpmn_type_id, 'dgi_bpmn_type'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- dgi_committee_session.status_id
DO $$ BEGIN
  ALTER TABLE core.dgi_committee_session
    ADD CONSTRAINT chk_dgi_committee_session_status
    CHECK (fn_validate_category_scheme(status_id, 'dgi_session_status'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- dgi_data_source_status.status_id
DO $$ BEGIN
  ALTER TABLE core.dgi_data_source_status
    ADD CONSTRAINT chk_dgi_data_source_status
    CHECK (fn_validate_category_scheme(status_id, 'dgi_source_status'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- dgi_report.report_type_id
DO $$ BEGIN
  ALTER TABLE core.dgi_report
    ADD CONSTRAINT chk_dgi_report_type
    CHECK (fn_validate_category_scheme(report_type_id, 'dgi_report_type'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- dgi_report.status_id
DO $$ BEGIN
  ALTER TABLE core.dgi_report
    ADD CONSTRAINT chk_dgi_report_status
    CHECK (fn_validate_category_scheme(status_id, 'dgi_report_status'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


-- ═══════════════════════════════════════════════════════════════════════════
-- 10. REGISTER MIGRATION
-- ═══════════════════════════════════════════════════════════════════════════

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_dgi_process_entity.sql', 'claude-code')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
