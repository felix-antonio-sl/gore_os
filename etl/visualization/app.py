import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import glob
import json

# Configuration
st.set_page_config(
    page_title="GORE OS - Legacy Explorer v3.0",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paths
BASE_DIR = Path(__file__).parent.parent / "normalized"


# --- Data Loading ---
@st.cache_data
def load_data(category, filename):
    """Load a specific CSV file."""
    path = BASE_DIR / category / filename
    if path.exists():
        return pd.read_csv(path)
    return None


@st.cache_data
def load_all_metadata():
    """Load metadata counts for dashboard."""
    counts = {}
    for cat in ["dimensions", "facts", "documents", "relationships"]:
        files = glob.glob(str(BASE_DIR / cat / "*.csv"))
        for f in files:
            name = Path(f).stem
            df = pd.read_csv(f)
            counts[name] = len(df)
    return counts


# --- Views ---


def show_dashboard():
    st.title("📊 GORE OS - Dashboard Principal")

    counts = load_all_metadata()

    # Top KPIs - Row 1
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Iniciativas Unificadas", f"{counts.get('dim_iniciativa_unificada', 0):,}"
        )
    with col2:
        st.metric("Instituciones", f"{counts.get('dim_institucion_unificada', 0):,}")
    with col3:
        st.metric("Documentos", f"{counts.get('doc_documento', 0):,}")
    with col4:
        st.metric("Cross-Domain Links", f"{counts.get('cross_domain_matches', 0):,}")

    # Row 2 - Omega Dimensions
    st.markdown("### 📐 Catálogos Omega")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Divisiones GORE", f"{counts.get('dim_division', 0)}")
    with c2:
        st.metric("Mecanismos Fin.", f"{counts.get('dim_mecanismo_financiamiento', 0)}")
    with c3:
        st.metric("Estados IPR", f"{counts.get('dim_estado_ipr', 0)}")
    with c4:
        st.metric("Comunas", f"{counts.get('dim_territorio_canonico', 0)}")
    with c5:
        st.metric("Trazos 250", f"{counts.get('dim_trazo_250', 0)}")

    st.divider()

    # Charts Row
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 📈 Volumen por Tabla de Hechos")
        facts_data = {k: v for k, v in counts.items() if k.startswith("fact_")}
        if facts_data:
            df_facts = pd.DataFrame(
                list(facts_data.items()), columns=["Tabla", "Registros"]
            )
            df_facts = df_facts.sort_values("Registros", ascending=True)
            fig = px.bar(
                df_facts,
                x="Registros",
                y="Tabla",
                orientation="h",
                color="Registros",
                color_continuous_scale="Blues",
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### 🏛️ Instituciones por Tipo")
        df_inst = load_data("dimensions", "dim_institucion_unificada.csv")
        if df_inst is not None and "tipo_institucion" in df_inst.columns:
            tipo_counts = df_inst["tipo_institucion"].value_counts().reset_index()
            tipo_counts.columns = ["Tipo", "Cantidad"]
            fig_pie = px.pie(tipo_counts, names="Tipo", values="Cantidad", hole=0.4)
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)


def show_buscador_360():
    st.title("🔎 Buscador 360°")
    st.markdown("Explora una iniciativa y ve toda su información relacionada.")

    df_uni = load_data("dimensions", "dim_iniciativa_unificada.csv")
    if df_uni is None:
        st.error("No se encontró dim_iniciativa_unificada.csv")
        return

    # Search box
    search_query = st.text_input("Buscar por Código, Nombre o BIP...", "")

    if search_query:
        # Filter
        mask = (
            df_uni["codigo_normalizado"]
            .astype(str)
            .str.contains(search_query, case=False, na=False)
            | df_uni["nombre_iniciativa"].str.contains(
                search_query, case=False, na=False
            )
            | df_uni["bip"].astype(str).str.contains(search_query, case=False, na=False)
            | df_uni["cod_unico_idis"]
            .astype(str)
            .str.contains(search_query, case=False, na=False)
        )
        results = df_uni[mask]
        st.info(f"Encontrados: {len(results)} registros")

        if not results.empty:
            selected_id = results.iloc[0]["id"]
            if len(results) > 1:
                selected_option = st.selectbox(
                    "Selecciona una iniciativa:",
                    options=results["id"].tolist(),
                    format_func=lambda x: f"{results[results['id']==x].iloc[0]['codigo_normalizado']} - {results[results['id']==x].iloc[0]['nombre_iniciativa'][:60]}...",
                )
                selected_id = selected_option

            # Detail View
            record = df_uni[df_uni["id"] == selected_id].iloc[0]

            st.divider()
            st.header(f"{record['nombre_iniciativa']}")

            # Key IDs Row 1
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Código Unificado", record.get("codigo_normalizado", "N/A"))
            c2.metric(
                "BIP",
                record.get("bip", "N/A") if pd.notna(record.get("bip")) else "N/A",
            )
            c3.metric("Fuente", record.get("fuente_principal", "N/A"))
            c4.metric(
                "Etapa",
                record.get("etapa", "N/A") if pd.notna(record.get("etapa")) else "N/A",
            )

            # Omega Fields Row 2
            if "tipo_ipr" in record:
                c5, c6, c7, c8 = st.columns(4)
                c5.metric("Tipo IPR", record.get("tipo_ipr", "N/A"))
                c6.metric("Mecanismo", record.get("mecanismo_id", "N/A"))
                c7.metric("Tipología", record.get("tipologia", "N/A") or "N/A")
                c8.metric("Comuna", record.get("comuna", "N/A") or "N/A")

            st.divider()

            # Origin IDs
            st.markdown("#### 🔗 IDs Originales")
            cols = st.columns(4)
            with cols[0]:
                if pd.notna(record["cod_unico_idis"]):
                    st.success(f"🆔 **IDIS**: {record['cod_unico_idis']}")
                else:
                    st.caption("No vinculado a IDIS")
            with cols[1]:
                if pd.notna(record["codigo_convenios"]):
                    st.success(f"🤝 **CONVENIOS**: {record['codigo_convenios']}")
                else:
                    st.caption("No vinculado a Convenios")
            with cols[2]:
                if pd.notna(record.get("codigo_fril")):
                    st.success(f"🏗️ **FRIL**: {record['codigo_fril']}")
                else:
                    st.caption("No vinculado a FRIL")
            with cols[3]:
                if pd.notna(record.get("codigo_progs")):
                    st.success(f"📋 **PROGS**: {record['codigo_progs']}")
                else:
                    st.caption("No vinculado a PROGS")


