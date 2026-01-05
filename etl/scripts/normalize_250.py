"""
250 Domain Normalizer
Processes strategic investment planning data from the "250" initiative tracking sheets.
Contains BROUCHURE (summary) and CONSOLIDADO (detailed tracking with timeline).
"""

import csv
import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


SOURCES_DIR = Path(__file__).parent.parent / "sources" / "250"
OUTPUT_DIR = Path(__file__).parent.parent / "normalized"


@dataclass
class Iniciativa250:
    id: str
    trazo_primario: str
    trazo_secundario: str
    nombre_iniciativa: str
    division: str
    bip: str
    bip_base: str  # BIP without check digit for IDIS join
    iniciativa_id: str  # FK to dim_iniciativa_idis
    comunas: str
    contraparte_externa: str
    responsable_gore: str
    estado: str
    etapa: str
    formulador: str
    unidad_tecnica: str
    fuente_financiera: str
    estado_financiero: str
    monto: Optional[float]
    hito: str
    medida: str
    unidad: str
    # Timeline quarters
    q1_2026: str
    q2_2026: str
    q3_2026: str
    q4_2026: str
    q1_2027: str
    q2_2027: str
    q3_2027: str
    q4_2027: str
    q1_2028: str
    q2_2028: str
    q3_2028: str
    q4_2028: str
    y2029_plus: str
    fecha_inicio: str
    fecha_termino: str
    observacion: str
    accion: str
    origen_archivo: str


def parse_money(value: str) -> Optional[float]:
    """Parse Chilean peso format to float (in thousands - M$)."""
    if not value or value.strip() in ("", "-"):
        return None
    # Remove $ symbol, spaces, and thousand separators
    clean = re.sub(r"[$\s]", "", str(value))
    clean = clean.replace(",", "")
    try:
        return float(clean)
    except ValueError:
        return None


def parse_bip_base(bip: str) -> str:
    """Extract BIP base (without check digit) for IDIS join."""
    if not bip:
        return ""
    # Pattern: NNNNNNNN-D -> NNNNNNNN
    match = re.match(r"^(\d{8})-\d$", bip.strip())
    if match:
        return match.group(1)
    # Already base format
    if re.match(r"^\d{8}$", bip.strip()):
        return bip.strip()
    return ""


