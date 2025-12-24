#!/usr/bin/env python3
"""
GORE_OS ETL Migration Executor
Migrates cleaned CSV data from ETL sources to canonical PostgreSQL tables.
Usage: python3 migrate_to_model.py [--dry-run]
"""
import os
import csv
import sys
import uuid
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation

# Check for psycopg2 (optional for dry-run)
PSYCOPG2_AVAILABLE = False
try:
    import psycopg2
    from psycopg2.extras import execute_values

    PSYCOPG2_AVAILABLE = True
except ImportError:
    pass

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/goreos")


def parse_decimal(val):
    if not val:
        return Decimal(0)
    try:
        # Remove points (thousands), replace comma with dot
        clean = val.replace(".", "").replace(",", ".")
        return Decimal(clean)
    except:
        return Decimal(0)


# Migration configuration: (source_name, csv_path, target_table, column_mapping)
MIGRATIONS = [
    {
        "name": "divisiones",
        "csv": "sources/funcionarios/listado_funcionarios_integrado_remediado.csv",  # Dummy source
        "table": "org_division",
        "unique_on": "nombre",
        "single_row": True,  # Custom flag to insert just one default
        "mapping": {
            "id_division": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "GORE_NUBLE_DEFAULT")
            ),
            "nombre": lambda r: "GOBIERNO REGIONAL DE ÑUBLE (DEFAULT)",
            "codigo": lambda r: "GORE_DEFAULT",
            "sigla": lambda r: "GORE",
            "tipo": lambda r: "ADMINISTRATIVA",
            "jefe_id": lambda r: None,
            # Checking constraints in ent-org-division.yml... Assuming just name/code/id are critical or defaultable
        },
    },
    {
        "name": "cargos",
        "csv": "sources/funcionarios/listado_funcionarios_integrado_remediado.csv",
        "table": "org_cargo",
        "unique_on": "nombre",  # Pseudo-instruction for logic
        "mapping": {
            "id_cargo": lambda r: str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    r.get("Cargo o función", "SIN CARGO").strip().upper(),
                )
            ),
            "codigo": lambda r: r.get("Cargo o función", "SIN CARGO")
            .strip()
            .upper()
            .replace(" ", "_")
            .replace(".", "")[:50],
            "nombre": lambda r: r.get("Cargo o función", "SIN CARGO").strip().upper(),
            "estamento": lambda r: r.get("Estamento", "").upper(),
            "division_id": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "GORE_NUBLE_DEFAULT")
            ),
            "grado_min": lambda r: 0,
            "grado_max": lambda r: 0,
            "jefatura": lambda r: False,
        },
    },
    {
        "name": "funcionarios",
        "csv": "sources/funcionarios/listado_funcionarios_integrado_remediado.csv",
        "table": "org_funcionario",
        "mapping": {
            "id_funcionario": lambda r: str(uuid.uuid4()),
            "rut": lambda r: clean_rut(r.get("RUN", r.get("RUT", ""))),
            "nombres": lambda r: extract_nombres(
                r.get("Nombre completo", "")
            ),  # Fixed key from "NOMBRE" to "Nombre completo" from header check
            "apellido_paterno": lambda r: extract_apellido_paterno(
                r.get("Nombre completo", "")
            ),
            "apellido_materno": lambda r: extract_apellido_materno(
                r.get("Nombre completo", "")
            ),
            "email_institucional": lambda r: "",  # CSV does not seem to have EMAIL based on header check?
            "cargo_id": lambda r: str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    r.get("Cargo o función", "SIN CARGO").strip().upper(),
                )
            ),
            "division_id": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "GORE_NUBLE_DEFAULT")
            ),
            "fecha_ingreso": lambda r: parse_date(r.get("Fecha_inicio", "")),
            "calidad_juridica": lambda r: r.get("Tipo vínculo", "CONTRATA"),
            "grado": lambda r: parse_int(r.get("Grado EUS o jornada", "0")),
            "estado": lambda r: "ACTIVO",
            # Extension fields
            "estamento": lambda r: r.get("Estamento", "").upper(),
            "formacion_profesional": lambda r: r.get(
                "Calificación profesional o formación", ""
            ),
            "fecha_termino_contrato": lambda r: parse_date(r.get("Fecha_termino", "")),
            "derecho_horas_extras": lambda r: r.get("Derecho_horas_extras", "False")
            == "True",
        },
    },
    {
        "name": "regiones",
        "csv": "sources/idis/cleaned/idis_cleaned.csv",  # Dummy source
        "table": "loc_region",
        "unique_on": "nombre",
        "single_row": True,
        "mapping": {
            "id_region": lambda r: str(uuid.uuid5(uuid.NAMESPACE_DNS, "REGION_NUBLE")),
            "nombre": lambda r: "REGIÓN DE ÑUBLE",
            "codigo_ine": lambda r: "16",
            "capital": lambda r: "CHILLÁN",
            "superficie_km2": lambda r: 13178.5,
            "poblacion": lambda r: 480609,
        },
    },
    {
        "name": "provincias",
        "csv": "sources/idis/cleaned/idis_cleaned.csv",  # Dummy source
        "table": "loc_provincia",
        "unique_on": "nombre",
        "single_row": True,
        "mapping": {
            "id_provincia": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "PROVINCIA_DEFAULT")
            ),
            "nombre": lambda r: "DIGUILLÍN",  # Default
            "codigo_ine": lambda r: "161",  # Default
            "region_id": lambda r: str(uuid.uuid5(uuid.NAMESPACE_DNS, "REGION_NUBLE")),
        },
    },
    {
        "name": "comunas",
        "csv": "sources/idis/cleaned/idis_cleaned.csv",  # Dummy source
        "table": "loc_comuna",
        "unique_on": "nombre",
        "single_row": True,
        "mapping": {
            "id_comuna": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "COMUNA_DEFAULT")
            ),
            "nombre": lambda r: "SIN COMUNA",
            "provincia_id": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "PROVINCIA_DEFAULT")
            ),
            "codigo_ine": lambda r: "00000",
            "superficie_km2": lambda r: 0.0,
            "poblacion": lambda r: 0,
            "tipologia": lambda r: "RURAL",
        },
    },
    {
        "name": "fondos",
        "csv": "sources/idis/cleaned/idis_cleaned.csv",  # Dummy source
        "table": "fin_fondo",
        "unique_on": "nombre",
        "single_row": True,
        "mapping": {
            "id_fondo": lambda r: str(uuid.uuid5(uuid.NAMESPACE_DNS, "FONDO_DEFAULT")),
            "nombre": lambda r: "FNDR",
            "codigo": lambda r: "FNDR",
            "descripcion": lambda r: "Fondo por defecto",
            "normativa_base": lambda r: "Ley 19.175",
            "vigente": lambda r: True,
            "requiere_aporte_propio": lambda r: False,
        },
    },
    {
        "name": "mecanismos",
        "csv": "sources/idis/cleaned/idis_cleaned.csv",  # Dummy source
        "table": "fin_mecanismo",
        "unique_on": "nombre",
        "single_row": True,
        "mapping": {
            "id_mecanismo": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "MECANISMO_DEFAULT")
            ),
            "nombre": lambda r: "FONDO NACIONAL DE DESARROLLO REGIONAL",
            "codigo": lambda r: "FNDR",
            "tipo": lambda r: "FONDO",
            "normativa": lambda r: "Ley 19.175",
            "activo": lambda r: True,
            # Removed invalid attributes: sigla, fondo_id, descripcion
        },
    },
    {
        "name": "idis (IPR)",
        "csv": "sources/idis/cleaned/idis_cleaned.csv",
        "table": "fin_ipr",
        "mapping": {
            "id_ipr": lambda r: str(uuid.uuid4()),
            "codigo_bip": lambda r: r.get("BIP", r.get("COD. ÚNICO", "")),
            "nombre": lambda r: r.get("NOMBRE INICIATIVA", ""),
            "descripcion": lambda r: r.get("NOMBRE INICIATIVA", ""),
            "tipo": lambda r: derive_tipo_from_bip(r.get("BIP", "")),
            "mecanismo_id": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "MECANISMO_DEFAULT")
            ),
            "monto_total": lambda r: parse_decimal(r.get("MONTO INICIATIVA", "0")),
            "comuna_id": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "COMUNA_DEFAULT")
            ),
            "estado_ciclo": lambda r: map_estado_ciclo(r.get("ESTADO ACTUAL", "")),
            "etapa_actual": lambda r: map_etapa(r.get("ETAPA", "")),
            "fecha_rs": lambda r: parse_date(r.get("FECHA ESTADO ACTUAL", ""))
            or "1970-01-01",
            # IMPLICIT RELATIONSHIP RECOVERY
            "asignacion_id": lambda r: str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"ASG_{r.get('AÑO', '2025')}_{r.get('SUBT', '00')}_{r.get('ITEM', '00')}_{r.get('ASIG', '000')}",
                )
            ),
        },
    },
    # === IMPLICIT ASSIGNMENTS FROM IPRs ===
    {
        "name": "asignaciones_from_ipr",
        "csv": "sources/idis/cleaned/idis_cleaned.csv",
        "table": "fin_asignacion",
        "unique_composite": ["AÑO", "SUBT", "ITEM", "ASIG"],  # Dedupe by year+code
        "mapping": {
            "id_asignacion": lambda r: str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"ASG_{r.get('AÑO', '2025')}_{r.get('SUBT', '00')}_{r.get('ITEM', '00')}_{r.get('ASIG', '000')}",
                )
            ),
            # Link to the historical budget we generated
            "presupuesto_id": lambda r: str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS, f"PRESUPUESTO_{r.get('AÑO', '2025')}_INICIAL"
                )
            ),
            "subtitulo": lambda r: r.get("SUBT", "00"),
            "item": lambda r: r.get("ITEM", "00"),
            "asignacion": lambda r: r.get("ASIG", "000"),
            "monto_inicial": lambda r: 0,
            "monto_vigente": lambda r: 0,
            "monto_ejecutado": lambda r: parse_decimal(
                r.get("GASTO VIGENTE", "0")
            ),  # Estimate execution
            "denominacion": lambda r: f"Asignación IPR {r.get('SUBT')}-{r.get('ITEM')}-{r.get('ASIG')}",
        },
    },
    # === BASE DEFAULTS ===
    {
        "name": "periodos",
        "csv": "sources/modificaciones/cleaned/modificaciones_cleaned.csv",  # Dummy source
        "table": "sys_periodo",
        "unique_on": "_source_file",  # Run once essentially (or per file)
        "single_row": True,
        "mapping": {
            "id_periodo": lambda r: str(uuid.uuid5(uuid.NAMESPACE_DNS, "PERIODO_2025")),
            "anio": lambda r: 2025,
            "tipo": lambda r: "FISCAL",
            "fecha_inicio": lambda r: "2025-01-01",
            "fecha_fin": lambda r: "2025-12-31",
        },
    },
    {
        "name": "presupuestos",
        "csv": "sources/modificaciones/cleaned/modificaciones_cleaned.csv",
        "table": "fin_presupuesto",
        "single_row": True,
        "unique_on": "_source_file",
        "mapping": {
            "id_presupuesto": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "PRESUPUESTO_2025_INICIAL")
            ),
            "periodo_id": lambda r: str(uuid.uuid5(uuid.NAMESPACE_DNS, "PERIODO_2025")),
            "ley_presupuesto": lambda r: "Ley de Presupuestos 2025",
            "monto_inicial": lambda r: 0,
            "monto_vigente": lambda r: 0,
            "estado": lambda r: "VIGENTE",
        },
    },
    {
        "name": "actores_sistema",
        "csv": "sources/modificaciones/cleaned/modificaciones_cleaned.csv",
        "table": "sys_actor",
        "single_row": True,
        "unique_on": "_source_file",
        "mapping": {
            "id_actor": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "ACTOR_GOBERNADOR_DEFAULT")
            ),
            "tipo_actor": lambda r: "INTERNO",
            "identificador": lambda r: "DEFAULT_BOSS",
            "nombre": lambda r: "GOBERNADOR REGIONAL (SISTEMA)",
            "activo": lambda r: True,
        },
    },
    {
        "name": "bolsa_ajuste",
        "csv": "sources/modificaciones/cleaned/modificaciones_cleaned.csv",
        "table": "fin_asignacion",
        "single_row": True,
        "unique_on": "_source_file",
        "mapping": {
            "id_asignacion": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "ASIGNACION_BOLSA_AJUSTE")
            ),
            "presupuesto_id": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "PRESUPUESTO_2025_INICIAL")
            ),
            "subtitulo": lambda r: "00",
            "item": lambda r: "00",
            "asignacion": lambda r: "000",
            "monto_inicial": lambda r: 0,
            "monto_vigente": lambda r: 0,
            "monto_ejecutado": lambda r: 0,
            "denominacion": lambda r: "BOLSA DE AJUSTE (SISTEMA)",
        },
    },
    # === MODIFICACIONES DEPS ===
    {
        "name": "asignaciones_from_mods",
        "csv": "sources/modificaciones/cleaned/modificaciones_cleaned.csv",
        "table": "fin_asignacion",
        "unique_composite": ["subtitulo", "item", "asignacion"],
        "mapping": {
            "id_asignacion": lambda r: str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{r.get('subtitulo')}-{r.get('item')}-{r.get('asignacion')}",
                )
            ),
            "presupuesto_id": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "PRESUPUESTO_2025_INICIAL")
            ),
            "subtitulo": lambda r: r.get("subtitulo", "00"),
            "item": lambda r: r.get("item", "00"),
            "asignacion": lambda r: r.get("asignacion", "000"),
            "monto_inicial": lambda r: parse_decimal(
                r.get("distribucion_inicial", "0")
            ),
            "monto_vigente": lambda r: parse_decimal(
                r.get("ppto_vigente_final", "0")
            ),  # Using final as valid snapshot
            "monto_ejecutado": lambda r: 0,
            "denominacion": lambda r: r.get("denominacion", "").strip(),
        },
    },
    {
        "name": "actos_modificaciones",
        "csv": "sources/modificaciones/cleaned/modificaciones_cleaned.csv",
        "table": "sys_acto",
        "unique_composite": ["numero_modificacion"],
        "mapping": {
            "id_acto": lambda r: str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS, f"ACTO_MOD_{r.get('numero_modificacion')}"
                )
            ),
            "tipo_acto": lambda r: "RESOLUCION",
            "materia": lambda r: f"MODIFICACION PRESUPUESTARIA N° {r.get('numero_modificacion')}",
            "autoridad_id": lambda r: str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "ACTOR_GOBERNADOR_DEFAULT")
            ),
            "fecha_dictacion": lambda r: "2025-01-01",  # Default
            "requiere_toma_razon": lambda r: False,
            "requiere_toma_razon": lambda r: False,
            "estado_tramitacion": lambda r: "TOTALMENTE TRAMITADO",
        },
    },
    {
        "name": "modificaciones",
        "csv": "sources/modificaciones/cleaned/modificaciones_cleaned.csv",
        "table": "fin_modificacion_presupuestaria",
        "mapping": {
            "id_modificacion": lambda r: str(uuid.uuid4()),
            "tipo": lambda r: r.get(
                "tipo_operacion", "GASTOS"
            ),  # Often 'GASTOS' or 'INGRESOS'
            # Logic: If monto < 0, source=This, dest=Bolsa. If monto > 0, source=Bolsa, dest=This.
            "asignacion_origen_id": lambda r: (
                str(
                    uuid.uuid5(
                        uuid.NAMESPACE_DNS,
                        f"{r.get('subtitulo')}-{r.get('item')}-{r.get('asignacion')}",
                    )
                )
                if parse_decimal(r.get("monto_modificacion", "0")) < 0
                else str(uuid.uuid5(uuid.NAMESPACE_DNS, "ASIGNACION_BOLSA_AJUSTE"))
            ),
            "asignacion_destino_id": lambda r: (
                str(
                    uuid.uuid5(
                        uuid.NAMESPACE_DNS,
                        f"{r.get('subtitulo')}-{r.get('item')}-{r.get('asignacion')}",
                    )
                )
                if parse_decimal(r.get("monto_modificacion", "0")) >= 0
                else str(uuid.uuid5(uuid.NAMESPACE_DNS, "ASIGNACION_BOLSA_AJUSTE"))
            ),
            "monto": lambda r: abs(parse_decimal(r.get("monto_modificacion", "0"))),
            "justificacion": lambda r: r.get("denominacion", ""),
            "acto_id": lambda r: str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS, f"ACTO_MOD_{r.get('numero_modificacion')}"
                )
            ),
            "estado": lambda r: (
                "ANULADA" if r.get("sin_efecto") == "True" else "VIGENTE"
            ),
        },
    },
]


