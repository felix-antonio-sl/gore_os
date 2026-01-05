import csv
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
MAP_FILE = BASE_DIR / "normalized" / "relationships" / "institution_semantic_map.csv"
CONVERGENT_DIM = (
    BASE_DIR / "normalized" / "dimensions" / "dim_institucion_convergente.csv"
)
FINAL_DIM = BASE_DIR / "normalized" / "dimensions" / "dim_institucion_unificada.csv"

FACTS_DIR = BASE_DIR / "normalized" / "facts"
RELATIONSHIPS_DIR = BASE_DIR / "normalized" / "relationships"


def propagate():
    print("=" * 60)
    print("PROPAGATING CANONICAL IDS")
    print("=" * 60)

    # 1. Load Map
    if not MAP_FILE.exists():
        print(f"Error: {MAP_FILE} not found.")
        return

    id_map = {}
    with open(MAP_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["original_id"] != row["canonical_id"]:
                id_map[row["original_id"]] = row["canonical_id"]

    print(f"Loaded {len(id_map)} ID mappings.")

    # 2. Update dim_institucion_unificada (Replace with convergent)
    if CONVERGENT_DIM.exists():
        # Rename original columns to match if necessary, but here they are compatible
        os.replace(CONVERGENT_DIM, FINAL_DIM)
        print(f"Updated primary dimension: {FINAL_DIM}")

    # 3. Update Fact Tables
    for fact_file in FACTS_DIR.glob("*.csv"):
        # Only process if file has relevant columns
        temp_file = fact_file.with_suffix(".tmp")
        updated = False

        with open(fact_file, "r", encoding="utf-8") as fin, open(
            temp_file, "w", encoding="utf-8", newline=""
        ) as fout:

            reader = csv.reader(fin)
            writer = csv.writer(fout)

            header = next(reader, None)
            if not header:
                continue
            writer.writerow(header)

            # Find candidate columns for ID replacement
            id_cols = [
                i
                for i, col in enumerate(header)
                if "institucion_id" in col or "entidad_id" in col
            ]

            if not id_cols:
                # Still write the rest of the file
                for row in reader:
                    writer.writerow(row)
                continue

            for row in reader:
                for col_idx in id_cols:
                    if col_idx < len(row):
                        old_id = row[col_idx]
                        if old_id in id_map:
                            row[col_idx] = id_map[old_id]
                            updated = True
                writer.writerow(row)

        if updated:
            os.replace(temp_file, fact_file)
            print(f"  ✓ Updated IDs in {fact_file.name}")
        else:
            os.remove(temp_file)

    # 4. Update cross_domain_matches.csv
    match_file = RELATIONSHIPS_DIR / "cross_domain_matches.csv"
    if match_file.exists():
        temp_file = match_file.with_suffix(".tmp")
        updated = False
        with open(match_file, "r", encoding="utf-8") as fin, open(
            temp_file, "w", encoding="utf-8", newline=""
        ) as fout:

            reader = csv.DictReader(fin)
            writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
            writer.writeheader()

            for row in reader:
                # source_id or target_id might correspond to an institution
                if row["source_id"] in id_map:
                    row["source_id"] = id_map[row["source_id"]]
                    updated = True
                if row["target_id"] in id_map:
                    row["target_id"] = id_map[row["target_id"]]
                    updated = True
                writer.writerow(row)

        if updated:
            os.replace(temp_file, match_file)
            print(f"  ✓ Updated IDs in cross_domain_matches.csv")
        else:
            os.remove(temp_file)


if __name__ == "__main__":
    propagate()
