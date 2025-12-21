#!/usr/bin/env python3
"""
Semantic Deduplication of Legacy Stories
Applies D-01 to D-04 rules from consensus_user_stories.md to legacy stories.

Process:
1. Load all legacy stories from user-stories/kb_goreos_us_*.yml
2. Apply deduplication rules (same as refactor_stories.py)
3. Generate refactored output to user-stories-refactored/

Based on consensus achieved in previous multi-agent dialogue.
"""

import re
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

LEGACY_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/user-stories")
OUTPUT_FILE = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/user-stories-refactored/consolidated_legacy.yml"
)

# ============================================================================
# D-01: Capability Bundles (Consolidate by Function)
# ============================================================================
CAPABILITY_KEYWORDS = {
    "CAP-FIN-DASH": {
        "name": "Dashboard de Ejecución Presupuestaria",
        "keywords": [
            "dashboard",
            "ejecución presupuestaria",
            "kpi",
            "tablero",
            "monitoreo ejecución",
        ],
        "domain": "D-FIN",
    },
    "CAP-EJEC-SEG": {
        "name": "Seguimiento de Proyectos",
        "keywords": ["seguimiento", "cartera", "estado proyecto", "avance", "semáforo"],
        "domain": "D-EJEC",
    },
    "CAP-FIN-REND": {
        "name": "Módulo de Rendiciones",
        "keywords": ["rendición", "rendiciones", "rendir cuentas", "rendimiento"],
        "domain": "D-FIN",
    },
    "CAP-BACK-PERS": {
        "name": "Gestión de Personas",
        "keywords": [
            "ficha funcionario",
            "liquidación",
            "remuneración",
            "licencia médica",
        ],
        "domain": "D-BACK",
    },
    "CAP-BACK-COMP": {
        "name": "Compras y Abastecimiento",
        "keywords": ["pac", "plan anual de compras", "orden de compra", "licitación"],
        "domain": "D-BACK",
    },
    "CAP-BACK-INV": {
        "name": "Inventarios y Activo Fijo",
        "keywords": ["bodega", "activo fijo", "inventario", "alta", "baja"],
        "domain": "D-BACK",
    },
    "CAP-BACK-BIEN": {
        "name": "Bienestar Funcionario",
        "keywords": ["bienestar", "bonificación", "préstamo", "socio"],
        "domain": "D-BACK",
    },
    "CAP-BACK-TES": {
        "name": "Tesorería y Contabilidad",
        "keywords": ["tesorero", "saldo bancario", "conciliación", "pago", "sigfe"],
        "domain": "D-BACK",
    },
    "CAP-TDE-FIRMA": {
        "name": "Bandeja de Firma Electrónica",
        "keywords": ["bandeja firma", "firma electrónica", "firmar", "fea"],
        "domain": "D-TDE",
    },
}

# ============================================================================
# D-02: Territorial Archetypes
# ============================================================================
TERRITORIAL_PATTERNS = [
    (r"secpla_\w+", "secpla_municipal"),
    (r"alcalde_\w+", "alcalde_municipal"),
    (r"ito_\w+_municipal", "ito_municipal"),
]

# ============================================================================
# D-03: Sectoral Archetypes
# ============================================================================
SECTORAL_PATTERNS = [
    (r"seremi_\w+", "seremi_sectorial"),
    (r"director_\w+", "director_servicio_regional"),
]

# ============================================================================
# D-04: NFR Patterns
# ============================================================================
NFR_PATTERNS = {
    "NFR-SIGFE": ["sigfe", "contabilidad gubernamental"],
    "NFR-FEA": ["firma electrónica", "fea", "ley 21.180"],
    "NFR-GIS": ["georreferencia", "gis", "mapa"],
    "NFR-ALERT": ["alerta", "notificación"],
}

# Priority mapping
PRIORITY_MAP = {
    "Crítica": "P0",
    "critica": "P0",
    "Alta": "P1",
    "alta": "P1",
    "Media": "P2",
    "media": "P2",
    "Baja": "P3",
    "baja": "P3",
}


