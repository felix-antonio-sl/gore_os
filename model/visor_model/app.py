"""
GORE_OS US Model Editor - Streamlit Application
Visor y editor interactivo para el modelo de datos de User Stories
"""

import streamlit as st
from db import get_stats

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
st.set_page_config(
    page_title="GORE_OS Model Editor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS personalizados
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1e3a5f, #2d5a87);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .entity-tag {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        margin: 0.1rem;
        border-radius: 15px;
        font-size: 0.75rem;
        background: #e3f2fd;
        color: #1565c0;
    }
    .success-msg {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }
    .warning-msg {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================================
# PÁGINA PRINCIPAL
# ============================================================================
def main():
    st.markdown(
        '<h1 class="main-header">🔍 GORE_OS Model Editor</h1>', unsafe_allow_html=True
    )
    st.caption("Editor interactivo del modelo de datos de User Stories")

    # Intentar conexión
    try:
        stats = get_stats()
        connection_ok = True
    except Exception as e:
        connection_ok = False
        st.error(f"⚠️ No se pudo conectar a la base de datos: {e}")
        st.info("Asegúrate de que el contenedor PostgreSQL esté ejecutándose.")
        st.code("docker-compose up -d", language="bash")
        return

    # Stats
    st.markdown("---")
    cols = st.columns(6)
    metrics = [
        ("📋", "User Stories", stats["user_stories"]),
        ("👤", "Roles", stats["roles"]),
        ("📦", "Entidades", stats["entities"]),
        ("⚙️", "Procesos", stats["processes"]),
        ("🏷️", "Tags", stats["tags"]),
        ("✅", "Criterios AC", stats["acceptance_criteria"]),
    ]

    for col, (icon, label, value) in zip(cols, metrics):
        col.metric(f"{icon} {label}", f"{value:,}")

    st.markdown("---")

    # Instrucciones
    st.markdown(
        """
    ## 📑 Navegación
    
    Usa el menú lateral para explorar y editar cada dimensión del modelo:
    
    | Página | Descripción |
    |--------|-------------|
    | **📋 User Stories** | Ver, editar y eliminar User Stories |
    | **👤 Roles** | Explorar roles y sus US asociadas |
    | **📦 Entidades** | Navegar entidades por dominio |
    | **⚙️ Procesos** | Ver procesos y sus referencias |
    | **🏷️ Tags** | Explorar nube de tags |
    
    ---
    
    ### 🔧 Estado de la conexión
    """
    )

    if connection_ok:
        st.success("✅ Conectado a PostgreSQL")

    # Info de la base de datos
    st.markdown(
        """
    **Base de datos:** `goreos_model`  
    **Host:** `postgres` (Docker) / `localhost` (local)  
    **Puerto:** `5432`
    """
    )


if __name__ == "__main__":
    main()
