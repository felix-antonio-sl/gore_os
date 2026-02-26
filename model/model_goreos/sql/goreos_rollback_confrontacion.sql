-- ============================================================================
-- GORE_OS — Rollback: Migración Categórica de Datos
-- ============================================================================
--
-- Invierte las 7 operaciones de goreos_migration_confrontacion.sql
-- Orden inverso: Op 7 → Op 1
--
-- Uso:
--   docker exec -i goreos_db psql -U goreos -d goreos_model < goreos_rollback_confrontacion.sql
-- ============================================================================

BEGIN;

-- ────────────────────────────────────────────────────────────────────────────
-- Rollback Op 7: Restaurar duplicados legacy (un-soft-delete)
-- ────────────────────────────────────────────────────────────────────────────

UPDATE core.organization SET deleted_at = NULL
WHERE code LIKE 'ORG_GORE-%';

UPDATE core.organization SET deleted_at = NULL
WHERE code = 'ORG-85ea3272';

-- Nota: No revertimos la reasignación de FKs (user.division_id, ipr.sponsor_division_id)
-- porque el pre-flight confirmó 0 FKs activas en duplicados. Si alguna fue reasignada
-- durante la migración, el duplicado restaurado no la recupera automáticamente.


-- ────────────────────────────────────────────────────────────────────────────
-- Rollback Op 6: Eliminar 5 nuevos system_role
-- ────────────────────────────────────────────────────────────────────────────

DELETE FROM ref.category
WHERE scheme = 'system_role'
  AND code IN ('GOBERNADOR', 'CONSEJERO_REGIONAL', 'SECRETARIO_EJECUTIVO',
               'JEFE_DEPARTAMENTO', 'JEFE_UNIDAD');


-- ────────────────────────────────────────────────────────────────────────────
-- Rollback Op 5: Restaurar coalgebra agreement_state original (10 estados)
-- ────────────────────────────────────────────────────────────────────────────

-- Restaurar valid_transitions originales
UPDATE ref.category SET valid_transitions = '["FIRMADO_GORE","EN_NEGOCIACION"]'::jsonb
WHERE scheme='agreement_state' AND code='EN_REVISION_JURIDICA';

UPDATE ref.category SET valid_transitions = '["VIGENTE"]'::jsonb
WHERE scheme='agreement_state' AND code='FIRMADO_CONTRAPARTE';

-- Eliminar los 3 estados nuevos
DELETE FROM ref.category
WHERE scheme = 'agreement_state'
  AND code IN ('EN_REVISION_FINANCIERA', 'VISADO_INTERNO', 'TDR_PENDIENTE');

-- Restaurar sort_order original (1-10)
UPDATE ref.category SET sort_order = CASE code
  WHEN 'BORRADOR' THEN 1
  WHEN 'EN_NEGOCIACION' THEN 2
  WHEN 'EN_REVISION_JURIDICA' THEN 3
  WHEN 'FIRMADO_GORE' THEN 4
  WHEN 'FIRMADO_CONTRAPARTE' THEN 5
  WHEN 'VIGENTE' THEN 6
  WHEN 'EN_MODIFICACION' THEN 7
  WHEN 'VENCIDO' THEN 8
  WHEN 'TERMINADO' THEN 9
  WHEN 'RESCILIADO' THEN 10
END WHERE scheme='agreement_state';


-- ────────────────────────────────────────────────────────────────────────────
-- Rollback Op 4: Eliminar 8 nuevas organizaciones
-- ────────────────────────────────────────────────────────────────────────────

DELETE FROM core.organization
WHERE code IN ('URAI', 'COSOC', 'CTCI', 'DGI',
               'TESORERIA', 'CONTABILIDAD', 'ADQUISICIONES', 'OPERACIONES');


-- ────────────────────────────────────────────────────────────────────────────
-- Rollback Op 3: Restaurar parent_id plano (todo → GORE-NUBLE)
-- ────────────────────────────────────────────────────────────────────────────

UPDATE core.organization SET parent_id = (SELECT id FROM core.organization WHERE code='GORE-NUBLE')
WHERE code IN ('FINANZAS','PERSONAS','OFICINA-PARTES','INVERSIONES','PRESUPUESTO','PREINVERSION','UCR')
  AND deleted_at IS NULL;


-- ────────────────────────────────────────────────────────────────────────────
-- Rollback Op 2: Reclasificar todo de vuelta a DIVISION
-- ────────────────────────────────────────────────────────────────────────────

UPDATE core.organization SET org_type_id = (
  SELECT id FROM ref.category WHERE scheme='org_type' AND code='DIVISION'
) WHERE code IN (
  'GABINETE','COMUNICACIONES','AUDITORIA','DIJ','NUBLE-250','CIES',  -- eran STAFF_UNIT
  'CORE',                                                             -- era ADVISORY_BODY
  'FINANZAS','INVERSIONES','PRESUPUESTO','PERSONAS','PREINVERSION',  -- eran DEPARTAMENTO
  'UCR','OFICINA-PARTES','INFORMATICA','SERVICIOS-GENERALES'         -- eran UNIDAD
) AND deleted_at IS NULL;


-- ────────────────────────────────────────────────────────────────────────────
-- Rollback Op 1: Eliminar 2 nuevos org_type
-- ────────────────────────────────────────────────────────────────────────────

DELETE FROM ref.category
WHERE scheme = 'org_type'
  AND code IN ('STAFF_UNIT', 'ADVISORY_BODY');


-- ────────────────────────────────────────────────────────────────────────────
-- Verificación rollback
-- ────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE
  v_org_types INT; v_roles INT; v_states INT; v_active_orgs INT;
BEGIN
  SELECT COUNT(DISTINCT c.code) INTO v_org_types
  FROM core.organization o JOIN ref.category c ON o.org_type_id = c.id
  WHERE o.deleted_at IS NULL;

  SELECT COUNT(*) INTO v_roles FROM ref.category WHERE scheme='system_role' AND deleted_at IS NULL;
  SELECT COUNT(*) INTO v_states FROM ref.category WHERE scheme='agreement_state' AND deleted_at IS NULL;
  SELECT COUNT(*) INTO v_active_orgs FROM core.organization WHERE deleted_at IS NULL;

  RAISE NOTICE '── Verificación Rollback ──────────────────────';
  RAISE NOTICE 'Tipos org en uso:    % (esperado: 2 — GORE + DIVISION)', v_org_types;
  RAISE NOTICE 'Roles del sistema:   % (esperado: 8)', v_roles;
  RAISE NOTICE 'Estados convenio:    % (esperado: 10)', v_states;
  RAISE NOTICE 'Orgs activas:        % (esperado: ~31)', v_active_orgs;
  RAISE NOTICE '───────────────────────────────────────────────';
END $$;

COMMIT;
