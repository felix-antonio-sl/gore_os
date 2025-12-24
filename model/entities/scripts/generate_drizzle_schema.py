#!/usr/bin/env python3
"""
GORE_OS Entity → Drizzle Schema Generator

Reads YAML entity definitions from model/entities/ and generates
TypeScript Drizzle ORM schema files.

Usage:
    python3 scripts/generate_drizzle_schema.py
"""
import os
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Type mapping: GORE_OS type → Drizzle type
TYPE_MAP = {
    "UUID": "uuid",
    "String": "text",
    "Text": "text",
    "Integer": "integer",
    "Decimal": "numeric",
    "Boolean": "boolean",
    "Date": "date",
    "DateTime": "timestamp",
    "JSON": "jsonb",
}

# Domain to file mapping
DOMAIN_FILES = {
    "D-ORG": "org",
    "D-FIN": "fin",
    "D-EJE": "eje",
    "D-SYS": "sys",
    "D-GOV": "gov",
    "D-LOC": "loc",
    "D-CONV": "conv",
    "D-DIG": "dig",
    "D-SAL": "sal",
    "D-SEG": "seg",
    "D-PLAN": "plan",
    "D-GEO": "geo",
    "D-NORM": "norm",
    "D-DATA": "data",
}


def parse_yaml_simple(filepath: Path) -> dict:
    """Simple YAML parser for entity files (avoids pyyaml dependency)."""
    result = {}
    current_list = None
    current_list_name = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()

            # Skip empty lines and comments
            if not line or line.startswith("#") or line == "---":
                continue

            # Detect list items
            if line.strip().startswith("- {"):
                if current_list_name:
                    # Parse inline dict: - {name: foo, type: bar}
                    match = re.search(r"\{([^}]+)\}", line)
                    if match:
                        item = {}
                        for pair in match.group(1).split(","):
                            if ":" in pair:
                                k, v = pair.split(":", 1)
                                item[k.strip()] = v.strip().strip("\"'")
                        if current_list_name not in result:
                            result[current_list_name] = []
                        result[current_list_name].append(item)
                continue

            # Detect key: value
            if ":" in line and not line.strip().startswith("-"):
                indent = len(line) - len(line.lstrip())
                parts = line.split(":", 1)
                key = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ""

                # Check if this is a list start
                if value == "":
                    current_list_name = key
                    result[key] = []
                else:
                    result[key] = value.strip("\"'")
                    current_list_name = None

    return result


def entity_id_to_table_name(entity_id: str) -> str:
    """Convert ENT-ORG-FUNCIONARIO → org_funcionario"""
    parts = entity_id.lower().replace("ent-", "").split("-")
    return "_".join(parts)


def generate_drizzle_column(attr: dict) -> str:
    """Generate Drizzle column definition."""
    name = attr.get("name", "")
    attr_type = attr.get("type", "String")
    is_key = attr.get("key", "") == "true"
    is_nullable = attr.get("nullable", "") == "true"
    fk = attr.get("fk", "")
    default = attr.get("default", "")

    drizzle_type = TYPE_MAP.get(attr_type, "text")

    # Build column definition
    if drizzle_type == "uuid":
        col = f"uuid('{name}')"
    elif drizzle_type == "numeric":
        col = f"numeric('{name}', {{ precision: 15, scale: 2 }})"
    elif drizzle_type == "jsonb":
        col = f"jsonb('{name}')"
    else:
        col = f"{drizzle_type}('{name}')"

    # Add modifiers
    if is_key:
        if drizzle_type == "uuid":
            col += ".primaryKey().defaultRandom()"
        else:
            col += ".primaryKey()"
    elif not is_nullable and not default:
        col += ".notNull()"

    if default and default not in ["null", "false", "true"]:
        col += f".default('{default}')"
    elif default == "false":
        col += ".default(false)"
    elif default == "true":
        col += ".default(true)"

    return f"  {name}: {col},"


def generate_schema_file(domain: str, entities: list) -> str:
    """Generate complete Drizzle schema file for a domain."""
    lines = [
        f"// GORE_OS Drizzle Schema - Domain: {domain}",
        f"// Auto-generated: {datetime.now().isoformat()}",
        f"// DO NOT EDIT MANUALLY - Regenerate from model/entities/",
        "",
        "import { pgTable, uuid, text, integer, numeric, boolean, date, timestamp, jsonb } from 'drizzle-orm/pg-core';",
        "",
    ]

    for entity in entities:
        entity_id = entity.get("id", "")
        entity_name = entity.get("name", "")
        table_name = entity_id_to_table_name(entity_id)
        attributes = entity.get("attributes", [])

        lines.append(f"// {entity_name}")
        lines.append(
            f"export const {table_name.replace('_', '')} = pgTable('{table_name}', {{"
        )

        for attr in attributes:
            lines.append(generate_drizzle_column(attr))

        lines.append("});")
        lines.append("")

    return "\n".join(lines)


def main():
    # Resolve from script location: scripts/ is inside model/entities/
    # So we go up 3 levels to reach gore_os root
    base_path = Path(__file__).parent.parent.parent.parent  # gore_os/
    entities_path = base_path / "model" / "entities"
    output_path = base_path / "apps" / "api" / "src" / "db" / "schema"

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    print("🔄 GORE_OS Entity → Drizzle Schema Generator")
    print(f"   Entities path: {entities_path}")
    print(f"   Output path: {output_path}")
    print("=" * 60)

    # Group entities by domain
    entities_by_domain = defaultdict(list)

    for yml_file in sorted(entities_path.glob("ent-*.yml")):
        try:
            entity = parse_yaml_simple(yml_file)
            domain = entity.get("domain", "D-SYS")
            entities_by_domain[domain].append(entity)
            print(f"  ✓ Parsed: {yml_file.name} → {domain}")
        except Exception as e:
            print(f"  ⚠️ Error parsing {yml_file.name}: {e}")

    print()
    print("📝 Generating Drizzle schemas...")

    # Generate schema files by domain
    for domain, entities in entities_by_domain.items():
        file_prefix = DOMAIN_FILES.get(domain, "misc")
        output_file = output_path / f"{file_prefix}.ts"

        schema_content = generate_schema_file(domain, entities)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(schema_content)

        print(f"  ✓ Generated: {output_file.name} ({len(entities)} entities)")

    # Generate index file
    index_content = [
        "// GORE_OS Drizzle Schema Index",
        f"// Auto-generated: {datetime.now().isoformat()}",
        "",
    ]
    for domain in sorted(entities_by_domain.keys()):
        file_prefix = DOMAIN_FILES.get(domain, "misc")
        index_content.append(f"export * from './{file_prefix}';")

    with open(output_path / "index.ts", "w", encoding="utf-8") as f:
        f.write("\n".join(index_content))

    print()
    print("=" * 60)
    print(f"✅ Generated {len(entities_by_domain)} schema files")
    print(f"📁 Output: {output_path}")


if __name__ == "__main__":
    main()
