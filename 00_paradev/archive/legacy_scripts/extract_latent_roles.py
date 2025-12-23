#!/usr/bin/env python3
"""
Extract and categorize latent roles (roles without associated user stories).
Outputs a structured analysis for planning future story development.
"""
import yaml
import os
from collections import defaultdict

BASE_DIR = (
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/historias_usuarios"
)
ROLES_FILE = os.path.join(BASE_DIR, "roles.yml")
STORIES_FILE = os.path.join(BASE_DIR, "historias_usuarios.yml")
OUTPUT_FILE = "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/roles/latent_roles_analysis.md"


def load_yaml(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    roles_data = load_yaml(ROLES_FILE)
    stories_data = load_yaml(STORIES_FILE)

    # Build set of used roles
    used_roles = set()
    for story in stories_data.get("atomic_stories", []):
        if story.get("role_id"):
            used_roles.add(story["role_id"])

    # Extract all roles with metadata, grouped by unit
    all_roles = {}
    role_to_unit = {}
    unit_type_map = {}

    for unit in roles_data.get("organization", []):
        unit_name = unit.get("unit", "Unknown")
        unit_type = unit.get("type", "Unknown")
        unit_type_map[unit_name] = unit_type
        for role in unit.get("roles", []):
            role_id = role.get("id")
            if role_id:
                all_roles[role_id] = role
                role_to_unit[role_id] = unit_name

    # Identify latent roles
    latent_role_ids = set(all_roles.keys()) - used_roles

    # Group latent roles by unit
    latent_by_unit = defaultdict(list)
    for role_id in sorted(latent_role_ids):
        unit = role_to_unit.get(role_id, "Unknown")
        latent_by_unit[unit].append(all_roles[role_id])

    # Generate Report
    lines = [
        "# Análisis de Roles Latentes",
        "",
        f"**Total Roles Latentes:** {len(latent_role_ids)} de {len(all_roles)} ({100*len(latent_role_ids)/len(all_roles):.1f}%)",
        "",
        "## Categorización por Unidad Organizacional",
        "",
    ]

    # Count by type
    type_counts = defaultdict(int)
    for unit, roles in latent_by_unit.items():
        unit_type = unit_type_map.get(unit, "Unknown")
        type_counts[unit_type] += len(roles)

    lines.append("### Resumen por Tipo de Unidad")
    lines.append("| Tipo | Roles Latentes |")
    lines.append("|------|----------------|")
    for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {t} | {count} |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Detalle por Unidad")
    lines.append("")

    for unit in sorted(latent_by_unit.keys()):
        roles = latent_by_unit[unit]
        unit_type = unit_type_map.get(unit, "Unknown")
        lines.append(f"### {unit} ({unit_type})")
        lines.append("")
        lines.append("| ID | Título | Descripción |")
        lines.append("|---|---|---|")
        for role in roles:
            role_id = role.get("id", "-")
            title = role.get("title", "-")
            desc = role.get("description", role.get("role_key", "-"))
            # Truncate long descriptions
            if len(desc) > 80:
                desc = desc[:77] + "..."
            lines.append(f"| `{role_id}` | {title} | {desc} |")
        lines.append("")

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Analysis written to {OUTPUT_FILE}")
    print(f"Total latent roles: {len(latent_role_ids)}")


if __name__ == "__main__":
    main()
