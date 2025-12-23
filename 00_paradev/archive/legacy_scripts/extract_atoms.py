#!/usr/bin/env python3
"""
GORE_OS Atomic Extraction Script
Extrae átomos desde los archivos YAML actuales hacia la nueva estructura categórica.

Ontología: v2.0.0
Arquitecto: Arquitecto Categórico v1.3
"""

import yaml
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Any

# Rutas base
BLUEPRINT_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint")
HU_DIR = BLUEPRINT_DIR / "historias_usuarios"
ATOMS_DIR = BLUEPRINT_DIR / "atoms"
PROFUNCTORS_DIR = BLUEPRINT_DIR / "profunctors"


def load_yaml(path: Path) -> dict:
    """Carga un archivo YAML."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data: dict, path: Path):
    """Guarda datos en archivo YAML."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, allow_unicode=True, default_flow_style=False, sort_keys=False
        )
    print(f"  ✓ Saved: {path.name}")


def normalize_role_key(role_id: str) -> str:
    """Normaliza un role_id a role_key."""
    return role_id.lower().replace("-", "_")


# =============================================================================
# EXTRACTORES DE ÁTOMOS
# =============================================================================


def extract_roles(roles_data: dict) -> Dict[str, dict]:
    """Extrae roles a formato atómico desde la estructura real de roles.yml."""
    atoms = {}

    # Procesar archetypes (estructura anidada: external, municipal, internal_bases)
    archetypes = roles_data.get("archetypes", {})

    # Si archetypes es un dict (estructura anidada)
    if isinstance(archetypes, dict):
        # External archetypes (SEREMIs, Directores)
        for arch in archetypes.get("external", []):
            arch_id = arch.get("archetype_id", "")
            role_key = arch_id.lower().replace("-", "_")
            atoms[role_key] = {
                "_meta": {
                    "urn": f"urn:goreos:atom:role:{role_key}:1.0.0",
                    "type": "Role",
                    "source": "archetypes.external",
                },
                "id": f"ARCH-EXT-{arch_id.upper()}",
                "role_key": role_key,
                "title": arch.get("title", ""),
                "description": arch.get("description", ""),
                "type": "External",
                "archetype": None,
                "parameter": arch.get("parameter"),
                "morphisms_req": {"es_actor_de": []},
                "morphisms_ops": {"ejecuta": []},
            }

        # Municipal archetypes
        for arch in archetypes.get("municipal", []):
            arch_id = arch.get("archetype_id", "")
            role_key = arch_id.lower().replace("-", "_")
            atoms[role_key] = {
                "_meta": {
                    "urn": f"urn:goreos:atom:role:{role_key}:1.0.0",
                    "type": "Role",
                    "source": "archetypes.municipal",
                },
                "id": f"ARCH-MUN-{arch_id.upper()}",
                "role_key": role_key,
                "title": arch_id.replace("_", " ").title(),
                "description": arch.get("description", ""),
                "type": "External",
                "archetype": None,
                "member_roles": arch.get("member_roles", []),
                "morphisms_req": {"es_actor_de": []},
                "morphisms_ops": {"ejecuta": []},
            }

        # Internal bases
        for base in archetypes.get("internal_bases", []):
            base_id = base.get("base_id", "")
            role_key = base_id.lower().replace("-", "_")
            atoms[role_key] = {
                "_meta": {
                    "urn": f"urn:goreos:atom:role:{role_key}:1.0.0",
                    "type": "Role",
                    "source": "archetypes.internal_bases",
                },
                "id": f"ARCH-BASE-{base_id.upper()}",
                "role_key": role_key,
                "title": base.get("title_pattern", ""),
                "description": base.get("description", ""),
                "type": "Human",
                "archetype": None,
                "responsibilities": base.get("responsibilities", []),
                "morphisms_req": {"es_actor_de": []},
                "morphisms_ops": {"ejecuta": []},
            }

    # Procesar organization (unidades con roles)
    for unit_data in roles_data.get("organization", []):
        unit_name = unit_data.get("unit", "")
        unit_type = unit_data.get("type", "")

        for role in unit_data.get("roles", []):
            role_id = role.get("id", "")
            role_key = role.get("role_key", normalize_role_key(role_id))
            role_type = "Bot" if role_id.startswith("BOT-") else "Human"

            atoms[role_key] = {
                "_meta": {
                    "urn": f"urn:goreos:atom:role:{role_key}:1.0.0",
                    "type": "Role",
                    "source": "organization",
                },
                "id": role_id,
                "role_key": role_key,
                "title": role.get("title", ""),
                "description": role.get("description", ""),
                "type": role_type,
                "unit": unit_name,
                "unit_type": unit_type,
                "archetype": role.get("archetype"),
                "morphisms_req": {"es_actor_de": []},
                "morphisms_ops": {"ejecuta": []},
            }

    return atoms


