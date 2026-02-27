-- Wave 3: Reconciliar IPRs con status conocido pero sin mcd_phase.
-- SAFE: solo actualiza mcd_phase_id. El trigger fn_validate_state_transition
-- solo dispara en cambios de status_id, no de mcd_phase_id.
-- Idempotente: WHERE mcd_phase_id IS NULL.

BEGIN;

-- EN_EJECUCION → F4 (~330 filas)
UPDATE core.ipr
SET mcd_phase_id = (SELECT id FROM ref.category WHERE scheme = 'mcd_phase' AND code = 'F4')
WHERE status_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_state' AND code = 'EN_EJECUCION')
  AND mcd_phase_id IS NULL AND deleted_at IS NULL;

-- CERRADO → F5 (~1,296 filas)
UPDATE core.ipr
SET mcd_phase_id = (SELECT id FROM ref.category WHERE scheme = 'mcd_phase' AND code = 'F5')
WHERE status_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_state' AND code = 'CERRADO')
  AND mcd_phase_id IS NULL AND deleted_at IS NULL;

-- EN_RENDICION → F5 (~12 filas)
UPDATE core.ipr
SET mcd_phase_id = (SELECT id FROM ref.category WHERE scheme = 'mcd_phase' AND code = 'F5')
WHERE status_id = (SELECT id FROM ref.category WHERE scheme = 'ipr_state' AND code = 'EN_RENDICION')
  AND mcd_phase_id IS NULL AND deleted_at IS NULL;

-- ANULADO → no asignar fase (terminal cross-cutting)

COMMIT;
