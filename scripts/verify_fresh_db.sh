#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
compose_config="$(mktemp)"
probe_name="goreos_bootstrap_check_${BASHPID}"
probe_volume="${probe_name}_data"

cleanup() {
    docker rm -f "$probe_name" >/dev/null 2>&1 || true
    docker volume rm "$probe_volume" >/dev/null 2>&1 || true
    rm -f "$compose_config"
}
trap cleanup EXIT

cd "$repo_root"
GOREOS_BASICAUTH=bootstrap-check \
    docker compose --env-file /dev/null --profile standalone config --format json > "$compose_config"

python3 - "$compose_config" "$repo_root" <<'PY'
import json
import sys
from pathlib import Path

config_path = Path(sys.argv[1])
repo_root = Path(sys.argv[2]).resolve()
config = json.loads(config_path.read_text())

postgres = config["services"]["postgres"]
api = config["services"]["api"]

postgres_db = postgres["environment"]["POSTGRES_DB"]
api_db = api["environment"]["DB_NAME"]
if postgres_db != "goreos_model" or api_db != postgres_db:
    raise SystemExit(
        "FAIL: PostgreSQL y API deben usar goreos_model por defecto "
        f"(postgres={postgres_db!r}, api={api_db!r})"
    )

expected_init_mounts = {
    "/docker-entrypoint-initdb.d/10-schema.sql": (
        repo_root / "model/model_goreos/sql/goreos_ddl.sql"
    ),
    "/docker-entrypoint-initdb.d/20-reference-data.sql": (
        repo_root / "model/model_goreos/sql/goreos_seed.sql"
    ),
    "/docker-entrypoint-initdb.d/30-territory.sql": (
        repo_root / "model/model_goreos/sql/goreos_seed_territory.sql"
    ),
}
actual_init_mounts = {
    volume["target"]: Path(volume["source"]).resolve()
    for volume in postgres.get("volumes", [])
    if volume.get("type") == "bind"
    and volume.get("target", "").startswith("/docker-entrypoint-initdb.d")
}

if actual_init_mounts != expected_init_mounts:
    raise SystemExit(
        "FAIL: initdb debe recibir solo schema, datos de referencia y territorio; "
        f"targets actuales={sorted(actual_init_mounts)}"
    )

if any(
    not volume.get("read_only", False)
    for volume in postgres.get("volumes", [])
    if volume.get("target") in expected_init_mounts
):
    raise SystemExit("FAIL: todos los artefactos de initdb deben montarse read-only")
PY

postgres_image="$(
    python3 - "$compose_config" <<'PY'
import json
import sys

with open(sys.argv[1]) as config_file:
    print(json.load(config_file)["services"]["postgres"]["image"])
PY
)"

ddl="$repo_root/model/model_goreos/sql/goreos_ddl.sql"
reference_seed="$repo_root/model/model_goreos/sql/goreos_seed.sql"
territory_seed="$repo_root/model/model_goreos/sql/goreos_seed_territory.sql"
expected_tables="$(awk '/^CREATE TABLE / { count += 1 } END { print count + 0 }' "$ddl")"
expected_triggers="$(awk '/^CREATE TRIGGER / { count += 1 } END { print count + 0 }' "$ddl")"

if docker container inspect "$probe_name" >/dev/null 2>&1 \
    || docker volume inspect "$probe_volume" >/dev/null 2>&1; then
    echo "FAIL: ya existe un recurso temporal con la identidad $probe_name" >&2
    exit 1
fi

docker volume create "$probe_volume" >/dev/null
docker run -d \
    --name "$probe_name" \
    --network none \
    -e POSTGRES_PASSWORD=bootstrap_check_only \
    -e POSTGRES_USER=goreos \
    -e POSTGRES_DB=goreos_model \
    -e 'POSTGRES_INITDB_ARGS=--encoding=UTF-8 --locale=es_CL.UTF-8' \
    -v "$probe_volume:/var/lib/postgresql/data" \
    -v "$ddl:/docker-entrypoint-initdb.d/10-schema.sql:ro" \
    -v "$reference_seed:/docker-entrypoint-initdb.d/20-reference-data.sql:ro" \
    -v "$territory_seed:/docker-entrypoint-initdb.d/30-territory.sql:ro" \
    "$postgres_image" >/dev/null

ready=0
for _ in $(seq 1 60); do
    container_state="$(docker inspect -f '{{.State.Status}}' "$probe_name")"
    if [[ "$container_state" == "exited" ]]; then
        break
    fi
    if docker logs "$probe_name" 2>&1 \
        | grep -Fq 'PostgreSQL init process complete; ready for start up.' \
        && docker exec "$probe_name" pg_isready -U goreos -d goreos_model >/dev/null 2>&1; then
        ready=1
        break
    fi
    sleep 1
