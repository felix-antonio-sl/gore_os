"""
MODIFICACIONES normalizer - Fixed version.
Handles non-standard CSV format with headers not in first row.
"""

import csv
import uuid
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from common import (
    parse_amount,
    normalize_text,
)


SOURCES_DIR = Path(__file__).parent.parent / "sources" / "modificaciones" / "originales"
OUTPUT_DIR = Path(__file__).parent.parent / "normalized"


@dataclass
class FactModificacion:
    id: str
    subtitulo: Optional[str]
    item: Optional[str]
    asignacion: Optional[str]
    denominacion: Optional[str]
    distribucion_inicial: Optional[float]
    ppto_vigente_anterior: Optional[float]
    modificacion: Optional[float]
    ppto_vigente_final: Optional[float]
    numero_modificacion: int
    tipo_bloque: str  # INGRESOS / GASTOS
    vigente: bool  # False if "SIN EFECTO"
    origen_hoja: str
    fila_origen: int


class ModificacionesNormalizer:
    def __init__(self):
        self.facts: List[FactModificacion] = []
        self.errors: List[Dict] = []

    def _extract_num_modificacion(
        self, filename: str, content_rows: List[str] = None
    ) -> int:
        """Extract modification number from filename or content header."""
        # 1. Try filename
        match = re.search(r"N[°ºoO]\s*(\d+)", filename, re.IGNORECASE)
        if match:
            return int(match.group(1))

        # 2. Try content headers (first 20 rows)
        if content_rows:
            for row in content_rows[:20]:
                text = "|".join(str(c) for c in row).upper()
                match = re.search(r"MODIFICACIÓN.*N[°ºoO]\s*(\d+)", text)
                if match:
                    return int(match.group(1))
        return 0

    def _is_sin_efecto(self, filename: str) -> bool:
        """Check if sheet is marked as 'SIN EFECTO'."""
        return "SIN EFECTO" in filename.upper()

    def _find_header_row(self, rows: List[List[str]]) -> int:
        """Find the row containing 'SUBT' header."""
        for i, row in enumerate(rows):
            for cell in row:
                if cell and "SUBT" in str(cell).upper():
                    return i
        return -1

    def _find_column_indices(
        self, header_row: List[str], num_mod: int
    ) -> Dict[str, int]:
        """Find column indices."""
        indices = {}
        header_upper = [str(c).upper().strip() for c in header_row]

        for i, cell in enumerate(header_upper):
            if "SUBT" in cell:
                indices["subt"] = i
            elif cell == "ITEM":
                indices["item"] = i
            elif "ASIG" in cell:
                indices["asig"] = i
            elif "DENOMINAC" in cell:
                indices["denom"] = i
            elif "DISTRIBUCIÓN INICIAL" in cell:
                indices["inicial"] = i
            elif "VIGENTE CON MODIF" in cell or "ANTERIORES" in cell:
                indices["anterior"] = i
            elif "INCLUYE PRESENTE" in cell or "PPTO. VIGENTE" in cell:
                # Prioritize final balance
                indices["final"] = i

            # Smart detection of Modification Column
            # If we know the mod number, look for it specifically
            elif "MODIFICACIÓN" in cell and "M$" in cell:
                # If specifically naming this mod: "MODIFICACIÓN N°9 M$"
                if num_mod > 0 and str(num_mod) in cell:
                    indices["mod"] = i
                # Fallback if no specific mod column found yet
                elif "mod" not in indices:
                    indices["mod"] = i

        return indices

    def process_csv(self, filepath: Path):
        """Process a single MODIFICACIONES CSV file."""
        # Read all rows first
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            all_rows = list(reader)

        if not all_rows:
            return

        # Extract metadata
        num_mod = self._extract_num_modificacion(filepath.name, all_rows)
        sin_efecto = self._is_sin_efecto(filepath.name)

        print(f"Processing: {filepath.name} (mod={num_mod}, vigente={not sin_efecto})")

        # Find header row
        header_idx = self._find_header_row(all_rows)
        if header_idx < 0:
            print(f"  ⚠️ Could not find header row with SUBT")
            return

        header_row = all_rows[header_idx]
        indices = self._find_column_indices(header_row, num_mod)

        if "subt" not in indices:
            print(f"  ⚠️ Could not find SUBT column")
            return

        # Process data rows
        current_subt = None
        current_item = None
        current_bloque = "GASTOS"

        for row_idx in range(header_idx + 1, len(all_rows)):
            row = all_rows[row_idx]

            # Pad row
            max_idx = max(indices.values()) if indices else 0
            while len(row) <= max_idx:
                row.append("")

            # Get denomination
            denom_idx = indices.get("denom", indices.get("subt", 0) + 3)
            denom = normalize_text(row[denom_idx] if denom_idx < len(row) else "")

            # Track block type
            if denom == "INGRESOS":
                current_bloque = "INGRESOS"
                continue
            if denom == "GASTOS":
                current_bloque = "GASTOS"
                continue
            if denom in ("TOTAL", "TOTAL GASTOS", "TOTAL INGRESOS", "", None):
                continue

            # Safe Get
            def get_val(key):
                if key not in indices:
                    return None
                idx = indices[key]
                val = row[idx]
                return val if idx < len(row) else None

            # Check if MODIFICATION amount is valid. If it is, we accept the row even if others are REF.
            # If MOD itself is REF, we interpret as 0 or skip? Usually 0.
            mod_val = get_val("mod")
            if mod_val and "#REF!" in str(mod_val):
                self.errors.append(
                    {
                        "file": filepath.name,
                        "row": row_idx + 1,
                        "error": "#REF! in Mod Amount",
                    }
                )
                continue  # Cannot trust the mod amount

            # If subt/item/asig has REF, we might have issues tracking hierarchy.
            subt_raw = normalize_text(get_val("subt"))
            if subt_raw and "#REF!" in subt_raw:
                continue

            # Extract hierarchy
            item_raw = normalize_text(get_val("item"))
            asig_raw = normalize_text(get_val("asig"))

            if subt_raw and subt_raw.isdigit():
                current_subt = subt_raw
                current_item = None
            if item_raw and item_raw.isdigit():
                current_item = item_raw

            subt = current_subt
            item = current_item
            asig = asig_raw if asig_raw and asig_raw not in ("-", "") else None

            # Parse amounts (handle REF as None)
            def safe_amount(val):
                if not val or "#REF!" in str(val):
                    return None
                return parse_amount(val)

            inicial = safe_amount(get_val("inicial"))
            anterior = safe_amount(get_val("anterior"))
            mod = safe_amount(mod_val)
            final = safe_amount(get_val("final"))

            # Save if meaningful
            if subt or item or asig or (denom and "TRANSFERENCIAS" not in denom):
                self.facts.append(
                    FactModificacion(
                        id=str(uuid.uuid4()),
                        subtitulo=subt,
                        item=item,
                        asignacion=asig,
                        denominacion=denom,
                        distribucion_inicial=float(inicial) if inicial else None,
                        ppto_vigente_anterior=float(anterior) if anterior else None,
                        modificacion=float(mod) if mod else None,
                        ppto_vigente_final=float(final) if final else None,
                        numero_modificacion=num_mod,
                        tipo_bloque=current_bloque,
                        vigente=not sin_efecto,
                        origen_hoja=filepath.name,
                        fila_origen=row_idx + 1,
                    )
                )

    def write_outputs(self):
        """Write normalized outputs."""
        self._write_csv(
            OUTPUT_DIR / "facts" / "fact_modificacion.csv",
            [asdict(f) for f in self.facts],
        )

        # Write errors report
        if self.errors:
            self._write_csv(
                OUTPUT_DIR / "metadata" / "modificaciones_errors.csv", self.errors
            )

        print(f"\nMODIFICACIONES outputs written to {OUTPUT_DIR}")
        print(f"  Records: {len(self.facts)}")
        print(f"  Errors: {len(self.errors)}")

        # Count by modification number
        by_mod = {}
        for f in self.facts:
            key = f"{f.numero_modificacion}{'*' if not f.vigente else ''}"
            by_mod[key] = by_mod.get(key, 0) + 1
        for mod, count in sorted(
            by_mod.items(), key=lambda x: (x[0].replace("*", ""), x[0])
        ):
            print(f"    Mod #{mod}: {count}")

    def _write_csv(self, filepath: Path, data: List[Dict[str, Any]]):
        """Write data to CSV file."""
        if not data:
            return

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)


def main():
    normalizer = ModificacionesNormalizer()

    if SOURCES_DIR.exists():
        for csv_file in sorted(SOURCES_DIR.glob("*.csv")):
            normalizer.process_csv(csv_file)
    else:
        print(f"Source directory not found: {SOURCES_DIR}")
        return

    normalizer.write_outputs()


if __name__ == "__main__":
    main()