def text_similarity(a: str, b: str) -> float:
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def parse_legacy_stories(filepath: Path) -> list:
    """Parse stories from a legacy YAML file."""
    content = filepath.read_text(encoding="utf-8")
    stories = []

    # Split by story blocks
    blocks = re.split(r"\n  - id:", content)

    for i, block in enumerate(blocks):
        if i == 0:
            continue

        block = "  - id:" + block
        story = {"source_file": filepath.name}

        # Extract fields
        for match in re.finditer(r"(\w+):\s*(.+?)(?=\n\s+\w+:|$)", block, re.DOTALL):
            key, value = match.groups()
            value = value.strip().strip('"')

            if key == "as_a":
                # Handle list format
                list_match = re.search(r"-\s+(.+)", value)
                story["as_a"] = list_match.group(1).strip() if list_match else value
            elif key == "priority":
                story["priority"] = PRIORITY_MAP.get(value, "P2")
            elif key in ["id", "i_want", "so_that", "module", "title"]:
                story[key] = value

        # Extract acceptance criteria
        criteria_match = re.search(
            r"acceptance_criteria:\s*\n((?:\s*-\s*.+\n?)+)", block
        )
        if criteria_match:
            criteria = []
            for line in criteria_match.group(1).split("\n"):
                if line.strip().startswith("-"):
                    criteria.append(line.strip()[1:].strip())
            story["acceptance_criteria"] = criteria

        if "id" in story:
            stories.append(story)

    return stories


def extract_nfrs(story: dict) -> list:
    """Extract NFR references from story content."""
    text = (
        story.get("i_want", "") + " " + " ".join(story.get("acceptance_criteria", []))
    ).lower()

    nfrs = []
    for nfr_id, patterns in NFR_PATTERNS.items():
        for pattern in patterns:
            if pattern in text:
                nfrs.append(nfr_id)
                break
    return nfrs


def get_capability(story: dict) -> str | None:
    """Determine capability bundle for a story."""
    i_want = story.get("i_want", "").lower()
    title = story.get("title", "").lower()
    text = i_want + " " + title

    for cap_id, cap_data in CAPABILITY_KEYWORDS.items():
        for keyword in cap_data["keywords"]:
            if keyword in text:
                return cap_id
    return None


def normalize_role(role: str) -> str:
    """Apply D-02 and D-03 archetype rules."""
    role_lower = role.lower().replace(" ", "_")

    # D-02: Territorial
    for pattern, archetype in TERRITORIAL_PATTERNS:
        if re.match(pattern, role_lower):
            return archetype

    # D-03: Sectoral
    for pattern, archetype in SECTORAL_PATTERNS:
        if re.match(pattern, role_lower):
            return archetype

    return role_lower


def deduplicate_by_similarity(stories: list, threshold: float = 0.85) -> list:
    """Remove semantically duplicate stories."""
    seen = []
    unique = []
    duplicates = []

    for story in stories:
        i_want = story.get("i_want", "")
        is_dup = False

        for seen_text in seen:
            if text_similarity(i_want, seen_text) > threshold:
                is_dup = True
                duplicates.append(story["id"])
                break

        if not is_dup:
            seen.append(i_want)
            unique.append(story)

    return unique, duplicates


