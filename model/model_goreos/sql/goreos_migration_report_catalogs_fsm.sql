-- =============================================================================
-- GORE_OS — Catálogos y autoridad DB del flujo de informes DGI
-- =============================================================================

BEGIN;

INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
('dgi_report_type', 'FLASH', 'Flash', 'Informe urgente y conciso', 1),
('dgi_report_type', 'SEMANAL', 'Semanal', 'Informe semanal de gestión', 2),
('dgi_report_type', 'MENSUAL', 'Mensual', 'Informe mensual de gestión', 3),
('dgi_report_type', 'TEMATICO', 'Temático', 'Informe sobre una materia específica', 4)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order;

INSERT INTO ref.category
    (scheme, code, label, description, sort_order, valid_transitions)
VALUES
('dgi_report_status', 'BORRADOR', 'Borrador', 'Informe en elaboración', 1, '["EN_REVISION"]'::jsonb),
('dgi_report_status', 'EN_REVISION', 'En Revisión', 'Informe en revisión por jefatura', 2, '["BORRADOR", "ENVIADO"]'::jsonb),
('dgi_report_status', 'ENVIADO', 'Enviado', 'Informe enviado a su destinatario', 3, '[]'::jsonb)
ON CONFLICT (scheme, code) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    valid_transitions = EXCLUDED.valid_transitions;

DROP TRIGGER IF EXISTS trg_dgi_report_status_transition ON core.dgi_report;
CREATE TRIGGER trg_dgi_report_status_transition
BEFORE UPDATE OF status_id ON core.dgi_report
FOR EACH ROW
EXECUTE FUNCTION public.fn_validate_state_transition('status_id');

INSERT INTO core.schema_migration (filename, applied_by)
VALUES ('goreos_migration_report_catalogs_fsm.sql', 'codex')
ON CONFLICT (filename) DO NOTHING;

COMMIT;
