-- =============================================================================
-- MIGRACIÓN: Remaining Fixes — Schemes, CHECKs, Partial Index, FSM Transitions
-- =============================================================================
-- Fecha: 2026-03-10
-- Descripción: Cierra los 4 items pendientes de la auditoría categórica:
--   1. 6 nuevos schemes + 6 CHECK constraints (vehicle, risk, inventory, planning)
--   2. UNIQUE partial index on ipr_party (replace non-partial)
--   3. ~11 FSMs: poblar valid_transitions + crear triggers (DGI + scaffold)
--
-- Fuente de verdad: SSOT /gorenuble/knowledge/domains/gn/01_fundamentos/ssot/
-- =============================================================================

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════════════
-- PARTE 1: 6 nuevos schemes + 6 CHECK constraints
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─── vehicle_type (SSOT: scaffold, asset management) ─────────────────────────
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
  ('vehicle_type', 'SEDAN',       'Sedán',       'Vehículo tipo sedán', 1),
  ('vehicle_type', 'SUV',         'SUV',         'Vehículo todoterreno', 2),
  ('vehicle_type', 'CAMIONETA',   'Camioneta',   'Camioneta de trabajo', 3),
  ('vehicle_type', 'FURGON',      'Furgón',      'Furgón de transporte', 4),
  ('vehicle_type', 'BUS',         'Bus',         'Transporte colectivo', 5),
  ('vehicle_type', 'CAMION',      'Camión',      'Vehículo de carga', 6),
  ('vehicle_type', 'MOTOCICLETA', 'Motocicleta', 'Motocicleta institucional', 7)
ON CONFLICT (scheme, code) DO NOTHING;

ALTER TABLE core.vehicle
  ADD CONSTRAINT chk_vehicle_type_scheme
  CHECK (vehicle_type_id IS NULL OR fn_validate_category_scheme(vehicle_type_id, 'vehicle_type'));

-- ─── fuel_type ───────────────────────────────────────────────────────────────
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
  ('fuel_type', 'GASOLINA',  'Gasolina',  'Gasolina 93/95/97', 1),
  ('fuel_type', 'DIESEL',    'Diésel',    'Petróleo diésel', 2),
  ('fuel_type', 'ELECTRICO', 'Eléctrico', 'Vehículo eléctrico', 3),
  ('fuel_type', 'HIBRIDO',   'Híbrido',   'Motor híbrido', 4),
  ('fuel_type', 'GNC',       'GNC',       'Gas natural comprimido', 5)
ON CONFLICT (scheme, code) DO NOTHING;

ALTER TABLE core.vehicle
  ADD CONSTRAINT chk_fuel_type_scheme
  CHECK (fuel_type_id IS NULL OR fn_validate_category_scheme(fuel_type_id, 'fuel_type'));

-- ─── risk_probability ────────────────────────────────────────────────────────
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
  ('risk_probability', 'MUY_BAJA', 'Muy Baja', 'Probabilidad <10%', 1),
  ('risk_probability', 'BAJA',     'Baja',     'Probabilidad 10-30%', 2),
  ('risk_probability', 'MEDIA',    'Media',    'Probabilidad 30-60%', 3),
  ('risk_probability', 'ALTA',     'Alta',     'Probabilidad 60-85%', 4),
  ('risk_probability', 'MUY_ALTA', 'Muy Alta', 'Probabilidad >85%', 5)
ON CONFLICT (scheme, code) DO NOTHING;

ALTER TABLE core.risk
  ADD CONSTRAINT chk_risk_probability_scheme
  CHECK (probability_id IS NULL OR fn_validate_category_scheme(probability_id, 'risk_probability'));

-- ─── risk_status ─────────────────────────────────────────────────────────────
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
  ('risk_status', 'IDENTIFICADO',   'Identificado',   'Riesgo detectado, pendiente evaluación', 1),
  ('risk_status', 'EN_EVALUACION',  'En Evaluación',  'Evaluando impacto y probabilidad', 2),
  ('risk_status', 'EN_MITIGACION',  'En Mitigación',  'Plan de mitigación en ejecución', 3),
  ('risk_status', 'MITIGADO',       'Mitigado',       'Acciones de mitigación completadas', 4),
  ('risk_status', 'ACEPTADO',       'Aceptado',       'Riesgo aceptado sin mitigación', 5),
  ('risk_status', 'CERRADO',        'Cerrado',        'Riesgo ya no aplica', 6)
ON CONFLICT (scheme, code) DO NOTHING;

