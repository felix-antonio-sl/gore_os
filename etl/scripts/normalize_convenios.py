"""
CONVENIOS normalizer.
Transforms CONVENIOS 2023-2024, CONVENIOS 2025, and MODIFICACIONES sheets
into the canonical star schema model.
"""

import csv
import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from common import (
    parse_date,
    parse_amount,
    normalize_text,
    normalize_estado_convenio,
    normalize_estado_cgr,
    normalize_tipo_resolucion,
    normalize_comuna,
    normalize_provincia,
)


# Source directory
SOURCES_DIR = Path(__file__).parent.parent / "sources" / "convenios" / "originales"
OUTPUT_DIR = Path(__file__).parent.parent / "normalized"


@dataclass
class DimTerritorio:
    id: str
    provincia_raw: Optional[str]
    provincia_norm: Optional[str]
    comuna_raw: Optional[str]
    comuna_norm: Optional[str]


@dataclass
class DimInstitucion:
    id: str
    rut: Optional[str]
    unidad_tecnica_raw: Optional[str]
    unidad_tecnica_norm: Optional[str]


@dataclass
class DimIniciativa:
    id: str
    codigo: Optional[str]
    nombre_raw: Optional[str]
    nombre_norm: Optional[str]


@dataclass
class DimClasificadorPresup:
    id: str
    subtitulo: Optional[str]
    item: Optional[str]
    asignacion: Optional[str]


@dataclass
class DimPeriodo:
    id: str
    anio: Optional[int]
    fuente_hoja: str


@dataclass
class DimTipoEvento:
    id: str
    familia: str
    tipo_evento: str
    descripcion: Optional[str]


@dataclass
class FactConvenio:
    id: str
    periodo_id: str
    clasificador_id: Optional[str]
    territorio_id: Optional[str]
    institucion_id: Optional[str]
    iniciativa_id: Optional[str]
    monto_fndr_ms: Optional[float]
    tipo_convenio: Optional[str]  # CONVENIO DE TRANSFERENCIA / MODIFICACION
    estado_convenio_raw: Optional[str]
    estado_convenio_norm: Optional[str]
    fecha_firma_convenio: Optional[str]
    estado_cgr_raw: Optional[str]
    estado_cgr_norm: Optional[str]
    estado_operacional: Optional[str]  # ENVIADO AL SERVICIO / EN CGR etc
    referente_tecnico: Optional[str]
    tipo_registro: str
    origen_hoja: str
    fila_origen: int


@dataclass
class FactEventoDocumental:
    id: str
    convenio_id: str
    tipo_evento_id: str
    numero_documento: Optional[str]
    fecha_documento: Optional[str]
    tipo_resolucion_norm: Optional[str]
    observacion_raw: Optional[str]
    columna_fuente: str


