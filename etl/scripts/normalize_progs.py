"""
PROGS normalizer - Fixed version.
Processes F.*.csv fund files (F.DEPORTE.csv, F.CULTURA.csv, etc.)
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
    normalize_provincia,
    normalize_rut,
    validate_rut,
)


SOURCES_DIR = Path(__file__).parent.parent / "sources" / "progs" / "originales"
OUTPUT_DIR = Path(__file__).parent.parent / "normalized"


@dataclass
class FactRendicion8Pct:
    id: str
    fondo: str
    codigo: Optional[str]
    tipologia: Optional[str]
    nombre_institucion: Optional[str]
    nombre_iniciativa: Optional[str]
    rut_institucion: Optional[str]
    rut_valido: bool
    provincia: Optional[str]
    comuna: Optional[str]
    correo: Optional[str]
    telefono: Optional[str]
    representante_legal: Optional[str]
    fecha_transferencia: Optional[str]
    monto_transferido: Optional[float]
    resolucion_incorpora: Optional[str]
    estado_ejecucion: Optional[str]
    fecha_ingreso_partes: Optional[str]
    fecha_cierre_tecnico: Optional[str]
    fecha_cierre_financiero: Optional[str]
    ingreso_rendicion_tiempo: Optional[str]
    observaciones: Optional[str]
    origen_hoja: str


class ProgsNormalizer:
    def __init__(self):
        self.rendiciones: List[FactRendicion8Pct] = []
        self.codigos_vistos: Dict[str, int] = {}
        self.duplicates: List[str] = []

    def _extract_fondo(self, filename: str) -> str:
        """Extract fund name from filename like F.DEPORTE.csv."""
        # Remove prefix and extension
        name = filename.upper()

        # Map common patterns
        fondo_map = {
            "F.DEPORTE": "DEPORTE",
            "F.CULTURA": "CULTURA",
            "F.SEGURIDAD": "SEGURIDAD",
            "F.SOCIAL": "SOCIAL",
            "F.ADULTO MAYOR": "ADULTO_MAYOR",
            "F.EQUIDAD DE GÉNERO": "EQUIDAD_GENERO",
            "F.EQUIDAD DE GENERO": "EQUIDAD_GENERO",
            "F.MEDIO AMBIENTE": "MEDIO_AMBIENTE",
        }

        base = filename.rsplit(".csv", 1)[0]
        # If explicitly in map, use it
        if base.upper() in fondo_map:
            return fondo_map[base.upper()]

        # Otherwise clean filename
        return base.replace("F.", "").replace(".", "_").replace(" ", "_").upper()

    def _normalize_codigo(self, codigo_raw: Optional[str]) -> Optional[str]:
        """Normalize initiative code."""
        if not codigo_raw:
            return None

        codigo = normalize_text(codigo_raw)
        if not codigo:
            return None

        # Track duplicates
        if codigo in self.codigos_vistos:
            self.codigos_vistos[codigo] += 1
            self.duplicates.append(codigo)
        else:
            self.codigos_vistos[codigo] = 1

        return codigo

    def _find_header_row(self, rows: List[List[str]]) -> int:
        """Find the row containing 'CÓDIGO' or 'CODIGO' header."""
        for i, row in enumerate(rows):
            for cell in row:
                cell_upper = str(cell).upper().strip()
                if cell_upper in ("CÓDIGO", "CODIGO"):
                    return i
                # Also check if column starts with code pattern
                if "TIPOLOGÍA" in cell_upper or "TIPOLOGIA" in cell_upper:
                    # This row might be the header even if first column is empty
                    return i
        return -1

    def process_fund_file(self, filepath: Path):
        """Process a single fund CSV file (F.*.csv)."""
        fondo = self._extract_fondo(filepath.name)
        print(f"Processing: {filepath.name} (fondo={fondo})")

        # Read all rows first
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            all_rows = list(reader)

        if not all_rows:
            return

        # Find header row
        header_idx = self._find_header_row(all_rows)
        if header_idx < 0:
            print(f"  ⚠️ Could not find header row with CÓDIGO")
            return

        header = all_rows[header_idx]

        # Build column index map
        col_map = {}
        for i, cell in enumerate(header):
            cell_upper = str(cell).upper().strip()
            if cell_upper in ("CÓDIGO", "CODIGO"):
                col_map["codigo"] = i
            elif "TIPOLOG" in cell_upper:
                col_map["tipologia"] = i
            elif (
                "NOMBRE DE LA INSTIT" in cell_upper
                or "NOMBRE INSTITUCI" in cell_upper
                or "UNIDAD EJECUTORA" in cell_upper
                or "INSTITUCIÓN" in cell_upper
            ):
                col_map["institucion"] = i
            elif "NOMBRE INICIATIVA" in cell_upper:
                col_map["iniciativa"] = i
            elif "RUT INSTIT" in cell_upper or "RUT EJECUTOR" in cell_upper:
                col_map["rut"] = i
            elif cell_upper == "PROVINCIA":
                col_map["provincia"] = i
            elif cell_upper == "COMUNA":
                col_map["comuna"] = i
            elif cell_upper == "CORREO" and "correo" not in col_map:
                col_map["correo"] = i
            elif "TELÉFONO" in cell_upper or "TELEFONO" in cell_upper:
                col_map["telefono"] = i
            elif "REPRESENTANTE" in cell_upper:
                col_map["representante"] = i
            elif (
                "RECIBIÓ TRANSFER" in cell_upper
                or "FECHA DE LA TRANSFERENCIA" in cell_upper
            ):
                col_map["fecha_transfer"] = i
            elif "MONTO TRANSFER" in cell_upper:
                col_map["monto"] = i
            elif "RESOLUCIÓN" in cell_upper and "INCORPORA" in cell_upper:
                col_map["resolucion"] = i
            elif (
                "ESTADO EJECUC" in cell_upper or "ESTADO DE LA INICIATIVA" in cell_upper
            ):
                col_map["estado"] = i
            elif "FECHA INGRESO" in cell_upper and "PARTES" in cell_upper:
                col_map["fecha_partes"] = i
            elif "CIERRE TÉCNICO" in cell_upper:
                col_map["fecha_cierre_tec"] = i
            elif "CIERRE FINANCIERO" in cell_upper:
                col_map["fecha_cierre_fin"] = i
            elif "INGRESO RENDICI" in cell_upper and "TIEMPO" in cell_upper:
                col_map["rendicion_tiempo"] = i
            elif "OBSERVACI" in cell_upper:
                col_map["observaciones"] = i

        print(f"  Header at row {header_idx + 1}, {len(col_map)} columns mapped")

        # Process data rows
        for row_idx in range(header_idx + 1, len(all_rows)):
            row = all_rows[row_idx]

            # Skip empty rows
            if not row or all(not str(c).strip() for c in row):
                continue

            # Get code - skip if empty
            codigo = self._normalize_codigo(
                row[col_map["codigo"]]
                if "codigo" in col_map and col_map["codigo"] < len(row)
                else None
            )
            if not codigo:
                continue

            # Get values with safe indexing
            def get_val(key: str) -> Optional[str]:
                if key in col_map and col_map[key] < len(row):
                    return row[col_map[key]]
                return None

            # Parse RUT
            rut_raw = get_val("rut")
            rut = normalize_rut(rut_raw)
            rut_valido = validate_rut(rut) if rut else False

            # Parse monto
            monto = parse_amount(get_val("monto"))

            self.rendiciones.append(
                FactRendicion8Pct(
                    id=str(uuid.uuid4()),
                    fondo=fondo,
                    codigo=codigo,
                    tipologia=normalize_text(get_val("tipologia")),
                    nombre_institucion=normalize_text(
                        get_val("institucion"), uppercase=False
                    ),
                    nombre_iniciativa=normalize_text(
                        get_val("iniciativa"), uppercase=False
                    ),
                    rut_institucion=rut,
                    rut_valido=rut_valido,
                    provincia=normalize_provincia(get_val("provincia")),
                    comuna=normalize_comuna(get_val("comuna")),
                    correo=normalize_text(get_val("correo"), uppercase=False),
                    telefono=normalize_text(get_val("telefono")),
                    representante_legal=normalize_text(
                        get_val("representante"), uppercase=False
                    ),
                    fecha_transferencia=normalize_text(get_val("fecha_transfer")),
                    monto_transferido=float(monto) if monto else None,
                    resolucion_incorpora=normalize_text(get_val("resolucion")),
                    estado_ejecucion=normalize_text(get_val("estado")),
                    fecha_ingreso_partes=normalize_text(get_val("fecha_partes")),
                    fecha_cierre_tecnico=normalize_text(get_val("fecha_cierre_tec")),
                    fecha_cierre_financiero=normalize_text(get_val("fecha_cierre_fin")),
                    ingreso_rendicion_tiempo=normalize_text(
                        get_val("rendicion_tiempo")
                    ),
                    observaciones=normalize_text(
                        get_val("observaciones"), uppercase=False
                    ),
                    origen_hoja=filepath.name,
                )
            )

    def write_outputs(self):
        """Write normalized outputs."""
        self._write_csv(
            OUTPUT_DIR / "facts" / "fact_rendicion_8pct.csv",
            [asdict(r) for r in self.rendiciones],
        )

        print(f"\nPROGS outputs written to {OUTPUT_DIR}")
        print(f"  Rendiciones: {len(self.rendiciones)}")
        print(f"  Unique Códigos: {len(self.codigos_vistos)}")
        print(f"  Duplicate Códigos: {len(set(self.duplicates))}")
        print(
            f"  Invalid RUTs: {sum(1 for r in self.rendiciones if r.rut_institucion and not r.rut_valido)}"
        )

        # Count by fund
        by_fondo = {}
        for r in self.rendiciones:
            by_fondo[r.fondo] = by_fondo.get(r.fondo, 0) + 1

        print("\n  By Fund:")
        for fondo, count in sorted(by_fondo.items(), key=lambda x: -x[1]):
            print(f"    {fondo}: {count}")

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
    normalizer = ProgsNormalizer()

    if SOURCES_DIR.exists():
        # Process ALL CSV files in the directory
        for csv_file in sorted(SOURCES_DIR.glob("*.csv")):
            if csv_file.name.startswith("~$"):
                continue  # Skip temp files
            normalizer.process_fund_file(csv_file)
    else:
        print(f"Source directory not found: {SOURCES_DIR}")
        return

    normalizer.write_outputs()


if __name__ == "__main__":
    main()