def clean_rut(rut: str) -> str:
    """Clean and normalize RUT."""
    if not rut:
        return ""
    return rut.replace(".", "").replace(" ", "").upper().strip()


def extract_nombres(nombre_completo: str) -> str:
    """Extract first names from full name."""
    parts = nombre_completo.strip().split()
    if len(parts) >= 3:
        return " ".join(parts[:-2])
    return parts[0] if parts else ""


def extract_apellido_paterno(nombre_completo: str) -> str:
    """Extract paternal surname from full name."""
    parts = nombre_completo.strip().split()
    if len(parts) >= 2:
        return parts[-2]
    return ""


def extract_apellido_materno(nombre_completo: str) -> str:
    """Extract maternal surname from full name."""
    parts = nombre_completo.strip().split()
    if len(parts) >= 1:
        return parts[-1]
    return ""


def parse_date(date_str: str) -> str:
    """Parse date string to ISO format."""
    if not date_str or date_str in ["#REF!", "-", ""]:
        return None

    # Try common formats
    for fmt in ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%y"]:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def parse_int(value: str) -> int:
    """Parse integer from string."""
    if not value or value in ["#REF!", "-", ""]:
        return 0
    try:
        return int(float(value.replace(",", ".")))
    except (ValueError, TypeError):
        return 0


