-- =============================================================================
-- GORE_OS — Catálogo y autoridad DB de fases DMAIC
-- =============================================================================

BEGIN;

INSERT INTO ref.category
    (scheme, code, label, description, sort_order, valid_transitions)
VALUES
('dgi_dmaic_phase', 'DEFINE', 'Definir', 'Definición del problema y alcance', 1, '["MEASURE", "ANALYZE", "IMPROVE", "VERIFY"]'::jsonb),
('dgi_dmaic_phase', 'MEASURE', 'Medir', 'Medición de la línea base', 2, '["ANALYZE", "IMPROVE", "VERIFY"]'::jsonb),
('dgi_dmaic_phase', 'ANALYZE', 'Analizar', 'Análisis de causas raíz', 3, '["IMPROVE", "VERIFY"]'::jsonb),
('dgi_dmaic_phase', 'IMPROVE', 'Mejorar', 'Diseño y prueba de mejoras', 4, '["VERIFY"]'::jsonb),
('dgi_dmaic_phase', 'VERIFY', 'Verificar', 'Verificación y sostenibilidad de la mejora', 5, '[]'::jsonb)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    valid_transitions = EXCLUDED.valid_transitions;

DROP TRIGGER IF EXISTS trg_dgi_initiative_dmaic_transition ON core.dgi_initiative;
CREATE TRIGGER trg_dgi_initiative_dmaic_transition
BEFORE UPDATE OF dmaic_phase_id ON core.dgi_initiative
FOR EACH ROW
EXECUTE FUNCTION public.fn_validate_state_transition('dmaic_phase_id');

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_dmaic_catalog_fsm.sql', 'codex')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
