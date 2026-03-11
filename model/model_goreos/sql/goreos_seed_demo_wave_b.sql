-- =============================================================================
-- GORE_OS — Demo Data Wave B (Coordination, Escalation, Services)
-- =============================================================================
-- All records use DEMO- prefix. FK references via subqueries (no hardcoded UUIDs).
-- Safe to run multiple times: ON CONFLICT DO NOTHING on unique constraints.
-- Remove with: goreos_unseed_demo_wave_b.sql
-- =============================================================================

BEGIN;

-- =============================================================================
-- 1. AR DECISIONS (3 records, mixed statuses)
-- =============================================================================
INSERT INTO core.dgi_ar_decision (
    description, decision_type_id, status_id, due_date, context,
    responsible_id, created_by_id
)
SELECT
    'DEMO-DEC-001: Priorizar inversión FNDR en conectividad rural',
    (SELECT id FROM ref.category WHERE scheme = 'dgi_ar_decision_type' AND code = 'PRIORIDAD'),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_ar_decision_status' AND code = 'PENDIENTE'),
    CURRENT_DATE + INTERVAL '14 days',
    'Análisis de brechas territoriales indica déficit de conectividad en 8 comunas rurales',
    (SELECT id FROM core."user" WHERE email = 'jefe.dgi@goreos.cl'),
    (SELECT id FROM core."user" WHERE email = 'jefe.dgi@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_ar_decision WHERE description LIKE 'DEMO-DEC-001%'
);

INSERT INTO core.dgi_ar_decision (
    description, decision_type_id, status_id, due_date, context,
    responsible_id, created_by_id
)
SELECT
    'DEMO-DEC-002: Reasignar recursos desde programa cancelado a emergencia hídrica',
    (SELECT id FROM ref.category WHERE scheme = 'dgi_ar_decision_type' AND code = 'RECURSO'),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_ar_decision_status' AND code = 'EN_EJECUCION'),
    CURRENT_DATE + INTERVAL '7 days',
    'Programa de capacitación cancelado libera M$120.000 reasignables',
    (SELECT id FROM core."user" WHERE email = 'control.gestion@goreos.cl'),
    (SELECT id FROM core."user" WHERE email = 'jefe.dgi@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_ar_decision WHERE description LIKE 'DEMO-DEC-002%'
);

INSERT INTO core.dgi_ar_decision (
    description, decision_type_id, status_id, due_date, context,
    responsible_id, resolved_at, created_by_id
)
SELECT
    'DEMO-DEC-003: Estrategia de digitalización para trámites ciudadanos',
    (SELECT id FROM ref.category WHERE scheme = 'dgi_ar_decision_type' AND code = 'ESTRATEGIA'),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_ar_decision_status' AND code = 'COMPLETADA'),
    CURRENT_DATE - INTERVAL '3 days',
    'Ley 21.180 exige cumplimiento progresivo — plan aprobado en última AR',
    (SELECT id FROM core."user" WHERE email = 'td@goreos.cl'),
    NOW(),
    (SELECT id FROM core."user" WHERE email = 'jefe.dgi@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_ar_decision WHERE description LIKE 'DEMO-DEC-003%'
);


-- =============================================================================
-- 2. ESCALATIONS (3 records, N1/N2/N3, mixed statuses)
-- =============================================================================
INSERT INTO core.dgi_escalation (
    code, level_id, status_id, situation, impact,
    options, recommendation, deadline, created_by_id
)
SELECT
    'DEMO-ESC-001',
    (SELECT id FROM ref.category WHERE scheme = 'dgi_escalation_level' AND code = 'NIVEL_1'),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_escalation_status' AND code = 'ABIERTO'),
    'Retraso en entrega de información presupuestaria de DAF',
    'Imposibilidad de generar informe mensual a tiempo',
    '[]'::jsonb,
    'Solicitar reunión bilateral con jefe DAF',
    (CURRENT_TIMESTAMP + INTERVAL '5 days'),
    (SELECT id FROM core."user" WHERE email = 'control.gestion@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_escalation WHERE code = 'DEMO-ESC-001'
);

INSERT INTO core.dgi_escalation (
    code, level_id, status_id, situation, impact,
    options, recommendation, deadline, created_by_id
)
SELECT
    'DEMO-ESC-002',
    (SELECT id FROM ref.category WHERE scheme = 'dgi_escalation_level' AND code = 'NIVEL_2'),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_escalation_status' AND code = 'EN_GESTION'),
    'Incumplimiento reiterado de SLAs por DIDESO en procesos de rendición',
    '3 rendiciones vencidas, riesgo de observación CGR',
    '[{"option":"Notificación formal","pros":"Registro oficial","cons":"Puede generar fricción"}]'::jsonb,
    'Escalar a nivel directivo con evidencia documental',
    (CURRENT_TIMESTAMP + INTERVAL '3 days'),
    (SELECT id FROM core."user" WHERE email = 'jefe.dgi@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_escalation WHERE code = 'DEMO-ESC-002'
);

