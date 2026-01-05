"""
Staging Loader (Lean Presheaf Model)
====================================
Transforms normalized CSVs into the "Lean Categorical" SQLite database.
Follows the Yoneda principle: Internalizes dimensions into dense objects.
"""

import csv
import sqlite3
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import re
from stg_schema import (
    StgIPR,
    StgInstitucion,
    StgPresupuesto,
    StgConvenio,
    StgDocumento,
    StgFuncionario,
)


# Paths
NORMALIZED_DIR = Path(__file__).parent.parent / "normalized"
STAGING_DIR = Path(__file__).parent.parent / "staging"
STAGING_DB = STAGING_DIR / "staging_lean.db"


# =============================================================================
# DDL SCHEMA (Lean - 6 Tables)
# =============================================================================

DDL_SCHEMA = """
-- 1. OBJECT: IPR (Terminal Object)
CREATE TABLE IF NOT EXISTS stg_ipr (
    id TEXT PRIMARY KEY,
    codigo_normalizado TEXT NOT NULL,
    bip TEXT,
    nombre TEXT NOT NULL,
    tipo_ipr TEXT CHECK(tipo_ipr IN ('PROYECTO','PROGRAMA')),
    
    -- Internalized Dimensions
    mecanismo_track TEXT CHECK(mecanismo_track IN ('A','B','C','D','E')),
    mecanismo_nombre TEXT,
    fase_actual TEXT, -- Was estado_fase
    estado_evaluacion TEXT, -- Was estado_nombre
    estado_orden INTEGER,
    territorio_codigo TEXT,
    territorio_nombre TEXT,
    provincia_nombre TEXT,
    division_codigo TEXT,
    trazo_nombre TEXT,
    
    -- Attributes
    unidad_tecnica TEXT,
    origen_data TEXT,
    vigencia TEXT,
    codigos_secundarios TEXT,
    kpi_meta TEXT,
    kpi_unidad TEXT,
    programacion_financiera TEXT, -- JSON/Pipe
    fuente_principal TEXT,
    tipologia TEXT,
    etapa TEXT,
    monto_total REAL
);

-- 2. OBJECT: INSTITUCION (Agent)
CREATE TABLE IF NOT EXISTS stg_institucion (
    id TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    tipo TEXT CHECK(tipo IN ('GORE','MUNICIPIO','OSC','EMPRESA','SERVICIO','OTRO')),
    rut TEXT,
    nombre_original TEXT
);

-- 3. MORPHISM: PRESUPUESTO (Value)
CREATE TABLE IF NOT EXISTS stg_presupuesto (
    id TEXT PRIMARY KEY,
    ipr_id TEXT NOT NULL, -- FK to IPR
    
    -- Classifier
    subtitulo TEXT,
    item TEXT,
    asignacion TEXT,
    
    -- Values
    anio INTEGER,
    mes INTEGER,
    monto_vigente REAL,
    monto_devengado REAL,
    monto_pagado REAL,
    fuente TEXT,
    estado_ejecucion TEXT,
    
    -- Details
    tipo_movimiento TEXT, -- LEY, MODIFICACION, DEVENGADO, PAGADO
    numero_documento TEXT,
    
    FOREIGN KEY(ipr_id) REFERENCES stg_ipr(id)
);

-- 4. MORPHISM: CONVENIO (Legal)
CREATE TABLE IF NOT EXISTS stg_convenio (
    id TEXT PRIMARY KEY,
    ipr_id TEXT NOT NULL,
    institucion_id TEXT NOT NULL,
    
    numero_resolucion TEXT,
    tipo_convenio TEXT,
    estado_legal TEXT,
    estado_operacional TEXT,
    referente_tecnico TEXT,
    monto_total REAL,
    
    fecha_inicio DATE,
    fecha_termino DATE,
    fecha_firma DATE,
    estado TEXT,
    
    FOREIGN KEY(ipr_id) REFERENCES stg_ipr(id),
    FOREIGN KEY(institucion_id) REFERENCES stg_institucion(id)
);

-- 5. MORPHISM: DOCUMENTO (Evidence)
CREATE TABLE IF NOT EXISTS stg_documento (
    id TEXT PRIMARY KEY,
    tipo TEXT,
    numero INTEGER,
    fecha DATE,
    materia TEXT,
    ipr_id TEXT,
    institucion_id TEXT,
    convenio_id TEXT, -- Added
    remitente_texto TEXT,
    destinatario_texto TEXT,
    url TEXT,
    monto REAL,
    codigo_interno TEXT,
    tipo_evento TEXT -- Added
);

-- 6. OBJECT: FUNCIONARIO (Resource)
CREATE TABLE IF NOT EXISTS stg_funcionario (
    id TEXT PRIMARY KEY,
    rut TEXT,
    nombre_completo TEXT,
    division_codigo TEXT,
    cargo TEXT,
    calidad_juridica TEXT,
    grado TEXT,
    estamento TEXT,
    calificacion TEXT,
    anio INTEGER,
    mes INTEGER,
    remuneracion_bruta REAL,
    remuneracion_liquida REAL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ipr_cod ON stg_ipr(codigo_normalizado);
CREATE INDEX IF NOT EXISTS idx_presup_ipr ON stg_presupuesto(ipr_id);
CREATE INDEX IF NOT EXISTS idx_conv_ipr ON stg_convenio(ipr_id);
CREATE INDEX IF NOT EXISTS idx_doc_ipr ON stg_documento(ipr_id);
"""


