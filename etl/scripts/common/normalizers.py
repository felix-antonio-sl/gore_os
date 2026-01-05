"""
Catalog normalizers for ETL.
Maps raw values to canonical codes using domain-specific catalogs.
"""

from typing import Optional, Dict
import re

# ============================================================================
# ESTADO CONVENIO
# ============================================================================
ESTADO_CONVENIO_MAP: Dict[str, str] = {
    # FIRMADO
    "firmado": "FIRMADO",
    "FIRMADO": "FIRMADO",
    # SIN_CONVENIO
    "sin convenio": "SIN_CONVENIO",
    "SIN CONVENIO": "SIN_CONVENIO",
    "sin.convenio": "SIN_CONVENIO",
    "SIN.CONVENIO": "SIN_CONVENIO",
    # ENCOMENDADO_DIT
    "encomendado dit": "ENCOMENDADO_DIT",
    "ENCOMENDADO DIT": "ENCOMENDADO_DIT",
    "ENCOMENDADO A DIT": "ENCOMENDADO_DIT",
    # NO_SE_FIRMO
    "no se firmo": "NO_SE_FIRMO",
    "NO SE FIRMO": "NO_SE_FIRMO",
    "no se firmó": "NO_SE_FIRMO",
    "NO SE FIRMÓ": "NO_SE_FIRMO",
    # EN_TRAMITE
    "en tramite": "EN_TRAMITE",
    "EN TRAMITE": "EN_TRAMITE",
    "en trámite": "EN_TRAMITE",
    "EN TRÁMITE": "EN_TRAMITE",
    "tramite": "EN_TRAMITE",
    "TRAMITE": "EN_TRAMITE",
    # RS_NO_VIGENTE
    "rs no vigente": "RS_NO_VIGENTE",
    "RS NO VIGENTE": "RS_NO_VIGENTE",
    "sin rs vigente": "RS_NO_VIGENTE",
    # ENVIADO_AL_SERVICIO
    "enviado al servicio": "ENVIADO_AL_SERVICIO",
    "ENVIADO AL SERVICIO": "ENVIADO_AL_SERVICIO",
}

# ============================================================================
# ESTADO CGR
# ============================================================================
ESTADO_CGR_MAP: Dict[str, str] = {
    # TOMADO_DE_RAZON
    "tomado de razon": "TOMADO_DE_RAZON",
    "TOMADO DE RAZON": "TOMADO_DE_RAZON",
    "tomado de razón": "TOMADO_DE_RAZON",
    "TOMADO DE RAZÓN": "TOMADO_DE_RAZON",
    "tr": "TOMADO_DE_RAZON",
    "TR": "TOMADO_DE_RAZON",
    "TOMADA DE RAZON": "TOMADO_DE_RAZON",
    # TR_CON_ALCANCES
    "tr con alcances": "TR_CON_ALCANCES",
    "TR CON ALCANCES": "TR_CON_ALCANCES",
    "tomado razon con alcances": "TR_CON_ALCANCES",
    "TOMADO RAZON CON ALCANCES": "TR_CON_ALCANCES",
    "con alcance": "TR_CON_ALCANCES",
    "CON ALCANCE": "TR_CON_ALCANCES",
    # REPRESENTADO
    "representado": "REPRESENTADO",
    "REPRESENTADO": "REPRESENTADO",
    "representada": "REPRESENTADO",
    "REPRESENTADA": "REPRESENTADO",
    # EN_CGR
    "en cgr": "EN_CGR",
    "EN CGR": "EN_CGR",
    "ingresado cgr": "EN_CGR",
    "INGRESADO CGR": "EN_CGR",
}

