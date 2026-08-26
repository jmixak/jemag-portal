import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import datetime
import os
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Jemag Portal",
    page_icon="⚡",
    layout="wide"
)

# --- DATABASE CONNECTION HELPER ---
def get_db_connection():
    """Establishes connection to MySQL database using Streamlit secrets."""
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
    except Exception as e:
        st.error(f"❌ Database Connection Error: {e}")
        return None

# --- BACKGROUND IMAGE & CUSTOM CSS ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

bg_style = ""
if os.path.exists("jemag logo back.png"):
    bin_str = get_base64_of_bin_file("jemag logo back.png")
    bg_style = f"""
    .stApp {{
        background-image: linear-gradient(rgba(248, 249, 250, 0.92), rgba(248, 249, 250, 0.92)), url("data:image/png;base64,{bin_str}");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }}
    """
else:
    bg_style = ".stApp { background-color: #f8f9fa; }"

st.markdown(f"""
<style>
{bg_style}

/* Global Typography & Headers */
h1, h2, h3 {{
    color: #0F4C81 !important;
    font-weight: 700 !important;
}}

div.block-container {{
    padding-top: 1.5rem;
}}

/* Sidebar Custom Styling */
[data-testid="stSidebar"] {{
    background-color: #ffffff !important;
    border-right: 1px solid #e0e0e0;
}}

[data-testid="stSidebar"] .stRadio label {{
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    padding: 8px 10px !important;
    border-radius: 6px;
    margin-bottom: 2px;
}}

/* Buttons & Form Elements */
.stButton > button {{
    border-radius: 8px;
    font-weight: 600;
    height: 2.8rem;
    font-size: 1rem;
    background-color: #0F4C81;
    color: white;
}}
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
col_logo, col_title = st.columns([1, 6])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=100)
with col_title:
    st.title("JEMAG Solar & Battery Operations Portal")

st.divider()

# --- SIDEBAR AUTHENTICATION & NAVIGATION ---
if "role" not in st.session_state:
    st.session_state.role = "staff"

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.title("Navigation Menu")

    # PIN Authentication Box
    st.subheader("🔑 Access Control")
    admin_pin = st.secrets.get("admin_pin", "1234")
    entered_pin = st.text_input("Enter Admin PIN", type="password", help="Default PIN: 1234")
    
    if entered_pin == str(admin_pin):
        st.session_state.role = "admin"
        st.success("🔓 Admin Access Unlocked")
    else:
        st.session_state.role = "staff"
        if entered_pin:
            st.error("Incorrect PIN")
        else:
            st.info("🔒 Staff Mode (Read/Log Only)")

    st.divider()

# Role-Based Navigation Options
if st.session_state.role == "admin":
    menu_options = [
        "🔋 Battery Production Log",
        "🏢 View Master Directory",  
        "👨‍🎓 Student Evaluation",
        "📝 Register New Profile",
        "🧳 Travel Log",
        "📈 Analytics & Insights"
    ]
else:
    menu_options = [
        "🔋 Battery Production Log",
        "🧳 Travel Log"
    ]

choice = st.sidebar.radio("Select Portal View", menu_options)

# --- VIEW FUNCTIONS ---

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


def render_master_directory():
    st.header("📋 Staff & IT Student Directory")
    conn = get_db_connection()
    if conn:
        try:
            query = "SELECT * FROM View_JemagDirectory"
            df = pd.read_sql(query, conn)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("The database directory is currently empty.")
        except Exception as e:
            st.error(f"Error fetching directory: {e}")
        finally:
            conn.close()


def render_student_evaluation():
    st.header("📝 Submit Trainee Evaluation")
    student_id = st.number_input("Enter Student ID", min_value=1, step=1)
    eval_type = st.selectbox("Evaluation Type", ["Mid-Term Review", "Final Defense", "Logbook Check"])
    score = st.slider("Performance Score (0 - 100)", 0, 100, 80)
    comments = st.text_area("Supervisor Comments & Technical Feedback")
    
    if st.button("Submit Evaluation"):
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.callproc("sp_LogStudentEvaluation", [student_id, eval_type, score, comments])
                conn.commit()
                cursor.close()
                st.success(f"Successfully logged {eval_type} for Student ID {student_id}!")
            except Exception as e:
                st.error(f"Failed to submit evaluation: {e}")
            finally:
                conn.close()


def render_register_profile():
    st.header("👤 Add New Staff or Student Profile")
    
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name *")
        last_name = st.text_input("Last Name *")
        email = st.text_input("Email Address *")
    with col2:
        regular_phone = st.text_input("Regular Phone Number")
        whatsapp_phone = st.text_input("WhatsApp Number")
        role_type = st.selectbox("Role Type *", ["Staff", "IT Student"])

    st.divider()

    if role_type == "Staff":
        st.subheader("💼 Staff Information")
        staff_role = st.text_input("Staff Role / Job Title", placeholder="e.g., Senior Technician, QC Lead")
        school, focus_area, supervisor = None, None, None
    else:
        st.subheader("🎓 IT Student Information")
        col3, col4 = st.columns(2)
        with col3:
            school = st.text_input("School / Institution", placeholder="e.g., UNIJOS, PLAPOLY")
            focus_area = st.text_input("Focus Area / Department", placeholder="e.g., Electrical Installation")
        with col4:
            supervisor = st.text_input("Assigned Supervisor", placeholder="e.g., Engr. Joshua")
        staff_role = None

    st.divider()

    if st.button("💾 Save Profile"):
        if first_name and last_name and email:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    query_people = """INSERT INTO People (FirstName, LastName, Email, RegularPhone, WhatsappPhone, RoleType) 
                                       VALUES (%s, %s, %s, %s, %s, %s)"""
                    cursor.execute(query_people, (first_name, last_name, email, regular_phone, whatsapp_phone, role_type))
                    person_id = cursor.lastrowid

                    if role_type == "Staff":
                        query_staff = "INSERT INTO Staff (PersonID, Role) VALUES (%s, %s)"
                        cursor.execute(query_staff, (person_id, staff_role))
                    elif role_type == "IT Student":
                        query_student = "INSERT INTO ITStudents (PersonID, School, FocusArea, AssignedSupervisor) VALUES (%s, %s, %s, %s)"
                        cursor.execute(query_student, (person_id, school, focus_area, supervisor))

                    conn.commit()
                    cursor.close()
                    st.success(f"✅ Profile created successfully for {first_name} {last_name}! (ID: {person_id})")
                except Exception as e:
                    st.error(f"❌ Error saving profile: {e}")
                finally:
                    conn.close()
        else:
            st.warning("⚠️ Please fill out required fields (First Name, Last Name, Email).")


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

    # KPI CARDS
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("🔋 Total Packs Built", f"{len(df)} Units")
    with k2: st.metric("⚡ Total Storage Deployed", f"{df['Estimated_kWh'].sum():.1f} kWh")
    with k3:
        clean_models = df['BMSModel'].dropna().astype(str).str.strip()
        top_model = clean_models.mode()[0] if not clean_models.empty else "N/A"
        st.metric("⚙️ Top BMS Model", top_model)
    with k4: st.metric("📦 Main Pack Size", f"{df['CellCapacityAh'].mode()[0] if not df['CellCapacityAh'].empty else 120} Ah")

    st.divider()

    # BMS & CAPACITY DISTRIBUTION
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

    # CLIENT DISTRIBUTION
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


# --- ROUTER EXECUTION ---
if choice == "🔋 Battery Production Log":
    render_battery_production()
elif choice == "🏢 View Master Directory":
    render_master_directory()
elif choice == "👨‍🎓 Student Evaluation":
    render_student_evaluation()
elif choice == "📝 Register New Profile":
    render_register_profile()
elif choice == "🧳 Travel Log":
    render_travel_log()
elif choice == "📈 Analytics & Insights":
    render_analytics()