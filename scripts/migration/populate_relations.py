#!/usr/bin/env python3
"""
GORE_OS Relationship Populator v2 - Fixed URN extraction
"""

import re
from pathlib import Path
from collections import defaultdict


class Config:
    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    MODEL_DIR = GORE_OS_ROOT / "model"
    ATOMS_DIR = MODEL_DIR / "atoms"
    PROFUNCTORS_DIR = MODEL_DIR / "profunctors"


def extract_meta_urn(content: str) -> str:
    """Extrae URN del bloque _meta"""
    m = re.search(r'_meta:\s*\n\s+urn:\s*"?([^"\n]+)"?', content)
    return m.group(1).strip() if m else ""


def extract_field(content: str, field: str) -> str:
    m = re.search(rf"^{field}:\s*(.+)$", content, re.MULTILINE)
    return m.group(1).strip().strip("\"'") if m else ""


def extract_all_urns(content: str) -> list:
    """Extrae todos los URNs de cualquier parte del contenido"""
    return re.findall(r"urn:goreos:atom:[^:\s,\]]+:[^:\s,\]]+:[^\s,\]]+", content)


def populate_ejecuta():
    """Roles → Processes: Usar procesos que mencionan roles en mermaid"""
    print("\n=== Populating ejecuta (Roles → Processes) ===")

    relations = []
    processes_dir = Config.ATOMS_DIR / "processes"
    roles_dir = Config.ATOMS_DIR / "roles"

    # Cargar roles
    role_lookup = {}
    for f in roles_dir.glob("*.yml"):
        if f.name.startswith("_") or f.name.startswith("."):
            continue
        try:
            content = f.read_text()
            urn = extract_meta_urn(content)
            title = extract_field(content, "title")
            if urn and title:
                role_lookup[title.lower()] = urn
        except:
            pass

    print(f"  Roles indexed: {len(role_lookup)}")

    # Analizar procesos buscando menciones a roles en mermaid
    keywords_to_roles = {
        "gobernador": "gobernador regional",
        "dipir": "jefe dipir",
        "daf": "jefe daf",
        "uj": "abogado",
        "ejecutor": "ejecutor",
        "ito": "inspector técnico",
        "analista": "analista",
    }

    for f in processes_dir.glob("*.yml"):
        if f.name.startswith("_"):
            continue
        try:
            content = f.read_text()
            proc_urn = extract_meta_urn(content)
            if not proc_urn:
                continue

            content_lower = content.lower()
            for keyword, role_hint in keywords_to_roles.items():
                if keyword in content_lower:
                    for role_title, role_urn in role_lookup.items():
                        if role_hint in role_title:
                            relations.append((role_urn, proc_urn))
                            break
        except:
            pass

    # Escribir profunctor
    write_profunctor("ejecuta", "Role", "Process", relations)
    return len(set(relations))


def populate_module_relations():
    """Modules → Processes/Entities: Usar composition block"""
    print("\n=== Populating module relations ===")

    mod_proc_rels = []
    mod_ent_rels = []

    modules_dir = Config.ATOMS_DIR / "modules"

    for f in modules_dir.glob("*.yml"):
        if f.name.startswith("_") or f.name.startswith("."):
            continue
        try:
            content = f.read_text()
            mod_urn = extract_meta_urn(content)
            if not mod_urn:
                continue

            # Extraer URNs de composition
            all_urns = extract_all_urns(content)

            for urn in all_urns:
                if urn == mod_urn:
                    continue
                if ":process:" in urn:
                    mod_proc_rels.append((mod_urn, urn))
                elif ":entity:" in urn:
                    mod_ent_rels.append((mod_urn, urn))
        except:
            pass

    write_profunctor("module_contains_process", "Module", "Process", mod_proc_rels)
    write_profunctor("module_manages_entity", "Module", "Entity", mod_ent_rels)

    print(f"  Module → Process: {len(set(mod_proc_rels))}")
    print(f"  Module → Entity: {len(set(mod_ent_rels))}")

    return len(set(mod_proc_rels)) + len(set(mod_ent_rels))


def write_profunctor(name: str, source_type: str, target_type: str, relations: list):
    if not relations:
        print(f"  ⚠️ No relations for {name}")
        return

    lines = [
        "_meta:",
        f'  urn: "urn:goreos:profunctor:{name}:1.0.0"',
        "  type: Profunctor",
        '  ontology_version: "3.0.0"',
        "",
        "signature:",
        f"  source_type: {source_type}",
        f"  target_type: {target_type}",
        "",
        "relations:",
    ]

    seen = set()
    for src, tgt in relations:
        if (src, tgt) in seen:
            continue
        seen.add((src, tgt))
        lines.append(f'  - source: "{src}"')
        lines.append(f'    target: "{tgt}"')

    (Config.PROFUNCTORS_DIR / f"{name}.yml").write_text("\n".join(lines))
    print(f"  ✅ Written {name}.yml with {len(seen)} relations")


if __name__ == "__main__":
    print("=" * 60)
    print("Relationship Populator v2")
    print("=" * 60)

    total = 0
    total += populate_ejecuta()
    total += populate_module_relations()

    print("\n" + "=" * 60)
    print(f"Total new relations created: {total}")
    print("=" * 60)
