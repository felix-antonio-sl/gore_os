#!/usr/bin/env python3
"""
Rigorous Legacy Story Integration Script
Evaluates each legacy story 1x1 against all v3 stories.
Only adds if not a semantic duplicate (threshold: 80%).
Generates detailed decision log.
"""

import re
from pathlib import Path
from difflib import SequenceMatcher
from datetime import datetime

# Paths
V3_FILE = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/historias_usuarios_v3.yml"
)
LEGACY_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/user-stories")
LOG_FILE = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/integration_log.yml"
)

SIMILARITY_THRESHOLD = 0.80


def text_similarity(a: str, b: str) -> float:
    """Calculate similarity between two strings."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def extract_v3_stories() -> list:
    """Extract all stories from v3 file."""
    content = V3_FILE.read_text(encoding="utf-8")
    stories = []

    # Find all story blocks (both capability_bundles and atomic_stories)
    blocks = re.split(r"\n\s*- id:\s*", content)

    for block in blocks[1:]:  # Skip first (manifest)
        story = {}

        # Get ID
        id_match = re.match(r"(\S+)", block)
        if id_match:
            story["id"] = id_match.group(1)

        # Get i_want
        i_want_match = re.search(r"i_want:\s*(.+?)(?=\n\s+\w+:|$)", block, re.DOTALL)
        if i_want_match:
            story["i_want"] = i_want_match.group(1).strip().strip('"')

        # Get as_a
        as_a_match = re.search(r"as_a:\s*(.+?)(?=\n|$)", block)
        if as_a_match:
            story["as_a"] = as_a_match.group(1).strip()

        if story.get("id") and story.get("i_want"):
            stories.append(story)

    return stories


def extract_legacy_stories(filepath: Path) -> list:
    """Extract stories from a legacy YAML file."""
    content = filepath.read_text(encoding="utf-8")
    stories = []

    blocks = re.split(r"\n\s*- id:\s*", content)

    for block in blocks[1:]:
        story = {"source_file": filepath.name}

        id_match = re.match(r"(\S+)", block)
        if id_match:
            story["id"] = id_match.group(1)

        # as_a (handle list format)
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
            # Normalize priority
            prio_map = {"Crítica": "P0", "Alta": "P1", "Media": "P2", "Baja": "P3"}
            story["priority"] = prio_map.get(prio, prio)

        if story.get("id") and story.get("i_want"):
            stories.append(story)

    return stories


def is_semantic_duplicate(legacy_story: dict, v3_stories: list) -> tuple:
    """
    Check if legacy story is a semantic duplicate of any v3 story.
    Returns: (is_duplicate, best_match_id, best_similarity)
    """
    legacy_i_want = legacy_story.get("i_want", "")

    best_match_id = None
    best_similarity = 0.0

    for v3_story in v3_stories:
        v3_i_want = v3_story.get("i_want", "")
        similarity = text_similarity(legacy_i_want, v3_i_want)

        if similarity > best_similarity:
            best_similarity = similarity
            best_match_id = v3_story["id"]

    is_dup = best_similarity >= SIMILARITY_THRESHOLD
    return (is_dup, best_match_id, best_similarity)


def format_story_yaml(story: dict, indent: int = 2) -> str:
    """Format a story as YAML for appending to v3."""
    prefix = " " * indent
    lines = [
        f"{prefix}- id: {story['id']}",
        f"{prefix}  as_a: {story.get('as_a', '')}",
        f"{prefix}  i_want: {story.get('i_want', '')}",
        f"{prefix}  so_that: {story.get('so_that', '')}",
        f"{prefix}  priority: {story.get('priority', 'P2')}",
        f"{prefix}  origin: legacy",
        f"{prefix}  source_file: {story.get('source_file', '')}",
    ]
    return "\n".join(lines)


def process_batch(legacy_file: Path, v3_stories: list, log_entries: list) -> tuple:
    """
    Process one legacy file, comparing each story against v3.
    Returns: (stories_to_add, updated_log_entries)
    """
    legacy_stories = extract_legacy_stories(legacy_file)
    stories_to_add = []

    print(f"\n📂 Processing: {legacy_file.name} ({len(legacy_stories)} stories)")

    added_count = 0
    skipped_count = 0

    for story in legacy_stories:
        is_dup, match_id, similarity = is_semantic_duplicate(story, v3_stories)

        if is_dup:
            decision = "SKIP"
            reason = f"Duplicates {match_id} ({similarity*100:.0f}% similar)"
            skipped_count += 1
        else:
            decision = "ADD"
            reason = f"Unique (best match: {match_id} at {similarity*100:.0f}%)"
            stories_to_add.append(story)
            added_count += 1

        log_entries.append(
            {
                "legacy_id": story["id"],
                "legacy_i_want": story.get("i_want", "")[:60] + "...",
                "decision": decision,
                "reason": reason,
                "match_id": match_id,
                "similarity": round(similarity, 2),
            }
        )

    print(f"   ✅ Added: {added_count} | ⏭️ Skipped: {skipped_count}")

    return stories_to_add, log_entries


def main():
    print("=" * 70)
    print("RIGOROUS LEGACY STORY INTEGRATION")
    print(f"Threshold: {SIMILARITY_THRESHOLD*100:.0f}% similarity")
    print("=" * 70)

    # Step 1: Load current v3
    print("\n📂 Loading v3 baseline...")
    v3_stories = extract_v3_stories()
    print(f"   v3 stories: {len(v3_stories)}")

    # Step 2: Process each legacy file
    log_entries = []
    all_stories_to_add = []

    legacy_files = [
        "kb_goreos_us_d-back.yml",
        "kb_goreos_us_d-fin.yml",
        "kb_goreos_us_d-tde.yml",
        "kb_goreos_us_d-gob.yml",
        "kb_goreos_us_d-ejec.yml",
        "kb_goreos_us_d-norm.yml",
        "kb_goreos_us_d-seg.yml",
        "kb_goreos_us_d-evol.yml",
        "kb_goreos_us_d-terr.yml",
        "kb_goreos_us_d-gestion.yml",
        "kb_goreos_us_d-dev.yml",
        "kb_goreos_us_d-ops.yml",
        "kb_goreos_us_d-com.yml",
        "kb_goreos_us_fenix.yml",
    ]

    for filename in legacy_files:
        filepath = LEGACY_DIR / filename
        if filepath.exists():
            new_stories, log_entries = process_batch(filepath, v3_stories, log_entries)
            all_stories_to_add.extend(new_stories)
            # Add new stories to v3_stories for subsequent comparisons
            v3_stories.extend(new_stories)

    # Step 3: Append unique stories to v3
    print("\n" + "=" * 70)
    print("APPENDING UNIQUE STORIES TO V3")
    print("=" * 70)

    if all_stories_to_add:
        v3_content = V3_FILE.read_text(encoding="utf-8")

        # Add legacy stories section
        v3_content += "\n\n# ============================================\n"
        v3_content += "# LEGACY STORIES (rigorously deduplicated)\n"
        v3_content += f"# Added: {datetime.now().isoformat()}\n"
        v3_content += f"# Total: {len(all_stories_to_add)} unique stories\n"
        v3_content += "# ============================================\n\n"

        for story in all_stories_to_add:
            v3_content += format_story_yaml(story) + "\n"

        V3_FILE.write_text(v3_content, encoding="utf-8")
        print(f"✅ Added {len(all_stories_to_add)} stories to v3")

    # Step 4: Save log
    log_content = f"# Integration Log - {datetime.now().isoformat()}\n"
    log_content += f"# Threshold: {SIMILARITY_THRESHOLD}\n"
    log_content += f"# Total processed: {len(log_entries)}\n"
    log_content += (
        f"# Added: {len([e for e in log_entries if e['decision'] == 'ADD'])}\n"
    )
    log_content += (
        f"# Skipped: {len([e for e in log_entries if e['decision'] == 'SKIP'])}\n\n"
    )
    log_content += "decisions:\n"

    for entry in log_entries:
        log_content += f"  - legacy_id: {entry['legacy_id']}\n"
        log_content += f"    decision: {entry['decision']}\n"
        log_content += f"    similarity: {entry['similarity']}\n"
        log_content += f"    match_id: {entry['match_id']}\n"
        log_content += f"    reason: \"{entry['reason']}\"\n"

    LOG_FILE.write_text(log_content, encoding="utf-8")
    print(f"📝 Log saved to: {LOG_FILE}")

    # Summary
    added = len([e for e in log_entries if e["decision"] == "ADD"])
    skipped = len([e for e in log_entries if e["decision"] == "SKIP"])

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Legacy stories processed: {len(log_entries)}")
    print(f"Added to v3: {added}")
    print(f"Skipped (duplicates): {skipped}")
    print(f"New v3 total: {len(v3_stories)}")


if __name__ == "__main__":
    main()
