#!/usr/bin/env python3
"""
GORE_OS Module/Process Extraction Script
Extrae módulos y procesos desde los archivos domain_*.md hacia la estructura atómica.

Ontología: v2.0.0
Fase: 2
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Rutas base
BLUEPRINT_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint")
DOMAINS_DIR = BLUEPRINT_DIR / "domains"
ATOMS_DIR = BLUEPRINT_DIR / "atoms"

# Mapeo de dominios
DOMAIN_FILES = [
    "domain_d-back.md",
    "domain_d-fin.md",
    "domain_d-ejec.md",
    "domain_d-plan.md",
    "domain_d-norm.md",
    "domain_d-gob.md",
    "domain_d-tde.md",
    "domain_d-terr.md",
    "domain_d-seg.md",
    "domain_d-gestion.md",
    "domain_d-evol.md",
    "domain_d-ops.md",
    "domain_d-dev.md",
    "domain_fenix.md",
]

# D-FIN Subdominios (estructura: d-fin/sub_dfin_*.md)
DFIN_SUBDOMAINS = [
    "d-fin/sub_dfin_ejecutores.md",
    "d-fin/sub_dfin_ipr_core.md",
    "d-fin/sub_dfin_mecanismos.md",
    "d-fin/sub_dfin_portafolio.md",
    "d-fin/sub_dfin_presupuesto.md",
    "d-fin/sub_dfin_rendiciones.md",
]


def extract_domain_id(filename: str) -> str:
    """Extrae el ID del dominio desde el nombre del archivo."""
    if filename == "domain_fenix.md":
        return "FENIX"
    # Handle D-FIN subdomains
    if filename.startswith("d-fin/sub_dfin_"):
        subname = filename.replace("d-fin/sub_dfin_", "").replace(".md", "")
        return f"D-FIN-{subname.upper()}"
    match = re.search(r"domain_d-(\w+)\.md", filename)
    return f"D-{match.group(1).upper()}" if match else "D-UNKNOWN"


def parse_modules(content: str, domain_id: str) -> List[Dict]:
    """Extrae módulos desde la sección ## Módulos o ## Módulos Funcionales (Tablas)."""
    modules = []

    # 1. Estrategia Original: Header Standard (### 1. Nombre)
    modules_section = re.search(r"## Módulos\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if modules_section:
        section_text = modules_section.group(1)
        module_pattern = r"### (\d+)\. ([^\n]+)\n(.*?)(?=\n### \d+\.|\Z)"
        for match in re.finditer(module_pattern, section_text, re.DOTALL):
            num = match.group(1)
            name = match.group(2).strip()
            body = match.group(3).strip()

            subsystems = []
            subsystems_match = re.search(r"Subsistemas:\s*\n((?:- [^\n]+\n?)+)", body)
            if subsystems_match:
                for line in subsystems_match.group(1).split("\n"):
                    if line.strip().startswith("- "):
                        subsystems.append(line.strip()[2:])

            module_key = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
            module_id = f"MOD-{domain_id.replace('D-', '')}-{module_key.upper()[:20]}"

            modules.append(
                {
                    "_meta": {
                        "urn": f"urn:goreos:atom:module:{domain_id.lower().replace('-', '_')}_{module_key}:1.0.0",
                        "type": "Module",
                        "source": f"domains/{domain_id.lower()}",
                    },
                    "id": module_id,
                    "name": name,
                    "domain": domain_id,
                    "number": int(num),
                    "type": "DOMAIN_SPECIFIC",
                    "subsystems": subsystems if subsystems else None,
                    "morphisms": {
                        "capabilities": [],
                        "implementado_por": [],
                        "depends_on": [],
                    },
                }
            )

    # 2. Estrategia Tabla (D-FIN): ## Módulos Funcionales
    table_section = re.search(
        r"## Módulos Funcionales\s*\n\n?\|[^\n]+\|\s*\n\|[-\s|]+\|\s*\n((?:\|[^\n]+\|\s*\n)+)",
        content,
    )
    if table_section:
        rows = table_section.group(1).strip().split("\n")
        # Format: | # | Módulo | Función | Subdominio |
        for row in rows:
            cols = [c.strip() for c in row.split("|")[1:-1]]
            if len(cols) >= 2:
                mod_num_str = cols[0].replace("M", "")
                mod_name = cols[1]

                if mod_num_str.isdigit():
                    num = int(mod_num_str)
                    module_key = re.sub(r"[^a-z0-9]+", "_", mod_name.lower()).strip("_")
                    module_id = (
                        f"MOD-{domain_id.replace('D-', '')}-{module_key.upper()[:20]}"
                    )

                    # Check duplication
                    if any(m["name"] == mod_name for m in modules):
                        continue

                    modules.append(
                        {
                            "_meta": {
                                "urn": f"urn:goreos:atom:module:{domain_id.lower().replace('-', '_')}_{module_key}:1.0.0",
                                "type": "Module",
                                "source": f"domains/{domain_id.lower()}/table",
                            },
                            "id": module_id,
                            "name": mod_name,
                            "domain": domain_id,
                            "number": num,
                            "type": "DOMAIN_SPECIFIC",
                            "morphisms": {
                                "capabilities": [],
                                "implementado_por": [],
                                "depends_on": [],
                            },
                        }
                    )

    return modules


def parse_processes(content: str, domain_id: str) -> List[Dict]:
    """Extrae procesos desde la sección ## 📋 Procesos BPMN o headers inline."""
    processes = []

    # Buscar sección de procesos BPMN
    bpmn_section = re.search(
        r"## 📋 Procesos BPMN\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL
    )
    if not bpmn_section:
        # Intentar variantes
        bpmn_section = re.search(
            r"## Procesos BPMN\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL
        )
    if not bpmn_section:
        bpmn_section = re.search(
            r"## Procesos\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL
        )

    section_text = bpmn_section.group(1) if bpmn_section else content

    # Extraer índice de procesos si existe
    index_match = re.search(
        r"\|\s*Dominio\s*\|\s*ID\s*\|\s*Nombre\s*\|\s*Líneas\s*\|\s*\n\|[-\s|]+\|\s*\n((?:\|[^\n]+\|\s*\n)+)",
        section_text,
    )
    if index_match:
        for row in index_match.group(1).strip().split("\n"):
            cols = [c.strip() for c in row.split("|")[1:-1]]
            if len(cols) >= 3:
                proc_domain = cols[0]
                proc_id = cols[1]
                proc_name = cols[2]

                proc_key = re.sub(r"[^a-z0-9]+", "_", proc_name.lower()).strip("_")

                processes.append(
                    {
                        "_meta": {
                            "urn": f"urn:goreos:atom:process:{domain_id.lower().replace('-', '_')}_{proc_id.lower()}:1.0.0",
                            "type": "Process",
                            "source": f"domains/{domain_id.lower()}",
                        },
                        "id": f"PROC-{domain_id.replace('D-', '')}-{proc_id}",
                        "code": proc_id,
                        "name": proc_name,
                        "domain": domain_id,
                        "subdomain": proc_domain,
                        "type": "BPMN",
                        "morphisms": {
                            "roles_ejecutores": [],
                            "manipula": [],
                            "triggers": [],
                        },
                    }
                )

    # También extraer procesos inline (### DXX: Nombre, #### P1: Nombre, ## P4-bis: Nombre)
    inline_pattern = r"(?:##|###|####)\s*(D\d+(?:\.\w)?|P\d+(?:-\w+)?|P\d+):\s*([^\n]+)"
    for match in re.finditer(inline_pattern, content):  # Search whole content
        proc_id = match.group(1)
        proc_name = match.group(2).strip()

        # Evitar duplicados
        if any(p["code"] == proc_id for p in processes):
            continue

        proc_key = re.sub(r"[^a-z0-9]+", "_", proc_name.lower()).strip("_")

        processes.append(
            {
                "_meta": {
                    "urn": f"urn:goreos:atom:process:{domain_id.lower().replace('-', '_')}_{proc_id.lower().replace('-', '_')}:1.0.0",
                    "type": "Process",
                    "source": f"domains/{domain_id.lower()}",
                },
                "id": f"PROC-{domain_id.replace('D-', '')}-{proc_id}",
                "code": proc_id,
                "name": proc_name,
                "domain": domain_id,
                "type": "BPMN",
                "morphisms": {"roles_ejecutores": [], "manipula": [], "triggers": []},
            }
        )

    return processes


def extract_entities_from_glossary(content: str, domain_id: str) -> List[Dict]:
    """Extrae entidades desde tablas de glosario o sección 'Entidades de Datos'."""
    entities = []

    # Buscar glosario (primary pattern)
    glossary_match = re.search(
        r"## Glosario[^\n]*\n\n\|[^\n]+\|\s*\n\|[-\s|]+\|\s*\n((?:\|[^\n]+\|\s*\n)+)",
        content,
    )

    # Buscar "Entidades de Datos" (D-FIN subdomains pattern)
    entity_data_match = re.search(
        r"## Entidades de Datos\s*\n\n?\|[^\n]+\|\s*\n\|[-\s|]+\|\s*\n((?:\|[^\n]+\|\s*\n)+)",
        content,
    )

    sources = []
    if glossary_match:
        sources.append(("glossary", glossary_match.group(1)))
    if entity_data_match:
        sources.append(("entity_data", entity_data_match.group(1)))

    for source_type, rows_text in sources:
        for row in rows_text.strip().split("\n"):
            cols = [c.strip() for c in row.split("|")[1:-1]]
            if len(cols) >= 2:
                term = cols[0].strip("`")  # Remove backticks if present
                definition = cols[1]

                # Filtrar términos que parecen entidades (sustantivos, no acrónimos puros)
                if len(term) > 2 and not term.isupper():
                    entity_key = re.sub(r"[^a-z0-9]+", "_", term.lower()).strip("_")

                    # Avoid duplicates
                    if any(e["entity_key"] == entity_key for e in entities):
                        continue

                    entities.append(
                        {
                            "_meta": {
                                "urn": f"urn:goreos:atom:entity:{domain_id.lower().replace('-', '_')}_{entity_key}:1.0.0",
                                "type": "Entity",
                                "source": f"domains/{domain_id.lower()}/{source_type}",
                            },
                            "id": f"ENT-{domain_id.replace('D-', '')}-{entity_key.upper()[:20]}",
                            "name": term,
                            "entity_key": entity_key,
                            "domain": domain_id,
                            "category": "Reference",
                            "description": definition,
                            "morphisms": {
                                "manipulado_por": [],
                                "mencionado_en": [],
                                "relacionado_con": [],
                            },
                        }
                    )

    return entities


def save_yaml(data: dict, path: Path):
    """Guarda datos en archivo YAML."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, allow_unicode=True, default_flow_style=False, sort_keys=False
        )


def generate_index(atoms: List[Dict], atom_type: str) -> dict:
    """Genera archivo _index.yml."""
    return {
        "_meta": {
            "urn": f"urn:goreos:index:{atom_type}:1.0.0",
            "type": f"{atom_type.capitalize()}Index",
            "generated_at": "2025-12-21",
        },
        "total": len(atoms),
        "items": [
            {
                "id": a["id"],
                "urn": a["_meta"]["urn"],
                "name": a.get("name", a["id"]),
                "domain": a.get("domain"),
            }
            for a in atoms
        ],
    }


def main():
    print("=" * 60)
    print("GORE_OS Module/Process Extraction - Fase 2.1")
    print("=" * 60)

    all_modules = []
    all_processes = []
    all_entities = []

    # Combine all files to process
    all_domain_files = DOMAIN_FILES + DFIN_SUBDOMAINS

    for domain_file in all_domain_files:
        filepath = DOMAINS_DIR / domain_file
        if not filepath.exists():
            print(f"  ⚠ Not found: {domain_file}")
            continue

        domain_id = extract_domain_id(domain_file)
        print(f"\n[{domain_id}] Procesando {domain_file}...")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extraer módulos
        modules = parse_modules(content, domain_id)
        print(f"  ✓ Módulos: {len(modules)}")
        all_modules.extend(modules)

        # Extraer procesos
        processes = parse_processes(content, domain_id)
        print(f"  ✓ Procesos: {len(processes)}")
        all_processes.extend(processes)

        # Extraer entidades del glosario
        entities = extract_entities_from_glossary(content, domain_id)
        print(f"  ✓ Entidades (glosario): {len(entities)}")
        all_entities.extend(entities)

    # Guardar átomos
    print("\n" + "=" * 60)
    print("Guardando átomos...")

    # Módulos
    for mod in all_modules:
        domain_prefix = mod["domain"].lower().replace("-", "_")
        mod_key = mod["_meta"]["urn"].split(":")[-2]
        filename = f"{domain_prefix}_{mod_key}.yml"
        save_yaml(mod, ATOMS_DIR / "modules" / filename)
    save_yaml(
        generate_index(all_modules, "modules"), ATOMS_DIR / "modules" / "_index.yml"
    )
    print(f"  ✓ {len(all_modules)} módulos guardados")

    # Procesos
    for proc in all_processes:
        domain_prefix = proc["domain"].lower().replace("-", "_")
        proc_key = proc["code"].lower().replace(".", "_")
        filename = f"{domain_prefix}_{proc_key}.yml"
        save_yaml(proc, ATOMS_DIR / "processes" / filename)
    save_yaml(
        generate_index(all_processes, "processes"),
        ATOMS_DIR / "processes" / "_index.yml",
    )
    print(f"  ✓ {len(all_processes)} procesos guardados")

    # Entidades
    for ent in all_entities:
        domain_prefix = ent["domain"].lower().replace("-", "_")
        ent_key = ent["entity_key"]
        filename = f"{domain_prefix}_{ent_key}.yml"
        save_yaml(ent, ATOMS_DIR / "entities" / filename)
    save_yaml(
        generate_index(all_entities, "entities"), ATOMS_DIR / "entities" / "_index.yml"
    )
    print(f"  ✓ {len(all_entities)} entidades guardadas")

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN FASE 2")
    print("=" * 60)
    print(f"  Dominios procesados: {len(DOMAIN_FILES)}")
    print(f"  Módulos extraídos:   {len(all_modules)}")
    print(f"  Procesos extraídos:  {len(all_processes)}")
    print(f"  Entidades extraídas: {len(all_entities)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
