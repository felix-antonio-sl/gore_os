"""
Página: User Stories - CRUD completo
"""

import streamlit as st
import db

st.set_page_config(page_title="User Stories", page_icon="📋", layout="wide")

st.title("📋 User Stories")

# ============================================================================
# FILTROS
# ============================================================================
col1, col2, col3 = st.columns(3)

with col1:
    try:
        domains = ["Todos"] + db.get_domains()
    except:
        domains = ["Todos"]
    selected_domain = st.selectbox("Dominio", domains)

with col2:
    try:
        priorities = ["Todos"] + db.get_priorities()
    except:
        priorities = ["Todos"]
    selected_priority = st.selectbox("Prioridad", priorities)

with col3:
    search = st.text_input("🔍 Buscar", placeholder="ID o nombre...")

# ============================================================================
# LISTA DE USER STORIES
# ============================================================================
domain_filter = None if selected_domain == "Todos" else selected_domain
priority_filter = None if selected_priority == "Todos" else selected_priority
search_filter = search if search else None

try:
    user_stories = db.get_all_user_stories(
        limit=50, domain=domain_filter, priority=priority_filter, search=search_filter
    )
    total = len(user_stories)
    st.info(f"Mostrando {total} User Stories")
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    user_stories = []

# ============================================================================
# RENDERIZAR USER STORIES
# ============================================================================
for us in user_stories:
    with st.expander(
        f"📋 **{us['id']}** - {us['name'][:60] if us['name'] else 'Sin nombre'}...",
        expanded=False,
    ):

        # Modo edición
        edit_mode = st.checkbox(f"✏️ Editar", key=f"edit_{us['id']}")

        if edit_mode:
            # Formulario de edición
            with st.form(key=f"form_{us['id']}"):
                col1, col2 = st.columns(2)

                with col1:
                    new_name = st.text_input("Nombre", value=us["name"] or "")
                    new_as_a = st.text_input("Como (as_a)", value=us["as_a"] or "")
                    new_i_want = st.text_area(
                        "Quiero (i_want)", value=us["i_want"] or ""
                    )
                    new_so_that = st.text_area(
                        "Para (so_that)", value=us["so_that"] or ""
                    )

                with col2:
                    new_domain = st.text_input("Dominio", value=us["domain"] or "")
                    new_aspect = st.text_input("Aspecto", value=us["aspect"] or "")
                    new_priority = st.selectbox(
                        "Prioridad",
                        ["P0", "P1", "P2"],
                        index=(
                            ["P0", "P1", "P2"].index(us["priority"])
                            if us["priority"] in ["P0", "P1", "P2"]
                            else 1
                        ),
                    )
                    new_scope = st.text_input("Scope", value=us["scope"] or "")
                    new_status = st.selectbox(
                        "Status",
                        ["ENRICHED", "DRAFT"],
                        index=0 if us["status"] == "ENRICHED" else 1,
                    )

                col_save, col_delete = st.columns([3, 1])

                with col_save:
                    if st.form_submit_button("💾 Guardar cambios", type="primary"):
                        data = {
                            "name": new_name,
                            "as_a": new_as_a,
                            "i_want": new_i_want,
                            "so_that": new_so_that,
                            "domain": new_domain,
                            "aspect": new_aspect,
                            "priority": new_priority,
                            "scope": new_scope,
                            "status": new_status,
                        }
                        try:
                            db.update_user_story(us["id"], data)
                            st.success("✅ Cambios guardados")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

                with col_delete:
                    if st.form_submit_button("🗑️ Eliminar", type="secondary"):
                        try:
                            db.delete_user_story(us["id"])
                            st.success("✅ US eliminada")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
        else:
            # Modo vista
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Como** {us['as_a'] or 'N/A'}")
                st.markdown(f"**Quiero** {us['i_want'] or 'N/A'}")
                st.markdown(f"**Para** {us['so_that'] or 'N/A'}")

            with col2:
                st.markdown(f"**Dominio:** `{us['domain'] or 'N/A'}`")
                st.markdown(f"**Prioridad:** `{us['priority'] or 'N/A'}`")
                st.markdown(f"**Aspecto:** `{us['aspect'] or 'N/A'}`")
                st.markdown(f"**Rol:** `{us['role_id'] or 'N/A'}`")
                st.markdown(f"**Proceso:** `{us['process_id'] or 'N/A'}`")

            # Acceptance Criteria
            try:
                criteria = db.get_acceptance_criteria(us["id"])
                if criteria:
                    st.markdown("**✅ Criterios de Aceptación:**")
                    for ac in criteria:
                        col_ac, col_del = st.columns([10, 1])
                        with col_ac:
                            st.markdown(f"- {ac['description']}")
                        with col_del:
                            if st.button(
                                "🗑️", key=f"del_ac_{ac['id']}", help="Eliminar criterio"
                            ):
                                db.delete_acceptance_criterion(ac["id"])
                                st.rerun()

                # Agregar nuevo criterio
                with st.form(key=f"new_ac_{us['id']}"):
                    new_ac = st.text_input(
                        "Nuevo criterio de aceptación", key=f"input_ac_{us['id']}"
                    )
                    if st.form_submit_button("➕ Agregar"):
                        if new_ac:
                            db.add_acceptance_criterion(us["id"], new_ac)
                            st.rerun()
            except Exception as e:
                st.caption(f"Error cargando AC: {e}")
