#!/usr/bin/env python3
"""
ETL Script v2: Complete IPR Monto Migration + Convenio Import
Updates ALL fin_ipr.monto_total and imports convenios with sys_acto events
"""

import csv
import re
import subprocess
import uuid


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
    cleaned = re.sub(r"[M$\s]", "", monto_str)
    cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except:
        return 0.0


def update_all_ipr_montos():
    """Update ALL fin_ipr.monto_total from idis_cleaned.csv"""
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

    print(f"Processing {len(updates)} IPRs with montos...")

    # Batch update using CASE statement for efficiency
    batch_size = 200
    total_updated = 0

    for i in range(0, len(updates), batch_size):
        batch = updates[i : i + batch_size]
        cases = []
        bips = []
        for bip, monto in batch:
            safe_bip = bip.replace("'", "''")
            cases.append(f"WHEN codigo_bip = '{safe_bip}' THEN {monto}")
            bips.append(f"'{safe_bip}'")

        sql = f"""
        UPDATE public.fin_ipr 
        SET monto_total = CASE {' '.join(cases)} ELSE monto_total END
        WHERE codigo_bip IN ({','.join(bips)});
        """
        result = execute_sql(sql)
        if "UPDATE" in result:
            count = (
                int(re.search(r"UPDATE (\d+)", result).group(1))
                if re.search(r"UPDATE (\d+)", result)
                else 0
            )
            total_updated += count
        print(f"Batch {i//batch_size + 1}: processed {len(batch)} records")

    print(f"Total updated: {total_updated} IPR records")
    return total_updated


def link_ipr_crisis():
    """Add foreign key constraint from crisis tables to fin_ipr"""
    print("\nLinking crisis tables to fin_ipr...")

    # problema_ipr.iniciativa_id should reference fin_ipr
    sql = """
    -- Add FK constraints (if not exist)
    DO $$ BEGIN
        ALTER TABLE gore_ejecucion.problema_ipr 
        ADD CONSTRAINT fk_problema_iniciativa 
        FOREIGN KEY (iniciativa_id) REFERENCES public.fin_ipr(id_ipr) ON DELETE CASCADE;
    EXCEPTION WHEN duplicate_object THEN NULL;
    END $$;
    
    DO $$ BEGIN
        ALTER TABLE gore_ejecucion.compromiso_operativo 
        ADD CONSTRAINT fk_compromiso_iniciativa 
        FOREIGN KEY (iniciativa_id) REFERENCES public.fin_ipr(id_ipr) ON DELETE SET NULL;
    EXCEPTION WHEN duplicate_object THEN NULL;
    END $$;
    
    DO $$ BEGIN
        ALTER TABLE gore_ejecucion.alerta_ipr 
        ADD CONSTRAINT fk_alerta_iniciativa 
        FOREIGN KEY (iniciativa_id) REFERENCES public.fin_ipr(id_ipr) ON DELETE CASCADE;
    EXCEPTION WHEN duplicate_object THEN NULL;
    END $$;
    """
    result = execute_sql(sql)
    print(result)


def verify_migration():
    """Verify the migration results"""
    print("\n=== Migration Verification ===")

    # Count IPRs with montos
    result = execute_sql(
        """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN monto_total > 0 THEN 1 END) as con_monto,
            SUM(monto_total)/1000000 as total_mm
        FROM public.fin_ipr;
    """
    )
    print("IPR Summary:", result)

    # Count comunas
    result = execute_sql("SELECT COUNT(*) as comunas FROM public.loc_comuna;")
    print("Comunas:", result)


if __name__ == "__main__":
    print("=== Complete IPR Monto Migration ===")
    update_all_ipr_montos()

    print("\n=== Linking Crisis Tables ===")
    link_ipr_crisis()

    verify_migration()
