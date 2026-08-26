import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from db import get_db_connection

def render_travel_log():
    st.header("🧳 Staff Travel & Field Dispatch Tracker")

    tab_log, tab_map, tab_analytics = st.tabs([
        "📝 Log New Travel", 
        "🗺️ Live Travel Map & Records", 
        "📊 Travel Analytics"
    ])

    with tab_log:
        st.subheader("📝 Record Staff Travel / Field Dispatch")
        
        staff_names = []
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT CONCAT(FirstName, ' ', LastName) FROM People ORDER BY FirstName ASC")
                staff_names = [row[0] for row in cursor.fetchall()]
                cursor.close()
                conn.close()
            except Exception:
                staff_names = []

        with st.form("travel_log_form", clear_on_submit=True):
            tc1, tc2 = st.columns(2)
            with tc1:
                staff_name = st.selectbox("Staff / Student Name *", staff_names) if staff_names else st.text_input("Staff Name *")
                state = st.selectbox("Destination State *", [
                    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno", 
                    "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "FCT - Abuja", "Gombe", 
                    "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", 
                    "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", 
                    "Taraba", "Yobe", "Zamfara"
                ])
                destination_city = st.text_input("City / Town *")
                specific_location = st.text_area("Specific Destination / Client Site")

            with tc2:
                dep_date = st.date_input("Departure Date *", datetime.date.today())
                ret_date = st.date_input("Expected Return Date *", datetime.date.today() + datetime.timedelta(days=3))
                purpose = st.selectbox("Purpose of Travel *", [
                    "Solar & Battery Installation", "Routine Site Maintenance", 
                    "Emergency Repair / Troubleshooting", "Site Audit & Inspection", 
                    "Client Consultation / Meeting", "Equipment Delivery", "Training / Defense"
                ])
                travel_status = st.selectbox("Current Status", ["On Trip", "Returned", "Delayed"])

            g1, g2 = st.columns(2)
            with g1:
                lat = st.number_input("Latitude", format="%.6f", value=9.8965)
            with g2:
                lon = st.number_input("Longitude", format="%.6f", value=8.8583)

            submit_travel = st.form_submit_button("💾 Save Travel Log")

            if submit_travel:
                if not staff_name or not destination_city:
                    st.error("Please fill in required fields (Staff Name & City).")
                else:
                    conn = get_db_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            query = """
                                INSERT INTO TravelLogs 
                                (StaffName, State, DestinationCity, SpecificLocation, DepartureDate, 
                                 ExpectedReturnDate, Purpose, TravelStatus, Latitude, Longitude)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(query, (staff_name, state, destination_city, specific_location, dep_date, ret_date, purpose, travel_status, lat, lon))
                            conn.commit()
                            cursor.close()
                            conn.close()
                            st.success(f"✅ Travel log saved for {staff_name}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving travel log: {e}")

    with tab_map:
        st.subheader("🗺️ Live Travel Dispatches & History")
        conn = get_db_connection()
        if conn:
            try:
                df_travel = pd.read_sql("SELECT * FROM TravelLogs ORDER BY LogDate DESC", conn)
                conn.close()
            except Exception:
                df_travel = pd.DataFrame()
        else:
            df_travel = pd.DataFrame()

        if not df_travel.empty:
            map_data = df_travel.dropna(subset=['Latitude', 'Longitude']).copy()
            map_data['Latitude'] = pd.to_numeric(map_data['Latitude'], errors='coerce')
            map_data['Longitude'] = pd.to_numeric(map_data['Longitude'], errors='coerce')
            map_data = map_data.dropna(subset=['Latitude', 'Longitude'])

            if not map_data.empty:
                status_emoji = {"On Trip": "🚨", "Returned": "✅", "Delayed": "⚠️"}
                map_data['PinEmoji'] = map_data['TravelStatus'].map(status_emoji).fillna("📍")

                fig_travel_map = px.scatter_mapbox(
                    map_data, lat="Latitude", lon="Longitude", text="PinEmoji",
                    hover_name="StaffName", hover_data={"State": True, "DestinationCity": True, "Purpose": True, "TravelStatus": True},
                    zoom=6.0, center={"lat": 9.0820, "lon": 8.6753}
                )
                fig_travel_map.update_traces(mode="text", textfont=dict(size=26))
                fig_travel_map.update_layout(
                    mapbox_style="white-bg",
                    mapbox_layers=[{"below": "traces", "sourcetype": "raster", "source": ["https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"]}],
                    mapbox_pitch=45, mapbox_bearing=10, margin={"r":0, "t":0, "l":0, "b":0}, height=500
                )
                st.plotly_chart(fig_travel_map, use_container_width=True)

            st.divider()
            st.dataframe(df_travel, use_container_width=True)
        else:
            st.info("No travel records logged yet.")

    with tab_analytics:
        st.subheader("📊 Dispatch Frequency Analytics")
        conn = get_db_connection()
        df_analytics = pd.read_sql("SELECT * FROM TravelLogs", conn) if conn else pd.DataFrame()
        if conn: conn.close()

        if not df_analytics.empty:
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                st.markdown("### 👤 Trips Per Person")
                person_counts = df_analytics['StaffName'].str.strip().value_counts().reset_index()
                person_counts.columns = ['Staff Name', 'Total Trips']
                fig_person = px.bar(person_counts, x='Total Trips', y='Staff Name', orientation='h', text='Total Trips', color_discrete_sequence=['#0F4C81'])
                fig_person.update_traces(textposition='outside')
                fig_person.update_layout(yaxis=dict(autorange="reversed"), height=350)
                st.plotly_chart(fig_person, use_container_width=True)

            with col_a2:
                st.markdown("### 📍 Visits Per State")
                loc_counts = df_analytics['State'].str.strip().value_counts().reset_index()
                loc_counts.columns = ['State', 'Visits']
                fig_loc = px.bar(loc_counts, x='State', y='Visits', text='Visits', color='State', color_discrete_sequence=px.colors.qualitative.Set2)
                fig_loc.update_traces(textposition='outside')
                fig_loc.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig_loc, use_container_width=True)