def extract_capabilities(capabilities_data: dict) -> Dict[str, dict]:
    """Extrae capabilities a formato atómico."""
    atoms = {}

    for bundle in capabilities_data.get("capability_bundles", []):
        cap_id = bundle["id"]
        cap_key = cap_id.lower().replace("-", "_")

        # Determinar dominio desde el ID (ej: CAP-BACK-001 -> D-BACK)
        parts = cap_id.split("-")
        domain = f"D-{parts[1]}" if len(parts) > 1 else "D-UNKNOWN"

        atoms[cap_key] = {
            "_meta": {
                "urn": f"urn:goreos:atom:capability:{cap_key}:1.0.0",
                "type": "Capability",
            },
            "id": cap_id,
            "name": bundle.get("capability", ""),
            "domain": bundle.get("domain", domain),
            "type": "DOMAIN_SPECIFIC",
            "description": bundle.get("description", ""),
            "value_proposition": bundle.get("value_proposition", ""),
            "orko_mapping": bundle.get("orko_mapping", {}),
            "stories": [],  # Se poblará desde stories
            "ofrecida_por": None,  # Se derivará de módulos
        }

    return atoms


def extract_stories(
    stories_data: dict, role_atoms: Dict[str, dict], cap_atoms: Dict[str, dict]
) -> Dict[str, dict]:
    """Extrae stories a formato atómico y actualiza morfismos de roles."""
    atoms = {}

    for story in stories_data.get("atomic_stories", []):
        story_id = story["id"]
        story_key = story_id.lower().replace("-", "_")

        role_id = story.get("role_id", story.get("role", ""))
        cap_id = story.get("capability_bundle_id", "")

        # Determinar dominio
        parts = story_id.split("-")
        domain = f"D-{parts[1]}" if len(parts) > 1 else "D-UNKNOWN"

        atoms[story_key] = {
            "_meta": {
                "urn": f"urn:goreos:atom:story:{story_key}:1.0.0",
                "type": "Story",
            },
            "id": story_id,
            "role_id": f"urn:goreos:atom:role:{normalize_role_key(role_id)}",
            "as_a": story.get("as_a", ""),
            "i_want": story.get("i_want", ""),
            "so_that": story.get("so_that", ""),
            "domain": domain,
            "priority": story.get("priority", "P2"),
            "morphisms": {
                "contribuye_a": (
                    f"urn:goreos:atom:capability:{cap_id.lower().replace('-', '_')}"
                    if cap_id
                    else None
                ),
                "menciona": [],  # Se derivará del análisis de i_want
            },
        }

        # Actualizar morfismo es_actor_de en el rol
        role_key = normalize_role_key(role_id)
        if role_key in role_atoms:
            story_urn = f"urn:goreos:atom:story:{story_key}"
            if story_urn not in role_atoms[role_key]["morphisms_req"]["es_actor_de"]:
                role_atoms[role_key]["morphisms_req"]["es_actor_de"].append(story_urn)

        # Actualizar lista de stories en capability
        cap_key = cap_id.lower().replace("-", "_") if cap_id else None
        if cap_key and cap_key in cap_atoms:
            story_urn = f"urn:goreos:atom:story:{story_key}"
            if story_urn not in cap_atoms[cap_key]["stories"]:
                cap_atoms[cap_key]["stories"].append(story_urn)

    return atoms


# =============================================================================
# GENERADOR DE PROFUNCTORES
# =============================================================================


def generate_profunctor_role_story(role_atoms: Dict[str, dict]) -> dict:
    """Genera profunctor es_actor_de: Role ⊗ Story → 2."""
    relations = []

    for role_key, role in role_atoms.items():
        for story_urn in role["morphisms_req"]["es_actor_de"]:
            relations.append(
                {
                    "role": f"urn:goreos:atom:role:{role_key}",
                    "story": story_urn,
                    "evidence": {"active": True},
                }
            )

    return {
        "_meta": {
            "urn": "urn:goreos:profunctor:es_actor_de:1.0.0",
            "type": "Role ⊗ Story → 2",
            "generated_at": "2025-12-21",
        },
        "total_relations": len(relations),
        "relations": relations,
    }


