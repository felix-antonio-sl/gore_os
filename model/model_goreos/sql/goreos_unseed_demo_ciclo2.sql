-- =============================================================================
-- GORE_OS — Remover Datos Demo Ciclo 2
-- =============================================================================
-- Elimina SOLO los registros demo (prefijo DEMO-)
-- Los catálogos estructurales pertenecen a goreos_seed.sql y NO se eliminan
-- La app sigue funcionando después de esto (sin datos demo, pero sin errores)
-- =============================================================================

BEGIN;

-- Cuotas de convenios demo
DELETE FROM core.agreement_installment
WHERE agreement_id IN (
    SELECT id FROM core.agreement WHERE agreement_number LIKE 'DEMO-%'
);

-- CDPs demo
DELETE FROM core.budget_commitment
WHERE commitment_number LIKE 'DEMO-%';

-- Arrastres de programas demo
DELETE FROM core.budget_carryover
WHERE budget_program_id IN (
    SELECT id FROM core.budget_program WHERE code LIKE 'DEMO-%'
);

-- Convenios demo
DELETE FROM core.agreement
WHERE agreement_number LIKE 'DEMO-%';

-- Programas presupuestarios demo
DELETE FROM core.budget_program
WHERE code LIKE 'DEMO-%';

COMMIT;

-- Verificación:
-- SELECT COUNT(*) FROM core.budget_program WHERE code LIKE 'DEMO-%';  -- debe ser 0
-- SELECT COUNT(*) FROM core.agreement WHERE agreement_number LIKE 'DEMO-%';  -- debe ser 0
