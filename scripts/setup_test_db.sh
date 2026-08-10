#!/usr/bin/env bash
# Usage: ./scripts/setup_test_db.sh [container_name] [test_db_name] [db_user]
# Defaults: goreos_db goreos_test goreos
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
container="${1:-goreos_db}"
test_db="${2:-goreos_test}"
db_user="${3:-goreos}"
sql_dir="$repo_root/model/model_goreos/sql"

if [[ ! "$test_db" =~ ^[A-Za-z_][A-Za-z0-9_]*_test$ ]]; then
    echo "FAIL: la base de destino debe terminar en _test: $test_db" >&2
    exit 1
fi
if [[ ! "$db_user" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
    echo "FAIL: usuario PostgreSQL inválido: $db_user" >&2
    exit 1
fi
if [[ "$(docker container inspect -f '{{.State.Running}}' "$container" 2>/dev/null || true)" != "true" ]]; then
    echo "FAIL: el contenedor PostgreSQL no está corriendo: $container" >&2
    exit 1
fi

sql_files=(
    goreos_ddl.sql
    goreos_seed.sql
    goreos_seed_territory.sql
    goreos_seed_users.sql
    goreos_seed_core_members.sql
    goreos_migration_wave7_evaluation.sql
    goreos_migration_wave8_financing_track.sql
    goreos_migration_ciclo20_thresholds.sql
    goreos_migration_ciclo24_wave1.sql
    goreos_migration_ciclo24_wave4.sql
    goreos_migration_parametrize_thresholds.sql
    goreos_migration_ciclo23_sni_levels.sql
    goreos_migration_sisrec_8phase.sql
    goreos_migration_rendition_escalation_uniqueness.sql
    goreos_migration_tp02_tp04.sql
    goreos_migration_dgi_wave_a.sql
    goreos_migration_budget_cycle.sql
    goreos_migration_wave_e.sql
    goreos_migration_act_state_cross_cutting.sql
    goreos_migration_bottleneck_fsm.sql
    goreos_migration_indicator_catalogs_fsm.sql
    goreos_migration_process_catalogs_fsm.sql
    goreos_migration_opportunity_fsm.sql
    goreos_migration_service_request_active_guard.sql
    goreos_migration_report_catalogs_fsm.sql
    goreos_migration_dmaic_catalog_fsm.sql
    goreos_migration_session_lifecycle_authority.sql
    goreos_migration_evaluation_result_authority.sql
    goreos_migration_session_agreement_status_authority.sql
    goreos_migration_budget_cycle_completion_authority.sql
    goreos_migration_lifecycle_wave2.sql
    goreos_migration_lifecycle_wave4.sql
    goreos_migration_lifecycle_wave5.sql
)

for filename in "${sql_files[@]}"; do
    if [[ ! -r "$sql_dir/$filename" ]]; then
        echo "FAIL: falta el SQL requerido: $sql_dir/$filename" >&2
        exit 1
    fi
done

echo "Preparando $test_db desde fuentes versionadas..."
docker exec "$container" psql -X -v ON_ERROR_STOP=1 -U "$db_user" -d postgres \
    -c "DROP DATABASE IF EXISTS \"$test_db\" WITH (FORCE);"
docker exec "$container" psql -X -v ON_ERROR_STOP=1 -U "$db_user" -d postgres \
    -c "CREATE DATABASE \"$test_db\" OWNER \"$db_user\";"

for filename in "${sql_files[@]}"; do
    echo "  APPLY $filename"
    docker exec -i "$container" psql -X -v ON_ERROR_STOP=1 \
        -U "$db_user" -d "$test_db" < "$sql_dir/$filename" >/dev/null
done

counts="$(docker exec "$container" psql -X -v ON_ERROR_STOP=1 \
    -U "$db_user" -d "$test_db" -At -F '|' -c "
SELECT
    (SELECT count(*)
       FROM pg_class c
       JOIN pg_namespace n ON n.oid = c.relnamespace
      WHERE n.nspname IN ('core', 'meta', 'ref', 'txn', 'public')
        AND c.relkind IN ('r', 'p')),
    (SELECT count(*) FROM ref.category),
    (SELECT count(*) FROM core.\"user\"),
    (SELECT count(*) FROM core.committee_member),
    (SELECT count(*) FROM core.financing_track),
    (SELECT count(*) FROM core.financial_threshold),
    (SELECT count(*) FROM core.sni_level_config),
    (SELECT count(*) FROM core.rendition_phase),
    (SELECT count(*) FROM core.subv8_fund),
    (SELECT count(*) FROM core.fril_category),
    (SELECT count(*) FROM core.dgi_decree),
    (SELECT count(*) FROM core.budget_cycle_milestone),
    (SELECT (sla_days ? 'report_frequency_days')
         AND (sla_days ? 'evaluation_max_days')
         AND (sla_days ? 'rs_validity_days')
         AND (role_permissions ? 'register_eval_result')
       FROM core.financing_track WHERE code = 'FRIL'),
    (SELECT count(*) = 11 FROM ref.category
      WHERE scheme = 'ipr_party_role'),
    (SELECT count(*) = 6 FROM ref.category
      WHERE scheme = 'act_state'
        AND code NOT IN ('TOMADO_RAZON', 'RECHAZADO_CGR', 'ANULADO')
        AND valid_transitions ? 'ANULADO'),
    (SELECT count(*) = 3 FROM ref.category
      WHERE scheme = 'act_state'
        AND code IN ('TOMADO_RAZON', 'RECHAZADO_CGR', 'ANULADO')
        AND valid_transitions = '[]'::jsonb),
    (SELECT valid_transitions ?& ARRAY['ADMISIBLE', 'INADMISIBLE']
            AND jsonb_array_length(valid_transitions) = 2
       FROM ref.category
      WHERE scheme = 'ipr_state' AND code = 'PRE_ADMISIBLE'),
    (SELECT count(*) = 2 FROM ref.category
      WHERE scheme = 'categoria_c33'
        AND (code, metadata->>'certifier_org_code') IN (
          ('EDIFICACION', 'SERVIU'), ('VIALIDAD', 'MOP')
        )),
    (SELECT count(*) = 8 AND bool_or(code = 'PROGRAMA_8PCT')
       FROM ref.category WHERE scheme = 'ipr_type'),
    (SELECT count(*) = 13 AND bool_or(code = 'LICITACION')
       FROM ref.category WHERE scheme = 'milestone_type'),
    (SELECT count(*) = 4 AND bool_or(code = 'UBICACION')
       FROM ref.category WHERE scheme = 'territory_impact'),
    (SELECT count(*) = 9
            AND bool_or(code = 'EN_REVISION_RTF')
            AND bool_or(code = 'VISADA_RTF')
            AND bool_or(code = 'EN_REVISION_UCR')
       FROM ref.category WHERE scheme = 'rendition_state'),
    (SELECT count(*) = 4 FROM ref.category
      WHERE scheme = 'ipr_state'
        AND code IN ('TERMINADO_ANTICIPADAMENTE', 'CONTRATO_FIRMADO',
                     'RENDICION_APROBADA', 'EN_CIERRE_ADMINISTRATIVO')),
    (SELECT count(*) = 3 FROM ref.category WHERE scheme = 'expost_eval_type'),
    (SELECT count(*) = 4 FROM ref.category WHERE scheme = 'expost_rating'),
    (SELECT valid_transitions ? 'COMPLETADO'
       FROM ref.category
      WHERE scheme = 'commitment_state' AND code = 'PENDIENTE'),
    (SELECT valid_transitions ?& ARRAY['EN_PROGRESO', 'COMPLETADO']
       FROM ref.category
      WHERE scheme = 'commitment_state' AND code = 'VENCIDO'),
    (SELECT count(*) = 4
       FROM ref.category
      WHERE scheme = 'dgi_initiative_status'
        AND (
          (code = 'BACKLOG'
            AND valid_transitions ?& ARRAY['EN_CURSO', 'REVISION', 'COMPLETADO']
            AND jsonb_array_length(valid_transitions) = 3)
          OR (code = 'EN_CURSO'
            AND valid_transitions ?& ARRAY['BACKLOG', 'REVISION', 'COMPLETADO']
            AND jsonb_array_length(valid_transitions) = 3)
          OR (code = 'REVISION'
            AND valid_transitions ?& ARRAY['BACKLOG', 'EN_CURSO', 'COMPLETADO']
            AND jsonb_array_length(valid_transitions) = 3)
          OR (code = 'COMPLETADO'
            AND valid_transitions = jsonb_build_array('BACKLOG'))
        )),
    (SELECT
      (SELECT count(*) = 5 FROM ref.category WHERE scheme = 'dgi_indicator_dimension')
      AND (SELECT count(*) = 3 FROM ref.category WHERE scheme = 'dgi_signal')
      AND (SELECT count(*) = 4
        FROM ref.category
        WHERE scheme = 'dgi_indicator_lifecycle'
          AND (
            (code = 'BORRADOR' AND valid_transitions = jsonb_build_array('APROBADO'))
            OR (code = 'APROBADO'
              AND valid_transitions ?& ARRAY['VIGENTE', 'BORRADOR']
              AND jsonb_array_length(valid_transitions) = 2)
            OR (code = 'VIGENTE'
              AND valid_transitions ?& ARRAY['DEPRECADO', 'APROBADO']
              AND jsonb_array_length(valid_transitions) = 2)
            OR (code = 'DEPRECADO' AND valid_transitions = '[]'::jsonb)
          ))),
    (SELECT
      (SELECT count(*) = 6
        FROM ref.category
        WHERE scheme = 'dgi_process_status'
          AND (
            (code = 'IDENTIFICADO'
              AND valid_transitions ?& ARRAY['EN_LEVANTAMIENTO', 'SUSPENDIDO']
              AND jsonb_array_length(valid_transitions) = 2)
            OR (code = 'EN_LEVANTAMIENTO'
              AND valid_transitions ?& ARRAY['MODELADO', 'IDENTIFICADO', 'SUSPENDIDO']
              AND jsonb_array_length(valid_transitions) = 3)
            OR (code = 'MODELADO'
              AND valid_transitions ?& ARRAY['VALIDADO', 'EN_LEVANTAMIENTO', 'SUSPENDIDO']
              AND jsonb_array_length(valid_transitions) = 3)
            OR (code = 'VALIDADO'
              AND valid_transitions ?& ARRAY['PUBLICADO', 'MODELADO', 'SUSPENDIDO']
              AND jsonb_array_length(valid_transitions) = 3)
            OR (code = 'PUBLICADO' AND valid_transitions = jsonb_build_array('SUSPENDIDO'))
            OR (code = 'SUSPENDIDO' AND valid_transitions = jsonb_build_array('IDENTIFICADO'))
          ))
      AND (SELECT count(*) = 3
        FROM ref.category
        WHERE scheme = 'dgi_bpmn_status'
          AND (
            (code = 'BORRADOR' AND valid_transitions = jsonb_build_array('REVISION'))
            OR (code = 'REVISION'
              AND valid_transitions ?& ARRAY['BORRADOR', 'VALIDADO']
              AND jsonb_array_length(valid_transitions) = 2)
            OR (code = 'VALIDADO' AND valid_transitions = jsonb_build_array('BORRADOR'))
          ))
      AND (SELECT count(*) = 2 FROM ref.category WHERE scheme = 'dgi_bpmn_type')),
    (SELECT
      (SELECT count(*) = 4 FROM ref.category WHERE scheme = 'dgi_report_type')
      AND (SELECT count(*) = 3
        FROM ref.category
        WHERE scheme = 'dgi_report_status'
          AND (
            (code = 'BORRADOR' AND valid_transitions = jsonb_build_array('EN_REVISION'))
            OR (code = 'EN_REVISION'
              AND valid_transitions ?& ARRAY['BORRADOR', 'ENVIADO']
              AND jsonb_array_length(valid_transitions) = 2)
            OR (code = 'ENVIADO' AND valid_transitions = '[]'::jsonb)
          ))),
    (SELECT count(*) = 5
       FROM ref.category
      WHERE scheme = 'dgi_dmaic_phase'
        AND (
          (code = 'DEFINE'
            AND valid_transitions ?& ARRAY['MEASURE', 'ANALYZE', 'IMPROVE', 'VERIFY']
            AND jsonb_array_length(valid_transitions) = 4)
          OR (code = 'MEASURE'
            AND valid_transitions ?& ARRAY['ANALYZE', 'IMPROVE', 'VERIFY']
            AND jsonb_array_length(valid_transitions) = 3)
          OR (code = 'ANALYZE'
            AND valid_transitions ?& ARRAY['IMPROVE', 'VERIFY']
            AND jsonb_array_length(valid_transitions) = 2)
          OR (code = 'IMPROVE' AND valid_transitions = jsonb_build_array('VERIFY'))
          OR (code = 'VERIFY' AND valid_transitions = '[]'::jsonb)
        )),
    (SELECT count(*) = 5 FROM ref.category WHERE scheme = 'risk_probability'),
    (SELECT count(*) = 6
       FROM ref.category
      WHERE scheme = 'risk_status'
        AND (
          (code = 'IDENTIFICADO'
            AND valid_transitions ?& ARRAY['EN_EVALUACION', 'ACEPTADO']
            AND jsonb_array_length(valid_transitions) = 2)
          OR (code = 'EN_EVALUACION'
            AND valid_transitions ?& ARRAY['EN_MITIGACION', 'ACEPTADO', 'CERRADO']
            AND jsonb_array_length(valid_transitions) = 3)
          OR (code = 'EN_MITIGACION'
            AND valid_transitions ?& ARRAY['MITIGADO', 'CERRADO']
            AND jsonb_array_length(valid_transitions) = 2)
          OR (code IN ('MITIGADO', 'ACEPTADO')
            AND valid_transitions = jsonb_build_array('CERRADO'))
          OR (code = 'CERRADO' AND valid_transitions = '[]'::jsonb)
        )),
    (SELECT count(*) = 6
       FROM ref.category
      WHERE scheme = 'dgi_bottleneck_status'
        AND (
          (code = 'DETECTADO'
            AND valid_transitions ?& ARRAY['VERIFICADO', 'CERRADO']
            AND jsonb_array_length(valid_transitions) = 2)
          OR (code = 'VERIFICADO'
            AND valid_transitions ?& ARRAY['ANALIZADO', 'CERRADO']
            AND jsonb_array_length(valid_transitions) = 2)
          OR (code = 'ANALIZADO'
            AND valid_transitions ?& ARRAY['PROPUESTO', 'CERRADO']
            AND jsonb_array_length(valid_transitions) = 2)
          OR (code = 'PROPUESTO'
            AND valid_transitions ?& ARRAY['IMPLEMENTADO', 'CERRADO']
            AND jsonb_array_length(valid_transitions) = 2)
          OR (code = 'IMPLEMENTADO'
            AND valid_transitions = jsonb_build_array('CERRADO'))
          OR (code = 'CERRADO' AND valid_transitions = '[]'::jsonb)
        )),
    (SELECT count(*) = 14
            AND bool_or(code = 'PERSONAL')
            AND bool_or(code = 'BIENES_SERVICIOS')
       FROM ref.category WHERE scheme = 'budget_item'),
    (SELECT count(*) = 15 FROM ref.category WHERE scheme = 'budget_allocation'),
    (SELECT count(*) = 5 FROM ref.category WHERE scheme = 'program_type'),
    (SELECT count(*) = 5
       FROM ref.category
      WHERE scheme = 'budget_commitment_status'
        AND (
          (code = 'EMITIDO'
            AND valid_transitions ?& ARRAY['VIGENTE', 'ANULADO']
            AND jsonb_array_length(valid_transitions) = 2)
          OR (code = 'VIGENTE'
            AND valid_transitions ?& ARRAY['EJECUTADO', 'VENCIDO', 'ANULADO']
            AND jsonb_array_length(valid_transitions) = 3)
          OR (code IN ('EJECUTADO', 'ANULADO') AND valid_transitions = '[]'::jsonb)
          OR (code = 'VENCIDO' AND valid_transitions = jsonb_build_array('VIGENTE'))
        )),
    (SELECT
      (SELECT count(*) = 4 FROM ref.category WHERE scheme = 'dgi_ar_decision_type')
      AND (SELECT count(*) = 3 FROM ref.category WHERE scheme = 'dgi_ar_decision_status')
      AND (SELECT count(*) = 4 FROM ref.category WHERE scheme = 'dgi_escalation_level')
      AND (SELECT count(*) = 4 FROM ref.category WHERE scheme = 'dgi_escalation_status')
      AND (SELECT count(*) = 3 FROM ref.category WHERE scheme = 'dgi_service_status')
      AND (SELECT count(*) = 6 FROM ref.category WHERE scheme = 'dgi_request_status')
      AND (SELECT count(*) = 6 FROM ref.category WHERE scheme = 'dgi_interaction_type')
      AND (SELECT count(*) = 7 FROM ref.category WHERE scheme = 'dgi_sla_product_type')),
    (SELECT count(*) = 13
       FROM ref.category
      WHERE
        (scheme = 'dgi_ar_decision_status' AND (
          (code = 'PENDIENTE' AND valid_transitions = jsonb_build_array('EN_EJECUCION'))
          OR (code = 'EN_EJECUCION' AND valid_transitions = jsonb_build_array('COMPLETADA'))
          OR (code = 'COMPLETADA' AND valid_transitions = '[]'::jsonb)))
        OR (scheme = 'dgi_escalation_status' AND (
          (code = 'ABIERTO' AND valid_transitions ?& ARRAY['EN_GESTION', 'CERRADO'] AND jsonb_array_length(valid_transitions) = 2)
          OR (code = 'EN_GESTION' AND valid_transitions ?& ARRAY['RESUELTO', 'CERRADO'] AND jsonb_array_length(valid_transitions) = 2)
          OR (code = 'RESUELTO' AND valid_transitions = jsonb_build_array('CERRADO'))
          OR (code = 'CERRADO' AND valid_transitions = '[]'::jsonb)))
        OR (scheme = 'dgi_request_status' AND (
          (code = 'RECIBIDA' AND valid_transitions ?& ARRAY['EN_EVALUACION', 'RECHAZADA'] AND jsonb_array_length(valid_transitions) = 2)
          OR (code = 'EN_EVALUACION' AND valid_transitions ?& ARRAY['ACEPTADA', 'RECHAZADA'] AND jsonb_array_length(valid_transitions) = 2)
          OR (code = 'ACEPTADA' AND valid_transitions = jsonb_build_array('EN_EJECUCION'))
          OR (code = 'EN_EJECUCION' AND valid_transitions = jsonb_build_array('COMPLETADA'))
          OR (code IN ('COMPLETADA', 'RECHAZADA') AND valid_transitions = '[]'::jsonb)))),
    (SELECT
      (SELECT count(*) = 3 FROM ref.category WHERE scheme = 'session_type')
      AND (SELECT count(*) = 3 FROM ref.category WHERE scheme = 'vote_option')
      AND (SELECT count(*) = 2 FROM ref.category WHERE scheme = 'quorum_type'));
")"

IFS='|' read -r tables categories users core_members tracks thresholds sni_levels rendition_phases subv8_funds fril_categories decrees milestones fril_lifecycle party_roles cancellable_act_states terminal_act_states pre_admissible_state c33_certifiers ipr_types milestone_types territory_impacts rendition_states lifecycle_states expost_types expost_ratings quick_complete late_complete initiative_fsm indicator_catalogs process_catalogs report_catalogs dmaic_fsm risk_probabilities risk_fsm bottleneck_fsm budget_items budget_allocations program_types budget_commitment_fsm coordination_catalogs coordination_fsms governance_catalogs <<< "$counts"

if [[ "$tables" -ne 128 || "$categories" -le 0 || "$users" -ne 25 \
    || "$core_members" -ne 16 || "$tracks" -ne 7 || "$thresholds" -ne 10 \
    || "$sni_levels" -ne 4 || "$rendition_phases" -ne 8 || "$subv8_funds" -ne 7 \
    || "$fril_categories" -ne 12 || "$decrees" -ne 6 || "$milestones" -ne 17 \
    || "$fril_lifecycle" != "t" || "$party_roles" != "t" \
    || "$cancellable_act_states" != "t" || "$terminal_act_states" != "t" \
    || "$pre_admissible_state" != "t" || "$c33_certifiers" != "t" \
    || "$ipr_types" != "t" || "$milestone_types" != "t" \
    || "$territory_impacts" != "t" || "$rendition_states" != "t" \
    || "$lifecycle_states" != "t" || "$expost_types" != "t" \
    || "$expost_ratings" != "t" || "$quick_complete" != "t" \
    || "$late_complete" != "t" || "$initiative_fsm" != "t" \
    || "$indicator_catalogs" != "t" \
    || "$process_catalogs" != "t" \
    || "$report_catalogs" != "t" \
    || "$dmaic_fsm" != "t" \
    || "$risk_probabilities" != "t" || "$risk_fsm" != "t" \
    || "$bottleneck_fsm" != "t" \
    || "$budget_items" != "t" || "$budget_allocations" != "t" \
    || "$program_types" != "t" || "$budget_commitment_fsm" != "t" \
    || "$coordination_catalogs" != "t" || "$coordination_fsms" != "t" \
    || "$governance_catalogs" != "t" ]]; then
    echo "FAIL: la DB de test quedó incompleta: $counts" >&2
    exit 1
fi

echo "PASS: $test_db lista — $tables tablas, $categories categorías, $users usuarios, $tracks tracks"