def generate_profunctor_story_capability(story_atoms: Dict[str, dict]) -> dict:
    """Genera profunctor contribuye_a: Story → Capability."""
    relations = []

    for story_key, story in story_atoms.items():
        cap_urn = story["morphisms"].get("contribuye_a")
        if cap_urn:
            relations.append(
                {
                    "story": f"urn:goreos:atom:story:{story_key}",
                    "capability": cap_urn,
                    "evidence": {"contributes": True},
                }
            )

    return {
        "_meta": {
            "urn": "urn:goreos:profunctor:contribuye_a:1.0.0",
            "type": "Story → Capability",
            "generated_at": "2025-12-21",
        },
        "total_relations": len(relations),
        "relations": relations,
    }


# =============================================================================
# GENERADOR DE ÍNDICES
# =============================================================================


def generate_index(atoms: Dict[str, dict], atom_type: str) -> dict:
    """Genera archivo _index.yml para un tipo de átomo."""
    return {
        "_meta": {
            "urn": f"urn:goreos:index:{atom_type}:1.0.0",
            "type": f"{atom_type.capitalize()}Index",
            "generated_at": "2025-12-21",
        },
        "total": len(atoms),
        "items": [
            {
                "key": k,
                "urn": v["_meta"]["urn"],
                "title": v.get("title", v.get("name", k)),
            }
            for k, v in atoms.items()
        ],
    }


# =============================================================================
# MAIN
# =============================================================================


def main():
    print("=" * 60)
    print("GORE_OS Atomic Extraction - Ontología Categórica v2.0")
    print("=" * 60)

    # Cargar fuentes actuales
    print("\n[1/5] Cargando fuentes...")
    roles_data = load_yaml(HU_DIR / "roles.yml")
    capabilities_data = load_yaml(HU_DIR / "capabilities.yml")
    stories_data = load_yaml(HU_DIR / "historias_usuarios.yml")
    print(
        f"  ✓ roles.yml: {len(roles_data.get('archetypes', []))} archetypes, {len(roles_data.get('organizational_roles', []))} org_roles"
    )
    print(
        f"  ✓ capabilities.yml: {len(capabilities_data.get('capability_bundles', []))} bundles"
    )
    print(
        f"  ✓ historias_usuarios.yml: {len(stories_data.get('atomic_stories', []))} stories"
    )

    # Extraer átomos
    print("\n[2/5] Extrayendo átomos...")
    role_atoms = extract_roles(roles_data)
    print(f"  ✓ Roles: {len(role_atoms)}")

    cap_atoms = extract_capabilities(capabilities_data)
    print(f"  ✓ Capabilities: {len(cap_atoms)}")

    story_atoms = extract_stories(stories_data, role_atoms, cap_atoms)
    print(f"  ✓ Stories: {len(story_atoms)}")

    # Guardar átomos
    print("\n[3/5] Guardando átomos...")

    # Roles
    for role_key, role_data in role_atoms.items():
        save_yaml(role_data, ATOMS_DIR / "roles" / f"{role_key}.yml")
    save_yaml(generate_index(role_atoms, "roles"), ATOMS_DIR / "roles" / "_index.yml")

    # Capabilities
    for cap_key, cap_data in cap_atoms.items():
        save_yaml(cap_data, ATOMS_DIR / "capabilities" / f"{cap_key}.yml")
    save_yaml(
        generate_index(cap_atoms, "capabilities"),
        ATOMS_DIR / "capabilities" / "_index.yml",
    )

    # Stories (too many to save individually - save index only for now)
    save_yaml(
        generate_index(story_atoms, "stories"), ATOMS_DIR / "stories" / "_index.yml"
    )
    print(f"  ✓ Stories: saved index only ({len(story_atoms)} items)")

    # Generar profunctores
    print("\n[4/5] Generando profunctores...")

    prof_role_story = generate_profunctor_role_story(role_atoms)
    save_yaml(prof_role_story, PROFUNCTORS_DIR / "role-story.yml")

    prof_story_cap = generate_profunctor_story_capability(story_atoms)
    save_yaml(prof_story_cap, PROFUNCTORS_DIR / "story-capability.yml")

    # Estadísticas finales
    print("\n[5/5] Resumen")
    print("=" * 60)
    print(f"  Roles extraídos:       {len(role_atoms)}")
    print(f"  Capabilities extraídas: {len(cap_atoms)}")
    print(f"  Stories indexadas:     {len(story_atoms)}")
    print(f"  Profunctor role-story: {prof_role_story['total_relations']} relaciones")
    print(f"  Profunctor story-cap:  {prof_story_cap['total_relations']} relaciones")
    print("=" * 60)
    print("✓ Extracción completa")


if __name__ == "__main__":
    main()
