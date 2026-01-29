"""Search and filter components."""
import streamlit as st
from models.registry import get_table_config


def render_search_bar():
    """Render global search bar."""
    col1, col2 = st.columns([4, 1])

    with col1:
        search_query = st.text_input(
            "Buscar",
            value=st.session_state.get("search_query", ""),
            placeholder="Buscar en todos los campos...",
            label_visibility="collapsed",
            key="global_search"
        )
        if search_query != st.session_state.get("search_query", ""):
            st.session_state.search_query = search_query
            st.session_state.current_page = 0

    with col2:
        show_filters = st.toggle("Filtros", value=st.session_state.get("show_filters", False))
        st.session_state.show_filters = show_filters

    return search_query


def render_filters(table_name: str, conn) -> dict:
    """Render column filters for the selected table."""

    if not st.session_state.get("show_filters", False):
        return st.session_state.get("filters", {})

    config = get_table_config(table_name)
    filters_config = config.get("filters", {})
    relations = config.get("relations", {})

    if not filters_config:
        return {}

    current_filters = st.session_state.get("filters", {})

    with st.expander("Filtros avanzados", expanded=True):
        cols = st.columns(3)

        for idx, (field, filter_cfg) in enumerate(filters_config.items()):
            col = cols[idx % 3]
            filter_type = filter_cfg.get("type", "text")
            label = filter_cfg.get("label", field)

            with col:
                if filter_type == "text":
                    value = st.text_input(
                        label,
                        value=current_filters.get(field, ""),
                        key=f"filter_{field}"
                    )
                    if value:
                        current_filters[field] = value
                    elif field in current_filters:
                        del current_filters[field]

                elif filter_type == "boolean":
                    options = ["Todos", "Sí", "No"]
                    current_val = current_filters.get(field)
                    if current_val is True:
                        default_idx = 1
                    elif current_val is False:
                        default_idx = 2
                    else:
                        default_idx = 0

                    value = st.selectbox(
                        label,
                        options=options,
                        index=default_idx,
                        key=f"filter_{field}"
                    )
                    if value == "Sí":
                        current_filters[field] = True
                    elif value == "No":
                        current_filters[field] = False
                    elif field in current_filters:
                        del current_filters[field]

                elif filter_type == "relation" and field in relations:
                    rel_config = relations[field]
                    rel_table = rel_config["table"]
                    rel_display = rel_config["display"]

                    # Fetch options from related table
                    options_df = conn.query(
                        f"SELECT id, {rel_display} FROM {rel_table} WHERE deleted_at IS NULL ORDER BY {rel_display} LIMIT 500"
                    )

                    options = {"": "Todos"}
                    for _, row in options_df.iterrows():
                        options[str(row["id"])] = row[rel_display] or "(sin nombre)"

                    current_val = current_filters.get(field, "")

                    value = st.selectbox(
                        label,
                        options=list(options.keys()),
                        format_func=lambda x: options.get(x, x),
                        index=list(options.keys()).index(current_val) if current_val in options else 0,
                        key=f"filter_{field}"
                    )
                    if value:
                        current_filters[field] = value
                    elif field in current_filters:
                        del current_filters[field]

        # Clear filters button
        if current_filters:
            if st.button("Limpiar filtros", type="secondary"):
                current_filters = {}
                st.session_state.filters = {}
                st.rerun()

    st.session_state.filters = current_filters
    return current_filters


def build_where_clause(table_name: str, search_query: str, filters: dict) -> tuple[str, dict]:
    """Build WHERE clause from search and filters."""

    config = get_table_config(table_name)
    search_columns = config.get("search_columns", [])
    filters_config = config.get("filters", {})

    conditions = ["deleted_at IS NULL"]
    params = {}

    # Global search
    if search_query and search_columns:
        search_conditions = []
        for col in search_columns:
            search_conditions.append(f"COALESCE({col}::text, '') ILIKE :search")
        conditions.append(f"({' OR '.join(search_conditions)})")
        params["search"] = f"%{search_query}%"

    # Column filters
    for field, value in filters.items():
        filter_cfg = filters_config.get(field, {})
        filter_type = filter_cfg.get("type", "text")

        if filter_type == "text":
            conditions.append(f"COALESCE({field}::text, '') ILIKE :filter_{field}")
            params[f"filter_{field}"] = f"%{value}%"
        elif filter_type == "boolean":
            conditions.append(f"{field} = :filter_{field}")
            params[f"filter_{field}"] = value
        elif filter_type == "relation":
            conditions.append(f"{field} = :filter_{field}")
            params[f"filter_{field}"] = value

    where_clause = " AND ".join(conditions)
    return where_clause, params