ALTER TABLE core.risk
  ADD CONSTRAINT chk_risk_status_scheme
  CHECK (status_id IS NULL OR fn_validate_category_scheme(status_id, 'risk_status'));

-- ─── asset_status (inventory items) ──────────────────────────────────────────
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
  ('asset_status', 'EN_USO',        'En Uso',        'Activo en operación', 1),
  ('asset_status', 'EN_BODEGA',     'En Bodega',     'Almacenado sin asignar', 2),
  ('asset_status', 'EN_REPARACION', 'En Reparación', 'En mantenimiento correctivo', 3),
  ('asset_status', 'EN_TRANSITO',   'En Tránsito',   'En proceso de traslado', 4),
  ('asset_status', 'DADO_DE_BAJA',  'Dado de Baja',  'Retirado del inventario', 5)
ON CONFLICT (scheme, code) DO NOTHING;

ALTER TABLE core.inventory_item
  ADD CONSTRAINT chk_asset_status_scheme
  CHECK (current_status_id IS NULL OR fn_validate_category_scheme(current_status_id, 'asset_status'));

-- ─── instrument_type (SSOT ssot-ecosistema: 13 planning instruments) ─────────
INSERT INTO ref.category (scheme, code, label, description, sort_order) VALUES
  -- Strategic (7)
  ('instrument_type', 'ERD',             'ERD',                     'Estrategia Regional de Desarrollo', 1),
  ('instrument_type', 'PROT',            'PROT',                    'Plan Regional de Ordenamiento Territorial', 2),
  ('instrument_type', 'PLADETUR',        'PLADETUR',                'Plan de Desarrollo Turístico', 3),
  ('instrument_type', 'PLAN_DIRECTOR',   'Plan Director',           'Plan director sectorial', 4),
  ('instrument_type', 'PLAN_MAESTRO',    'Plan Maestro',            'Plan maestro territorial', 5),
  ('instrument_type', 'PLAN_SECTORIAL',  'Plan Sectorial',          'Plan sectorial temático', 6),
  ('instrument_type', 'POLITICA_REG',    'Política Regional',       'Política regional de largo plazo', 7),
  -- Operational (6)
  ('instrument_type', 'PROPIR',          'PROPIR',                  'Programa Público de Inversión Regional', 8),
  ('instrument_type', 'ARI',             'ARI',                     'Anteproyecto Regional de Inversiones', 9),
  ('instrument_type', 'PMU',             'PMU',                     'Programa de Mejoramiento Urbano', 10),
  ('instrument_type', 'PROG_PUBLICO',    'Programa Público',        'Programa público regional', 11),
  ('instrument_type', 'CDT',             'CDT',                     'Convenio de Transferencia', 12),
  ('instrument_type', 'PLAN_ACCION',     'Plan de Acción',          'Plan de acción operativo', 13)
ON CONFLICT (scheme, code) DO NOTHING;

ALTER TABLE core.planning_instrument
  ADD CONSTRAINT chk_instrument_type_scheme
  CHECK (instrument_type_id IS NULL OR fn_validate_category_scheme(instrument_type_id, 'instrument_type'));

-- ═══════════════════════════════════════════════════════════════════════════════
-- PARTE 2: UNIQUE partial index on ipr_party (replace non-partial)
-- ═══════════════════════════════════════════════════════════════════════════════
-- El UNIQUE actual incluye soft-deleted rows, bloqueando re-inserción.
-- Reemplazamos con partial index que excluye deleted_at IS NOT NULL.

ALTER TABLE core.ipr_party DROP CONSTRAINT IF EXISTS uq_ipr_party_role;

CREATE UNIQUE INDEX uq_ipr_party_role
  ON core.ipr_party (ipr_id, organization_id, party_role_id)
  WHERE deleted_at IS NULL;

-- ═══════════════════════════════════════════════════════════════════════════════
-- PARTE 3: FSM valid_transitions + triggers para DGI + scaffold entities
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─── dgi_initiative_status: Kanban (any→any except terminal) ─────────────────
-- BACKLOG ↔ EN_CURSO ↔ REVISION → COMPLETADO (libre, WIP en Python)
UPDATE ref.category SET valid_transitions = '["EN_CURSO", "REVISION", "COMPLETADO"]'::jsonb
WHERE scheme = 'dgi_initiative_status' AND code = 'BACKLOG';

UPDATE ref.category SET valid_transitions = '["BACKLOG", "REVISION", "COMPLETADO"]'::jsonb
WHERE scheme = 'dgi_initiative_status' AND code = 'EN_CURSO';

UPDATE ref.category SET valid_transitions = '["BACKLOG", "EN_CURSO", "COMPLETADO"]'::jsonb
WHERE scheme = 'dgi_initiative_status' AND code = 'REVISION';

