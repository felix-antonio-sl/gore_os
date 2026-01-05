"""
Cross-Domain Relationship Matrix Generator
Analyzes ALL 77+ CSV source files and generates an NxN adjacency matrix
showing relationships between every pair of files based on shared keys.

Keys analyzed:
- codigo/cod_unico (initiative codes)
- rut (institution/person identifiers)
- comuna (territory)
- nombre (entity names)
"""

import csv
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, asdict
import uuid


SOURCES_DIR = Path(__file__).parent.parent / "sources"
OUTPUT_DIR = Path(__file__).parent.parent / "normalized"
RELATIONSHIPS_DIR = OUTPUT_DIR / "relationships"


@dataclass
class FileProfile:
    """Profile of a source file with extracted key sets."""

    file_path: str
    domain: str
    file_name: str
    row_count: int
    columns: List[str]
    # Key sets
    codigos: Set[str]
    ruts: Set[str]
    comunas: Set[str]
    nombres: Set[str]
    # Column presence
    has_codigo: bool
    has_rut: bool
    has_comuna: bool
    has_nombre: bool


@dataclass
class RelationshipCell:
    """A cell in the NxN matrix."""

    file_a: str
    file_b: str
    codigo_matches: int
    rut_matches: int
    comuna_matches: int
    nombre_matches: int
    total_matches: int
    relationship_strength: float  # 0.0 to 1.0


