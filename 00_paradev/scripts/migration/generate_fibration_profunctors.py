#!/usr/bin/env python3
"""
Generate Fibration Profunctors

Crea assumes.yml (L1 → L2) y specializes.yml (L2 → L3)
"""

import re
from pathlib import Path
from collections import defaultdict


class Config:
    GORE_OS_ROOT = Path("/Users/felixsanhueza/fx_felixiando/gore_os")
    ROLES_DIR = GORE_OS_ROOT / "model" / "atoms" / "roles"
    PROFUNCTORS_DIR = GORE_OS_ROOT / "model" / "profunctors"


def extract_meta_urn(content: str) -> str:
    m = re.search(r'_meta:\s*\n\s+urn:\s*"?([^"\n]+)"?', content)
    return m.group(1).strip() if m else ""


def extract_field(content: str, field: str) -> str:
    m = re.search(rf"^{field}:\s*(.+)$", content, re.MULTILINE)
    return m.group(1).strip().strip("\"'") if m else ""


def load_roles_by_level():
    """Carga todos los roles agrupados por nivel"""
    roles_by_level = {"L1": [], "L2": [], "L3": []}

    for f in Config.ROLES_DIR.glob("*.yml"):
        if f.name.startswith("_") or f.name.startswith("."):
            continue
        try:
            content = f.read_text()
            urn = extract_meta_urn(content)
            if not urn:
                continue

            # Buscar level
            level_match = re.search(r"categorical:\s*\n\s+level:\s*(\w+)", content)
            if not level_match:
                continue
            level = level_match.group(1)

            role_data = {
                "urn": urn,
                "file": f.name,
                "title": extract_field(content, "title"),
                "domain": extract_field(content, "domain"),
                "unit_type": extract_field(content, "unit_type"),
            }

            roles_by_level[level].append(role_data)
        except:
            pass

    return roles_by_level


def generate_assumes(roles_by_level):
    """
    Genera profunctor assumes: L1 → L2

    Heurística: L1 asume L2 si:
    1. Comparten el mismo dominio
    2. El nombre de L2 contiene keywords relacionados al nombre de L1
    """
    relations = []

    for l1_role in roles_by_level["L1"]:
        l1_title_lower = l1_role["title"].lower()
        l1_domain = l1_role["domain"]

        # Extraer keywords del L1
        l1_keywords = set()
        # "Jefe División de Planificación" → ["jefe", "división", "planificación"]
        words = re.findall(r"\w+", l1_title_lower)
        l1_keywords = {w for w in words if len(w) > 4}  # Palabras significativas

        for l2_role in roles_by_level["L2"]:
            # Mismo dominio
            if l2_role["domain"] != l1_domain:
                continue

            l2_title_lower = l2_role["title"].lower()

            # Buscar overlap de keywords
            l2_words = set(re.findall(r"\w+", l2_title_lower))
            overlap = l1_keywords & l2_words

            # Si hay 2+ palabras en común, es un match probable
            if len(overlap) >= 2:
                relations.append(
                    {
                        "source": l1_role["urn"],
                        "target": l2_role["urn"],
                        "reason": f"Domain match + keywords: {', '.join(overlap)}",
                    }
                )
            # Casos específicos
            elif "jefe" in l1_title_lower and "analista" in l2_title_lower:
                # Jefe puede asumir cualquier Analista de su dominio
                relations.append(
                    {
                        "source": l1_role["urn"],
                        "target": l2_role["urn"],
                        "reason": "Hierarchical: Jefe → Analista",
                    }
                )

    return relations


def generate_specializes(roles_by_level):
    """
    Genera profunctor specializes: L2 → L3

    Heurística: L2 se especializa en L3 si el título de L3 contiene el de L2
    """
    relations = []

    for l2_role in roles_by_level["L2"]:
        l2_title_lower = l2_role["title"].lower()
        l2_keywords = set(re.findall(r"\w+", l2_title_lower)) - {
            "de",
            "del",
            "la",
            "el",
        }

        for l3_role in roles_by_level["L3"]:
            l3_title_lower = l3_role["title"].lower()

            # ¿L3 contiene keywords de L2?
            matches = [k for k in l2_keywords if k in l3_title_lower]

            if len(matches) >= 1:
                relations.append(
                    {
                        "source": l2_role["urn"],
                        "target": l3_role["urn"],
                        "reason": f"Specialization: {', '.join(matches)}",
                    }
                )

    return relations


def write_profunctor(name: str, source_type: str, target_type: str, relations: list):
    """Escribe un profunctor de fibración"""
    lines = [
        "_meta:",
        f'  urn: "urn:goreos:profunctor:{name}:1.0.0"',
        "  type: Profunctor",
        '  ontology_version: "3.0.0"',
        "",
        "signature:",
        f"  source_type: Role",
        f"  target_type: Role",
        f'  semantics: "{source_type} → {target_type}"',
        "",
        "relations:",
    ]

    if not relations:
        lines.append("  []")
    else:
        for rel in relations:
            lines.append(f'  - source: "{rel["source"]}"')
            lines.append(f'    target: "{rel["target"]}"')
            lines.append(f"    metadata:")
            lines.append(f'      reason: "{rel["reason"]}"')

    (Config.PROFUNCTORS_DIR / f"{name}.yml").write_text("\n".join(lines))
    print(f"  ✅ Written {name}.yml with {len(relations)} relations")


def main():
    print("=" * 60)
    print("Fibration Profunctors Generator")
    print("=" * 60)

    # 1. Load roles
    print("\n[1/3] Loading roles by level...")
    roles_by_level = load_roles_by_level()
    for level, roles in roles_by_level.items():
        print(f"  {level}: {len(roles)} roles")

    # 2. Generate assumes (L1 → L2)
    print("\n[2/3] Generating assumes.yml (L1 → L2)...")
    assumes_rels = generate_assumes(roles_by_level)
    write_profunctor("assumes", "L1 (Structural)", "L2 (Competencial)", assumes_rels)

    # 3. Generate specializes (L2 → L3)
    print("\n[3/3] Generating specializes.yml (L2 → L3)...")
    spec_rels = generate_specializes(roles_by_level)
    write_profunctor("specializes", "L2 (Competencial)", "L3 (Contextual)", spec_rels)

    print("\n" + "=" * 60)
    print(f"Total categorical relations: {len(assumes_rels) + len(spec_rels)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
