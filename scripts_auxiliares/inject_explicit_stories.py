#!/usr/bin/env python3
"""
Explicit Story Injection Script
Injects ALL story IDs from historias_usuarios_v2.yml into domain files.
Groups stories by target_domain and creates comprehensive tables.
"""

import re
from pathlib import Path
from collections import defaultdict

SSOT_PATH = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/historias_usuarios_v2.yml"
)
DOMAINS_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/domains")

# Domain file mapping
DOMAIN_FILES = {
    "D-BACK": "domain_d-back.md",
    "D-DEV": "domain_d-dev.md",
    "D-EJEC": "domain_d-ejec.md",
    "D-EVOL": "domain_d-evol.md",
    "D-FIN": "domain_d-fin.md",
    "D-GESTION": "domain_d-gestion.md",
    "D-GOB": "domain_d-gob.md",
    "D-NORM": "domain_d-norm.md",
    "D-OPS": "domain_d-ops.md",
    "D-PLAN": "domain_d-plan.md",
    "D-SEG": "domain_d-seg.md",
    "D-TDE": "domain_d-tde.md",
    "D-TERR": "domain_d-terr.md",
}


def parse_stories(content: str) -> list:
    """Parse all stories from SSOT content."""
    stories = []

    # Parse atomic stories and capability bundles
    # Simple regex-based extraction
    lines = content.split("\n")
    current_story = {}
    in_story = False

    for i, line in enumerate(lines):
        # Detect story start
        if re.match(r"\s*- id:\s*(US-|CAP-)", line):
            if current_story and "id" in current_story:
                stories.append(current_story)
            current_story = {}
            match = re.search(r"id:\s*(\S+)", line)
            if match:
                current_story["id"] = match.group(1)
            in_story = True
        elif in_story:
            # Extract as_a
            if "as_a:" in line:
                match = re.search(r"as_a:\s*(.+)", line)
                if match:
                    current_story["as_a"] = match.group(1).strip()
            # Extract i_want (first line only)
            elif "i_want:" in line:
                match = re.search(r"i_want:\s*(.+)", line)
                if match:
                    current_story["i_want"] = match.group(1).strip()[:60]  # Truncate
            # Extract domain
            elif re.match(r"\s+domain:\s*", line):
                match = re.search(r"domain:\s*(\S+)", line)
                if match:
                    current_story["domain"] = match.group(1)
            # Extract target_domain
            elif "target_domain:" in line:
                match = re.search(r"target_domain:\s*(\S+)", line)
                if match:
                    current_story["target_domain"] = match.group(1)
            # Extract priority
            elif "priority:" in line:
                match = re.search(r"priority:\s*(\S+)", line)
                if match:
                    current_story["priority"] = match.group(1)
            # Extract role_key
            elif "role_key:" in line:
                match = re.search(r"role_key:\s*(\S+)", line)
                if match:
                    current_story["role_key"] = match.group(1)
            # Detect next story or section
            elif re.match(r"\s*- id:\s*", line) or re.match(r"\w+:", line):
                in_story = False

    # Don't forget the last story
    if current_story and "id" in current_story:
        stories.append(current_story)

    return stories


def group_by_domain(stories: list) -> dict:
    """Group stories by target_domain (or domain if target_domain not present)."""
    grouped = defaultdict(list)
    for story in stories:
        domain = story.get("target_domain", story.get("domain", "UNKNOWN"))
        grouped[domain].append(story)
    return grouped


def generate_stories_table(stories: list) -> str:
    """Generate markdown table for stories."""
    if not stories:
        return ""

    lines = []
    lines.append("| ID | Role | Descripción | P |")
    lines.append("|-----|------|-------------|---|")

    for s in sorted(stories, key=lambda x: x.get("id", "")):
        story_id = s.get("id", "?")
        role = s.get("role_key", s.get("as_a", "?"))[:20]
        desc = s.get("i_want", "?")[:50]
        priority = s.get("priority", "?")
        lines.append(f"| {story_id} | {role} | {desc}... | {priority} |")

    return "\n".join(lines)


def inject_into_domain(domain_file: Path, stories: list, domain_id: str) -> bool:
    """Inject stories table into domain file."""
    content = domain_file.read_text(encoding="utf-8")

    # Check if explicit table already exists
    if "## Catálogo Completo de Historias (SSOT)" in content:
        print(f"   ⏭️  {domain_file.name}: Already has explicit catalog, skipping")
        return False

    # Generate table
    table = generate_stories_table(stories)

    # Create section
    section = f"""
---

## Catálogo Completo de Historias (SSOT)

> Fuente: `historias_usuarios_v2.yml` | Filtro: `target_domain: {domain_id}`  
> Total: {len(stories)} historias

{table}

"""

    # Find insertion point (before footer)
    footer_pattern = r"\n---\n\n\*Documento parte de GORE_OS"
    match = re.search(footer_pattern, content)

    if match:
        # Insert before footer
        insert_pos = match.start()
        new_content = content[:insert_pos] + section + content[insert_pos:]
    else:
        # Append at end
        new_content = content + section

    domain_file.write_text(new_content, encoding="utf-8")
    print(f"   ✅ {domain_file.name}: Injected {len(stories)} stories")
    return True


def main():
    print("=" * 70)
    print("EXPLICIT STORY INJECTION")
    print("=" * 70)

    # Read and parse SSOT
    print("\n📖 Reading SSOT...")
    ssot_content = SSOT_PATH.read_text(encoding="utf-8")
    stories = parse_stories(ssot_content)
    print(f"   Found {len(stories)} stories")

    # Group by domain
    grouped = group_by_domain(stories)
    print(f"\n📊 Stories by domain:")
    for domain, domain_stories in sorted(grouped.items()):
        print(f"   {domain}: {len(domain_stories)}")

    # Inject into each domain
    print("\n💉 Injecting into domain files...")
    injected = 0
    total_stories_injected = 0

    for domain_id, filename in DOMAIN_FILES.items():
        domain_file = DOMAINS_DIR / filename
        if not domain_file.exists():
            print(f"   ⚠️  {filename}: File not found")
            continue

        domain_stories = grouped.get(domain_id, [])
        if domain_stories:
            if inject_into_domain(domain_file, domain_stories, domain_id):
                injected += 1
                total_stories_injected += len(domain_stories)
        else:
            print(f"   ℹ️  {filename}: No stories for {domain_id}")

    print("\n" + "=" * 70)
    print("INJECTION SUMMARY")
    print("=" * 70)
    print(f"Domains modified: {injected}")
    print(f"Stories injected: {total_stories_injected}")
    print("\n✅ Done! Run verify_ssot_coverage.py to confirm 100%.")


if __name__ == "__main__":
    main()
