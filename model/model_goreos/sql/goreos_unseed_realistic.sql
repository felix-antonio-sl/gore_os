-- =============================================================================
-- GORE_OS — Unseed Realista (reversal de goreos_seed_realistic.sql)
-- =============================================================================
-- Elimina SOLO registros con prefijo DEMO-R en orden inverso de FK.
-- Seguro para ejecutar múltiples veces.
--
-- Para ejecutar:
--   docker exec -i goreos_db psql -U goreos -d goreos_model < model/model_goreos/sql/goreos_unseed_realistic.sql
-- =============================================================================

BEGIN;

-- TIER 11: Audit trail
DELETE FROM txn.event
WHERE (subject_id IN (SELECT id FROM core.ipr WHERE codigo_bip LIKE 'DEMO-R-%')
    OR subject_id IN (SELECT id FROM core.agreement WHERE agreement_number LIKE 'DEMO-R-%')
    OR subject_id IN (SELECT id FROM core.risk WHERE code LIKE 'DEMO-R-%')
    OR subject_id IN (SELECT id FROM core.operational_commitment WHERE code LIKE 'DEMO-R-%')
    OR subject_id IN (SELECT id FROM core.committee WHERE code IN ('CONSEJO-REGIONAL','COMITE-CRISIS','COMITE-TD'))
    OR subject_id IN (SELECT id FROM core."user" WHERE email IN ('admin@goreos.cl','jefe.dipir@goreos.cl','jefe.dgi@goreos.cl','gobernador@goreos.cl','analista.dipir@goreos.cl','profesional.dit@goreos.cl','rtf.daf@goreos.cl','juridico@goreos.cl','td@goreos.cl','profesional.dideso@goreos.cl','jefe.daf@goreos.cl','jefe.difoi@goreos.cl','control.gestion@goreos.cl','secretario.core@goreos.cl'))
)
AND occurred_at > CURRENT_TIMESTAMP - INTERVAL '150 days'
AND data::text LIKE '%DEMO-R-%';

-- Additional txn.event cleanup for login/access events
DELETE FROM txn.event
WHERE subject_type = 'core.user'
AND data::text LIKE '%10.0.%'
AND occurred_at > CURRENT_TIMESTAMP - INTERVAL '10 days';

-- TIER 10: Ciclo de vida avanzado
DELETE FROM core.ipr_expost_evaluation WHERE ipr_id IN (SELECT id FROM core.ipr WHERE codigo_bip LIKE 'DEMO-R-%');
DELETE FROM core.ipr_closure WHERE ipr_id IN (SELECT id FROM core.ipr WHERE codigo_bip LIKE 'DEMO-R-%');
DELETE FROM core.ipr_modification WHERE code LIKE 'DEMO-R-%';

-- TIER 9: Alertas + Riesgos
DELETE FROM core.alert WHERE message LIKE '%DEMO-R-%';
DELETE FROM core.risk WHERE code LIKE 'DEMO-R-%';

-- TIER 8: Gobernanza (reverse order: agreements→minutes→crisis→sessions→members→committees)
-- Session agreements via minutes via sessions
DELETE FROM core.session_agreement WHERE minute_id IN (
    SELECT m.id FROM core.minute m
    JOIN core.session s ON m.session_id = s.id
    WHERE m.minute_number LIKE 'DEMO-R-%'
);
DELETE FROM core.crisis_meeting WHERE session_id IN (
    SELECT s.id FROM core.session s
    JOIN core.minute m ON m.session_id = s.id
    WHERE m.minute_number LIKE 'DEMO-R-%'
);
DELETE FROM core.minute WHERE minute_number LIKE 'DEMO-R-%';
DELETE FROM core.session WHERE session_number IN (901, 902, 903, 801, 802, 701)
    AND committee_id IN (SELECT id FROM core.committee WHERE code IN ('CONSEJO-REGIONAL','COMITE-CRISIS','COMITE-TD'));
-- Note: We do NOT delete committees (CONSEJO-REGIONAL, COMITE-CRISIS, COMITE-TD) as they may be auto-created
-- We also do NOT delete committee_members as they may be shared

-- TIER 7: DGI Coordinación
DELETE FROM core.dgi_division_interaction WHERE created_by_id IN (
    SELECT id FROM core."user" WHERE email IN ('control.gestion@goreos.cl','procesos@goreos.cl','td@goreos.cl','jefe.dgi@goreos.cl')
) AND notes IS NOT NULL AND (
    notes LIKE '%DIPIR prioriza%' OR notes LIKE '%DIT acepta%' OR notes LIKE '%DAF proyecta%'
    OR notes LIKE '%DIDESO presenta%' OR notes LIKE '%DIFOI solicita%' OR notes LIKE '%vincular indicadores%'
);
DELETE FROM core.dgi_service_request WHERE code LIKE 'DEMO-R-%';
DELETE FROM core.dgi_escalation WHERE code LIKE 'DEMO-R-%';
DELETE FROM core.dgi_ar_decision WHERE description LIKE 'DEMO-R-%';

