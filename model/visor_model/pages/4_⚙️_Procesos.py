"""
Página: Procesos - Explorador
"""

import streamlit as st
import db

st.set_page_config(page_title="Procesos", page_icon="⚙️", layout="wide")

st.title("⚙️ Procesos")

# ============================================================================
# BÚSQUEDA
# ============================================================================
search = st.text_input("🔍 Buscar proceso", placeholder="PROC-...")

# ============================================================================
# LISTA DE PROCESOS
# ============================================================================
try:
    processes = db.get_all_processes(search=search if search else None)
    st.info(f"Mostrando {len(processes)} procesos")
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    processes = []

# ============================================================================
# RENDERIZAR PROCESOS
# ============================================================================
for proc in processes[:50]:
    try:
        us_list = db.get_us_by_process(proc["id"])
        us_count = len(us_list)
    except:
        us_count = 0
        us_list = []

    with st.expander(f"⚙️ `{proc['id']}` ({us_count} US)", expanded=False):
        st.markdown(f"**Uso:** {proc['usage_count'] or 0} referencias")

        if us_list:
            st.markdown("**User Stories que lo referencian:**")
            for us in us_list[:10]:
                st.markdown(
                    f"- `{us['id']}`: {us['name'][:50] if us['name'] else ''}..."
                )
            if len(us_list) > 10:
                st.caption(f"... y {len(us_list) - 10} más")