# =============================================================================
# HELPERS
# =============================================================================


def load_csv(file_path: Path) -> list[dict]:
    if not file_path.exists():
        print(f"  ⚠️ File not found: {file_path.name}")
        return []
    with open(file_path, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_decimal(value: str) -> float:
    if not value or value in ("-", "N/A", ""):
        return 0.0
    try:
        cleaned = value.replace("$", "").replace(".", "").replace(",", ".").strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def parse_month(val) -> int:
    month_map = {
        "ENERO": 1,
        "FEBRERO": 2,
        "MARZO": 3,
        "ABRIL": 4,
        "MAYO": 5,
        "JUNIO": 6,
        "JULIO": 7,
        "AGOSTO": 8,
        "SEPTIEMBRE": 9,
        "OCTUBRE": 10,
        "NOVIEMBRE": 11,
        "DICIEMBRE": 12,
    }
    if not val:
        return 0
    val_upper = str(val).upper().strip()
    if val_upper in month_map:
        return month_map[val_upper]
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


class LeanLoader:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

        # In-memory Dimensions (Yoneda Embedding dictionaries)
        self.dim_territorio: Dict[str, Tuple[str, str, str]] = (
            {}
        )  # id -> (codigo, nombre, provincia)
        self.dim_territorio_by_name: Dict[str, str] = {}  # nombre -> id (for lookup)
        self.ipr_250_kpi: Dict[str, Tuple[str, str]] = {}  # bip -> (meta, unidad)
        self.ipr_250_finance: Dict[str, str] = {}  # bip -> json_schedule

        self.dim_mecanismo: Dict[str, Tuple[str, str]] = {}  # id -> (track, nombre)
        self.dim_estado: Dict[str, Tuple[str, str, int]] = (
            {}
        )  # id -> (fase, nombre, orden)
        self.dim_division: Dict[str, str] = {}  # id -> codigo
        self.dim_trazo: Dict[str, str] = {}  # id -> nombre
        self.trazo_map: Dict[str, str] = (
            {}
        )  # bip -> trazo_nombre (from fact_iniciativa_250)
        self.dim_clasificador: Dict[str, Tuple[str, str, str]] = (
            {}
        )  # id -> (subt, item, asig)

        self.institucion_map: Dict[str, str] = {}  # canonical -> id
        self.ipr_map: Dict[str, str] = {}  # codigo_norm -> id

    def connect(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if self.db_path.exists():
            self.db_path.unlink()
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA foreign_keys = ON")
        print(f"✅ Connected to {self.db_path}")

    def create_schema(self):
        self.conn.executescript(DDL_SCHEMA)
        self.conn.commit()
        print("✅ Lean Schema created")

    # =========================================================================
    # INTERNALIZERS (Reading small dims into memory)
    # =========================================================================

    def load_dimensions_to_memory(self):
        print("🧠 Internalizing Dimensions (Yoneda Embedding)...")

        # Territorio
        rows = load_csv(NORMALIZED_DIR / "dimensions" / "dim_territorio_canonico.csv")
        for r in rows:
            tid = r.get("id")
            # FIX: CSV uses 'nombre_oficial', fallback to 'nombre'
            nombre = r.get("nombre_oficial", r.get("nombre", "")).upper()
            # FIX: Generate code if missing
            codigo = r.get("codigo_comuna", nombre[:3])
            provincia = r.get("provincia", "")
            self.dim_territorio[tid] = (codigo, nombre, provincia)
            self.dim_territorio_by_name[nombre] = tid
        print(f"  ✓ Mem: {len(self.dim_territorio)} territorios")

        # Mecanismo
        rows = load_csv(
            NORMALIZED_DIR / "dimensions" / "dim_mecanismo_financiamiento.csv"
        )
        for r in rows:
            self.dim_mecanismo[r.get("id")] = (r.get("track", "A"), r.get("nombre", ""))
        print(f"  ✓ Mem: {len(self.dim_mecanismo)} mecanismos")

        # Estado
        rows = load_csv(NORMALIZED_DIR / "dimensions" / "dim_estado_ipr.csv")
        for r in rows:
            orden = 0
            try:
                orden = int(r.get("orden", 0))
            except:
                pass
            self.dim_estado[r.get("id")] = (
                r.get("fase", ""),
                r.get("nombre", ""),
                orden,
            )
        print(f"  ✓ Mem: {len(self.dim_estado)} estados")

        # Division
        rows = load_csv(NORMALIZED_DIR / "dimensions" / "dim_division.csv")
        for r in rows:
            self.dim_division[r.get("id")] = r.get("codigo", "")
        print(f"  ✓ Mem: {len(self.dim_division)} divisiones")

        # Trazo 250
        rows = load_csv(NORMALIZED_DIR / "dimensions" / "dim_trazo_250.csv")
        for r in rows:
            self.dim_trazo[r.get("id")] = r.get("trazo", "")

        # Trazo Links (Fact -> Map) & Enriched IPR Attributes (KPIs, Schedule)
        rows_fact = load_csv(NORMALIZED_DIR / "facts" / "fact_iniciativa_250.csv")
        for r in rows_fact:
            bip = r.get("bip") or r.get("bip_base")
            trazo = r.get("trazo_primario")
            if bip:
                # Trazo
                if trazo:
                    self.trazo_map[bip] = trazo

                # KPIs (medida, unidad)
                medida = r.get("medida", "")
                unidad = r.get("unidad", "")
                if medida or unidad:
                    self.ipr_250_kpi[bip] = (medida, unidad)

                # Financial Schedule (q1_2026...y2029_plus)
                schedule = {}
                cols = [
                    "q1_2026",
                    "q2_2026",
                    "q3_2026",
                    "q4_2026",
                    "q1_2027",
                    "q2_2027",
                    "q3_2027",
                    "q4_2027",
                    "q1_2028",
                    "q2_2028",
                    "q3_2028",
                    "q4_2028",
                    "y2029_plus",
                ]
                has_data = False
                for c in cols:
                    val = r.get(c, "")
                    if val and val != "0" and val != "0.0":
                        schedule[c] = val
                        has_data = True

                if has_data:
                    # Simple Pipe format: q1_2026:100|q2_2026:200
                    self.ipr_250_finance[bip] = "|".join(
                        [f"{k}:{v}" for k, v in schedule.items()]
                    )

        print(
            f"  ✓ Mem: {len(self.dim_trazo)} trazos definitions, {len(self.trazo_map)} trazo links"
        )
        print(
            f"  ✓ Mem: {len(self.ipr_250_kpi)} KPIs, {len(self.ipr_250_finance)} financial schedules"
        )

        # Clasificador
        rows = load_csv(NORMALIZED_DIR / "dimensions" / "dim_clasificador_presup.csv")
        for r in rows:
            self.dim_clasificador[r.get("id")] = (
                r.get("subtitulo", ""),
                r.get("item", ""),
                r.get("asignacion", ""),
            )
        print(f"  ✓ Mem: {len(self.dim_clasificador)} clasificadores")

    # =========================================================================
    # DENSE OBJECT LOADERS
    # =========================================================================

    def load_iprs_dense(self):
        """
        Load all initiatives (unificada, idis, and basic dim) to ensure fact links resolve.
        categorical density approach: colimit of all source IDs.
        """
        sources = [
            (
                "dimensions/dim_iniciativa.csv",
                {"nombre": "nombre_norm", "codigo": "codigo"},
            ),
            (
                "dimensions/dim_iniciativa_idis.csv",
                {"nombre": "nombre_iniciativa", "codigo": "cod_unico"},
            ),
            (
                "dimensions/dim_iniciativa_unificada.csv",
                {"nombre": "nombre_iniciativa", "codigo": "codigo_normalizado"},
            ),
            (
                "facts/fact_fril.csv",
                {"nombre": "nombre_iniciativa", "codigo": "codigo"},
            ),
        ]

        total_rows = 0
        for rel_path, mapping in sources:
            path = NORMALIZED_DIR / rel_path
            if not path.exists():
                continue
            rows = load_csv(path)
            total_rows += len(rows)

            for row in rows:
                ipr_id = row.get("id")
                if not ipr_id:
                    continue

                nombre = row.get(
                    mapping["nombre"], row.get("nombre_iniciativa", "SIN NOMBRE")
                )
                codigo = row.get(
                    mapping["codigo"], row.get("codigo_normalizado", "S/C")
                )
                bip = row.get("bip")

                # Update Map for name-based lookup if needed
                self.ipr_map[codigo] = ipr_id

                # Embed Mecanismo
                mec_id = row.get("mecanismo_id")
                mec_data = self.dim_mecanismo.get(mec_id, ("A", "Desconocido"))

                # Embed Territorio
                comuna_name = row.get("comuna", "").upper()
                tid = self.dim_territorio_by_name.get(comuna_name)
                # (codigo, nombre, provincia)
                terr_data = self.dim_territorio.get(tid, ("", comuna_name, ""))

                # Embed Trazo & Strategic Data (KPI, Finance)
                trazo_nombre = ""
                kpi_meta = ""
                kpi_unidad = ""
                finance_schedule = ""

                # Try lookup by BIP first, then Code
                keys_to_try = [bip, codigo]
                for k in keys_to_try:
                    if not k:
                        continue
                    if not trazo_nombre:
                        trazo_nombre = self.trazo_map.get(k, "")
                    if not kpi_meta:
                        meta_data = self.ipr_250_kpi.get(k, ("", ""))
                        kpi_meta = meta_data[0]
                        kpi_unidad = meta_data[1]
                    if not finance_schedule:
                        finance_schedule = self.ipr_250_finance.get(k, "")

                # Secondary Codes
                sec_codes = []
                for k in [
                    "codigo_fril",
                    "codigo_convenios",
                    "codigo_progs",
                    "cod_unico_idis",
                ]:
                    val = row.get(k)
                    if val:
                        sec_codes.append(f"{k}:{val}")
                sec_codes_str = "|".join(sec_codes)

                self.conn.execute(
                    """INSERT OR IGNORE INTO stg_ipr (
                        id, codigo_normalizado, bip, nombre, tipo_ipr,
                        mecanismo_track, mecanismo_nombre,
                        fase_actual, estado_evaluacion, estado_orden,
                        territorio_codigo, territorio_nombre, provincia_nombre,
                        division_codigo, trazo_nombre,
                        unidad_tecnica, origen_data, vigencia, codigos_secundarios,
                        kpi_meta, kpi_unidad, programacion_financiera,
                        fuente_principal, tipologia, etapa, monto_total
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        ipr_id,
                        codigo,
                        bip,
                        nombre,
                        row.get("tipo_ipr", "PROYECTO"),
                        mec_data[0],
                        mec_data[1],
                        row.get("etapa", ""),  # fase_actual
                        row.get(
                            "estado_actual", row.get("rate_actual", "")
                        ),  # estado_evaluacion
                        0,  # estado_orden default
                        terr_data[0],
                        terr_data[1],
                        terr_data[2],  # provincia
                        "",  # division
                        trazo_nombre,
                        row.get("unidad_tecnica", ""),
                        row.get("origen", "NORMALIZED"),
                        row.get("vigencia", ""),
                        sec_codes_str,
                        kpi_meta,
                        kpi_unidad,
                        finance_schedule,
                        row.get("fuente_financiamiento", row.get("fuente_principal")),
                        row.get("tipologia"),
                        row.get("etapa"),
                        parse_decimal(row.get("costo_total", "0")),
                    ),
                )
        self.conn.commit()
        print(f"  ✓ Total Dense IPRs loaded from multiple sources: {total_rows}")

    def load_instituciones(self):
        """Loads institutions from unificada and original dim files."""
        sources = [
            "dimensions/dim_institucion.csv",
            "dimensions/dim_institucion_unificada.csv",
        ]
        valid_tipos = {"GORE", "MUNICIPIO", "OSC", "EMPRESA", "SERVICIO", "OTRO"}
        total_rows = 0

        for rel_path in sources:
            path = NORMALIZED_DIR / rel_path
            if not path.exists():
                continue
            rows = load_csv(path)
            total_rows += len(rows)

            for row in rows:
                iid = row.get("id")
                if not iid:
                    continue
                canonical = row.get(
                    "canonical_name",
                    row.get(
                        "nombre_normalizado",
                        row.get("nombre_raw", row.get("nombre_original", "")),
                    ),
                )

                # Logic for typing
                tipo_raw = row.get("tipo_institucion", "OTRO").upper().strip()
                if tipo_raw in valid_tipos:
                    tipo = tipo_raw
                elif "MUNICIPALIDAD" in canonical.upper():
                    tipo = "MUNICIPIO"
                elif "GORE" in canonical.upper():
                    tipo = "GORE"
                elif any(
                    k in canonical.upper()
                    for k in ["ASOCIACIÓN", "CLUB", "JUNTA", "ONG"]
                ):
                    tipo = "OSC"
                elif any(
                    k in canonical.upper() for k in ["S.A.", "LTDA", "SPA", "EMPRESA"]
                ):
                    tipo = "EMPRESA"
                elif any(k in canonical.upper() for k in ["SERVICIO", "MINISTERIO"]):
                    tipo = "SERVICIO"
                else:
                    tipo = "OTRO"

                self.conn.execute(
                    "INSERT OR IGNORE INTO stg_institucion (id, canonical_name, tipo, rut, nombre_original) VALUES (?, ?, ?, ?, ?)",
                    (
                        iid,
                        canonical,
                        tipo,
                        row.get("rut"),
                        row.get("nombre_original", ""),
                    ),
                )
                self.institucion_map[canonical.upper()] = iid
        self.conn.commit()
        print(f"  ✓ Institutions loaded from multiple sources: {total_rows}")

    # =============================================================================
    # 3. LOAD BUDGET (Presupuesto) - Dense & Granular
    # =============================================================================
    def load_presupuesto(self):
        """
        Master loader for budget data.
        1. Ley (Initial Lines)
        2. Modificaciones
        3. Ejecucion (Mensual)
        """
        self._load_presupuesto_ley()
        self._load_presupuesto_modificaciones()
        self._load_presupuesto_ejecucion()

    def _load_presupuesto_ley(self):
        print(f"Loading Presupuesto (LEY) from fact_linea_presupuestaria...")
        path = NORMALIZED_DIR / "facts/fact_linea_presupuestaria.csv"
        if not path.exists():
            return

        batch = []
        # cache valid iprs
        valid_ipr_ids = {r[0] for r in self.conn.execute("SELECT id FROM stg_ipr")}

        rows = load_csv(path)
        for row in rows:
            p_id = row.get("id", str(uuid.uuid4()))
            ipr_id = row.get("iniciativa_id", "")
            if ipr_id not in valid_ipr_ids:
                continue

            monto = parse_decimal(
                row.get("monto_final_aprobado") or row.get("gasto_vigente") or "0"
            )

            # Initial Budget is usually Monto Vigente at start, or Ley.
            # We assume this file represents the snapshot of lines.

            obj = StgPresupuesto(
                id=p_id,
                ipr_id=ipr_id,
                subtitulo=row.get("subtitulo", ""),
                item=row.get("item", ""),
                asignacion=row.get("asignacion", ""),
                monto_vigente=monto,
                tipo_movimiento="LEY",
                anio=int(row.get("anio_presupuestario") or 0),
                fuente="fact_linea",
            )
            batch.append(obj)

        self._insert_presupuesto_batch(batch)

    def _load_presupuesto_modificaciones(self):
        print(f"Loading Presupuesto (MODIF) from fact_modificacion...")
        path = NORMALIZED_DIR / "facts/fact_modificacion.csv"
        if not path.exists():
            return

        # We need to map modification lines to IPRs.
        # Modificaciones link to Subt/Item/Asig. We need a heuristic or direct link.
        # Check if fact_modificacion has iniciativa_id?
        # Inspecting CSV header: id, subtitulo, ... vigente ...
        # It DOES NOT seem to have iniciativa_id.
        # Constraint: Modifications are global or per line?
        # If per line, we need line_id.
        # Current CSV has 'id' but no 'linea_id'.
        # Attempt: If we can't link to IPR, we can't load into StgPresupuesto (which requires ipr_id).
        # Strategy: Skip for now if no link, or try to link via classifier + manual match?
        # Decided: Skip modifications that are not linked to an IPR.
        # Wait, StgPresupuesto represents specific IPR budget execution. Global modifications might belong to "Partida"?
        # Recommendation: Only load if we can link. Since we can't easily, we might skip this pass
        # OR assume they are applied to the "Global" IPR?
        # Let's SKIP for this iteration to avoid bad data, but log awareness.
        print("  WARNING: fact_modificacion.csv lacks lineage to IPR. Skipping load.")

    def _load_presupuesto_ejecucion(self):
        print(f"Loading Presupuesto (EXEC) from fact_ejecucion_mensual...")
        path = NORMALIZED_DIR / "facts/fact_ejecucion_mensual.csv"
        if not path.exists():
            return

        # This table links to 'linea_id'. We need to resolve linea_id -> ipr_id
        # Build map: linea_id -> (ipr_id, subt, item, asig)
        linea_map = {}
        rows_linea = load_csv(NORMALIZED_DIR / "facts/fact_linea_presupuestaria.csv")
        for r in rows_linea:
            linea_map[r.get("id")] = (
                r.get("iniciativa_id"),
                r.get("subtitulo"),
                r.get("item"),
                r.get("asignacion"),
                r.get("anio_presupuestario"),
            )

        batch = []
        rows = load_csv(path)
        for row in rows:
            p_id = row.get("id", str(uuid.uuid4()))
            linea_id = row.get("linea_id")

            linea_data = linea_map.get(linea_id)
            if not linea_data or not linea_data[0]:
                continue

            ipr_id, subt, item, asig, anio = linea_data

            monto = parse_decimal(row.get("monto", "0"))
            tipo_orig = row.get("tipo", "DEVENGADO").upper()  # DEVENGADO / PAGADO
            tipo = "DEVENGADO" if "REAL" in tipo_orig else tipo_orig

            # Create distinct record for each monthly execution event
            obj = StgPresupuesto(
                id=p_id,
                ipr_id=ipr_id,
                subtitulo=subt,
                item=item,
                asignacion=asig,
                anio=int(anio or 0),
                mes=int(row.get("mes", 0)),  # 1-12
                # We map monto to devengado OR pagado based on type
                monto_devengado=monto if tipo == "DEVENGADO" else Decimal("0"),
                monto_pagado=monto if tipo == "PAGADO" else Decimal("0"),
                tipo_movimiento=tipo,
                fuente="fact_ejecucion",
            )
            batch.append(obj)

        self._insert_presupuesto_batch(batch)

    def _insert_presupuesto_batch(self, batch: List[StgPresupuesto]):
        if not batch:
            return
        self.conn.executemany(
            """INSERT INTO stg_presupuesto (
                id, ipr_id, subtitulo, item, asignacion, 
                anio, mes, monto_vigente, monto_devengado, monto_pagado, 
                tipo_movimiento, numero_documento, fuente
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    b.id,
                    b.ipr_id,
                    b.subtitulo,
                    b.item,
                    b.asignacion,
                    b.anio,
                    b.mes,
                    float(b.monto_vigente),
                    float(b.monto_devengado),
                    float(b.monto_pagado),
                    b.tipo_movimiento,
                    b.numero_documento,
                    "loader",
                )
                for b in batch
            ],
        )
        self.conn.commit()
        print(f"  Inserted {len(batch)} Presupuesto records.")

    def _load_eventos_documentales(self):
        # Implementation for Events linked to Convenios
        pass

    # =============================================================================
    # 4. LOAD CONVENIOS - Dense
    # =============================================================================
    def load_convenios(self):
        """
        Loads fact_convenio.csv into stg_convenio.
        Uses iniciativa_id (UUID) to link to StgIPR.
        Populates extra fields for Omega Compliance.
        """
        print(f"Loading Convenios from {NORMALIZED_DIR / 'facts/fact_convenio.csv'}...")
        path = NORMALIZED_DIR / "facts/fact_convenio.csv"
        if not path.exists():
            print(f"  WARNING: {path} not found. Skipping.")
            return

        batch = []
        valid_ipr_ids = set()
        for r in self.conn.execute("SELECT id FROM stg_ipr"):
            valid_ipr_ids.add(r[0])
        valid_inst_ids = set()
        for r in self.conn.execute("SELECT id FROM stg_institucion"):
            valid_inst_ids.add(r[0])

        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                c_id = row.get("id", str(uuid.uuid4()))
                ipr_id = row.get("iniciativa_id", "")
                inst_id = row.get("institucion_id", "")

                if ipr_id not in valid_ipr_ids or inst_id not in valid_inst_ids:
                    continue

                monto = Decimal("0")
                try:
                    # 'monto_fndr_ms' seems to be the total amount
                    val = row.get("monto_fndr_ms") or "0"
                    monto = Decimal(val)
                except:
                    pass

                fecha_firma = row.get("fecha_firma_convenio", "")

                obj = StgConvenio(
                    id=c_id,
                    ipr_id=ipr_id,
                    institucion_id=inst_id,
                    numero_resolucion=row.get("numero_resolucion"),
                    tipo_convenio=row.get("tipo_convenio", "MANDATO"),
                    estado_legal=row.get("estado_cgr_norm", "TRAMITE"),
                    estado_operacional=row.get("estado_operacional", ""),
                    referente_tecnico=row.get("referente_tecnico", ""),
                    fecha_firma=fecha_firma,
                    monto_total=monto,
                    fecha_inicio=None,
                    fecha_termino=None,
                    estado=row.get("estado_convenio_norm", ""),
                )
                batch.append(obj)

        if batch:
            self.conn.executemany(
                "INSERT INTO stg_convenio (id, ipr_id, institucion_id, numero_resolucion, tipo_convenio, estado_legal, estado_operacional, referente_tecnico, fecha_firma, monto_total, estado) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        b.id,
                        b.ipr_id,
                        b.institucion_id,
                        b.numero_resolucion,
                        b.tipo_convenio,
                        b.estado_legal,
                        b.estado_operacional,
                        b.referente_tecnico,
                        b.fecha_firma,
                        float(b.monto_total),
                        b.estado,
                    )
                    for b in batch
                ],
            )
            self.conn.commit()
            print(f"  Inserted {len(batch)} Convenio records.")

    # =============================================================================
    # 5. LOAD DOCUMENTS - Dense
    # =============================================================================
    def load_documentos(self):
        """
        Loads doc_documento.csv into stg_documento.
        Note: Checks for ipr_id?
        If doc_documento doesnt have ipr_id, we might need a relation table.
        For now, loading basic metadata.
        """
        print(
            f"Loading Documentos from {NORMALIZED_DIR / 'documents/doc_documento.csv'}..."
        )
        path = NORMALIZED_DIR / "documents/doc_documento.csv"
        if not path.exists():
            print(f"  WARNING: {path} not found. Skipping.")
            return

        batch = []
        valid_ipr_ids = set()
        for r in self.conn.execute("SELECT id FROM stg_ipr"):
            valid_ipr_ids.add(r[0])

        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                d_id = row.get("id", str(uuid.uuid4()))
                ipr_id = row.get("iniciativa_id", "")  # Try to find ipr link
                if not ipr_id or ipr_id not in valid_ipr_ids:
                    ipr_id = None

                # Parse monto
                monto_val = Decimal("0")
                monto_raw = row.get("monto")
                if monto_raw:
                    try:
                        clean_monto = re.sub(r"[^\d\.]", "", str(monto_raw))
                        monto_val = Decimal(clean_monto)
                    except:
                        pass

                obj = StgDocumento(
                    id=d_id,
                    ipr_id=ipr_id,
                    institucion_id="",
                    tipo=row.get("tipo_documento", "OFICIO"),
                    numero=row.get("numero_documento", ""),
                    fecha=row.get("fecha_documento", ""),
                    url=row.get("link_documento_url", ""),
                    materia=row.get("materia", ""),
                    remitente_texto=row.get("remitente", ""),
                    destinatario_texto=row.get("destinatario", ""),
                    monto=monto_val,
                    codigo_interno=row.get("codigo", ""),
                )
                batch.append(obj)

        if batch:
            self.conn.executemany(
                "INSERT INTO stg_documento (id, tipo, numero, fecha, materia, ipr_id, institucion_id, remitente_texto, destinatario_texto, url, monto, codigo_interno) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        b.id,
                        b.tipo,
                        b.numero,
                        b.fecha,
                        b.materia,
                        b.ipr_id,
                        b.institucion_id,
                        b.remitente_texto,
                        b.destinatario_texto,
                        b.url,
                        float(b.monto),
                        b.codigo_interno,
                    )
                    for b in batch
                ],
            )
            self.conn.commit()
            print(f"  Inserted {len(batch)} Documento records.")

        # Load additional document types
        self._load_eventos_documentales()
        self._load_rendiciones_8pct()

    def _load_eventos_documentales(self):
        print(
            f"Loading Eventos Documentales from {NORMALIZED_DIR / 'facts/fact_evento_documental.csv'}..."
        )
        path = NORMALIZED_DIR / "facts/fact_evento_documental.csv"
        if not path.exists():
            return

        batch = []
        rows = load_csv(path)
        for row in rows:
            d_id = row.get("id", str(uuid.uuid4()))
            convenio_id = row.get("convenio_id")

            tipo = row.get("tipo_resolucion_norm", "RESOLUCION")
            fecha = row.get("fecha_documento")
            numero = 0
            try:
                numero = int(row.get("numero_documento", "0"))
            except:
                pass

            obj = StgDocumento(
                id=d_id,
                tipo=tipo,
                numero=numero,
                fecha=fecha,
                materia=row.get("observacion_raw", ""),
                convenio_id=convenio_id,
                tipo_evento=row.get("tipo_evento_id", ""),
            )
            batch.append(obj)

        if batch:
            self.conn.executemany(
                "INSERT INTO stg_documento (id, tipo, numero, fecha, materia, convenio_id, tipo_evento) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        b.id,
                        b.tipo,
                        b.numero,
                        b.fecha,
                        b.materia,
                        b.convenio_id,
                        b.tipo_evento,
                    )
                    for b in batch
                ],
            )
            self.conn.commit()
            print(f"  Inserted {len(batch)} Eventos Documentales.")

    def _load_rendiciones_8pct(self):
        print(
            f"Loading Rendiciones 8% from {NORMALIZED_DIR / 'facts/fact_rendicion_8pct.csv'}..."
        )
        path = NORMALIZED_DIR / "facts/fact_rendicion_8pct.csv"
        if not path.exists():
            return

        batch = []
        rows = load_csv(path)
        for row in rows:
            d_id = row.get("id", str(uuid.uuid4()))
            inst_id = row.get("institucion_id")
            codigo = row.get("codigo")
            ipr_id = self.ipr_map.get(codigo)

            monto = parse_decimal(row.get("monto_transferido", "0"))

            obj = StgDocumento(
                id=d_id,
                tipo="RENDICION_8PCT",
                ipr_id=ipr_id,
                institucion_id=inst_id,
                materia=f"Rendicion: {row.get('nombre_iniciativa','')}",
                fecha=row.get("fecha_transferencia"),
                monto=monto,
                remitente_texto=row.get("nombre_institucion", ""),
                codigo_interno=codigo,
            )
            batch.append(obj)

        if batch:
            self.conn.executemany(
                """INSERT INTO stg_documento (
                    id, tipo, ipr_id, institucion_id, materia, fecha, monto, remitente_texto, codigo_interno
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    (
                        b.id,
                        b.tipo,
                        b.ipr_id,
                        b.institucion_id,
                        b.materia,
                        b.fecha,
                        float(b.monto),
                        b.remitente_texto,
                        b.codigo_interno,
                    )
                    for b in batch
                ],
            )
            self.conn.commit()
            print(f"  Inserted {len(batch)} Rendiciones 8%.")

    # =============================================================================
    # 6. LOAD FUNCIONARIOS - Dense
    # =============================================================================
    def load_funcionarios(self):
        """
        Loads fact_funcionario.csv into stg_funcionario.
        Infers Division from cargo_funcion using Regex.
        """
        path = NORMALIZED_DIR / "facts/fact_funcionario.csv"
        print(f"Loading Funcionarios from {path}...")
        if not path.exists():
            print(f"  WARNING: {path} not found. Skipping.")
            return

        # Simple Regex Map for Division
        div_map = {
            r"DIPLADE": "DIPLADE",
            r"PLANIFICACI[ÓO]N": "DIPLADE",
            r"DIFOI": "DIFOI",
            r"FOMENTO": "DIFOI",
            r"INDUSTRIA": "DIFOI",
            r"DIT": "DIT",
            r"INFRAESTRUCTURA": "DIT",
            r"TRANSPORTE": "DIT",
            r"DIDESO": "DIDESO",
            r"SOCIAL": "DIDESO",
            r"DIPIR": "DIPIR",
            r"PRESUPUESTO": "DIPIR",
            r"INVERSI[ÓO]N": "DIPIR",
            r"DAF": "DAF",
            r"ADMINISTRACI[ÓO]N": "DAF",
            r"FINANZAS": "DAF",
            r"GABINETE": "GABINETE",
            r"JUR[ÍI]DICA": "JURIDICA",
            r"CONTROL": "CONTROL",
        }

        batch = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("id"):
                    continue

                # Parse Cargo -> Division
                cargo = (row.get("cargo_funcion") or "").upper()
                division = "S/I"
                for pattern, code in div_map.items():
                    if re.search(pattern, cargo):
                        division = code
                        break

                mes_str = row.get("mes", "0")
                mes_int = self.parse_month_name(mes_str)

                # Costo Mensual
                rem_bruta = Decimal("0")
                try:
                    val = row.get("remuneracion_bruta", "0")
                    rem_bruta = Decimal(val)
                except:
                    pass

                rem_liquida = Decimal("0")
                try:
                    val = row.get("remuneracion_liquida", "0")
                    rem_liquida = Decimal(val)
                except:
                    pass

                obj = StgFuncionario(
                    id=row["id"],
                    nombre_completo=row.get("nombre_completo", ""),
                    rut=row.get("rut"),
                    division_codigo=division,
                    cargo=cargo,
                    calidad_juridica=row.get("tipo_vinculo", ""),
                    grado=row.get("grado_eus"),
                    estamento=row.get("estamento", ""),
                    calificacion=row.get("calificacion_profesional", ""),
                    anio=int(row.get("anio", 0)),
                    mes=mes_int,
                    remuneracion_bruta=rem_bruta,
                    remuneracion_liquida=rem_liquida,
                )
                batch.append(obj)

        if batch:
            self.conn.executemany(
                """INSERT INTO stg_funcionario (
                    id, rut, nombre_completo, division_codigo, cargo, 
                    calidad_juridica, grado, estamento, calificacion, anio, mes, 
                    remuneracion_bruta, remuneracion_liquida
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    (
                        b.id,
                        b.rut,
                        b.nombre_completo,
                        b.division_codigo,
                        b.cargo,
                        b.calidad_juridica,
                        b.grado,
                        b.estamento,
                        b.calificacion,
                        b.anio,
                        b.mes,
                        float(b.remuneracion_bruta),
                        float(b.remuneracion_liquida),
                    )
                    for b in batch
                ],
            )
            self.conn.commit()
            print(f"  Inserted {len(batch)} Funcionario records.")

    def parse_month_name(self, mes_name: str) -> int:
        """Helper to parse Spanish month names."""
        m_map = {
            "ENERO": 1,
            "FEBRERO": 2,
            "MARZO": 3,
            "ABRIL": 4,
            "MAYO": 5,
            "JUNIO": 6,
            "JULIO": 7,
            "AGOSTO": 8,
            "SEPTIEMBRE": 9,
            "OCTUBRE": 10,
            "NOVIEMBRE": 11,
            "DICIEMBRE": 12,
        }
        try:
            return int(mes_name)
        except:
            return m_map.get(mes_name.upper().strip(), 0)

    def run(self):
        print("=" * 60)
        print("STAGING LOADER (LEAN) - Internalizing Dimensions")
        print("=" * 60)

        self.connect()
        self.create_schema()

        self.load_dimensions_to_memory()

        print("\n🚀 Populating Dense Objects...")
        self.load_instituciones()
        self.load_iprs_dense()

        print("\n📎 Populating Morphisms...")
        self.load_presupuesto()
        self.load_convenios()
        self.load_documentos()
        self.load_funcionarios()

        print("\n" + "=" * 60)
        print("LEAN LOAD COMPLETE")
        self.conn.close()


if __name__ == "__main__":
    LeanLoader(STAGING_DB).run()
