#!/usr/bin/env python3
"""
Capability-Based Consolidation
Reduces legacy story variants by grouping into capability bundles.
Applies D-01 rule from consensus: consolidate by functional capability.
"""

import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

LEGACY_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/user-stories")
V2_FILE = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/historias_usuarios_v2.yml"
)
OUTPUT_FILE = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/historias_usuarios_v3.yml"
)
REPORT_FILE = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/consolidation_report.md"
)

# Capability patterns - stories matching these will be consolidated
CAPABILITIES = {
    "CAP-DASH-EJEC": {
        "name": "Dashboard de Ejecución/KPIs",
        "patterns": [
            "dashboard",
            "tablero",
            "panel",
            "kpi",
            "indicador",
            "semáforo",
            "monitoreo",
        ],
        "domain": "D-FIN",
    },
    "CAP-RENDICIONES": {
        "name": "Gestión de Rendiciones",
        "patterns": ["rendición", "rendir", "rendiciones", "rendimiento cuenta"],
        "domain": "D-FIN",
    },
    "CAP-PROYECTOS": {
        "name": "Seguimiento de Proyectos/Cartera",
        "patterns": [
            "proyecto",
            "cartera",
            "portafolio",
            "ipr",
            "fndr",
            "inversión",
            "seguimiento",
        ],
        "domain": "D-EJEC",
    },
    "CAP-FIRMA": {
        "name": "Bandeja de Firma Electrónica",
        "patterns": ["firma electrónica", "fea", "bandeja firma", "firmar documento"],
        "domain": "D-TDE",
    },
    "CAP-TRANSPARENCIA": {
        "name": "Transparencia y Acceso Info",
        "patterns": ["transparencia", "acceso información", "cplt", "ley 20.285"],
        "domain": "D-TDE",
    },
    "CAP-COMPRAS": {
        "name": "Compras y Licitaciones",
        "patterns": [
            "compra",
            "licitación",
            "mercado público",
            "pac",
            "orden de compra",
            "proveedor",
        ],
        "domain": "D-BACK",
    },
    "CAP-PAGOS": {
        "name": "Pagos y Tesorería",
        "patterns": ["pago", "transferencia", "tesorería", "tef", "desembolso", "giro"],
        "domain": "D-BACK",
    },
    "CAP-RRHH-FUNC": {
        "name": "Autoservicio Funcionario",
        "patterns": [
            "ficha funcionario",
            "liquidación",
            "permiso",
            "licencia",
            "feriado",
            "certificado",
        ],
        "domain": "D-BACK",
    },
    "CAP-RRHH-GESTOR": {
        "name": "Gestión de Personas",
        "patterns": [
            "remuneración",
            "ausentismo",
            "calificación",
            "capacitación",
            "contrato",
        ],
        "domain": "D-BACK",
    },
    "CAP-DOCUMENTOS": {
        "name": "Gestión Documental",
        "patterns": [
            "documento",
            "resolución",
            "decreto",
            "oficio",
            "acto administrativo",
            "visación",
        ],
        "domain": "D-NORM",
    },
}


def extract_legacy_stories(filepath: Path) -> list:
    """Extract stories from legacy file."""
    content = filepath.read_text(encoding="utf-8")
    stories = []

    blocks = re.split(r"\n\s*- id:\s*", content)
    for block in blocks[1:]:
        story = {"source_file": filepath.name}

        id_match = re.match(r"(\S+)", block)
        if id_match:
            story["id"] = id_match.group(1)

        as_a_match = re.search(r"as_a:\s*\n?\s*-?\s*(.+?)(?=\n\s+\w+:|$)", block)
        if as_a_match:
            story["as_a"] = as_a_match.group(1).strip().strip("- ")

        i_want_match = re.search(r"i_want:\s*(.+?)(?=\n\s+\w+:|$)", block, re.DOTALL)
        if i_want_match:
            story["i_want"] = i_want_match.group(1).strip().strip('"')

        so_that_match = re.search(r"so_that:\s*(.+?)(?=\n|$)", block)
        if so_that_match:
            story["so_that"] = so_that_match.group(1).strip()

        priority_match = re.search(r"priority:\s*(\S+)", block)
        if priority_match:
            prio = priority_match.group(1)
            prio_map = {"Crítica": "P0", "Alta": "P1", "Media": "P2", "Baja": "P3"}
            story["priority"] = prio_map.get(prio, prio)

        if story.get("id") and story.get("i_want"):
            stories.append(story)

    return stories


def classify_story(story: dict) -> tuple:
    """Classify story into capability or mark as atomic."""
    text = (story.get("i_want", "") + " " + story.get("so_that", "")).lower()

    for cap_id, cap_data in CAPABILITIES.items():
        for pattern in cap_data["patterns"]:
            if pattern in text:
                return (cap_id, cap_data["name"])

    return (None, "atomic")


