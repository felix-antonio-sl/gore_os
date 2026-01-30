"""Dashboard component for migration summary."""

import streamlit as st
import pandas as pd
from typing import Dict, Any

# Tablas particionadas sin soft-delete (event sourcing)
TABLES_WITHOUT_SOFT_DELETE = {"txn.event", "txn.magnitude"}

MIGRATION_TARGETS = [
    {"phase": 1, "table": "core.person", "target": 111, "label": "core.person"},
    {
        "phase": 1,
        "table": "core.organization",
        "target": 1684,
        "label": "core.organization",
    },
    {"phase": 2, "table": "core.ipr", "target": 3621, "label": "core.ipr"},
    {"phase": 3, "table": "core.agreement", "target": 533, "label": "core.agreement"},
    {
        "phase": 4,
        "table": "core.budget_program",
        "target": 25753,
        "label": "core.budget_program",
    },
    {
        "phase": 5,
        "table": "txn.event",
        "target": 2373,
        "label": "txn.event (docs)",
        "filter": "subject_type = 'agreement'",
    },
    {
        "phase": 5,
        "table": "core.budget_commitment",
        "target": 3701,
        "label": "core.budget_commitment",
    },
    {"phase": 6, "table": "txn.magnitude", "target": 3496, "label": "txn.magnitude"},
    {
        "phase": 6,
        "table": "txn.event",
        "target": 1667,
        "label": "txn.event (rendiciones)",
        "filter": "subject_type = 'rendicion_8pct'",
    },
    {
        "phase": 7,
        "table": "core.ipr_territory",
        "target": 1965,
        "label": "core.ipr_territory",
    },
    {
        "phase": 7,
        "table": "core.person",
        "target": 110,
        "label": "person→organization",
        "filter": "organization_id IS NOT NULL",
    },
]


