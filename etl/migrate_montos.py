#!/usr/bin/env python3
"""
ETL Script: Migrate IPR Montos and Convenios
Updates fin_ipr.monto_total from idis_cleaned.csv
Imports convenios with administrative events (sys_acto)
"""

import csv
import re
from datetime import datetime
import subprocess


# Database connection via docker exec
def execute_sql(sql: str) -> str:
    """Execute SQL via docker exec psql"""
    result = subprocess.run(
        ["docker", "exec", "gore_db", "psql", "-U", "gore", "-d", "gore_os", "-c", sql],
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr


def parse_monto(monto_str: str) -> float:
    """Parse Chilean currency strings like '$817,390' or 'M$817,390'"""
    if not monto_str or monto_str == "":
        return 0.0
    # Remove currency symbols, M prefix, and spaces
    cleaned = re.sub(r"[M$\s]", "", monto_str)
    # Remove thousands separator (comma)
    cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except:
        return 0.0


def update_ipr_montos():
    """Update fin_ipr.monto_total from idis_cleaned.csv using codigo_bip matching"""
    csv_path = "/Users/felixsanhueza/fx_felixiando/gore_os/etl/sources/idis/cleaned/idis_cleaned.csv"

    updates = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bip = row.get("BIP", "").strip()
            monto_fndr = parse_monto(row.get("MONTO FNDR", ""))
            monto_iniciativa = parse_monto(row.get("MONTO INICIATIVA", ""))
            monto = monto_fndr if monto_fndr > 0 else monto_iniciativa

            if bip and monto > 0:
                updates.append((bip, monto * 1000))  # Convert M$ to $

    print(f"Found {len(updates)} IPRs with valid montos to update")

    # Generate and execute SQL updates
    update_count = 0
    for bip, monto in updates[:100]:  # First 100 as test
        sql = f"UPDATE public.fin_ipr SET monto_total = {monto} WHERE codigo_bip = '{bip}' AND monto_total = 0;"
        result = execute_sql(sql)
        if "UPDATE 1" in result:
            update_count += 1

    print(f"Updated {update_count} IPR records with montos")
    return update_count


def import_convenios():
    """Import convenios from CSV"""
    csv_path = "/Users/felixsanhueza/fx_felixiando/gore_os/etl/sources/convenios/originales/CONVENIOS 2023 y 2024.csv"

    # First check eje_convenio schema
    schema_result = execute_sql("\\d public.eje_convenio")
    print("Convenio schema:", schema_result[:500])

    convenios = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            convenios.append(
                {
                    "codigo_bip": row.get("CODIGO", "").strip(),
                    "nombre": row.get("NOMBRE DE LA INICIATIVA", "").strip()[:200],
                    "monto": parse_monto(row.get(" MONTO FNDR M$ ", "0")),
                    "estado": row.get("ESTADO DE CONVENIO", "").strip(),
                    "fecha_firma": row.get("FECHA FIRMA DE CONVENIO ", "").strip(),
                }
            )

    print(f"Found {len(convenios)} convenios to import")
    return convenios


if __name__ == "__main__":
    print("=== IPR Monto Migration ===")
    update_ipr_montos()

    print("\n=== Convenio Import ===")
    convenios = import_convenios()