# Removed duplicate parse_decimal


def derive_tipo_from_bip(bip: str) -> str:
    """Derive IPR type from BIP code prefix."""
    if not bip:
        return "PROYECTO"

    prefix = bip[:2] if len(bip) >= 2 else ""
    if prefix == "30":
        return "PROYECTO"
    elif prefix == "31":
        return "PROGRAMA"
    elif prefix == "40":
        return "ESTUDIO_BASICO"
    return "PROYECTO"


def map_estado_ciclo(estado: str) -> str:
    """Map legacy estado to canonical estado_ciclo."""
    estado = (estado or "").upper()
    mapping = {
        "VIGENTE": "EJECUCION",
        "TERMINADO": "TERMINADO",
        "EN EJECUCION": "EJECUCION",
        "APROBADO": "APROBADO",
    }
    return mapping.get(estado, "FORMULACION")


def map_etapa(etapa: str) -> str:
    """Map legacy etapa to canonical etapa_actual."""
    etapa = (etapa or "").upper()
    mapping = {
        "PREFACTIBILIDAD": "PREFACTIBILIDAD",
        "FACTIBILIDAD": "FACTIBILIDAD",
        "DISEÑO": "DISEÑO",
        "EJECUCION": "EN_EJECUCION",
        "TERMINADO": "CIERRE",
    }
    return mapping.get(etapa, "PERFIL")


