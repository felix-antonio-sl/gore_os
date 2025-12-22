#!/usr/bin/env python3
"""
SSOT Domain Boundary Correction Script (No Dependencies Version)
Adds target_domain field to historias_usuarios_v2.yml using regex.

Domain Boundary Rules:
- D-FIN (Tactical): Strategic decisions (CDP approval, IPR prioritization)
- D-BACK (Operational): Transactional execution (payments, procurement, accounting)
"""

import re
from pathlib import Path

# Configuration
SSOT_PATH = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/historias_usuarios_v2.yml"
)
OUTPUT_PATH = SSOT_PATH.parent / "historias_usuarios_v3.yml"

# ID-based overrides: story_id -> target_domain
ID_OVERRIDES = {
    # Tesorería stories (operativo → D-BACK)
    "US-TES-001-01": "D-BACK",
    "US-TES-001-02": "D-BACK",
    "US-TES-002-01": "D-BACK",
    # Abastecimiento stories (operativo → D-BACK)
    "US-ABAST-001-01": "D-BACK",
    "US-ABAST-001-02": "D-BACK",
    # Comprador Público (operativo → D-BACK)
    "US-COMP-001-01": "D-BACK",
    # Finanzas operativas (contabilidad → D-BACK)
    "US-FIN-001-01": "D-BACK",
    # DAF closing
    "US-DAF-001-01": "D-BACK",
}

# Role-based reclassification: role_key -> (from_domain, to_domain)
ROLE_RULES = {
    "tesorero_regional": ("D-FIN", "D-BACK"),
    "encargado_abastecimiento": ("D-FIN", "D-BACK"),
    "comprador_publico": ("D-FIN", "D-BACK"),
    "jefe_finanzas": ("D-FIN", "D-BACK"),
    "contador_gubernamental": ("D-FIN", "D-BACK"),
}


def process_file():
    """Process the YAML file and add target_domain field."""
    print("=" * 60)
    print("SSOT Domain Boundary Correction Script")
    print("=" * 60)

    # Read file
    print(f"\n📂 Loading: {SSOT_PATH}")
    with open(SSOT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    new_lines = []

    stats = {
        "total_stories": 0,
        "reclassified": 0,
        "by_id": 0,
        "by_role": 0,
        "unchanged": 0,
    }

    current_story_id = None
    current_role_key = None
    current_domain = None
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect story ID
        id_match = re.match(r"^(\s*)- id: (US-\w+-\d+-\d+|CAP-\w+-\w+-\d+)", line)
        if id_match:
            current_story_id = id_match.group(2)
            current_role_key = None
            current_domain = None
            stats["total_stories"] += 1

        # Detect role_key
        role_match = re.match(r"^(\s+)role_key: (\w+)", line)
        if role_match:
            current_role_key = role_match.group(2)

        # Detect domain and inject target_domain after it
        domain_match = re.match(r"^(\s+)domain: (D-\w+)", line)
        if domain_match:
            indent = domain_match.group(1)
            current_domain = domain_match.group(2)

            # Determine target_domain
            target = current_domain  # default

            # Check ID override first
            if current_story_id and current_story_id in ID_OVERRIDES:
                target = ID_OVERRIDES[current_story_id]
                if target != current_domain:
                    stats["by_id"] += 1
                    stats["reclassified"] += 1
            # Then check role-based
            elif current_role_key and current_role_key in ROLE_RULES:
                from_domain, to_domain = ROLE_RULES[current_role_key]
                if current_domain == from_domain:
                    target = to_domain
                    stats["by_role"] += 1
                    stats["reclassified"] += 1
            else:
                stats["unchanged"] += 1

            # Add original line
            new_lines.append(line)

            # Check if next line is already target_domain (avoid duplicate)
            if i + 1 < len(lines) and "target_domain:" in lines[i + 1]:
                i += 1  # Skip existing target_domain line

            # Add target_domain line
            new_lines.append(f"{indent}target_domain: {target}")
            i += 1
            continue

        new_lines.append(line)
        i += 1

    # Add manifest note at top
    manifest_addition = """# DOMAIN BOUNDARY CORRECTION APPLIED: 2025-12-20
# Added target_domain field to each story for architectural alignment
# Rules: Operational functions (Tesorería, Compras) moved from D-FIN to D-BACK
"""

    final_content = "\n".join(new_lines)

    # Write output
    print(f"\n💾 Saving to: {OUTPUT_PATH}")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(final_content)

    # Report
    print("\n" + "=" * 60)
    print("📊 CORRECTION REPORT")
    print("=" * 60)
    print(f"Total stories processed: {stats['total_stories']}")
    print(f"Reclassified: {stats['reclassified']}")
    print(f"  - By ID override: {stats['by_id']}")
    print(f"  - By role rule: {stats['by_role']}")
    print(f"Unchanged: {stats['unchanged']}")

    print(f"\n✅ Output written to: {OUTPUT_PATH}")
    print("Review the v3 file before replacing v2.")


if __name__ == "__main__":
    process_file()
