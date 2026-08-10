-- =============================================================================
-- GORE_OS — Catálogos y autoridad DB del ciclo de vida de indicadores DGI
-- =============================================================================

BEGIN;

INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_indicator_dimension', 'PRESUPUESTO', 'Presupuesto', 'Ejecución y gestión presupuestaria', 1),
('dgi_indicator_dimension', 'CARTERA_IPR', 'Cartera IPR', 'Estado agregado de la cartera de iniciativas', 2),
('dgi_indicator_dimension', 'CONVENIOS', 'Convenios', 'Gestión y vigencia de convenios', 3),
('dgi_indicator_dimension', 'RIESGOS', 'Riesgos', 'Alertas, problemas y riesgos operacionales', 4),
('dgi_indicator_dimension', 'TDE', 'Transformación Digital', 'Transformación digital del Estado', 5),
('dgi_signal', 'VERDE', 'Verde', 'Resultado dentro del rango esperado', 1),
('dgi_signal', 'AMARILLO', 'Amarillo', 'Resultado que requiere atención', 2),
('dgi_signal', 'ROJO', 'Rojo', 'Resultado crítico', 3)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

INSERT INTO ref.category
    (scheme, code, label, description, sort_order, valid_transitions)
VALUES
('dgi_indicator_lifecycle', 'BORRADOR', 'Borrador', 'Indicador en definición', 1, '["APROBADO"]'::jsonb),
('dgi_indicator_lifecycle', 'APROBADO', 'Aprobado', 'Indicador aprobado, aún no vigente', 2, '["VIGENTE", "BORRADOR"]'::jsonb),
('dgi_indicator_lifecycle', 'VIGENTE', 'Vigente', 'Indicador activo', 3, '["DEPRECADO", "APROBADO"]'::jsonb),
('dgi_indicator_lifecycle', 'DEPRECADO', 'Deprecado', 'Indicador retirado', 4, '[]'::jsonb)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    valid_transitions = EXCLUDED.valid_transitions;

DROP TRIGGER IF EXISTS trg_dgi_indicator_lifecycle_transition
    ON core.dgi_indicator;

CREATE TRIGGER trg_dgi_indicator_lifecycle_transition
BEFORE UPDATE OF lifecycle_status_id ON core.dgi_indicator
FOR EACH ROW
EXECUTE FUNCTION public.fn_validate_state_transition('lifecycle_status_id');

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_indicator_catalogs_fsm.sql', 'codex')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