UPDATE ref.category SET valid_transitions = '["BACKLOG"]'::jsonb
WHERE scheme = 'dgi_initiative_status' AND code = 'COMPLETADO';

DROP TRIGGER IF EXISTS trg_dgi_initiative_status_transition ON core.dgi_initiative;
CREATE TRIGGER trg_dgi_initiative_status_transition
    BEFORE UPDATE ON core.dgi_initiative
    FOR EACH ROW
    EXECUTE FUNCTION fn_validate_state_transition('status_id');

-- ─── dgi_report_status: BORRADOR → EN_REVISION ↔ BORRADOR, EN_REVISION → APROBADO → ENVIADO
UPDATE ref.category SET valid_transitions = '["EN_REVISION"]'::jsonb
WHERE scheme = 'dgi_report_status' AND code = 'BORRADOR';

UPDATE ref.category SET valid_transitions = '["BORRADOR", "APROBADO", "ENVIADO"]'::jsonb
WHERE scheme = 'dgi_report_status' AND code = 'EN_REVISION';

UPDATE ref.category SET valid_transitions = '["ENVIADO"]'::jsonb
WHERE scheme = 'dgi_report_status' AND code = 'APROBADO';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'dgi_report_status' AND code = 'ENVIADO';

DROP TRIGGER IF EXISTS trg_dgi_report_status_transition ON core.dgi_report;
CREATE TRIGGER trg_dgi_report_status_transition
    BEFORE UPDATE ON core.dgi_report
    FOR EACH ROW
    EXECUTE FUNCTION fn_validate_state_transition('status_id');

-- ─── dgi_bpmn_status: BORRADOR → REVISION → VALIDADO (linear) ───────────────
UPDATE ref.category SET valid_transitions = '["REVISION"]'::jsonb
WHERE scheme = 'dgi_bpmn_status' AND code = 'BORRADOR';

UPDATE ref.category SET valid_transitions = '["BORRADOR", "VALIDADO"]'::jsonb
WHERE scheme = 'dgi_bpmn_status' AND code = 'REVISION';

UPDATE ref.category SET valid_transitions = '["BORRADOR"]'::jsonb
WHERE scheme = 'dgi_bpmn_status' AND code = 'VALIDADO';

DROP TRIGGER IF EXISTS trg_dgi_bpmn_status_transition ON core.dgi_bpmn_model;
CREATE TRIGGER trg_dgi_bpmn_status_transition
    BEFORE UPDATE ON core.dgi_bpmn_model
    FOR EACH ROW
    EXECUTE FUNCTION fn_validate_state_transition('status_id');

-- ─── dgi_session_status: PLANIFICADA → AGENDA_LISTA → REALIZADA → ACTA_PENDIENTE → CERRADA
UPDATE ref.category SET valid_transitions = '["AGENDA_LISTA", "CANCELADA"]'::jsonb
WHERE scheme = 'dgi_session_status' AND code = 'PLANIFICADA';

UPDATE ref.category SET valid_transitions = '["REALIZADA", "PLANIFICADA", "CANCELADA"]'::jsonb
WHERE scheme = 'dgi_session_status' AND code = 'AGENDA_LISTA';

UPDATE ref.category SET valid_transitions = '["ACTA_PENDIENTE"]'::jsonb
WHERE scheme = 'dgi_session_status' AND code = 'REALIZADA';

UPDATE ref.category SET valid_transitions = '["CERRADA"]'::jsonb
WHERE scheme = 'dgi_session_status' AND code = 'ACTA_PENDIENTE';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'dgi_session_status' AND code = 'CERRADA';

-- Note: CANCELADA not in seed — check if it exists, add if not
INSERT INTO ref.category (scheme, code, label, description, sort_order)
SELECT 'dgi_session_status', 'CANCELADA', 'Cancelada', 'Sesión cancelada', 6
WHERE NOT EXISTS (
    SELECT 1 FROM ref.category WHERE scheme = 'dgi_session_status' AND code = 'CANCELADA'
);
UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'dgi_session_status' AND code = 'CANCELADA';

DROP TRIGGER IF EXISTS trg_dgi_session_status_transition ON core.dgi_committee_session;
CREATE TRIGGER trg_dgi_session_status_transition
    BEFORE UPDATE ON core.dgi_committee_session
    FOR EACH ROW
    EXECUTE FUNCTION fn_validate_state_transition('status_id');