def clean_db(conn):
    """Truncate tables to ensure fresh start (no duplicates)."""
    print("🧹 Cleaning database (TRUNCATE)...")
    tables = [
        "fin_ipr",
        "fin_modificacion_presupuestaria",
        "sys_acto",
        "fin_asignacion",
        "org_funcionario",
        "org_cargo",
        "org_division",
        "fin_fondo",
        "fin_mecanismo",
        "loc_comuna",
        "loc_provincia",
        "loc_region",
        "fin_presupuesto",
        "sys_periodo",
        "sys_actor",
    ]
    with conn.cursor() as cur:
        for t in tables:
            cur.execute(f"TRUNCATE TABLE {t} CASCADE;")
    conn.commit()
    print("✨ Database cleaned.")


def generate_historical_context(conn):
    """Generate periods and budgets for 2018-2025."""
    print("📅 Generating historical context (2018-2025)...")
    years = range(2018, 2026)
    batch_periodos = []
    batch_presupuestos = []

    for year in years:
        pid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"PERIODO_{year}"))
        bid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"PRESUPUESTO_{year}_INICIAL"))

        batch_periodos.append((pid, year, "FISCAL", f"{year}-01-01", f"{year}-12-31"))
        batch_presupuestos.append(
            (bid, pid, f"Ley de Presupuestos {year}", 0, 0, "VIGENTE")
        )

    with conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO sys_periodo (id_periodo, anio, tipo, fecha_inicio, fecha_fin) VALUES %s ON CONFLICT DO NOTHING",
            batch_periodos,
        )
        execute_values(
            cur,
            "INSERT INTO fin_presupuesto (id_presupuesto, periodo_id, ley_presupuesto, monto_inicial, monto_vigente, estado) VALUES %s ON CONFLICT DO NOTHING",
            batch_presupuestos,
        )
    conn.commit()


