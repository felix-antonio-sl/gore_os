"""
Territory and Institution linker.
Links entities across domains by normalizing territory and institution names.
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict
import uuid

from common import normalize_comuna, normalize_provincia, normalize_text


NORMALIZED_DIR = Path(__file__).parent.parent / "normalized"
OUTPUT_DIR = NORMALIZED_DIR / "relationships"


class TerritoryLinker:
    """Links territories (comuna/provincia) across domains."""

    def __init__(self):
        # Canonical territories
        self.comunas: Dict[str, Dict] = {}
        self.provincias: Dict[str, str] = {
            "DIGUILLÍN": "DIGUILLÍN",
            "ITATA": "ITATA",
            "PUNILLA": "PUNILLA",
        }

        # Maps normalized name -> canonical id
        self.comuna_lookup: Dict[str, str] = {}

        self._init_canonical_territories()

    def _init_canonical_territories(self):
        """Initialize canonical territory catalog for Ñuble region."""
        # Official comunas with provinces
        comunas_data = [
            # Diguillín
            ("BULNES", "DIGUILLÍN"),
            ("CHILLÁN", "DIGUILLÍN"),
            ("CHILLÁN VIEJO", "DIGUILLÍN"),
            ("EL CARMEN", "DIGUILLÍN"),
            ("PEMUCO", "DIGUILLÍN"),
            ("PINTO", "DIGUILLÍN"),
            ("QUILLÓN", "DIGUILLÍN"),
            ("SAN IGNACIO", "DIGUILLÍN"),
            ("YUNGAY", "DIGUILLÍN"),
            # Itata
            ("COBQUECURA", "ITATA"),
            ("COELEMU", "ITATA"),
            ("NINHUE", "ITATA"),
            ("PORTEZUELO", "ITATA"),
            ("QUIRIHUE", "ITATA"),
            ("RÁNQUIL", "ITATA"),
            ("TREGUACO", "ITATA"),
            # Punilla
            ("COIHUECO", "PUNILLA"),
            ("ÑIQUÉN", "PUNILLA"),
            ("SAN CARLOS", "PUNILLA"),
            ("SAN FABIÁN", "PUNILLA"),
            ("SAN NICOLÁS", "PUNILLA"),
            # Special
            ("REGIONAL", "REGIONAL"),
            ("INTERCOMUNAL", "REGIONAL"),
        ]

        for comuna, provincia in comunas_data:
            comuna_id = str(uuid.uuid4())
            self.comunas[comuna] = {
                "id": comuna_id,
                "nombre_oficial": comuna,
                "provincia": provincia,
                "region": "ÑUBLE",
            }
            self.comuna_lookup[comuna] = comuna_id

            # Add common variants
            self.comuna_lookup[
                comuna.replace("Á", "A")
                .replace("É", "E")
                .replace("Í", "I")
                .replace("Ó", "O")
                .replace("Ú", "U")
                .replace("Ñ", "N")
            ] = comuna_id

    def link_record(
        self, comuna_raw: Optional[str], provincia_raw: Optional[str] = None
    ) -> Optional[str]:
        """Link a record's territory to canonical comuna."""
        if not comuna_raw:
            return None

        comuna_norm = normalize_comuna(comuna_raw) or normalize_text(comuna_raw)
        if not comuna_norm:
            return None

        # Direct lookup
        if comuna_norm in self.comuna_lookup:
            return self.comuna_lookup[comuna_norm]

        # Try without accents
        comuna_ascii = (
            comuna_norm.replace("Á", "A")
            .replace("É", "E")
            .replace("Í", "I")
            .replace("Ó", "O")
            .replace("Ú", "U")
            .replace("Ñ", "N")
        )
        if comuna_ascii in self.comuna_lookup:
            return self.comuna_lookup[comuna_ascii]

        return None

    def write_catalog(self):
        """Write canonical territory catalog."""
        filepath = NORMALIZED_DIR / "dimensions" / "dim_territorio_canonico.csv"
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = list(self.comunas.values())
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["id", "nombre_oficial", "provincia", "region"]
            )
            writer.writeheader()
            writer.writerows(data)

        print(
            f"  Wrote {len(data)} canonical territories to dim_territorio_canonico.csv"
        )
        return data


