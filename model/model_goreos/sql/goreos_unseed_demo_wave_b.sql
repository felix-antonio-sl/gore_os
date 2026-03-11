-- =============================================================================
-- GORE_OS — Remove Demo Data Wave B
-- =============================================================================
-- Removes ONLY DEMO- records from Wave B tables.
-- Safe to run multiple times. Order respects FK dependencies.
-- =============================================================================

BEGIN;

-- SLAs depend on services
DELETE FROM core.dgi_sla
WHERE service_id IN (SELECT id FROM core.dgi_service WHERE code LIKE 'DEMO-%');

-- Service requests depend on services
DELETE FROM core.dgi_service_request
WHERE code LIKE 'DEMO-%';

-- Services
DELETE FROM core.dgi_service
WHERE code LIKE 'DEMO-%';

-- Escalations
DELETE FROM core.dgi_escalation
WHERE code LIKE 'DEMO-%';

-- AR Decisions
DELETE FROM core.dgi_ar_decision
WHERE description LIKE 'DEMO-%';

-- Division interactions (no code column — match by created_by DGI users + recent dates)
DELETE FROM core.dgi_division_interaction
WHERE created_by_id IN (
    SELECT id FROM core."user"
    WHERE email IN ('control.gestion@goreos.cl', 'procesos@goreos.cl', 'td@goreos.cl')
)
AND interaction_date >= CURRENT_DATE - INTERVAL '30 days';

COMMIT;

-- Verificación:
-- SELECT COUNT(*) FROM core.dgi_service WHERE code LIKE 'DEMO-%';           -- 0
-- SELECT COUNT(*) FROM core.dgi_escalation WHERE code LIKE 'DEMO-%';        -- 0
-- SELECT COUNT(*) FROM core.dgi_ar_decision WHERE description LIKE 'DEMO-%'; -- 0
