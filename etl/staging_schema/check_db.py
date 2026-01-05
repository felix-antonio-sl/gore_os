import sqlite3
from pathlib import Path

# Correct path relative to script or absolute
DB_PATH = Path("/Users/felixsanhueza/fx_felixiando/gore_os/etl/staging/staging_lean.db")

if not DB_PATH.exists():
    print(f"ERROR: {DB_PATH} does not exist!")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

tables = [
    "stg_convenio",
    "stg_presupuesto",
    "stg_funcionario",
    "stg_documento",
    "stg_ipr",
]

print(f"Checking DB at {DB_PATH.absolute()}")
print("-" * 60)

for t in tables:
    try:
        cursor.execute(f"SELECT count(*) FROM {t}")
        count = cursor.fetchone()[0]
        print(f"Table {t}: {count} rows")
    except Exception as e:
        print(f"Error querying {t}: {e}")

print("-" * 60)
print("QUALITY CHECKS:")

# 1. Check Convenios Amounts
try:
    cursor.execute("SELECT count(*) FROM stg_convenio WHERE monto_total > 0")
    valid_monto = cursor.fetchone()[0]
    print(f"Convenios with Amount > 0: {valid_monto}")
except:
    pass

# 2. Check Convenios Links
try:
    cursor.execute(
        "SELECT count(*) FROM stg_convenio WHERE ipr_id != '' AND ipr_id IS NOT NULL"
    )
    linked_conv = cursor.fetchone()[0]
    print(f"Convenios with IPR Link: {linked_conv}")

    cursor.execute(
        "SELECT ipr_id, monto_total FROM stg_convenio WHERE monto_total > 0 LIMIT 1"
    )
    sample = cursor.fetchone()
    print(f"Sample Linked Convenio: {sample}")
except:
    pass

# 3. Check Funcionarios Divisions
try:
    cursor.execute("SELECT count(*) FROM stg_funcionario WHERE division != 'S/I'")
    valid_div = cursor.fetchone()[0]
    print(f"Funcionarios with Division (not S/I): {valid_div}")

    cursor.execute(
        "SELECT cargo, division FROM stg_funcionario WHERE division != 'S/I' LIMIT 3"
    )
    rows = cursor.fetchall()
    print(f"Sample Divisions: {rows}")
except:
    pass

conn.close()
