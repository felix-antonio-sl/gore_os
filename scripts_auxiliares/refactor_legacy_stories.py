#!/usr/bin/env python3
"""
Step 1: Refactor Legacy Stories to v2 Format
Transforms stories from user-stories/kb_goreos_us_*.yml to v2 YAML format.
"""

import re
from pathlib import Path
from collections import defaultdict

LEGACY_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/user-stories")
OUTPUT_DIR = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/user-stories-refactored"
)

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

# Module to domain mapping
MODULE_TO_DOMAIN = {
    "Personas": "D-BACK",
    "Abastecimiento": "D-BACK",
    "Inventarios": "D-BACK",
    "ActivoFijo": "D-BACK",
    "Flota": "D-BACK",
    "Servicios": "D-BACK",
    "Bienestar": "D-BACK",
    "ContabilidadOperativa": "D-BACK",
    "Competencias": "D-BACK",
    "Tesorería": "D-BACK",
}

# Role mapping (actor to role_key)
ACTOR_TO_ROLE = {
    "Funcionario": "funcionario",
    "Gestor de Personas": "gestor_personas",
    "Gestor Personas": "gestor_personas",
    "Junta Calificadora": "junta_calificadora",
    "Encargado Abastecimiento": "encargado_abastecimiento",
    "Encargado Bodega": "bodeguero",
    "Encargado Activo Fijo": "encargado_activo_fijo",
    "Encargado Flota": "encargado_flota",
    "Encargado Servicios Generales": "encargado_servicios",
    "Profesional Bienestar": "profesional_bienestar",
    "Socio Bienestar": "socio_bienestar",
    "Encargado Capacitación": "encargado_capacitacion",
    "Tesorero": "tesorero_regional",
    "Contador": "contador_gubernamental",
    "Jefe DAF": "jefe_daf",
}


def parse_legacy_file(filepath: Path) -> list:
    """Parse a legacy YAML file and extract stories."""
    content = filepath.read_text(encoding="utf-8")
    stories = []

    # Split by story delimiter
    story_blocks = re.split(r"\n  - id:", content)

    for i, block in enumerate(story_blocks):
        if i == 0:
            continue  # Skip manifest

        block = "  - id:" + block
        story = {}

        # Extract fields
        id_match = re.search(r"id:\s*(\S+)", block)
        if id_match:
            story["id"] = id_match.group(1)

        # as_a (may be list or string)
        as_a_match = re.search(r"as_a:\s*\n\s*-\s*(.+)", block)
        if as_a_match:
            story["as_a"] = as_a_match.group(1).strip()
        else:
            as_a_match = re.search(r"as_a:\s*(.+)", block)
            if as_a_match:
                story["as_a"] = as_a_match.group(1).strip()

        # i_want
        i_want_match = re.search(r"i_want:\s*(.+)", block)
        if i_want_match:
            story["i_want"] = i_want_match.group(1).strip().strip('"')

        # so_that
        so_that_match = re.search(r"so_that:\s*(.+)", block)
        if so_that_match:
            story["so_that"] = so_that_match.group(1).strip()

        # priority
        priority_match = re.search(r"priority:\s*(\S+)", block)
        if priority_match:
            orig_priority = priority_match.group(1)
            story["priority"] = PRIORITY_MAP.get(orig_priority, "P2")

        # module
        module_match = re.search(r"module:\s*(\S+)", block)
        if module_match:
            story["module"] = module_match.group(1)

        # acceptance_criteria
        criteria = []
        criteria_match = re.search(
            r"acceptance_criteria:\s*\n((?:\s*-\s*.+\n?)+)", block
        )
        if criteria_match:
            for line in criteria_match.group(1).split("\n"):
                line = line.strip()
                if line.startswith("-"):
                    criteria.append(line[1:].strip())
        story["acceptance_criteria"] = criteria

        if "id" in story:
            stories.append(story)

    return stories


def transform_to_v2(story: dict, domain: str) -> dict:
    """Transform a legacy story to v2 format."""
    v2 = {
        "id": story.get("id", ""),
        "as_a": story.get("as_a", ""),
        "i_want": story.get("i_want", ""),
        "so_that": story.get("so_that", ""),
        "acceptance_criteria": story.get("acceptance_criteria", []),
        "domain": domain,
        "target_domain": domain,
        "priority": story.get("priority", "P2"),
        "origin": "legacy",
    }

    # Map actor to role_key
    actor = story.get("as_a", "")
    v2["role_key"] = ACTOR_TO_ROLE.get(actor, actor.lower().replace(" ", "_"))

    return v2


def format_v2_yaml(stories: list) -> str:
    """Format stories as v2 YAML."""
    lines = ["atomic_stories:"]

    for s in stories:
        lines.append(f"  - id: {s['id']}")
        lines.append(f"    as_a: {s['as_a']}")
        lines.append(f"    i_want: {s['i_want']}")
        lines.append(f"    so_that: {s['so_that']}")

        if s["acceptance_criteria"]:
            lines.append("    acceptance_criteria:")
            for c in s["acceptance_criteria"]:
                lines.append(f'      - "{c}"')

        lines.append(f"    domain: {s['domain']}")
        lines.append(f"    target_domain: {s['target_domain']}")
        lines.append(f"    priority: {s['priority']}")
        lines.append(f"    role_key: {s['role_key']}")
        lines.append(f"    origin: {s['origin']}")

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("STEP 1: REFACTOR LEGACY STORIES TO V2 FORMAT")
    print("=" * 70)

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Domain mapping from filename
    domain_from_file = {
        "d-back": "D-BACK",
        "d-dev": "D-DEV",
        "d-ejec": "D-EJEC",
        "d-evol": "D-EVOL",
        "d-fin": "D-FIN",
        "d-gestion": "D-GESTION",
        "d-gob": "D-GOB",
        "d-norm": "D-NORM",
        "d-ops": "D-OPS",
        "d-plan": "D-PLAN",
        "d-seg": "D-SEG",
        "d-tde": "D-TDE",
        "d-terr": "D-TERR",
        "fenix": "FENIX",
        "d-com": "D-BACK",  # Communications → BACK
    }

    total_stories = 0

    for legacy_file in sorted(LEGACY_DIR.glob("kb_goreos_us_*.yml")):
        print(f"\n📂 Processing: {legacy_file.name}")

        # Determine domain from filename
        for key, domain in domain_from_file.items():
            if key in legacy_file.name:
                break
        else:
            domain = "UNKNOWN"

        # Parse legacy stories
        stories = parse_legacy_file(legacy_file)
        print(f"   Found {len(stories)} stories")

        if not stories:
            continue

        # Transform to v2
        v2_stories = [transform_to_v2(s, domain) for s in stories]

        # Write refactored file
        output_file = OUTPUT_DIR / legacy_file.name.replace(
            "kb_goreos_us_", "refactored_"
        )
        output_content = format_v2_yaml(v2_stories)
        output_file.write_text(output_content, encoding="utf-8")

        print(f"   ✅ Saved to: {output_file.name}")
        total_stories += len(v2_stories)

    print("\n" + "=" * 70)
    print(f"STEP 1 COMPLETE: Refactored {total_stories} stories")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
