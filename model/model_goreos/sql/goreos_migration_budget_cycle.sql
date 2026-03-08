-- Budget Cycle Timeline (TP-05) — HΩ-15
-- Creates parametric milestone table + operational tracking table
-- Seeds 17 standard milestones from Omega GORE Ñuble spec
BEGIN;

-- TP-05: Parametric milestone definitions
CREATE TABLE IF NOT EXISTS core.budget_cycle_milestone (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phase VARCHAR(4) NOT NULL CHECK (phase IN ('T-1', 'T', 'T+1')),
    quarter VARCHAR(4) CHECK (quarter IN ('Q1', 'Q2', 'Q3', 'Q4')),
    ordinal SMALLINT NOT NULL UNIQUE CHECK (ordinal BETWEEN 1 AND 30),
    month_label VARCHAR(32) NOT NULL,
    name TEXT NOT NULL,
    responsible TEXT NOT NULL,
    deliverable TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Operational tracking: one row per milestone per fiscal year
CREATE TABLE IF NOT EXISTS core.budget_cycle_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    milestone_id UUID NOT NULL REFERENCES core.budget_cycle_milestone(id),
    fiscal_year SMALLINT NOT NULL CHECK (fiscal_year BETWEEN 2020 AND 2040),
    status VARCHAR(16) NOT NULL DEFAULT 'PENDIENTE'
        CHECK (status IN ('PENDIENTE', 'EN_CURSO', 'COMPLETADO', 'OMITIDO')),
    planned_date DATE,
    completed_at TIMESTAMPTZ,
    completed_by_id UUID REFERENCES core."user"(id),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (milestone_id, fiscal_year)
);

CREATE INDEX IF NOT EXISTS idx_bct_fiscal_year ON core.budget_cycle_tracking(fiscal_year);

-- Seed 17 standard milestones (Omega GORE Ñuble v2.6.0)
INSERT INTO core.budget_cycle_milestone (phase, quarter, ordinal, month_label, name, responsible, deliverable) VALUES
-- T-1: FORMULACIÓN (Jul-Dic año anterior)
('T-1', NULL,  1, 'Jul-Ago', 'DIPRES emite instrucciones presupuestarias',          'DIPRES',      'Circular instrucciones'),
('T-1', NULL,  2, 'Sep',     'Gobernador presenta proyecto presupuesto al CORE',     'Gobernador',  'Proyecto de presupuesto'),
('T-1', NULL,  3, 'Oct-Nov', 'CORE analiza y aprueba presupuesto',                   'CORE',        'Acuerdo aprobación'),
('T-1', NULL,  4, 'Dic',     'Ley de Presupuestos promulgada',                       'Congreso',    'Ley publicada en DO'),
-- T: EJECUCIÓN Q1 (Ene-Mar)
('T',   'Q1',  5, 'Ene',     'Decreto inicial de presupuesto',                       'Gobernador',  'Decreto promulgado'),
('T',   'Q1',  6, 'Feb-Mar', 'Primera distribución FNDR',                            'DIPIR',       'Resolución distribución'),
-- T: EJECUCIÓN Q2 (Abr-Jun)
('T',   'Q2',  7, 'Abr',     'Informe trimestral al CORE',                           'DIPIR/DAF',   'Informe Q1'),
('T',   'Q2',  8, 'May-Jun', 'Evaluación ejecución primer semestre',                 'DIPIR/DAF',   'Informe evaluación'),
-- T: EJECUCIÓN Q3 (Jul-Sep)
('T',   'Q3',  9, 'Jul',     'Informe semestral',                                    'DIPIR/DAF',   'Informe semestral'),
('T',   'Q3', 10, 'Ago',     'Solicitud de modificaciones presupuestarias',           'DIPIR',       'Propuesta modificación'),
('T',   'Q3', 11, 'Sep',     'CORE aprueba ajustes',                                 'CORE',        'Acuerdo ajustes'),
-- T: EJECUCIÓN Q4 (Oct-Dic)
('T',   'Q4', 12, 'Oct',     'Aceleración ejecución',                                'DIPIR/DAF',   'Plan aceleración'),
('T',   'Q4', 13, 'Nov',     'Última distribución recursos',                         'DIPIR',       'Resolución distribución'),
('T',   'Q4', 14, 'Dic',     'Cierre ejercicio presupuestario',                      'DAF',         'Acta cierre'),
-- T+1: EVALUACIÓN (Ene-Jun año siguiente)
('T+1', NULL, 15, 'Ene-Mar', 'Rendición de cuentas',                                 'DAF/UCR',     'Informe rendición'),
('T+1', NULL, 16, 'Abr',     'Cuenta Pública Gobernador',                            'Gobernador',  'Cuenta pública'),
('T+1', NULL, 17, 'May-Jun', 'Auditoría CGR',                                        'CGR',         'Informe auditoría')
ON CONFLICT DO NOTHING;

-- Self-register migration
INSERT INTO core.schema_migration (filename, checksum, applied_by)
VALUES ('goreos_migration_budget_cycle.sql', 'manual', 'budget_cycle')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
