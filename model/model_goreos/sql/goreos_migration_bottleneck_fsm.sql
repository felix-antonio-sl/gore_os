-- =============================================================================
-- GORE_OS — Autoridad DB para el ciclo de investigación de cuellos de botella
-- =============================================================================

BEGIN;

INSERT INTO ref.category
    (scheme, code, label, description, sort_order, valid_transitions)
VALUES
('dgi_bottleneck_status', 'DETECTADO', 'Detectado', 'Cuello de botella detectado, pendiente de verificación', 1, '["VERIFICADO", "CERRADO"]'::jsonb),
('dgi_bottleneck_status', 'VERIFICADO', 'Verificado', 'Hallazgo confirmado', 2, '["ANALIZADO", "CERRADO"]'::jsonb),
('dgi_bottleneck_status', 'ANALIZADO', 'Analizado', 'Causa raíz analizada', 3, '["PROPUESTO", "CERRADO"]'::jsonb),
('dgi_bottleneck_status', 'PROPUESTO', 'Propuesto', 'Solución propuesta', 4, '["IMPLEMENTADO", "CERRADO"]'::jsonb),
('dgi_bottleneck_status', 'IMPLEMENTADO', 'Implementado', 'Solución implementada, pendiente de cierre', 5, '["CERRADO"]'::jsonb),
('dgi_bottleneck_status', 'CERRADO', 'Cerrado', 'Investigación cerrada', 6, '[]'::jsonb)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    valid_transitions = EXCLUDED.valid_transitions;

DROP TRIGGER IF EXISTS trg_dgi_bottleneck_status_transition
    ON core.dgi_bottleneck_investigation;

CREATE TRIGGER trg_dgi_bottleneck_status_transition
BEFORE UPDATE OF status_id ON core.dgi_bottleneck_investigation
FOR EACH ROW
EXECUTE FUNCTION public.fn_validate_state_transition('status_id');

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_bottleneck_fsm.sql', 'codex')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