done

if [[ "$ready" -ne 1 ]]; then
    echo "FAIL: PostgreSQL no quedó disponible después del bootstrap" >&2
    docker logs --tail 120 "$probe_name" 2>&1 \
        | sed -E 's/(password|secret|token)[^ ]*/<redacted>/Ig' >&2
    exit 1
fi

probe_counts="$(docker exec "$probe_name" psql -X -v ON_ERROR_STOP=1 \
    -U goreos -d goreos_model -At -F '|' -c "
SELECT
    (SELECT count(*)
       FROM pg_class c
       JOIN pg_namespace n ON n.oid = c.relnamespace
      WHERE n.nspname IN ('core', 'meta', 'ref', 'txn', 'public')
        AND c.relkind IN ('r', 'p')),
    (SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal),
    (SELECT count(*)
       FROM pg_proc p
       JOIN pg_namespace n ON n.oid = p.pronamespace
      WHERE (n.nspname, p.proname) IN (
          ('core', 'trg_ar_decision_state_transition_fn'),
          ('core', 'trg_escalation_state_transition_fn'),
          ('core', 'trg_request_state_transition_fn'),
          ('core', 'trg_session_lifecycle_guard_fn'),
          ('core', 'trg_session_lifecycle_sync_fn'),
          ('core', 'trg_crisis_meeting_lifecycle_guard_fn'),
          ('core', 'trg_evaluation_assignment_result_guard_fn'),
          ('core', 'trg_session_agreement_status_default_fn'),
          ('core', 'trg_budget_cycle_completion_guard_fn'),
          ('core', 'trg_dgi_opportunity_status_transition_fn'),
          ('core', 'trg_service_request_active_service_fn'),
          ('public', 'fn_validate_state_transition')
      )),
    (SELECT (i.indisunique
             AND pg_get_expr(i.indpred, i.indrelid) = '(resolved_at IS NULL)')::int
       FROM pg_index i
       JOIN pg_class index_relation ON index_relation.oid = i.indexrelid
       JOIN pg_namespace index_namespace ON index_namespace.oid = index_relation.relnamespace
      WHERE index_namespace.nspname = 'core'
        AND index_relation.relname = 'uq_rendition_escalation_open'),
    (SELECT count(*) FROM ref.category),
    (SELECT count(*) FROM ref.actor),
    (SELECT count(*) FROM ref.operational_commitment_type),
    (SELECT count(*) FROM core.territory),
    (SELECT count(*) FROM core.\"user\"),
    (SELECT count(*) FROM core.schema_migration),
    to_regclass('core.notification')::text,
    (SELECT datcollate FROM pg_database WHERE datname = current_database()),
    (SELECT count(*) FROM ref.category
      WHERE scheme = 'act_state'
        AND code NOT IN ('TOMADO_RAZON', 'RECHAZADO_CGR', 'ANULADO')
        AND valid_transitions ? 'ANULADO'),
    (SELECT count(*) FROM ref.category
      WHERE scheme = 'act_state'
        AND code IN ('TOMADO_RAZON', 'RECHAZADO_CGR', 'ANULADO')
        AND valid_transitions = '[]'::jsonb),
    (SELECT count(*) FROM ref.category
      WHERE scheme = 'ipr_state'
        AND code = 'PRE_ADMISIBLE'
        AND valid_transitions ?& ARRAY['ADMISIBLE', 'INADMISIBLE']
        AND jsonb_array_length(valid_transitions) = 2),
    (SELECT count(*) FROM ref.category
      WHERE scheme = 'categoria_c33'
        AND (code, metadata->>'certifier_org_code') IN (
          ('EDIFICACION', 'SERVIU'), ('VIALIDAD', 'MOP')
        )),
    (SELECT count(*) FROM ref.category WHERE scheme = 'ipr_type'),
    (SELECT count(*) FROM ref.category
      WHERE scheme = 'ipr_type' AND code = 'PROGRAMA_8PCT'),
    (SELECT count(*) FROM ref.category WHERE scheme = 'milestone_type'),
    (SELECT count(*) FROM ref.category
      WHERE scheme = 'milestone_type' AND code = 'LICITACION'),
    (SELECT count(*) FROM ref.category WHERE scheme = 'territory_impact'),
    (SELECT count(*) FROM ref.category WHERE scheme = 'ipr_party_role'),
    (SELECT count(*) FROM ref.category WHERE scheme = 'rendition_state'),
    (SELECT count(*) FROM ref.category
      WHERE scheme = 'rendition_state'
        AND code IN ('EN_REVISION_RTF', 'VISADA_RTF', 'EN_REVISION_UCR')),
    (SELECT count(*) FROM ref.category
      WHERE scheme = 'ipr_state'
        AND code IN ('TERMINADO_ANTICIPADAMENTE', 'CONTRATO_FIRMADO',
                     'RENDICION_APROBADA', 'EN_CIERRE_ADMINISTRATIVO')),
    (SELECT count(*) FROM ref.category WHERE scheme = 'expost_eval_type'),
    (SELECT count(*) FROM ref.category WHERE scheme = 'expost_rating'),
    (SELECT (valid_transitions ? 'COMPLETADO')::int
       FROM ref.category
      WHERE scheme = 'commitment_state' AND code = 'PENDIENTE'),
    (SELECT (valid_transitions ?& ARRAY['EN_PROGRESO', 'COMPLETADO'])::int
       FROM ref.category
      WHERE scheme = 'commitment_state' AND code = 'VENCIDO'),
    (SELECT (count(*) = 4)::int
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
    (SELECT ((
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
          )))::int)),
    (SELECT ((
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
      AND (SELECT count(*) = 2 FROM ref.category WHERE scheme = 'dgi_bpmn_type'))::int)),
    (SELECT ((
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
          )))::int)),
    (SELECT count(*)
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
    (SELECT count(*) FROM ref.category WHERE scheme = 'risk_probability'),
    (SELECT count(*)
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
    (SELECT count(*)
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
    (SELECT count(*) FROM ref.category WHERE scheme = 'budget_item'),
    (SELECT count(*) FROM ref.category WHERE scheme = 'budget_allocation'),
    (SELECT count(*) FROM ref.category WHERE scheme = 'program_type'),
    (SELECT count(*)
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
    (SELECT (
      (SELECT count(*) = 4 FROM ref.category WHERE scheme = 'dgi_ar_decision_type')
      AND (SELECT count(*) = 3 FROM ref.category WHERE scheme = 'dgi_ar_decision_status')
      AND (SELECT count(*) = 4 FROM ref.category WHERE scheme = 'dgi_escalation_level')
      AND (SELECT count(*) = 4 FROM ref.category WHERE scheme = 'dgi_escalation_status')
      AND (SELECT count(*) = 3 FROM ref.category WHERE scheme = 'dgi_service_status')
      AND (SELECT count(*) = 6 FROM ref.category WHERE scheme = 'dgi_request_status')
      AND (SELECT count(*) = 6 FROM ref.category WHERE scheme = 'dgi_interaction_type')
      AND (SELECT count(*) = 7 FROM ref.category WHERE scheme = 'dgi_sla_product_type'))::int),
    (SELECT count(*)
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
    (SELECT ((
      (SELECT count(*) = 3 FROM ref.category WHERE scheme = 'session_type')
      AND (SELECT count(*) = 3 FROM ref.category WHERE scheme = 'vote_option')
      AND (SELECT count(*) = 2 FROM ref.category WHERE scheme = 'quorum_type'))::int));
")" || {
    echo "FAIL: no se pudieron verificar los invariantes del bootstrap" >&2
    exit 1
}
IFS='|' read -r actual_tables actual_triggers transition_functions open_escalation_uniqueness categories actors commitment_types territories users migration_rows notification_table collate cancellable_act_states terminal_act_states pre_admissible_state c33_certifiers ipr_types programa_8pct milestone_types licitacion_type territory_impacts party_roles rendition_states sisrec_states lifecycle_states expost_types expost_ratings quick_complete late_complete initiative_fsm indicator_catalogs process_catalogs report_catalogs dmaic_fsm risk_probabilities risk_fsm bottleneck_fsm budget_items budget_allocations program_types budget_commitment_fsm coordination_catalogs coordination_fsms governance_catalogs <<< "$probe_counts"

if [[ "$actual_tables" -ne "$expected_tables" ]]; then
    echo "FAIL: el DDL declara $expected_tables tablas y PostgreSQL creó $actual_tables" >&2
    exit 1
fi
if [[ "$actual_triggers" -ne "$expected_triggers" || "$transition_functions" -ne 12 ]]; then
    echo "FAIL: faltan triggers o funciones canónicas de transición de estado" >&2
    exit 1
fi
if [[ "$open_escalation_uniqueness" -ne 1 ]]; then
    echo "FAIL: falta la unicidad parcial de escalaciones SISREC abiertas" >&2
    exit 1
fi
if [[ "$categories" -le 0 || "$actors" -le 0 || "$commitment_types" -le 0 ]]; then
    echo "FAIL: los datos de referencia canónicos quedaron incompletos" >&2
    exit 1
fi
if [[ "$territories" -ne 25 ]]; then
    echo "FAIL: se esperaban 25 territorios de Ñuble y se obtuvieron $territories" >&2
    exit 1
fi
if [[ "$users" -ne 0 || "$migration_rows" -ne 0 ]]; then
    echo "FAIL: el bootstrap fresco no debe cargar usuarios demo ni fingir migraciones" >&2
    exit 1
fi
if [[ "$notification_table" != "core.notification" ]]; then
    echo "FAIL: el baseline no contiene core.notification" >&2
    exit 1
fi
if [[ "$collate" != "es_CL.UTF-8" ]]; then
    echo "FAIL: locale inesperado: $collate" >&2
    exit 1
fi
if [[ "$cancellable_act_states" -ne 6 || "$terminal_act_states" -ne 3 ]]; then
    echo "FAIL: la FSM de actos no conserva ANULADO transversal y estados terminales cerrados" >&2
    exit 1
fi
if [[ "$pre_admissible_state" -ne 1 ]]; then
    echo "FAIL: el bootstrap no contiene PRE_ADMISIBLE con su transición canónica" >&2
    exit 1
fi
if [[ "$c33_certifiers" -ne 2 ]]; then
    echo "FAIL: el bootstrap no contiene el enrutamiento certificador C33" >&2
    exit 1
fi
if [[ "$ipr_types" -ne 8 || "$programa_8pct" -ne 1 ]]; then
    echo "FAIL: el bootstrap no contiene los 8 tipos IPR canónicos" >&2
    exit 1
fi
if [[ "$milestone_types" -ne 13 || "$licitacion_type" -ne 1 \
    || "$territory_impacts" -ne 4 || "$party_roles" -ne 9 ]]; then
    echo "FAIL: faltan catálogos canónicos de hitos, territorio o partes IPR" >&2
    exit 1
fi
if [[ "$rendition_states" -ne 9 || "$sisrec_states" -ne 3 ]]; then
    echo "FAIL: el bootstrap no contiene la FSM SISREC RTF→UCR canónica" >&2
    exit 1
fi
if [[ "$lifecycle_states" -ne 4 || "$expost_types" -ne 3 || "$expost_ratings" -ne 4 ]]; then
    echo "FAIL: faltan estados de cierre o catálogos de evaluación ex-post" >&2
    exit 1
fi
if [[ "$quick_complete" -ne 1 || "$late_complete" -ne 1 ]]; then
    echo "FAIL: las transiciones de compromiso no coinciden con los endpoints" >&2
    exit 1
fi
if [[ "$initiative_fsm" -ne 1 ]]; then
    echo "FAIL: falta la FSM canónica de iniciativas DGI" >&2
    exit 1
fi
if [[ "$indicator_catalogs" -ne 1 ]]; then
    echo "FAIL: faltan catálogos o FSM canónica de indicadores DGI" >&2
    exit 1
fi
if [[ "$process_catalogs" -ne 1 ]]; then
    echo "FAIL: faltan catálogos o FSM canónicas de procesos/BPMN" >&2
    exit 1
fi
if [[ "$report_catalogs" -ne 1 ]]; then
    echo "FAIL: faltan catálogos o FSM canónica de informes DGI" >&2
    exit 1
fi
if [[ "$dmaic_fsm" -ne 5 ]]; then
    echo "FAIL: falta la FSM canónica de fases DMAIC" >&2
    exit 1
fi
if [[ "$risk_probabilities" -ne 5 || "$risk_fsm" -ne 6 ]]; then
    echo "FAIL: faltan probabilidad o FSM canónica de riesgos" >&2
    exit 1
fi
if [[ "$bottleneck_fsm" -ne 6 ]]; then
    echo "FAIL: falta la FSM canónica de investigaciones de cuello de botella" >&2
    exit 1
fi
if [[ "$budget_items" -ne 14 || "$budget_allocations" -ne 15 \
    || "$program_types" -ne 5 || "$budget_commitment_fsm" -ne 5 ]]; then
    echo "FAIL: faltan catálogos presupuestarios o la FSM de CDP" >&2
    exit 1
fi
if [[ "$coordination_catalogs" -ne 1 || "$coordination_fsms" -ne 13 ]]; then
    echo "FAIL: faltan catálogos o FSM canónicas de coordinación DGI" >&2
    exit 1
fi
if [[ "$governance_catalogs" -ne 1 ]]; then
    echo "FAIL: faltan catálogos canónicos de sesiones, voto o quórum" >&2
    exit 1
fi

cleanup
trap - EXIT

if docker container inspect "$probe_name" >/dev/null 2>&1; then
    echo "FAIL: quedó el contenedor temporal $probe_name" >&2
    exit 1
fi
if docker volume inspect "$probe_volume" >/dev/null 2>&1; then
    echo "FAIL: quedó el volumen temporal $probe_volume" >&2
    exit 1
fi

echo "PASS: bootstrap fresco — $actual_tables tablas, $actual_triggers triggers, $categories categorías, $territories territorios, 0 usuarios demo"