INSERT INTO core.dgi_escalation (
    code, level_id, status_id, situation, impact,
    options, recommendation, deadline,
    resolved_description, resolved_at, created_by_id
)
SELECT
    'DEMO-ESC-003',
    (SELECT id FROM ref.category WHERE scheme = 'dgi_escalation_level' AND code = 'NIVEL_3'),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_escalation_status' AND code = 'RESUELTO'),
    'Bloqueo en firma de convenio con universidad por observación jurídica',
    'Proyecto de innovación regional paralizado hace 45 días',
    '[]'::jsonb,
    'Intervención directa del Gobernador',
    (CURRENT_TIMESTAMP - INTERVAL '2 days'),
    'Convenio reformulado con nueva cláusula jurídica aprobada',
    NOW(),
    (SELECT id FROM core."user" WHERE email = 'jefe.dgi@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_escalation WHERE code = 'DEMO-ESC-003'
);


-- =============================================================================
-- 3. SERVICES (4 records, one per area)
-- =============================================================================
INSERT INTO core.dgi_service (
    code, name, description, area, status_id, sla_days,
    how_to_request, deliverables, created_by_id
)
SELECT
    'DEMO-SVC-CG-001',
    'Informe de Gestión Mensual',
    'Elaboración del informe consolidado de gestión para la AR',
    'CG',
    (SELECT id FROM ref.category WHERE scheme = 'dgi_service_status' AND code = 'ACTIVO'),
    5,
    'Solicitar vía plataforma o correo a control.gestion@goreos.cl',
    'Informe PDF + presentación ejecutiva',
    (SELECT id FROM core."user" WHERE email = 'jefe.dgi@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_service WHERE code = 'DEMO-SVC-CG-001'
);

INSERT INTO core.dgi_service (
    code, name, description, area, status_id, sla_days,
    how_to_request, deliverables, created_by_id
)
SELECT
    'DEMO-SVC-CG-002',
    'Análisis de Indicadores Sectoriales',
    'Análisis ad-hoc de indicadores por sector o territorio',
    'CG',
    (SELECT id FROM ref.category WHERE scheme = 'dgi_service_status' AND code = 'ACTIVO'),
    10,
    'Solicitar con al menos 5 días de anticipación',
    'Dashboard interactivo + ficha técnica',
    (SELECT id FROM core."user" WHERE email = 'jefe.dgi@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_service WHERE code = 'DEMO-SVC-CG-002'
);

INSERT INTO core.dgi_service (
    code, name, description, area, status_id, sla_days,
    how_to_request, deliverables, created_by_id
)
SELECT
    'DEMO-SVC-MP-001',
    'Levantamiento de Procesos',
    'Modelamiento BPMN de procesos institucionales con equipo de mejora',
    'MP',
    (SELECT id FROM ref.category WHERE scheme = 'dgi_service_status' AND code = 'ACTIVO'),
    20,
    'Coordinar con procesos@goreos.cl — requiere disponibilidad del equipo divisional',
    'Diagrama BPMN AS-IS + informe de hallazgos',
    (SELECT id FROM core."user" WHERE email = 'jefe.dgi@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_service WHERE code = 'DEMO-SVC-MP-001'
);

INSERT INTO core.dgi_service (
    code, name, description, area, status_id, sla_days,
    how_to_request, deliverables, created_by_id
)
SELECT
    'DEMO-SVC-TD-001',
    'Soporte Plataformas Digitales',
    'Asistencia técnica en plataformas institucionales y firma electrónica',
    'TD',
    (SELECT id FROM ref.category WHERE scheme = 'dgi_service_status' AND code = 'ACTIVO'),
    3,
    'Mesa de ayuda td@goreos.cl o extensión 4500',
    'Resolución de incidente + registro en bitácora',
    (SELECT id FROM core."user" WHERE email = 'jefe.dgi@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_service WHERE code = 'DEMO-SVC-TD-001'
);


-- =============================================================================
-- 4. SLAs (3 records, one per service except TD)
-- =============================================================================
INSERT INTO core.dgi_sla (
    service_id, product_type_id, description, target_days, priority
)
SELECT
    (SELECT id FROM core.dgi_service WHERE code = 'DEMO-SVC-CG-001'),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_sla_product_type' AND code = 'INFORME_FLASH'),
    'SLA informe flash para AR',
    3,
    1
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_sla
    WHERE service_id = (SELECT id FROM core.dgi_service WHERE code = 'DEMO-SVC-CG-001')
      AND product_type_id = (SELECT id FROM ref.category WHERE scheme = 'dgi_sla_product_type' AND code = 'INFORME_FLASH')
);

