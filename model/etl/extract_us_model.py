import yaml
import os
import glob
import re
from collections import defaultdict

# Configuración de rutas
STORIES_PATH = "/Users/felixsanhueza/Developer/goreos/model/stories/*.yml"
OUTPUT_YAML = "/Users/felixsanhueza/Developer/goreos/model/us_model_output.yml"
OUTPUT_SQL = "/Users/felixsanhueza/Developer/goreos/model/goreos_us_model.sql"


def normalize_tag(tag):
    """Normalize tag to lowercase and kebab-case."""
    t = tag.lower().strip()
    t = re.sub(r"[^a-z0-9]+", "-", t)
    t = t.strip("-")

    # Agrupación de sinónimos evidentes (ejemplos comunes)
    synonyms = {
        "notificaciones": "notificacion",
        "alertas": "alerta",
        "proyectos": "proyecto",
        "programas": "programa",
        "admisibilidades": "admisibilidad",
        "rendiciones": "rendicion",
        "usuarios": "usuario",
        "roles": "rol",
    }
    return synonyms.get(t, t)


def extract_data():
    files = glob.glob(STORIES_PATH)
    files = [f for f in files if not f.endswith("_index.yml")]

    model = {
        "user_stories": [],
        "roles": {},
        "entities": {},
        "processes": {},
        "tags": set(),
        "extra_tags": set(),
        "acceptance_criteria": [],
    }

    processed_count = 0

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
                if not data or "id" not in data:
                    continue

                us_id = data["id"]
                processed_count += 1

                # Extracción de US Core
                us_entry = {
                    "id": us_id,
                    "urn": data.get("_meta", {}).get("urn"),
                    "name": data.get("name"),
                    "as_a": data.get("as_a"),
                    "i_want": data.get("i_want"),
                    "so_that": data.get("so_that"),
                    "status": data.get("status"),
                    "role_id": data.get("user", {}).get("role_id"),
                    "process_id": data.get("process_ref", {}).get("id"),
                    "tags": data.get("tags", {}),
                    "extra_tags": (
                        [normalize_tag(t) for t in data.get("extra_tags", [])]
                        if data.get("extra_tags")
                        else []
                    ),
                }
                model["user_stories"].append(us_entry)

                # Extracción de Roles
                if us_entry["role_id"]:
                    rid = us_entry["role_id"]
                    if rid not in model["roles"]:
                        model["roles"][rid] = {
                            "id": rid,
                            "label": data.get("as_a"),
                            "agent_type": data.get("user", {}).get("agent_type"),
                            "description": data.get("user", {}).get("description"),
                        }

                # Extracción de Entidades
                for ent in data.get("entities_mentioned", []):
                    eid = ent.get("id")
                    if eid:
                        if eid not in model["entities"]:
                            model["entities"][eid] = {"id": eid}
                        # Relación US-Entity se guarda implícitamente en la US o bridge

                # Extracción de Procesos
                pref = data.get("process_ref")
                if pref and pref.get("id"):
                    pid = pref["id"]
                    if pid not in model["processes"]:
                        model["processes"][pid] = {"id": pid}

                # Tags Estructurados
                t = data.get("tags", {})
                if t:
                    model["tags"].add(
                        (
                            t.get("domain"),
                            t.get("aspect"),
                            t.get("priority"),
                            t.get("scope"),
                        )
                    )

                # Extra Tags
                for et in us_entry["extra_tags"]:
                    model["extra_tags"].add(et)

                # Acceptance Criteria
                for ac in data.get("acceptance_criteria", []):
                    model["acceptance_criteria"].append(
                        {"us_id": us_id, "description": ac}
                    )

            except Exception as e:
                print(f"Error procesando {file_path}: {e}")

    # Convertir sets a listas/dicts para YAML
    model["tags"] = [
        {"domain": t[0], "aspect": t[1], "priority": t[2], "scope": t[3]}
        for t in model["tags"]
    ]
    model["extra_tags"] = sorted(list(model["extra_tags"]))

    return model, processed_count


def generate_yaml(model):
    # Simplificar para el output final
    output = {
        "metadata": {
            "total_us": len(model["user_stories"]),
            "total_roles": len(model["roles"]),
            "total_entities": len(model["entities"]),
            "total_processes": len(model["processes"]),
            "total_extra_tags": len(model["extra_tags"]),
        },
        "roles": list(model["roles"].values()),
        "entities": list(model["entities"].values()),
        "processes": list(model["processes"].values()),
        "tags": model["tags"],
        "extra_tags": model["extra_tags"],
        "user_stories": model["user_stories"],
        "acceptance_criteria": model["acceptance_criteria"],
    }

    with open(OUTPUT_YAML, "w", encoding="utf-8") as f:
        yaml.dump(output, f, allow_unicode=True, sort_keys=False)


