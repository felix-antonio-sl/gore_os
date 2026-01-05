"""
PARTES normalizer.
Transforms 10 document registry sheets into doc_documento with UUID PKs.
"""

import csv
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from common import (
    parse_date,
    normalize_text,
    normalize_canal,
)


SOURCES_DIR = Path(__file__).parent.parent / "sources" / "partes" / "originales"
OUTPUT_DIR = Path(__file__).parent.parent / "normalized"


@dataclass
class DocDocumento:
    id: str
    origen_hoja: str
    correlativo_recibidos: Optional[str]
    numero_documento: Optional[str]
    folio: Optional[str]
    tipo_documento: Optional[str]
    fecha_documento: Optional[str]
    fecha_recepcion: Optional[str]
    fecha_entrega: Optional[str]
    remitente: Optional[str]
    destinatario: Optional[str]
    solicita: Optional[str]
    responsable: Optional[str]
    materia: Optional[str]
    canal_recepcion: Optional[str]
    canal_despacho: Optional[str]
    link_documento_url: Optional[str]
    observaciones: Optional[str]
    estado: Optional[str]  # Solo para resoluciones afectas
    monto: Optional[str] = None
    codigo: Optional[str] = None


@dataclass
class DocDerivacion:
    id: str
    documento_id: str
    division: str
    rol: str
    texto_original: Optional[str]
    orden: int


