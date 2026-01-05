"""
Generate complete relationship map between all legacy domains.
Creates a visual and tabular summary of all cross-domain links.
"""

import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List


NORMALIZED_DIR = Path(__file__).parent.parent / "normalized"
OUTPUT_DIR = NORMALIZED_DIR / "relationships"


def load_csv(filepath: Path) -> List[Dict]:
    """Load CSV file as list of dicts."""
    if not filepath.exists():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def count_records():
    """Count records in all normalized tables."""
    counts = {}

    # Dimensions
    for f in (NORMALIZED_DIR / "dimensions").glob("*.csv"):
        data = load_csv(f)
        counts[f"dim/{f.stem}"] = len(data)

    # Facts
    for f in (NORMALIZED_DIR / "facts").glob("*.csv"):
        data = load_csv(f)
        counts[f"fact/{f.stem}"] = len(data)

    # Documents
    for f in (NORMALIZED_DIR / "documents").glob("*.csv"):
        data = load_csv(f)
        counts[f"doc/{f.stem}"] = len(data)

    # Relationships
    for f in OUTPUT_DIR.glob("*.csv"):
        data = load_csv(f)
        counts[f"rel/{f.stem}"] = len(data)

    return counts


def analyze_unified_iniciativas():
    """Analyze coverage of unified iniciativas."""
    data = load_csv(NORMALIZED_DIR / "dimensions" / "dim_iniciativa_unificada.csv")

    stats = {
        "total": len(data),
        "has_idis": 0,
        "has_convenios": 0,
        "has_fril": 0,
        "has_progs": 0,
        "multi_source": 0,
        "by_fuente": defaultdict(int),
    }

    for row in data:
        sources = 0
        if row.get("cod_unico_idis"):
            stats["has_idis"] += 1
            sources += 1
        if row.get("codigo_convenios"):
            stats["has_convenios"] += 1
            sources += 1
        if row.get("codigo_fril"):
            stats["has_fril"] += 1
            sources += 1
        if row.get("codigo_progs"):
            stats["has_progs"] += 1
            sources += 1

        if sources > 1:
            stats["multi_source"] += 1

        stats["by_fuente"][row.get("fuente_principal", "UNKNOWN")] += 1

    return stats


def analyze_matches():
    """Analyze cross-domain matches."""
    data = load_csv(OUTPUT_DIR / "cross_domain_matches.csv")

    stats = {
        "total": len(data),
        "by_pair": defaultdict(int),
        "by_type": defaultdict(int),
    }

    for row in data:
        # Normalize domain names
        src = row.get("source_domain", "").split("_")[0]
        tgt = row.get("target_domain", "").split("_")[0]
        pair = tuple(sorted([src, tgt]))
        stats["by_pair"][pair] += 1
        stats["by_type"][row.get("match_type", "UNKNOWN")] += 1

    return stats


