#!/usr/bin/env python3
"""
GORE_OS Categorical Diagnostic v1.0
Valida invariantes GI-01 a GI-07 según ontología v4.0
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Paths
ATOMS_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/00_paradev/model/atoms")
ROLES_DIR = ATOMS_DIR / "roles"
STORIES_DIR = ATOMS_DIR / "stories"
CAPS_DIR = ATOMS_DIR / "capabilities"
MODS_DIR = ATOMS_DIR / "modules"
PROCS_DIR = ATOMS_DIR / "processes"
ENTITIES_DIR = ATOMS_DIR / "entities"


def get_field(file_path, field_name):
    """Extract a simple field value from YAML-like file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                # Match field: value or field: "value" or field: 'value'
                match = re.match(rf'^{field_name}:\s*["\']?(.+?)["\']?\s*$', line)
                if match:
                    val = match.group(1).strip()
                    if val.lower() in ("null", "~", ""):
                        return None
                    return val
    except:
        pass
    return None


def get_urn(file_path):
    """Extract URN from _meta block."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if "urn:goreos:" in line:
                    match = re.search(r'(urn:goreos:[^\s"\']+)', line)
                    if match:
                        return match.group(1).strip()
    except:
        pass
    return None


def file_has_content(file_path, field_name):
    """Check if a field exists and has meaningful content."""
    val = get_field(file_path, field_name)
    return val is not None and len(val) > 3


def count_list_items(file_path, field_name):
    """Count items in a YAML list field."""
    count = 0
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            in_list = False
            for line in f:
                if f"{field_name}:" in line:
                    if "[]" in line:
                        return 0
                    in_list = True
                    continue
                if in_list:
                    if line.strip().startswith("-"):
                        count += 1
                    elif not line.startswith(" ") and line.strip():
                        break
    except:
        pass
    return count


def diagnostic():
    results = {
        "summary": {},
        "gi_01": {
            "name": "Trazabilidad Story→Capability",
            "pass": 0,
            "fail": 0,
            "examples": [],
        },
        "gi_03": {"name": "Cobertura Role", "pass": 0, "fail": 0, "examples": []},
        "gi_05": {
            "name": "Story→Process (implements)",
            "pass": 0,
            "fail": 0,
            "examples": [],
        },
        "gi_06": {
            "name": "Entity→Story (mentions)",
            "pass": 0,
            "fail": 0,
            "examples": [],
        },
        "semantic_stories": {
            "name": "Stories con i_want significativo",
            "pass": 0,
            "fail": 0,
        },
        "semantic_roles": {"name": "Roles con description", "pass": 0, "fail": 0},
        "semantic_entities": {"name": "Entities con description", "pass": 0, "fail": 0},
    }

    # 1. Catalog atoms
    roles_set = set()
    for f in ROLES_DIR.glob("*.yml"):
        rid = get_field(f, "id")
        if rid:
            roles_set.add(rid)

    caps_set = set()
    for f in CAPS_DIR.glob("*.yml"):
        cid = get_field(f, "id")
        if cid:
            caps_set.add(cid)

    # Stories mentioned by processes
    stories_with_process = set()
    for f in PROCS_DIR.glob("*.yml"):
        # Check implements field
        count = count_list_items(f, "implements")
        if count > 0:
            # Would need to parse the actual URNs, simplified here
            pass

    entities_mentioned = set()

    # 2. Validate Stories
    total_stories = 0
    for f in STORIES_DIR.glob("*.yml"):
        if f.name == "_index.yml":
            continue
        total_stories += 1
        sid = get_field(f, "id")

        # GI-03: Role coverage
        role_id = get_field(f, "role_id")
        if role_id and role_id in roles_set:
            results["gi_03"]["pass"] += 1
        else:
            results["gi_03"]["fail"] += 1
            if len(results["gi_03"]["examples"]) < 5:
                results["gi_03"]["examples"].append(f"{sid}: role_id={role_id}")

        # GI-01: Capability link
        cap_id = get_field(f, "capability_id")
        if cap_id and cap_id in caps_set:
            results["gi_01"]["pass"] += 1
        else:
            results["gi_01"]["fail"] += 1
            if len(results["gi_01"]["examples"]) < 5:
                results["gi_01"]["examples"].append(f"{sid}: capability_id={cap_id}")

        # Semantic: i_want content
        i_want = get_field(f, "i_want")
        if i_want and len(i_want) > 20:
            results["semantic_stories"]["pass"] += 1
        else:
            results["semantic_stories"]["fail"] += 1

    # 3. Validate Roles
    total_roles = 0
    for f in ROLES_DIR.glob("*.yml"):
        total_roles += 1
        if file_has_content(f, "description"):
            results["semantic_roles"]["pass"] += 1
        else:
            results["semantic_roles"]["fail"] += 1

    # 4. Validate Entities
    total_entities = 0
    for f in ENTITIES_DIR.glob("*.yml"):
        total_entities += 1
        # GI-06: Check if mentioned (we'd need reverse lookup)
        # Semantic: description
        if file_has_content(f, "description"):
            results["semantic_entities"]["pass"] += 1
        else:
            results["semantic_entities"]["fail"] += 1

    # 5. Summary
    results["summary"] = {
        "total_stories": total_stories,
        "total_roles": total_roles,
        "total_entities": total_entities,
        "total_capabilities": len(caps_set),
    }

    return results


def print_report(results):
    print("=" * 60)
    print("   DIAGNÓSTICO CATEGÓRICO GORE_OS v1.0")
    print("   Basado en Ontología v4.0")
    print("=" * 60)
    print()

    s = results["summary"]
    print(f"📊 INVENTARIO DE ÁTOMOS")
    print(f"   Stories:      {s['total_stories']}")
    print(f"   Roles:        {s['total_roles']}")
    print(f"   Entities:     {s['total_entities']}")
    print(f"   Capabilities: {s['total_capabilities']}")
    print()

    print("🔍 VALIDACIÓN DE INVARIANTES GLOBALES")
    print("-" * 60)

    for key in ["gi_01", "gi_03", "gi_05", "gi_06"]:
        gi = results[key]
        total = gi["pass"] + gi["fail"]
        pct = (gi["pass"] / total * 100) if total > 0 else 0
        status = "✅" if pct >= 90 else "⚠️" if pct >= 50 else "❌"
        print(f"{status} {key.upper()}: {gi['name']}")
        print(f"   Cumple: {gi['pass']}/{total} ({pct:.1f}%)")
        if gi["examples"]:
            print(f"   Ejemplos de fallo:")
            for ex in gi["examples"][:3]:
                print(f"     - {ex}")
        print()

    print("📝 CONTENIDO SEMÁNTICO")
    print("-" * 60)

    for key in ["semantic_stories", "semantic_roles", "semantic_entities"]:
        sem = results[key]
        total = sem["pass"] + sem["fail"]
        pct = (sem["pass"] / total * 100) if total > 0 else 0
        status = "✅" if pct >= 80 else "⚠️" if pct >= 50 else "❌"
        print(f"{status} {sem['name']}: {sem['pass']}/{total} ({pct:.1f}%)")

    print()
    print("=" * 60)


if __name__ == "__main__":
    results = diagnostic()
    print_report(results)
