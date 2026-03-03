-- ============================================================================
-- GORE_OS Migration: Ciclo 20+21 — Financial Thresholds + Glosa Rules
-- Fecha: 2026-03-03
-- Descripcion: Tabla core.financial_threshold para umbrales financieros
--              universales (4) + reglas de glosa (5) + UTM value
-- ============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. Tabla core.financial_threshold
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS core.financial_threshold (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(64) UNIQUE NOT NULL,
    label           TEXT NOT NULL,
    value_utm       NUMERIC(10,2),
    value_pct       NUMERIC(5,2),
    enforcement_point VARCHAR(32) NOT NULL,
    source_normativa TEXT,
    applies_to_track VARCHAR(32),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE core.financial_threshold IS 'Umbrales financieros parametrizables (universales + glosa). Administrables sin code change.';
COMMENT ON COLUMN core.financial_threshold.code IS 'Identificador unico del umbral (e.g. CORE_APPROVAL, GLOSA_ADMIN_MAX)';
COMMENT ON COLUMN core.financial_threshold.value_utm IS 'Valor en UTM (NULL si es porcentual)';
COMMENT ON COLUMN core.financial_threshold.value_pct IS 'Valor porcentual (NULL si es UTM)';
COMMENT ON COLUMN core.financial_threshold.enforcement_point IS 'Punto de aplicacion: F3_F4, F1_F2, ACTO, CONVENIO, GLOSA, CONFIG';
COMMENT ON COLUMN core.financial_threshold.source_normativa IS 'Fuente legal: LOC GORE Art. 36, Ley Presupuestos, etc.';
COMMENT ON COLUMN core.financial_threshold.applies_to_track IS 'NULL = universal, codigo track = track-especifico';

-- ---------------------------------------------------------------------------
-- 2. Seed: 10 registros (4 universales + 5 glosa + 1 UTM config)
-- ---------------------------------------------------------------------------
INSERT INTO core.financial_threshold (code, label, value_utm, value_pct, enforcement_point, source_normativa, applies_to_track)
VALUES
    -- Universales (UTM)
    ('CORE_APPROVAL',       'Aprobacion CORE (Consejo Regional)',   7000,   NULL,  'F3_F4',    'LOC GORE Art. 36 bis',     NULL),
    ('RATE_EXENCION',       'Exencion evaluacion RATE/SNI',         5000,   NULL,  'F1_F2',    'Res. CGR / NIP',           NULL),
    ('CGR_TOMA_RAZON',      'Toma de Razon CGR',                    2500,   NULL,  'ACTO',     'Art. 99 CPR',              NULL),
    ('GARANTIA_CONVENIO',   'Garantia fiel cumplimiento convenio',  1000,   NULL,  'CONVENIO', 'LOC GORE',                 NULL),
    -- Glosa (porcentuales)
    ('GLOSA_ADMIN_MAX',         'Tope gastos administracion',       NULL,   5.00,  'GLOSA',    'Ley de Presupuestos',      NULL),
    ('GLOSA_HONORARIOS_MAX',    'Tope honorarios',                  NULL,   5.00,  'GLOSA',    'Ley de Presupuestos',      NULL),
    ('GLOSA_ANF_MAX',           'Tope Activos No Financieros',      NULL,   10.00, 'GLOSA',    'NIP',                      NULL),
    ('GLOSA_EQUIPAMIENTO_MAX',  'Tope equipamiento',                NULL,   20.00, 'GLOSA',    'Ley de Presupuestos',      NULL),
    ('GLOSA_REMUNERACIONES_MAX','Tope remuneraciones',              NULL,   30.00, 'GLOSA',    'Ley de Presupuestos',      NULL),
    -- UTM value (administrable)
    ('UTM_VALUE',           'Valor UTM vigente (CLP)',              67294,  NULL,  'CONFIG',   'SII',                      NULL)
ON CONFLICT (code) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 3. Register migration
-- ---------------------------------------------------------------------------
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_ciclo20_thresholds.sql', 'pending', 'migration_script')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
