"""
Funcionarios Normalizer
Processes the integrated employee listing preserving all data while normalizing structure.
"""

import csv
import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime


SOURCES_DIR = Path(__file__).parent.parent / "sources" / "funcionarios"
OUTPUT_DIR = Path(__file__).parent.parent / "normalized"


@dataclass
class Funcionario:
    id: str
    periodo: str
    anio: int
    mes: str
    mes_num: int
    tipo_vinculo: str
    estamento: str
    nombre_completo: str
    cargo_funcion: str
    grado_eus: str
    calificacion_profesional: str
    region: str
    fecha_inicio: Optional[str]
    fecha_termino: Optional[str]
    asignaciones_especiales: Optional[float]
    remuneracion_bruta: Optional[float]
    remuneracion_liquida: Optional[float]
    rem_adicionales: Optional[float]
    bonos_incentivos: Optional[float]
    derecho_horas_extra: bool
    horas_extra_diurnas_monto: Optional[float]
    horas_extra_diurnas_horas: Optional[float]
    horas_extra_nocturnas_monto: Optional[float]
    horas_extra_nocturnas_horas: Optional[float]
    horas_extra_festivas_monto: Optional[float]
    horas_extra_festivas_horas: Optional[float]
    viaticos: Optional[float]
    observaciones: str
    fuente: str
    origen_archivo: str


def parse_money(value: str) -> Optional[float]:
    """Parse Chilean peso format to float."""
    if not value or value in ("", "-", "No tiene"):
        return None
    # Remove $ and thousand separators
    clean = re.sub(r"[$\s]", "", str(value))
    clean = clean.replace(".", "").replace(",", ".")
    try:
        return float(clean)
    except ValueError:
        return None


def parse_bool(value: str) -> bool:
    """Parse boolean from various formats."""
    return str(value).lower() in ("true", "sí", "si", "yes", "1")


def normalize_funcionarios():
    """Normalize funcionarios data."""
    source_file = SOURCES_DIR / "listado_funcionarios_integrado_remediado.csv"

    if not source_file.exists():
        print(f"Source file not found: {source_file}")
        return []

    funcionarios: List[Funcionario] = []

    with open(source_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                func = Funcionario(
                    id=str(uuid.uuid4()),
                    periodo=row.get("Periodo", ""),
                    anio=int(row.get("Año", 0) or 0),
                    mes=row.get("Mes", ""),
                    mes_num=int(row.get("Mes_num", 0) or 0),
                    tipo_vinculo=row.get("Tipo vínculo", ""),
                    estamento=row.get("Estamento", ""),
                    nombre_completo=row.get("Nombre completo", ""),
                    cargo_funcion=row.get("Cargo o función", ""),
                    grado_eus=row.get("Grado EUS o jornada", ""),
                    calificacion_profesional=row.get(
                        "Calificación profesional o formación", ""
                    ),
                    region=row.get("Región", ""),
                    fecha_inicio=row.get("Fecha_inicio", ""),
                    fecha_termino=row.get("Fecha_termino", ""),
                    asignaciones_especiales=parse_money(
                        row.get(
                            "Asignaciones especiales del mes (inc. en rem. bruta)_CLP",
                            "",
                        )
                    ),
                    remuneracion_bruta=parse_money(
                        row.get(
                            "Remuneración bruta del mes (incluye bonos e incentivos, asig. especiales, horas extras)_CLP",
                            "",
                        )
                    ),
                    remuneracion_liquida=parse_money(
                        row.get("Remuneración líquida del mes_CLP", "")
                    ),
                    rem_adicionales=parse_money(
                        row.get(
                            "Rem. adicionales del mes (no inc. en rem. bruta)_CLP", ""
                        )
                    ),
                    bonos_incentivos=parse_money(
                        row.get(
                            "Remuneración Bonos incentivos del mes (inc. en rem. bruta)_CLP",
                            "",
                        )
                    ),
                    derecho_horas_extra=parse_bool(row.get("Derecho_horas_extras", "")),
                    horas_extra_diurnas_monto=parse_money(
                        row.get(
                            "Montos y horas extraordinarias diurnas del mes(inc. en rem. bruta)_CLP",
                            "",
                        )
                    ),
                    horas_extra_diurnas_horas=parse_money(
                        row.get(
                            "Montos y horas extraordinarias diurnas del mes(inc. en rem. bruta)_Horas",
                            "",
                        )
                    ),
                    horas_extra_nocturnas_monto=parse_money(
                        row.get(
                            "Montos y horas extraordinarias nocturnas del mes(inc. en rem. bruta)_CLP",
                            "",
                        )
                    ),
                    horas_extra_nocturnas_horas=parse_money(
                        row.get(
                            "Montos y horas extraordinarias nocturnas del mes(inc. en rem. bruta)_Horas",
                            "",
                        )
                    ),
                    horas_extra_festivas_monto=parse_money(
                        row.get(
                            "Montos y horas extraordinarias festivas del mes (inc. en rem. bruta)_CLP",
                            "",
                        )
                    ),
                    horas_extra_festivas_horas=parse_money(
                        row.get(
                            "Montos y horas extraordinarias festivas del mes (inc. en rem. bruta)_Horas",
                            "",
                        )
                    ),
                    viaticos=parse_money(
                        row.get("Viáticos del mes (no inc. en rem. bruta)_CLP", "")
                    ),
                    observaciones=row.get("Observaciones", ""),
                    fuente=row.get("_fuente", ""),
                    origen_archivo="listado_funcionarios_integrado_remediado.csv",
                )
                funcionarios.append(func)
            except Exception as e:
                print(f"Error processing row: {e}")
                continue

    return funcionarios


def write_outputs(funcionarios: List[Funcionario]):
    """Write normalized outputs."""
    output_path = OUTPUT_DIR / "facts" / "fact_funcionario.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not funcionarios:
        print("No funcionarios to write")
        return

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(funcionarios[0]).keys()))
        writer.writeheader()
        for func in funcionarios:
            writer.writerow(asdict(func))

    print(f"Wrote {len(funcionarios)} funcionarios to {output_path.name}")

    # Generate dimension: unique funcionarios by name
    unique_names = {}
    for func in funcionarios:
        name = func.nombre_completo.strip()
        if name and name not in unique_names:
            unique_names[name] = {
                "id": str(uuid.uuid4()),
                "nombre_completo": name,
                "cargo_ultimo": func.cargo_funcion,
                "estamento": func.estamento,
                "calificacion": func.calificacion_profesional,
            }

    dim_path = OUTPUT_DIR / "dimensions" / "dim_funcionario.csv"
    with open(dim_path, "w", newline="", encoding="utf-8") as f:
        if unique_names:
            writer = csv.DictWriter(
                f, fieldnames=list(list(unique_names.values())[0].keys())
            )
            writer.writeheader()
            for record in unique_names.values():
                writer.writerow(record)

    print(f"Wrote {len(unique_names)} unique funcionarios to dim_funcionario.csv")


def main():
    print("=" * 60)
    print("FUNCIONARIOS NORMALIZER")
    print("=" * 60)

    funcionarios = normalize_funcionarios()
    print(f"Loaded {len(funcionarios)} funcionario records")

    write_outputs(funcionarios)

    # Stats
    if funcionarios:
        by_year = {}
        for f in funcionarios:
            by_year[f.anio] = by_year.get(f.anio, 0) + 1
        print("\nBy Year:")
        for year, count in sorted(by_year.items()):
            print(f"  {year}: {count}")


if __name__ == "__main__":
    main()
