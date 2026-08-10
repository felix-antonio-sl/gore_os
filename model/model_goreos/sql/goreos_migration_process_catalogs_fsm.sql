-- =============================================================================
-- GORE_OS — Catálogos y autoridad DB del modelamiento de procesos DGI
-- =============================================================================

BEGIN;

INSERT INTO ref.category
    (scheme, code, label, description, sort_order, valid_transitions)
VALUES
('dgi_process_status', 'IDENTIFICADO', 'Identificado', 'Proceso identificado', 1, '["EN_LEVANTAMIENTO", "SUSPENDIDO"]'::jsonb),
('dgi_process_status', 'EN_LEVANTAMIENTO', 'En Levantamiento', 'Proceso en levantamiento', 2, '["MODELADO", "IDENTIFICADO", "SUSPENDIDO"]'::jsonb),
('dgi_process_status', 'MODELADO', 'Modelado', 'Proceso modelado', 3, '["VALIDADO", "EN_LEVANTAMIENTO", "SUSPENDIDO"]'::jsonb),
('dgi_process_status', 'VALIDADO', 'Validado', 'Modelo validado', 4, '["PUBLICADO", "MODELADO", "SUSPENDIDO"]'::jsonb),
('dgi_process_status', 'PUBLICADO', 'Publicado', 'Proceso publicado', 5, '["SUSPENDIDO"]'::jsonb),
('dgi_process_status', 'SUSPENDIDO', 'Suspendido', 'Proceso temporalmente suspendido', 6, '["IDENTIFICADO"]'::jsonb),
('dgi_bpmn_status', 'BORRADOR', 'Borrador', 'Modelo BPMN en edición', 1, '["REVISION"]'::jsonb),
('dgi_bpmn_status', 'REVISION', 'En Revisión', 'Modelo BPMN en revisión', 2, '["BORRADOR", "VALIDADO"]'::jsonb),
('dgi_bpmn_status', 'VALIDADO', 'Validado', 'Modelo BPMN validado', 3, '["BORRADOR"]'::jsonb)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    valid_transitions = EXCLUDED.valid_transitions;

INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_bpmn_type', 'AS_IS', 'Estado Actual', 'Modelo del proceso vigente', 1),
('dgi_bpmn_type', 'TO_BE', 'Estado Futuro', 'Modelo del proceso objetivo', 2)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

DROP TRIGGER IF EXISTS trg_dgi_process_status_transition ON core.dgi_process;
CREATE TRIGGER trg_dgi_process_status_transition
BEFORE UPDATE OF status_id ON core.dgi_process
FOR EACH ROW
EXECUTE FUNCTION public.fn_validate_state_transition('status_id');

DROP TRIGGER IF EXISTS trg_dgi_bpmn_status_transition ON core.dgi_bpmn_model;
CREATE TRIGGER trg_dgi_bpmn_status_transition
BEFORE UPDATE OF status_id ON core.dgi_bpmn_model
FOR EACH ROW
EXECUTE FUNCTION public.fn_validate_state_transition('status_id');

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_process_catalogs_fsm.sql', 'codex')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
