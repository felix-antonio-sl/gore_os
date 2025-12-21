#!/usr/bin/env python3
"""
SSOT Coverage Verification Script
Verifies that 100% of stories from historias_usuarios_v2.yml
are referenced in domain files.
"""

import re
from pathlib import Path

SSOT_PATH = Path(
    "/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/historias_usuarios_v2.yml"
)
DOMAINS_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/domains")


def extract_story_ids(ssot_content: str) -> set:
    """Extract all story IDs from SSOT file."""
    # Match CAP-* and US-* patterns
    pattern = r"(?:- id:|id:)\s*((?:CAP|US)-[\w-]+)"
    matches = re.findall(pattern, ssot_content)
    return set(matches)


def extract_role_keys(ssot_content: str) -> set:
    """Extract all role_keys from SSOT file."""
    pattern = r"role_key:\s*(\w+)"
    matches = re.findall(pattern, ssot_content)
    return set(matches)


def search_in_domains(story_ids: set, role_keys: set) -> dict:
    """Search for each story ID and role_key in domain files."""
    results = {
        "stories_found": set(),
        "stories_missing": set(),
        "roles_found": set(),
        "roles_missing": set(),
        "story_locations": {},
        "role_locations": {},
    }

    # Collect all domain content
    all_domain_content = ""
    domain_files = list(DOMAINS_DIR.glob("**/*.md"))

    for domain_file in domain_files:
        content = domain_file.read_text(encoding="utf-8")
        all_domain_content += content

    # Check each story ID
    for story_id in story_ids:
        if story_id in all_domain_content:
            results["stories_found"].add(story_id)
            # Find which file contains it
            for domain_file in domain_files:
                if story_id in domain_file.read_text(encoding="utf-8"):
                    results["story_locations"][story_id] = domain_file.name
                    break
        else:
            results["stories_missing"].add(story_id)

    # Check each role_key
    for role_key in role_keys:
        if role_key in all_domain_content:
            results["roles_found"].add(role_key)
        else:
            results["roles_missing"].add(role_key)

    return results


def main():
    print("=" * 70)
    print("SSOT COVERAGE VERIFICATION")
    print("=" * 70)

    # Read SSOT
    ssot_content = SSOT_PATH.read_text(encoding="utf-8")

    # Extract IDs
    story_ids = extract_story_ids(ssot_content)
    role_keys = extract_role_keys(ssot_content)

    print(f"\n📊 SSOT STATISTICS")
    print(f"   Total Story IDs (CAP-* + US-*): {len(story_ids)}")
    print(f"   Total Role Keys: {len(role_keys)}")

    # Search in domains
    results = search_in_domains(story_ids, role_keys)

    # Report Stories
    print(f"\n📖 STORY COVERAGE")
    print(f"   Found in domains: {len(results['stories_found'])} / {len(story_ids)}")
    coverage_pct = (
        (len(results["stories_found"]) / len(story_ids)) * 100 if story_ids else 0
    )
    print(f"   Coverage: {coverage_pct:.1f}%")

    if results["stories_missing"]:
        print(f"\n   ⚠️  Missing Stories ({len(results['stories_missing'])}):")
        for sid in sorted(results["stories_missing"])[:20]:
            print(f"       - {sid}")
        if len(results["stories_missing"]) > 20:
            print(f"       ... and {len(results['stories_missing']) - 20} more")
    else:
        print(f"\n   ✅ ALL STORIES ACCOUNTED FOR!")

    # Report Roles
    print(f"\n👥 ROLE KEY COVERAGE")
    print(f"   Found in domains: {len(results['roles_found'])} / {len(role_keys)}")
    role_coverage = (
        (len(results["roles_found"]) / len(role_keys)) * 100 if role_keys else 0
    )
    print(f"   Coverage: {role_coverage:.1f}%")

    if results["roles_missing"]:
        print(f"\n   ⚠️  Missing Roles ({len(results['roles_missing'])}):")
        for rid in sorted(results["roles_missing"])[:20]:
            print(f"       - {rid}")
    else:
        print(f"\n   ✅ ALL ROLES ACCOUNTED FOR!")

    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print(
        f"Stories: {len(results['stories_found'])}/{len(story_ids)} ({coverage_pct:.1f}%)"
    )
    print(
        f"Roles: {len(results['roles_found'])}/{len(role_keys)} ({role_coverage:.1f}%)"
    )

    if coverage_pct == 100 and role_coverage == 100:
        print("\n🎉 100% COVERAGE VERIFIED!")
    else:
        print(f"\n⚠️  Coverage incomplete. See missing items above.")


if __name__ == "__main__":
    main()
