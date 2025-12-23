#!/usr/bin/env python3
"""
GORE_OS Manifest Generator
Genera un inventario completo de átomos y profunctores.
Ontología v3.0.0
"""

import yaml
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def load_yaml_safe(path: Path) -> dict:
    """Carga YAML manejando errores."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        return {"_error": str(e)}


def scan_atoms(base_path: Path, atom_type: str) -> list:
    """Escanea átomos de un tipo específico."""
    atom_path = base_path / "model" / "atoms" / atom_type
    if not atom_path.exists():
        return []

    items = []
    for file in sorted(atom_path.glob("*.yml")):
        if file.name.startswith("_"):
            continue

        data = load_yaml_safe(file)
        item = {
            "file": file.name,
            "id": data.get("id", data.get("story_key", data.get("role_key", ""))),
            "urn": data.get("urn", data.get("_meta", {}).get("urn", "")),
            "name": data.get("name", data.get("title", "")),
            "domain": data.get("domain", ""),
        }

        if "_error" in data:
            item["error"] = data["_error"]

        items.append(item)

    return items


def scan_profunctors(base_path: Path) -> list:
    """Escanea profunctores."""
    prof_path = base_path / "model" / "profunctors"
    if not prof_path.exists():
        return []

    items = []
    for file in sorted(prof_path.glob("*.yml")):
        if file.name.startswith("_"):
            continue

        data = load_yaml_safe(file)
        links = data.get("links", [])
        item = {
            "file": file.name,
            "id": data.get("id", ""),
            "urn": data.get("urn", data.get("_meta", {}).get("urn", "")),
            "links_count": len(links) if isinstance(links, list) else 0,
        }
        items.append(item)

    return items


def scan_schemas(base_path: Path) -> list:
    """Escanea schemas JSON."""
    schema_path = base_path / "schemas"
    if not schema_path.exists():
        return []

    items = []
    for file in sorted(schema_path.glob("*.json")):
        items.append({"file": file.name})

    return items


def generate_manifest(base_path: Path) -> dict:
    """Genera el manifest completo."""

    atom_types = ["stories", "entities", "roles", "processes", "modules"]

    manifest = {
        "_meta": {
            "urn": "urn:goreos:catalog:inventory:1.0.0",
            "type": "Inventory",
            "generated_at": datetime.now().isoformat(),
            "ontology_version": "v3.0.0",
        },
        "summary": {},
        "atoms": {},
        "profunctors": [],
        "schemas": [],
    }

    # Scan atoms
    total_atoms = 0
    for atom_type in atom_types:
        items = scan_atoms(base_path, atom_type)
        manifest["atoms"][atom_type] = {
            "count": len(items),
            "items": items,
        }
        total_atoms += len(items)

    # Scan profunctors
    profunctors = scan_profunctors(base_path)
    manifest["profunctors"] = {
        "count": len(profunctors),
        "total_links": sum(p.get("links_count", 0) for p in profunctors),
        "items": profunctors,
    }

    # Scan schemas
    schemas = scan_schemas(base_path)
    manifest["schemas"] = {
        "count": len(schemas),
        "items": schemas,
    }

    # Summary
    manifest["summary"] = {
        "total_atoms": total_atoms,
        "total_profunctors": len(profunctors),
        "total_schemas": len(schemas),
        "atoms_by_type": {t: manifest["atoms"][t]["count"] for t in atom_types},
    }

    return manifest


def main():
    base_path = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    output_path = base_path / "model" / "catalog" / "_inventory.yml"

    print("=== GORE_OS Manifest Generator ===")
    print(f"Base: {base_path}")
    print()

    manifest = generate_manifest(base_path)

    # Print summary
    s = manifest["summary"]
    print(f"Total Atoms: {s['total_atoms']}")
    for t, c in s["atoms_by_type"].items():
        print(f"  - {t}: {c}")
    print(f"Total Profunctors: {s['total_profunctors']}")
    print(f"Total Schemas: {s['total_schemas']}")
    print()

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(
            manifest, f, allow_unicode=True, sort_keys=False, default_flow_style=False
        )

    print(f"Saved to: {output_path}")
    print("Done.")


if __name__ == "__main__":
    main()
