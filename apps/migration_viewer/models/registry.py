"""Table registry - declarative configuration for viewable tables."""

TABLES = {
    "core.person": {
        "label": "Personas",
        "icon": "person",
        "display_columns": ["rut", "names", "paternal_surname", "maternal_surname", "email", "phone", "is_active"],
        "search_columns": ["rut", "names", "paternal_surname", "maternal_surname", "email"],
        "column_labels": {
            "rut": "RUT",
            "names": "Nombres",
            "paternal_surname": "Apellido Paterno",
            "maternal_surname": "Apellido Materno",
            "email": "Email",
            "phone": "Teléfono",
            "is_active": "Activo",
        },
        "relations": {
            "organization_id": {"table": "core.organization", "display": "name", "label": "Organización"},
            "person_type_id": {"table": "ref.category", "display": "label", "label": "Tipo Persona"},
            "role_id": {"table": "ref.category", "display": "label", "label": "Rol"},
        },
        "filters": {
            "rut": {"type": "text", "label": "RUT"},
            "names": {"type": "text", "label": "Nombres"},
            "paternal_surname": {"type": "text", "label": "Apellido"},
            "email": {"type": "text", "label": "Email"},
            "is_active": {"type": "boolean", "label": "Activo"},
            "organization_id": {"type": "relation", "label": "Organización"},
        },
    },
    "core.organization": {
        "label": "Organizaciones",
        "icon": "apartment",
        "display_columns": ["code", "name", "short_name"],
        "search_columns": ["code", "name", "short_name"],
        "column_labels": {
            "code": "Código",
            "name": "Nombre",
            "short_name": "Nombre Corto",
        },
        "relations": {
            "org_type_id": {"table": "ref.category", "display": "label", "label": "Tipo Organización"},
            "parent_id": {"table": "core.organization", "display": "name", "label": "Organización Padre"},
        },
        "filters": {
            "code": {"type": "text", "label": "Código"},
            "name": {"type": "text", "label": "Nombre"},
            "org_type_id": {"type": "relation", "label": "Tipo"},
        },
    },
    "ref.category": {
        "label": "Categorías",
        "icon": "sell",
        "display_columns": ["scheme", "code", "label", "description"],
        "search_columns": ["scheme", "code", "label", "description"],
        "column_labels": {
            "scheme": "Esquema",
            "code": "Código",
            "label": "Etiqueta",
            "description": "Descripción",
        },
        "relations": {},
        "filters": {
            "scheme": {"type": "text", "label": "Esquema"},
            "code": {"type": "text", "label": "Código"},
            "label": {"type": "text", "label": "Etiqueta"},
        },
    },
    "core.ipr": {
        "label": "IPR (Iniciativas)",
        "icon": "work",
        "display_columns": ["code", "name", "progress", "is_active"],
        "search_columns": ["code", "name"],
        "column_labels": {
            "code": "Código",
            "name": "Nombre",
            "progress": "Avance",
            "is_active": "Activo",
        },
        "relations": {
            "ipr_type_id": {"table": "ref.category", "display": "label", "label": "Tipo IPR"},
            "state_id": {"table": "ref.category", "display": "label", "label": "Estado"},
            "mechanism_id": {"table": "ref.category", "display": "label", "label": "Mecanismo"},
        },
        "filters": {
            "code": {"type": "text", "label": "Código"},
            "name": {"type": "text", "label": "Nombre"},
            "is_active": {"type": "boolean", "label": "Activo"},
        },
    },
    "core.agreement": {
        "label": "Convenios",
        "icon": "handshake",
        "display_columns": ["code", "subject", "signed_date"],
        "search_columns": ["code", "subject"],
        "column_labels": {
            "code": "Código",
            "subject": "Materia",
            "signed_date": "Fecha Firma",
        },
        "relations": {
            "agreement_type_id": {"table": "ref.category", "display": "label", "label": "Tipo Convenio"},
            "state_id": {"table": "ref.category", "display": "label", "label": "Estado"},
        },
        "filters": {
            "code": {"type": "text", "label": "Código"},
            "subject": {"type": "text", "label": "Materia"},
        },
    },
}


def get_table_config(table_name: str) -> dict:
    """Get configuration for a specific table."""
    return TABLES.get(table_name, {})


def get_all_tables() -> dict:
    """Get all registered tables."""
    return TABLES