def migrate_source(conn, config: dict, dry_run: bool = False):
    """Migrate a single source to the target table."""
    base_path = Path(__file__).parent.parent
    csv_path = base_path / config["csv"]

    if not csv_path.exists():
        print(f"  ⚠️ CSV not found: {csv_path}")
        return 0

    rows_migrated = 0
    errors = 0

    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)

        columns = list(config["mapping"].keys())
        insert_sql = f"""
            INSERT INTO {config['table']} ({', '.join(columns)})
            VALUES ({', '.join(['%s'] * len(columns))})
        """

        batch = []
        if config.get("single_row"):
            # Insert just one row derived from the first valid row (or dummy)
            try:
                # Iterate to find one valid row to use as template, or just use empty dict if lambdas support it
                first_row = next(reader, {})
                values = tuple(config["mapping"][col](first_row) for col in columns)
                batch.append(values)
                rows_migrated = 1
                # Stop processing file
            except Exception as e:
                errors += 1
                print(f"    ⚠️ Single row error: {e}")
        else:
            # Standard loop
            seen_keys = set()
            for row in reader:
                # Skip empty rows or invalid names
                if "Nombre completo" in row and not row["Nombre completo"].strip():
                    continue
                if "Cargo o función" in row and not row["Cargo o función"].strip():
                    if config["table"] == "org_cargo":
                        # Skip cargos without name
                        continue

                try:
                    # Deduplication logic for Cargos
                    should_process = True
                    if "unique_on" in config:
                        key_val = config["mapping"][config["unique_on"]](row)
                        if key_val in seen_keys:
                            should_process = False
                        else:
                            seen_keys.add(key_val)
                    elif "unique_composite" in config:
                        # Composite key deduplication
                        key_parts = [
                            row.get(k, "").strip() for k in config["unique_composite"]
                        ]
                        key_val = "-".join(key_parts)
                        if key_val in seen_keys:
                            should_process = False
                        else:
                            seen_keys.add(key_val)

                    if should_process:
                        values = tuple(config["mapping"][col](row) for col in columns)
                        batch.append(values)
                        rows_migrated += 1
                except Exception as e:
                    errors += 1
                    if errors <= 10:
                        print(f"    ⚠️ Row error: {e}")
                        print(f"       Keys: {list(row.keys())}")
                        if "monto_modificacion" in row:
                            val = row.get("monto_modificacion")
                            parsed = parse_decimal(val)
                            print(
                                f"       Monto: {val!r} -> {parsed!r} ({type(parsed)})"
                            )

        if not dry_run and batch:
            cursor = conn.cursor()

            defaults_tables = [
                "sys_periodo",
                "fin_presupuesto",
                "sys_actor",
                "fin_asignacion",
                "sys_acto",
                "org_cargo",
                "org_division",
                "fin_fondo",
                "fin_mecanismo",
                "loc_comuna",
                "loc_region",
                "loc_provincia",
            ]

            if config["table"] in defaults_tables:
                sql = f"INSERT INTO {config['table']} ({', '.join(columns)}) VALUES %s ON CONFLICT DO NOTHING"
                execute_values(cursor, sql, batch)
            else:
                cursor.executemany(insert_sql, batch)

            cursor.close()

    return rows_migrated, errors


