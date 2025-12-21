#!/usr/bin/env python3
"""
Deep Refactoring Functor
Transforms a raw set of stories (v2 + legacy) into a coherent Categorical SSOT.
Applies normalization, bundle fusion, and semantic absorption.
"""

import re
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
from datetime import datetime

# ==============================================================================
# 0. CONFIGURATION & TYPES
# ==============================================================================

V3_RAW_FILE = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/historias_usuarios_v3.yml"
)
OUTPUT_FILE = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/historias_usuarios_final.yml"
)

# Domain Inference Rules
DOMAIN_PREFIX_MAP = {
    "US-BACK": "D-BACK",
    "US-FIN": "D-FIN",
    "US-TDE": "D-TDE",
    "US-GOB": "D-GOB",
    "US-EJEC": "D-EJEC",
    "US-NORM": "D-NORM",
    "US-SEG": "D-SEG",
    "US-EVOL": "D-EVOL",
    "US-TERR": "D-TERR",
    "US-GEST": "D-GESTION",
    "US-DEV": "D-DEV",
    "US-OPS": "D-OPS",
    "US-COM": "D-COM",
    "US-FNX": "D-FENIX",
    "US-AR": "D-GOB",
    "US-DIPIR": "D-EJEC",
}

# Capability Merging Map (Redundant -> Canonical)
CAPABILITY_MERGE_MAP = {
    "CAP-DASH-EJEC": "CAP-FIN-DASH",  # Merge legacy dashboard into v2 dashboard
    "CAP-PROYECTOS": "CAP-EJEC-SEG",  # Merge legacy project tracking into v2 exec
    "CAP-RENDICIONES": "CAP-FIN-REND",  # Merge legacy rendiciones into v2 rend
}

# Canonical Capabilities Definitions (for enrichment)
CANONICAL_CAPABILITIES = {
    "CAP-FIN-DASH": {
        "name": "Dashboard de Ejecución Presupuestaria",
        "domain": "D-FIN",
    },
    "CAP-FIN-REND": {"name": "Gestión de Rendiciones de Cuentas", "domain": "D-FIN"},
    "CAP-EJEC-SEG": {"name": "Seguimiento de Cartera de Proyectos", "domain": "D-EJEC"},
    "CAP-BACK-COMP": {"name": "Compras y Licitaciones", "domain": "D-BACK"},
    "CAP-BACK-TES": {"name": "Tesorería y Pagos", "domain": "D-BACK"},
    "CAP-BACK-PERS": {"name": "Gestión de Personas", "domain": "D-BACK"},
    "CAP-TDE-FIRMA": {"name": "Firma Electrónica Avanzada", "domain": "D-TDE"},
    "CAP-TDE-TRANS": {"name": "Transparencia Activa", "domain": "D-TDE"},
    "CAP-NORM-DOC": {"name": "Gestión Documental", "domain": "D-NORM"},
}

# ==============================================================================
# 1. PARSING & EXTRACTION (The Source Category)
# ==============================================================================


def load_stories_raw(filepath: Path) -> dict:
    """Reads YAML manually to withstand format inconsistencies."""
    content = filepath.read_text(encoding="utf-8")

    # Simple rigorous parser to avoid PyYAML issues with complex objects
    stories = []
    bundles = []
    current_object = {}
    section = None  # 'bundles' or 'atomic'

    lines = content.split("\n")
    for line in lines:
        stripped = line.strip()

        # Section detection
        if stripped.startswith("capability_bundles:"):
            section = "bundles"
            continue
        if stripped.startswith("atomic_stories:"):
            section = "atomic"
            continue
        if stripped.startswith("#"):
            continue

        # Object detection
        if stripped.startswith("- id:"):
            if current_object:
                if "capability" in current_object:
                    bundles.append(current_object)
                else:
                    stories.append(current_object)
            current_object = {}
            current_object["id"] = stripped.replace("- id:", "").strip()
            continue

        # Field extraction
        if ":" in stripped:
            key, val = stripped.split(":", 1)
            key = key.strip()
            val = val.split("#")[0].strip()
            if (len(val) >= 2 and val[0] == '"' and val[-1] == '"') or (
                len(val) >= 2 and val[0] == "'" and val[-1] == "'"
            ):
                val = val[1:-1]

            # Simple list handling (beneficiaries, criteria)
            if not val and key in [
                "beneficiaries",
                "acceptance_criteria",
                "consolidated_from",
            ]:
                current_object[key] = []
                continue

            if key.startswith("-") and not ":" in stripped:  # List item
                item = stripped.replace("-", "").strip()
                # Try to find last list key
                for k in ["beneficiaries", "acceptance_criteria", "consolidated_from"]:
                    if k in current_object and isinstance(current_object[k], list):
                        current_object[k].append(item)
                        break
            elif key and val:
                current_object[key] = val

    # Add last object
    if current_object:
        if "capability" in current_object:
            bundles.append(current_object)
        else:
            stories.append(current_object)

    return {"bundles": bundles, "stories": stories}