# ============================================================================
# CANALES DOCUMENTALES
# ============================================================================
CANAL_MAP: Dict[str, str] = {
    # EMAIL
    "email": "EMAIL",
    "EMAIL": "EMAIL",
    "e-mail": "EMAIL",
    "E-MAIL": "EMAIL",
    "e mail": "EMAIL",
    "E MAIL": "EMAIL",
    "correo electronico": "EMAIL",
    "CORREO ELECTRONICO": "EMAIL",
    "correo electrónico": "EMAIL",
    # DOCDIGITAL
    "doc digital": "DOCDIGITAL",
    "DOC DIGITAL": "DOCDIGITAL",
    "docdigital": "DOCDIGITAL",
    "DOCDIGITAL": "DOCDIGITAL",
    "doc.digital": "DOCDIGITAL",
    "DOC.DIGITAL": "DOCDIGITAL",
    # PAPEL
    "papel": "PAPEL",
    "PAPEL": "PAPEL",
    "físico": "PAPEL",
    "FÍSICO": "PAPEL",
    "fisico": "PAPEL",
    "FISICO": "PAPEL",
    # POR_MANO
    "por mano": "POR_MANO",
    "POR MANO": "POR_MANO",
    "en mano": "POR_MANO",
    "EN MANO": "POR_MANO",
    "mano": "POR_MANO",
    "MANO": "POR_MANO",
    # LIBRO
    "libro": "LIBRO",
    "LIBRO": "LIBRO",
    "en libro": "LIBRO",
    "EN LIBRO": "LIBRO",
    # VENTANILLA
    "ventanilla unica": "VENTANILLA",
    "VENTANILLA UNICA": "VENTANILLA",
    "ventanilla única": "VENTANILLA",
    # PLATAFORMA
    "plataforma": "PLATAFORMA",
    "PLATAFORMA": "PLATAFORMA",
}

# ============================================================================
# TIPO RESOLUCION
# ============================================================================
TIPO_RESOLUCION_MAP: Dict[str, str] = {
    "exenta": "EXENTA",
    "EXENTA": "EXENTA",
    "res exenta": "EXENTA",
    "RES EXENTA": "EXENTA",
    "resolucion exenta": "EXENTA",
    "RESOLUCION EXENTA": "EXENTA",
    "afecta": "AFECTA",
    "AFECTA": "AFECTA",
    "res afecta": "AFECTA",
    "RES AFECTA": "AFECTA",
    "resolucion afecta": "AFECTA",
    "RESOLUCION AFECTA": "AFECTA",
}

