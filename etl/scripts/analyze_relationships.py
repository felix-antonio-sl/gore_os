"""
Cross-domain relationship analyzer and linker.
Identifies and resolves relationships between normalized legacy domains.
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict
import uuid


NORMALIZED_DIR = Path(__file__).parent.parent / "normalized"
OUTPUT_DIR = NORMALIZED_DIR / "relationships"


@dataclass
class RelationshipMatch:
    source_domain: str
    source_id: str
    source_code: str
    target_domain: str
    target_id: str
    target_code: str
    match_type: str  # EXACT, NORMALIZED, FUZZY
    confidence: float


class RelationshipAnalyzer:
    def __init__(self):
        # Caches for loaded data
        self.convenios_iniciativas: Dict[str, Dict] = {}  # codigo -> record
        self.idis_iniciativas: Dict[str, Dict] = {}  # cod_unico_norm -> record
        self.fril_proyectos: Dict[str, Dict] = {}  # codigo -> record
        self.progs_rendiciones: Dict[str, Dict] = {}  # codigo -> record

        # Normalized code -> original code mapping
        self.code_mappings: Dict[str, List[Tuple[str, str, str]]] = defaultdict(list)

        # Matches found
        self.matches: List[RelationshipMatch] = []

        # Statistics
        self.stats = {
            "convenios_codes": 0,
            "idis_codes": 0,
            "fril_codes": 0,
            "progs_codes": 0,
            "matches_convenios_idis": 0,
            "matches_convenios_fril": 0,
            "matches_idis_fril": 0,
            "unmatched_convenios": 0,
            "unmatched_idis": 0,
        }

    def _normalize_code(self, code: Optional[str]) -> Optional[str]:
        """
        Normalize code to base format for matching.
        Removes year suffix, trailing dashes, and whitespace.
        Examples:
            40046207-2024 -> 40046207
            40046207- -> 40046207
            40046207 -> 40046207
        """
        if not code:
            return None

        # Strip whitespace
        code = str(code).strip()

        # Remove trailing year pattern (-2019, -2020, etc.)
        code = re.sub(r"-\d{4}$", "", code)

        # Remove trailing dash
        code = code.rstrip("-")

        # Remove leading zeros for numeric codes
        if code.isdigit():
            code = str(int(code))

        return code if code else None

    def _extract_bip(self, code: Optional[str]) -> Optional[str]:
        """Extract BIP code from various formats (e.g., 40046207 from 40046207-2024)."""
        if not code:
            return None

        # Pattern: XXXXXXXX or XXXXXXXX-YYYY
        match = re.match(r"^(\d{8})(?:-\d{4})?", str(code).strip())
        if match:
            return match.group(1)
        return None

    def load_data(self):
        """Load all normalized data."""
        print("Loading normalized data...")

        # Load CONVENIOS iniciativas
        dim_ini_path = NORMALIZED_DIR / "dimensions" / "dim_iniciativa.csv"
        if dim_ini_path.exists():
            with open(dim_ini_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = row.get("codigo")
                    if code:
                        self.convenios_iniciativas[code] = row
                        norm_code = self._normalize_code(code)
                        if norm_code:
                            self.code_mappings[norm_code].append(
                                ("CONVENIOS", row["id"], code)
                            )
        self.stats["convenios_codes"] = len(self.convenios_iniciativas)
        print(f"  Loaded {self.stats['convenios_codes']} CONVENIOS iniciativas")

        # Load IDIS iniciativas
        dim_idis_path = NORMALIZED_DIR / "dimensions" / "dim_iniciativa_idis.csv"
        if dim_idis_path.exists():
            with open(dim_idis_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = row.get("cod_unico")
                    if code:
                        self.idis_iniciativas[code] = row
                        norm_code = self._normalize_code(code)
                        if norm_code:
                            self.code_mappings[norm_code].append(
                                ("IDIS", row["id"], code)
                            )
                        # Also add BIP as lookup key
                        bip = row.get("bip")
                        if bip and bip != code:
                            norm_bip = self._normalize_code(bip)
                            if norm_bip:
                                self.code_mappings[norm_bip].append(
                                    ("IDIS_BIP", row["id"], bip)
                                )
        self.stats["idis_codes"] = len(self.idis_iniciativas)
        print(f"  Loaded {self.stats['idis_codes']} IDIS iniciativas")

        # Load FRIL projects
        fril_path = NORMALIZED_DIR / "facts" / "fact_fril.csv"
        if fril_path.exists():
            with open(fril_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = row.get("codigo")
                    if code:
                        self.fril_proyectos[code] = row
                        norm_code = self._normalize_code(code)
                        if norm_code:
                            self.code_mappings[norm_code].append(
                                ("FRIL", row["id"], code)
                            )
        self.stats["fril_codes"] = len(self.fril_proyectos)
        print(f"  Loaded {self.stats['fril_codes']} FRIL projects")

        # Load PROGS rendiciones
        progs_path = NORMALIZED_DIR / "facts" / "fact_rendicion_8pct.csv"
        if progs_path.exists():
            with open(progs_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = row.get("codigo")
                    if code:
                        self.progs_rendiciones[code] = row
                        norm_code = self._normalize_code(code)
                        if norm_code:
                            self.code_mappings[norm_code].append(
                                ("PROGS", row["id"], code)
                            )
        self.stats["progs_codes"] = len(self.progs_rendiciones)
        print(f"  Loaded {self.stats['progs_codes']} PROGS rendiciones")

    def find_matches(self):
        """Find all matches between domains based on normalized codes."""
        print("\nFinding cross-domain matches...")

        for norm_code, entries in self.code_mappings.items():
            if len(entries) <= 1:
                continue  # No cross-domain match possible

            # Group by domain
            by_domain = defaultdict(list)
            for domain, record_id, original_code in entries:
                by_domain[domain].append((record_id, original_code))

            domains = list(by_domain.keys())

            # Create matches for each pair of domains
            for i in range(len(domains)):
                for j in range(i + 1, len(domains)):
                    domain1, domain2 = domains[i], domains[j]

                    for id1, code1 in by_domain[domain1]:
                        for id2, code2 in by_domain[domain2]:
                            # Determine match type
                            if code1 == code2:
                                match_type = "EXACT"
                                confidence = 1.0
                            else:
                                match_type = "NORMALIZED"
                                confidence = 0.9

                            self.matches.append(
                                RelationshipMatch(
                                    source_domain=domain1,
                                    source_id=id1,
                                    source_code=code1,
                                    target_domain=domain2,
                                    target_id=id2,
                                    target_code=code2,
                                    match_type=match_type,
                                    confidence=confidence,
                                )
                            )

        # Count matches by domain pair
        match_pairs = defaultdict(int)
        for m in self.matches:
            pair = tuple(
                sorted([m.source_domain.split("_")[0], m.target_domain.split("_")[0]])
            )
            match_pairs[pair] += 1

        self.stats["matches_convenios_idis"] = match_pairs.get(("CONVENIOS", "IDIS"), 0)
        self.stats["matches_convenios_fril"] = match_pairs.get(("CONVENIOS", "FRIL"), 0)
        self.stats["matches_idis_fril"] = match_pairs.get(("FRIL", "IDIS"), 0)

        print(f"  Found {len(self.matches)} total matches")
        for pair, count in sorted(match_pairs.items()):
            print(f"    {pair[0]} <-> {pair[1]}: {count}")

    def build_unified_iniciativa(self):
        """Build unified iniciativa dimension combining all sources."""
        print("\nBuilding unified dim_iniciativa_unificada...")

        # Track which codes we've seen
        unified: Dict[str, Dict] = {}

        # Start with IDIS (most complete)
        for code, record in self.idis_iniciativas.items():
            norm_code = self._normalize_code(code)
            if norm_code and norm_code not in unified:
                unified[norm_code] = {
                    "id": str(uuid.uuid4()),
                    "codigo_normalizado": norm_code,
                    "cod_unico_idis": code,
                    "codigo_convenios": None,
                    "codigo_fril": None,
                    "codigo_progs": None,
                    "nombre_iniciativa": record.get("nombre_iniciativa"),
                    "bip": record.get("bip"),
                    "tipologia": record.get("tipologia"),
                    "etapa": record.get("etapa"),
                    "origen": record.get("origen"),
                    "unidad_tecnica": record.get("unidad_tecnica"),
                    "provincia": record.get("provincia"),
                    "comuna": record.get("comuna"),
                    "fuente_principal": "IDIS",
                }

        # Add CONVENIOS codes
        for code, record in self.convenios_iniciativas.items():
            norm_code = self._normalize_code(code)
            if norm_code:
                if norm_code in unified:
                    unified[norm_code]["codigo_convenios"] = code
                    # Fill gaps
                    if not unified[norm_code]["nombre_iniciativa"]:
                        unified[norm_code]["nombre_iniciativa"] = record.get(
                            "nombre_norm"
                        )
                else:
                    unified[norm_code] = {
                        "id": str(uuid.uuid4()),
                        "codigo_normalizado": norm_code,
                        "cod_unico_idis": None,
                        "codigo_convenios": code,
                        "codigo_fril": None,
                        "codigo_progs": None,
                        "nombre_iniciativa": record.get("nombre_norm"),
                        "bip": None,
                        "tipologia": None,
                        "etapa": None,
                        "origen": None,
                        "unidad_tecnica": None,
                        "provincia": None,
                        "comuna": None,
                        "fuente_principal": "CONVENIOS",
                    }

        # Add FRIL codes
        for code, record in self.fril_proyectos.items():
            norm_code = self._normalize_code(code)
            if norm_code:
                if norm_code in unified:
                    unified[norm_code]["codigo_fril"] = code
                    # Fill gaps
                    if not unified[norm_code]["nombre_iniciativa"]:
                        unified[norm_code]["nombre_iniciativa"] = record.get(
                            "nombre_iniciativa"
                        )
                    if not unified[norm_code]["comuna"]:
                        unified[norm_code]["comuna"] = record.get("comuna")
                else:
                    unified[norm_code] = {
                        "id": str(uuid.uuid4()),
                        "codigo_normalizado": norm_code,
                        "cod_unico_idis": None,
                        "codigo_convenios": None,
                        "codigo_fril": code,
                        "codigo_progs": None,
                        "nombre_iniciativa": record.get("nombre_iniciativa"),
                        "bip": None,
                        "tipologia": None,
                        "etapa": None,
                        "origen": None,
                        "unidad_tecnica": record.get("unidad_tecnica"),
                        "provincia": None,
                        "comuna": record.get("comuna"),
                        "fuente_principal": "FRIL",
                    }

        # PROGS uses different code universe (2401D0001, etc.) - don't merge
        # They're 8% FNDR social programs, not investment initiatives

        print(f"  Created {len(unified)} unified iniciativas")

        # Count by source
        by_source = defaultdict(int)
        for record in unified.values():
            by_source[record["fuente_principal"]] += 1
        for source, count in sorted(by_source.items()):
            print(f"    Primary from {source}: {count}")

        # Count overlaps
        overlaps = sum(
            1
            for r in unified.values()
            if sum(
                1
                for k in ["cod_unico_idis", "codigo_convenios", "codigo_fril"]
                if r.get(k)
            )
            > 1
        )
        print(f"    With cross-domain links: {overlaps}")

        return list(unified.values())

    def write_outputs(self, unified_iniciativas: List[Dict]):
        """Write relationship outputs."""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Write matches
        self._write_csv(
            OUTPUT_DIR / "cross_domain_matches.csv", [asdict(m) for m in self.matches]
        )

        # Write unified iniciativa dimension
        self._write_csv(
            NORMALIZED_DIR / "dimensions" / "dim_iniciativa_unificada.csv",
            unified_iniciativas,
        )

        # Write statistics
        with open(OUTPUT_DIR / "relationship_stats.txt", "w") as f:
            f.write("Cross-Domain Relationship Analysis\n")
            f.write("=" * 50 + "\n\n")
            f.write("Source Counts:\n")
            f.write(f"  CONVENIOS iniciativas: {self.stats['convenios_codes']}\n")
            f.write(f"  IDIS iniciativas: {self.stats['idis_codes']}\n")
            f.write(f"  FRIL projects: {self.stats['fril_codes']}\n")
            f.write(f"  PROGS rendiciones: {self.stats['progs_codes']}\n\n")
            f.write("Cross-Domain Matches:\n")
            f.write(f"  CONVENIOS <-> IDIS: {self.stats['matches_convenios_idis']}\n")
            f.write(f"  CONVENIOS <-> FRIL: {self.stats['matches_convenios_fril']}\n")
            f.write(f"  IDIS <-> FRIL: {self.stats['matches_idis_fril']}\n\n")
            f.write(f"Total matches: {len(self.matches)}\n")
            f.write(f"Unified iniciativas: {len(unified_iniciativas)}\n")

        print(f"\nOutputs written to {OUTPUT_DIR}")

    def _write_csv(self, filepath: Path, data: List[Dict]):
        """Write data to CSV file."""
        if not data:
            print(f"  Skipping {filepath.name} (no data)")
            return

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        print(f"  Wrote {len(data)} records to {filepath.name}")


def main():
    analyzer = RelationshipAnalyzer()
    analyzer.load_data()
    analyzer.find_matches()
    unified = analyzer.build_unified_iniciativa()
    analyzer.write_outputs(unified)


if __name__ == "__main__":
    main()
