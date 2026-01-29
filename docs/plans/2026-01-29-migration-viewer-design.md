# Diseño: Visor de Datos Migrados

**Fecha:** 2026-01-29
**Estado:** Aprobado
**Objetivo:** Exploración de datos migrados a PostgreSQL

---

## Requisitos

- **Objetivo:** Exploración libre de tablas, filtros, búsqueda, relaciones entre entidades
- **Relaciones:** Nivel intermedio - vista detalle con entidades relacionadas inline
- **Tablas:** Estructura extensible, solo mostrar tablas con datos
- **Navegación:** Sidebar con lista de tablas y contadores de registros
- **Filtros:** Búsqueda global rápida + filtros avanzados por columna

## Arquitectura

```
apps/migration_viewer/
├── app.py                 # Entry point, configuración Streamlit
├── config.py              # Conexión DB, tablas registradas
├── components/
│   ├── sidebar.py         # Navegación con tablas y contadores
│   ├── data_grid.py       # Tabla paginada con filtros
│   ├── detail_view.py     # Vista detalle con relaciones inline
│   └── search.py          # Búsqueda global + filtros por columna
├── models/
│   └── registry.py        # Registro de tablas y sus metadatos
└── requirements.txt       # streamlit, psycopg2, pandas
```

## Registro de Tablas

Patrón declarativo para agregar nuevas tablas:

```python
TABLES = {
    "core.person": {
        "label": "Personas",
        "icon": "👤",
        "display_columns": ["rut", "names", "paternal_surname", "email"],
        "search_columns": ["rut", "names", "paternal_surname", "email"],
        "relations": {
            "organization_id": ("core.organization", "name"),
            "person_type_id": ("ref.category", "label"),
        }
    },
    "core.organization": {
        "label": "Organizaciones",
        "icon": "🏛️",
        "display_columns": ["code", "name", "short_name"],
        "search_columns": ["code", "name", "short_name"],
        "relations": {
            "org_type_id": ("ref.category", "label"),
            "parent_id": ("core.organization", "name"),
        }
    },
    "ref.category": {
        "label": "Categorías",
        "icon": "🏷️",
        "display_columns": ["scheme", "code", "label"],
        "search_columns": ["scheme", "code", "label"],
        "relations": {}
    }
}
```

## Layout UI

```
┌─────────────────────────────────────────────────────────────────┐
│  🔍 Búsqueda global...                              [Filtros ▼] │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│  📊 TABLAS   │   Personas (110 registros)                       │
│              │   ─────────────────────────────────────────────  │
│  👤 Personas │   [Filtros por columna expandibles]              │
│     (110)    │                                                  │
│              │   ┌────────┬──────────┬──────────┬─────────┐    │
│  🏛️ Orgs     │   │ RUT    │ Nombres  │ Apellido │ Email   │    │
│     (1612)   │   ├────────┼──────────┼──────────┼─────────┤    │
│              │   │ 12.3.. │ Juan     │ Pérez    │ jp@...  │ 👁️ │
│     (350)    │   │ 15.6.. │ María    │ López    │ ml@...  │ 👁️ │
│              │   └────────┴──────────┴──────────┴─────────┘    │
│              │                                                  │
│              │   ◀ 1 2 3 ... 11 ▶  (10 por página)              │
└──────────────┴──────────────────────────────────────────────────┘
```

## Vista Detalle

Al hacer click en 👁️ se expande panel mostrando:
- Todos los campos del registro
- Metadata JSON formateado
- Relaciones inline con datos de la entidad relacionada
- Fechas de auditoría (created_at, updated_at)

## Sistema de Filtros

| Tipo Dato | Filtro | SQL |
|-----------|--------|-----|
| text | TextInput | `ILIKE '%valor%'` |
| uuid_fk | SelectBox | `= uuid` |
| boolean | Checkbox | `= true/false` |
| timestamp | DateRange | `BETWEEN` |
| jsonb | TextInput | `::text ILIKE` |

Filtros se combinan con AND. Badge muestra cantidad de filtros activos.

## Conexión

```python
DATABASE_URL = "postgresql://goreos:goreos_dev_password@localhost:5433/goreos_model"
```

Pool de conexiones con `@st.cache_resource`.

## Detección Automática

Solo muestra tablas del registro que tienen `COUNT(*) > 0`.

## Ejecución

```bash
cd apps/migration_viewer
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

## Dependencias

- streamlit>=1.28
- psycopg2-binary>=2.9
- pandas>=2.0
