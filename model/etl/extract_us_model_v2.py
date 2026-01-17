#!/usr/bin/env python3
"""
US Data Model Extractor v2.0
============================
Extrae el modelo de datos completo desde las 818 User Stories de GORE_OS.
Genera archivos YAML y SQL con todas las relaciones correctamente modeladas.

Uso:
    cd /Users/felixsanhueza/Developer/goreos/model
    python3 etl/extract_us_model_v2.py

Salidas:
    - us_model_complete.yml (modelo YAML con todas las US y dimensiones)
    - goreos_us_model_complete.sql (DDL + DML completo)
"""

import yaml
import os
import glob
import re
from collections import defaultdict
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════

STORIES_DIR = "/Users/felixsanhueza/Developer/goreos/model/stories"
OUTPUT_YAML = "/Users/felixsanhueza/Developer/goreos/model/us_model_complete.yml"
OUTPUT_SQL = "/Users/felixsanhueza/Developer/goreos/model/goreos_us_model_complete.sql"

# Sinónimos para normalización de extra_tags
SYNONYMS = {
    "notificaciones": "notificacion",
    "alertas": "alerta",
    "proyectos": "proyecto",
    "programas": "programa",
    "admisibilidades": "admisibilidad",
    "rendiciones": "rendicion",
    "usuarios": "usuario",
    "roles": "rol",
    "contratos": "contrato",
    "convenios": "convenio",
    "pagos": "pago",
    "garantias": "garantia",
    "procesos": "proceso",
    "documentos": "documento",
    "informes": "informe",
    "reportes": "reporte",
    "solicitudes": "solicitud",
}

# ══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE NORMALIZACIÓN
# ══════════════════════════════════════════════════════════════════════════════


def normalize_tag(tag: str) -> str:
    """Normaliza un tag a lowercase, kebab-case, y aplica sinónimos."""
    if not tag:
        return ""
    t = tag.lower().strip()
    t = re.sub(r"[^a-z0-9áéíóúñü]+", "-", t)
    t = t.strip("-")
    return SYNONYMS.get(t, t)


def escape_sql(value: str) -> str:
    """Escapa comillas simples para SQL."""
    if value is None:
        return ""
    return str(value).replace("'", "''")


# ══════════════════════════════════════════════════════════════════════════════
# EXTRACCIÓN DE DATOS
# ══════════════════════════════════════════════════════════════════════════════


