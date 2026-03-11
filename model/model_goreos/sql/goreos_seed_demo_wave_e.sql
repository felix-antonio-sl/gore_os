-- =============================================================================
-- GORE_OS — Demo Data Wave E (Risk Management)
-- =============================================================================
-- All records use DEMO- prefix. FK references via subqueries (no hardcoded UUIDs).
-- Safe to run multiple times: WHERE NOT EXISTS guards.
-- Remove with: goreos_unseed_demo_wave_e.sql
-- =============================================================================

BEGIN;

-- =============================================================================
-- 1. RISKS (5 records, mixed statuses/types/probabilities)
-- =============================================================================

-- DEMO-RSK-0001: FINANCIERO, MUY_ALTA prob, BLOQUEA_PAGO impact, IDENTIFICADO
INSERT INTO core.risk (
    code, name, risk_type_id, probability_id, impact_id,
    status_id, subject_type, subject_id,
    mitigation_plan, identified_at, created_by_id
)
SELECT
    'DEMO-RSK-0001',
    'Riesgo de bloqueo de pagos por rendiciones vencidas',
    (SELECT id FROM ref.category WHERE scheme = 'risk_type' AND code = 'FINANCIERO'),
    (SELECT id FROM ref.category WHERE scheme = 'risk_probability' AND code = 'MUY_ALTA'),
    (SELECT id FROM ref.category WHERE scheme = 'problem_impact' AND code = 'BLOQUEA_PAGO'),
    (SELECT id FROM ref.category WHERE scheme = 'risk_status' AND code = 'IDENTIFICADO'),
    'core.ipr',
    (SELECT id FROM core.ipr WHERE deleted_at IS NULL ORDER BY created_at LIMIT 1),
    NULL,
    CURRENT_DATE - INTERVAL '10 days',
    (SELECT id FROM core."user" WHERE email = 'jefe.dgi@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.risk WHERE code = 'DEMO-RSK-0001'
);

-- DEMO-RSK-0002: OPERACIONAL, ALTA prob, RETRASA_OBRA impact, EN_EVALUACION
INSERT INTO core.risk (
    code, name, risk_type_id, probability_id, impact_id,
    status_id, subject_type, subject_id,
    mitigation_plan, identified_at, created_by_id
)
SELECT
    'DEMO-RSK-0002',
    'Retraso en obra de conectividad rural por problemas de acceso',
    (SELECT id FROM ref.category WHERE scheme = 'risk_type' AND code = 'OPERACIONAL'),
    (SELECT id FROM ref.category WHERE scheme = 'risk_probability' AND code = 'ALTA'),
    (SELECT id FROM ref.category WHERE scheme = 'problem_impact' AND code = 'RETRASA_OBRA'),
    (SELECT id FROM ref.category WHERE scheme = 'risk_status' AND code = 'EN_EVALUACION'),
    'core.ipr',
    (SELECT id FROM core.ipr WHERE deleted_at IS NULL ORDER BY created_at OFFSET 1 LIMIT 1),
    'Evaluar rutas alternativas de acceso con municipio',
    CURRENT_DATE - INTERVAL '7 days',
    (SELECT id FROM core."user" WHERE email = 'control.gestion@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.risk WHERE code = 'DEMO-RSK-0002'
);

-- DEMO-RSK-0003: LEGAL, MEDIA prob, INCUMPLIMIENTO_PLAZO impact, EN_MITIGACION
INSERT INTO core.risk (
    code, name, risk_type_id, probability_id, impact_id,
    status_id, subject_type, subject_id,
    mitigation_plan, identified_at, created_by_id
)
SELECT
    'DEMO-RSK-0003',
    'Incumplimiento de plazos legales en convenio con universidad',
    (SELECT id FROM ref.category WHERE scheme = 'risk_type' AND code = 'LEGAL'),
    (SELECT id FROM ref.category WHERE scheme = 'risk_probability' AND code = 'MEDIA'),
    (SELECT id FROM ref.category WHERE scheme = 'problem_impact' AND code = 'INCUMPLIMIENTO_PLAZO'),
    (SELECT id FROM ref.category WHERE scheme = 'risk_status' AND code = 'EN_MITIGACION'),
    'core.ipr',
    (SELECT id FROM core.ipr WHERE deleted_at IS NULL ORDER BY created_at OFFSET 2 LIMIT 1),
    'Reformulación de cláusulas con asesoría jurídica. Plazo extendido 30 días.',
    CURRENT_DATE - INTERVAL '15 days',
    (SELECT id FROM core."user" WHERE email = 'jefe.dgi@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.risk WHERE code = 'DEMO-RSK-0003'
);

-- DEMO-RSK-0004: TECNICO, BAJA prob, OTRO impact, MITIGADO
INSERT INTO core.risk (
    code, name, risk_type_id, probability_id, impact_id,
    status_id, subject_type, subject_id,
    mitigation_plan, identified_at, created_by_id
)
SELECT
    'DEMO-RSK-0004',
    'Fallo técnico en plataforma de firma electrónica',
    (SELECT id FROM ref.category WHERE scheme = 'risk_type' AND code = 'TECNICO'),
    (SELECT id FROM ref.category WHERE scheme = 'risk_probability' AND code = 'BAJA'),
    (SELECT id FROM ref.category WHERE scheme = 'problem_impact' AND code = 'OTRO'),
    (SELECT id FROM ref.category WHERE scheme = 'risk_status' AND code = 'MITIGADO'),
    'core.ipr',
    (SELECT id FROM core.ipr WHERE deleted_at IS NULL ORDER BY created_at OFFSET 3 LIMIT 1),
    'Proveedor implementó parche correctivo. Monitoreo activo por 30 días.',
    CURRENT_DATE - INTERVAL '30 days',
    (SELECT id FROM core."user" WHERE email = 'td@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.risk WHERE code = 'DEMO-RSK-0004'
);

-- DEMO-RSK-0005: REPUTACIONAL, ALTA prob, RIESGO_RENDICION impact, ACEPTADO
INSERT INTO core.risk (
    code, name, risk_type_id, probability_id, impact_id,
    status_id, subject_type, subject_id,
    mitigation_plan, identified_at, created_by_id
)
SELECT
    'DEMO-RSK-0005',
    'Riesgo reputacional por atraso en rendición de fondos SUBDERE',
    (SELECT id FROM ref.category WHERE scheme = 'risk_type' AND code = 'REPUTACIONAL'),
    (SELECT id FROM ref.category WHERE scheme = 'risk_probability' AND code = 'ALTA'),
    (SELECT id FROM ref.category WHERE scheme = 'problem_impact' AND code = 'RIESGO_RENDICION'),
    (SELECT id FROM ref.category WHERE scheme = 'risk_status' AND code = 'ACEPTADO'),
    'core.ipr',
    (SELECT id FROM core.ipr WHERE deleted_at IS NULL ORDER BY created_at OFFSET 4 LIMIT 1),
    'Riesgo aceptado — dependencia de contraparte externa. Seguimiento quincenal.',
    CURRENT_DATE - INTERVAL '20 days',
    (SELECT id FROM core."user" WHERE email = 'jefe.dgi@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.risk WHERE code = 'DEMO-RSK-0005'
);

COMMIT;

-- Verificación:
-- SELECT code, name, status_id FROM core.risk WHERE code LIKE 'DEMO-%';
