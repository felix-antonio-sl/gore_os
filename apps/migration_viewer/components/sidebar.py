"""Sidebar component with table navigation."""

import streamlit as st
from models.registry import get_all_tables


def render_sidebar(available_tables: dict) -> str | None:
    """Render sidebar with table list and return selected table."""

    with st.sidebar:
        st.markdown("### :material/database: Tablas")

        # Summary Button
        if st.button(
            "📊 Resumen Dashboard",
            key="btn_dashboard",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.get("selected_table") is None
                else "secondary"
            ),
        ):
            st.session_state.selected_table = None
            st.session_state.search_query = ""
            st.rerun()

        st.markdown("---")

        selected_table = None

        for table_name, config in available_tables.items():
            count = config.get("count", 0)
            label = config.get("label", table_name)
            icon = config.get("icon", "table")

            # Create button for each table
            button_label = f":{icon}: {label} ({count:,})"

            if st.button(
                button_label,
                key=f"btn_{table_name}",
                use_container_width=True,
                type=(
                    "secondary"
                    if st.session_state.get("selected_table") != table_name
                    else "primary"
                ),
            ):
                st.session_state.selected_table = table_name
                st.session_state.current_page = 0
                st.session_state.filters = {}
                st.session_state.search_query = ""
                st.rerun()

        selected_table = st.session_state.get("selected_table")

        # Info section
        st.markdown("---")
        st.markdown("### :material/info: Info")
        total_records = sum(t.get("count", 0) for t in available_tables.values())
        st.metric("Total Registros", f"{total_records:,}")
        st.metric("Tablas Activas", len(available_tables))

    return selected_table
