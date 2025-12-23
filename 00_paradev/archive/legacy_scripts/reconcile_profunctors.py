#!/usr/bin/env python3
"""
GORE_OS Profunctor Reconciliation Script
Reconcilia la relación Role-Story mapeando IDs a URNs canónicos.

Ontología: v2.0.0
Fase: 3
"""

import yaml
from pathlib import Path
from typing import Dict

# Rutas base
BLUEPRINT_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint")
ATOMS_DIR = BLUEPRINT_DIR / "atoms"
PROFUNCTORS_DIR = BLUEPRINT_DIR / "profunctors"
HU_FILE = BLUEPRINT_DIR / "historias_usuarios/historias_usuarios.yml"


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, allow_unicode=True, default_flow_style=False, sort_keys=False
        )


def build_role_map() -> Dict[str, str]:
    """Construye mapa RoleID -> RoleURN desde átomos."""
    role_map = {}
    print("  Construyendo mapa de roles...")

    # Iterar sobre todos los archivos de rol
    for role_file in ATOMS_DIR.glob("roles/*.yml"):
        if role_file.name == "_index.yml":
            continue

        role_data = load_yaml(role_file)
        role_id = role_data.get("id")
        role_urn = role_data.get("_meta", {}).get("urn")

        if role_id and role_urn:
            role_map[role_id] = role_urn

    print(f"  ✓ {len(role_map)} roles indexados")
    return role_map


def reconcile_role_story(role_map: Dict[str, str]):
    """Genera profunctor Role ⊗ Story → 2."""
    print("  Reconciliando Stories...")

    stories_data = load_yaml(HU_FILE)
    relations = []
    missing_roles = set()

    for story in stories_data.get("atomic_stories", []):
        story_id = story["id"]
        story_key = story_id.lower().replace("-", "_")
        story_urn = f"urn:goreos:atom:story:{story_key}:1.0.0"

        role_id = story.get("role_id", story.get("role"))

        if role_id in role_map:
            relations.append(
                {
                    "role": role_map[role_id],
                    "story": story_urn,
                    "evidence": {"active": True},
                }
            )
        else:
            missing_roles.add(role_id)

    if missing_roles:
        print(f"  ⚠ Roles no encontrados: {len(missing_roles)}")
        for r in list(missing_roles)[:5]:
            print(f"    - {r}")

    profunctor = {
        "_meta": {
            "urn": "urn:goreos:profunctor:es_actor_de:1.0.0",
            "type": "Role ⊗ Story → 2",
            "generated_at": "2025-12-21",
            "reconciled": True,
        },
        "total_relations": len(relations),
        "relations": relations,
    }

    save_yaml(profunctor, PROFUNCTORS_DIR / "role-story.yml")
    print(f"  ✓ Guardado profunctor/role-story.yml con {len(relations)} relaciones")


def main():
    print("=" * 60)
    print("GORE_OS Profunctor Reconciliation - Fase 3")
    print("=" * 60)

    role_map = build_role_map()
    reconcile_role_story(role_map)

    print("=" * 60)
    print("✓ Reconciliación completa")


if __name__ == "__main__":
    main()
