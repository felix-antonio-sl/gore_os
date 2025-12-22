#!/usr/bin/env python3
"""
Domain Cleanup Script: Remove Legacy Inline Stories
Removes pre-SSOT inline story catalogs and replaces with SSOT reference.
"""

import re
from pathlib import Path

DOMAINS_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/docs/blueprint/domains")

# Patterns to identify legacy inline story sections
LEGACY_PATTERNS = [
    # Table rows with legacy story IDs
    r"\|\s*US-BACK-[A-Z]+-\d+\s*\|[^\n]+\n",
    r"\|\s*US-DEV-[A-Z]+-\d+\s*\|[^\n]+\n",
    r"\|\s*US-TDE-[A-Z]+-\d+\s*\|[^\n]+\n",
]


def find_legacy_sections(content: str) -> list:
    """Find sections with legacy US-XXX-YYY-NNN patterns that are NOT in the SSOT catalog."""
    legacy_ids = set()

    # Patterns for legacy IDs (e.g., US-BACK-ABS-001, US-DEV-CODE-01)
    pattern = r"US-BACK-[A-Z]+-\d+"
    matches = re.findall(pattern, content)
    legacy_ids.update(matches)

    return list(legacy_ids)


def count_ssot_vs_legacy(content: str) -> tuple:
    """Count SSOT stories vs Legacy stories."""
    # SSOT pattern (US-XXX-NNN-NN format like US-TES-001-01)
    ssot_pattern = r"US-[A-Z]+-\d{3}-\d{2}"
    ssot_matches = set(re.findall(ssot_pattern, content))

    # Legacy pattern (US-BACK-XXX-NNN format like US-BACK-ABS-001)
    legacy_pattern = r"US-BACK-[A-Z]+-\d+"
    legacy_matches = set(re.findall(legacy_pattern, content))

    return ssot_matches, legacy_matches


def analyze_domain(domain_file: Path) -> dict:
    """Analyze a domain file for duplication issues."""
    content = domain_file.read_text(encoding="utf-8")
    name = domain_file.name

    ssot_stories, legacy_stories = count_ssot_vs_legacy(content)

    # Check if has SSOT catalog
    has_ssot_catalog = "## Catálogo Completo de Historias (SSOT)" in content

    # Check for legacy sections
    has_legacy_catalog = bool(legacy_stories)

    return {
        "name": name,
        "ssot_count": len(ssot_stories),
        "legacy_count": len(legacy_stories),
        "has_ssot_catalog": has_ssot_catalog,
        "has_legacy": has_legacy_catalog,
        "legacy_ids": sorted(legacy_stories)[:10],  # Sample
        "needs_cleanup": has_legacy_catalog and has_ssot_catalog,
    }


def main():
    print("=" * 70)
    print("DOMAIN DUPLICATION ANALYSIS")
    print("=" * 70)

    domain_files = list(DOMAINS_DIR.glob("domain_*.md"))

    results = []
    for domain_file in sorted(domain_files):
        result = analyze_domain(domain_file)
        results.append(result)

    print("\n📊 ANALYSIS RESULTS\n")
    print(f"{'Domain':<25} {'SSOT':<8} {'Legacy':<8} {'Needs Cleanup':<15}")
    print("-" * 60)

    cleanup_needed = []
    for r in results:
        cleanup = "⚠️ YES" if r["needs_cleanup"] else "✅ No"
        print(
            f"{r['name']:<25} {r['ssot_count']:<8} {r['legacy_count']:<8} {cleanup:<15}"
        )
        if r["needs_cleanup"]:
            cleanup_needed.append(r)

    print("\n" + "=" * 70)
    print(f"SUMMARY: {len(cleanup_needed)} domains need cleanup")
    print("=" * 70)

    if cleanup_needed:
        print("\nDomains requiring cleanup:")
        for c in cleanup_needed:
            print(f"  - {c['name']}: {c['legacy_count']} legacy stories")
            if c["legacy_ids"]:
                print(f"    Sample: {', '.join(c['legacy_ids'][:5])}")


if __name__ == "__main__":
    main()