def generate_sql(model):
    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write("-- Schema para US Model GORE_OS\n")
        f.write("-- Generado automáticamente\n\n")

        # Tablas dimensionales
        f.write(
            "CREATE TABLE dim_role (\n    id VARCHAR(50) PRIMARY KEY,\n    label TEXT,\n    agent_type VARCHAR(20),\n    description TEXT\n);\n\n"
        )
        f.write("CREATE TABLE dim_entity (\n    id VARCHAR(50) PRIMARY KEY\n);\n\n")
        f.write("CREATE TABLE dim_process (\n    id VARCHAR(50) PRIMARY KEY\n);\n\n")
        f.write(
            "CREATE TABLE dim_extra_tag (\n    tag_value VARCHAR(100) PRIMARY KEY\n);\n\n"
        )

        # Tabla de hechos US
        f.write("CREATE TABLE fact_user_story (\n")
        f.write("    id VARCHAR(50) PRIMARY KEY,\n")
        f.write("    urn TEXT,\n")
        f.write("    name TEXT,\n")
        f.write("    as_a TEXT,\n")
        f.write("    i_want TEXT,\n")
        f.write("    so_that TEXT,\n")
        f.write("    status VARCHAR(20),\n")
        f.write("    role_id VARCHAR(50) REFERENCES dim_role(id),\n")
        f.write("    process_id VARCHAR(50) REFERENCES dim_process(id),\n")
        f.write("    domain VARCHAR(50),\n")
        f.write("    aspect VARCHAR(50),\n")
        f.write("    priority VARCHAR(10),\n")
        f.write("    scope VARCHAR(20)\n")
        f.write(");\n\n")

        # Tabla AC (1:N)
        f.write("CREATE TABLE acceptance_criteria (\n")
        f.write("    id SERIAL PRIMARY KEY,\n")
        f.write("    us_id VARCHAR(50) REFERENCES fact_user_story(id),\n")
        f.write("    description TEXT\n")
        f.write(");\n\n")

        # Tablas puente
        f.write(
            "CREATE TABLE bridge_us_entity (\n    us_id VARCHAR(50) REFERENCES fact_user_story(id),\n    entity_id VARCHAR(50) REFERENCES dim_entity(id),\n    PRIMARY KEY (us_id, entity_id)\n);\n\n"
        )
        f.write(
            "CREATE TABLE bridge_us_extra_tag (\n    us_id VARCHAR(50) REFERENCES fact_user_story(id),\n    tag_value VARCHAR(100) REFERENCES dim_extra_tag(tag_value),\n    PRIMARY KEY (us_id, tag_value)\n);\n\n"
        )

        # Inserciones (DML simplificado para este script)
        # Roles
        for r in model["roles"].values():
            desc = (r["description"] or "").replace("'", "''")
            label = (r["label"] or "").replace("'", "''")
            f.write(
                f"INSERT INTO dim_role (id, label, agent_type, description) VALUES ('{r['id']}', '{label}', '{r['agent_type']}', '{desc}') ON CONFLICT DO NOTHING;\n"
            )

        # Entidades
        for e in model["entities"].values():
            f.write(
                f"INSERT INTO dim_entity (id) VALUES ('{e['id']}') ON CONFLICT DO NOTHING;\n"
            )

        # Procesos
        for p in model["processes"].values():
            f.write(
                f"INSERT INTO dim_process (id) VALUES ('{p['id']}') ON CONFLICT DO NOTHING;\n"
            )

        # Extra Tags
        for et in model["extra_tags"]:
            f.write(
                f"INSERT INTO dim_extra_tag (tag_value) VALUES ('{et}') ON CONFLICT DO NOTHING;\n"
            )

        f.write("\n-- User Stories y Relaciones\n")
        for us in model["user_stories"]:
            name = (us["name"] or "").replace("'", "''")
            as_a = (us["as_a"] or "").replace("'", "''")
            want = (us["i_want"] or "").replace("'", "''")
            that = (us["so_that"] or "").replace("'", "''")
            rid = f"'{us['role_id']}'" if us["role_id"] else "NULL"
            pid = f"'{us['process_id']}'" if us["process_id"] else "NULL"
            t = us["tags"]
            f.write(
                f"INSERT INTO fact_user_story (id, urn, name, as_a, i_want, so_that, status, role_id, process_id, domain, aspect, priority, scope) "
            )
            f.write(
                f"VALUES ('{us['id']}', '{us['urn']}', '{name}', '{as_a}', '{want}', '{that}', '{us['status']}', {rid}, {pid}, '{t.get('domain')}', '{t.get('aspect')}', '{t.get('priority')}', '{t.get('scope')}') ON CONFLICT DO NOTHING;\n"
            )

            # Bridge tags
            for et in us["extra_tags"]:
                f.write(
                    f"INSERT INTO bridge_us_extra_tag (us_id, tag_value) VALUES ('{us['id']}', '{et}') ON CONFLICT DO NOTHING;\n"
                )

        # AC
        for ac in model["acceptance_criteria"]:
            desc = ac["description"].replace("'", "''")
            f.write(
                f"INSERT INTO acceptance_criteria (us_id, description) VALUES ('{ac['us_id']}', '{desc}');\n"
            )


if __name__ == "__main__":
    print("Iniciando extracción de modelo de datos US...")
    full_model, count = extract_data()
    print(f"Historias de usuario procesadas: {count}")

    print("Generando archivo YAML...")
    generate_yaml(full_model)
    print(f"Archivo generado: {OUTPUT_YAML}")

    print("Generando script SQL...")
    generate_sql(full_model)
    print(f"Archivo generado: {OUTPUT_SQL}")
    print("Proceso completado.")
