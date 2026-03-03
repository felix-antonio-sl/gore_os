-- Wave 8: Migrate TRACK_CONFIG from hardcoded Python dict to DB table
-- This allows runtime administration of financing track configuration
-- without code deployment.
-- IDEMPOTENT: Uses IF NOT EXISTS / ON CONFLICT

BEGIN;

-- 1. Create financing_track table
CREATE TABLE IF NOT EXISTS core.financing_track (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) UNIQUE NOT NULL,
    label TEXT NOT NULL,
    evaluator_code VARCHAR(32) NOT NULL,
    evaluator_label TEXT NOT NULL,
    favorable_products TEXT[] NOT NULL DEFAULT '{}',
    unfavorable_products TEXT[] NOT NULL DEFAULT '{}',
    terminal_negative TEXT[] NOT NULL DEFAULT '{}',
    thresholds JSONB NOT NULL DEFAULT '{}',
    required_attrs TEXT[] NOT NULL DEFAULT '{}',
    sla_days JSONB NOT NULL DEFAULT '{}',
    rs_validity_years INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. Seed the 7 financing track configurations
INSERT INTO core.financing_track (code, label, evaluator_code, evaluator_label, favorable_products, unfavorable_products, terminal_negative, thresholds, required_attrs, sla_days, rs_validity_years)
VALUES
    ('SNI', 'Track A: SNI General', 'MDSF', 'Ministerio de Desarrollo Social y Familia',
     ARRAY['RS'], ARRAY['FI', 'OT'], ARRAY['FC', 'IN'],
     '{"cgr_toma_razon": 2500, "core_approval": 7000}',
     ARRAY['rate_mdsf', 'etapa_bip', 'sector'],
     '{"admisibilidad": 5, "ate_first_rate": 10, "fi_subsanacion": 60}',
     3),

    ('C33', 'Track B: Circular 33', 'MDSF', 'Ministerio de Desarrollo Social y Familia',
     ARRAY['RS'], ARRAY['FI', 'OT'], ARRAY['NV'],
     '{"conservation_exempt_pct": 30}',
     ARRAY['categoria_c33', 'vida_util_residual'],
     '{"admisibilidad": 5}',
     2),

    ('FRIL', 'Track C: FRIL', 'GORE_DAE', 'División de Análisis y Evaluación GORE',
     ARRAY['RS'], ARRAY['FI', 'OT'], ARRAY['NV', 'IN'],
     '{"max_utm": 4545, "min_clp": 100000000, "licitacion_max_days": 45}',
     ARRAY['tipo_fril', 'cumple_norma_5k_utm'],
     '{"rate_max": 60, "fi_subsanacion": 30, "licitacion": 45}',
     3),

    ('GLOSA06', 'Track D1: Glosa 06 (PPR Directo)', 'DIPRES_SES', 'Subdirección de Evaluación Social DIPRES',
     ARRAY['RF'], ARRAY['FI', 'OT'], ARRAY[]::TEXT[],
     '{"gasto_admin_max_pct": 5}',
     ARRAY['fase_eval_central', 'rate_ses'],
     '{"feedback_round": 20}',
     NULL),

    ('TRANSFER', 'Track D2: Transferencias', 'GORE_COMITE', 'Comité Técnico de Transferencias GORE',
     ARRAY['ITF'], ARRAY['FI', 'OT'], ARRAY[]::TEXT[],
     '{}',
     ARRAY[]::TEXT[],
     '{}',
     NULL),

    ('SUBV8', 'Track E1: Subvención 8%', 'GORE_DIDESO', 'División de Desarrollo Social y Humano',
     ARRAY['RS'], ARRAY['FI'], ARRAY['NV'],
     '{"sisrec_mandatory_utm": 500, "core_direct_assign_pct": 10}',
     ARRAY['fondo_tematico', 'puntaje_evaluacion'],
     '{"admisibilidad": 5, "ejecucion_max_months": 8}',
     NULL),

    ('FRPD', 'Track E2: FRPD Royalty', 'GORE_COMISION', 'Comisión de Evaluación FRPD (6-11 rep.)',
     ARRAY['RS'], ARRAY['FI', 'OT'], ARRAY['NV'],
     '{"puntaje_min": 5.0, "cgr_res30_utm": 1000, "core_approval": 7000}',
     ARRAY['eje_fomento', 'nivel_trl', 'innovacion_ctci'],
     '{"consultas": 7}',
     2)
ON CONFLICT (code) DO NOTHING;

COMMIT;
