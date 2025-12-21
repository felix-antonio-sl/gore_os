#!/usr/bin/env python3
"""
GORE_OS Domain Composition Script
Agrega átomos en composiciones de dominio (Categoría Domain).

Ontología: v2.0.0
Fase: 4
"""

import yaml
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

# Rutas base
BLUEPRINT_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint")
ATOMS_DIR = BLUEPRINT_DIR / "atoms"
COMPOSITIONS_DIR = BLUEPRINT_DIR / "compositions/domains"


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(data: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, allow_unicode=True, default_flow_style=False, sort_keys=False
        )


def scan_atoms() -> Dict[str, Dict[str, List[str]]]:
    """Escanea todos los átomos y los agrupa por dominio."""
    domain_map = defaultdict(lambda: defaultdict(list))

    # 1. Modules
    print("  Escaneando Módulos...")
    for f in ATOMS_DIR.glob("modules/*.yml"):
        if f.name == "_index.yml":
            continue
        data = load_yaml(f)
        domain = data.get("domain")
        urn = data.get("_meta", {}).get("urn")
        if domain and urn:
            domain_map[domain]["modules"].append(urn)

    # 2. Processes
    print("  Escaneando Procesos...")
    for f in ATOMS_DIR.glob("processes/*.yml"):
        if f.name == "_index.yml":
            continue
        data = load_yaml(f)
        domain = data.get("domain")
        urn = data.get("_meta", {}).get("urn")
        if domain and urn:
            domain_map[domain]["processes"].append(urn)

    # 3. Entities
    print("  Escaneando Entidades...")
    for f in ATOMS_DIR.glob("entities/*.yml"):
        if f.name == "_index.yml":
            continue
        data = load_yaml(f)
        domain = data.get("domain")
        urn = data.get("_meta", {}).get("urn")
        if domain and urn:
            domain_map[domain]["entities"].append(urn)

    # 4. Capabilities
    print("  Escaneando Capabilities...")
    for f in ATOMS_DIR.glob("capabilities/*.yml"):
        if f.name == "_index.yml":
            continue
        data = load_yaml(f)
        domain = data.get("domain")
        urn = data.get("_meta", {}).get("urn")
        if domain and urn:
            domain_map[domain]["capabilities"].append(urn)

    return domain_map


def generate_compositions(domain_map: Dict[str, Dict]):
    """Genera archivos de composición por dominio."""
    print(f"  Generando composiciones para {len(domain_map)} dominios...")

    for domain_id, components in domain_map.items():
        # Metadata del dominio
        domain_urn = (
            f"urn:goreos:composition:domain:{domain_id.lower().replace('-', '_')}:1.0.0"
        )

        composition = {
            "_meta": {
                "urn": domain_urn,
                "type": "DomainComposition",
                "generated_at": "2025-12-21",
            },
            "id": domain_id,
            "name": f"Dominio {domain_id}",  # Idealmente mapear a nombre real si existe
            "aggregation": {
                "modules": sorted(components["modules"]),
                "processes": sorted(components["processes"]),
                "entities": sorted(components["entities"]),
                "capabilities": sorted(components["capabilities"]),
            },
            "stats": {
                "modules_count": len(components["modules"]),
                "processes_count": len(components["processes"]),
                "entities_count": len(components["entities"]),
                "capabilities_count": len(components["capabilities"]),
            },
        }

        filename = f"{domain_id.lower().replace('-', '_')}.yml"
        save_yaml(composition, COMPOSITIONS_DIR / filename)


def main():
    print("=" * 60)
    print("GORE_OS Domain Composition - Fase 4")
    print("=" * 60)

    domain_map = scan_atoms()
    generate_compositions(domain_map)

    print("=" * 60)
    print(f"✓ Fase 4 Completa: {len(domain_map)} composiciones generadas.")


if __name__ == "__main__":
    main()
