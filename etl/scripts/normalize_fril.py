"""
FRIL normalizer.
Unifies 6 operational sheets (31 and FRIL sources) into fact_linea_presupuestaria.
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
    normalize_comuna,
)


SOURCES_DIR = Path(__file__).parent.parent / "sources" / "fril" / "originales"
OUTPUT_DIR = Path(__file__).parent.parent / "normalized"


@dataclass
class FactFRIL:
    id: str
    codigo: Optional[str]
    nombre_iniciativa: Optional[str]
    comuna: Optional[str]
    unidad_tecnica: Optional[str]
    fuente: str  # '31' or 'FRIL'
    item_presupuestario: Optional[str]
    estado_iniciativa: Optional[str]
    subestado_iniciativa: Optional[str]
    saldo_2026: Optional[float]
    saldo_2027: Optional[float]
    categoria_hoja: str  # AVAN_ADJ, LIC_CON, PARA_REEVA_TER
    origen_hoja: str


class FRILNormalizer:
    def __init__(self):
        self.facts: List[FactFRIL] = []
        self.errors: List[Dict] = []

    def _detect_fuente_and_categoria(self, filename: str) -> tuple[str, str]:
        """Detect source (31/FRIL) and category from filename."""
        name = filename.upper()

        if name.startswith("31"):
            fuente = "31"
        elif name.startswith("FRIL"):
            fuente = "FRIL"
        else:
            fuente = "UNKNOWN"

        if "AVAN" in name and "ADJ" in name:
            categoria = "AVAN_ADJ"
        elif "LIC" in name and "CON" in name:
            categoria = "LIC_CON"
        elif "PARA" in name or "REEVA" in name or "TER" in name:
            categoria = "PARA_REEVA_TER"
        elif "TOTAL" in name:
            categoria = "RESUMEN"
        else:
            categoria = "OTRO"

        return fuente, categoria

    def _parse_codigo(self, value: Optional[str]) -> Optional[str]:
        """Parse and normalize project code."""
        if value is None:
            return None

        # Handle float codes from CSV (40055833.0 -> 40055833)
        try:
            if "." in str(value):
                code = str(int(float(value)))
            else:
                code = str(value).strip()

            if code == "" or code == "nan":
                return None

            return code
        except (ValueError, TypeError):
            return normalize_text(value)

    def _parse_saldo(self, value: Optional[str]) -> Optional[float]:
        """Parse monetary saldo value."""
        if value is None:
            return None

        # Handle "$ -" as zero/null
        cleaned = str(value).strip()
        if cleaned in ("$ -", "$-", "-", ""):
            return None

        amount = parse_amount(value)
        return float(amount) if amount else None

    def process_csv(self, filepath: Path):
        """Process a single FRIL/31 CSV file."""
        fuente, categoria = self._detect_fuente_and_categoria(filepath.name)

        # Skip summary sheets
        if categoria == "RESUMEN":
            print(f"Skipping summary: {filepath.name}")
            return

        print(f"Processing: {filepath.name} (fuente={fuente}, categoria={categoria})")

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Skip total rows (empty codigo/comuna)
                codigo = self._parse_codigo(
                    row.get("Código") or row.get("Codigo") or row.get("CÓDIGO")
                )
                comuna = normalize_text(row.get("Comuna") or row.get(" Comuna "))

                if not codigo and not comuna:
                    continue

                # Parse fields
                nombre = normalize_text(
                    row.get("Nombre Iniciativa") or row.get("NOMBRE INICIATIVA"),
                    uppercase=False,
                )

                unidad_tecnica = normalize_text(
                    row.get("Unidad Técnica") or row.get("Unidad Tecnica")
                )

                item_presup = normalize_text(
                    row.get("Item Presupuestario") or row.get("ITEM PRESUPUESTARIO")
                )

                # Si no hay item en hoja FRIL Avan, usar default 33.03.125
                if fuente == "FRIL" and not item_presup:
                    item_presup = "33.03.125"

                estado = normalize_text(
                    row.get("Estado Iniciativa") or row.get("ESTADO INICIATIVA")
                )

                subestado = normalize_text(
                    row.get("Sub-Estado Iniciativa") or row.get("SUB-ESTADO INICIATIVA")
                )

                saldo_2026 = self._parse_saldo(
                    row.get("Saldo 2026") or row.get("SALDO 2026")
                )

                saldo_2027 = self._parse_saldo(
                    row.get("Saldo 2027") or row.get("SALDO 2027")
                )

                self.facts.append(
                    FactFRIL(
                        id=str(uuid.uuid4()),
                        codigo=codigo,
                        nombre_iniciativa=nombre,
                        comuna=normalize_comuna(comuna),
                        unidad_tecnica=unidad_tecnica,
                        fuente=fuente,
                        item_presupuestario=item_presup,
                        estado_iniciativa=estado,
                        subestado_iniciativa=subestado,
                        saldo_2026=saldo_2026,
                        saldo_2027=saldo_2027,
                        categoria_hoja=categoria,
                        origen_hoja=filepath.name,
                    )
                )

    def write_outputs(self):
        """Write normalized outputs."""
        self._write_csv(
            OUTPUT_DIR / "facts" / "fact_fril.csv", [asdict(f) for f in self.facts]
        )

        print(f"\nFRIL outputs written to {OUTPUT_DIR}")
        print(f"  Records: {len(self.facts)}")

        # Count by source
        by_fuente = {}
        for f in self.facts:
            by_fuente[f.fuente] = by_fuente.get(f.fuente, 0) + 1
        for fuente, count in sorted(by_fuente.items()):
            print(f"    {fuente}: {count}")

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
    normalizer = FRILNormalizer()

    if SOURCES_DIR.exists():
        for csv_file in SOURCES_DIR.glob("*.csv"):
            normalizer.process_csv(csv_file)
    else:
        print(f"Source directory not found: {SOURCES_DIR}")
        return

    normalizer.write_outputs()


if __name__ == "__main__":
    main()
