#!/usr/bin/env python3
"""
GORE_OS Fix Story-Capability Profunctor
Agrega sufijo :1.0.0 a las URNs para cumplir I14.

Ontología: v2.0.0
Fase: 4.5
"""

import yaml
from pathlib import Path

# Rutas base
BLUEPRINT_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint")
PROFUNCTORS_DIR = BLUEPRINT_DIR / "profunctors"
SC_FILE = PROFUNCTORS_DIR / "story-capability.yml"


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, allow_unicode=True, default_flow_style=False, sort_keys=False
        )


def fix_profunctor():
    print("Corregyendo Profunctor story-capability...")

    if not SC_FILE.exists():
        print("  ⚠ Archivo no encontrado")
        return

    data = load_yaml(SC_FILE)
    relations = data.get("relations", [])
    fixed = 0

    for rel in relations:
        # Fix Story URN
        if "story" in rel:
            urn = rel["story"]
            if not urn.endswith(":1.0.0"):
                rel["story"] = f"{urn}:1.0.0"
                fixed += 1

        # Fix Capability URN
        if "capability" in rel:
            urn = rel["capability"]
            if not urn.endswith(":1.0.0"):
                rel["capability"] = f"{urn}:1.0.0"
                fixed += 1

    save_yaml(data, SC_FILE)
    print(f"  ✓ Corregidas {fixed} referencias URN")


if __name__ == "__main__":
    fix_profunctor()