def load_idis_bip_map() -> Dict[str, str]:
    """Load BIP -> iniciativa_id mapping from dim_iniciativa_idis."""
    idis_dim = OUTPUT_DIR / "dimensions" / "dim_iniciativa_idis.csv"
    bip_map = {}

    if not idis_dim.exists():
        print(f"Warning: IDIS dimension not found at {idis_dim}")
        return bip_map

    with open(idis_dim, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bip = row.get("bip", "").strip()
            if bip and bip not in bip_map:
                bip_map[bip] = row.get("id", "")

    print(f"Loaded {len(bip_map)} BIP mappings from IDIS")
    return bip_map


def normalize_consolidado():
    """Normalize the CONSOLIDADO (detailed) file."""
    source_file = SOURCES_DIR / "CONSOLIDADO.csv"

    if not source_file.exists():
        print(f"Source not found: {source_file}")
        return []

    # Load IDIS mapping for FK joins
    idis_map = load_idis_bip_map()
    matched_count = 0

    iniciativas: List[Iniciativa250] = []

    with open(source_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Skip empty rows
            nombre = row.get("NOMBRE DE INICIATIVA", "").strip()
            if not nombre:
                continue

            try:
                bip_raw = row.get("BIP", "").strip()
                bip_base = parse_bip_base(bip_raw)

                # Lookup iniciativa_id from IDIS
                iniciativa_id = idis_map.get(bip_base, "")
                if iniciativa_id:
                    matched_count += 1

                ini = Iniciativa250(
                    id=str(uuid.uuid4()),
                    trazo_primario=row.get("TRAZO PRIMARIO", "").strip().upper(),
                    trazo_secundario=row.get("TRAZO SECUNDARIO", "").strip().upper(),
                    nombre_iniciativa=nombre,
                    division=row.get("DIVISIÓN", "").strip(),
                    bip=bip_raw,
                    bip_base=bip_base,
                    iniciativa_id=iniciativa_id,
                    comunas=row.get("COMUNA", "").strip(),
                    contraparte_externa=row.get(
                        "CONTRAPARTE TÉCNICA EXTERNA \n(NOMBRE.,  CARGO, CORREO, TELEFONO)",
                        "",
                    ).strip(),
                    responsable_gore=row.get(
                        "RESPONSABLE SEGUIMIENTO GORE\n(NOMBRE.,  CARGO, CORREO, TELEFONO)",
                        "",
                    ).strip(),
                    estado=row.get("ESTADO", "").strip(),
                    etapa=row.get("ETAPA A LA CUAL POSTULA", "").strip(),
                    formulador=row.get("FORMULADOR", "").strip(),
                    unidad_tecnica=row.get("UNIDAD TÉCNICA", "").strip(),
                    fuente_financiera=row.get("FUENTE FINANCIERA", "").strip(),
                    estado_financiero=row.get("ESTADO FINANCIERO", "").strip(),
                    monto=parse_money(row.get("MONTO", "")),
                    hito=row.get("HITO", "").strip(),
                    medida=row.get("MEDIDA", "").strip(),
                    unidad=row.get("UNIDAD", "").strip(),
                    q1_2026=row.get("ENE-MAR 2026", "").strip(),
                    q2_2026=row.get("MAR-JUN 2026", "").strip(),
                    q3_2026=row.get("JUN-SEP 2026", "").strip(),
                    q4_2026=row.get("SEP-DIC 2026", "").strip(),
                    q1_2027=row.get("ENE-MAR 2027", "").strip(),
                    q2_2027=row.get("MAR-JUN 2027", "").strip(),
                    q3_2027=row.get("JUN-SEP 2027", "").strip(),
                    q4_2027=row.get("SEP-DIC 2027", "").strip(),
                    q1_2028=row.get("ENE-MAR 2028", "").strip(),
                    q2_2028=row.get("MAR-JUN 2028", "").strip(),
                    q3_2028=row.get("JUN-SEP 2028", "").strip(),
                    q4_2028=row.get("SEP-DIC 2028", "").strip(),
                    y2029_plus=row.get("2029  Y MÁS", "").strip(),
                    fecha_inicio=row.get("FECHA DE INICIO", "").strip(),
                    fecha_termino=row.get("FECHA DE TERMINO", "").strip(),
                    observacion=row.get("OBSERVACIÓN", "").strip().replace("\n", " "),
                    accion=row.get("ACCIÓN", "").strip().replace("\n", " "),
                    origen_archivo="CONSOLIDADO.csv",
                )
                iniciativas.append(ini)
            except Exception as e:
                print(f"Error processing row: {e}")
                continue

    print(f"  IDIS FK matches: {matched_count}/{len(iniciativas)}")

    return iniciativas


def write_outputs(iniciativas: List[Iniciativa250]):
    """Write normalized outputs."""
    # Write fact table
    fact_path = OUTPUT_DIR / "facts" / "fact_iniciativa_250.csv"
    fact_path.parent.mkdir(parents=True, exist_ok=True)

    if not iniciativas:
        print("No iniciativas to write")
        return

    with open(fact_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(iniciativas[0]).keys()))
        writer.writeheader()
        for ini in iniciativas:
            writer.writerow(asdict(ini))

    print(f"Wrote {len(iniciativas)} iniciativas to {fact_path.name}")

    # Extract unique BIPs for dimension linking
    bips = {}
    for ini in iniciativas:
        if ini.bip and ini.bip not in bips:
            bips[ini.bip] = {
                "bip": ini.bip,
                "nombre": ini.nombre_iniciativa,
                "fuente": "250",
            }

    # Extract unique trazos
    trazos = set()
    for ini in iniciativas:
        if ini.trazo_primario:
            trazos.add(ini.trazo_primario)
        if ini.trazo_secundario:
            trazos.add(ini.trazo_secundario)

    # Write trazo dimension
    dim_path = OUTPUT_DIR / "dimensions" / "dim_trazo_250.csv"
    with open(dim_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "trazo", "descripcion"])
        writer.writeheader()
        for trazo in sorted(trazos):
            writer.writerow(
                {
                    "id": str(uuid.uuid4()),
                    "trazo": trazo,
                    "descripcion": get_trazo_description(trazo),
                }
            )

    print(f"Wrote {len(trazos)} trazos to dim_trazo_250.csv")

    # Stats
    print("\nBy Trazo Primario:")
    by_trazo = {}
    for ini in iniciativas:
        t = ini.trazo_primario or "SIN_TRAZO"
        by_trazo[t] = by_trazo.get(t, 0) + 1
    for t, count in sorted(by_trazo.items()):
        print(f"  {t}: {count}")

    print("\nBy Estado Financiero:")
    by_estado = {}
    for ini in iniciativas:
        e = ini.estado_financiero or "SIN_ESTADO"
        by_estado[e] = by_estado.get(e, 0) + 1
    for e, count in sorted(by_estado.items()):
        print(f"  {e}: {count}")

    # Total monto
    total_monto = sum(ini.monto or 0 for ini in iniciativas)
    print(f"\nMonto Total: M$ {total_monto:,.0f}")


def get_trazo_description(trazo: str) -> str:
    """Map trazo code to description."""
    descriptions = {
        "AZUL": "Infraestructura y Conectividad",
        "VERDE": "Medio Ambiente y Sustentabilidad",
        "ROJO": "Desarrollo Social",
        "AMARILLO": "Desarrollo Económico",
        "CAFÉ": "Sector Productivo",
        "NARANJO": "Emergencias y Reconstrucción",
        "MORADO": "Cultura y Patrimonio",
    }
    return descriptions.get(trazo.upper(), "Otro")


def main():
    print("=" * 60)
    print("250 DOMAIN NORMALIZER")
    print("=" * 60)

    iniciativas = normalize_consolidado()
    print(f"Loaded {len(iniciativas)} iniciativas from CONSOLIDADO")

    write_outputs(iniciativas)


if __name__ == "__main__":
    main()
