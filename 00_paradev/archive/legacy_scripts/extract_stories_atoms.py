#!/usr/bin/env python3
"""
GORE_OS Story Atomization Script
Genera archivos individuales para cada historia de usuario (Story → Atom).

Ontología: v2.0.0
Fase: 5.1 (Uniformidad Categórica)
"""

import yaml
from pathlib import Path
import re

# Rutas base
BLUEPRINT_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint")
HU_FILE = BLUEPRINT_DIR / "historias_usuarios/historias_usuarios.yml"
STORIES_DIR = BLUEPRINT_DIR / "atoms/stories"


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, allow_unicode=True, default_flow_style=False, sort_keys=False
        )


def generate_story_key(story_id: str) -> str:
    """Convierte ID de historia a clave de archivo."""
    return story_id.lower().replace("-", "_")


def extract_stories():
    print("=" * 60)
    print("GORE_OS Story Atomization - Fase 5.1")
    print("=" * 60)

    hu_data = load_yaml(HU_FILE)
    stories = hu_data.get("atomic_stories", [])

    print(f"  Encontradas {len(stories)} historias en SSOT")

    generated = 0
    index_items = []

    for story in stories:
        story_id = story.get("id")
        if not story_id:
            continue

        story_key = generate_story_key(story_id)
        story_urn = f"urn:goreos:atom:story:{story_key}:1.0.0"

        # Construir átomo Story
        atom = {
            "_meta": {
                "urn": story_urn,
                "type": "Story",
                "source": "historias_usuarios/historias_usuarios.yml",
            },
            "id": story_id,
            "story_key": story_key,
            "role_id": story.get("role_id"),
            "as_a": story.get("as_a"),
            "i_want": story.get("i_want"),
            "so_that": story.get("so_that"),
            "domain": story.get("domain"),
            "priority": story.get("priority"),
            "capability_bundle_id": story.get("capability_bundle_id"),
            "morphisms": {
                "protagonizado_por": story.get("role_id"),
                "contribuye_a": story.get("capability_bundle_id"),
            },
        }

        # Guardar archivo
        filename = f"{story_key}.yml"
        save_yaml(atom, STORIES_DIR / filename)
        generated += 1

        # Agregar a índice
        index_items.append(
            {
                "id": story_id,
                "urn": story_urn,
                "role_id": story.get("role_id"),
                "domain": story.get("domain"),
            }
        )

    # Generar índice actualizado
    index = {
        "_meta": {
            "urn": "urn:goreos:index:stories:1.0.0",
            "type": "StoriesIndex",
            "generated_at": "2025-12-21",
        },
        "total": len(index_items),
        "items": index_items,
    }
    save_yaml(index, STORIES_DIR / "_index.yml")

    print(f"  ✓ {generated} archivos de historia generados")
    print(f"  ✓ Índice actualizado")
    print("=" * 60)


if __name__ == "__main__":
    extract_stories()