# ==============================================================================
# 2. TRANSFORMATION (The Functor)
# ==============================================================================


def normalize_story(story: dict) -> dict:
    """Normalizes a story object to CanonicalStory type."""
    if "id" not in story:
        return story  # Should be caught by parser but safe guard

    # 1. Domain Inference
    if "domain" not in story:
        prefix = story["id"].split("-")[:2]  # US-BACK -> US, BACK
        prefix_key = "-".join(prefix)
        # Try full prefix match specific ID prefixes like US-FNX
        for k, v in DOMAIN_PREFIX_MAP.items():
            if story["id"].startswith(k):
                story["domain"] = v
                break
        if "domain" not in story:
            story["domain"] = "D-UNK"

    # 2. Role Normalization
    role_val = story.get("role") or story.get("as_a") or ""
    story["role_key"] = str(role_val).lower().replace(" ", "_")

    # 3. Priority Normalization
    prio = story.get("priority", "P2")
    if prio not in ["P0", "P1", "P2", "P3"]:
        story["priority"] = "P2"

    return story


def merge_bundles(bundles: list) -> list:
    """Merges overlapping capability bundles."""
    merged_map = {}  # canonical_id -> bundle

    for b in bundles:
        cap_id = b["id"].split("-001")[0]

        # Check if this bundle should be merged into another
        target_cap = CAPABILITY_MERGE_MAP.get(cap_id, cap_id)
        canonical_id = f"{target_cap}-001"

        if canonical_id not in merged_map:
            # Initialize with canonical data if available
            base_data = CANONICAL_CAPABILITIES.get(
                target_cap, {"name": b.get("capability"), "domain": b.get("domain")}
            )
            merged_map[canonical_id] = {
                "id": canonical_id,
                "capability": base_data["name"],
                "domain": base_data["domain"],
                "beneficiaries": set(),
                "story_count": 0,
                "origin_ids": set(),
            }

        # Merge data
        target = merged_map[canonical_id]
        if "beneficiaries" in b:
            # Sanitize input: ensure list
            b_bens = b["beneficiaries"]
            if isinstance(b_bens, str):
                # Handle inline list "[a, b]" or single string
                cleaned = b_bens.strip("[]")
                b_bens = (
                    [x.strip().strip("'").strip('"') for x in cleaned.split(",")]
                    if cleaned
                    else []
                )

            for ben in b_bens:
                if ben:
                    target["beneficiaries"].add(ben)

        count = int(b.get("original_count", 0))
        target["story_count"] += count
        target["origin_ids"].add(b["id"])

    # Convert sets to lists
    result = []
    for k, v in merged_map.items():
        v["beneficiaries"] = sorted(list(v["beneficiaries"]))
        v["origin_ids"] = sorted(list(v["origin_ids"]))
        result.append(v)

    return result