def consolidate_capability(cap_id: str, stories: list) -> dict:
    """Consolidate multiple stories into one capability bundle."""
    # Collect all roles/beneficiaries
    beneficiaries = set()
    for s in stories:
        role = s.get("as_a", "").lower().replace(" ", "_")
        if role:
            beneficiaries.add(role)

    # Use first story as template
    template = stories[0] if stories else {}

    return {
        "id": f"{cap_id}-001",
        "capability": CAPABILITIES[cap_id]["name"],
        "domain": CAPABILITIES[cap_id]["domain"],
        "as_a": "Múltiples roles",
        "i_want": f"Acceder a {CAPABILITIES[cap_id]['name']}",
        "so_that": "Se cubran las necesidades de diferentes stakeholders",
        "beneficiaries": sorted(list(beneficiaries)),
        "consolidated_from": [s["id"] for s in stories[:10]],
        "original_count": len(stories),
        "priority": "P0",
        "origin": "legacy_consolidated",
    }


def main():
    print("=" * 70)
    print("CAPABILITY-BASED CONSOLIDATION")
    print("=" * 70)

    # Load all legacy stories
    all_stories = []
    for filepath in sorted(LEGACY_DIR.glob("kb_goreos_us_*.yml")):
        stories = extract_legacy_stories(filepath)
        all_stories.extend(stories)

    print(f"\n📂 Total legacy stories: {len(all_stories)}")

    # Classify stories
    capability_groups = defaultdict(list)
    atomic_stories = []

    for story in all_stories:
        cap_id, cap_name = classify_story(story)
        if cap_id:
            capability_groups[cap_id].append(story)
        else:
            atomic_stories.append(story)

    print(f"\n🔷 Capability distribution:")
    total_consolidated = 0
    for cap_id, stories in sorted(capability_groups.items()):
        print(f"   {cap_id}: {len(stories)} stories → 1 bundle")
        total_consolidated += len(stories)

    print(f"\n🔹 Atomic (not consolidated): {len(atomic_stories)}")

    # Create consolidated bundles
    consolidated_bundles = []
    for cap_id, stories in capability_groups.items():
        bundle = consolidate_capability(cap_id, stories)
        consolidated_bundles.append(bundle)

    # Results
    final_count = len(consolidated_bundles) + len(atomic_stories)
    reduction = len(all_stories) - final_count
    reduction_pct = round(reduction / len(all_stories) * 100, 1)

    print(f"\n" + "=" * 70)
    print("CONSOLIDATION RESULTS")
    print("=" * 70)
    print(f"Original legacy: {len(all_stories)}")
    print(f"Capability bundles: {len(consolidated_bundles)}")
    print(f"Atomic stories: {len(atomic_stories)}")
    print(f"Final count: {final_count}")
    print(f"Reduction: {reduction} ({reduction_pct}%)")

    # Generate report
    report = f"""# Consolidation Report

**Fecha**: {datetime.now().isoformat()}

## Resumen

| Métrica | Valor |
|---------|-------|
| Legacy original | {len(all_stories)} |
| Bundles creados | {len(consolidated_bundles)} |
| Historias atómicas | {len(atomic_stories)} |
| **Total consolidado** | **{final_count}** |
| **Reducción** | **{reduction} ({reduction_pct}%)** |

## Capability Bundles

| Bundle | Historias Originales | Beneficiarios |
|--------|---------------------|---------------|
"""

    for bundle in consolidated_bundles:
        report += f"| {bundle['id']} | {bundle['original_count']} | {len(bundle['beneficiaries'])} |\n"

    REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"\n📝 Report: {REPORT_FILE}")

    # Now create v3 by combining v2 + consolidated legacy
    print(f"\n📂 Creating v3...")

    v2_content = V2_FILE.read_text(encoding="utf-8")

    # Add consolidated bundles
    v3_content = v2_content
    v3_content += "\n\n# ================================================\n"
    v3_content += "# LEGACY STORIES - CAPABILITY CONSOLIDATED\n"
    v3_content += f"# Original: {len(all_stories)} → Final: {final_count}\n"
    v3_content += f"# Reduction: {reduction_pct}%\n"
    v3_content += "# ================================================\n\n"

    v3_content += "# Capability Bundles\n"
    for bundle in consolidated_bundles:
        v3_content += f"  - id: {bundle['id']}\n"
        v3_content += f"    capability: {bundle['capability']}\n"
        v3_content += f"    domain: {bundle['domain']}\n"
        v3_content += f"    beneficiaries: {bundle['beneficiaries'][:5]}  # Sample\n"
        v3_content += f"    original_count: {bundle['original_count']}\n"
        v3_content += f"    origin: legacy_consolidated\n\n"

    v3_content += "\n# Atomic Stories (not consolidated)\n"
    for story in atomic_stories:
        v3_content += f"  - id: {story['id']}\n"
        v3_content += f"    as_a: {story.get('as_a', '')}\n"
        v3_content += f"    i_want: {story.get('i_want', '')}\n"
        v3_content += f"    so_that: {story.get('so_that', '')}\n"
        v3_content += f"    priority: {story.get('priority', 'P2')}\n"
        v3_content += f"    origin: legacy_atomic\n"

    OUTPUT_FILE.write_text(v3_content, encoding="utf-8")
    print(f"✅ v3 saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
