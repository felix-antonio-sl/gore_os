"""
Página: Tags - Nube de tags
"""

import streamlit as st
import db

st.set_page_config(page_title="Tags", page_icon="🏷️", layout="wide")

st.title("🏷️ Extra Tags")

# ============================================================================
# BÚSQUEDA
# ============================================================================
search = st.text_input("🔍 Buscar tag", placeholder="tag-name...")

# ============================================================================
# LISTA DE TAGS
# ============================================================================
try:
    tags = db.get_all_tags(search=search if search else None, limit=100)
    st.info(f"Mostrando {len(tags)} tags (ordenados por frecuencia)")
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    tags = []

# ============================================================================
# NUBE DE TAGS (vista rápida)
# ============================================================================
st.subheader("Top 30 Tags")
top_tags = tags[:30]
if top_tags:
    tags_html = " ".join(
        [
            f"<span style='display:inline-block; padding:0.3rem 0.6rem; margin:0.2rem; "
            f"border-radius:15px; background:#e3f2fd; color:#1565c0; font-size:{max(0.7, min(1.5, 0.7 + t['usage_count']/50))}rem;'>"
            f"{t['tag']} ({t['usage_count']})</span>"
            for t in top_tags
        ]
    )
    st.markdown(tags_html, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# DETALLE DE TAGS
# ============================================================================
st.subheader("Detalle por Tag")

for tag in tags[:50]:
    try:
        us_list = db.get_us_by_tag(tag["tag"])
        us_count = len(us_list)
    except:
        us_count = 0
        us_list = []

    with st.expander(f"🏷️ `{tag['tag']}` ({us_count} US)", expanded=False):
        st.markdown(f"**Uso:** {tag['usage_count'] or 0} menciones")

        if us_list:
            st.markdown("**User Stories con este tag:**")
            for us in us_list[:10]:
                st.markdown(
                    f"- `{us['id']}`: {us['name'][:50] if us['name'] else ''}..."
                )
            if len(us_list) > 10:
                st.caption(f"... y {len(us_list) - 10} más")