def process_all_legacy() -> dict:
    """Main processing pipeline."""
    all_stories = []

    # Load all legacy files
    for legacy_file in sorted(LEGACY_DIR.glob("kb_goreos_us_*.yml")):
        stories = parse_legacy_stories(legacy_file)
        all_stories.extend(stories)
        print(f"  📂 {legacy_file.name}: {len(stories)} stories")

    print(f"\n📊 Total legacy stories: {len(all_stories)}")

    # Group by capability bundle (D-01)
    capability_groups = defaultdict(list)
    atomic_stories = []

    for story in all_stories:
        cap = get_capability(story)
        if cap:
            capability_groups[cap].append(story)
        else:
            atomic_stories.append(story)

    print(f"\n🔹 Capability bundles identified: {len(capability_groups)}")
    for cap_id, stories in capability_groups.items():
        print(f"   {cap_id}: {len(stories)} stories")

    # Consolidate capability bundles
    consolidated_bundles = []
    for cap_id, stories in capability_groups.items():
        # Deduplicate within bundle
        unique_stories, dups = deduplicate_by_similarity(stories)

        # Get all beneficiaries
        beneficiaries = set()
        for s in stories:
            role = normalize_role(s.get("as_a", ""))
            beneficiaries.add(role)

        bundle = {
            "id": f"{cap_id}-001",
            "capability": CAPABILITY_KEYWORDS[cap_id]["name"],
            "domain": CAPABILITY_KEYWORDS[cap_id]["domain"],
            "beneficiaries": sorted(list(beneficiaries)),
            "original_count": len(stories),
            "deduplicated_count": len(unique_stories),
            "representative_stories": [
                {
                    "id": s["id"],
                    "i_want": s.get("i_want", ""),
                    "priority": s.get("priority", "P2"),
                }
                for s in unique_stories[:5]  # Keep top 5 as representatives
            ],
        }
        consolidated_bundles.append(bundle)

    # Process atomic stories
    print(f"\n🔹 Atomic stories: {len(atomic_stories)}")

    # Apply NFR extraction (D-04)
    for story in atomic_stories:
        story["nfr_refs"] = extract_nfrs(story)
        story["role_key"] = normalize_role(story.get("as_a", ""))

    # Deduplicate atomic stories
    unique_atomic, atomic_dups = deduplicate_by_similarity(atomic_stories)
    print(f"   After deduplication: {len(unique_atomic)} unique")

    # Build output
    output = {
        "_manifest": {
            "title": "Legacy Stories - Consolidated",
            "original_count": len(all_stories),
            "bundle_count": len(consolidated_bundles),
            "atomic_count": len(unique_atomic),
            "total_consolidated": len(consolidated_bundles) + len(unique_atomic),
            "reduction_pct": round(
                (
                    1
                    - (len(consolidated_bundles) + len(unique_atomic))
                    / len(all_stories)
                )
                * 100,
                1,
            ),
            "rules_applied": ["D-01", "D-02", "D-03", "D-04"],
        },
        "capability_bundles": consolidated_bundles,
        "atomic_stories": [
            {
                "id": s["id"],
                "as_a": s.get("as_a", ""),
                "i_want": s.get("i_want", ""),
                "so_that": s.get("so_that", ""),
                "priority": s.get("priority", "P2"),
                "role_key": s.get("role_key", ""),
                "nfr_refs": s.get("nfr_refs", []),
                "origin": "legacy",
            }
            for s in unique_atomic
        ],
    }

    return output


def format_yaml(data: dict) -> str:
    """Format data as YAML string without external dependencies."""
    lines = []

    def format_value(value, indent=0):
        prefix = "  " * indent
        if isinstance(value, dict):
            result = []
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    result.append(f"{prefix}{k}:")
                    result.append(format_value(v, indent + 1))
                else:
                    result.append(f"{prefix}{k}: {v}")
            return "\n".join(result)
        elif isinstance(value, list):
            result = []
            for item in value:
                if isinstance(item, dict):
                    first = True
                    for k, v in item.items():
                        if first:
                            result.append(f"{prefix}- {k}: {v}")
                            first = False
                        else:
                            result.append(f"{prefix}  {k}: {v}")
                else:
                    result.append(f"{prefix}- {item}")
            return "\n".join(result)
        else:
            return f"{prefix}{value}"

    return format_value(data)


def main():
    print("=" * 70)
    print("SEMANTIC DEDUPLICATION OF LEGACY STORIES")
    print("Applying D-01 to D-04 rules from consensus_user_stories.md")
    print("=" * 70)

    print("\n📂 Loading legacy stories...")
    result = process_all_legacy()

    manifest = result["_manifest"]
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Original stories: {manifest['original_count']}")
    print(f"Capability bundles: {manifest['bundle_count']}")
    print(f"Atomic stories: {manifest['atomic_count']}")
    print(f"Total consolidated: {manifest['total_consolidated']}")
    print(f"Reduction: {manifest['reduction_pct']}%")

    # Save output
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    output_text = format_yaml(result)
    OUTPUT_FILE.write_text(output_text, encoding="utf-8")
    print(f"\n✅ Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
