"""
Enrich Institutions with Type Classification
Based on Omega Model alignment requirements.
"""

import csv
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent / "normalized"

# Institution type classification rules
TIPO_RULES = [
    # (pattern, tipo)
    (r"\bMUNI(CIPAL)?\b", "MUNICIPALIDAD"),
    (r"\bI\.\s*MUNICIPALIDAD\b", "MUNICIPALIDAD"),
    (r"\bMUN\.\s", "MUNICIPALIDAD"),
    (r"\bGOBIERNO\s+REGIONAL\b", "GORE"),
    (r"\bGORE\b", "GORE"),
    (r"\bUNIVERSIDA?D\b", "UNIVERSIDAD"),
    (r"\bUDEC\b", "UNIVERSIDAD"),
    (r"\bUCSC\b", "UNIVERSIDAD"),
    (r"\bUNACH\b", "UNIVERSIDAD"),
    (r"\bU\.\s*DE\s*CHILE\b", "UNIVERSIDAD"),
    (r"\bCARABINEROS\b", "SERVICIO_PUBLICO"),
    (r"\bPDI\b", "SERVICIO_PUBLICO"),
    (r"\bSERVICIO\s+DE?\s*SALUD\b", "SERVICIO_PUBLICO"),
    (r"\bSERNATUR\b", "SERVICIO_PUBLICO"),
    (r"\bCORFO\b", "SERVICIO_PUBLICO"),
    (r"\bINDAP\b", "SERVICIO_PUBLICO"),
    (r"\bSERCOTEC\b", "SERVICIO_PUBLICO"),
    (r"\bSENAPESCA\b", "SERVICIO_PUBLICO"),
    (r"\bINIA\b", "SERVICIO_PUBLICO"),
    (r"\bINFOR\b", "SERVICIO_PUBLICO"),
    (r"\bMOP\b", "SERVICIO_PUBLICO"),
    (r"\bSERNAGEOMIN\b", "SERVICIO_PUBLICO"),
    # OSCs
    (r"\bBOMBEROS\b", "OSC"),  # Bomberos de Chile are private non-profit
    (r"\bJUNTA\s+DE\s+VECINOS\b", "OSC"),
    (r"\bJJVV\b", "OSC"),
    (r"\bJ\.J\.V\.V\.\b", "OSC"),
    (r"\bCLUB\b", "OSC"),  # Generalized CLUB
    (r"\bAGRUPACI[OÓ]N\b", "OSC"),
    (r"\bCOMIT[EÉ]\b", "OSC"),
    (r"\bASO[CI]+ACI[OÓ]N\b", "OSC"),
    (r"\bFUNDACI[OÓ]N\b", "OSC"),
    (r"\bCORPORACI[OÓ]N\b", "OSC"),
    (r"\bCENTRO\s+DE\s+PADRES\b", "OSC"),
    (r"\bIGLESIA\b", "OSC"),
    (r"\bPARROQUIA\b", "OSC"),
    (r"\bCONSEJO\s+VECINAL\b", "OSC"),
    (r"\bUNI[OÓ]N\s+COMUNAL\b", "OSC"),
    (r"\bTALLER\b", "OSC"),
    (r"\bCONSEJO\s+DE\s+DESARROLLO\b", "OSC"),
    (r"\bSOCIEDAD\s+BENEFI\w+\b", "OSC"),
    (r"\bCRUZ\s+ROJA\b", "OSC"),
    # Business
    (r"\bCOOPERATIVA\b", "EMPRESA"),
    (r"\bS\.A\.\b", "EMPRESA"),
    (r"\bLTDA\b", "EMPRESA"),
    (r"\bEIRL\b", "EMPRESA"),
    (r"\bSPA\b", "EMPRESA"),
    (r"\bCONSULTORA\b", "EMPRESA"),
    (r"\bCONSTRUCTORA\b", "EMPRESA"),
    (r"\bSOCIEDAD\b", "EMPRESA"),
]


def classify_institution(nombre: str) -> str:
    """Classify institution type based on name patterns."""
    if not nombre:
        return "OTROS"

    nombre_upper = nombre.upper()

    for pattern, tipo in TIPO_RULES:
        if re.search(pattern, nombre_upper):
            return tipo

    return "OTROS"


def enrich_institutions():
    """Add tipo_institucion to dim_institucion_unificada."""
    input_file = BASE_DIR / "dimensions" / "dim_institucion_unificada.csv"
    output_file = BASE_DIR / "dimensions" / "dim_institucion_unificada_enriched.csv"

    if not input_file.exists():
        print(f"Error: {input_file} not found")
        return

    with open(input_file, "r", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        fieldnames = list(reader.fieldnames) + ["tipo_institucion"]

        rows = []
        for row in reader:
            nombre = row.get("nombre_original", "") or row.get("nombre_normalizado", "")
            row["tipo_institucion"] = classify_institution(nombre)
            rows.append(row)

    with open(output_file, "w", encoding="utf-8", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Stats
    by_tipo = {}
    for r in rows:
        t = r["tipo_institucion"]
        by_tipo[t] = by_tipo.get(t, 0) + 1

    print(f"Enriched {len(rows)} instituciones")
    print("\nBy tipo_institucion:")
    for t, c in sorted(by_tipo.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")

    # Replace original
    import os

    os.replace(output_file, input_file)
    print(f"\nUpdated: {input_file}")


def validate_territorio():
    """Validate territorio against 21 comunas oficiales."""
    comunas_oficiales = {
        "CHILLÁN",
        "CHILLÁN VIEJO",
        "BULNES",
        "EL CARMEN",
        "PEMUCO",
        "PINTO",
        "QUILLÓN",
        "SAN IGNACIO",
        "YUNGAY",
        "QUIRIHUE",
        "COBQUECURA",
        "COELEMU",
        "NINHUE",
        "PORTEZUELO",
        "RÁNQUIL",
        "TREGUACO",
        "SAN CARLOS",
        "COIHUECO",
        "ÑIQUÉN",
        "SAN FABIÁN",
        "SAN NICOLÁS",
    }

    territorio_file = BASE_DIR / "dimensions" / "dim_territorio_canonico.csv"

    if not territorio_file.exists():
        print(f"Error: {territorio_file} not found")
        return

    with open(territorio_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        found_comunas = set()
        other_entries = []

        for row in reader:
            nombre = row.get("nombre_oficial", "").upper()
            if nombre in comunas_oficiales:
                found_comunas.add(nombre)
            else:
                other_entries.append(nombre)

    missing = comunas_oficiales - found_comunas

    print("\n" + "=" * 60)
    print("TERRITORIO VALIDATION")
    print("=" * 60)
    print(f"Expected: 21 comunas")
    print(f"Found: {len(found_comunas)} comunas")

    if missing:
        print(f"\nMissing comunas ({len(missing)}):")
        for c in sorted(missing):
            print(f"  - {c}")

    if other_entries:
        print(f"\nNon-comuna entries ({len(other_entries)}):")
        for e in other_entries:
            print(f"  - {e}")


def main():
    print("=" * 60)
    print("OMEGA MODEL ALIGNMENT - P2 ENRICHMENT")
    print("=" * 60)

    enrich_institutions()
    validate_territorio()


if __name__ == "__main__":
    main()