def show_catalogos_omega():
    st.title("📐 Catálogos Omega")
    st.markdown("Dimensiones estándar basadas en el modelo conceptual GORE Ñuble.")

    tab_mec, tab_div, tab_est, tab_ter = st.tabs(
        ["Mecanismos Financiamiento", "Divisiones GORE", "Estados IPR", "Territorio"]
    )

    with tab_mec:
        st.markdown("### 💰 Mecanismos de Financiamiento (8)")
        df = load_data("dimensions", "dim_mecanismo_financiamiento.csv")
        if df is not None:
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Visual
            fig = px.treemap(
                df,
                path=["tipo_ipr", "codigo"],
                values=[1] * len(df),
                color="tipo_ipr",
                title="Mecanismos por Tipo IPR",
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab_div:
        st.markdown("### 🏛️ Divisiones Orgánicas GORE (6)")
        df = load_data("dimensions", "dim_division.csv")
        if df is not None:
            for _, row in df.iterrows():
                with st.expander(f"**{row['codigo']}**: {row['nombre']}"):
                    st.write(f"**Jefatura**: {row['jefatura']}")
                    st.write(f"**Departamentos**: {row['departamentos']}")
                    st.caption(row["descripcion"])

    with tab_est:
        st.markdown("### 📊 Estados del Ciclo de Vida IPR (28)")
        df = load_data("dimensions", "dim_estado_ipr.csv")
        if df is not None:
            # Group by fase
            fases = df["fase"].unique()
            for fase in fases:
                with st.expander(f"**{fase}**"):
                    fase_df = df[df["fase"] == fase][
                        ["codigo", "nombre", "aplica_a", "descripcion"]
                    ]
                    st.dataframe(fase_df, use_container_width=True, hide_index=True)

            # Timeline visualization
            fig = px.scatter(
                df,
                x="orden",
                y="fase",
                text="codigo",
                color="aplica_a",
                size=[10] * len(df),
                title="Línea de Tiempo de Estados IPR",
            )
            fig.update_traces(textposition="top center")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    with tab_ter:
        st.markdown("### 🗺️ Territorio - Comunas de Ñuble (21)")
        df = load_data("dimensions", "dim_territorio_canonico.csv")
        if df is not None:
            # Group by provincia
            for prov in df["provincia"].dropna().unique():
                with st.expander(f"**Provincia de {prov}**"):
                    prov_df = df[df["provincia"] == prov]["nombre_oficial"]
                    st.write(", ".join(prov_df.tolist()))


def show_instituciones():
    st.title("🏢 Explorador de Instituciones")

    df = load_data("dimensions", "dim_institucion_unificada.csv")
    if df is None:
        st.error("No se encontró dim_institucion_unificada.csv")
        return

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        if "tipo_institucion" in df.columns:
            tipo_filter = st.multiselect(
                "Filtrar por Tipo", df["tipo_institucion"].unique()
            )
    with col2:
        search = st.text_input("Buscar por nombre...")

    # Apply filters
    filtered = df.copy()
    if "tipo_institucion" in df.columns and tipo_filter:
        filtered = filtered[filtered["tipo_institucion"].isin(tipo_filter)]
    if search:
        filtered = filtered[
            filtered["nombre_original"].str.contains(search, case=False, na=False)
        ]

    st.info(f"Mostrando {len(filtered):,} de {len(df):,} instituciones")

    # Stats by type
    if "tipo_institucion" in df.columns:
        st.markdown("### Distribución por Tipo")
        tipo_counts = filtered["tipo_institucion"].value_counts()
        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.dataframe(
                tipo_counts.reset_index().rename(
                    columns={"index": "Tipo", "tipo_institucion": "Total"}
                )
            )
        with col_b:
            fig = px.bar(
                x=tipo_counts.index,
                y=tipo_counts.values,
                labels={"x": "Tipo", "y": "Cantidad"},
            )
            st.plotly_chart(fig, use_container_width=True)

    # Table
    st.markdown("### Listado")

    # Robust column selection
    possible_cols = [
        "nombre_original",
        "rut",
        "tipo_institucion",
        "fuente_original",
        "nombre_normalizado",
    ]
    display_cols = [c for c in possible_cols if c in filtered.columns]

    st.dataframe(
        filtered[display_cols].head(100), use_container_width=True, hide_index=True
    )


def show_matrix():
    st.title("🔗 Matriz de Relaciones NxN")
    st.markdown("Heatmap de relaciones entre **todos** los archivos fuente legacy.")

    matrix_path = BASE_DIR / "relationships" / "relationship_matrix.json"
    if not matrix_path.exists():
        st.warning(
            "Matriz no generada. Ejecuta `python generate_relationship_matrix.py` primero."
        )
        return

    with open(matrix_path, "r") as f:
        matrix_data = json.load(f)

    files = matrix_data["files"]
    adj_matrix = matrix_data["adjacency_matrix"]
    relationships = matrix_data["relationships"]

    col1, col2 = st.columns(2)
    col1.metric("Archivos Analizados", len(files))
    col2.metric("Relaciones Encontradas", len(relationships))

    # Create heatmap
    import numpy as np

    labels = [f["path"].split("/")[-1][:20] for f in files]
    z = np.array(adj_matrix)

    fig = px.imshow(
        z,
        labels=dict(x="Archivo B", y="Archivo A", color="Strength"),
        x=labels,
        y=labels,
        color_continuous_scale="Blues",
        aspect="auto",
        title="Matriz de Adyacencia (Fuerza de Relación)",
    )
    fig.update_layout(height=700)
    st.plotly_chart(fig, use_container_width=True)

    # Top relationships
    st.markdown("### 🔝 Top 20 Relaciones")
    top_rels = sorted(relationships, key=lambda x: -x["total_matches"])[:20]
    df_rels = pd.DataFrame(top_rels)
    st.dataframe(
        df_rels[
            [
                "file_a",
                "file_b",
                "codigo_matches",
                "rut_matches",
                "comuna_matches",
                "total_matches",
            ]
        ],
        hide_index=True,
    )


def show_plan_250():
    st.title("📅 Plan 250 - Inversiones 2026-2029")

    df = load_data("facts", "fact_iniciativa_250.csv")
    if df is None:
        st.error("No se encontró fact_iniciativa_250.csv")
        return

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Iniciativas", f"{len(df):,}")
    c2.metric(
        "Monto Total (M$)",
        f"{df['monto'].sum():,.0f}" if "monto" in df.columns else "N/A",
    )
    c3.metric("Financiadas", len(df[df["estado_financiero"] == "FINANCIADO"]))
    c4.metric("No Financiadas", len(df[df["estado_financiero"] == "NO FINANCIADO"]))

    st.divider()

    # By Trazo
    st.markdown("### Por Trazo Estratégico")
    trazo_counts = df["trazo_primario"].value_counts().reset_index()
    trazo_counts.columns = ["Trazo", "Cantidad"]
    fig = px.bar(
        trazo_counts,
        x="Trazo",
        y="Cantidad",
        color="Trazo",
        title="Iniciativas por Trazo",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Table
    st.markdown("### Listado de Iniciativas")
    display_cols = [
        "trazo_primario",
        "nombre_iniciativa",
        "division",
        "bip",
        "estado_financiero",
        "monto",
    ]
    cols_available = [c for c in display_cols if c in df.columns]
    st.dataframe(df[cols_available], use_container_width=True, hide_index=True)


def show_explorer():
    st.title("📁 Explorador de Tablas")

    category = st.selectbox(
        "Categoría", ["dimensions", "facts", "documents", "relationships", "metadata"]
    )

    files = [Path(f).name for f in glob.glob(str(BASE_DIR / category / "*.csv"))]
    selected_file = st.selectbox("Archivo", sorted(files))

    if selected_file:
        df = load_data(category, selected_file)
        if df is not None:
            st.write(f"**Registros:** {len(df):,} | **Columnas:** {len(df.columns)}")
            st.dataframe(df, use_container_width=True, hide_index=True)


# --- Main App Structure ---


def show_ipr_explorer():
    st.title("🏛️ Explorador IPR - Intervenciones Públicas Regionales")
    st.markdown(
        "Las IPRs son los **ciudadanos de primera categoría** del sistema GORE."
    )

    df_uni = load_data("dimensions", "dim_iniciativa_unificada.csv")
    df_mec = load_data("dimensions", "dim_mecanismo_financiamiento.csv")

    if df_uni is None:
        st.error("No se encontró dim_iniciativa_unificada.csv")
        return

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        tipo_filter = st.multiselect(
            "Tipo IPR",
            df_uni["tipo_ipr"].unique() if "tipo_ipr" in df_uni.columns else [],
        )
    with col2:
        fuente_filter = st.multiselect(
            "Fuente",
            (
                df_uni["fuente_principal"].unique()
                if "fuente_principal" in df_uni.columns
                else []
            ),
        )
    with col3:
        search = st.text_input("Buscar nombre/código...")

    filtered = df_uni.copy()
    if tipo_filter:
        filtered = filtered[filtered["tipo_ipr"].isin(tipo_filter)]
    if fuente_filter:
        filtered = filtered[filtered["fuente_principal"].isin(fuente_filter)]
    if search:
        mask = filtered["nombre_iniciativa"].str.contains(
            search, case=False, na=False
        ) | filtered["codigo_normalizado"].astype(str).str.contains(
            search, case=False, na=False
        )
        filtered = filtered[mask]

    st.info(f"Mostrando {len(filtered):,} de {len(df_uni):,} IPRs")

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total IPRs", f"{len(filtered):,}")
    with c2:
        linked = (
            len(
                filtered[
                    filtered[["cod_unico_idis", "codigo_convenios", "codigo_fril"]]
                    .notna()
                    .sum(axis=1)
                    > 1
                ]
            )
            if all(
                c in filtered.columns
                for c in ["cod_unico_idis", "codigo_convenios", "codigo_fril"]
            )
            else 0
        )
        st.metric("Cross-Domain", f"{linked:,}")
    with c3:
        if "tipo_ipr" in filtered.columns:
            st.metric("Proyectos", len(filtered[filtered["tipo_ipr"] == "PROYECTO"]))
    with c4:
        if "tipo_ipr" in filtered.columns:
            st.metric("Programas", len(filtered[filtered["tipo_ipr"] == "PROGRAMA"]))

    st.divider()

    # Charts
    col_a, col_b = st.columns(2)
    with col_a:
        if "fuente_principal" in filtered.columns:
            st.markdown("### Por Fuente de Datos")
            fig = px.pie(filtered, names="fuente_principal", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    with col_b:
        if "mecanismo_id" in filtered.columns and df_mec is not None:
            st.markdown("### Por Mecanismo de Financiamiento")
            mec_counts = filtered["mecanismo_id"].value_counts().reset_index()
            mec_counts.columns = ["mecanismo_id", "count"]
            mec_counts = mec_counts.merge(
                df_mec[["id", "nombre"]],
                left_on="mecanismo_id",
                right_on="id",
                how="left",
            )
            fig = px.bar(mec_counts, x="nombre", y="count", color="nombre")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # Table with Selection
    st.markdown("### 📋 Listado de IPRs")

    # Create a selection mechanism
    if not filtered.empty:
        # Selectbox for IPR selection
        ipr_options = filtered.apply(
            lambda r: f"{r.get('codigo_normalizado', 'N/A')} - {str(r.get('nombre_iniciativa', ''))[:50]}...",
            axis=1,
        ).tolist()

        selected_idx = st.selectbox(
            "Seleccionar IPR para ver detalle:",
            range(len(ipr_options)),
            format_func=lambda i: ipr_options[i],
        )

        # Show table preview
        possible_cols = [
            "codigo_normalizado",
            "nombre_iniciativa",
            "tipo_ipr",
            "fuente_principal",
            "bip",
        ]
        display_cols = [c for c in possible_cols if c in filtered.columns]
        st.dataframe(
            filtered[display_cols].head(50), use_container_width=True, hide_index=True
        )

        # Detail View Panel
        st.divider()
        st.markdown("## 📄 Vista Detalle IPR")

        record = filtered.iloc[selected_idx]

        # Header
        st.subheader(f"🏛️ {record.get('nombre_iniciativa', 'Sin Nombre')}")

        # Main attributes
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Código Unificado", record.get("codigo_normalizado", "N/A"))
        with col2:
            st.metric(
                "BIP",
                record.get("bip", "N/A") if pd.notna(record.get("bip")) else "N/A",
            )
        with col3:
            st.metric("Tipo IPR", record.get("tipo_ipr", "N/A"))
        with col4:
            st.metric("Mecanismo", record.get("mecanismo_id", "N/A"))

        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("Fuente Principal", record.get("fuente_principal", "N/A"))
        with col6:
            st.metric(
                "Etapa",
                record.get("etapa", "N/A") if pd.notna(record.get("etapa")) else "N/A",
            )
        with col7:
            st.metric(
                "Tipología",
                (
                    record.get("tipologia", "N/A")
                    if pd.notna(record.get("tipologia"))
                    else "N/A"
                ),
            )
        with col8:
            st.metric(
                "Comuna",
                (
                    record.get("comuna", "N/A")
                    if pd.notna(record.get("comuna"))
                    else "N/A"
                ),
            )

        # Cross-Domain Links
        st.markdown("### 🔗 Enlaces Cross-Domain")
        link_cols = st.columns(4)

        with link_cols[0]:
            idis_code = record.get("cod_unico_idis")
            if pd.notna(idis_code):
                st.success(f"✅ **IDIS**\n\n`{idis_code}`")
            else:
                st.info("❌ No vinculado a IDIS")

        with link_cols[1]:
            conv_code = record.get("codigo_convenios")
            if pd.notna(conv_code):
                st.success(f"✅ **CONVENIOS**\n\n`{conv_code}`")
            else:
                st.info("❌ No vinculado a Convenios")

        with link_cols[2]:
            fril_code = record.get("codigo_fril")
            if pd.notna(fril_code):
                st.success(f"✅ **FRIL**\n\n`{fril_code}`")
            else:
                st.info("❌ No vinculado a FRIL")

        with link_cols[3]:
            progs_code = record.get("codigo_progs")
            if pd.notna(progs_code):
                st.success(f"✅ **PROGS**\n\n`{progs_code}`")
            else:
                st.info("❌ No vinculado a PROGS")

        # Related Data Tabs
        st.markdown("### 📊 Datos Relacionados")
        tab_fin, tab_conv, tab_fril, tab_progs, tab_raw = st.tabs(
            ["💰 Financiero", "📄 Convenios", "🏗️ FRIL", "📋 PROGS (8%)", "🔧 Raw Data"]
        )

        with tab_fin:
            if pd.notna(record.get("cod_unico_idis")):
                df_lines = load_data("facts", "fact_linea_presupuestaria.csv")
                df_dim_idis = load_data("dimensions", "dim_iniciativa_idis.csv")

                if df_lines is not None and df_dim_idis is not None:
                    idis_rec = df_dim_idis[
                        df_dim_idis["cod_unico"] == record["cod_unico_idis"]
                    ]
                    if not idis_rec.empty:
                        idis_id = idis_rec.iloc[0]["id"]
                        lines = df_lines[df_lines["iniciativa_id"] == idis_id]

                        if not lines.empty:
                            st.write(
                                f"**{len(lines)} Líneas Presupuestarias encontradas**"
                            )
                            line_cols = [
                                "anio_presupuestario",
                                "subtitulo",
                                "item",
                                "monto_vigente",
                                "tipo_ipr",
                            ]
                            avail_cols = [c for c in line_cols if c in lines.columns]
                            st.dataframe(
                                lines[avail_cols],
                                use_container_width=True,
                                hide_index=True,
                            )
                        else:
                            st.info("Sin líneas presupuestarias asociadas")
                    else:
                        st.info("No se encontró registro IDIS")
            else:
                st.info("Esta IPR no tiene datos financieros de IDIS")

        with tab_conv:
            if pd.notna(record.get("codigo_convenios")):
                df_fact_conv = load_data("facts", "fact_convenio.csv")
                df_dim_conv = load_data("dimensions", "dim_iniciativa.csv")

                if df_fact_conv is not None and df_dim_conv is not None:
                    conv_rec = df_dim_conv[
                        df_dim_conv["codigo"] == record["codigo_convenios"]
                    ]
                    if not conv_rec.empty:
                        conv_ids = conv_rec["id"].tolist()
                        agreements = df_fact_conv[
                            df_fact_conv["iniciativa_id"].isin(conv_ids)
                        ]

                        if not agreements.empty:
                            st.write(f"**{len(agreements)} Convenios encontrados**")
                            conv_cols = [
                                "fecha_firma_convenio",
                                "monto_fndr_ms",
                                "estado_convenio_norm",
                                "estado_cgr_norm",
                            ]
                            avail_cols = [
                                c for c in conv_cols if c in agreements.columns
                            ]
                            st.dataframe(
                                agreements[avail_cols],
                                use_container_width=True,
                                hide_index=True,
                            )
                        else:
                            st.info("Sin convenios asociados")
                    else:
                        st.info("No se encontró registro de convenio")
            else:
                st.info("Esta IPR no tiene datos de Convenios")

        with tab_fril:
            if pd.notna(record.get("codigo_fril")):
                df_fril = load_data("facts", "fact_fril.csv")
                if df_fril is not None:
                    fril_items = df_fril[df_fril["codigo"] == record["codigo_fril"]]
                    if not fril_items.empty:
                        st.write(f"**{len(fril_items)} Registros FRIL encontrados**")
                        st.dataframe(
                            fril_items, use_container_width=True, hide_index=True
                        )
                    else:
                        st.info("Sin registros FRIL asociados")
            else:
                st.info("Esta IPR no tiene datos de FRIL")

        with tab_progs:
            if pd.notna(record.get("codigo_progs")):
                df_progs = load_data("facts", "fact_rendicion_8pct.csv")
                if df_progs is not None:
                    progs_items = df_progs[df_progs["codigo"] == record["codigo_progs"]]
                    if not progs_items.empty:
                        st.write(f"**{len(progs_items)} Rendiciones 8% encontradas**")
                        st.dataframe(
                            progs_items, use_container_width=True, hide_index=True
                        )
                    else:
                        st.info("Sin rendiciones PROGS asociadas")
            else:
                st.info("Esta IPR no tiene datos de PROGS (8%)")

        with tab_raw:
            st.markdown("**Todos los atributos del registro:**")
            st.json(record.to_dict())


def show_gestion_presupuestaria():
    st.title("💸 Gestión Presupuestaria")
    st.markdown("Análisis de modificaciones y ejecución presupuestaria regional.")

    tab_mod, tab_exec = st.tabs(["Modificaciones Presupuestarias", "Ejecución Mensual"])

    with tab_mod:
        df_mod = load_data("facts", "fact_modificacion.csv")
        if df_mod is not None:
            st.metric("Total Modificaciones", f"{len(df_mod):,}")

            # Filters
            sub = st.selectbox(
                "Subtítulo", ["Todos"] + sorted(df_mod["subtitulo"].unique().tolist())
            )
            if sub != "Todos":
                df_mod = df_mod[df_mod["subtitulo"] == sub]

            st.dataframe(df_mod, use_container_width=True, hide_index=True)

            # Chart
            fig = px.histogram(
                df_mod,
                x="subtitulo",
                y="modificacion",
                color="tipo_bloque",
                title="Impacto de Modificaciones por Subtítulo",
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab_exec:
        df_exec = load_data("facts", "fact_ejecucion_mensual.csv")
        if df_exec is not None:
            st.metric("Registros de Ejecución", f"{len(df_exec):,}")

            # Pivot by month/year
            exec_pivot = (
                df_exec.groupby(["anio", "mes", "tipo"])["monto"].sum().reset_index()
            )
            fig = px.line(
                exec_pivot,
                x="mes",
                y="monto",
                color="tipo",
                facet_col="anio",
                title="Evolución de la Ejecución Presupuestaria",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_exec.head(100), use_container_width=True, hide_index=True)


def show_recursos_humanos():
    st.title("👥 Recursos Humanos (Capital Humano)")
    st.markdown("Exploración de la dotación y estructura de personal del GORE.")

    df_func = load_data("facts", "fact_funcionario.csv")
    if df_func is not None:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Dotación", f"{df_func['nombre_completo'].nunique():,}")
        col2.metric(
            "Gasto Bruto Mensual (M$)",
            f"{(df_func['remuneracion_bruta'].sum()/1000):,.0f}",
        )
        col3.metric(
            "Promedio Bruto (M$)", f"{(df_func['remuneracion_bruta'].mean()/1000):,.1f}"
        )

        st.divider()

        # Breakdown by estamento
        st.markdown("### Dotación por Estamento")
        est_counts = df_func.groupby("estamento").size().reset_index(name="Personal")
        fig = px.bar(est_counts, x="estamento", y="Personal", color="estamento")
        st.plotly_chart(fig, use_container_width=True)

        # Table
        st.markdown("### Nómina de Personal")
        search = st.text_input("Buscar funcionario por nombre...")
        if search:
            df_func = df_func[
                df_func["nombre_completo"].str.contains(search, case=False, na=False)
            ]

        display_cols = [
            "nombre_completo",
            "estamento",
            "cargo_funcion",
            "tipo_vinculo",
            "remuneracion_bruta",
        ]
        avail_cols = [c for c in display_cols if c in df_func.columns]
        st.dataframe(
            df_func[avail_cols].head(100), use_container_width=True, hide_index=True
        )


def show_centro_documentacion():
    st.title("📂 Centro de Documentación")
    st.markdown("Repositorio centralizado de documentos, oficios y resoluciones.")

    df_doc = load_data("documents", "doc_documento.csv")
    if df_doc is not None:
        st.metric("Total Documentos", f"{len(df_doc):,}")

        # Filters
        tipo = st.multiselect(
            "Tipo Documento",
            df_doc["origen_hoja"].unique() if "origen_hoja" in df_doc.columns else [],
        )
        search = st.text_input("Buscar en materia o remitente...")

        filtered = df_doc.copy()
        if tipo:
            filtered = filtered[filtered["origen_hoja"].isin(tipo)]
        if search:
            mask = filtered["materia"].str.contains(
                search, case=False, na=False
            ) | filtered["remitente"].str.contains(search, case=False, na=False)
            filtered = filtered[mask]

        st.dataframe(filtered, use_container_width=True, hide_index=True)
    else:
        st.info("No se encontraron documentos normalizados.")


def show_convenios_explorer():
    st.title("📄 Explorador de Convenios")
    st.markdown("Gestión y seguimiento de convenios con entidades ejecutoras.")

    df_conv = load_data("facts", "fact_convenio.csv")
    df_dim_inic = load_data("dimensions", "dim_iniciativa.csv")
    df_dim_inst = load_data("dimensions", "dim_institucion.csv")
    df_eventos = load_data("facts", "fact_evento_documental.csv")
    df_uni = load_data("dimensions", "dim_iniciativa_unificada.csv")

    if df_conv is None:
        st.error("No se encontró fact_convenio.csv")
        return

    # Enrich with iniciativa name
    if df_dim_inic is not None:
        df_conv = df_conv.merge(
            df_dim_inic[["id", "codigo", "nombre_norm"]],
            left_on="iniciativa_id",
            right_on="id",
            how="left",
            suffixes=("", "_inic"),
        )

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Convenios", f"{len(df_conv):,}")
    c2.metric("Monto Total (M$)", f"{df_conv['monto_fndr_ms'].sum():,.0f}")

    firmados = len(df_conv[df_conv["estado_convenio_norm"] == "FIRMADO"])
    c3.metric("Firmados", f"{firmados:,}")

    cgr_ok = len(df_conv[df_conv["estado_cgr_norm"].notna()])
    c4.metric("Con Trámite CGR", f"{cgr_ok:,}")

    st.divider()

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        estado_filter = st.multiselect(
            "Estado Convenio",
            (
                df_conv["estado_convenio_norm"].unique()
                if "estado_convenio_norm" in df_conv.columns
                else []
            ),
        )
    with col2:
        origen_filter = st.multiselect(
            "Origen/Año",
            df_conv["origen_hoja"].unique() if "origen_hoja" in df_conv.columns else [],
        )
    with col3:
        search = st.text_input("Buscar código o nombre iniciativa...")

    filtered = df_conv.copy()
    if estado_filter:
        filtered = filtered[filtered["estado_convenio_norm"].isin(estado_filter)]
    if origen_filter:
        filtered = filtered[filtered["origen_hoja"].isin(origen_filter)]
    if search:
        mask = filtered["codigo"].astype(str).str.contains(
            search, case=False, na=False
        ) | filtered["nombre_norm"].str.contains(search, case=False, na=False)
        filtered = filtered[mask]

    st.info(f"Mostrando {len(filtered):,} de {len(df_conv):,} convenios")

    # Charts
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### Por Estado")
        estado_counts = filtered["estado_convenio_norm"].value_counts()
        fig = px.pie(values=estado_counts.values, names=estado_counts.index, hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("### Monto por Origen")
        if "origen_hoja" in filtered.columns:
            monto_by_origen = (
                filtered.groupby("origen_hoja")["monto_fndr_ms"].sum().reset_index()
            )
            fig2 = px.bar(
                monto_by_origen, x="origen_hoja", y="monto_fndr_ms", color="origen_hoja"
            )
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    # Table with selection
    st.markdown("### 📋 Listado de Convenios")
    if not filtered.empty:
        conv_options = filtered.apply(
            lambda r: f"{r.get('codigo', 'N/A')} - {str(r.get('nombre_norm', ''))[:40]}... ({r.get('estado_convenio_norm', 'N/A')})",
            axis=1,
        ).tolist()

        selected_idx = st.selectbox(
            "Seleccionar convenio para ver detalle:",
            range(len(conv_options)),
            format_func=lambda i: conv_options[i],
        )

        # Preview table
        display_cols = [
            "codigo",
            "nombre_norm",
            "monto_fndr_ms",
            "estado_convenio_norm",
            "fecha_firma_convenio",
        ]
        avail_cols = [c for c in display_cols if c in filtered.columns]
        st.dataframe(
            filtered[avail_cols].head(50), use_container_width=True, hide_index=True
        )

        # Detail Panel
        st.divider()
        st.markdown("## 📄 Detalle del Convenio")

        record = filtered.iloc[selected_idx]

        st.subheader(f"📄 {record.get('nombre_norm', 'Sin Nombre')}")

        # Main attributes
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Código BIP", record.get("codigo", "N/A"))
        col2.metric("Monto (M$)", f"{record.get('monto_fndr_ms', 0):,.0f}")
        col3.metric("Estado", record.get("estado_convenio_norm", "N/A"))
        col4.metric("Firma", str(record.get("fecha_firma_convenio", "N/A"))[:10])

        col5, col6, col7, col8 = st.columns(4)
        col5.metric(
            "Estado CGR",
            (
                record.get("estado_cgr_norm", "N/A")
                if pd.notna(record.get("estado_cgr_norm"))
                else "Pendiente"
            ),
        )
        col6.metric(
            "Referente",
            (
                record.get("referente_tecnico", "N/A")
                if pd.notna(record.get("referente_tecnico"))
                else "N/A"
            ),
        )
        col7.metric("Origen", record.get("origen_hoja", "N/A"))
        col8.metric("Tipo", record.get("tipo_registro", "N/A"))

        # Tabs for related data
        st.markdown("### 🔗 Datos Relacionados")
        tab_ipr, tab_eventos, tab_raw = st.tabs(
            ["🏛️ IPR Vinculada", "📋 Eventos Documentales", "🔧 Raw Data"]
        )

        with tab_ipr:
            # Find unified IPR
            if df_uni is not None and "codigo" in record:
                codigo_conv = record["codigo"]
                ipr_match = df_uni[df_uni["codigo_convenios"] == codigo_conv]
                if not ipr_match.empty:
                    ipr = ipr_match.iloc[0]
                    st.success(f"✅ Vinculado a IPR Unificada")
                    st.write(f"**Nombre:** {ipr.get('nombre_iniciativa', 'N/A')}")
                    st.write(
                        f"**Código Unificado:** {ipr.get('codigo_normalizado', 'N/A')}"
                    )
                    st.write(f"**Tipo IPR:** {ipr.get('tipo_ipr', 'N/A')}")
                    st.write(f"**Mecanismo:** {ipr.get('mecanismo_id', 'N/A')}")

                    # Show other links
                    other_links = []
                    if pd.notna(ipr.get("cod_unico_idis")):
                        other_links.append(f"IDIS: {ipr['cod_unico_idis']}")
                    if pd.notna(ipr.get("codigo_fril")):
                        other_links.append(f"FRIL: {ipr['codigo_fril']}")
                    if other_links:
                        st.info(f"**Otros enlaces:** {', '.join(other_links)}")
                else:
                    st.warning("No se encontró IPR unificada para este convenio")

        with tab_eventos:
            if df_eventos is not None:
                conv_id = record.get("id")
                eventos = df_eventos[df_eventos["convenio_id"] == conv_id]
                if not eventos.empty:
                    st.write(f"**{len(eventos)} Eventos Documentales**")
                    evento_cols = [
                        "numero_documento",
                        "fecha_documento",
                        "columna_fuente",
                        "observacion_raw",
                    ]
                    avail_cols = [c for c in evento_cols if c in eventos.columns]
                    st.dataframe(
                        eventos[avail_cols], use_container_width=True, hide_index=True
                    )
                else:
                    st.info("Sin eventos documentales registrados")

        with tab_raw:
            st.json(record.to_dict())


def show_relationship_graph():
    st.title("🕸️ Grafo de Relaciones IPR")
    st.markdown(
        "Visualización de conexiones entre iniciativas, instituciones y territorios."
    )

    df_uni = load_data("dimensions", "dim_iniciativa_unificada.csv")
    df_matches = load_data("relationships", "cross_domain_matches.csv")

    if df_uni is None:
        st.error("No se encontró dim_iniciativa_unificada.csv")
        return

    # Filters for graph size
    max_nodes = st.slider("Máximo de nodos", 20, 200, 50)

    # Build graph data
    nodes = []
    edges = []
    node_ids = set()

    # Sample IPRs for visualization
    sample = df_uni.head(max_nodes)

    for _, row in sample.iterrows():
        ipr_id = row.get("id", "")
        nombre = str(row.get("nombre_iniciativa", ""))[:40]
        fuente = row.get("fuente_principal", "UNKNOWN")

        if ipr_id and ipr_id not in node_ids:
            nodes.append(
                {"id": ipr_id, "label": nombre, "type": "IPR", "fuente": fuente}
            )
            node_ids.add(ipr_id)

        # Add edges to linked sources
        if pd.notna(row.get("cod_unico_idis")) and pd.notna(
            row.get("codigo_convenios")
        ):
            # This IPR has cross-domain links
            edges.append(
                {
                    "source": ipr_id,
                    "target": f"IDIS_{row['cod_unico_idis']}",
                    "type": "IDIS_LINK",
                }
            )

    if not nodes:
        st.warning("No hay datos para graficar")
        return

    # Create network layout
    import numpy as np

    n = len(nodes)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x_pos = np.cos(angles)
    y_pos = np.sin(angles)

    # Color by fuente
    fuente_colors = {
        "IDIS": "#0f766e",
        "CONVENIOS": "#b45309",
        "FRIL": "#1e40af",
        "PROGS": "#7c3aed",
        "UNKNOWN": "#6b7280",
    }

    node_colors = [fuente_colors.get(n["fuente"], "#6b7280") for n in nodes]
    node_labels = [n["label"] for n in nodes]

    # Create edge traces
    edge_x = []
    edge_y = []
    for edge in edges:
        src_idx = next(
            (i for i, n in enumerate(nodes) if n["id"] == edge["source"]), None
        )
        if src_idx is not None:
            edge_x.extend([x_pos[src_idx], x_pos[src_idx] + 0.1, None])
            edge_y.extend([y_pos[src_idx], y_pos[src_idx] + 0.1, None])

    fig = go.Figure()

    # Add edges
    if edge_x:
        fig.add_trace(
            go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                line=dict(width=0.5, color="#888"),
                hoverinfo="none",
            )
        )

    # Add nodes
    fig.add_trace(
        go.Scatter(
            x=x_pos,
            y=y_pos,
            mode="markers+text",
            marker=dict(size=15, color=node_colors, line=dict(width=1, color="white")),
            text=node_labels,
            textposition="top center",
            textfont=dict(size=8),
            hoverinfo="text",
            hovertext=[f"{n['label']}<br>Fuente: {n['fuente']}" for n in nodes],
        )
    )

    fig.update_layout(
        title=f"Red de {len(nodes)} IPRs",
        showlegend=False,
        hovermode="closest",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Legend
    st.markdown("**Leyenda de Colores:**")
    cols = st.columns(5)
    for i, (fuente, color) in enumerate(fuente_colors.items()):
        with cols[i]:
            st.markdown(
                f"<span style='color:{color}'>●</span> {fuente}", unsafe_allow_html=True
            )

    # Cross-domain stats
    st.divider()
    st.markdown("### 📊 Estadísticas de Conectividad")

    if df_matches is not None:
        match_counts = (
            df_matches["match_type"].value_counts()
            if "match_type" in df_matches.columns
            else pd.Series()
        )
        if not match_counts.empty:
            fig2 = px.bar(
                x=match_counts.index,
                y=match_counts.values,
                labels={"x": "Tipo de Match", "y": "Cantidad"},
                title="Tipos de Matches Cross-Domain",
            )
            st.plotly_chart(fig2, use_container_width=True)


def show_cross_domain():
    st.title("🔗 Explorador Cross-Domain")
    st.markdown("Analiza las conexiones entre diferentes fuentes de datos.")

    df_matches = load_data("relationships", "cross_domain_matches.csv")
    df_uni = load_data("dimensions", "dim_iniciativa_unificada.csv")

    if df_matches is None:
        st.warning("No se encontró cross_domain_matches.csv")
        return

    st.metric("Total Links Cross-Domain", f"{len(df_matches):,}")

    # Domain pair analysis
    if "source_domain" in df_matches.columns and "target_domain" in df_matches.columns:
        st.markdown("### Matriz de Conexiones por Dominio")

        # Create pivot
        pair_counts = (
            df_matches.groupby(["source_domain", "target_domain"])
            .size()
            .reset_index(name="count")
        )
        pivot = pair_counts.pivot(
            index="source_domain", columns="target_domain", values="count"
        ).fillna(0)

        fig = px.imshow(
            pivot,
            text_auto=True,
            color_continuous_scale="Blues",
            title="Conexiones entre Dominios",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Match type distribution
    if "match_type" in df_matches.columns:
        st.markdown("### Por Tipo de Match")
        fig2 = px.pie(
            df_matches, names="match_type", title="Distribución de Tipos de Match"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Sample matches
    st.markdown("### 📋 Muestra de Matches")
    possible_cols = [
        "source_domain",
        "source_code",
        "target_domain",
        "target_code",
        "match_type",
        "confidence",
    ]
    display_cols = [c for c in possible_cols if c in df_matches.columns]
    st.dataframe(
        df_matches[display_cols].head(100), use_container_width=True, hide_index=True
    )


def main():
    st.sidebar.title("🔍 GORE OS")
    st.sidebar.caption("Legacy Data Explorer v6.0")

    page = st.sidebar.radio(
        "Navegación",
        [
            "Dashboard",
            "🏛️ IPR Explorer",
            "📄 Convenios",
            "🕸️ Grafo Relaciones",
            "🔗 Cross-Domain",
            "💸 Gestión Presupuestaria",
            "👥 Recursos Humanos",
            "📂 Centro Documentación",
            "Buscador 360°",
            "Catálogos Omega",
            "Instituciones",
            "Plan 250",
            "Matriz NxN",
            "Explorador de Tablas",
        ],
    )

    st.sidebar.divider()

    # Stats
    counts = load_all_metadata()
    st.sidebar.metric("Total Registros", f"{sum(counts.values()):,}")
    st.sidebar.metric("Tablas Normalizadas", len(counts))

    st.sidebar.divider()
    st.sidebar.info("v6.0 - Convenios + Ecosistema")

    if page == "Dashboard":
        show_dashboard()
    elif page == "🏛️ IPR Explorer":
        show_ipr_explorer()
    elif page == "📄 Convenios":
        show_convenios_explorer()
    elif page == "🕸️ Grafo Relaciones":
        show_relationship_graph()
    elif page == "🔗 Cross-Domain":
        show_cross_domain()
    elif page == "💸 Gestión Presupuestaria":
        show_gestion_presupuestaria()
    elif page == "👥 Recursos Humanos":
        show_recursos_humanos()
    elif page == "📂 Centro Documentación":
        show_centro_documentacion()
    elif page == "Buscador 360°":
        show_buscador_360()
    elif page == "Catálogos Omega":
        show_catalogos_omega()
    elif page == "Instituciones":
        show_instituciones()
    elif page == "Plan 250":
        show_plan_250()
    elif page == "Matriz NxN":
        show_matrix()
    elif page == "Explorador de Tablas":
        show_explorer()


if __name__ == "__main__":
    main()