class PartesNormalizer:
    def __init__(self):
        self.documentos: List[DocDocumento] = []
        self.derivaciones: List[DocDerivacion] = []

    def _normalize_tipo_documento(
        self, tipo_raw: Optional[str], origen_hoja: str
    ) -> Optional[str]:
        """Normalize document type from various representations."""
        if tipo_raw:
            tipo = normalize_text(tipo_raw)
            # Mapping
            tipo_map = {
                "OFICIO": "OFICIO",
                "ORDINARIO": "OFICIO",
                "CARTA": "CARTA",
                "MEMO": "MEMO",
                "MEMORANDUM": "MEMO",
                "MEMORÁNDUM": "MEMO",
                "RES EXE": "RES_EXENTA",
                "RESOLUCION EXENTA": "RES_EXENTA",
                "RESOLUCIÓN EXENTA": "RES_EXENTA",
                "RES AFE": "RES_AFECTA",
                "RESOLUCION AFECTA": "RES_AFECTA",
                "RESOLUCIÓN AFECTA": "RES_AFECTA",
                "RENDICION": "RENDICION",
                "INVITACION": "INVITACION",
                "INVITACIÓN": "INVITACION",
            }
            return tipo_map.get(tipo, tipo)

        # Infer from sheet name
        if "MEMO" in origen_hoja.upper():
            return "MEMO"
        if "OFICIO" in origen_hoja.upper():
            return "OFICIO"
        if "RESOL" in origen_hoja.upper() and "EXEN" in origen_hoja.upper():
            return "RES_EXENTA"
        if "RESOL" in origen_hoja.upper() and "AFEC" in origen_hoja.upper():
            return "RES_AFECTA"
        if "CARTA" in origen_hoja.upper():
            return "CARTA"
        if "REND" in origen_hoja.upper():
            return "RENDICION"

        return None

    def _parse_derivaciones(
        self, derivado_raw: Optional[str], doc_id: str
    ) -> List[DocDerivacion]:
        """Parse multi-value 'DERIVADO A' field."""
        if not derivado_raw or derivado_raw.strip() == "":
            return []

        derivaciones = []
        texto = normalize_text(derivado_raw)
        if not texto:
            return []

        # Split by common separators
        import re

        partes = re.split(r"[-/,;]|\s+[yY]\s+", texto)

        for i, parte in enumerate(partes):
            div = normalize_text(parte)
            if div and len(div) > 1:
                derivaciones.append(
                    DocDerivacion(
                        id=str(uuid.uuid4()),
                        documento_id=doc_id,
                        division=div,
                        rol="DERIVADO_A",
                        texto_original=derivado_raw,
                        orden=i + 1,
                    )
                )

        return derivaciones

    def _process_recibidos(self, filepath: Path):
        """Process RECIBIDOS sheet."""
        print(f"Processing RECIBIDOS: {filepath.name}")

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Skip empty
                if all(not v.strip() for v in row.values()):
                    continue

                doc_id = str(uuid.uuid4())

                fecha_doc = parse_date(row.get("FECHA DOCUMENTO"))
                fecha_rec = parse_date(row.get("FECHA RECEPCIÓN"))
                fecha_ent = parse_date(row.get("FECHA DE ENTREGA"))

                self.documentos.append(
                    DocDocumento(
                        id=doc_id,
                        origen_hoja="RECIBIDOS",
                        correlativo_recibidos=normalize_text(row.get("C")),
                        numero_documento=normalize_text(row.get("NÚMERO DOCUMENTO")),
                        folio=None,
                        tipo_documento=self._normalize_tipo_documento(
                            row.get("TIPO DE DOCUMENTO"), "RECIBIDOS"
                        ),
                        fecha_documento=fecha_doc.isoformat() if fecha_doc else None,
                        fecha_recepcion=fecha_rec.isoformat() if fecha_rec else None,
                        fecha_entrega=fecha_ent.isoformat() if fecha_ent else None,
                        remitente=normalize_text(row.get("REMITENTE"), uppercase=False),
                        destinatario=normalize_text(
                            row.get("DESTINATARIO"), uppercase=False
                        ),
                        solicita=None,
                        responsable=normalize_text(
                            row.get("Responsable"), uppercase=False
                        ),
                        materia=normalize_text(row.get("MATERIA"), uppercase=False),
                        canal_recepcion=normalize_canal(row.get("VIA RECEPCIÓN")),
                        canal_despacho=normalize_canal(row.get("VIA DISTRIBUCIÓN")),
                        link_documento_url=None,
                        observaciones=normalize_text(
                            row.get("Observación"), uppercase=False
                        ),
                        estado=None,
                    )
                )

                # Derivaciones
                derivaciones = self._parse_derivaciones(
                    row.get("DERIVADO A: (DIVISIÓN)"), doc_id
                )
                self.derivaciones.extend(derivaciones)

    def _process_oficios(self, filepath: Path):
        """Process OFICIOS sheet."""
        print(f"Processing OFICIOS: {filepath.name}")

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                if all(not str(v).strip() for v in row.values()):
                    continue

                doc_id = str(uuid.uuid4())

                fecha_doc = parse_date(row.get("FECHA DCTO"))
                fecha_rec = parse_date(row.get("FECHA RECEPCIÓN"))
                fecha_ent = parse_date(row.get("FECHA ENTREGA"))

                # Normalize N° DCTO (may be float)
                num_dcto_raw = row.get("N° DCTO")
                num_dcto = None
                if num_dcto_raw:
                    try:
                        num_dcto = str(int(float(num_dcto_raw)))
                    except:
                        num_dcto = normalize_text(num_dcto_raw)

                self.documentos.append(
                    DocDocumento(
                        id=doc_id,
                        origen_hoja="OFICIOS",
                        correlativo_recibidos=None,
                        numero_documento=num_dcto,
                        folio=None,
                        tipo_documento=self._normalize_tipo_documento(
                            row.get("TIPO DE DCTO"), "OFICIOS"
                        ),
                        fecha_documento=fecha_doc.isoformat() if fecha_doc else None,
                        fecha_recepcion=fecha_rec.isoformat() if fecha_rec else None,
                        fecha_entrega=fecha_ent.isoformat() if fecha_ent else None,
                        remitente=normalize_text(row.get("REMITENTE"), uppercase=False),
                        destinatario=normalize_text(
                            row.get("DESTINATARIO"), uppercase=False
                        ),
                        solicita=normalize_text(row.get("SOLICITA"), uppercase=False),
                        responsable=None,
                        materia=normalize_text(row.get("MATERIA"), uppercase=False),
                        canal_recepcion=None,
                        canal_despacho=normalize_canal(row.get("DISTRIBUCIÓN")),
                        link_documento_url=row.get("LINK AL DOCUMENTO"),
                        observaciones=None,
                        estado=None,
                    )
                )

    def _process_memos(self, filepath: Path):
        """Process MEMOS sheet."""
        print(f"Processing MEMOS: {filepath.name}")

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                if all(not str(v).strip() for v in row.values()):
                    continue

                doc_id = str(uuid.uuid4())

                fecha_doc = parse_date(row.get("FECHA DOCTO"))
                fecha_ent = parse_date(row.get("FECHA ENTREGA"))

                self.documentos.append(
                    DocDocumento(
                        id=doc_id,
                        origen_hoja="MEMOS",
                        correlativo_recibidos=None,
                        numero_documento=None,
                        folio=normalize_text(row.get("FOLIO")),
                        tipo_documento="MEMO",
                        fecha_documento=fecha_doc.isoformat() if fecha_doc else None,
                        fecha_recepcion=None,
                        fecha_entrega=fecha_ent.isoformat() if fecha_ent else None,
                        remitente=normalize_text(row.get("DE"), uppercase=False),
                        destinatario=normalize_text(row.get("PARA:"), uppercase=False),
                        solicita=None,
                        responsable=normalize_text(
                            row.get("RESPONSABLE"), uppercase=False
                        ),
                        materia=normalize_text(row.get("MATERIA"), uppercase=False),
                        canal_recepcion=None,
                        canal_despacho=normalize_canal(row.get("VÍA DESPACHO")),
                        link_documento_url=row.get("LINK AL DOCUMENTO"),
                        observaciones=normalize_text(
                            row.get("OBSERVACIONES"), uppercase=False
                        ),
                        estado=None,
                    )
                )

    def _process_resoluciones(self, filepath: Path, tipo: str):
        """Process RESOLUCIONES EXENTAS/AFECTAS sheets."""
        print(f"Processing {tipo}: {filepath.name}")

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                if all(not str(v).strip() for v in row.values()):
                    continue

                doc_id = str(uuid.uuid4())

                fecha_doc = parse_date(row.get("FECHA DOCTO"))

                self.documentos.append(
                    DocDocumento(
                        id=doc_id,
                        origen_hoja=tipo,
                        correlativo_recibidos=None,
                        numero_documento=None,
                        folio=normalize_text(row.get("FOLIO")),
                        tipo_documento=(
                            "RES_EXENTA" if "EXENTA" in tipo else "RES_AFECTA"
                        ),
                        fecha_documento=fecha_doc.isoformat() if fecha_doc else None,
                        fecha_recepcion=None,
                        fecha_entrega=None,
                        remitente=None,
                        destinatario=None,
                        solicita=normalize_text(row.get("SOLICITA"), uppercase=False),
                        responsable=None,
                        materia=normalize_text(row.get("MATERIA"), uppercase=False),
                        canal_recepcion=None,
                        canal_despacho=normalize_canal(row.get("OBSERVACIONES")),
                        link_documento_url=row.get("LINK AL DOCUMENTO"),
                        observaciones=normalize_text(
                            row.get("OBSERVACIONES"), uppercase=False
                        ),
                        estado=(
                            normalize_text(row.get("ESTADO"))
                            if "AFECTA" in tipo
                            else None
                        ),
                    )
                )

    def process_all(self):
        """Process all PARTES source files."""
        if not SOURCES_DIR.exists():
            print(f"Source directory not found: {SOURCES_DIR}")
            return

        for csv_file in SOURCES_DIR.glob("*.csv"):
            name = csv_file.stem.upper()

            if "RECIBIDO" in name:
                self._process_recibidos(csv_file)
            elif "OFICIO" in name:
                self._process_oficios(csv_file)
            elif "MEMO" in name:
                self._process_memos(csv_file)
            elif "RES" in name and "EXEN" in name:
                self._process_resoluciones(csv_file, "RES_EXENTAS")
            elif "RES" in name and "AFEC" in name:
                self._process_resoluciones(csv_file, "RES_AFECTAS")
            elif "CARTA" in name:
                self._process_cartas(csv_file)
            elif "RENDICION" in name:
                self._process_rendiciones(csv_file)

    def _process_cartas(self, filepath: Path):
        """Process CARTAS sheet."""
        print(f"Processing CARTAS: {filepath.name}")

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                if all(not str(v).strip() for v in row.values()):
                    continue

                doc_id = str(uuid.uuid4())
                fecha_doc = parse_date(row.get("FECHA DCTO"))
                fecha_rec = parse_date(row.get("FECHA RECEPCIÓN"))
                fecha_ent = parse_date(row.get("FECHA ENTREGA"))

                self.documentos.append(
                    DocDocumento(
                        id=doc_id,
                        origen_hoja="CARTAS",
                        correlativo_recibidos=None,
                        numero_documento=normalize_text(row.get("NUMERO DOCUMENTO")),
                        folio=None,
                        tipo_documento="CARTA",
                        fecha_documento=fecha_doc.isoformat() if fecha_doc else None,
                        fecha_recepcion=fecha_rec.isoformat() if fecha_rec else None,
                        fecha_entrega=fecha_ent.isoformat() if fecha_ent else None,
                        remitente=normalize_text(row.get("REMITENTE"), uppercase=False),
                        destinatario=normalize_text(
                            row.get("DESTINATARIO"), uppercase=False
                        ),
                        solicita=normalize_text(row.get("SOLICITA"), uppercase=False),
                        responsable=None,
                        materia=normalize_text(row.get("MATERIA"), uppercase=False),
                        canal_recepcion=None,
                        canal_despacho=normalize_canal(row.get("DISTRIBUCIÓN")),
                        link_documento_url=row.get("LINK AL DOCUMENTO"),
                        observaciones=None,
                        estado=None,
                    )
                )

    def _process_rendiciones(self, filepath: Path):
        """Process RENDICIONES sheets."""
        print(f"Processing RENDICIONES: {filepath.name}")

        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Find header - usually around row 4
        header_idx = -1
        for i, row in enumerate(rows):
            if any("CÓDIGO" in str(c).upper() for c in row) and any(
                "NOMBRE INSTITUCI" in str(c).upper() for c in row
            ):
                header_idx = i
                break

        if header_idx == -1:
            print("  ⚠️ Header not found for Rendiciones")
            return

        header = [str(c).upper().strip() for c in rows[header_idx]]
        # Simple index mapping
        try:
            idx_inst = -1
            idx_iniciativa = -1
            idx_codigo = -1
            idx_fecha_dcto = -1
            idx_fecha_ing = -1
            idx_monto = -1

            for i, h in enumerate(header):
                if "INSTITUCI" in h:
                    idx_inst = i
                elif "INICIATIVA" in h:
                    idx_iniciativa = i
                elif "CÓDIGO" in h or "CODIGO" in h:
                    idx_codigo = i
                elif "FECHA DCTO" in h:
                    idx_fecha_dcto = i
                elif "FECHA INGRESO" in h:
                    idx_fecha_ing = i
                elif "MONTO" in h:
                    idx_monto = i

            for row in rows[header_idx + 1 :]:
                if not row or all(not str(c).strip() for c in row):
                    continue

                # Safe get
                def get(idx):
                    return row[idx] if idx >= 0 and idx < len(row) else ""

                inst = get(idx_inst)
                iniciativa = get(idx_iniciativa)
                codigo = get(idx_codigo)

                doc_id = str(uuid.uuid4())
                fecha_doc = parse_date(get(idx_fecha_dcto))
                fecha_rec = parse_date(get(idx_fecha_ing))

                materia = (
                    f"RENDICIÓN {codigo}: {iniciativa}"
                    if codigo
                    else f"RENDICIÓN: {iniciativa}"
                )

                # Monto cleaning (basic)
                monto_raw = get(idx_monto)

                self.documentos.append(
                    DocDocumento(
                        id=doc_id,
                        origen_hoja="RENDICIONES",
                        correlativo_recibidos=None,
                        numero_documento=None,
                        folio=None,
                        tipo_documento="RENDICION",
                        fecha_documento=fecha_doc.isoformat() if fecha_doc else None,
                        fecha_recepcion=fecha_rec.isoformat() if fecha_rec else None,
                        fecha_entrega=None,
                        remitente=normalize_text(inst, uppercase=False),
                        destinatario="GORE ÑUBLE",
                        solicita=None,
                        responsable=None,
                        materia=normalize_text(materia, uppercase=False),
                        canal_recepcion="PRESENCIAL",
                        canal_despacho=None,
                        link_documento_url=None,
                        observaciones=None,
                        estado=None,
                        monto=normalize_text(monto_raw),
                        codigo=normalize_text(codigo),
                    )
                )
        except Exception as e:
            print(f"  Error processing rendiciones: {e}")

    def write_outputs(self):
        """Write normalized outputs."""
        self._write_csv(
            OUTPUT_DIR / "documents" / "doc_documento.csv",
            [asdict(d) for d in self.documentos],
        )

        self._write_csv(
            OUTPUT_DIR / "documents" / "doc_derivacion.csv",
            [asdict(d) for d in self.derivaciones],
        )

        print(f"\nPARTES outputs written to {OUTPUT_DIR}")
        print(f"  Documents: {len(self.documentos)}")
        print(f"  Derivaciones: {len(self.derivaciones)}")

        # Count by origin
        by_origen = {}
        for d in self.documentos:
            by_origen[d.origen_hoja] = by_origen.get(d.origen_hoja, 0) + 1
        for origen, count in sorted(by_origen.items()):
            print(f"    {origen}: {count}")

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
    normalizer = PartesNormalizer()
    normalizer.process_all()
    normalizer.write_outputs()


if __name__ == "__main__":
    main()
