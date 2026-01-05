"""
IDIS normalizer.
Processes ANALISIS and MAESTRA_DIPIR sheets (highest quality sources).
Discards MASTER and CONSOLIDADO due to formula corruption.
"""

import csv
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from common import (
    parse_date,
    parse_amount,
    normalize_text,
    normalize_comuna,
    normalize_provincia,
)


SOURCES_DIR = Path(__file__).parent.parent / "sources" / "idis" / "originales"
OUTPUT_DIR = Path(__file__).parent.parent / "normalized"


@dataclass
class DimIniciativaIDIS:
    id: str
    cod_unico: Optional[str]
    bip: Optional[str]
    dv: Optional[str]
    nombre_iniciativa: Optional[str]
    vigencia: Optional[str]
    etapa: Optional[str]
    tipologia: Optional[str]
    origen: Optional[str]
    unidad_tecnica: Optional[str]
    provincia: Optional[str]
    comuna: Optional[str]
    estado_actual: Optional[str]
    rate_actual: Optional[str]
    anio: Optional[int]
    anio_presupuestario: Optional[int]


@dataclass
class FactLineaPresupuestaria:
    id: str
    iniciativa_id: str
    anio_presupuestario: Optional[int]
    subtitulo: Optional[str]
    item: Optional[str]
    asignacion: Optional[str]
    nombre_linea: Optional[str]
    monto_iniciativa: Optional[float]
    monto_sectorial: Optional[float]
    monto_fndr: Optional[float]
    monto_final_aprobado: Optional[float]
    gasto_vigente: Optional[float]
    gasto_sig_anios: Optional[float]
    arrastre_2024: Optional[float]
    arrastre_2025: Optional[float]
    arrastre_2026: Optional[float]
    origen_hoja: str


@dataclass
class FactEjecucionMensual:
    id: str
    linea_id: str
    anio: int
    mes: int
    tipo: str  # PROYECTADO or REAL
    monto: Optional[float]


