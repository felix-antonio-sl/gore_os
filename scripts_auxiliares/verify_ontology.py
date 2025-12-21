#!/usr/bin/env python3
"""
GORE_OS Ontology Verification Script
Verifica los invariantes y la integridad referencial del KB atómico.

Invariantes verificados:
- I1: Atomicidad y Parseabilidad
- I2: Identidad (Unique URN)
- I13: Integridad Referencial (Compositions)
- I14: Integridad Profunctorial

Ontología: v2.0.0
Fase: 5
"""

import yaml
from pathlib import Path
from collections import defaultdict
from typing import Set, Dict, List

# Rutas base
BLUEPRINT_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint")
ATOMS_DIR = BLUEPRINT_DIR / "atoms"
COMPOSITIONS_DIR = BLUEPRINT_DIR / "compositions/domains"
PROFUNCTORS_DIR = BLUEPRINT_DIR / "profunctors"

# Colores output
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"


def load_yaml(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"{RED}Error parsing {path}: {e}{RESET}")
        return None


def verify_atoms() -> Set[str]:
    """Verifica I1 y I2. Retorna conjunto de URNs válidas."""
    print("Verificando Átomos (I1, I2)...")
    valid_urns = set()
    urn_file_map = {}

    atom_files = list(ATOMS_DIR.rglob("*.yml"))
    stats = defaultdict(int)

    for f in atom_files:
        if f.name == "_index.yml":
            # Load index to get virtual atoms (like Stories if not individual files)
            try:
                index_data = load_yaml(f)
                if index_data and "items" in index_data:
                    for item in index_data["items"]:
                        i_urn = item.get("urn")
                        if i_urn and i_urn not in valid_urns:
                            valid_urns.add(i_urn)
                            urn_file_map[i_urn] = f.name
                            stats[
                                f"IndexItem ({index_data.get('_meta', {}).get('type')})"
                            ] += 1
            except Exception as e:
                print(f"{RED}Error reading index {f}: {e}{RESET}")
            continue

        data = load_yaml(f)
        if not data:
            continue

        # Check Meta
        meta = data.get("_meta", {})
        urn = meta.get("urn")

        if not urn:
            print(f"{RED}  [Violation I1] Missing URN in {f.name}{RESET}")
            continue

        # Check Duplicate URN (I2)
        if urn in valid_urns:
            print(
                f"{RED}  [Violation I2] Duplicate URN {urn} in {f.name} (First seen in {urn_file_map[urn]}){RESET}"
            )
            continue

        valid_urns.add(urn)
        urn_file_map[urn] = f.name
        atom_type = meta.get("type", "Unknown")
        stats[atom_type] += 1

    for k, v in stats.items():
        print(f"  ✓ {k}: {v}")

    return valid_urns


def verify_compositions(valid_urns: Set[str]):
    """Verifica I13 (Integridad Referencial en Composiciones)."""
    print("\nVerificando Composiciones (I13)...")

    comp_files = list(COMPOSITIONS_DIR.glob("*.yml"))
    errors = 0

    for f in comp_files:
        data = load_yaml(f)
        if not data:
            continue

        domain_id = data.get("id")
        agg = data.get("aggregation", {})

        for category, urn_list in agg.items():
            for urn in urn_list:
                if urn not in valid_urns:
                    # Ignore module capability references for now if generic
                    print(
                        f"{YELLOW}  [Warning I13] Domain {domain_id} references missing {category}: {urn}{RESET}"
                    )
                    errors += 1

    if errors == 0:
        print(f"{GREEN}  ✓ Todas las composiciones referencian átomos válidos.{RESET}")
    else:
        print(f"{YELLOW}  ⚠ Se detectaron {errors} referencias rotas.{RESET}")


def verify_profunctors(valid_urns: Set[str]):
    """Verifica I14 (Integridad Profunctorial)."""
    print("\nVerificando Profunctores (I14)...")

    prof_files = list(PROFUNCTORS_DIR.glob("*.yml"))

    for f in prof_files:
        data = load_yaml(f)
        if not data:
            continue

        relations = data.get("relations", [])
        print(f"  Checking {f.name} ({len(relations)} relations)...")

        broken = 0
        for rel in relations:
            # Check known keys for URNs
            for key in ["role", "story", "capability"]:
                if key in rel:
                    urn = rel[key]
                    if urn not in valid_urns:
                        # Sometimes URNs might be slightly different in profunctors vs atoms?
                        # Need to be strict.
                        broken += 1
                        if broken <= 5:
                            print(f"{RED}    Broken Link: {urn}{RESET}")

        if broken == 0:
            print(f"{GREEN}    ✓ Integrity OK{RESET}")
        else:
            print(f"{RED}    FAILED: {broken} broken links{RESET}")


def main():
    print("=" * 60)
    print("GORE_OS Validacion Ontológica - Fase 5")
    print("=" * 60)

    valid_urns = verify_atoms()
    verify_compositions(valid_urns)
    verify_profunctors(valid_urns)

    print("=" * 60)


if __name__ == "__main__":
    main()
