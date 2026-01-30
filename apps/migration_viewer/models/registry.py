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
        "display_columns": ["codigo_bip", "name", "ipr_nature", "crea_activo"],
        "search_columns": ["codigo_bip", "name"],
        "column_labels": {
            "codigo_bip": "Código BIP",
            "name": "Nombre",
            "ipr_nature": "Naturaleza",
            "crea_activo": "Activo",
        },
        "relations": {
            "ipr_type_id": {"table": "ref.category", "display": "label", "label": "Tipo IPR"},
            "status_id": {"table": "ref.category", "display": "label", "label": "Estado"},
            "mechanism_id": {"table": "ref.category", "display": "label", "label": "Mecanismo"},
            "funding_source_id": {"table": "ref.category", "display": "label", "label": "Fuente Financiamiento"},
            "executor_id": {"table": "core.organization", "display": "name", "label": "Ejecutor"},
            "formulator_id": {"table": "core.organization", "display": "name", "label": "Formulador"},
        },
        "filters": {
            "codigo_bip": {"type": "text", "label": "Código BIP"},
            "name": {"type": "text", "label": "Nombre"},
            "ipr_nature": {"type": "text", "label": "Naturaleza"},
            "crea_activo": {"type": "boolean", "label": "Activo"},
            "mechanism_id": {"type": "relation", "label": "Mecanismo"},
        },
    },
    "core.agreement": {
        "label": "Convenios",
        "icon": "handshake",
        "display_columns": ["agreement_number", "total_amount", "signed_at", "valid_from", "valid_to"],
        "search_columns": ["agreement_number"],
        "column_labels": {
            "agreement_number": "Nº Convenio",
            "total_amount": "Monto Total",
            "signed_at": "Fecha Firma",
            "valid_from": "Vigencia Desde",
            "valid_to": "Vigencia Hasta",
        },
        "relations": {
            "agreement_type_id": {"table": "ref.category", "display": "label", "label": "Tipo Convenio"},
            "state_id": {"table": "ref.category", "display": "label", "label": "Estado"},
            "ipr_id": {"table": "core.ipr", "display": "name", "label": "IPR Asociado"},
            "giver_id": {"table": "core.organization", "display": "name", "label": "Otorgante"},
            "receiver_id": {"table": "core.organization", "display": "name", "label": "Receptor"},
        },
        "filters": {
            "agreement_number": {"type": "text", "label": "Nº Convenio"},
            "agreement_type_id": {"type": "relation", "label": "Tipo"},
            "state_id": {"type": "relation", "label": "Estado"},
        },
    },
    "core.budget_program": {
        "label": "Programas Presupuestarios",
        "icon": "account_balance",
        "display_columns": ["code", "name", "fiscal_year", "initial_amount", "current_amount", "paid_amount"],
        "search_columns": ["code", "name"],
        "column_labels": {
            "code": "Código",
            "name": "Nombre",
            "fiscal_year": "Año Fiscal",
            "initial_amount": "Monto Inicial",
            "current_amount": "Monto Vigente",
            "committed_amount": "Comprometido",
            "accrued_amount": "Devengado",
            "paid_amount": "Pagado",
        },
        "relations": {
            "program_type_id": {"table": "ref.category", "display": "label", "label": "Tipo Programa"},
            "subtitle_id": {"table": "ref.category", "display": "label", "label": "Subtítulo"},
            "owner_division_id": {"table": "core.organization", "display": "name", "label": "División Responsable"},
        },
        "filters": {
            "code": {"type": "text", "label": "Código"},
            "name": {"type": "text", "label": "Nombre"},
            "fiscal_year": {"type": "text", "label": "Año Fiscal"},
            "program_type_id": {"type": "relation", "label": "Tipo"},
        },
    },
    "core.budget_commitment": {
        "label": "Compromisos Presupuestarios",
        "icon": "request_quote",
        "display_columns": ["commitment_number", "amount", "issued_at", "expires_at"],
        "search_columns": ["commitment_number"],
        "column_labels": {
            "commitment_number": "Nº Compromiso",
            "amount": "Monto",
            "issued_at": "Fecha Emisión",
            "expires_at": "Fecha Vencimiento",
        },
        "relations": {
            "commitment_type_id": {"table": "ref.category", "display": "label", "label": "Tipo Compromiso"},
            "status_id": {"table": "ref.category", "display": "label", "label": "Estado"},
            "budget_program_id": {"table": "core.budget_program", "display": "name", "label": "Programa"},
            "ipr_id": {"table": "core.ipr", "display": "name", "label": "IPR"},
            "agreement_id": {"table": "core.agreement", "display": "agreement_number", "label": "Convenio"},
        },
        "filters": {
            "commitment_number": {"type": "text", "label": "Nº Compromiso"},
            "commitment_type_id": {"type": "relation", "label": "Tipo"},
        },
    },
    "txn.event": {
        "label": "Eventos",
        "icon": "event",
        "display_columns": ["subject_type", "occurred_at", "recorded_at"],
        "search_columns": ["subject_type"],
        "column_labels": {
            "subject_type": "Tipo Sujeto",
            "occurred_at": "Fecha Ocurrencia",
            "recorded_at": "Fecha Registro",
        },
        "relations": {
            "event_type_id": {"table": "ref.category", "display": "label", "label": "Tipo Evento"},
        },
        "filters": {
            "subject_type": {"type": "text", "label": "Tipo Sujeto"},
            "event_type_id": {"type": "relation", "label": "Tipo Evento"},
        },
    },
    "txn.magnitude": {
        "label": "Magnitudes (Ejecución)",
        "icon": "trending_up",
        "display_columns": ["subject_type", "numeric_value", "as_of_date"],
        "search_columns": ["subject_type"],
        "column_labels": {
            "subject_type": "Tipo Sujeto",
            "numeric_value": "Valor",
            "as_of_date": "Fecha",
        },
        "relations": {
            "aspect_id": {"table": "ref.category", "display": "label", "label": "Aspecto"},
            "unit_id": {"table": "ref.category", "display": "label", "label": "Unidad"},
        },
        "filters": {
            "subject_type": {"type": "text", "label": "Tipo Sujeto"},
            "aspect_id": {"type": "relation", "label": "Aspecto"},
        },
    },
    "core.ipr_territory": {
        "label": "IPR ↔ Territorios",
        "icon": "location_on",
        "display_columns": ["is_primary", "notes"],
        "search_columns": ["notes"],
        "column_labels": {
            "is_primary": "Principal",
            "notes": "Notas",
        },
        "relations": {
            "ipr_id": {"table": "core.ipr", "display": "name", "label": "IPR"},
            "territory_id": {"table": "core.territory", "display": "name", "label": "Territorio"},
            "impact_type_id": {"table": "ref.category", "display": "label", "label": "Tipo Impacto"},
        },
        "filters": {
            "is_primary": {"type": "boolean", "label": "Principal"},
            "impact_type_id": {"type": "relation", "label": "Tipo Impacto"},
        },
    },
    "core.territory": {
        "label": "Territorios",
        "icon": "map",
        "display_columns": ["code", "name", "population", "area_km2"],
        "search_columns": ["code", "name"],
        "column_labels": {
            "code": "Código",
            "name": "Nombre",
            "population": "Población",
            "area_km2": "Área (km²)",
        },
        "relations": {
            "territory_type_id": {"table": "ref.category", "display": "label", "label": "Tipo Territorio"},
            "parent_id": {"table": "core.territory", "display": "name", "label": "Territorio Padre"},
        },
        "filters": {
            "code": {"type": "text", "label": "Código"},
            "name": {"type": "text", "label": "Nombre"},
            "territory_type_id": {"type": "relation", "label": "Tipo"},
        },
    },
}


def get_table_config(table_name: str) -> dict:
    """Get configuration for a specific table."""
    return TABLES.get(table_name, {})


def get_all_tables() -> dict:
    """Get all registered tables."""
    return TABLES