INSERT INTO core.dgi_sla (
    service_id, product_type_id, description, target_days, priority
)
SELECT
    (SELECT id FROM core.dgi_service WHERE code = 'DEMO-SVC-CG-002'),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_sla_product_type' AND code = 'INFORME_MENSUAL'),
    'SLA análisis sectorial mensual',
    10,
    2
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_sla
    WHERE service_id = (SELECT id FROM core.dgi_service WHERE code = 'DEMO-SVC-CG-002')
      AND product_type_id = (SELECT id FROM ref.category WHERE scheme = 'dgi_sla_product_type' AND code = 'INFORME_MENSUAL')
);

INSERT INTO core.dgi_sla (
    service_id, product_type_id, description, target_days, priority
)
SELECT
    (SELECT id FROM core.dgi_service WHERE code = 'DEMO-SVC-MP-001'),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_sla_product_type' AND code = 'MODELAMIENTO_BPMN'),
    'SLA levantamiento de procesos',
    20,
    3
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_sla
    WHERE service_id = (SELECT id FROM core.dgi_service WHERE code = 'DEMO-SVC-MP-001')
      AND product_type_id = (SELECT id FROM ref.category WHERE scheme = 'dgi_sla_product_type' AND code = 'MODELAMIENTO_BPMN')
);


-- =============================================================================
-- 5. SERVICE REQUESTS (4 records, mixed status/urgency)
-- =============================================================================
INSERT INTO core.dgi_service_request (
    code, service_id, requester_id, status_id,
    description, urgency
)
SELECT
    'DEMO-REQ-001',
    (SELECT id FROM core.dgi_service WHERE code = 'DEMO-SVC-CG-001'),
    (SELECT id FROM core."user" WHERE email = 'jefe.daf@goreos.cl'),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_request_status' AND code = 'RECIBIDA'),
    'Solicito informe de ejecución presupuestaria para presentación a Consejo Regional',
    'ALTA'
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_service_request WHERE code = 'DEMO-REQ-001'
);

INSERT INTO core.dgi_service_request (
    code, service_id, requester_id, status_id,
    description, urgency, assigned_to_id, started_at
)
SELECT
    'DEMO-REQ-002',
    (SELECT id FROM core.dgi_service WHERE code = 'DEMO-SVC-MP-001'),
    (SELECT id FROM core."user" WHERE email = 'jefe.dideso@goreos.cl'),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_request_status' AND code = 'EN_EJECUCION'),
    'Levantamiento del proceso de rendición de cuentas de subvenciones',
    'NORMAL',
    (SELECT id FROM core."user" WHERE email = 'procesos@goreos.cl'),
    NOW() - INTERVAL '5 days'
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_service_request WHERE code = 'DEMO-REQ-002'
);

INSERT INTO core.dgi_service_request (
    code, service_id, requester_id, status_id,
    description, urgency, assigned_to_id, started_at, completed_at,
    satisfaction_score, feedback_text
)
SELECT
    'DEMO-REQ-003',
    (SELECT id FROM core.dgi_service WHERE code = 'DEMO-SVC-TD-001'),
    (SELECT id FROM core."user" WHERE email = 'encargado.daf@goreos.cl'),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_request_status' AND code = 'COMPLETADA'),
    'Problema con firma electrónica avanzada — no reconoce certificado',
    'ALTA',
    (SELECT id FROM core."user" WHERE email = 'td@goreos.cl'),
    NOW() - INTERVAL '3 days',
    NOW() - INTERVAL '1 day',
    5,
    'Excelente respuesta, problema resuelto en 2 días'
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_service_request WHERE code = 'DEMO-REQ-003'
);

INSERT INTO core.dgi_service_request (
    code, service_id, requester_id, status_id,
    description, urgency
)
SELECT
    'DEMO-REQ-004',
    (SELECT id FROM core.dgi_service WHERE code = 'DEMO-SVC-CG-002'),
    (SELECT id FROM core."user" WHERE email = 'jefe.diplade@goreos.cl'),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_request_status' AND code = 'EN_EVALUACION'),
    'Análisis comparativo de indicadores de inversión pública regional vs nacional',
    'NORMAL'
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_service_request WHERE code = 'DEMO-REQ-004'
);


