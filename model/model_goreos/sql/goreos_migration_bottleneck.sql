-- =============================================================================
-- GORE_OS — Migration: Bottleneck Detection & Investigation (CG-019..023)
-- =============================================================================
-- Creates dgi_bottleneck_status scheme and core.dgi_bottleneck_investigation table.
-- =============================================================================

BEGIN;

INSERT INTO ref.category (scheme, code, label) VALUES
  ('dgi_bottleneck_status', 'DETECTADO',    'Detectado'),
  ('dgi_bottleneck_status', 'VERIFICADO',   'Verificado'),
  ('dgi_bottleneck_status', 'ANALIZADO',    'Analizado'),
  ('dgi_bottleneck_status', 'PROPUESTO',    'Propuesto'),
  ('dgi_bottleneck_status', 'IMPLEMENTADO', 'Implementado'),
  ('dgi_bottleneck_status', 'CERRADO',      'Cerrado')
ON CONFLICT (scheme, code) DO NOTHING;

CREATE TABLE IF NOT EXISTS core.dgi_bottleneck_investigation (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code                  TEXT UNIQUE,
    status_id             UUID NOT NULL REFERENCES ref.category(id),
    division_id           UUID REFERENCES core.organization(id),
    indicator_id          UUID REFERENCES core.dgi_indicator(id),
    process_id            UUID REFERENCES core.dgi_process(id),
    detection_type        TEXT NOT NULL,
    detection_value       NUMERIC(10,2),
    detection_threshold   NUMERIC(10,2),
    problem               TEXT,
    verification          TEXT,
    root_cause_analysis   TEXT,
    proposal              TEXT,
    communication         TEXT,
    follow_up             TEXT,
    detected_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at             TIMESTAMPTZ,
    created_by_id         UUID REFERENCES core."user"(id),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at            TIMESTAMPTZ,
    CONSTRAINT ck_dgi_bottleneck_status CHECK (fn_validate_category_scheme(status_id, 'dgi_bottleneck_status'))
);

CREATE INDEX IF NOT EXISTS idx_dgi_bottleneck_status ON core.dgi_bottleneck_investigation(status_id);
CREATE INDEX IF NOT EXISTS idx_dgi_bottleneck_division ON core.dgi_bottleneck_investigation(division_id) WHERE deleted_at IS NULL;

INSERT INTO core.schema_migration (filename, applied_by) VALUES ('goreos_migration_bottleneck.sql', 'claude-code') ON CONFLICT (filename) DO NOTHING;

COMMIT;
