-- ============================================================================
-- Wave 7: Evaluation Assignment model (Poly-Switch)
-- Adds: evaluator_type scheme + core.evaluation_assignment table
-- Dependencies: none (additive migration)
-- Idempotent: ON CONFLICT, IF NOT EXISTS
-- ============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. Scheme: evaluator_type (quién evalúa)
-- ---------------------------------------------------------------------------
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('evaluator_type', 'MDSF',         'MDSF',                 'Ministerio de Desarrollo Social y Familia',           1),
('evaluator_type', 'GORE_DAE',     'GORE DAE',             'División de Análisis y Evaluación GORE',              2),
('evaluator_type', 'DIPRES_SES',   'DIPRES SES',           'Subdirección de Evaluación Social DIPRES',            3),
('evaluator_type', 'GORE_COMITE',  'Comité GORE',          'Comité Técnico de Transferencias GORE',               4),
('evaluator_type', 'GORE_DIDESO',  'GORE DIDESO',          'División de Desarrollo Social y Humano',              5),
('evaluator_type', 'GORE_COMISION','Comisión Evaluadora',  'Comisión de Evaluación FRPD (6-11 rep.)',             6),
('evaluator_type', 'SUBDERE',      'SUBDERE',              'Subsecretaría de Desarrollo Regional',                7),
('evaluator_type', 'ANID',         'ANID',                 'Agencia Nacional de Investigación y Desarrollo',      8)
ON CONFLICT (scheme, code) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 2. Table: core.evaluation_assignment
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS core.evaluation_assignment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ipr_id UUID NOT NULL REFERENCES core.ipr(id) ON DELETE CASCADE,
    evaluator_type_id UUID NOT NULL REFERENCES ref.category(id),
    evaluator_organization_id UUID REFERENCES core.organization(id),
    evaluator_name VARCHAR(200),
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deadline_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    result_id UUID REFERENCES ref.category(id),
    result_code VARCHAR(10),
    observations TEXT,
    -- Auditoría estándar
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by_id UUID REFERENCES core."user"(id),
    updated_by_id UUID REFERENCES core."user"(id),
    deleted_at TIMESTAMPTZ,
    deleted_by_id UUID REFERENCES core."user"(id),
    metadata JSONB DEFAULT '{}'::jsonb
);

COMMENT ON TABLE core.evaluation_assignment IS 'Asignación de evaluación: quién evalúa un IPR y con qué resultado (Poly-Switch Wave 7)';

CREATE INDEX IF NOT EXISTS idx_eval_assignment_ipr
    ON core.evaluation_assignment(ipr_id) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_eval_assignment_evaluator
    ON core.evaluation_assignment(evaluator_type_id) WHERE deleted_at IS NULL;

COMMIT;
