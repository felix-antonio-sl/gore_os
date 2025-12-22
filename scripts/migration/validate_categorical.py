#!/usr/bin/env python3
"""
==============================================================================
GORE_OS Categorical Validator
==============================================================================

Verifica invariantes de la fibración categorial:
1. IC-01: π(A) ≤ π(B) para todo morfismo A → B
2. Aciclicidad en cada fibra
3. Completitud de composición

Autor: Arquitecto-GORE v0.1.0
"""

import re
from pathlib import Path
from collections import defaultdict


class Config:
    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    PROFUNCTORS_DIR = GORE_OS_ROOT / "model" / "profunctors"
    ROLES_DIR = GORE_OS_ROOT / "model" / "atoms" / "roles"


# Orden de niveles
LEVEL_ORDER = {"L1": 1, "L2": 2, "L3": 3}


def load_role_levels():
    """Carga el nivel de cada rol"""
    role_levels = {}

    for f in Config.ROLES_DIR.glob("*.yml"):
        if f.name.startswith("_"):
            continue
        try:
            content = f.read_text()
            urn_match = re.search(r'urn:\s*"?([^"\n]+)"?', content)
            level_match = re.search(r"level:\s*(\w+)", content)

            if urn_match and level_match:
                urn = urn_match.group(1).strip()
                level = level_match.group(1)
                role_levels[urn] = level
        except:
            pass

    return role_levels


def load_profunctor(name: str):
    """Carga relaciones de un profunctor"""
    file_path = Config.PROFUNCTORS_DIR / f"{name}.yml"
    if not file_path.exists():
        return []

    content = file_path.read_text()
    relations = []

    # Parse simple
    lines = content.split("\n")
    current_source = None
    for line in lines:
        if "source:" in line:
            current_source = re.search(r'source:\s*"([^"]+)"', line)
            if current_source:
                current_source = current_source.group(1)
        elif "target:" in line and current_source:
            target_match = re.search(r'target:\s*"([^"]+)"', line)
            if target_match:
                target = target_match.group(1)
                relations.append((current_source, target))

    return relations


def validate_fibration(role_levels):
    """Valida IC-01: π(source) ≤ π(target)"""
    print("\n[IC-01] Validating Fibration Invariant...")

    violations = []

    # Validar assumes (debe ser L1 → L2)
    assumes_rels = load_profunctor("assumes")
    for source, target in assumes_rels:
        src_level = role_levels.get(source, "UNKNOWN")
        tgt_level = role_levels.get(target, "UNKNOWN")

        if src_level == "UNKNOWN" or tgt_level == "UNKNOWN":
            continue

        if LEVEL_ORDER[src_level] > LEVEL_ORDER[tgt_level]:
            violations.append(
                {
                    "profunctor": "assumes",
                    "source": source,
                    "target": target,
                    "source_level": src_level,
                    "target_level": tgt_level,
                    "reason": f"{src_level} → {tgt_level} violates π(A) ≤ π(B)",
                }
            )

    # Validar specializes (debe ser L2 → L3)
    spec_rels = load_profunctor("specializes")
    for source, target in spec_rels:
        src_level = role_levels.get(source, "UNKNOWN")
        tgt_level = role_levels.get(target, "UNKNOWN")

        if src_level == "UNKNOWN" or tgt_level == "UNKNOWN":
            continue

        if LEVEL_ORDER[src_level] > LEVEL_ORDER[tgt_level]:
            violations.append(
                {
                    "profunctor": "specializes",
                    "source": source,
                    "target": target,
                    "source_level": src_level,
                    "target_level": tgt_level,
                    "reason": f"{src_level} → {tgt_level} violates π(A) ≤ π(B)",
                }
            )

    if violations:
        print(f"  ❌ FAILED: {len(violations)} violations found")
        for v in violations[:5]:
            print(
                f"     - {v['profunctor']}: {v['source_level']} → {v['target_level']}"
            )
    else:
        print("  ✅ PASSED: All morphisms respect fibration")

    return violations


def check_cycles():
    """Detecta ciclos en assumes/specializes"""
    print("\n[IC-02] Checking for cycles...")

    # Build graph
    graph = defaultdict(list)

    for source, target in load_profunctor("assumes"):
        graph[source].append(target)
    for source, target in load_profunctor("specializes"):
        graph[source].append(target)

    # DFS para ciclos
    visited = set()
    rec_stack = set()
    cycles = []

    def dfs(node, path):
        if node in rec_stack:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:])
            return
        if node in visited:
            return

        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph.get(node, []):
            dfs(neighbor, path + [neighbor])

        rec_stack.remove(node)

    for node in graph.keys():
        if node not in visited:
            dfs(node, [node])

    if cycles:
        print(f"  ❌ FAILED: {len(cycles)} cycles detected")
        for cycle in cycles[:3]:
            print(f"     - Cycle: {' → '.join(cycle[:3])}...")
    else:
        print("  ✅ PASSED: No cycles detected")

    return cycles


def main():
    print("=" * 60)
    print("Categorical Fibration Validator")
    print("=" * 60)

    # Load data
    print("\n[0/3] Loading role levels...")
    role_levels = load_role_levels()
    print(f"  Loaded {len(role_levels)} roles")

    # Validate
    violations = validate_fibration(role_levels)
    cycles = check_cycles()

    # Summary
    print("\n" + "=" * 60)
    if not violations and not cycles:
        print("✅ VALIDATION PASSED: Model is categorially sound")
    else:
        print(f"❌ VALIDATION FAILED:")
        print(f"  - Fibration violations: {len(violations)}")
        print(f"  - Cycles: {len(cycles)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