class IDISNormalizer:
    def __init__(self):
        self.dim_iniciativa: Dict[str, DimIniciativaIDIS] = {}
        self.fact_linea: List[FactLineaPresupuestaria] = []
        self.fact_ejecucion: List[FactEjecucionMensual] = []

        # Track quality issues
        self.errors: List[Dict[str, Any]] = []

    def _normalize_cod_unico(self, value: Optional[str]) -> Optional[str]:
        """Normalize cod_unico: trim, uppercase, placeholders to None."""
        if value is None:
            return None

        cleaned = normalize_text(value)
        if not cleaned:
            return None

        # Placeholders
        if cleaned in ("-", "--", "N/A", "#REF!", "#VALUE!"):
            return None

        # Pattern like '-2023' or just year
        if cleaned.startswith("-") and cleaned[1:].isdigit():
            return None
        if cleaned.isdigit() and len(cleaned) == 4:
            return None  # Just a year

        return cleaned

    def _parse_anio_from_cod(self, cod_unico: str) -> Optional[int]:
        """Extract year from cod_unico pattern like 40012345-2024."""
        if "-" in cod_unico:
            parts = cod_unico.split("-")
            if len(parts) >= 2 and parts[-1].isdigit() and len(parts[-1]) == 4:
                return int(parts[-1])
        return None

    def _get_or_create_iniciativa(
        self, row: Dict[str, str], origen: str
    ) -> Optional[str]:
        """Get or create initiative dimension from row data."""
        cod_raw = (
            row.get("COD. ÚNICO") or row.get("CODIGO ÚNICO") or row.get("Codigo Unico")
        )
        cod_unico = self._normalize_cod_unico(cod_raw)

        if not cod_unico:
            return None

        if cod_unico not in self.dim_iniciativa:
            # Parse fields
            anio_raw = row.get("AÑO") or row.get("AÑO PRESP.")
            anio = int(anio_raw) if anio_raw and str(anio_raw).isdigit() else None
            if not anio:
                anio = self._parse_anio_from_cod(cod_unico)

            anio_presp_raw = row.get("AÑO PRESUPUESTARIO") or row.get("AÑO PRESP.")
            anio_presp = (
                int(anio_presp_raw)
                if anio_presp_raw and str(anio_presp_raw).isdigit()
                else None
            )

            self.dim_iniciativa[cod_unico] = DimIniciativaIDIS(
                id=str(uuid.uuid4()),
                cod_unico=cod_unico,
                bip=normalize_text(row.get("BIP") or row.get("CODIGO BIP")),
                dv=normalize_text(row.get("DV")),
                nombre_iniciativa=normalize_text(
                    row.get("NOMBRE INICIATIVA"), uppercase=False
                ),
                vigencia=normalize_text(row.get("VIGENCIA")),
                etapa=normalize_text(row.get("ETAPA")),
                tipologia=normalize_text(row.get("TIPOLOGÍA") or row.get("TIPOLOGIA")),
                origen=normalize_text(row.get("ORIGEN")),
                unidad_tecnica=normalize_text(
                    row.get("UNIDAD TÉCNICA") or row.get("UNIDAD TECNICA")
                ),
                provincia=normalize_provincia(row.get("PROVINCIA")),
                comuna=normalize_comuna(row.get("COMUNA")),
                estado_actual=normalize_text(row.get("ESTADO ACTUAL")),
                rate_actual=normalize_text(row.get("RATE ACTUAL")),
                anio=anio,
                anio_presupuestario=anio_presp,
            )

        return self.dim_iniciativa[cod_unico].id

    def _parse_month_columns(self, row: Dict[str, str], linea_id: str, anio: int):
        """Extract monthly execution data from wide columns."""
        MESES = {
            "ENERO": 1,
            "ENE": 1,
            "FEBRERO": 2,
            "FEB": 2,
            "MARZO": 3,
            "MAR": 3,
            "ABRIL": 4,
            "ABR": 4,
            "MAYO": 5,
            "MAY": 5,
            "JUNIO": 6,
            "JUN": 6,
            "JULIO": 7,
            "JUL": 7,
            "AGOSTO": 8,
            "AGO": 8,
            "SEPTIEMBRE": 9,
            "SEP": 9,
            "SEPT": 9,
            "OCTUBRE": 10,
            "OCT": 10,
            "NOVIEMBRE": 11,
            "NOV": 11,
            "DICIEMBRE": 12,
            "DIC": 12,
        }

        for col_name, value in row.items():
            col_upper = col_name.upper().strip()

            # Detect month column pattern
            for mes_name, mes_num in MESES.items():
                if mes_name in col_upper:
                    tipo = None
                    if "PROYECTADO" in col_upper:
                        tipo = "PROYECTADO"
                    elif "REAL" in col_upper:
                        tipo = "REAL"
                    else:
                        continue

                    # Extract year suffix if present (e.g., "ENE REAL 24")
                    col_anio = anio
                    for suffix in ["23", "24", "25", "2023", "2024", "2025"]:
                        if suffix in col_upper:
                            col_anio = (
                                2000 + int(suffix) if len(suffix) == 2 else int(suffix)
                            )
                            break

                    monto = parse_amount(value)
                    if monto is not None:
                        self.fact_ejecucion.append(
                            FactEjecucionMensual(
                                id=str(uuid.uuid4()),
                                linea_id=linea_id,
                                anio=col_anio,
                                mes=mes_num,
                                tipo=tipo,
                                monto=float(monto),
                            )
                        )
                    break

    def process_analisis(self, filepath: Path):
        """Process ANALISIS sheet - initiative-level data."""
        print(f"Processing ANALISIS: {filepath.name}")

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Skip empty rows
                if all(not v or v.strip() == "" for v in row.values()):
                    continue

                iniciativa_id = self._get_or_create_iniciativa(row, "ANALISIS")
                if not iniciativa_id:
                    continue

                # Create a basic line entry
                anio_presp_raw = row.get("AÑO PRESP.") or row.get("AÑO PRESUPUESTARIO")
                anio_presp = (
                    int(anio_presp_raw)
                    if anio_presp_raw and str(anio_presp_raw).isdigit()
                    else None
                )

                linea_id = str(uuid.uuid4())
                self.fact_linea.append(
                    FactLineaPresupuestaria(
                        id=linea_id,
                        iniciativa_id=iniciativa_id,
                        anio_presupuestario=anio_presp,
                        subtitulo=normalize_text(row.get("SUBT")),
                        item=normalize_text(row.get("ITEM")),
                        asignacion=normalize_text(row.get("ASIG")),
                        nombre_linea=normalize_text(
                            row.get("NOMBRE LINEA"), uppercase=False
                        ),
                        monto_iniciativa=float(
                            parse_amount(row.get("MONTO INICIATIVA")) or 0
                        ),
                        monto_sectorial=(
                            float(parse_amount(row.get("MONTO SECTORIAL")) or 0)
                            if parse_amount(row.get("MONTO SECTORIAL"))
                            else None
                        ),
                        monto_fndr=(
                            float(parse_amount(row.get("MONTO FNDR")) or 0)
                            if parse_amount(row.get("MONTO FNDR"))
                            else None
                        ),
                        monto_final_aprobado=(
                            float(parse_amount(row.get("MONTO FINAL APROB.")) or 0)
                            if parse_amount(row.get("MONTO FINAL APROB."))
                            else None
                        ),
                        gasto_vigente=(
                            float(parse_amount(row.get("GASTO VIGENTE")) or 0)
                            if parse_amount(row.get("GASTO VIGENTE"))
                            else None
                        ),
                        gasto_sig_anios=(
                            float(parse_amount(row.get("GASTO SIG. AÑOS")) or 0)
                            if parse_amount(row.get("GASTO SIG. AÑOS"))
                            else None
                        ),
                        arrastre_2024=None,
                        arrastre_2025=None,
                        arrastre_2026=None,
                        origen_hoja="ANALISIS",
                    )
                )

    def process_maestra_dipir(self, filepath: Path):
        """Process MAESTRA DIPIR sheet - budget line level with monthly detail."""
        print(f"Processing MAESTRA DIPIR: {filepath.name}")

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Skip empty rows
                if all(not v or v.strip() == "" for v in row.values()):
                    continue

                iniciativa_id = self._get_or_create_iniciativa(row, "MAESTRA_DIPIR")
                if not iniciativa_id:
                    continue

                # Get year
                anio_presp_raw = row.get("AÑO PRESUPUESTARIO")
                anio_presp = (
                    int(anio_presp_raw)
                    if anio_presp_raw and str(anio_presp_raw).isdigit()
                    else 2024
                )

                linea_id = str(uuid.uuid4())

                # Normalize SUBT/ITEM/ASIG (remove leading zeros inconsistency)
                subt = normalize_text(row.get("SUBT"))
                item = normalize_text(row.get("ITEM"))
                asig = normalize_text(row.get("ASIG"))

                # Remove leading zeros for consistency
                if subt and subt.isdigit():
                    subt = str(int(subt))
                if item and item.isdigit():
                    item = str(int(item))
                if asig and asig.isdigit():
                    asig = str(int(asig))

                self.fact_linea.append(
                    FactLineaPresupuestaria(
                        id=linea_id,
                        iniciativa_id=iniciativa_id,
                        anio_presupuestario=anio_presp,
                        subtitulo=subt,
                        item=item,
                        asignacion=asig,
                        nombre_linea=normalize_text(
                            row.get("NOMBRE LINEA") or row.get("NOMBRE INICIATIVA"),
                            uppercase=False,
                        ),
                        monto_iniciativa=(
                            float(parse_amount(row.get("MONTO INICIATIVA")) or 0)
                            if parse_amount(row.get("MONTO INICIATIVA"))
                            else None
                        ),
                        monto_sectorial=(
                            float(parse_amount(row.get("MONTO SECTORIAL M$")) or 0)
                            if parse_amount(row.get("MONTO SECTORIAL M$"))
                            else None
                        ),
                        monto_fndr=(
                            float(parse_amount(row.get("MONTO FNDR")) or 0)
                            if parse_amount(row.get("MONTO FNDR"))
                            else None
                        ),
                        monto_final_aprobado=(
                            float(parse_amount(row.get("MONTO FINAL APROB.")) or 0)
                            if parse_amount(row.get("MONTO FINAL APROB."))
                            else None
                        ),
                        gasto_vigente=(
                            float(parse_amount(row.get("GASTO VIGENTE")) or 0)
                            if parse_amount(row.get("GASTO VIGENTE"))
                            else None
                        ),
                        gasto_sig_anios=(
                            float(parse_amount(row.get("GASTO SIG. AÑOS")) or 0)
                            if parse_amount(row.get("GASTO SIG. AÑOS"))
                            else None
                        ),
                        arrastre_2024=(
                            float(parse_amount(row.get("ARRASTRE 2024")) or 0)
                            if parse_amount(row.get("ARRASTRE 2024"))
                            else None
                        ),
                        arrastre_2025=(
                            float(parse_amount(row.get("ARRASTRE 2025")) or 0)
                            if parse_amount(row.get("ARRASTRE 2025"))
                            else None
                        ),
                        arrastre_2026=(
                            float(parse_amount(row.get("ARRASTRE 2026")) or 0)
                            if parse_amount(row.get("ARRASTRE 2026"))
                            else None
                        ),
                        origen_hoja="MAESTRA_DIPIR",
                    )
                )

                # Extract monthly execution data
                self._parse_month_columns(row, linea_id, anio_presp)

    def process_consolidado(self, filepath: Path):
        """
        Process CONSOLIDADO sheet - recover historical initiatives.
        Has #REF! in 'cruce' column (formula) but core data is valid.
        Only adds initiatives NOT already loaded from ANALISIS.
        """
        print(f"Processing CONSOLIDADO (recovery): {filepath.name}")
        new_count = 0

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Skip empty rows
                if all(not v or v.strip() == "" for v in row.values()):
                    continue

                # Get cod_unico - skip if already in dimension
                cod_raw = row.get("COD. ÚNICO") or row.get("CODIGO ÚNICO")
                cod_unico = self._normalize_cod_unico(cod_raw)

                if not cod_unico:
                    continue

                # Skip if already loaded from ANALISIS
                if cod_unico in self.dim_iniciativa:
                    continue

                # This is a NEW initiative - create it
                iniciativa_id = self._get_or_create_iniciativa(row, "CONSOLIDADO")
                if not iniciativa_id:
                    continue

                new_count += 1

                # Create a basic line entry (skip monthly data due to #N/A)
                anio_presp_raw = row.get("AÑO PRESP.") or row.get("AÑO PRESUPUESTARIO")
                anio_presp = (
                    int(anio_presp_raw)
                    if anio_presp_raw and str(anio_presp_raw).isdigit()
                    else None
                )

                linea_id = str(uuid.uuid4())
                self.fact_linea.append(
                    FactLineaPresupuestaria(
                        id=linea_id,
                        iniciativa_id=iniciativa_id,
                        anio_presupuestario=anio_presp,
                        subtitulo=normalize_text(row.get("SUBT")),
                        item=normalize_text(row.get("ITEM")),
                        asignacion=normalize_text(row.get("ASIG")),
                        nombre_linea=normalize_text(
                            row.get("NOMBRE LINEA"), uppercase=False
                        ),
                        monto_iniciativa=float(
                            parse_amount(row.get("MONTO INICIATIVA")) or 0
                        ),
                        monto_sectorial=(
                            float(parse_amount(row.get("MONTO SECTORIAL")) or 0)
                            if parse_amount(row.get("MONTO SECTORIAL"))
                            else None
                        ),
                        monto_fndr=(
                            float(parse_amount(row.get("MONTO FNDR")) or 0)
                            if parse_amount(row.get("MONTO FNDR"))
                            else None
                        ),
                        monto_final_aprobado=(
                            float(parse_amount(row.get("MONTO FINAL APROB.")) or 0)
                            if parse_amount(row.get("MONTO FINAL APROB."))
                            else None
                        ),
                        gasto_vigente=(
                            float(parse_amount(row.get("GASTO VIGENTE")) or 0)
                            if parse_amount(row.get("GASTO VIGENTE"))
                            else None
                        ),
                        gasto_sig_anios=(
                            float(parse_amount(row.get("GASTO SIG. AÑOS")) or 0)
                            if parse_amount(row.get("GASTO SIG. AÑOS"))
                            else None
                        ),
                        arrastre_2024=None,
                        arrastre_2025=None,
                        arrastre_2026=None,
                        origen_hoja="CONSOLIDADO",
                    )
                )

        print(f"  Recovered {new_count} initiatives from CONSOLIDADO")

    def write_outputs(self):
        """Write all normalized outputs to CSV."""
        # Append to existing dimension or create new
        self._write_csv(
            OUTPUT_DIR / "dimensions" / "dim_iniciativa_idis.csv",
            [asdict(d) for d in self.dim_iniciativa.values()],
        )

        # Facts (append to existing)
        existing_lineas = self._read_existing(
            OUTPUT_DIR / "facts" / "fact_linea_presupuestaria.csv"
        )
        self._write_csv(
            OUTPUT_DIR / "facts" / "fact_linea_presupuestaria.csv",
            existing_lineas + [asdict(f) for f in self.fact_linea],
        )

        self._write_csv(
            OUTPUT_DIR / "facts" / "fact_ejecucion_mensual.csv",
            [asdict(f) for f in self.fact_ejecucion],
        )

        print(f"\nIDIS outputs written to {OUTPUT_DIR}")
        print(f"  Initiatives: {len(self.dim_iniciativa)}")
        print(f"  Budget Lines: {len(self.fact_linea)}")
        print(f"  Monthly Execution Records: {len(self.fact_ejecucion)}")

    def _read_existing(self, filepath: Path) -> List[Dict]:
        """Read existing CSV if it exists."""
        if not filepath.exists():
            return []
        with open(filepath, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

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
    normalizer = IDISNormalizer()

    if SOURCES_DIR.exists():
        # Process only the reliable sources first
        for csv_file in SOURCES_DIR.glob("*.csv"):
            name = csv_file.stem.upper()

            if "ANALISIS" in name or "ANÁLISIS" in name:
                normalizer.process_analisis(csv_file)
            elif "MAESTRA" in name and "DIPIR" in name:
                normalizer.process_maestra_dipir(csv_file)

        # Now process CONSOLIDADO to recover additional initiatives
        # (has #REF! in 'cruce' column but core data is valid)
        for csv_file in SOURCES_DIR.glob("*.csv"):
            name = csv_file.stem.upper()
            if "CONSOLIDADO" in name:
                normalizer.process_consolidado(csv_file)
    else:
        print(f"Source directory not found: {SOURCES_DIR}")
        return

    normalizer.write_outputs()


if __name__ == "__main__":
    main()