def main():
    dry_run = "--dry-run" in sys.argv

    print("🚀 GORE_OS ETL Migration Executor")
    print(f"   Mode: {'DRY-RUN (no changes)' if dry_run else 'EXECUTE'}")
    print(f"   Database: {DATABASE_URL[:50]}...")
    print("=" * 60)

    conn = None
    if not dry_run:
        if not PSYCOPG2_AVAILABLE:
            print("❌ psycopg2 not found. Install with: pip3 install psycopg2-binary")
            sys.exit(1)
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.autocommit = False
            clean_db(conn)  # TRUNCATE ALL
            generate_historical_context(conn)  # PRE-POPULATE PERIODS
        except Exception as e:
            print(f"❌ Database connection or cleanup failed: {e}")
            sys.exit(1)

    total_rows = 0
    total_errors = 0

    for config in MIGRATIONS:
        print(f"\n📦 Migrating: {config['name']}")
        print(f"   Source: {config['csv']}")
        print(f"   Target: {config['table']}")

        try:
            rows, errors = migrate_source(conn, config, dry_run)
            total_rows += rows
            total_errors += errors
            print(f"   ✅ {rows} rows prepared, {errors} errors")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            total_errors += 1

    print()
    print("=" * 60)

    if not dry_run and conn:
        try:
            conn.commit()
            print(f"✅ Migration completed: {total_rows} rows inserted")
        except Exception as e:
            conn.rollback()
            print(f"❌ Migration rolled back: {e}")
        finally:
            conn.close()
    else:
        print(f"📋 Dry-run summary: {total_rows} rows would be inserted")

    if total_errors > 0:
        print(f"⚠️ {total_errors} errors encountered")


if __name__ == "__main__":
    main()