class MatrixGenerator:
    def __init__(self):
        self.profiles: Dict[str, FileProfile] = {}
        self.matrix: Dict[Tuple[str, str], RelationshipCell] = {}

    def _normalize_codigo(self, value: Optional[str]) -> Optional[str]:
        """Normalize codigo/cod_unico to base format."""
        if not value:
            return None
        value = str(value).strip().upper()
        # Remove year suffix (-2024, etc.)
        value = re.sub(r"-\d{4}$", "", value)
        value = value.rstrip("-")
        # Remove leading zeros for numeric codes
        if value.isdigit():
            value = str(int(value))
        return value if value and value != "-" else None

    def _normalize_rut(self, value: Optional[str]) -> Optional[str]:
        """Normalize RUT to clean format."""
        if not value:
            return None
        # Remove dots and spaces
        value = re.sub(r"[\s\.]", "", str(value)).upper()
        # Keep only digits and K
        value = re.sub(r"[^0-9K-]", "", value)
        return value if len(value) >= 7 else None

    def _normalize_comuna(self, value: Optional[str]) -> Optional[str]:
        """Normalize comuna name."""
        if not value:
            return None
        value = str(value).strip().upper()
        # Remove accents
        replacements = {"Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ñ": "N"}
        for k, v in replacements.items():
            value = value.replace(k, v)
        return value if value and value not in ("", "-", "N/A", "NA") else None

    def _normalize_nombre(self, value: Optional[str]) -> Optional[str]:
        """Normalize entity name for matching."""
        if not value:
            return None
        value = str(value).strip().upper()
        # Remove extra spaces
        value = " ".join(value.split())
        return value if len(value) >= 4 else None

    def _find_column(self, columns: List[str], patterns: List[str]) -> Optional[str]:
        """Find a column matching any of the patterns."""
        columns_upper = [c.upper() for c in columns]
        for pattern in patterns:
            for i, col in enumerate(columns_upper):
                if pattern.upper() in col:
                    return columns[i]
        return None

    def _profile_file(self, file_path: Path) -> Optional[FileProfile]:
        """Create a profile for a single CSV file."""
        try:
            with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
                # Try to detect header row
                sample = f.read(4096)
                f.seek(0)

                # Find header row (skip rows without tabular structure)
                reader = csv.reader(f)
                header = None
                rows_scanned = 0
                for row in reader:
                    rows_scanned += 1
                    if rows_scanned > 20:
                        break
                    # Check if this looks like a header (has multiple non-empty cells)
                    non_empty = [c for c in row if c.strip()]
                    if len(non_empty) >= 3:
                        header = row
                        break

                if not header:
                    return None

                # Identify key columns
                col_codigo = self._find_column(
                    header, ["CÓDIGO", "CODIGO", "COD_UNICO", "COD ÚNICO", "CODIGO_BIP"]
                )
                col_rut = self._find_column(
                    header, ["RUT", "RUT INSTITUCIÓN", "RUT INSTITUCION"]
                )
                col_comuna = self._find_column(header, ["COMUNA", "COMUNAS"])
                col_nombre = self._find_column(
                    header,
                    [
                        "NOMBRE",
                        "NOMBRE INSTITUCIÓN",
                        "NOMBRE INICIATIVA",
                        "NOMBRE COMPLETO",
                    ],
                )

                # Extract sets
                codigos: Set[str] = set()
                ruts: Set[str] = set()
                comunas: Set[str] = set()
                nombres: Set[str] = set()
                row_count = 0

                for row in reader:
                    row_count += 1
                    row_dict = dict(zip(header, row)) if len(row) == len(header) else {}

                    if col_codigo and col_codigo in row_dict:
                        normalized = self._normalize_codigo(row_dict[col_codigo])
                        if normalized:
                            codigos.add(normalized)

                    if col_rut and col_rut in row_dict:
                        normalized = self._normalize_rut(row_dict[col_rut])
                        if normalized:
                            ruts.add(normalized)

                    if col_comuna and col_comuna in row_dict:
                        normalized = self._normalize_comuna(row_dict[col_comuna])
                        if normalized:
                            comunas.add(normalized)

                    if col_nombre and col_nombre in row_dict:
                        normalized = self._normalize_nombre(row_dict[col_nombre])
                        if normalized:
                            nombres.add(normalized)

                    # Special extraction for PARTES (Documents) - Scan text for BIPs
                    # We check MATERIA, REFERENCIA, or similar text fields
                    partes_cols = ["MATERIA", "REFERENCIA", "DESCRIPCION", "ASUNTO"]
                    for p_col in partes_cols:
                        if p_col in row_dict:
                            text = row_dict[p_col]
                            # Regex for BIP: 6-8 digits, optional -K or -digit
                            # Avoid matching phone numbers or generic large numbers by ensuring boundaries
                            matches = re.findall(
                                r"\b(\d{7,8})(?:-[\dkK])?\b", str(text)
                            )
                            for m in matches:
                                # m is the captured group (digits only) or we might want the full match
                                # Let's accept the digits part as the normalized code
                                if self._normalize_codigo(m):
                                    codigos.add(self._normalize_codigo(m))

                # Domain from path
                rel_path = file_path.relative_to(SOURCES_DIR)
                domain = rel_path.parts[0] if rel_path.parts else "unknown"

                return FileProfile(
                    file_path=str(rel_path),
                    domain=domain.upper(),
                    file_name=file_path.name,
                    row_count=row_count,
                    columns=header,
                    codigos=codigos,
                    ruts=ruts,
                    comunas=comunas,
                    nombres=nombres,
                    has_codigo=col_codigo is not None,
                    has_rut=col_rut is not None,
                    has_comuna=col_comuna is not None,
                    has_nombre=col_nombre is not None,
                )

        except Exception as e:
            print(f"  Error profiling {file_path.name}: {e}")
            return None

    def scan_all_sources(self):
        """Scan all CSV files in sources directory."""
        print("=" * 60)
        print("SCANNING ALL SOURCE FILES")
        print("=" * 60)

        csv_files = list(SOURCES_DIR.rglob("*.csv"))
        print(f"Found {len(csv_files)} CSV files\n")

        for file_path in sorted(csv_files):
            # Skip cleaned/processed files
            if "cleaned" in str(file_path).lower():
                continue

            profile = self._profile_file(file_path)
            if profile and profile.row_count > 0:
                self.profiles[profile.file_path] = profile
                print(
                    f"  ✓ {profile.file_path}: {profile.row_count} rows, "
                    f"códigos={len(profile.codigos)}, ruts={len(profile.ruts)}, "
                    f"comunas={len(profile.comunas)}, nombres={len(profile.nombres)}"
                )

        print(f"\nProfiled {len(self.profiles)} files")

    def compute_matrix(self):
        """Compute the NxN relationship matrix."""
        print("\n" + "=" * 60)
        print("COMPUTING RELATIONSHIP MATRIX")
        print("=" * 60)

        file_keys = sorted(self.profiles.keys())
        n = len(file_keys)

        for i, file_a in enumerate(file_keys):
            profile_a = self.profiles[file_a]
            for j, file_b in enumerate(file_keys):
                if i >= j:  # Skip diagonal and lower triangle (symmetric)
                    continue

                profile_b = self.profiles[file_b]

                # Compute intersections
                codigo_matches = len(profile_a.codigos & profile_b.codigos)
                rut_matches = len(profile_a.ruts & profile_b.ruts)
                comuna_matches = len(profile_a.comunas & profile_b.comunas)
                nombre_matches = len(profile_a.nombres & profile_b.nombres)

                total = codigo_matches + rut_matches + comuna_matches + nombre_matches

                # Calculate strength (weighted)
                max_possible = max(
                    len(profile_a.codigos) + len(profile_b.codigos),
                    len(profile_a.ruts) + len(profile_b.ruts),
                    len(profile_a.comunas) + len(profile_b.comunas),
                    1,  # Avoid division by zero
                )
                strength = (
                    min(
                        1.0,
                        (codigo_matches * 3 + rut_matches * 2 + comuna_matches)
                        / max_possible,
                    )
                    if max_possible > 0
                    else 0.0
                )

                if total > 0:
                    cell = RelationshipCell(
                        file_a=file_a,
                        file_b=file_b,
                        codigo_matches=codigo_matches,
                        rut_matches=rut_matches,
                        comuna_matches=comuna_matches,
                        nombre_matches=nombre_matches,
                        total_matches=total,
                        relationship_strength=round(strength, 4),
                    )
                    self.matrix[(file_a, file_b)] = cell

        print(f"Computed {len(self.matrix)} non-zero relationships")

    def write_outputs(self):
        """Write matrix and profiles to files."""
        RELATIONSHIPS_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Write file inventory
        inventory_path = RELATIONSHIPS_DIR / "source_file_inventory.csv"
        with open(inventory_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "file_path",
                    "domain",
                    "file_name",
                    "row_count",
                    "num_codigos",
                    "num_ruts",
                    "num_comunas",
                    "num_nombres",
                    "has_codigo",
                    "has_rut",
                    "has_comuna",
                    "has_nombre",
                ]
            )
            for path, profile in sorted(self.profiles.items()):
                writer.writerow(
                    [
                        profile.file_path,
                        profile.domain,
                        profile.file_name,
                        profile.row_count,
                        len(profile.codigos),
                        len(profile.ruts),
                        len(profile.comunas),
                        len(profile.nombres),
                        profile.has_codigo,
                        profile.has_rut,
                        profile.has_comuna,
                        profile.has_nombre,
                    ]
                )
        print(f"Wrote {len(self.profiles)} file profiles to source_file_inventory.csv")

        # 2. Write relationship matrix as CSV
        matrix_csv_path = RELATIONSHIPS_DIR / "relationship_matrix.csv"
        with open(matrix_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "file_a",
                    "file_b",
                    "domain_a",
                    "domain_b",
                    "codigo_matches",
                    "rut_matches",
                    "comuna_matches",
                    "nombre_matches",
                    "total_matches",
                    "strength",
                ]
            )
            for (fa, fb), cell in sorted(
                self.matrix.items(), key=lambda x: -x[1].total_matches
            ):
                writer.writerow(
                    [
                        fa,
                        fb,
                        self.profiles[fa].domain,
                        self.profiles[fb].domain,
                        cell.codigo_matches,
                        cell.rut_matches,
                        cell.comuna_matches,
                        cell.nombre_matches,
                        cell.total_matches,
                        cell.relationship_strength,
                    ]
                )
        print(f"Wrote {len(self.matrix)} relationships to relationship_matrix.csv")

        # 3. Write matrix as JSON for visualization
        matrix_json_path = RELATIONSHIPS_DIR / "relationship_matrix.json"

        # Create adjacency matrix format
        file_keys = sorted(self.profiles.keys())
        file_to_idx = {f: i for i, f in enumerate(file_keys)}

        # Initialize NxN matrix with zeros
        n = len(file_keys)
        adj_matrix = [[0.0] * n for _ in range(n)]

        for (fa, fb), cell in self.matrix.items():
            i, j = file_to_idx[fa], file_to_idx[fb]
            adj_matrix[i][j] = cell.relationship_strength
            adj_matrix[j][i] = cell.relationship_strength  # Symmetric

        matrix_data = {
            "files": [
                {
                    "index": i,
                    "path": f,
                    "domain": self.profiles[f].domain,
                    "rows": self.profiles[f].row_count,
                }
                for i, f in enumerate(file_keys)
            ],
            "adjacency_matrix": adj_matrix,
            "relationships": [asdict(cell) for cell in self.matrix.values()],
        }

        with open(matrix_json_path, "w", encoding="utf-8") as f:
            json.dump(matrix_data, f, indent=2)
        print(f"Wrote matrix JSON to relationship_matrix.json")

        # 4. Write summary statistics
        self._write_summary()

    def _write_summary(self):
        """Write human-readable summary."""
        summary_path = RELATIONSHIPS_DIR / "matrix_summary.txt"

        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("LEGACY ETL - SOURCE FILE RELATIONSHIP MATRIX\n")
            f.write("=" * 70 + "\n\n")

            f.write("FILE INVENTORY BY DOMAIN\n")
            f.write("-" * 40 + "\n")
            by_domain = defaultdict(list)
            for path, profile in self.profiles.items():
                by_domain[profile.domain].append(profile)

            for domain, profiles in sorted(by_domain.items()):
                total_rows = sum(p.row_count for p in profiles)
                f.write(f"\n{domain} ({len(profiles)} files, {total_rows:,} rows):\n")
                for p in sorted(profiles, key=lambda x: -x.row_count):
                    f.write(f"  - {p.file_name}: {p.row_count:,} rows\n")

            f.write("\n\nTOP 20 STRONGEST RELATIONSHIPS\n")
            f.write("-" * 40 + "\n")
            top_rels = sorted(self.matrix.values(), key=lambda x: -x.total_matches)[:20]
            for i, cell in enumerate(top_rels, 1):
                f.write(
                    f"\n{i}. {Path(cell.file_a).name} <-> {Path(cell.file_b).name}\n"
                )
                f.write(
                    f"   Domains: {self.profiles[cell.file_a].domain} <-> {self.profiles[cell.file_b].domain}\n"
                )
                f.write(
                    f"   Matches: códigos={cell.codigo_matches}, ruts={cell.rut_matches}, "
                )
                f.write(
                    f"comunas={cell.comuna_matches}, nombres={cell.nombre_matches}\n"
                )
                f.write(f"   Strength: {cell.relationship_strength:.2%}\n")

            f.write("\n\nCROSS-DOMAIN CONNECTIONS\n")
            f.write("-" * 40 + "\n")
            cross_domain = defaultdict(int)
            for cell in self.matrix.values():
                da = self.profiles[cell.file_a].domain
                db = self.profiles[cell.file_b].domain
                if da != db:
                    pair = tuple(sorted([da, db]))
                    cross_domain[pair] += cell.total_matches

            for pair, count in sorted(cross_domain.items(), key=lambda x: -x[1]):
                f.write(f"  {pair[0]} <-> {pair[1]}: {count:,} total matches\n")

        print(f"Wrote summary to matrix_summary.txt")


def main():
    generator = MatrixGenerator()
    generator.scan_all_sources()
    generator.compute_matrix()
    generator.write_outputs()

    print("\n" + "=" * 60)
    print("MATRIX GENERATION COMPLETE")
    print("=" * 60)
    print(f"Files profiled: {len(generator.profiles)}")
    print(f"Relationships found: {len(generator.matrix)}")
    print(f"Outputs in: {RELATIONSHIPS_DIR}")


if __name__ == "__main__":
    main()
