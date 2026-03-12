-- ============================================================================
-- Migration: Lifecycle Wave 3 — Cierre Administrativo + Evaluación Ex-Post
-- Date: 2026-03-11
-- Description:
--   3A. New states: RENDICION_APROBADA, EN_CIERRE_ADMINISTRATIVO
--   3B. New table: core.ipr_closure (formal closure record)
--   3C. New table: core.ipr_expost_evaluation (post-closure impact assessment)
--   3D. New schemes: expost_eval_type (3), expost_rating (4)
-- ============================================================================

BEGIN;

-- ============================================================================
-- 3A. New F5 states
-- ============================================================================

-- RENDICION_APROBADA: SSOT seq 24 — ciclo SISREC completado con aprobación UCR
INSERT INTO ref.category (scheme, code, label, description, sort_order)
VALUES ('ipr_state', 'RENDICION_APROBADA', 'Rendición Aprobada',
        'Ciclo SISREC completado con aprobación UCR — pendiente cierre administrativo',
        36)
ON CONFLICT (scheme, code) DO NOTHING;

UPDATE ref.category SET valid_transitions = '["EN_CIERRE_ADMINISTRATIVO", "CERRADO", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'RENDICION_APROBADA';

-- EN_CIERRE_ADMINISTRATIVO: proceso formal de cierre con acta y firma
INSERT INTO ref.category (scheme, code, label, description, sort_order)
VALUES ('ipr_state', 'EN_CIERRE_ADMINISTRATIVO', 'En Cierre Administrativo',
        'Proceso de cierre formal con acta y firma de autoridad', 37)
ON CONFLICT (scheme, code) DO NOTHING;

UPDATE ref.category SET valid_transitions = '["CERRADO", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_CIERRE_ADMINISTRATIVO';

-- Update EN_RENDICION to include RENDICION_APROBADA as target
UPDATE ref.category SET valid_transitions = '["RENDICION_APROBADA", "CERRADO", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_RENDICION';

-- ============================================================================
-- 3B. Schemes for evaluación ex-post
-- ============================================================================

INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
    ('expost_eval_type', 'SIMPLIFICADA', 'Simplificada', 'Evaluación simplificada de resultados', 1),
    ('expost_eval_type', 'PROFUNDIDAD', 'En Profundidad', 'Evaluación detallada de impacto y sostenibilidad', 2),
    ('expost_eval_type', 'IMPACTO', 'De Impacto', 'Evaluación de impacto socioeconómico a largo plazo', 3)
ON CONFLICT (scheme, code) DO NOTHING;

INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
    ('expost_rating', 'EXITOSO', 'Exitoso', 'IPR cumplió y superó objetivos planificados', 1),
    ('expost_rating', 'SATISFACTORIO', 'Satisfactorio', 'IPR cumplió objetivos principales', 2),
    ('expost_rating', 'PARCIAL', 'Parcialmente Satisfactorio', 'IPR cumplió parcialmente sus objetivos', 3),
    ('expost_rating', 'INSATISFACTORIO', 'Insatisfactorio', 'IPR no cumplió objetivos mínimos', 4)
ON CONFLICT (scheme, code) DO NOTHING;

-- ============================================================================
-- 3C. Table: core.ipr_closure
-- ============================================================================

CREATE TABLE IF NOT EXISTS core.ipr_closure (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id UUID NOT NULL UNIQUE REFERENCES core.ipr(id),
    closure_date DATE,
    closure_report TEXT,
    physical_completion NUMERIC(5, 2),
    financial_completion NUMERIC(5, 2),
    final_amount NUMERIC(18, 2),
    signed_by_id UUID REFERENCES core."user"(id),
    signed_at TIMESTAMPTZ,
    closure_act_id UUID REFERENCES core.administrative_act(id),
    created_by_id UUID NOT NULL REFERENCES core."user"(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 3D. Table: core.ipr_expost_evaluation
-- ============================================================================

CREATE TABLE IF NOT EXISTS core.ipr_expost_evaluation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id UUID NOT NULL REFERENCES core.ipr(id),
    evaluation_date DATE NOT NULL,
    evaluator_id UUID NOT NULL REFERENCES core."user"(id),
    evaluation_type_id UUID NOT NULL REFERENCES ref.category(id),
    impact_score NUMERIC(5, 2),
    sustainability_score NUMERIC(5, 2),
    efficiency_score NUMERIC(5, 2),
    effectiveness_score NUMERIC(5, 2),
    overall_rating_id UUID REFERENCES ref.category(id),
    findings TEXT,
    recommendations TEXT,
    lessons_learned TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_expost_eval_type_scheme
        CHECK (fn_validate_category_scheme(evaluation_type_id, 'expost_eval_type')),
    CONSTRAINT chk_expost_rating_scheme
        CHECK (overall_rating_id IS NULL OR fn_validate_category_scheme(overall_rating_id, 'expost_rating'))
);

CREATE INDEX IF NOT EXISTS idx_expost_eval_ipr ON core.ipr_expost_evaluation(ipr_id);

-- ============================================================================
-- Track migration
-- ============================================================================
INSERT INTO core.schema_migration (filename, applied_at)
VALUES ('goreos_migration_lifecycle_wave3.sql', NOW())
ON CONFLICT (filename) DO NOTHING;

COMMIT;
