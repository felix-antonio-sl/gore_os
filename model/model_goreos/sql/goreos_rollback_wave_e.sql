-- ═══════════════════════════════════════════════════════════════════════════════
-- Rollback Wave E: Crisis & Control
-- ═══════════════════════════════════════════════════════════════════════════════
BEGIN;

-- E-3: Remove bridge column
ALTER TABLE core.dgi_ar_decision DROP COLUMN IF EXISTS source_session_id;

-- E-4: Remove risk alert type
DELETE FROM ref.category WHERE scheme = 'alert_type' AND code = 'RIESGO_ALTO';

-- E-6: Remove audit event_type codes
DELETE FROM ref.category
WHERE scheme = 'event_type'
  AND code IN (
    'RISK_CREATED', 'RISK_STATUS_CHANGE',
    'ESCALATION_CREATED', 'ESCALATION_STATUS_CHANGE',
    'ALERT_CREATED', 'ALERT_ATTENDED',
    'MEETING_STARTED', 'MEETING_ENDED',
    'DECISION_CREATED', 'DECISION_STATUS_CHANGE'
  );

-- Remove migration record
DELETE FROM core.schema_migration WHERE filename = 'goreos_migration_wave_e.sql';

COMMIT;