-- =============================================================================
-- 6. DIVISION INTERACTIONS (3 records, DAF/DIDESO/DIFOI)
-- =============================================================================
INSERT INTO core.dgi_division_interaction (
    division_id, interaction_type_id, interaction_date,
    participants, topics, agreements, next_date, notes, created_by_id
)
SELECT
    (SELECT id FROM core.organization WHERE code = 'DIV-DAF' AND deleted_at IS NULL),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_interaction_type' AND code = 'REUNION_BILATERAL'),
    CURRENT_DATE - INTERVAL '5 days',
    '[{"name":"Jefe DAF","role":"Jefe División"},{"name":"Control Gestión","role":"ESP_CONTROL_GESTION"}]'::jsonb,
    '["Revisión ejecución presupuestaria Q1","Calendario rendiciones pendientes"]'::jsonb,
    '[{"description":"DAF enviará detalle CDP pendientes antes del viernes","responsible":"Jefe DAF","due_date":"' || (CURRENT_DATE + INTERVAL '2 days')::text || '","status":"PENDIENTE"}]'::jsonb,
    CURRENT_DATE + INTERVAL '15 days',
    'Reunión productiva, buena disposición del equipo DAF',
    (SELECT id FROM core."user" WHERE email = 'control.gestion@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_division_interaction
    WHERE division_id = (SELECT id FROM core.organization WHERE code = 'DIV-DAF' AND deleted_at IS NULL)
      AND interaction_date = CURRENT_DATE - INTERVAL '5 days'
      AND created_by_id = (SELECT id FROM core."user" WHERE email = 'control.gestion@goreos.cl')
);

INSERT INTO core.dgi_division_interaction (
    division_id, interaction_type_id, interaction_date,
    participants, topics, agreements, next_date, notes, created_by_id
)
SELECT
    (SELECT id FROM core.organization WHERE code = 'DIV-DIDESO' AND deleted_at IS NULL),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_interaction_type' AND code = 'TALLER'),
    CURRENT_DATE - INTERVAL '10 days',
    '[{"name":"Equipo DIDESO","role":"División"},{"name":"Procesos DGI","role":"ESP_PROCESOS"}]'::jsonb,
    '["Mapeo de procesos de subsidios","Identificación de cuellos de botella"]'::jsonb,
    '[{"description":"DIDESO compartirá flujo actual de postulaciones","responsible":"Encargado DIDESO","due_date":"' || (CURRENT_DATE - INTERVAL '3 days')::text || '","status":"COMPLETADO"}]'::jsonb,
    CURRENT_DATE + INTERVAL '20 days',
    'Taller de levantamiento exitoso — 12 participantes',
    (SELECT id FROM core."user" WHERE email = 'procesos@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_division_interaction
    WHERE division_id = (SELECT id FROM core.organization WHERE code = 'DIV-DIDESO' AND deleted_at IS NULL)
      AND interaction_date = CURRENT_DATE - INTERVAL '10 days'
      AND created_by_id = (SELECT id FROM core."user" WHERE email = 'procesos@goreos.cl')
);

INSERT INTO core.dgi_division_interaction (
    division_id, interaction_type_id, interaction_date,
    participants, topics, agreements, next_date, notes, created_by_id
)
SELECT
    (SELECT id FROM core.organization WHERE code = 'DIV-DIFOI' AND deleted_at IS NULL),
    (SELECT id FROM ref.category WHERE scheme = 'dgi_interaction_type' AND code = 'ASESORIA'),
    CURRENT_DATE - INTERVAL '2 days',
    '[{"name":"Jefe DIFOI","role":"Jefe División"},{"name":"TD DGI","role":"ESP_TD"}]'::jsonb,
    '["Implementación firma electrónica en resoluciones","Capacitación GESDOC"]'::jsonb,
    '[{"description":"Programar capacitación GESDOC para equipo DIFOI","responsible":"ESP_TD","due_date":"' || (CURRENT_DATE + INTERVAL '10 days')::text || '","status":"PENDIENTE"}]'::jsonb,
    CURRENT_DATE + INTERVAL '30 days',
    'DIFOI muestra interés en adopción temprana de plataformas digitales',
    (SELECT id FROM core."user" WHERE email = 'td@goreos.cl')
WHERE NOT EXISTS (
    SELECT 1 FROM core.dgi_division_interaction
    WHERE division_id = (SELECT id FROM core.organization WHERE code = 'DIV-DIFOI' AND deleted_at IS NULL)
      AND interaction_date = CURRENT_DATE - INTERVAL '2 days'
      AND created_by_id = (SELECT id FROM core."user" WHERE email = 'td@goreos.cl')
);


COMMIT;

-- Verificación:
-- SELECT description FROM core.dgi_ar_decision WHERE description LIKE 'DEMO-%';
-- SELECT code FROM core.dgi_escalation WHERE code LIKE 'DEMO-%';
-- SELECT code, name FROM core.dgi_service WHERE code LIKE 'DEMO-%';
-- SELECT code FROM core.dgi_service_request WHERE code LIKE 'DEMO-%';