-- TIER 6: DGI Core
DELETE FROM core.dgi_decree WHERE code LIKE 'DEMO-R-%';
DELETE FROM core.dgi_report WHERE code LIKE 'DEMO-R-%';
DELETE FROM core.dgi_bottleneck_investigation WHERE code LIKE 'DEMO-R-%';
DELETE FROM core.dgi_improvement_opportunity WHERE process_id IN (SELECT id FROM core.dgi_process WHERE code LIKE 'DEMO-R-%');
DELETE FROM core.dgi_initiative WHERE code LIKE 'DEMO-R-%';
DELETE FROM core.dgi_process_pain_point WHERE process_id IN (SELECT id FROM core.dgi_process WHERE code LIKE 'DEMO-R-%');
DELETE FROM core.dgi_process_rule WHERE process_id IN (SELECT id FROM core.dgi_process WHERE code LIKE 'DEMO-R-%');
DELETE FROM core.dgi_process_metric WHERE process_id IN (SELECT id FROM core.dgi_process WHERE code LIKE 'DEMO-R-%');
DELETE FROM core.dgi_process_actor WHERE process_id IN (SELECT id FROM core.dgi_process WHERE code LIKE 'DEMO-R-%');
DELETE FROM core.dgi_process WHERE code LIKE 'DEMO-R-%';
DELETE FROM core.dgi_indicator WHERE code LIKE 'DEMO-R-%';

-- TIER 5B: Cadenas IPR↔Convenio↔Resolución
-- Nullify resolution_id on CDPs before deleting resolutions
UPDATE core.budget_commitment SET resolution_id = NULL
WHERE commitment_number LIKE 'DEMO-R-%' AND resolution_id IS NOT NULL;
-- Nullify closure_act_id before deleting admin acts
UPDATE core.ipr_closure SET closure_act_id = NULL
WHERE ipr_id IN (SELECT id FROM core.ipr WHERE codigo_bip LIKE 'DEMO-R-%') AND closure_act_id IS NOT NULL;
-- Delete resolutions (must come before admin acts due to FK)
DELETE FROM core.resolution WHERE administrative_act_id IN (
    SELECT id FROM core.administrative_act WHERE act_number LIKE 'DEMO-R-%'
);

-- TIER 5: Normativo + Operacional
DELETE FROM core.ipr_problem WHERE code LIKE 'DEMO-R-%';
DELETE FROM core.operational_commitment WHERE code LIKE 'DEMO-R-%';
DELETE FROM core.administrative_act WHERE act_number LIKE 'DEMO-R-%';

-- TIER 4: Cadena financiera
DELETE FROM core.rendition WHERE agreement_id IN (SELECT id FROM core.agreement WHERE agreement_number LIKE 'DEMO-R-%');
DELETE FROM core.agreement_installment WHERE agreement_id IN (SELECT id FROM core.agreement WHERE agreement_number LIKE 'DEMO-R-%');
DELETE FROM core.agreement WHERE agreement_number LIKE 'DEMO-R-%';
DELETE FROM core.budget_commitment WHERE commitment_number LIKE 'DEMO-R-%';
DELETE FROM core.budget_carryover WHERE budget_program_id IN (SELECT id FROM core.budget_program WHERE code LIKE 'DEMO-R-%');
DELETE FROM core.budget_program WHERE code LIKE 'DEMO-R-%';

-- TIER 3: Satélites IPR
DELETE FROM core.progress_report WHERE ipr_id IN (SELECT id FROM core.ipr WHERE codigo_bip LIKE 'DEMO-R-%');
DELETE FROM core.evaluation_assignment WHERE ipr_id IN (SELECT id FROM core.ipr WHERE codigo_bip LIKE 'DEMO-R-%');
DELETE FROM core.ipr_milestone WHERE ipr_id IN (SELECT id FROM core.ipr WHERE codigo_bip LIKE 'DEMO-R-%');
DELETE FROM core.ipr_territory WHERE ipr_id IN (SELECT id FROM core.ipr WHERE codigo_bip LIKE 'DEMO-R-%');
DELETE FROM core.ipr_party WHERE ipr_id IN (SELECT id FROM core.ipr WHERE codigo_bip LIKE 'DEMO-R-%');

-- TIER 2: IPRs
DELETE FROM core.ipr WHERE codigo_bip LIKE 'DEMO-R-%';

-- TIER 1: Organizaciones y personas externas
DELETE FROM core.organization WHERE code LIKE 'DEMO-R-%';
DELETE FROM core.person WHERE email IN (
    'harriagada@munichillan.cl', 'pcifuentes@munisancarlos.cl', 'morellana@muniquirihue.cl',
    'fbustamante@municoihueco.cl', 'rsanhueza@munibulnes.cl', 'cvalenzuela@serviu-nuble.cl',
    'efigueroa@mop-nuble.cl', 'dcontreras@sernatur-nuble.cl', 'jespinoza@ubb.cl',
    'mnavarrete@uadventista.cl', 'griquelme@constructoraitata.cl', 'lzuniga@ingnuble.cl',
    'amedina@fundacionnuble.cl', 'sparedes@mdsf.gob.cl', 'rcastillo@mop-eval.cl'
);

COMMIT;

-- =============================================================================
-- VERIFICACIÓN:
-- SELECT 'IPRs restantes' AS check, COUNT(*) FROM core.ipr WHERE codigo_bip LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Orgs restantes', COUNT(*) FROM core.organization WHERE code LIKE 'DEMO-R-%'
-- UNION ALL SELECT 'Risks restantes', COUNT(*) FROM core.risk WHERE code LIKE 'DEMO-R-%';
-- Todos deben ser 0.
-- =============================================================================
