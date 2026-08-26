import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_db_connection

def render_analytics():
    st.header("📈 Production & Client Analytics")
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql("SELECT * FROM BatteryProduction", conn)
            conn.close()
        except Exception:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    if df.empty:
        st.info("No battery production data available for analysis.")
        return

    # --- KPI CARDS ---
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("🔋 Total Packs Built", f"{len(df)} Units")
    with k2: st.metric("⚡ Total Storage Deployed", f"{df['Estimated_kWh'].sum():.1f} kWh")
    with k3:
        clean_models = df['BMSModel'].dropna().astype(str).str.strip()
        top_model = clean_models.mode()[0] if not clean_models.empty else "N/A"
        st.metric("⚙️ Top BMS Model", top_model)
    with k4: st.metric("📦 Main Pack Size", f"{df['CellCapacityAh'].mode()[0] if not df['CellCapacityAh'].empty else 120} Ah")

    st.divider()

    # --- ROW 2: BMS MODELS & CAPACITY ---
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("### ⚙️ BMS Model Distribution")
        df_bms = df.copy()
        df_bms['BMSModel'] = df_bms['BMSModel'].fillna('Unspecified').astype(str).str.strip()
        bms_counts = df_bms['BMSModel'].value_counts().reset_index()
        bms_counts.columns = ['BMS Model', 'Units Installed']

        fig_bms = px.bar(bms_counts, x='BMS Model', y='Units Installed', color='BMS Model', text='Units Installed', color_discrete_sequence=px.colors.qualitative.Set2)
        fig_bms.update_traces(textposition='outside')
        fig_bms.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_bms, use_container_width=True)

    with col4:
        st.markdown("### 🔋 Capacity Distribution (Ah)")
        cap_counts = df['CellCapacityAh'].value_counts().reset_index()
        cap_counts.columns = ['Capacity (Ah)', 'Count']
        fig_cap = px.pie(cap_counts, values='Count', names='Capacity (Ah)', hole=0.4)
        fig_cap.update_layout(height=350)
        st.plotly_chart(fig_cap, use_container_width=True)

    st.divider()

    # --- ROW 3: CLIENT DISTRIBUTION ---
    st.markdown("### 👥 Top Clients & Order Volume")
    df_client = df.copy()
    df_client['ClientName'] = df_client['ClientName'].fillna('').astype(str).str.strip()
    df_client = df_client[~df_client['ClientName'].isin(['nan', '', 'None'])]

    col_c1, col_c2 = st.columns([3, 1])
    with col_c2:
        top_n = st.number_input("Clients to display", min_value=5, max_value=50, value=15, step=5)

    client_counts = df_client['ClientName'].value_counts().head(top_n).reset_index()
    client_counts.columns = ['Client Name', 'Packs Delivered']

    fig_client = px.bar(client_counts, x='Packs Delivered', y='Client Name', orientation='h', text='Packs Delivered', color_discrete_sequence=['#0F4C81'])
    fig_client.update_traces(textposition='outside')
    dynamic_height = max(300, len(client_counts) * 28)
    fig_client.update_layout(yaxis=dict(autorange="reversed"), height=dynamic_height)
    st.plotly_chart(fig_client, use_container_width=True)