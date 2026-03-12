-- ============================================================================
-- Migration: Lifecycle Wave 1 — Grafo de Transiciones SSOT-Aligned
-- Date: 2026-03-11
-- Description:
--   1A. Nuevos estados SSOT P1: TERMINADO_ANTICIPADAMENTE, CONTRATO_FIRMADO
--   1B. Bifurcación F4: EN_FORMALIZACION → [FORMALIZADO | EN_LICITACION]
--   1C. ANULADO + TERMINADO_ANTICIPADAMENTE cross-cutting
--   1D. AD → [EN_LICITACION, CDP_EMITIDO] para ambos flujos
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1A. Nuevos estados SSOT P1
-- ============================================================================

-- TERMINADO_ANTICIPADAMENTE: Terminal state para IPRs que finalizan antes de
-- completar el ciclo. Distinto de ANULADO (nunca debió existir) y CERRADO
-- (completó ciclo normal).
INSERT INTO ref.category (scheme, code, label, description, sort_order)
VALUES ('ipr_state', 'TERMINADO_ANTICIPADAMENTE', 'Terminado Anticipadamente',
        'IPR terminada antes de completar ciclo por decisión administrativa o fuerza mayor',
        30)
ON CONFLICT (scheme, code) DO NOTHING;

-- Terminal: sin transiciones salientes
UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'TERMINADO_ANTICIPADAMENTE';

-- CONTRATO_FIRMADO: Entre ADJUDICADO y EN_OBRA en flujo de proyectos.
-- ADJUDICADO = licitación adjudicada, CONTRATO_FIRMADO = contrato firmado.
INSERT INTO ref.category (scheme, code, label, description, sort_order)
VALUES ('ipr_state', 'CONTRATO_FIRMADO', 'Contrato Firmado',
        'Contrato firmado entre GORE y adjudicatario — inicio de ejecución de obra',
        33)
ON CONFLICT (scheme, code) DO NOTHING;

UPDATE ref.category SET valid_transitions = '["EN_OBRA", "SUSPENDIDO", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'CONTRATO_FIRMADO';

-- ============================================================================
-- 1B. Bifurcación F4: EN_FORMALIZACION → [FORMALIZADO | EN_LICITACION]
-- ============================================================================

-- EN_FORMALIZACION ahora puede ir a FORMALIZADO (programas) o EN_LICITACION (proyectos)
UPDATE ref.category SET valid_transitions = '["FORMALIZADO", "EN_LICITACION", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_FORMALIZACION';

-- ADJUDICADO ahora va a CONTRATO_FIRMADO (no directamente a EN_OBRA)
UPDATE ref.category SET valid_transitions = '["CONTRATO_FIRMADO", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'ADJUDICADO';

-- AD también puede ir a CDP_EMITIDO (como RS/FI) — no solo EN_LICITACION
UPDATE ref.category SET valid_transitions = '["EN_LICITACION", "CDP_EMITIDO", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'AD';

-- ============================================================================
-- 1C. ANULADO + TERMINADO_ANTICIPADAMENTE cross-cutting
-- ============================================================================

-- TERMINADO_ANTICIPADAMENTE accesible desde estados de ejecución F4
UPDATE ref.category SET valid_transitions = '["EN_RENDICION", "SUSPENDIDO", "CERRADO", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_EJECUCION';

UPDATE ref.category SET valid_transitions = '["RECEPCION_PROVISORIA", "SUSPENDIDO", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_OBRA';

-- SUSPENDIDO: agregar TERMINADO_ANTICIPADAMENTE
UPDATE ref.category SET valid_transitions = '["EN_EJECUCION", "EN_OBRA", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'SUSPENDIDO';

-- EN_LICITACION: agregar TERMINADO_ANTICIPADAMENTE
UPDATE ref.category SET valid_transitions = '["ADJUDICADO", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_LICITACION';

-- RECEPCION_PROVISORIA: agregar ANULADO + TERMINADO_ANTICIPADAMENTE
UPDATE ref.category SET valid_transitions = '["RECEPCION_DEFINITIVA", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'RECEPCION_PROVISORIA';

-- RECEPCION_DEFINITIVA: agregar TERMINADO_ANTICIPADAMENTE
UPDATE ref.category SET valid_transitions = '["EN_RENDICION", "CERRADO", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'RECEPCION_DEFINITIVA';

-- EN_RENDICION: agregar TERMINADO_ANTICIPADAMENTE
UPDATE ref.category SET valid_transitions = '["CERRADO", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_RENDICION';

-- FORMALIZADO: agregar ANULADO + TERMINADO_ANTICIPADAMENTE
UPDATE ref.category SET valid_transitions = '["EN_EJECUCION", "TERMINADO_ANTICIPADAMENTE", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'FORMALIZADO';

-- CDP_EMITIDO: agregar ANULADO
UPDATE ref.category SET valid_transitions = '["EN_FORMALIZACION", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'CDP_EMITIDO';

-- EN_EVALUACION: agregar ANULADO
UPDATE ref.category SET valid_transitions = '["RS", "FI", "FC", "OT", "RF", "ITF", "AT", "AD", "ANULADO"]'::jsonb
WHERE scheme = 'ipr_state' AND code = 'EN_EVALUACION';

-- ============================================================================
-- Track migration in schema_migration
-- ============================================================================
INSERT INTO core.schema_migration (filename, applied_at)
VALUES ('goreos_migration_lifecycle_wave1.sql', NOW())
ON CONFLICT (filename) DO NOTHING;

COMMIT;