# ============================================================================
# COMUNAS ÑUBLE
# ============================================================================
COMUNA_MAP: Dict[str, str] = {
    # Provincia Diguillín
    "bulnes": "BULNES",
    "BULNES": "BULNES",
    "chillan": "CHILLÁN",
    "CHILLAN": "CHILLÁN",
    "chillán": "CHILLÁN",
    "CHILLÁN": "CHILLÁN",
    "chillan viejo": "CHILLÁN VIEJO",
    "CHILLAN VIEJO": "CHILLÁN VIEJO",
    "chillán viejo": "CHILLÁN VIEJO",
    "CHILLÁN VIEJO": "CHILLÁN VIEJO",
    "ch. viejo": "CHILLÁN VIEJO",
    "el carmen": "EL CARMEN",
    "EL CARMEN": "EL CARMEN",
    "pemuco": "PEMUCO",
    "PEMUCO": "PEMUCO",
    "pinto": "PINTO",
    "PINTO": "PINTO",
    "quillon": "QUILLÓN",
    "QUILLON": "QUILLÓN",
    "quillón": "QUILLÓN",
    "QUILLÓN": "QUILLÓN",
    "san ignacio": "SAN IGNACIO",
    "SAN IGNACIO": "SAN IGNACIO",
    "yungay": "YUNGAY",
    "YUNGAY": "YUNGAY",
    # Provincia Itata
    "cobquecura": "COBQUECURA",
    "COBQUECURA": "COBQUECURA",
    "coelemu": "COELEMU",
    "COELEMU": "COELEMU",
    "ninhue": "NINHUE",
    "NINHUE": "NINHUE",
    "portezuelo": "PORTEZUELO",
    "PORTEZUELO": "PORTEZUELO",
    "quirihue": "QUIRIHUE",
    "QUIRIHUE": "QUIRIHUE",
    "ranquil": "RÁNQUIL",
    "RANQUIL": "RÁNQUIL",
    "ránquil": "RÁNQUIL",
    "RÁNQUIL": "RÁNQUIL",
    "trehuaco": "TREGUACO",
    "TREHUACO": "TREGUACO",
    "treguaco": "TREGUACO",
    "TREGUACO": "TREGUACO",
    # Provincia Punilla
    "coihueco": "COIHUECO",
    "COIHUECO": "COIHUECO",
    "niquen": "ÑIQUÉN",
    "NIQUEN": "ÑIQUÉN",
    "ñiquen": "ÑIQUÉN",
    "ÑIQUEN": "ÑIQUÉN",
    "ñiquén": "ÑIQUÉN",
    "ÑIQUÉN": "ÑIQUÉN",
    "san carlos": "SAN CARLOS",
    "SAN CARLOS": "SAN CARLOS",
    "san fabian": "SAN FABIÁN",
    "SAN FABIAN": "SAN FABIÁN",
    "san fabián": "SAN FABIÁN",
    "SAN FABIÁN": "SAN FABIÁN",
    "san nicolas": "SAN NICOLÁS",
    "SAN NICOLAS": "SAN NICOLÁS",
    "san nicolás": "SAN NICOLÁS",
    "SAN NICOLÁS": "SAN NICOLÁS",
    # Regional/Multiple
    "regional": "REGIONAL",
    "REGIONAL": "REGIONAL",
    "intercomunal": "INTERCOMUNAL",
    "INTERCOMUNAL": "INTERCOMUNAL",
}

PROVINCIA_MAP: Dict[str, str] = {
    "diguillin": "DIGUILLÍN",
    "DIGUILLIN": "DIGUILLÍN",
    "diguillín": "DIGUILLÍN",
    "DIGUILLÍN": "DIGUILLÍN",
    "itata": "ITATA",
    "ITATA": "ITATA",
    "punilla": "PUNILLA",
    "PUNILLA": "PUNILLA",
    "regional": "REGIONAL",
    "REGIONAL": "REGIONAL",
}


def normalize_catalog(
    value: Optional[str], catalog: Dict[str, str], default: str = "OTRO"
) -> Optional[str]:
    """
    Normalize a value using a catalog mapping.
    Returns normalized value if found, default if not, None if input is None.
    """
    if value is None:
        return None

    cleaned = str(value).strip()
    if cleaned in ("", "-", "N/A", "#REF!"):
        return None

    # Direct match
    if cleaned in catalog:
        return catalog[cleaned]

    # Case-insensitive match
    lower = cleaned.lower()
    for key, val in catalog.items():
        if key.lower() == lower:
            return val

    # Fuzzy match - check if any key is contained
    for key, val in catalog.items():
        if key.lower() in lower or lower in key.lower():
            return val

    return default


def normalize_estado_convenio(value: Optional[str]) -> Optional[str]:
    return normalize_catalog(value, ESTADO_CONVENIO_MAP)


def normalize_estado_cgr(value: Optional[str]) -> Optional[str]:
    return normalize_catalog(value, ESTADO_CGR_MAP)


def normalize_canal(value: Optional[str]) -> Optional[str]:
    return normalize_catalog(value, CANAL_MAP)


def normalize_tipo_resolucion(value: Optional[str]) -> Optional[str]:
    return normalize_catalog(value, TIPO_RESOLUCION_MAP)


def normalize_comuna(value: Optional[str]) -> Optional[str]:
    return normalize_catalog(
        value, COMUNA_MAP, default=value.strip().upper() if value else None
    )


def normalize_provincia(value: Optional[str]) -> Optional[str]:
    return normalize_catalog(
        value, PROVINCIA_MAP, default=value.strip().upper() if value else None
    )
