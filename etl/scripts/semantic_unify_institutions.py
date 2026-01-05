import csv
import re
import uuid
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import unicodedata

# Paths
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / "normalized" / "dimensions" / "dim_institucion_unificada.csv"
OUTPUT_DIM = BASE_DIR / "normalized" / "dimensions" / "dim_institucion_convergente.csv"
OUTPUT_MAP = BASE_DIR / "normalized" / "relationships" / "institution_semantic_map.csv"

# Normalization constants
STOPWORDS = {"DE", "LA", "EL", "Y", "EN", "POR", "CON", "PARA", "DEL", "LOS", "LAS"}
REPLACEMENTS = {
    r"\bAGRUPACION\b": "AGR",
    r"\bAGRUPACIÓN\b": "AGR",
    r"\bCLUB DEPORTIVO\b": "CD",
    r"\bC\.D\.\b": "CD",
    r"\bCD\b": "CD",
    r"\bJUNTA DE VECINOS\b": "JJVV",
    r"\bJJ\.VV\.\b": "JJVV",
    r"\bJJVV\b": "JJVV",
    r"\bMUNICIPALIDAD DE\b": "MUNI",
    r"\bI\. MUNICIPALIDAD DE\b": "MUNI",
    r"\bMUN\.\b": "MUNI",
    r"\bMUNI\b": "MUNI",
    r"\bILUSTRE MUNICIPALIDAD DE\b": "MUNI",
}


def normalize_text(text: str) -> str:
    """Aggressive normalization for semantic grouping."""
    if not text:
        return ""
    # To uppercase and remove accents
    text = "".join(
        c
        for c in unicodedata.normalize("NFD", text.upper())
        if unicodedata.category(c) != "Mn"
    )
    # Custom replacements
    for pattern, replacement in REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text)
    # Remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)
    # Remove stopwords and extra spaces
    tokens = [t for t in text.split() if t not in STOPWORDS]
    return " ".join(tokens)


def get_tokens(text: str) -> Tuple[str, ...]:
    """Get sorted tuple of tokens for order-independent matching."""
    return tuple(sorted(text.split()))


from difflib import SequenceMatcher


def fuzzy_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def semantic_unify():
    print("=" * 60)
    print("SEMANTIC INSTITUTION UNIFICATION (FUZZY)")
    print("=" * 60)

    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} not found.")
        return

    institutions = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["norm"] = normalize_text(row["nombre_original"])
            row["tokens"] = set(get_tokens(row["norm"]))
            institutions.append(row)

    print(f"Initial institutions: {len(institutions)}")

    canonical_map = {}  # old_id -> new_id
    canonical_records = []

    # Sort institutions by name length to pick solid ones first
    institutions.sort(key=lambda x: len(x["nombre_original"]), reverse=True)

    processed_ids = set()

    for i, inst in enumerate(institutions):
        if inst["id"] in processed_ids:
            continue

        canonical_id = inst["id"]
        processed_ids.add(canonical_id)
        canonical_map[canonical_id] = canonical_id

        # Current info
        norm_a = inst["norm"]
        tokens_a = inst["tokens"]
        rut_a = inst.get("rut", "").strip()

        # Compare with remaining
        for j in range(i + 1, len(institutions)):
            other = institutions[j]
            if other["id"] in processed_ids:
                continue

            norm_b = other["norm"]
            tokens_b = other["tokens"]
            rut_b = other.get("rut", "").strip()

            is_match = False

            # Rule 1: Same RUT (if exists)
            if rut_a and rut_b and rut_a != "-" and rut_b != "-" and rut_a == rut_b:
                is_match = True

            # Rule 2: Identical Tokens
            elif tokens_a and tokens_b and tokens_a == tokens_b:
                is_match = True

            # Rule 3: High Token Jaccard Similarity (> 0.8)
            elif tokens_a and tokens_b:
                intersection = len(tokens_a & tokens_b)
                union = len(tokens_a | tokens_b)
                if intersection / union >= 0.8:
                    is_match = True

            # Rule 4: Very high string ratio (> 0.95)
            elif norm_a and norm_b and fuzzy_ratio(norm_a, norm_b) > 0.95:
                is_match = True

            if is_match:
                canonical_map[other["id"]] = canonical_id
                processed_ids.add(other["id"])

        canonical_records.append(
            {
                "id": canonical_id,
                "nombre_original": inst["nombre_original"],
                "nombre_normalizado": inst["nombre_normalizado"],
                "rut": inst.get("rut", ""),
                "fuente_original": inst["fuente"],
            }
        )

    print(f"Unified institutions: {len(canonical_records)}")
    print(f"Reduction: {len(institutions) - len(canonical_records)} duplicates removed")

    # Save Mapping
    OUTPUT_MAP.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MAP, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["original_id", "canonical_id"])
        for old_id, new_id in canonical_map.items():
            writer.writerow([old_id, new_id])

    # Save Canonical Dimension
    with open(OUTPUT_DIM, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "id",
            "nombre_original",
            "nombre_normalizado",
            "rut",
            "fuente_original",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in canonical_records:
            writer.writerow(rec)

    print(f"Saved: {OUTPUT_DIM}")
    print(f"Saved: {OUTPUT_MAP}")


if __name__ == "__main__":
    semantic_unify()
