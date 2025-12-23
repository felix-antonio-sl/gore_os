"""
ETL Transform Library for GORE_OS
Implementa funciones de transformación reutilizables para pipelines ETL.
"""

import re
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from typing import Optional, Dict, Any, List, Tuple


# =============================================================================
# TRANSFORMACIONES DE TEXTO
# =============================================================================


def trim(value: str) -> str:
    """Elimina espacios externos."""
    return value.strip() if value else ""


def trim_upper(value: str) -> str:
    """Trim y uppercase."""
    return value.strip().upper() if value else ""


def normalize_whitespace(value: str) -> str:
    """Normaliza espacios múltiples a uno solo."""
    return re.sub(r"\s+", " ", value.strip()) if value else ""


# =============================================================================
# TRANSFORMACIONES DE MONTOS
# =============================================================================


def parse_decimal_clp(value: str) -> Optional[Decimal]:
    """
    Convierte montos en formato chileno a Decimal.

    Formatos soportados:
    - "$ 1.234.567"
    - "M$ 1.234,56"
    - "1234567"
    - "$ -" (retorna 0)

    Args:
        value: String con monto

    Returns:
        Decimal o None si es inválido
    """
    if not value or value.strip() in ["", "$ -", "-", "s/n", "sin datos"]:
        return Decimal("0")

    # Remover símbolos y normalizar
    cleaned = value.strip()
    cleaned = cleaned.replace("$", "").replace("M$", "")
    cleaned = cleaned.replace(".", "")  # Miles
    cleaned = cleaned.replace(",", ".")  # Decimales
    cleaned = cleaned.strip()

    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


# =============================================================================
# TRANSFORMACIONES DE FECHAS
# =============================================================================


def parse_date_multi(value: str, formats: List[str] = None) -> Optional[date]:
    """
    Parsea fechas en múltiples formatos.

    Args:
        value: String con fecha
        formats: Lista de formatos a intentar (default: formatos chilenos comunes)

    Returns:
        date o None
    """
    if not value or value.strip() in ["", "Indefinido", "s/n"]:
        return None

    if formats is None:
        formats = [
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%d/%m/%y",
            "%Y-%m-%d",
            "%d.%m.%Y",
        ]

    cleaned = value.strip()

    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue

    return None


# =============================================================================
# TRANSFORMACIONES DE NOMBRES (FUNCIONARIOS)
# =============================================================================


def parse_nombre_completo(value: str) -> Dict[str, Optional[str]]:
    """
    Parsea nombres en formato "Apellido1 Apellido2, Nombres".

    Maneja casos especiales:
    - Apellidos compuestos: "De La Fuente", "San Martín", etc.
    - Nombres múltiples: "Juan Pablo", "María José"
    - Sin apellido materno

    Args:
        value: Nombre completo en formato chileno

    Returns:
        Dict con apellido_paterno, apellido_materno, nombres

    Examples:
        >>> parse_nombre_completo("Aburto Contreras, Abraham Aníbal")
        {'apellido_paterno': 'Aburto', 'apellido_materno': 'Contreras', 'nombres': 'Abraham Aníbal'}

        >>> parse_nombre_completo("De La Fuente Torres, María José")
        {'apellido_paterno': 'De La Fuente', 'apellido_materno': 'Torres', 'nombres': 'María José'}
    """
    # Prefijos de apellidos compuestos
    PREFIJOS_COMPUESTOS = {
        "De",
        "Del",
        "De La",
        "De Las",
        "De Los",
        "San",
        "La",
        "Las",
        "Los",
        "Van",
        "Von",
    }

    if not value or "," not in value:
        return {
            "apellido_paterno": value.strip() if value else None,
            "apellido_materno": None,
            "nombres": None,
        }

    # Separar apellidos de nombres
    apellidos_str, nombres = value.split(",", 1)
    nombres = nombres.strip()

    # Tokenizar apellidos
    tokens = apellidos_str.strip().split()

    if not tokens:
        return {"apellido_paterno": None, "apellido_materno": None, "nombres": nombres}

    # Agrupar apellidos compuestos
    apellidos = []
    i = 0
    while i < len(tokens):
        token = tokens[i]

        # Verificar si es inicio de apellido compuesto
        if token in PREFIJOS_COMPUESTOS and i + 1 < len(tokens):
            # Buscar hasta dónde llega el apellido compuesto
            partes = [token]
            i += 1

            # Si es "De La/Los/Las", tomar el siguiente también
            if (
                token in {"De"}
                and i < len(tokens)
                and tokens[i] in {"La", "Las", "Los"}
            ):
                partes.append(tokens[i])
                i += 1

            # Tomar la parte sustantiva del apellido
            if i < len(tokens):
                partes.append(tokens[i])
                i += 1

            apellidos.append(" ".join(partes))
        else:
            apellidos.append(token)
            i += 1

    # Extraer apellido paterno y materno
    apellido_paterno = apellidos[0] if len(apellidos) >= 1 else None
    apellido_materno = apellidos[1] if len(apellidos) >= 2 else None

    # Si hay más de 2 apellidos, concatenar el resto al materno
    if len(apellidos) > 2:
        apellido_materno = " ".join(apellidos[1:])

    return {
        "apellido_paterno": apellido_paterno,
        "apellido_materno": apellido_materno,
        "nombres": nombres,
    }


# =============================================================================
# TRANSFORMACIONES DE LOOKUP
# =============================================================================