class InstitutionLinker:
    """Links institutions across domains by normalizing names and RUTs."""

    def __init__(self):
        # RUT -> canonical record
        self.by_rut: Dict[str, Dict] = {}
        # Normalized name -> canonical record
        self.by_name: Dict[str, Dict] = {}
        # All institutions
        self.institutions: Dict[str, Dict] = {}

    def _normalize_institution_name(self, name: Optional[str]) -> Optional[str]:
        """Normalize institution name for matching."""
        if not name:
            return None

        name = normalize_text(name)
        if not name:
            return None

        # Remove common prefixes/suffixes
        name = re.sub(r"^(ILUSTRE\s+)?MUNICIPALIDAD\s+(DE\s+)?", "MUNI ", name)
        name = re.sub(r"^JUNTA\s+DE\s+VECINOS\s+", "JV ", name)
        name = re.sub(r"^CLUB\s+DEPORTIVO\s+", "CD ", name)
        name = re.sub(r"^COMITE\s+CAMPESINO\s+", "CC ", name)
        name = re.sub(r"^ASOCIACION\s+(DE\s+)?", "ASOC ", name)

        # Remove extra spaces
        name = " ".join(name.split())

        return name

    def add_from_convenios(self, filepath: Path):
        """Add institutions from dim_institucion."""
        if not filepath.exists():
            return

        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("unidad_tecnica_norm") or row.get("unidad_tecnica_raw")
                rut = row.get("rut")

                if not name:
                    continue

                inst_id = row.get("id") or str(uuid.uuid4())
                norm_name = self._normalize_institution_name(name)

                record = {
                    "id": inst_id,
                    "nombre_original": name,
                    "nombre_normalizado": norm_name,
                    "rut": rut,
                    "fuente": "CONVENIOS",
                }

                if rut and rut not in self.by_rut:
                    self.by_rut[rut] = record

                if norm_name and norm_name not in self.by_name:
                    self.by_name[norm_name] = record

                self.institutions[inst_id] = record

    def add_from_progs(self, filepath: Path):
        """Add institutions from fact_rendicion_8pct."""
        if not filepath.exists():
            return

        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("nombre_institucion")
                rut = row.get("rut_institucion")

                if not name:
                    continue

                norm_name = self._normalize_institution_name(name)

                # Check if we already have this by RUT
                if rut and rut in self.by_rut:
                    continue

                # Check if we already have this by name
                if norm_name and norm_name in self.by_name:
                    continue

                inst_id = str(uuid.uuid4())
                record = {
                    "id": inst_id,
                    "nombre_original": name,
                    "nombre_normalizado": norm_name,
                    "rut": rut,
                    "fuente": "PROGS",
                }

                if rut:
                    self.by_rut[rut] = record
                if norm_name:
                    self.by_name[norm_name] = record

                self.institutions[inst_id] = record

    def write_catalog(self):
        """Write unified institution catalog."""
        filepath = NORMALIZED_DIR / "dimensions" / "dim_institucion_unificada.csv"
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = list(self.institutions.values())
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "id",
                    "nombre_original",
                    "nombre_normalizado",
                    "rut",
                    "fuente",
                ],
            )
            writer.writeheader()
            writer.writerows(data)

        print(
            f"  Wrote {len(data)} unified institutions to dim_institucion_unificada.csv"
        )

        # Stats by source
        by_source = defaultdict(int)
        for r in data:
            by_source[r["fuente"]] += 1
        for source, count in sorted(by_source.items()):
            print(f"    From {source}: {count}")

        return data


def main():
    print("=" * 60)
    print("Territory and Institution Linking")
    print("=" * 60)

    # Territory linking
    print("\n1. Building canonical territory catalog...")
    territory_linker = TerritoryLinker()
    territory_linker.write_catalog()

    # Institution linking
    print("\n2. Building unified institution catalog...")
    institution_linker = InstitutionLinker()

    # Load from various sources
    institution_linker.add_from_convenios(
        NORMALIZED_DIR / "dimensions" / "dim_institucion.csv"
    )
    institution_linker.add_from_progs(
        NORMALIZED_DIR / "facts" / "fact_rendicion_8pct.csv"
    )
    institution_linker.write_catalog()

    print("\nDone!")


if __name__ == "__main__":
    main()
