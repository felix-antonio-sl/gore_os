"""
Página: Entidades - Explorador por dominio
"""

import streamlit as st
import db

st.set_page_config(page_title="Entidades", page_icon="📦", layout="wide")

st.title("📦 Entidades")

# ============================================================================
# FILTROS
# ============================================================================
col1, col2 = st.columns([1, 3])

with col1:
    try:
        domains = ["Todos"] + db.get_entity_domains()
    except:
        domains = ["Todos"]
    selected_domain = st.selectbox("Dominio", domains)

with col2:
    search = st.text_input("🔍 Buscar entidad", placeholder="ENT-...")

# ============================================================================
# LISTA DE ENTIDADES
# ============================================================================
domain_filter = None if selected_domain == "Todos" else selected_domain
search_filter = search if search else None

try:
    entities = db.get_all_entities(domain=domain_filter, search=search_filter)
    st.info(f"Mostrando {len(entities)} entidades")
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    entities = []

# ============================================================================
# RENDERIZAR ENTIDADES
# ============================================================================
for ent in entities[:50]:  # Limitar para performance
    try:
        us_list = db.get_us_by_entity(ent["id"])
        us_count = len(us_list)
    except:
        us_count = 0
        us_list = []

    with st.expander(f"📦 `{ent['id']}` ({us_count} US)", expanded=False):
        st.markdown(f"**Dominio:** `{ent['domain'] or 'N/A'}`")
        st.markdown(f"**Uso:** {ent['usage_count'] or 0} menciones")

        if us_list:
            st.markdown("**User Stories que la mencionan:**")
            for us in us_list[:10]:
                status_badge = f"[{us['link_status']}]" if us.get("link_status") else ""
                st.markdown(
                    f"- `{us['id']}` {status_badge}: {us['name'][:50] if us['name'] else ''}..."
                )
            if len(us_list) > 10:
                st.caption(f"... y {len(us_list) - 10} más")
