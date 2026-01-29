"""
Migration Viewer - Visor de datos migrados a PostgreSQL
GORE_OS Project
"""
import streamlit as st
from streamlit import connection

from config import DATABASE_URL
from models.registry import get_all_tables
from components.sidebar import render_sidebar
from components.search import render_search_bar, render_filters, build_where_clause
from components.data_grid import render_data_grid, render_data_table
from components.detail_view import render_detail_view

# Page config
st.set_page_config(
    page_title="GORE_OS - Visor de Migración",
    page_icon=":material/database:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "selected_table" not in st.session_state:
    st.session_state.selected_table = None
if "current_page" not in st.session_state:
    st.session_state.current_page = 0
if "filters" not in st.session_state:
    st.session_state.filters = {}
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "page_size" not in st.session_state:
    st.session_state.page_size = 20


@st.cache_resource
def get_connection():
    """Get cached database connection."""
    return st.connection("postgresql", type="sql", url=DATABASE_URL)


def get_available_tables(conn) -> dict:
    """Get tables that have data."""
    all_tables = get_all_tables()
    available = {}

    for table_name, config in all_tables.items():
        try:
            count_df = conn.query(
                f"SELECT COUNT(*) as count FROM {table_name} WHERE deleted_at IS NULL"
            )
            count = int(count_df.iloc[0]["count"])
            if count > 0:
                available[table_name] = {**config, "count": count}
        except Exception:
            # Table might not exist yet
            pass

    return available


def main():
    """Main application entry point."""

    # Header
    st.title(":material/database: Visor de Datos Migrados")
    st.caption("GORE_OS - Explorador de datos PostgreSQL")

    # Get database connection
    try:
        conn = get_connection()
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")
        st.info("Verifica que PostgreSQL esté corriendo en localhost:5433")
        return

    # Get available tables
    available_tables = get_available_tables(conn)

    if not available_tables:
        st.warning("No hay tablas con datos disponibles.")
        return

    # Render sidebar and get selected table
    selected_table = render_sidebar(available_tables)

    # If no table selected, show welcome message
    if not selected_table:
        st.info("Selecciona una tabla del menú lateral para comenzar a explorar.")

        # Show summary cards
        st.markdown("### Resumen de Datos")
        cols = st.columns(len(available_tables))
        for idx, (table_name, config) in enumerate(available_tables.items()):
            with cols[idx]:
                st.metric(
                    label=config.get("label", table_name),
                    value=f"{config.get('count', 0):,}"
                )
        return

    # Get table config
    table_config = available_tables.get(selected_table, {})

    # Header for selected table
    st.markdown(f"### :{table_config.get('icon', 'table')}: {table_config.get('label', selected_table)}")
    st.caption(f"`{selected_table}` - {table_config.get('count', 0):,} registros")

    # Search bar
    search_query = render_search_bar()

    # Filters
    filters = render_filters(selected_table, conn)

    # Build WHERE clause
    where_clause, params = build_where_clause(selected_table, search_query, filters)

    # Show active filter count
    active_filters = len([f for f in filters.values() if f])
    if active_filters > 0 or search_query:
        filter_info = []
        if search_query:
            filter_info.append(f"búsqueda: '{search_query}'")
        if active_filters:
            filter_info.append(f"{active_filters} filtro(s)")
        st.caption(f"Filtros activos: {', '.join(filter_info)}")

    # Data grid
    df = render_data_grid(selected_table, conn, where_clause, params)

    if not df.empty:
        # Render selectable table
        selected_row = render_data_table(df, selected_table)

        # Detail view for selected row
        if selected_row is not None:
            render_detail_view(selected_row, selected_table, conn)


if __name__ == "__main__":
    main()
