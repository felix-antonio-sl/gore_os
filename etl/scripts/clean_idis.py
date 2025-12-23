#!/usr/bin/env python3
"""
IDIS Source Remediation Script
Cleans IDIS data by using only ANÁLISIS.csv (cleanest source),
removing #REF! errors, and deduplicating by codigo_bip.

Output: etl/sources/idis/cleaned/idis_cleaned.csv
"""
import csv
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def is_ref_error(value: str) -> bool:
    """Check if value is a #REF! error."""
    if not value:
        return False
    return "#REF!" in str(value) or "#N/A" in str(value) or "#VALUE!" in str(value)


def clean_value(value: str) -> str:
    """Clean a cell value, replacing errors with empty string."""
    if not value:
        return ""
    if is_ref_error(value):
        return ""
    return value.strip()


def extract_bip_code(row: dict) -> str:
    """Extract BIP code from row."""
    for key in ["BIP", "CODIGO BIP", "Codigo BIP", "COD. ÚNICO"]:
        if key in row and row[key]:
            return clean_value(row[key])
    return ""


def main():
    base_path = Path(__file__).parent.parent.parent
    source_path = base_path / "etl" / "sources" / "idis" / "originales"
    output_path = base_path / "etl" / "sources" / "idis" / "cleaned"

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Use only ANÁLISIS.csv - the cleanest source
    analisis_file = source_path / "ANÁLISIS.csv"

    if not analisis_file.exists():
        print(f"❌ Error: {analisis_file} not found")
        return

    print(f"📊 Processing: {analisis_file.name}")
    print("-" * 60)

    # Track statistics
    stats = {
        "total_rows": 0,
        "ref_errors": 0,
        "duplicates": 0,
        "clean_rows": 0,
        "null_bip": 0,
    }

    # Dictionary to track BIP codes (for dedup)
    seen_bips = {}
    clean_rows = []

    # Define columns to keep
    key_columns = [
        "COD. ÚNICO",
        "VIGENCIA",
        "AÑO",
        "AÑO PRESP.",
        "BIP",
        "DV",
        "NOMBRE INICIATIVA",
        "TIPO",
        "PROVINCIA",
        "COMUNA",
        "ETAPA",
        "TIPOLOGÍA",
        "Categoría GORE",
        "SUBT",
        "ITEM",
        "ASIG",
        "FORMULADOR",
        "ORIGEN",
        "UNIDAD TÉCNICA",
        "DIVISIÓN VINCULADA",
        "MONTO INICIATIVA",
        "MONTO FNDR",
        "MONTO FINAL APROB.",
        "GASTO VIGENTE",
        "ESTADO ACTUAL",
        "FECHA ESTADO ACTUAL",
        "RATE ACTUAL",
        "FECHA ULTIMO RATE",
        "OBSERVACIONES GENERALES",
    ]

    with open(analisis_file, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)

        for row in reader:
            stats["total_rows"] += 1

            # Extract BIP code
            bip = extract_bip_code(row)

            # Skip rows without BIP
            if not bip:
                stats["null_bip"] += 1
                continue

            # Count #REF! errors in this row
            ref_count = sum(
                1 for v in row.values() if is_ref_error(str(v) if v else "")
            )
            if ref_count > 0:
                stats["ref_errors"] += 1

            # Skip rows with >50% #REF! errors
            total_cols = len(row)
            if ref_count > total_cols * 0.5:
                continue

            # Deduplicate by BIP (keep first occurrence)
            if bip in seen_bips:
                stats["duplicates"] += 1
                continue

            seen_bips[bip] = True

            # Clean the row
            clean_row = {}
            for col in key_columns:
                if col in row:
                    clean_row[col] = clean_value(row.get(col, ""))

            # Add source metadata
            clean_row["_source_file"] = "ANÁLISIS.csv"
            clean_row["_cleaned_at"] = datetime.now().isoformat()

            clean_rows.append(clean_row)
            stats["clean_rows"] += 1

    # Write cleaned data
    output_file = output_path / "idis_cleaned.csv"

    if clean_rows:
        fieldnames = list(clean_rows[0].keys())

        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(clean_rows)

        print(f"\n✅ Cleaned data saved to: {output_file}")

    # Print statistics
    print("\n" + "=" * 60)
    print("📋 IDIS REMEDIATION REPORT")
    print("=" * 60)
    print(f"  Total rows processed: {stats['total_rows']}")
    print(f"  Rows with #REF! errors: {stats['ref_errors']}")
    print(f"  Duplicates removed: {stats['duplicates']}")
    print(f"  Rows without BIP: {stats['null_bip']}")
    print(f"  Clean rows output: {stats['clean_rows']}")
    print()

    # Quality improvement
    if stats["total_rows"] > 0:
        original_quality = (
            (stats["total_rows"] - stats["ref_errors"]) / stats["total_rows"] * 100
        )
        new_quality = 100  # All clean rows are now error-free
        print(f"  📈 Quality improvement: {original_quality:.1f}% → {new_quality:.1f}%")

    print("=" * 60)


if __name__ == "__main__":
    main()
