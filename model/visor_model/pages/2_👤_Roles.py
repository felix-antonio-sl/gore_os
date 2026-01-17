"""
Página: Roles - Vista Universal Canónica
"""

import streamlit as st
import db

st.set_page_config(page_title="Roles Canónicos", page_icon="🏛️", layout="wide")

st.title("🏛️ Roles Canónicos y Estructura Organizacional")
st.markdown("Visualización consolidada de la estructura Omega v2.6.0")

# ============================================================================
# FILTROS Y BÚSQUEDA
# ============================================================================
col1, col2 = st.columns([2, 1])

with col1:
    search = st.text_input(
        "🔍 Buscar rol canónico", placeholder="Ej: Analista, DAF, JUR..."
    )

with col2:
    div_filter = st.selectbox(
        "Filtrar por División",
        [
            "Todas",
            "GORE",
            "DAF",
            "JUR",
            "TIC",
            "DIPLADE",
            "DIPIR",
            "DIDESO",
            "DIFOI",
            "DIINF",
            "CIES",
            "STAFF",
            "EXT",
        ],
        index=0,
    )

# ============================================================================
# CARGAR DATOS
# ============================================================================
try:
    roles = db.get_canonical_roles(
        search=search if search else None,
        division=div_filter if div_filter != "Todas" else None,
    )

    # Agrupar por división para visualización
    roles_by_div = {}
    for r in roles:
        div = r["division"]
        if div not in roles_by_div:
            roles_by_div[div] = []
        roles_by_div[div].append(r)

    st.info(
        f"Mostrando {len(roles)} roles canónicos organizados en {len(roles_by_div)} divisiones"
    )

except Exception as e:
    st.error(f"Error al cargar roles canónicos: {e}")
    roles_by_div = {}

# ============================================================================
# RENDERIZAR VISTA JERÁRQUICA
# ============================================================================

# Orden de divisiones preferido
div_order = [
    "GORE",
    "DAF",
    "JUR",
    "TIC",
    "DIPLADE",
    "DIPIR",
    "DIDESO",
    "DIFOI",
    "DIINF",
    "CIES",
    "STAFF",
    "EXT",
]

for div in div_order:
    if div in roles_by_div:
        division_roles = roles_by_div[div]

        st.markdown(f"### 🏢 {div}")

        for role in division_roles:
            with st.expander(
                f"**{role['funcion']}** ({role['id']}) - {role['us_count']} US",
                expanded=False,
            ):
                # Layout de detalle
                c_main, c_spec, c_legacy = st.columns([2, 1, 1])

                with c_main:
                    st.markdown("#### ℹ️ Detalles")
                    st.write(f"**Nombre Oficial:** {role['label']}")
                    st.write(f"**Descripción:** {role['descripcion']}")
                    st.write(f"**Tipo:** `{role['agent_type']}`")

                    # Edición rápida
                    if st.checkbox("✏️ Editar", key=f"edit_{role['id']}"):
                        with st.form(key=f"form_{role['id']}"):
                            new_label = st.text_input("Label", role["label"])
                            new_desc = st.text_area("Descripción", role["descripcion"])
                            if st.form_submit_button("Guardar"):
                                db.update_canonical_role(
                                    role["id"], new_label, new_desc, role["agent_type"]
                                )
                                st.success("Guardado")
                                st.rerun()

                with c_spec:
                    st.markdown("#### 🎖️ Especialidades")
                    specs = db.get_role_specialties(role["id"])
                    if specs:
                        for s in specs:
                            st.markdown(
                                f"- **{s['especialidad']}**: {s['descripcion']}"
                            )
                    else:
                        st.caption("Sin especialidades definidas")

                with c_legacy:
                    st.markdown("#### 🕸️ Roles Legacy")
                    legacy = db.get_legacy_roles_by_canonical(role["id"])
                    if legacy:
                        for l in legacy:
                            spec_tag = (
                                f" `({l['especialidad']})`" if l["especialidad"] else ""
                            )
                            st.markdown(f"- `{l['id']}`{spec_tag}")
                    else:
                        st.caption("Sin roles legacy mapeados")

                st.divider()

                # US asociadas (Lazy load o link directo)
                if role["us_count"] > 0:
                    if st.button(
                        f"Ver {role['us_count']} User Stories",
                        key=f"btn_us_{role['id']}",
                    ):
                        us_list = db.get_us_by_role(role["id"])
                        for us in us_list:
                            st.markdown(
                                f"- [{us['priority']}] **{us['id']}**: {us['name']}"
                            )

        st.divider()
