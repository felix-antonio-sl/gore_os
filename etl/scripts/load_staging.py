import duckdb
import os
import glob
from pathlib import Path

# Configuración
DB_PATH = "goreos_omega.duckdb"
DDL_PATH = "../../db/schemata/schema_omega_ddl.sql"
SOURCES_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../sources"))


def init_db(con):
    """Inicializa la base de datos con el esquema DDL."""
    print(f"Inicializando esquema desde {DDL_PATH}...")
    with open(DDL_PATH, "r") as f:
        ddl_script = f.read()
    con.execute(ddl_script)
    print("Esquema inicializado correctamente.")


def load_source(con, source_dir, table_name, mapping_logic=None):
    """Carga archivos de una fuente específica a una tabla staging."""
    search_path = os.path.join(SOURCES_ROOT, source_dir, "**/*.csv")
    print(f"Buscando archivos en: {search_path}")
    files = glob.glob(search_path, recursive=True)
    if not files:
        # Fallback para estructura plana y mayúsculas
        files = glob.glob(os.path.join(SOURCES_ROOT, source_dir, "*.csv")) + glob.glob(
            os.path.join(SOURCES_ROOT, source_dir, "**/*.CSV"), recursive=True
        )

    print(f"Cargando {len(files)} archivos desde '{source_dir}' a '{table_name}'...")

    for file_path in files:
        filename = os.path.basename(file_path)
        print(f"  - Procesando: {filename}")

        try:
            query = f"""
                INSERT INTO {table_name} 
                SELECT 
                    '{filename}' as filename,
                    row_number() OVER () as row_number,
                    * 
                FROM read_csv_auto('{file_path}', filename=False, union_by_name=True, all_varchar=True);
            """

            if mapping_logic:
                query = mapping_logic(file_path, filename, table_name)

            con.execute(query)
            print(f"    -> Carga OK")

        except Exception as e:
            print(f"    -> ERROR al cargar {filename}: {e}")


# --- Helper Queries para Mapping Específico ---


def get_idis_query(file_path, filename, table_name):
    return f"""
        INSERT INTO {table_name} (filename, row_number, codigo_unico, nombre_iniciativa, monto_vigente, estado_actual)
        SELECT '{filename}', row_number() OVER (), "CODIGO BIP", "NOMBRE INICIATIVA", "MONTO VIGENTE", "ESTADO"
        FROM read_csv_auto('{file_path}', union_by_name=True, all_varchar=True);
    """


def get_progs_query(file_path, filename, table_name):
    return f"""
        INSERT INTO {table_name} (filename, row_number, codigo_iniciativa, fondo_origen, rut_institucion, nombre_institucion, monto_transferido)
        SELECT '{filename}', row_number() OVER (), "CÓDIGO", "FONDO", "RUT INSTITUCIÓN", "INSTITUCIÓN", "MONTO TRANSFERIDO"
        FROM read_csv_auto('{file_path}', union_by_name=True, all_varchar=True);
    """


def get_250_query(file_path, filename, table_name):
    return f"""
        INSERT INTO {table_name} (filename, row_number, trazo_primario, nombre_iniciativa, division, codigo_bip, comuna, estado_actual, etapa_postulacion, fuente_financiera, monto_estimado)
        SELECT '{filename}', row_number() OVER (), "TRAZO PRIMARIO", "NOMBRE DE INICIATIVA", "DIVISIÓN", "BIP", "COMUNA", "ESTADO", "ETAPA A LA CUAL POSTULA", "FUENTE FINANCIERA", "MONTO"
        FROM read_csv_auto('{file_path}', union_by_name=True, all_varchar=True);
    """


