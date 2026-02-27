-- Rollback Wave 3: Revert phase reconciliation (set mcd_phase_id back to NULL
-- for records that were reconciled by status code).
-- SAFE: only affects rows where status implies phase was auto-set.

BEGIN;

UPDATE core.ipr SET mcd_phase_id = NULL
WHERE status_id IN (
    SELECT id FROM ref.category WHERE scheme = 'ipr_state'
    AND code IN ('EN_EJECUCION', 'CERRADO', 'EN_RENDICION')
)
AND deleted_at IS NULL;

COMMIT;