def extract_all_stories():
    """Lee todas las US y extrae los datos estructurados."""

    # Estructuras para almacenar datos
    stories = []
    roles = {}  # id -> {id, label, agent_type, description, count}
    entities = {}  # id -> {id, domain, count}
    processes = {}  # id -> {id, count}
    extra_tags = {}  # tag -> count
    acceptance_criteria = []  # {us_id, description}

    # Relaciones N:M
    us_entities = []  # {us_id, entity_id, status}
    us_extra_tags = []  # {us_id, tag}

    # Leer todos los archivos US
    pattern = os.path.join(STORIES_DIR, "us_*.yml")
    files = sorted(glob.glob(pattern))

    print(f"📂 Encontrados {len(files)} archivos US")

    for i, filepath in enumerate(files):
        if i % 100 == 0:
            print(f"   Procesando... {i}/{len(files)}")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data or "id" not in data:
                continue

            us_id = data["id"]

            # ─────────────────────────────────────────────────────────────────
            # Extraer datos de la US
            # ─────────────────────────────────────────────────────────────────

            # Rol
            role_id = data.get("user", {}).get("role_id")
            if role_id:
                if role_id not in roles:
                    roles[role_id] = {
                        "id": role_id,
                        "label": data.get("as_a", ""),
                        "agent_type": data.get("user", {}).get("agent_type", "HUMAN"),
                        "description": data.get("user", {}).get("description", ""),
                        "count": 0,
                    }
                roles[role_id]["count"] += 1

            # Entidades mencionadas
            entity_ids = []
            for ent in data.get("entities_mentioned", []):
                ent_id = ent.get("id")
                ent_status = ent.get("status", "candidate")
                if ent_id:
                    entity_ids.append(ent_id)
                    domain = ent_id.split("-")[1] if "-" in ent_id else ""
                    if ent_id not in entities:
                        entities[ent_id] = {"id": ent_id, "domain": domain, "count": 0}
                    entities[ent_id]["count"] += 1
                    us_entities.append(
                        {"us_id": us_id, "entity_id": ent_id, "status": ent_status}
                    )

            # Proceso
            process_id = data.get("process_ref", {}).get("id")
            process_status = data.get("process_ref", {}).get("status", "candidate")
            if process_id:
                if process_id not in processes:
                    processes[process_id] = {"id": process_id, "count": 0}
                processes[process_id]["count"] += 1

            # Tags estructurados
            tags_data = data.get("tags", {})

            # Extra tags (normalizados)
            raw_extra_tags = data.get("extra_tags", []) or []
            normalized_tags = []
            for tag in raw_extra_tags:
                nt = normalize_tag(tag)
                if nt:
                    normalized_tags.append(nt)
                    extra_tags[nt] = extra_tags.get(nt, 0) + 1
                    us_extra_tags.append({"us_id": us_id, "tag": nt})

            # Acceptance criteria
            for ac in data.get("acceptance_criteria", []) or []:
                if ac:
                    acceptance_criteria.append({"us_id": us_id, "description": ac})

            # ─────────────────────────────────────────────────────────────────
            # Construir registro de la US
            # ─────────────────────────────────────────────────────────────────

            story = {
                "id": us_id,
                "urn": data.get("_meta", {}).get("urn", ""),
                "name": data.get("name", ""),
                "as_a": data.get("as_a", ""),
                "i_want": data.get("i_want", ""),
                "so_that": data.get("so_that", ""),
                "status": data.get("status", ""),
                "role_id": role_id,
                "process_id": process_id,
                "process_status": process_status,
                "entity_ids": entity_ids,
                "tags": {
                    "domain": tags_data.get("domain", ""),
                    "aspect": tags_data.get("aspect", ""),
                    "priority": tags_data.get("priority", ""),
                    "scope": tags_data.get("scope", ""),
                },
                "extra_tags": normalized_tags,
                "acceptance_criteria": [
                    ac["description"]
                    for ac in acceptance_criteria
                    if ac["us_id"] == us_id
                ],
            }
            stories.append(story)

        except Exception as e:
            print(f"   ⚠️  Error en {filepath}: {e}")

    print(f"✅ Procesadas {len(stories)} User Stories")

    return {
        "stories": stories,
        "roles": list(roles.values()),
        "entities": list(entities.values()),
        "processes": list(processes.values()),
        "extra_tags": sorted(
            [{"tag": k, "count": v} for k, v in extra_tags.items()],
            key=lambda x: -x["count"],
        ),
        "acceptance_criteria": acceptance_criteria,
        "us_entities": us_entities,
        "us_extra_tags": us_extra_tags,
    }


# ══════════════════════════════════════════════════════════════════════════════
# GENERACIÓN DE YAML
# ══════════════════════════════════════════════════════════════════════════════


def generate_yaml(data: dict):
    """Genera el archivo YAML completo."""

    output = {
        "metadata": {
            "version": "2.0.0",
            "generated_at": datetime.now().isoformat(),
            "source": "goreos/model/stories/*.yml",
            "statistics": {
                "total_stories": len(data["stories"]),
                "unique_roles": len(data["roles"]),
                "unique_entities": len(data["entities"]),
                "unique_processes": len(data["processes"]),
                "unique_extra_tags": len(data["extra_tags"]),
                "total_acceptance_criteria": len(data["acceptance_criteria"]),
                "total_us_entity_relations": len(data["us_entities"]),
                "total_us_tag_relations": len(data["us_extra_tags"]),
            },
        },
        "dimensions": {
            "roles": data["roles"],
            "entities": data["entities"],
            "processes": data["processes"],
            "extra_tags": data["extra_tags"],
        },
        "facts": {"stories": data["stories"]},
        "relations": {
            "us_entities": data["us_entities"],
            "us_extra_tags": data["us_extra_tags"],
            "acceptance_criteria": data["acceptance_criteria"],
        },
    }

    with open(OUTPUT_YAML, "w", encoding="utf-8") as f:
        yaml.dump(
            output, f, allow_unicode=True, sort_keys=False, default_flow_style=False
        )

    print(f"📄 Generado: {OUTPUT_YAML}")


