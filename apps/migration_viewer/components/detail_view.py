"""Detail view component showing record details and relations."""
import streamlit as st
import pandas as pd
import json
from models.registry import get_table_config

# Columnas a excluir de la vista de datos (siempre se muestran en secciones especiales)
EXCLUDED_COLUMNS = {
    "id", "metadata", "data", "created_at", "updated_at", "recorded_at",
    "created_by_id", "updated_by_id", "deleted_at", "deleted_by_id"
}


def render_detail_view(row: pd.Series, table_name: str, conn):
    """Render detail view for selected record."""

    config = get_table_config(table_name)
    column_labels = config.get("column_labels", {})
    relations = config.get("relations", {})

    st.markdown("---")
    st.markdown("### :material/visibility: Detalle del Registro")

    # Main columns: details and metadata
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Datos")

        # Display all non-null fields
        for col in row.index:
            if col in EXCLUDED_COLUMNS:
                continue

            value = row[col]
            label = column_labels.get(col, col)

            if pd.isna(value) or value is None:
                continue

            # Check if it's a relation field
            if col in relations:
                rel_config = relations[col]
                rel_value = _resolve_relation(conn, value, rel_config)
                st.markdown(f"**{label}:** {rel_value}")
            else:
                # Format booleans
                if isinstance(value, bool):
                    value = "Sí" if value else "No"
                st.markdown(f"**{label}:** {value}")

    with col2:
        st.markdown("#### Datos Adicionales")

        # Show metadata/data JSON (metadata para core.*, data para txn.event)
        json_data = row.get("metadata") or row.get("data")
        if json_data:
            if isinstance(json_data, str):
                try:
                    json_data = json.loads(json_data)
                except json.JSONDecodeError:
                    pass

            if isinstance(json_data, dict) and json_data:
                for key, value in json_data.items():
                    st.markdown(f"**{key}:** {value}")
            else:
                st.markdown("*(vacío)*")
        else:
            st.markdown("*(vacío)*")

        st.markdown("---")
        st.markdown("#### Auditoría")

        # Timestamps (created_at/recorded_at según la tabla)
        created_at = row.get("created_at") or row.get("recorded_at")
        updated_at = row.get("updated_at")

        if created_at:
            label = "Registrado" if "recorded_at" in row.index else "Creado"
            st.markdown(f"**{label}:** {_format_datetime(created_at)}")
        if updated_at:
            st.markdown(f"**Actualizado:** {_format_datetime(updated_at)}")

        # ID
        st.markdown(f"**ID:** `{row.get('id', 'N/A')}`")

    # Show related entities
    if relations:
        st.markdown("---")
        st.markdown("### :material/link: Entidades Relacionadas")

        rel_cols = st.columns(len(relations))

        for idx, (field, rel_config) in enumerate(relations.items()):
            fk_value = row.get(field)
            if pd.isna(fk_value) or fk_value is None:
                continue

            with rel_cols[idx % len(rel_cols)]:
                _render_related_entity(conn, fk_value, rel_config)


def _resolve_relation(conn, fk_value: str, rel_config: dict) -> str:
    """Resolve a foreign key to its display value."""

    rel_table = rel_config["table"]
    rel_display = rel_config["display"]

    try:
        result = conn.query(
            f"SELECT {rel_display} FROM {rel_table} WHERE id = :id",
            params={"id": str(fk_value)}
        )
        if not result.empty:
            return str(result.iloc[0][rel_display])
    except Exception:
        pass

    return str(fk_value)[:8] + "..."


def _render_related_entity(conn, fk_value: str, rel_config: dict):
    """Render a related entity card."""

    rel_table = rel_config["table"]
    rel_display = rel_config["display"]
    label = rel_config.get("label", rel_table)

    try:
        # Get the related record
        result = conn.query(
            f"SELECT * FROM {rel_table} WHERE id = :id",
            params={"id": str(fk_value)}
        )

        if result.empty:
            st.warning(f"{label}: No encontrado")
            return

        record = result.iloc[0]

        with st.container(border=True):
            st.markdown(f"**{label}**")
            st.markdown(f"**{record.get(rel_display, 'N/A')}**")

            # Show a few key fields
            rel_config_full = get_table_config(rel_table)
            display_cols = rel_config_full.get("display_columns", [])[:3]
            col_labels = rel_config_full.get("column_labels", {})

            for col in display_cols:
                if col == rel_display:
                    continue
                val = record.get(col)
                if pd.notna(val) and val is not None:
                    col_label = col_labels.get(col, col)
                    st.caption(f"{col_label}: {val}")

            # Button to navigate to this record
            if st.button(f"Ver {label}", key=f"nav_{fk_value}", type="secondary", use_container_width=True):
                st.session_state.selected_table = rel_table
                st.session_state.navigate_to_id = str(fk_value)
                st.session_state.current_page = 0
                st.session_state.filters = {}
                st.session_state.search_query = ""
                st.rerun()

    except Exception as e:
        st.error(f"Error cargando {label}: {e}")


def _format_datetime(dt) -> str:
    """Format datetime for display."""
    if pd.isna(dt):
        return "N/A"

    try:
        if hasattr(dt, "strftime"):
            return dt.strftime("%Y-%m-%d %H:%M")
        return str(dt)[:16]
    except Exception:
        return str(dt)
