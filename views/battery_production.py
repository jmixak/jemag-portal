import streamlit as st
import pandas as pd
from db import get_db_connection

def render_battery_production():
    st.header("🔋 Battery Production Log")

    tab1, tab2 = st.tabs(["📝 Log New Pack", "📦 Production Records"])

    with tab1:
        st.subheader("Record New Battery Assembly")
        with st.form("battery_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                client_name = st.text_input("Client / Customer Name *")
                bms_model = st.text_input("BMS Model *", placeholder="e.g., JBD, Seplos, Daly")
                capacity_ah = st.number_input("Cell Capacity (Ah) *", min_value=10, value=120, step=10)
            with col2:
                voltage = st.number_input("Nominal Voltage (V) *", value=51.2, step=0.1)
                est_kwh = (capacity_ah * voltage) / 1000.0
                st.metric("Estimated Capacity", f"{est_kwh:.2f} kWh")
                notes = st.text_area("Assembly Notes & Testing Logs")

            submit_pack = st.form_submit_button("💾 Save Battery Record")

            if submit_pack:
                if not client_name or not bms_model:
                    st.error("Please fill in required fields (Client Name & BMS Model).")
                else:
                    conn = get_db_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            query = """INSERT INTO BatteryProduction 
                                       (ClientName, BMSModel, CellCapacityAh, NominalVoltage, Estimated_kWh, Notes) 
                                       VALUES (%s, %s, %s, %s, %s, %s)"""
                            cursor.execute(query, (client_name, bms_model, capacity_ah, voltage, est_kwh, notes))
                            conn.commit()
                            cursor.close()
                            conn.close()
                            st.success(f"✅ Battery pack logged successfully for {client_name}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving battery pack: {e}")

    with tab2:
        st.subheader("📦 All Battery Production Logs")
        conn = get_db_connection()
        if conn:
            try:
                df_batt = pd.read_sql("SELECT * FROM BatteryProduction ORDER BY ProductionID DESC", conn)
                conn.close()
                if not df_batt.empty:
                    st.dataframe(df_batt, use_container_width=True)
                else:
                    st.info("No battery production records found in database.")
            except Exception as e:
                st.error(f"Error loading battery logs: {e}")