def lookup_division(cargo: str, catalog_path: str = None) -> Optional[str]:
    """
    Identifica la división a partir del cargo usando keywords.

    Args:
        cargo: Descripción del cargo
        catalog_path: Path al catálogo de divisiones (ignored, uses embedded catalog)

    Returns:
        Código de división o 'NO_DETERMINADO'

    Example:
        >>> lookup_division("Profesional DIFOI")
        'DIFOI'
    """
    if not cargo:
        return "NO_DETERMINADO"

    # Embedded catalog (sync with etl/catalogs/divisiones.yml)
    DIVISIONES = [
        {
            "codigo": "DIPIR",
            "keywords": [
                "DIPIR",
                "Inversión",
                "Presupuesto",
                "Preinversión",
                "Inversiones",
            ],
        },
        {"codigo": "DIFOI", "keywords": ["DIFOI", "Fomento", "Industria"]},
        {"codigo": "DIDESO", "keywords": ["DIDESO", "Desarrollo Social", "Social"]},
        {"codigo": "DIT", "keywords": ["DIT", "Infraestructura", "Transporte"]},
        {
            "codigo": "DIPLADE",
            "keywords": ["DIPLADE", "Planificación", "Ordenamiento Territorial"],
        },
        {
            "codigo": "DAF",
            "keywords": [
                "DAF",
                "Administración",
                "Finanzas",
                "Tesorería",
                "Gestión Personas",
                "Remuneraciones",
            ],
        },
        {
            "codigo": "CORE",
            "keywords": [
                "CORE",
                "Consejo Regional",
                "Secretaría CORE",
                "Secretaria CORE",
            ],
        },
        {"codigo": "GABINETE", "keywords": ["Gabinete", "Gobernador"]},
        {
            "codigo": "COMUNICACIONES",
            "keywords": ["Comunicaciones", "Periodista", "Prensa", "Fotógrafo"],
        },
        {
            "codigo": "JURIDICA",
            "keywords": ["Jurídica", "Abogado", "Legal", "Unidad Jurídica"],
        },
        {
            "codigo": "AUDITORIA",
            "keywords": ["Auditoría", "Auditoria", "Control", "Unidad Control"],
        },
        {"codigo": "CIES", "keywords": ["CIES", "Emergencias", "Seguridad"]},
        {
            "codigo": "ÑUBLE_250",
            "keywords": ["Ñuble 250", "Encargada Ñuble 250"],
        },
        {"codigo": "UCR", "keywords": ["UCR", "Coordinación Regional"]},
        {
            "codigo": "SERVICIOS_GENERALES",
            "keywords": ["Servicios Generales", "Conductor", "Oficina de Partes"],
        },
    ]

    cargo_upper = cargo.upper()

    # Buscar match por keywords
    for division in DIVISIONES:
        for keyword in division["keywords"]:
            if keyword.upper() in cargo_upper:
                return division["codigo"]

    return "NO_DETERMINADO"


# =============================================================================
# TRANSFORMACIONES DE ENUMERACIONES
# =============================================================================


def enum_map(value: str, mapping: Dict[str, str], default: str = None) -> Optional[str]:
    """
    Mapea valores a enums con fallback.

    Args:
        value: Valor a mapear
        mapping: Diccionario de mapeo
        default: Valor por defecto si no hay match

    Returns:
        Valor mapeado o default
    """
    if not value:
        return default

    return mapping.get(value.strip(), default)


# =============================================================================
# TRANSFORMACIONES DERIVADAS
# =============================================================================


def derive_calidad_juridica(tipo_vinculo: str) -> Optional[str]:
    """
    Deriva la calidad jurídica del tipo de vínculo.

    Args:
        tipo_vinculo: "Planta/Contrata" o "Honorarios"

    Returns:
        "PLANTA", "CONTRATA", "HONORARIO" o None
    """
    if not tipo_vinculo:
        return None

    tipo = tipo_vinculo.strip().upper()

    if "PLANTA" in tipo:
        return "PLANTA"
    elif "CONTRATA" in tipo:
        return "CONTRATA"
    elif "HONORARIO" in tipo:
        return "HONORARIO"

    return None


def parse_grado(grado_str: str) -> Optional[int]:
    """
    Parsea el grado EUS a entero.

    Args:
        grado_str: "13", "S/G", "1-A", etc.

    Returns:
        Grado como int o None para "S/G"
    """
    if not grado_str or grado_str.strip().upper() in ["S/G", "SG", ""]:
        return None

    # Extraer primer número
    match = re.search(r"\d+", grado_str)
    if match:
        return int(match.group())

    return None


# =============================================================================
# TRANSFORMACIONES DE JSON
# =============================================================================


def json_build(template: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construye objeto JSON desde template y contexto.

    Args:
        template: Estructura JSON con placeholders {field}
        context: Diccionario con valores

    Returns:
        JSON materializado
    """

    def resolve_value(value):
        if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
            field = value[1:-1]
            return context.get(field)
        elif isinstance(value, dict):
            return {k: resolve_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [resolve_value(item) for item in value]
        else:
            return value

    return resolve_value(template)


# =============================================================================
# UTILIDADES
# =============================================================================


def is_null_placeholder(value: str) -> bool:
    """
    Detecta placeholders de valores nulos.

    Args:
        value: String a verificar

    Returns:
        True si es placeholder de null
    """
    if not value:
        return True

    null_placeholders = {
        "",
        " ",
        "-",
        "$ -",
        "s/n",
        "sin datos",
        "sin dato",
        "#REF!",
        "#N/A",
        "N/A",
        "n/a",
        "NULL",
        "null",
        "None",
    }

    return value.strip().lower() in {p.lower() for p in null_placeholders}
