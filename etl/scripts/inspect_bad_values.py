import duckdb

try:
    con = duckdb.connect("goreos_omega.duckdb")

    print("\n--- FRIL (stg_fril_raw) Sample Values ---")
    try:
        res = con.execute(
            "SELECT DISTINCT saldo_2026 FROM stg.stg_fril_raw WHERE saldo_2026 IS NOT NULL AND length(saldo_2026) > 0 LIMIT 20"
        ).fetchall()
        for row in res:
            print(f"Value: {repr(row[0])}")
    except Exception as e:
        print(f"Error checking FRIL: {e}")

    print("\n--- CONVENIOS (stg_convenios_raw) Sample Values ---")
    try:
        res = con.execute(
            "SELECT DISTINCT monto FROM stg.stg_convenios_raw WHERE monto IS NOT NULL AND length(monto) > 0 LIMIT 20"
        ).fetchall()
        for row in res:
            print(f"Value: {repr(row[0])}")
    except Exception as e:
        print(f"Error: {e}")

    con.close()

except Exception as e:
    print(f"Connection failed: {e}")