-- ─── dgi_alert_status: GENERADA → RECONOCIDA → INVESTIGANDO → ACCION → RESUELTA → CERRADA
UPDATE ref.category SET valid_transitions = '["RECONOCIDA"]'::jsonb
WHERE scheme = 'dgi_alert_status' AND code = 'GENERADA';

UPDATE ref.category SET valid_transitions = '["INVESTIGANDO", "ACCION", "CERRADA"]'::jsonb
WHERE scheme = 'dgi_alert_status' AND code = 'RECONOCIDA';

UPDATE ref.category SET valid_transitions = '["ACCION", "CERRADA"]'::jsonb
WHERE scheme = 'dgi_alert_status' AND code = 'INVESTIGANDO';

UPDATE ref.category SET valid_transitions = '["RESUELTA", "CERRADA"]'::jsonb
WHERE scheme = 'dgi_alert_status' AND code = 'ACCION';

UPDATE ref.category SET valid_transitions = '["CERRADA"]'::jsonb
WHERE scheme = 'dgi_alert_status' AND code = 'RESUELTA';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'dgi_alert_status' AND code = 'CERRADA';

-- Note: dgi_alert_status currently has no referencing table with trigger.
-- No trigger to create — this scheme is used only for future DGI alert management.

-- ─── dgi_source_status: observational (not a real FSM, no trigger) ───────────
-- OK/ATRASADO/SIN_DATOS are computed states, not user-driven transitions.
-- Skip trigger — document as observational.

-- ─── dgi_decree_status: compliance states (VIGENTE/PARCIAL/PENDIENTE) ────────
-- These are assessment states, not workflow FSM. No trigger needed.
-- A decree can be re-assessed in any direction.

-- ─── budget_commitment_status: EMITIDO → VIGENTE → EJECUTADO, any → ANULADO
UPDATE ref.category SET valid_transitions = '["VIGENTE", "ANULADO"]'::jsonb
WHERE scheme = 'budget_commitment_status' AND code = 'EMITIDO';

UPDATE ref.category SET valid_transitions = '["EJECUTADO", "VENCIDO", "ANULADO"]'::jsonb
WHERE scheme = 'budget_commitment_status' AND code = 'VIGENTE';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'budget_commitment_status' AND code = 'EJECUTADO';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'budget_commitment_status' AND code = 'ANULADO';

UPDATE ref.category SET valid_transitions = '["VIGENTE"]'::jsonb
WHERE scheme = 'budget_commitment_status' AND code = 'VENCIDO';

DROP TRIGGER IF EXISTS trg_budget_commitment_status_transition ON core.budget_commitment;
CREATE TRIGGER trg_budget_commitment_status_transition
    BEFORE UPDATE ON core.budget_commitment
    FOR EACH ROW
    EXECUTE FUNCTION fn_validate_state_transition('status_id');

-- ─── risk_status: IDENTIFICADO → EN_EVALUACION → EN_MITIGACION → MITIGADO/ACEPTADO → CERRADO
UPDATE ref.category SET valid_transitions = '["EN_EVALUACION", "ACEPTADO"]'::jsonb
WHERE scheme = 'risk_status' AND code = 'IDENTIFICADO';

UPDATE ref.category SET valid_transitions = '["EN_MITIGACION", "ACEPTADO", "CERRADO"]'::jsonb
WHERE scheme = 'risk_status' AND code = 'EN_EVALUACION';

UPDATE ref.category SET valid_transitions = '["MITIGADO", "CERRADO"]'::jsonb
WHERE scheme = 'risk_status' AND code = 'EN_MITIGACION';

UPDATE ref.category SET valid_transitions = '["CERRADO"]'::jsonb
WHERE scheme = 'risk_status' AND code = 'MITIGADO';

UPDATE ref.category SET valid_transitions = '["CERRADO"]'::jsonb
WHERE scheme = 'risk_status' AND code = 'ACEPTADO';

UPDATE ref.category SET valid_transitions = '[]'::jsonb
WHERE scheme = 'risk_status' AND code = 'CERRADO';

DROP TRIGGER IF EXISTS trg_risk_status_transition ON core.risk;
CREATE TRIGGER trg_risk_status_transition
    BEFORE UPDATE ON core.risk
    FOR EACH ROW
    EXECUTE FUNCTION fn_validate_state_transition('status_id');

-- ═══════════════════════════════════════════════════════════════════════════════
-- REGISTRO
-- ═══════════════════════════════════════════════════════════════════════════════

INSERT INTO core.schema_migration (filename, applied_by)
VALUES (
  'goreos_migration_remaining_fixes.sql',
  'claude-categorical-audit'
)
ON CONFLICT DO NOTHING;

COMMIT;
