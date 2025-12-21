#!/usr/bin/env python3
"""
Step 2 & 3: Merge v2 + Consolidated Legacy → v3
Creates historias_usuarios_v3.yml by:
1. Copying v2 as base (marking origin: v2)
2. Adding consolidated legacy stories (avoiding semantic duplicates)
"""

import re
from pathlib import Path
from difflib import SequenceMatcher

V2_FILE = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/historias_usuarios_v2.yml"
)
LEGACY_FILE = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/user-stories-refactored/consolidated_legacy.yml"
)
V3_FILE = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/historias_usuarios_v3.yml"
)

SIMILARITY_THRESHOLD = 0.80


def text_similarity(a: str, b: str) -> float:
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def extract_stories_from_v2(content: str) -> list:
    """Extract all story IDs and i_want from v2."""
    stories = []

    # Pattern for atomic stories
    blocks = re.split(r"\n\s*- id:", content)
    for block in blocks[1:]:
        story = {}
        id_match = re.search(r"^(\S+)", block)
        if id_match:
            story["id"] = id_match.group(1)

        i_want_match = re.search(r"i_want:\s*(.+?)(?=\n\s+\w+:|$)", block, re.DOTALL)
        if i_want_match:
            story["i_want"] = i_want_match.group(1).strip()

        if story.get("id") and story.get("i_want"):
            stories.append(story)

    return stories


def extract_stories_from_legacy(content: str) -> list:
    """Extract stories from consolidated legacy file."""
    stories = []

    # Find atomic_stories section
    atomic_match = re.search(r"atomic_stories:(.*)", content, re.DOTALL)
    if not atomic_match:
        return stories

    blocks = re.split(r"\n\s*- id:", atomic_match.group(1))
    for block in blocks[1:]:
        story = {}
        id_match = re.search(r"^(\S+)", block)
        if id_match:
            story["id"] = id_match.group(1)

        for field in ["as_a", "i_want", "so_that", "priority", "role_key"]:
            match = re.search(rf"{field}:\s*(.+?)(?=\n|$)", block)
            if match:
                story[field] = match.group(1).strip()

        if story.get("id"):
            stories.append(story)

    return stories


def find_semantic_duplicates(legacy_stories: list, v2_stories: list) -> tuple:
    """Find legacy stories that are semantically duplicate of v2."""
    duplicates = []
    unique = []

    v2_i_wants = [s.get("i_want", "") for s in v2_stories]

    for story in legacy_stories:
        i_want = story.get("i_want", "")
        is_dup = False

        for v2_text in v2_i_wants:
            if text_similarity(i_want, v2_text) > SIMILARITY_THRESHOLD:
                is_dup = True
                duplicates.append(
                    {
                        "legacy_id": story["id"],
                        "similarity": text_similarity(i_want, v2_text),
                    }
                )
                break

        if not is_dup:
            unique.append(story)

    return unique, duplicates


def create_v3(v2_content: str, unique_legacy: list) -> str:
    """Create v3 file from v2 + unique legacy."""
    lines = []

    # Update manifest
    v2_lines = v2_content.split("\n")
    in_manifest = False
    manifest_done = False

    for line in v2_lines:
        if line.strip() == "_manifest:":
            in_manifest = True
            lines.append(line)
            continue

        if in_manifest and not manifest_done:
            if line.strip().startswith("urn:"):
                lines.append('  urn: "urn:goreos:specs:user-stories:3.0.0"')
                continue
            elif line.strip().startswith("title:"):
                lines.append('  title: "Catálogo Consolidado v3 (v2 + Legacy)"')
                continue
            elif line.strip() and not line.strip().startswith("-") and ":" in line:
                lines.append(line)
            else:
                # Add v3 metadata before ending manifest
                lines.append(f"  v2_stories_count: 317")
                lines.append(f"  legacy_added_count: {len(unique_legacy)}")
                lines.append(f"  total_stories: {317 + len(unique_legacy)}")
                lines.append(line)
                manifest_done = True
                in_manifest = False
        else:
            lines.append(line)

    # Add legacy stories to atomic_stories
    lines.append("\n# === LEGACY STORIES (added from user-stories/) ===")
    lines.append("")

    for story in unique_legacy:
        lines.append(f"  - id: {story.get('id', 'UNKNOWN')}")
        lines.append(f"    as_a: {story.get('as_a', '')}")
        lines.append(f"    i_want: {story.get('i_want', '')}")
        lines.append(f"    so_that: {story.get('so_that', '')}")
        lines.append(f"    priority: {story.get('priority', 'P2')}")
        lines.append(f"    role_key: {story.get('role_key', '')}")
        lines.append(f"    origin: legacy")

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("STEP 2 & 3: MERGE V2 + LEGACY → V3")
    print("=" * 70)

    # Load files
    print("\n📂 Loading v2...")
    v2_content = V2_FILE.read_text(encoding="utf-8")
    v2_stories = extract_stories_from_v2(v2_content)
    print(f"   v2 stories: {len(v2_stories)}")

    print("\n📂 Loading consolidated legacy...")
    legacy_content = LEGACY_FILE.read_text(encoding="utf-8")
    legacy_stories = extract_stories_from_legacy(legacy_content)
    print(f"   Legacy atomic stories: {len(legacy_stories)}")

    # Find duplicates
    print(f"\n🔍 Finding semantic duplicates (threshold: {SIMILARITY_THRESHOLD})...")
    unique_legacy, duplicates = find_semantic_duplicates(legacy_stories, v2_stories)
    print(f"   Duplicates found: {len(duplicates)}")
    print(f"   Unique legacy to add: {len(unique_legacy)}")

    # Create v3
    print("\n📝 Creating v3...")
    v3_content = create_v3(v2_content, unique_legacy)
    V3_FILE.write_text(v3_content, encoding="utf-8")

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"v2 stories: {len(v2_stories)}")
    print(f"Legacy added: {len(unique_legacy)}")
    print(f"Duplicates excluded: {len(duplicates)}")
    print(f"Total v3: {len(v2_stories) + len(unique_legacy)}")
    print(f"\n✅ Saved to: {V3_FILE}")


if __name__ == "__main__":
    main()
