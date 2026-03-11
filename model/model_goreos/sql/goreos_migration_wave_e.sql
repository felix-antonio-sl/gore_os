-- ═══════════════════════════════════════════════════════════════════════════════
-- Wave E: Crisis & Control — risk API, command center, audit trail
-- ═══════════════════════════════════════════════════════════════════════════════
BEGIN;

-- Track migration
INSERT INTO core.schema_migration (filename)
VALUES ('goreos_migration_wave_e.sql')
ON CONFLICT (filename) DO NOTHING;

-- ─── E-3: Bridge crisis meetings → AR decisions ────────────────────────────
ALTER TABLE core.dgi_ar_decision
    ADD COLUMN IF NOT EXISTS source_session_id UUID REFERENCES core.session(id);

-- ─── E-4: Alert type for risk-generated alerts ───────────────────────────
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
    ('alert_type', 'RIESGO_ALTO', 'Riesgo Alto', 'Alerta generada por riesgo de probabilidad alta o muy alta', 13)
ON CONFLICT DO NOTHING;

-- ─── E-6: New event_type codes for audit trail ─────────────────────────────
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
    ('event_type', 'RISK_CREATED',               'Riesgo Creado',              'Nuevo riesgo registrado', 20),
    ('event_type', 'RISK_STATUS_CHANGE',          'Cambio Estado Riesgo',       'Transición de estado de riesgo', 21),
    ('event_type', 'ESCALATION_CREATED',          'Escalamiento Creado',        'Nuevo escalamiento registrado', 22),
    ('event_type', 'ESCALATION_STATUS_CHANGE',    'Cambio Estado Escalamiento', 'Transición de estado de escalamiento', 23),
    ('event_type', 'ALERT_CREATED',               'Alerta Creada',              'Nueva alerta generada', 24),
    ('event_type', 'ALERT_ATTENDED',              'Alerta Atendida',            'Alerta marcada como atendida', 25),
    ('event_type', 'MEETING_STARTED',             'Reunión Iniciada',           'Reunión de crisis iniciada', 26),
    ('event_type', 'MEETING_ENDED',               'Reunión Finalizada',         'Reunión de crisis finalizada', 27),
    ('event_type', 'DECISION_CREATED',            'Decisión Creada',            'Nueva decisión AR registrada', 28),
    ('event_type', 'DECISION_STATUS_CHANGE',      'Cambio Estado Decisión',     'Transición de decisión AR', 29)
ON CONFLICT DO NOTHING;

COMMIT;