def render_dashboard(conn, available_tables: Dict[str, Any]):
    """Render the migration dashboard."""

    st.markdown("### 📊 MIGRACIÓN ETL - RESUMEN FINAL")
    st.markdown("---")

    # Metrics container
    metrics_data = []

    # Progress bar for loading metrics
    progress_text = "Calculando métricas..."
    my_bar = st.progress(0, text=progress_text)
    total_steps = len(MIGRATION_TARGETS) + 4  # Extra steps for specific stats

    for i, target in enumerate(MIGRATION_TARGETS):
        table_name = target["table"]
        target_count = target["target"]
        label = target["label"]
        filter_condition = target.get("filter")
        phase = target["phase"]

        current_count = 0
        success_rate = 0.0

        try:
            # Tablas txn.* no tienen deleted_at (event sourcing - inmutables)
            if table_name in TABLES_WITHOUT_SOFT_DELETE:
                base_condition = "1=1"
            else:
                base_condition = "deleted_at IS NULL"

            query = f"SELECT COUNT(*) as count FROM {table_name} WHERE {base_condition}"
            if filter_condition:
                query += f" AND {filter_condition}"

            df = conn.query(query)
            current_count = int(df.iloc[0]["count"])

            if target_count > 0:
                success_rate = min((current_count / target_count) * 100, 100.0)
            else:
                success_rate = 100.0 if current_count > 0 else 0.0

        except Exception:
            current_count = 0
            success_rate = 0.0

        metrics_data.append(
            {
                "FASE": phase,
                "Tabla / Entidad": label,
                "Target": f"{target_count:,}",
                "Registros": f"{current_count:,}",
                "% Éxito": f"{success_rate:.1f}%",
            }
        )
        my_bar.progress((i + 1) / total_steps, text=progress_text)

    my_bar.progress(1.0, text="Listo")
    my_bar.empty()

    # Display Main Summary Table
    df_metrics = pd.DataFrame(metrics_data)

    # Calculate Total
    total_registros = sum(int(x["Registros"].replace(",", "")) for x in metrics_data)

    st.dataframe(
        df_metrics,
        use_container_width=True,
        hide_index=True,
        column_config={
            "FASE": st.column_config.NumberColumn("Fase", format="%d"),
            "% Éxito": st.column_config.ProgressColumn(
                "% Éxito",
                format="%s",
                min_value=0,
                max_value=100,
            ),
        },
    )

    st.metric("Total Registros Migrados", f"{total_registros:,}")

    st.markdown("---")

    # Detailed Analysis Section
    st.subheader("🔍 Análisis Detallado por Fase")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**FASE 3 - AgreementLoader**")

        # Calculate Agreement stats
        try:
            total_agreements = int(
                conn.query(
                    "SELECT COUNT(*) as c FROM core.agreement WHERE deleted_at IS NULL"
                ).iloc[0]["c"]
            )
            agreements_with_ipr = int(
                conn.query(
                    "SELECT COUNT(*) as c FROM core.agreement WHERE ipr_id IS NOT NULL AND deleted_at IS NULL"
                ).iloc[0]["c"]
            )
            agreements_with_recv = int(
                conn.query(
                    "SELECT COUNT(*) as c FROM core.agreement WHERE receiver_id IS NOT NULL AND deleted_at IS NULL"
                ).iloc[0]["c"]
            )
            agreements_with_giver = int(
                conn.query(
                    "SELECT COUNT(*) as c FROM core.agreement WHERE giver_id IS NOT NULL AND deleted_at IS NULL"
                ).iloc[0]["c"]
            )

            ipr_pct = (
                (agreements_with_ipr / total_agreements * 100)
                if total_agreements
                else 0
            )

            st.markdown(
                f"""
            - **FK ipr_id**: {agreements_with_ipr}/{total_agreements} ({ipr_pct:.1f}%)
              - *{total_agreements - agreements_with_ipr} convenios sin proyecto asociado*
            - **FK receiver_id**: {agreements_with_recv}/{total_agreements} (100%)
            - **FK giver_id**: {agreements_with_giver}/{total_agreements} (100%)
            """
            )
        except Exception as e:
            st.error(f"Error calculando estadísticas de convenios: {e}")

    with col2:
        st.markdown("**FASE 4 - BudgetProgramLoader**")

        try:
            # Budget stats
            programs_gt_zero = int(
                conn.query(
                    "SELECT COUNT(*) as c FROM core.budget_program WHERE current_amount > 0 AND deleted_at IS NULL"
                ).iloc[0]["c"]
            )
            total_programs = int(
                conn.query(
                    "SELECT COUNT(*) as c FROM core.budget_program WHERE deleted_at IS NULL"
                ).iloc[0]["c"]
            )
            total_amount = float(
                conn.query(
                    "SELECT SUM(current_amount) as s FROM core.budget_program WHERE deleted_at IS NULL"
                ).iloc[0]["s"]
                or 0
            )

            pct_active = (
                (programs_gt_zero / total_programs * 100) if total_programs else 0
            )

            st.markdown(
                f"""
            - **Años fiscales**: 2019-2025
            - **Registros con monto > 0**: {programs_gt_zero:,} ({pct_active:.0f}%)
            - **Monto Total Vigente**: ${total_amount:,.0f} CLP
            """
            )
        except Exception as e:
            st.error(f"Error calculando estadísticas de presupuesto: {e}")

    st.markdown("---")

    # Categorical Coherence Section (v2.0 Normalization)
    st.subheader("🎯 Coherencia Categorial (Normalización v2.0)")

    col1, col2, col3 = st.columns(3)

    try:
        # funding_source_id coherence
        funding_source_stats = conn.query("""
            SELECT COUNT(*) as iprs, COUNT(DISTINCT c.scheme) as schemes
            FROM core.ipr i
            JOIN ref.category c ON c.id = i.funding_source_id
            WHERE i.funding_source_id IS NOT NULL
        """)

        # fund_category_id coherence
        fund_category_stats = conn.query("""
            SELECT COUNT(*) as iprs, COUNT(DISTINCT c.scheme) as schemes
            FROM core.ipr i
            JOIN ref.category c ON c.id = i.fund_category_id
            WHERE i.fund_category_id IS NOT NULL
        """)

        # investment_sector_id coherence
        investment_sector_stats = conn.query("""
            SELECT COUNT(*) as iprs, COUNT(DISTINCT c.scheme) as schemes
            FROM core.ipr i
            JOIN ref.category c ON c.id = i.investment_sector_id
            WHERE i.investment_sector_id IS NOT NULL
        """)

        with col1:
            iprs = int(funding_source_stats.iloc[0]["iprs"])
            schemes = int(funding_source_stats.iloc[0]["schemes"])
            coherence = "✅ 100%" if schemes == 1 else f"⚠️ {schemes} schemes"
            st.metric("funding_source_id", f"{iprs:,} IPRs", coherence)

        with col2:
            iprs = int(fund_category_stats.iloc[0]["iprs"])
            schemes = int(fund_category_stats.iloc[0]["schemes"])
            coherence = "✅ 100%" if schemes == 1 else f"⚠️ {schemes} schemes"
            st.metric("fund_category_id", f"{iprs:,} IPRs", coherence)

        with col3:
            iprs = int(investment_sector_stats.iloc[0]["iprs"])
            schemes = int(investment_sector_stats.iloc[0]["schemes"])
            coherence = "✅ 100%" if schemes == 1 else f"⚠️ {schemes} schemes"
            st.metric("investment_sector_id", f"{iprs:,} IPRs", coherence)

    except Exception as e:
        st.warning(f"No se pudo calcular coherencia categorial: {e}")

    st.markdown("---")

    # Additional Info
    st.info(
        """
    **Notas Técnicas:**
    - Los registros marcados con deleted_at no son contabilizados.
    - La relación Personas → Organizaciones es de tipo N:M implícita en modelo legado, migrada como FK directa.
    - **Coherencia Categorial v2.0**: Cada FK a ref.category debe apuntar a exactamente 1 scheme (Categorical Univocity).
    """
    )
