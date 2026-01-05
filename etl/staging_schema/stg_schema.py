"""
Staging Schema Definitions (Lean Presheaf Model)
================================================
Categorical Data Model v2: "Density over Fragmentation"

Objects: 6 Dense Entities (Colimits of dimensions)
Morphisms: Explicit FKs preserving structure
"""

from dataclasses import dataclass
from typing import Optional, Literal
from decimal import Decimal
from datetime import date
import uuid


# =============================================================================
# OBJECTS (Dense Entities)
# =============================================================================


@dataclass
class StgIPR:
    """
    Object: IPR (Intervención Pública Regional)
    Role: Terminal Object of the Domain

    Internalizes: Mecanismo, Estado, Territorio, Division
    """

    id: str
    codigo_normalizado: str  # Unique ID
    bip: Optional[str] = None
    nombre: str = ""
    tipo_ipr: Literal["PROYECTO", "PROGRAMA"] = "PROYECTO"

    # Internalized Dimensions (Yoneda Embedding)
    mecanismo_track: Literal["A", "B", "C", "D", "E"] = "A"
    mecanismo_nombre: str = ""
    fase_actual: str = ""  # Was estado_fase
    estado_evaluacion: str = ""  # Was estado_nombre
    estado_orden: int = 0  # Added
    territorio_codigo: str = ""  # Comuna ISO code
    territorio_nombre: str = ""
    provincia_nombre: str = ""  # Added
    division_codigo: str = ""  # DIPLADE, DIPIR, etc.
    trazo_nombre: str = ""  # Added

    # Attributes
    unidad_tecnica: str = ""  # Added
    origen_data: str = ""  # Added
    vigencia: str = ""  # Added
    codigos_secundarios: str = ""  # Added
    kpi_meta: str = ""  # Added
    kpi_unidad: str = ""  # Added
    programacion_financiera: str = ""  # Added
    fuente_principal: str = ""
    tipologia: Optional[str] = None
    etapa: Optional[str] = None
    monto_total: Decimal = Decimal("0")


@dataclass
class StgInstitucion:
    """
    Object: Institucion
    Role: Agent Object

    Internalizes: Tipo (Enum)
    """

    id: str
    canonical_name: str
    tipo: Literal["GORE", "MUNICIPIO", "OSC", "EMPRESA", "SERVICIO", "OTRO"]
    rut: Optional[str] = None
    nombre_original: str = ""  # Added


@dataclass
class StgPresupuesto:
    """
    Object: Presupuesto (Budget Execution)
    Role: Value Morphism (IPR → R)

    Collapses: Linea + Ejecucion + Clasificador
    """

    id: str
    ipr_id: str  # Morphism source

    # Internalized Classifier
    subtitulo: str
    item: str
    asignacion: str

    # Value attributes
    anio: int = 0
    mes: int = 0  # 0 for aggregated yearly rows
    monto_vigente: Decimal = Decimal("0")
    monto_devengado: Decimal = Decimal("0")
    monto_pagado: Decimal = Decimal("0")

    fuente: str = ""
    tipo_movimiento: str = "LEY"  # Added (LEY, MODIFICACION, DEVENGADO, PAGADO)
    numero_documento: str = ""  # Added (For modifications)


@dataclass
class StgConvenio:
    """
    Object: Convenio
    Role: Legal Morphism (IPR → Institucion)
    """

    id: str
    ipr_id: str  # Source
    institucion_id: str  # Target

    numero_resolucion: Optional[str] = None
    tipo_convenio: str = "MANDATO"  # Added
    estado_legal: str = "TRAMITE"  # Added (CGR Norm/Raw)
    estado_operacional: str = ""  # Added
    referente_tecnico: str = ""  # Added

    monto_total: Decimal = Decimal("0")

    fecha_inicio: Optional[date] = None
    fecha_termino: Optional[date] = None
    fecha_firma: Optional[str] = None  # Added (ISO String)

    estado: str = ""


@dataclass
class StgDocumento:
    """
    Object: Documento
    Role: Evidence Morphism (Trace)
    """

    id: str
    tipo: Literal["MEMO", "OFICIO", "CARTA", "RESOLUCION", "OTRO"]
    numero: int = 0
    fecha: Optional[date] = None
    materia: str = ""

    # Optional links (Orphan vs Linked)
    ipr_id: Optional[str] = None
    institucion_id: Optional[str] = None
    convenio_id: Optional[str] = None  # Added
    remitente_texto: str = ""
    destinatario_texto: str = ""
    url: Optional[str] = None

    # Extra attributes for Rendiciones
    monto: Decimal = Decimal("0")
    codigo_interno: str = ""
    tipo_evento: str = ""  # Added


@dataclass
class StgFuncionario:
    """
    Object: Funcionario
    Role: Resource Object
    """

    id: str
    nombre_completo: str = ""
    rut: Optional[str] = None
    division_codigo: str = ""
    cargo: str = ""
    calidad_juridica: str = ""
    grado: Optional[str] = None
    estamento: str = ""  # Added
    calificacion: str = ""  # Added

    # Compensation (Temporal slice)
    anio: int = 0
    mes: int = 0
    remuneracion_bruta: Decimal = Decimal("0")
    remuneracion_liquida: Decimal = Decimal("0")


# =============================================================================
# SCHEMA REGISTRY
# =============================================================================

STAGING_TABLES = [
    StgIPR,
    StgInstitucion,
    StgPresupuesto,
    StgConvenio,
    StgDocumento,
    StgFuncionario,
]


def get_table_name(cls) -> str:
    """Convert class name to SQL table name (snake_case)."""
    import re

    name = cls.__name__
    name = name[3:] if name.startswith("Stg") else name
    return "stg_" + re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
