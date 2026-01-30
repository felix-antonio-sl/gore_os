# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Migration Viewer is a Streamlit app for exploring GORE_OS PostgreSQL data. It provides a visual interface to browse migrated tables, view record details, and monitor data quality.

## Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the app
streamlit run app.py

# Access at http://localhost:8501
```

## Architecture

```
app.py              # Main entry point, page config, routing
config.py           # DATABASE_URL configuration
models/
  registry.py       # Declarative table configuration (columns, relations, filters)
components/
  sidebar.py        # Table navigation sidebar
  search.py         # Search bar and filter components
  data_grid.py      # Data table rendering with pagination
  detail_view.py    # Record detail view with relation resolution
  dashboard.py      # Migration summary dashboard with metrics
```

## Adding New Tables

Edit `models/registry.py` to add table configuration:

```python
"schema.table_name": {
    "label": "Human Label",
    "icon": "material_icon_name",
    "display_columns": ["col1", "col2"],      # Columns shown in grid
    "search_columns": ["col1"],               # Columns for text search
    "column_labels": {"col1": "Label"},       # Human-readable labels
    "relations": {                            # FK resolution
        "fk_column": {"table": "ref.category", "display": "label", "label": "Relation Name"}
    },
    "filters": {                              # Available filters
        "col1": {"type": "text", "label": "Label"},
        "fk_col": {"type": "relation", "label": "Label"},
        "bool_col": {"type": "boolean", "label": "Label"}
    }
}
```

## Key Patterns

- **Relations**: FK columns ending in `_id` are resolved to display values via `relations` config
- **Soft Delete**: Tables with `deleted_at` column filter out soft-deleted records automatically
- **Event Sourcing**: `txn.event` and `txn.magnitude` tables don't have soft delete (immutable)
- **Categorical Coherence**: Dashboard shows coherence metrics for FK columns pointing to `ref.category`

## Database Connection

Uses SQLAlchemy via Streamlit's `st.connection()`. Connection string in `config.py`:
```
postgresql://goreos:goreos_2026@localhost:5433/goreos_model
```

## Recent Updates (v2.0 - 2026-01-30)

- Added `investment_sector_id` and `fund_category_id` relations for IPR
- Added filters for Tipo IPR, Sector Inversión, Categoría Fondo 8%
- Dashboard shows Categorical Coherence metrics (100% univocity)
- Updated IPR migration target: 3,621 records
