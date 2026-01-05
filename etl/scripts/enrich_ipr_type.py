"""
Enrich Iniciativas with IPR Type and Financing Mechanism
Based on Omega Model alignment requirements.
"""

import csv
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent / "normalized"


# IPR Type rules based on subtitulo
def derive_tipo_ipr(subtitulo: str) -> str:
    """Derive IPR type from subtitulo."""
    if not subtitulo:
        return "DESCONOCIDO"
    sub = str(subtitulo).strip()
    if sub in ("31", "33"):
        return "PROYECTO"
    elif sub == "24":
        return "PROGRAMA"
    elif sub in ("24/31", "31/24"):
        return "MIXTO"
    else:
        return "DESCONOCIDO"


# Mechanism inference rules
def infer_mecanismo(row: dict, source_table: str) -> str:
    """Infer financing mechanism based on source table and attributes."""
    if source_table == "fact_fril":
        return "MEC-002"  # FRIL
    elif source_table == "fact_rendicion_8pct":
        return "MEC-006"  # SUB8
    elif source_table == "fact_convenio":
        # Convenios can be SNI or Transferencia
        sub = str(row.get("subtitulo", "")).strip()
        if sub in ("31", "33"):
            return "MEC-001"  # SNI
        elif sub == "24":
            return "MEC-005"  # Transferencia
    elif source_table == "fact_iniciativa_250":
        # 250 domain - use fuente_financiera
        fuente = str(row.get("fuente_financiera", "")).upper()
        if "FNDR" in fuente:
            return "MEC-001"  # SNI
        elif "FRPD" in fuente or "ROYALTY" in fuente:
            return "MEC-007"  # FRPD_CTCI
        else:
            return "MEC-001"  # Default SNI

    # Generic fallback based on IPR Type
    # If we are enriching from enriched dimension directly
    tipo_ipr = row.get("tipo_ipr", "PROYECTO")
    if tipo_ipr == "PROYECTO":
        return "MEC-001"  # Default to SNI General (most common)
    elif tipo_ipr == "PROGRAMA":
        return "MEC-005"  # Default to Public Transfer (safest guess)

    return ""


def identify_program_by_nlp(nombre: str) -> bool:
    """Use heuristic keywords to identify Programs in names."""
    if not nombre:
        return False

    n = nombre.upper()
    keywords = [
        "PROGRAMA",
        "CAPACITACION",
        "TRANSFERENCIA",
        "SUBSIDIO",
        "DIPLOMADO",
        "BECA",
        "FONDO CONCURSABLE",
        "EMPRENDIMIENTO",
        "INNOVACION",
        "COMPETITIVIDAD",
        "DIFUSION",
        "GIRA",
        "EVENTO",
        "TALLER",
        "CENTRO DE",
        "OFICINA DE",
        "SERVICIO DE",
        "ESTUDIO",
        "DIAGNOSTICO",
        "PLAN DE",
        "POLITICA",
        "ESTRATEGIA",
    ]

    # Exclusion triggers (names that look like programs but are projects)
    exclusions = [
        "CONSTRUCCION",
        "MEJORAMIENTO",
        "REPOSICION",
        "AMPLIACION",
        "HABILITACION",
        "INSTALACION",
        "RESTAURACION",
        "CONSERVACION",
        "ADQUISICION",
        "EQUIPAMIENTO",
        "VEHICULO",
        "MAQUINARIA",
    ]

    for exc in exclusions:
        if exc in n:
            return False

    for kw in keywords:
        if kw in n:
            return True

    return False


def enrich_iniciativas_unificada():
    """Add tipo_ipr and mecanismo_id to dim_iniciativa_unificada."""
    input_file = BASE_DIR / "dimensions" / "dim_iniciativa_unificada.csv"
    output_file = BASE_DIR / "dimensions" / "dim_iniciativa_unificada_enriched.csv"

    if not input_file.exists():
        print(f"Error: {input_file} not found")
        return

    with open(input_file, "r", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames
        if "tipo_ipr" not in fieldnames:
            fieldnames.append("tipo_ipr")
        if "mecanismo_id" not in fieldnames:
            fieldnames.append("mecanismo_id")

        rows = []
        for row in reader:
            fuente = row.get("fuente_principal", "").upper()
            nombre = row.get("nombre_iniciativa", "")

            # Default values
            tipo = "PROYECTO"
            mec = "MEC-001"  # SNI

            # 1. Strong signal: Explicit Source Classification
            if "PROGS" in fuente or "8%" in fuente:
                tipo = "PROGRAMA"
                mec = "MEC-006"  # Sub8
            elif "FRIL" in fuente:
                tipo = "PROYECTO"
                mec = "MEC-002"

            # 2. NLP Heuristics for ambiguous sources (IDIS, CONVENIOS, 250)
            else:
                is_prog = identify_program_by_nlp(nombre)

                # Check known mechanisms in legacy
                if "GLOSA" in nombre.upper() or "TRANSFERENCIA" in nombre.upper():
                    tipo = "PROGRAMA"
                    mec = "MEC-004" if "GLOSA" in nombre.upper() else "MEC-005"
                elif is_prog:
                    tipo = "PROGRAMA"
                    mec = "MEC-005"  # Generic Transfer
                else:
                    tipo = "PROYECTO"
                    mec = "MEC-001"

            # Final Safety Net for IPR Classification
            if not mec or mec == "DESCONOCIDO":
                mec = "MEC-001" if tipo == "PROYECTO" else "MEC-005"

            # Apply
            row["tipo_ipr"] = tipo
            row["mecanismo_id"] = mec

            rows.append(row)

    with open(output_file, "w", encoding="utf-8", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Stats
    by_tipo = {}
    by_mec = {}
    for r in rows:
        t = r["tipo_ipr"]
        m = r["mecanismo_id"]
        by_tipo[t] = by_tipo.get(t, 0) + 1
        by_mec[m] = by_mec.get(m, 0) + 1

    print(f"Enriched {len(rows)} iniciativas")
    print("\nBy tipo_ipr:")
    for t, c in sorted(by_tipo.items()):
        print(f"  {t}: {c}")
    print("\nBy mecanismo_id:")
    for m, c in sorted(by_mec.items()):
        print(f"  {m}: {c}")

    # Replace original
    import os

    os.replace(output_file, input_file)
    print(f"\nUpdated: {input_file}")


def enrich_fact_linea_presupuestaria():
    """Add tipo_ipr based on subtitulo column."""
    input_file = BASE_DIR / "facts" / "fact_linea_presupuestaria.csv"
    output_file = BASE_DIR / "facts" / "fact_linea_presupuestaria_enriched.csv"

    if not input_file.exists():
        print(f"Error: {input_file} not found")
        return

    with open(input_file, "r", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        fieldnames = list(reader.fieldnames)
        if "tipo_ipr" not in fieldnames:
            fieldnames.append("tipo_ipr")

        rows = []
        for row in reader:
            sub = row.get("subtitulo", "")
            tipo = derive_tipo_ipr(sub)
            row["tipo_ipr"] = tipo
            rows.append(row)

    with open(output_file, "w", encoding="utf-8", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Enriched {len(rows)} lineas presupuestarias")

    import os

    os.replace(output_file, input_file)
    print(f"Updated: {input_file}")


def main():
    print("=" * 60)
    print("OMEGA MODEL ALIGNMENT - IPR TYPE ENRICHMENT")
    print("=" * 60)

    enrich_iniciativas_unificada()
    print()
    enrich_fact_linea_presupuestaria()


if __name__ == "__main__":
    main()