class ConveniosNormalizer:
    def __init__(self):
        self.dim_territorio: Dict[str, DimTerritorio] = {}
        self.dim_institucion: Dict[str, DimInstitucion] = {}
        self.dim_iniciativa: Dict[str, DimIniciativa] = {}
        self.dim_clasificador: Dict[str, DimClasificadorPresup] = {}
        self.dim_periodo: Dict[str, DimPeriodo] = {}
        self.dim_tipo_evento: Dict[str, DimTipoEvento] = {}

        self.fact_convenio: List[FactConvenio] = []
        self.fact_evento: List[FactEventoDocumental] = []

        # Initialize event types
        self._init_event_types()

    def _init_event_types(self):
        """Pre-populate event type dimension."""
        events = [
            ("RESOLUCION", "incorpora_cert_core", "Res. Incorpora / Cert. CORE"),
            ("RESOLUCION", "crea_asignacion", "Res. Crea Asignación"),
            ("RESOLUCION", "aprueba_convenio", "Res. Aprueba Convenio"),
            ("OFICIO", "oficio_envio_convenio", "Oficio Envío Convenio"),
            ("CGR", "toma_razon_cgr", "Toma de Razón CGR"),
            ("RESOLUCION", "res_referente_tecnico", "Res. Referente Técnico"),
            ("RESOLUCION", "resolucion_modificacion", "Resolución Modificación"),
        ]
        for familia, tipo, desc in events:
            evt_id = str(uuid.uuid4())
            self.dim_tipo_evento[tipo] = DimTipoEvento(
                id=evt_id, familia=familia, tipo_evento=tipo, descripcion=desc
            )

    def _get_or_create_territorio(
        self, provincia: Optional[str], comuna: Optional[str]
    ) -> Optional[str]:
        """Get or create territory dimension entry."""
        if not provincia and not comuna:
            return None

        prov_norm = normalize_provincia(provincia)
        com_norm = normalize_comuna(comuna)
        key = f"{prov_norm or ''}|{com_norm or ''}"

        if key not in self.dim_territorio:
            self.dim_territorio[key] = DimTerritorio(
                id=str(uuid.uuid4()),
                provincia_raw=normalize_text(provincia, uppercase=False),
                provincia_norm=prov_norm,
                comuna_raw=normalize_text(comuna, uppercase=False),
                comuna_norm=com_norm,
            )
        return self.dim_territorio[key].id

    def _get_or_create_institucion(
        self, rut: Optional[str], unidad_tecnica: Optional[str]
    ) -> Optional[str]:
        """Get or create institution dimension entry."""
        if not unidad_tecnica:
            return None

        unidad_norm = normalize_text(unidad_tecnica)
        key = f"{rut or ''}|{unidad_norm or ''}"

        if key not in self.dim_institucion:
            self.dim_institucion[key] = DimInstitucion(
                id=str(uuid.uuid4()),
                rut=normalize_text(rut),
                unidad_tecnica_raw=normalize_text(unidad_tecnica, uppercase=False),
                unidad_tecnica_norm=unidad_norm,
            )
        return self.dim_institucion[key].id

    def _get_or_create_iniciativa(
        self, codigo: Optional[str], nombre: Optional[str]
    ) -> Optional[str]:
        """Get or create initiative dimension entry."""
        if not codigo:
            return None

        codigo_norm = normalize_text(codigo)
        key = codigo_norm

        if key not in self.dim_iniciativa:
            self.dim_iniciativa[key] = DimIniciativa(
                id=str(uuid.uuid4()),
                codigo=codigo_norm,
                nombre_raw=normalize_text(nombre, uppercase=False),
                nombre_norm=normalize_text(nombre),
            )
        return self.dim_iniciativa[key].id

    def _get_or_create_clasificador(
        self, sub: Optional[str], item: Optional[str], asig: Optional[str]
    ) -> Optional[str]:
        """Get or create budget classifier dimension entry."""
        sub_norm = normalize_text(sub)
        item_norm = normalize_text(item)
        asig_norm = normalize_text(asig) if asig and asig != "-" else None

        if not sub_norm and not item_norm:
            return None

        key = f"{sub_norm}|{item_norm}|{asig_norm}"

        if key not in self.dim_clasificador:
            self.dim_clasificador[key] = DimClasificadorPresup(
                id=str(uuid.uuid4()),
                subtitulo=sub_norm,
                item=item_norm,
                asignacion=asig_norm,
            )
        return self.dim_clasificador[key].id

    def _get_or_create_periodo(self, anio: Optional[int], fuente_hoja: str) -> str:
        """Get or create period dimension entry."""
        key = f"{anio}|{fuente_hoja}"

        if key not in self.dim_periodo:
            self.dim_periodo[key] = DimPeriodo(
                id=str(uuid.uuid4()),
                anio=anio,
                fuente_hoja=fuente_hoja,
            )
        return self.dim_periodo[key].id

    def _extract_events(self, row: Dict[str, str], convenio_id: str):
        """Extract document events from row columns (wide to long)."""
        # Map of column patterns to event types
        event_patterns = [
            # (num_col_pattern, fecha_col_pattern, event_type, tipo_res_col)
            ("Nº RES INCORPORA", "FECHA RES INCORPORA", "incorpora_cert_core", None),
            ("Nº RES CREA ASIGNACIÓN", "FECHA RES CREA", "crea_asignacion", None),
            (
                "Nº RES APRUEBA CONVENIO",
                "FECHA RES APRUEBA CONVENIO",
                "aprueba_convenio",
                "TIPO DE RESOLUCIÓN",
            ),
            (
                "Nº OFICIO ENVIA CONVENIO",
                "FECHA OFICIO ENVIA",
                "oficio_envio_convenio",
                None,
            ),
            ("FECHA TOMA DE RAZON", None, "toma_razon_cgr", None),
            ("Nº RES REFERENTE", None, "res_referente_tecnico", None),
            (
                "Nº RESOLUCION",
                "FECHA ",
                "resolucion_modificacion",
                "TIPO DE RESOLUCION",
            ),
        ]

        for num_pattern, fecha_pattern, event_type, tipo_res_col in event_patterns:
            # Find matching columns
            num_col = None
            fecha_col = None

            for col in row.keys():
                col_upper = col.upper().strip()
                if num_pattern and num_pattern.upper() in col_upper:
                    num_col = col
                if fecha_pattern and fecha_pattern.upper() in col_upper:
                    fecha_col = col

            # Special case: combined column "Nº RES Y FECHA..."
            for col in row.keys():
                if "Y FECHA" in col.upper():
                    num_col = col
                    fecha_col = col

            num_val = row.get(num_col) if num_col else None
            fecha_val = row.get(fecha_col) if fecha_col else row.get(num_col)

            # Skip if no data
            if not num_val and not fecha_val:
                continue
            if num_val and "#REF!" in str(num_val):
                continue

            # Parse date
            fecha_parsed = parse_date(fecha_val)

            # Get tipo resolucion if applicable
            tipo_res = None
            if tipo_res_col:
                for col in row.keys():
                    if tipo_res_col.upper() in col.upper():
                        tipo_res = normalize_tipo_resolucion(row.get(col))
                        break

            # Determine if it's an observation (non-parseable text)
            observacion = None
            if fecha_val and not fecha_parsed and not str(fecha_val).strip().isdigit():
                observacion = normalize_text(fecha_val, uppercase=False)

            tipo_evento = self.dim_tipo_evento.get(event_type)
            if tipo_evento:
                self.fact_evento.append(
                    FactEventoDocumental(
                        id=str(uuid.uuid4()),
                        convenio_id=convenio_id,
                        tipo_evento_id=tipo_evento.id,
                        numero_documento=normalize_text(num_val) if num_val else None,
                        fecha_documento=(
                            fecha_parsed.isoformat() if fecha_parsed else None
                        ),
                        tipo_resolucion_norm=tipo_res,
                        observacion_raw=observacion,
                        columna_fuente=num_col or fecha_col or event_type,
                    )
                )

    def process_csv(
        self,
        filepath: Path,
        fuente_hoja: str,
        anio: Optional[int] = None,
        tipo_registro: str = "CONVENIO",
    ):
        """Process a single CSV file."""
        print(f"Processing: {filepath.name}")

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, start=2):  # 2 because of header
                # Skip total/empty rows
                codigo = row.get("CODIGO") or row.get("Código") or row.get("CÓDIGO")
                if not codigo or codigo.strip() == "":
                    continue

                # Create dimension entries
                periodo_id = self._get_or_create_periodo(anio, fuente_hoja)

                territorio_id = self._get_or_create_territorio(
                    row.get("PROVINCIA"), row.get("COMUNA")
                )

                institucion_id = self._get_or_create_institucion(
                    row.get("RUT INSTITUCIÓN") or row.get("RUT INSTITUCION"),
                    row.get("UNIDAD TECNICA ") or row.get("UNIDAD TECNICA"),
                )

                iniciativa_id = self._get_or_create_iniciativa(
                    codigo, row.get("NOMBRE DE LA INICIATIVA")
                )

                clasificador_id = self._get_or_create_clasificador(
                    row.get("SUB"), row.get("ITEM"), row.get(" ASIG") or row.get("ASIG")
                )

                # Parse monto
                monto_raw = row.get("MONTO FNDR M$") or row.get(" MONTO FNDR M$")
                monto = parse_amount(monto_raw)

                # Parse estados
                estado_conv_raw = row.get("ESTADO DE CONVENIO")
                estado_cgr_raw = row.get("ESTADO CONVENIO EN CGR")

                # Parse fecha firma
                fecha_firma = parse_date(row.get("FECHA FIRMA DE CONVENIO "))

                # Create fact
                convenio_id = str(uuid.uuid4())

                # Extract TIPO DE CONVENIO (e.g., CONVENIO DE TRANSFERENCIA DE BIENES, MODIFICACION DE CONVENIO)
                tipo_convenio_raw = row.get(" TIPO DE CONVENIO ") or row.get(
                    "TIPO DE CONVENIO"
                )
                tipo_convenio = (
                    normalize_text(tipo_convenio_raw) if tipo_convenio_raw else None
                )

                # Extract ESTADO (operational status, different from estado_convenio)
                estado_op = row.get(" ESTADO ") or row.get("ESTADO")
                estado_operacional = normalize_text(estado_op) if estado_op else None

                self.fact_convenio.append(
                    FactConvenio(
                        id=convenio_id,
                        periodo_id=periodo_id,
                        clasificador_id=clasificador_id,
                        territorio_id=territorio_id,
                        institucion_id=institucion_id,
                        iniciativa_id=iniciativa_id,
                        monto_fndr_ms=float(monto) if monto else None,
                        tipo_convenio=tipo_convenio,
                        estado_convenio_raw=normalize_text(
                            estado_conv_raw, uppercase=False
                        ),
                        estado_convenio_norm=normalize_estado_convenio(estado_conv_raw),
                        fecha_firma_convenio=(
                            fecha_firma.isoformat() if fecha_firma else None
                        ),
                        estado_cgr_raw=normalize_text(estado_cgr_raw, uppercase=False),
                        estado_cgr_norm=normalize_estado_cgr(estado_cgr_raw),
                        estado_operacional=estado_operacional,
                        referente_tecnico=normalize_text(
                            row.get("REFERENTE TECNICO O CONTRAPARTE TECNICA")
                            or row.get("REFERENTE TECNICO "),
                            uppercase=False,
                        ),
                        tipo_registro=tipo_registro,
                        origen_hoja=fuente_hoja,
                        fila_origen=row_num,
                    )
                )

                # Extract events
                self._extract_events(row, convenio_id)

    def write_outputs(self):
        """Write all normalized outputs to CSV."""
        # Dimensions
        self._write_csv(
            OUTPUT_DIR / "dimensions" / "dim_territorio.csv",
            [asdict(d) for d in self.dim_territorio.values()],
        )
        self._write_csv(
            OUTPUT_DIR / "dimensions" / "dim_institucion.csv",
            [asdict(d) for d in self.dim_institucion.values()],
        )
        self._write_csv(
            OUTPUT_DIR / "dimensions" / "dim_iniciativa.csv",
            [asdict(d) for d in self.dim_iniciativa.values()],
        )
        self._write_csv(
            OUTPUT_DIR / "dimensions" / "dim_clasificador_presup.csv",
            [asdict(d) for d in self.dim_clasificador.values()],
        )
        self._write_csv(
            OUTPUT_DIR / "dimensions" / "dim_periodo.csv",
            [asdict(d) for d in self.dim_periodo.values()],
        )
        self._write_csv(
            OUTPUT_DIR / "dimensions" / "dim_tipo_evento.csv",
            [asdict(d) for d in self.dim_tipo_evento.values()],
        )

        # Facts
        self._write_csv(
            OUTPUT_DIR / "facts" / "fact_convenio.csv",
            [asdict(f) for f in self.fact_convenio],
        )
        self._write_csv(
            OUTPUT_DIR / "facts" / "fact_evento_documental.csv",
            [asdict(f) for f in self.fact_evento],
        )

        print(f"\nOutputs written to {OUTPUT_DIR}")
        print(f"  Territories: {len(self.dim_territorio)}")
        print(f"  Institutions: {len(self.dim_institucion)}")
        print(f"  Initiatives: {len(self.dim_iniciativa)}")
        print(f"  Classifiers: {len(self.dim_clasificador)}")
        print(f"  Convenios: {len(self.fact_convenio)}")
        print(f"  Events: {len(self.fact_evento)}")

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
    normalizer = ConveniosNormalizer()

    # Find and process CSV files
    if SOURCES_DIR.exists():
        for csv_file in SOURCES_DIR.glob("*.csv"):
            name = csv_file.stem.upper()

            if "2023" in name and "2024" in name:
                normalizer.process_csv(csv_file, "CONVENIOS_2023_2024", anio=2024)
            elif "2025" in name:
                normalizer.process_csv(csv_file, "CONVENIOS_2025", anio=2025)
            elif "MODIFICACION" in name:
                normalizer.process_csv(csv_file, name, tipo_registro="MODIFICACION")
    else:
        print(f"Source directory not found: {SOURCES_DIR}")
        return

    normalizer.write_outputs()


if __name__ == "__main__":
    main()