def generate_report():
    """Generate complete relationship report."""
    print("=" * 60)
    print("LEGACY ETL - COMPLETE RELATIONSHIP MAP")
    print("=" * 60)

    # Record counts
    print("\n1. NORMALIZED DATA COUNTS")
    print("-" * 40)
    counts = count_records()
    for table, count in sorted(counts.items()):
        print(f"  {table}: {count:,}")

    # Unified iniciativas analysis
    print("\n2. UNIFIED INICIATIVAS ANALYSIS")
    print("-" * 40)
    ini_stats = analyze_unified_iniciativas()
    print(f"  Total unified: {ini_stats['total']:,}")
    print(f"  With IDIS data: {ini_stats['has_idis']:,}")
    print(f"  With CONVENIOS data: {ini_stats['has_convenios']:,}")
    print(f"  With FRIL data: {ini_stats['has_fril']:,}")
    print(f"  Multi-source (cross-linked): {ini_stats['multi_source']:,}")
    print("\n  By primary source:")
    for fuente, count in sorted(ini_stats["by_fuente"].items()):
        print(f"    {fuente}: {count:,}")

    # Cross-domain matches
    print("\n3. CROSS-DOMAIN MATCHES")
    print("-" * 40)
    match_stats = analyze_matches()
    print(f"  Total matches: {match_stats['total']:,}")
    print("\n  By domain pair:")
    for pair, count in sorted(match_stats["by_pair"].items()):
        print(f"    {pair[0]} <-> {pair[1]}: {count:,}")
    print("\n  By match type:")
    for mtype, count in sorted(match_stats["by_type"].items()):
        print(f"    {mtype}: {count:,}")

    # Relationship summary
    print("\n4. RELATIONSHIP DIAGRAM")
    print("-" * 40)
    print(
        """
    ┌─────────────────────────────────────────────────────────────┐
    │                  LEGACY ETL RELATIONSHIPS                    │
    └─────────────────────────────────────────────────────────────┘
    
                        dim_iniciativa_unificada
                               (2,005)
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
          ▼                       ▼                       ▼
    ┌───────────┐          ┌───────────┐          ┌───────────┐
    │ CONVENIOS │◄────────►│   IDIS    │◄────────►│   FRIL    │
    │   (533)   │  1,528   │  (3,622)  │   links  │   (167)   │
    └─────┬─────┘ matches  └─────┬─────┘          └───────────┘
          │                      │
          ▼                      ▼
    ┌───────────┐          ┌───────────┐
    │ dim_inst  │          │ fact_ejec │
    │   (150)   │          │  (3,496)  │
    └───────────┘          └───────────┘
          │
          │  normalize
          ▼
    ┌─────────────────────────────────────┐
    │     dim_institucion_unificada       │
    │            (1,692)                  │
    │  ┌─────────────┬───────────────┐    │
    │  │ CONVENIOS   │    PROGS      │    │
    │  │    (150)    │   (1,542)     │    │
    └──┴─────────────┴───────────────┴────┘
    
    ┌─────────────────────────────────────┐
    │       dim_territorio_canonico       │
    │            (23 comunas)             │
    │  DIGUILLÍN(9) + ITATA(7) + PUNILLA(5) + REGIONAL(2) │
    └─────────────────────────────────────┘
    
    ┌─────────────────────────────────────┐
    │      DOCUMENTOS STANDALONE          │
    │  ┌─────────────┬───────────────┐    │
    │  │MODIFICACIONES│   PARTES     │    │
    │  │    (255)    │   (10,413)   │    │
    └──┴─────────────┴───────────────┴────┘
    
    ┌─────────────────────────────────────┐
    │      RENDICIONES 8% (PROGS)         │
    │         (1,570 rendiciones)          │
    │   7 fondos: SEGURIDAD, DEPORTE...   │
    └─────────────────────────────────────┘
    """
    )

    # Write report to file
    report_path = OUTPUT_DIR / "relationship_summary.txt"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("LEGACY ETL - COMPLETE RELATIONSHIP MAP\n")
        f.write("=" * 60 + "\n\n")

        f.write("1. NORMALIZED DATA COUNTS\n")
        f.write("-" * 40 + "\n")
        for table, count in sorted(counts.items()):
            f.write(f"  {table}: {count:,}\n")

        f.write("\n2. UNIFIED INICIATIVAS\n")
        f.write("-" * 40 + "\n")
        f.write(f"  Total: {ini_stats['total']:,}\n")
        f.write(f"  Cross-linked: {ini_stats['multi_source']:,}\n")

        f.write("\n3. CROSS-DOMAIN MATCHES\n")
        f.write("-" * 40 + "\n")
        for pair, count in sorted(match_stats["by_pair"].items()):
            f.write(f"  {pair[0]} <-> {pair[1]}: {count:,}\n")

    print(f"\nReport written to: {report_path}")


def main():
    generate_report()


if __name__ == "__main__":
    main()