def get_funcionarios_query(file_path, filename, table_name):
    # Asumiendo columnas probables de listado_funcionarios_integrado_remediado.csv
    # Se usa read_csv_auto genérico si no se conoce el esquema exacto, pero aquí forzamos mapeo simple
    # Si las columnas no coinciden, DuckDB arrojará error y se verá en el log.
    return f"""
        INSERT INTO {table_name} (filename, row_number, rut, nombre_completo, estamento, unidad_asignada)
        SELECT '{filename}', row_number() OVER (), "RUT", "NOMBRE COMPLETO", "ESTAMENTO", "UNIDAD"
        FROM read_csv_auto('{file_path}', union_by_name=True, all_varchar=True);
    """


def get_fril_query(file_path, filename, table_name):
    return f"""
        INSERT INTO {table_name} (filename, codigo, nombre_iniciativa, comuna, unidad_tecnica, estado_iniciativa, sub_estado, saldo_2026)
        SELECT '{filename}', "Código", "Nombre Iniciativa", "Comuna", "Unidad Técnica", "Estado Iniciativa", "Sub-Estado Iniciativa", "Saldo 2026"
        FROM read_csv_auto('{file_path}', union_by_name=True, all_varchar=True);
    """


def get_convenios_query(file_path, filename, table_name):
    return f"""
        INSERT INTO {table_name} (filename, codigo, sub, item, asig, nombre_iniciativa, monto, fecha_firma_convenio, nro_res_aprueba, fecha_res_aprueba, estado_convenio)
        SELECT '{filename}', "CODIGO", "SUB", "ITEM", "ASIG", "NOMBRE DE LA INICIATIVA", "MONTO FNDR M$", "FECHA FIRMA DE CONVENIO", "Nº RES INCORPORA/ CERT CORE", "FECHA RES INCORPORA/ CERT CORE", "ESTADO DE CONVENIO"
        FROM read_csv_auto('{file_path}', union_by_name=True, all_varchar=True);
    """


# Modificaciones y Partes suelen tener esquemas muy variables, se recomienda carga posicional o auto-inference
# Para este script, usaremos carga genérica sin mapping_logic específico (dejando que DuckDB infiera nombres o cargue por posición si coinciden)
# Ojo: Si la tabla destino tiene columnas definidas, DuckDB intentará matchear por nombre.


def main():
    con = duckdb.connect(DB_PATH)

    try:
        init_db(con)

        # 1. Carga IDIS
        load_source(con, "idis", "stg.stg_idis_raw", mapping_logic=get_idis_query)

        # 2. Carga PROGS
        load_source(con, "progs", "stg.stg_progs_raw", mapping_logic=get_progs_query)

        # 3. Carga FRIL
        load_source(con, "fril", "stg.stg_fril_raw", mapping_logic=get_fril_query)

        # 4. Carga ÑUBLE 250
        load_source(con, "250", "stg.stg_nuble250_raw", mapping_logic=get_250_query)

        # 5. Carga CONVENIOS
        load_source(
            con, "convenios", "stg.stg_convenios_raw", mapping_logic=get_convenios_query
        )

        # 6. Carga FUNCIONARIOS
        load_source(
            con, "funcionarios", "stg.stg_funcionarios_raw"
        )  # Intentar auto-match

        # 7. Carga MODIFICACIONES
        load_source(
            con, "modificaciones", "stg.stg_modificaciones_raw"
        )  # Intentar auto-match

        # 8. Carga PARTES
        load_source(con, "partes", "stg.stg_partes_raw")  # Intentar auto-match

        print("\nResumen de Carga (Conteos):")
        tables = [
            "stg_idis_raw",
            "stg_progs_raw",
            "stg_fril_raw",
            "stg_nuble250_raw",
            "stg_convenios_raw",
            "stg_funcionarios_raw",
            "stg_modificaciones_raw",
            "stg_partes_raw",
        ]
        for t in tables:
            try:
                count = con.execute(f"SELECT count(*) FROM stg.{t}").fetchone()[0]
                print(f"  {t}: {count}")
            except:
                print(f"  {t}: 0 (o error)")

    finally:
        con.close()
        print("\nConexión cerrada.")


if __name__ == "__main__":
    main()
