"""Data grid component with pagination."""
import streamlit as st
import pandas as pd
from models.registry import get_table_config
from config import DEFAULT_PAGE_SIZE, PAGE_SIZE_OPTIONS


def render_data_grid(
    table_name: str,
    conn,
    where_clause: str,
    params: dict
) -> pd.DataFrame:
    """Render paginated data grid for the selected table."""

    config = get_table_config(table_name)
    display_columns = config.get("display_columns", [])
    column_labels = config.get("column_labels", {})

    # Pagination controls
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        page_size = st.selectbox(
            "Registros por página",
            options=PAGE_SIZE_OPTIONS,
            index=PAGE_SIZE_OPTIONS.index(st.session_state.get("page_size", DEFAULT_PAGE_SIZE)),
            key="page_size_select",
            label_visibility="collapsed"
        )
        if page_size != st.session_state.get("page_size", DEFAULT_PAGE_SIZE):
            st.session_state.page_size = page_size
            st.session_state.current_page = 0

    # Get total count
    count_query = f"SELECT COUNT(*) as total FROM {table_name} WHERE {where_clause}"
    total_df = conn.query(count_query, params=params)
    total_count = int(total_df.iloc[0]["total"])

    page_size = st.session_state.get("page_size", DEFAULT_PAGE_SIZE)
    total_pages = max(1, (total_count + page_size - 1) // page_size)
    current_page = st.session_state.get("current_page", 0)

    with col2:
        st.markdown(f"**{total_count:,}** registros")

    with col3:
        # Page navigation
        nav_cols = st.columns([1, 2, 1])
        with nav_cols[0]:
            if st.button(":material/chevron_left:", disabled=current_page == 0):
                st.session_state.current_page = current_page - 1
                st.rerun()
        with nav_cols[1]:
            st.markdown(f"<center>Página {current_page + 1} de {total_pages}</center>", unsafe_allow_html=True)
        with nav_cols[2]:
            if st.button(":material/chevron_right:", disabled=current_page >= total_pages - 1):
                st.session_state.current_page = current_page + 1
                st.rerun()

    # Build and execute query
    columns_str = ", ".join(["id"] + display_columns + ["metadata", "created_at", "updated_at"])
    offset = current_page * page_size

    query = f"""
        SELECT {columns_str}
        FROM {table_name}
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT {page_size} OFFSET {offset}
    """

    df = conn.query(query, params=params)

    if df.empty:
        st.info("No se encontraron registros con los filtros aplicados.")
        return df

    # Prepare display dataframe
    display_df = df[display_columns].copy()

    # Rename columns to labels
    display_df.columns = [column_labels.get(col, col) for col in display_columns]

    return df  # Return full df for detail view


def render_data_table(df: pd.DataFrame, table_name: str):
    """Render the data as a selectable table."""

    config = get_table_config(table_name)
    display_columns = config.get("display_columns", [])
    column_labels = config.get("column_labels", {})

    if df.empty:
        return None

    # Create display dataframe with index
    display_df = df[display_columns].copy()
    display_df.columns = [column_labels.get(col, col) for col in display_columns]

    # Use dataframe with selection
    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="data_table"
    )

    # Get selected row
    if event.selection and event.selection.rows:
        selected_idx = event.selection.rows[0]
        return df.iloc[selected_idx]

    return None