# ══════════════════════════════════════════════════════════════════════════════
# GENERACIÓN DE SQL
# ══════════════════════════════════════════════════════════════════════════════


def generate_sql(data: dict):
    """Genera el archivo SQL DDL + DML completo."""

    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        # Header
        f.write(
            "-- ══════════════════════════════════════════════════════════════════════════════\n"
        )
        f.write("-- US Data Model - GORE_OS\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write(f"-- Stories: {len(data['stories'])}\n")
        f.write(
            "-- ══════════════════════════════════════════════════════════════════════════════\n\n"
        )

        # DDL
        f.write("-- DDL: TABLAS DIMENSIONALES\n\n")

        f.write(
            """CREATE TABLE IF NOT EXISTS dim_role (
    id VARCHAR(100) PRIMARY KEY,
    label TEXT,
    agent_type VARCHAR(20) DEFAULT 'HUMAN',
    description TEXT,
    usage_count INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS dim_entity (
    id VARCHAR(100) PRIMARY KEY,
    domain VARCHAR(20),
    usage_count INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS dim_process (
    id VARCHAR(100) PRIMARY KEY,
    usage_count INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS dim_extra_tag (
    tag VARCHAR(100) PRIMARY KEY,
    usage_count INT DEFAULT 0
);

"""
        )

        f.write("-- DDL: TABLA DE HECHOS\n\n")

        f.write(
            """CREATE TABLE IF NOT EXISTS fact_user_story (
    id VARCHAR(100) PRIMARY KEY,
    urn TEXT,
    name TEXT,
    as_a TEXT,
    i_want TEXT,
    so_that TEXT,
    status VARCHAR(20),
    role_id VARCHAR(100) REFERENCES dim_role(id),
    process_id VARCHAR(100) REFERENCES dim_process(id),
    process_status VARCHAR(20),
    domain VARCHAR(50),
    aspect VARCHAR(50),
    priority VARCHAR(10),
    scope VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS acceptance_criteria (
    id SERIAL PRIMARY KEY,
    us_id VARCHAR(100) REFERENCES fact_user_story(id) ON DELETE CASCADE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS bridge_us_entity (
    us_id VARCHAR(100) REFERENCES fact_user_story(id) ON DELETE CASCADE,
    entity_id VARCHAR(100) REFERENCES dim_entity(id) ON DELETE CASCADE,
    status VARCHAR(20),
    PRIMARY KEY (us_id, entity_id)
);

CREATE TABLE IF NOT EXISTS bridge_us_extra_tag (
    us_id VARCHAR(100) REFERENCES fact_user_story(id) ON DELETE CASCADE,
    tag VARCHAR(100) REFERENCES dim_extra_tag(tag) ON DELETE CASCADE,
    PRIMARY KEY (us_id, tag)
);

"""
        )

        # DML: Dimensiones
        f.write("-- DML: INSERCIÓN DE DIMENSIONES\n\n")

        for role in data["roles"]:
            f.write(
                f"INSERT INTO dim_role (id, label, agent_type, description, usage_count) VALUES ('{escape_sql(role['id'])}', '{escape_sql(role['label'])}', '{escape_sql(role['agent_type'])}', '{escape_sql(role['description'])}', {role['count']}) ON CONFLICT (id) DO NOTHING;\n"
            )
        f.write("\n")

        for entity in data["entities"]:
            f.write(
                f"INSERT INTO dim_entity (id, domain, usage_count) VALUES ('{escape_sql(entity['id'])}', '{escape_sql(entity['domain'])}', {entity['count']}) ON CONFLICT (id) DO NOTHING;\n"
            )
        f.write("\n")

        for process in data["processes"]:
            f.write(
                f"INSERT INTO dim_process (id, usage_count) VALUES ('{escape_sql(process['id'])}', {process['count']}) ON CONFLICT (id) DO NOTHING;\n"
            )
        f.write("\n")

        for tag in data["extra_tags"]:
            f.write(
                f"INSERT INTO dim_extra_tag (tag, usage_count) VALUES ('{escape_sql(tag['tag'])}', {tag['count']}) ON CONFLICT (tag) DO NOTHING;\n"
            )
        f.write("\n")

        # DML: Hechos
        f.write("-- DML: INSERCIÓN DE USER STORIES\n\n")

        for us in data["stories"]:
            role_id = f"'{escape_sql(us['role_id'])}'" if us["role_id"] else "NULL"
            process_id = (
                f"'{escape_sql(us['process_id'])}'" if us["process_id"] else "NULL"
            )

            f.write(
                f"""INSERT INTO fact_user_story (id, urn, name, as_a, i_want, so_that, status, role_id, process_id, process_status, domain, aspect, priority, scope)
VALUES ('{escape_sql(us['id'])}', '{escape_sql(us['urn'])}', '{escape_sql(us['name'])}', '{escape_sql(us['as_a'])}', '{escape_sql(us['i_want'])}', '{escape_sql(us['so_that'])}', '{escape_sql(us['status'])}', {role_id}, {process_id}, '{escape_sql(us['process_status'])}', '{escape_sql(us['tags']['domain'])}', '{escape_sql(us['tags']['aspect'])}', '{escape_sql(us['tags']['priority'])}', '{escape_sql(us['tags']['scope'])}')
ON CONFLICT (id) DO NOTHING;
"""
            )

        f.write("\n-- DML: RELACIONES US-ENTITY\n\n")
        for rel in data["us_entities"]:
            f.write(
                f"INSERT INTO bridge_us_entity (us_id, entity_id, status) VALUES ('{escape_sql(rel['us_id'])}', '{escape_sql(rel['entity_id'])}', '{escape_sql(rel['status'])}') ON CONFLICT DO NOTHING;\n"
            )

        f.write("\n-- DML: RELACIONES US-EXTRA_TAG\n\n")
        for rel in data["us_extra_tags"]:
            f.write(
                f"INSERT INTO bridge_us_extra_tag (us_id, tag) VALUES ('{escape_sql(rel['us_id'])}', '{escape_sql(rel['tag'])}') ON CONFLICT DO NOTHING;\n"
            )

        f.write("\n-- DML: ACCEPTANCE CRITERIA\n\n")
        for ac in data["acceptance_criteria"]:
            f.write(
                f"INSERT INTO acceptance_criteria (us_id, description) VALUES ('{escape_sql(ac['us_id'])}', '{escape_sql(ac['description'])}');\n"
            )

    print(f"📄 Generado: {OUTPUT_SQL}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════


def main():
    print(
        "╔══════════════════════════════════════════════════════════════════════════════╗"
    )
    print(
        "║  US Data Model Extractor v2.0 - GORE_OS                                      ║"
    )
    print(
        "╚══════════════════════════════════════════════════════════════════════════════╝"
    )
    print()

    # Verificar directorio
    if not os.path.exists(STORIES_DIR):
        print(f"❌ Directorio no encontrado: {STORIES_DIR}")
        return

    # Extraer datos
    print("🔍 Extrayendo datos de User Stories...")
    data = extract_all_stories()

    # Generar YAML
    print("\n📝 Generando archivo YAML...")
    generate_yaml(data)

    # Generar SQL
    print("\n🗃️  Generando archivo SQL...")
    generate_sql(data)

    # Resumen
    print("\n" + "═" * 78)
    print("📊 RESUMEN DE EXTRACCIÓN")
    print("═" * 78)
    print(f"   • User Stories:        {len(data['stories'])}")
    print(f"   • Roles únicos:        {len(data['roles'])}")
    print(f"   • Entidades únicas:    {len(data['entities'])}")
    print(f"   • Procesos únicos:     {len(data['processes'])}")
    print(f"   • Extra tags únicos:   {len(data['extra_tags'])}")
    print(f"   • Criterios aceptación: {len(data['acceptance_criteria'])}")
    print(f"   • Relaciones US↔ENT:   {len(data['us_entities'])}")
    print(f"   • Relaciones US↔TAG:   {len(data['us_extra_tags'])}")
    print("═" * 78)
    print("✅ Proceso completado con éxito!")


if __name__ == "__main__":
    main()
