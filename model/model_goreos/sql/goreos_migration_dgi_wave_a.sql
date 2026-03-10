-- ============================================================================
-- Migration: DGI Wave A — core.dgi_decree + seed DS7-DS12
-- Date: 2026-03-10
-- Description: Creates dgi_decree table for Ley 21.180 decree tracking.
--              Replaces hardcoded decree data in ESP_TD cockpit.
-- ============================================================================

BEGIN;

-- 1. Ensure dgi_decree_status scheme has required codes
INSERT INTO ref.category (scheme, code, label, sort_order)
SELECT 'dgi_decree_status', v.code, v.label, v.sort_order
FROM (VALUES
    ('VIGENTE',   'Vigente',   1),
    ('PARCIAL',   'Parcial',   2),
    ('PENDIENTE', 'Pendiente', 3)
) AS v(code, label, sort_order)
WHERE NOT EXISTS (
    SELECT 1 FROM ref.category WHERE scheme = 'dgi_decree_status' AND code = v.code
);

-- 2. Create dgi_decree table
CREATE TABLE IF NOT EXISTS core.dgi_decree (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    description TEXT,
    status_id   UUID NOT NULL REFERENCES ref.category(id),
    deadline    DATE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ,
    CONSTRAINT ck_dgi_decree_status
        CHECK (fn_validate_category_scheme(status_id, 'dgi_decree_status'))
);

CREATE INDEX IF NOT EXISTS idx_dgi_decree_status ON core.dgi_decree(status_id);

-- 3. Seed DS7-DS12 (Ley 21.180 compliance decrees)
INSERT INTO core.dgi_decree (code, name, description, status_id, deadline)
SELECT v.code, v.name, v.description,
       (SELECT id FROM ref.category WHERE scheme = 'dgi_decree_status' AND code = v.status),
       v.deadline::date
FROM (VALUES
    ('DS7',  'Decreto de Firma Electrónica',          'DS Nº7 — Firma electrónica avanzada en trámites públicos',     'VIGENTE',   NULL),
    ('DS8',  'Decreto Interoperabilidad',              'DS Nº8 — Interoperabilidad entre organismos del Estado',       'VIGENTE',   NULL),
    ('DS9',  'Decreto Datos Abiertos',                 'DS Nº9 — Publicación de datos abiertos gubernamentales',       'PENDIENTE', '2027-06-30'),
    ('DS10', 'Decreto Ciberseguridad',                 'DS Nº10 — Marco de ciberseguridad para el sector público',     'PENDIENTE', '2026-04-15'),
    ('DS11', 'Decreto Accesibilidad Digital',          'DS Nº11 — Accesibilidad de servicios digitales públicos',      'PENDIENTE', '2027-06-30'),
    ('DS12', 'Decreto Gestión Documental Electrónica', 'DS Nº12 — Gestión documental electrónica en el Estado',        'PARCIAL',   '2027-12-31')
) AS v(code, name, description, status, deadline)
WHERE NOT EXISTS (SELECT 1 FROM core.dgi_decree WHERE code = v.code);

-- 4. Register migration
INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_dgi_wave_a.sql', 'claude-code')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