def absorb_atomic_stories(stories: list, bundles: list) -> tuple:
    """
    Moves atomic stories that belong to a bundle INTO that bundle.
    Returns (remaining_atomic, updated_bundles)
    """
    remaining = []
    bundle_keywords = {}

    # Precompute keywords for each bundle
    for b in bundles:
        name = b["capability"].lower()
        keywords = set(name.split()) - {"de", "y", "la", "el", "gestión", "sistema"}
        bundle_keywords[b["id"]] = keywords

    for s in stories:
        absorbed = False
        text = (s.get("i_want", "") + " " + s.get("so_that", "")).lower()

        # Try to match to bundle
        best_match = None
        max_hits = 0

        for bid, kws in bundle_keywords.items():
            hits = sum(1 for kw in kws if kw in text)
            if hits > 0 and hits >= len(kws) * 0.6:  # 60% keyword match
                if hits > max_hits:
                    max_hits = hits
                    best_match = bid

        if best_match:
            # Absorb!
            target_bundle = next(b for b in bundles if b["id"] == best_match)
            target_bundle["story_count"] += 1
            if "beneficiaries" not in target_bundle:
                target_bundle["beneficiaries"] = []
            if "role_key" in s and s["role_key"] not in target_bundle["beneficiaries"]:
                target_bundle["beneficiaries"].append(s["role_key"])
            absorbed = True

        if not absorbed:
            remaining.append(s)

    return remaining, bundles


# ==============================================================================
# 3. GENERATION (The Sink Category)
# ==============================================================================


def write_ssot(bundles: list, atomic: list):
    """Writes the finalized YAML structure."""

    # Sort bundles by domain
    bundles.sort(key=lambda x: (x.get("domain", "Z"), x["id"]))

    # Sort atomic by domain then ID
    # Sort atomic by domain then ID (filtering invalid first)
    atomic = [s for s in atomic if "id" in s]
    atomic.sort(key=lambda x: (x.get("domain", "Z"), x["id"]))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # Header
        f.write("# GORE_OS User Stories SSOT v3.0 (Final)\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write("# Refactoring: Deep Compositional Functor\n\n")

        f.write("_manifest:\n")
        f.write("  urn: urn:goreos:specs:user-stories:3.0.0\n")
        f.write("  title: Catálogo Consolidado GORE_OS\n")
        f.write(f"  total_bundles: {len(bundles)}\n")
        f.write(f"  total_atomic: {len(atomic)}\n\n")

        # Bundles
        f.write("capability_bundles:\n")
        for b in bundles:
            f.write(f"  - id: {b['id']}\n")
            f.write(f"    capability: {b['capability']}\n")
            f.write(f"    domain: {b['domain']}\n")
            f.write(f"    stories_consolidated: {b['story_count']}\n")
            f.write("    beneficiaries:\n")
            for ben in b["beneficiaries"]:
                f.write(f"      - {ben}\n")
            f.write("\n")

        # Atomic
        f.write("atomic_stories:\n")
        current_domain = ""
        for s in atomic:
            # Section separators for readability
            if s.get("domain") != current_domain:
                current_domain = s.get("domain")
                f.write(f"\n  # --- {current_domain} ---\n")

            f.write(f"  - id: {s['id']}\n")
            f.write(f"    domain: {s.get('domain')}\n")
            f.write(f"    role: {s.get('role_key')}\n")
            f.write(f"    priority: {s.get('priority')}\n")
            # Escape quotes for safety
            i_want = s.get("i_want", "").replace('"', '\\"')
            so_that = s.get("so_that", "").replace('"', '\\"')

            f.write(f'    i_want: "{i_want}"\n')
            f.write(f'    so_that: "{so_that}"\n')
            if s.get("acceptance_criteria"):
                f.write("    acceptance_criteria:\n")
                for ac in s["acceptance_criteria"]:
                    ac_clean = ac.replace('"', '\\"')
                    f.write(f'      - "{ac_clean}"\n')


def main():
    print("🚀 Starting Deep Refactoring Functor...")

    # 1. LOAD
    data = load_stories_raw(V3_RAW_FILE)
    print(
        f"Loaded {len(data['bundles'])} bundles and {len(data['stories'])} atomic stories."
    )

    # 2. NORMALIZE
    normalized_stories = [normalize_story(s) for s in data["stories"]]

    # 3. MERGE BUNDLES
    merged_bundles = merge_bundles(data["bundles"])
    print(f"Merged into {len(merged_bundles)} canonical bundles.")

    # 4. ABSORB
    final_atomic, final_bundles = absorb_atomic_stories(
        normalized_stories, merged_bundles
    )

    absorbed_count = len(normalized_stories) - len(final_atomic)
    print(f"Absorbed {absorbed_count} atomic stories into bundles.")
    print(f"Remaining atomic stories: {len(final_atomic)}")

    # 5. EMIT
    write_ssot(final_bundles, final_atomic)
    print(f"✅ Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
