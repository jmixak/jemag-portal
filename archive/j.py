import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import mysql.connector
import pandas as pd
import datetime

# 1. Page configuration (Must be the very first Streamlit command)
st.set_page_config(page_title="Jemag Portal", layout="wide")

import base64
import os

# --- 1. DYNAMIC BACKGROUND IMAGE (BLURRED) ---
def set_blurred_background(image_base_name):
    # Finds the image whether Windows hid .png or .jpg
    image_path = None
    for ext in ["", ".jpg", ".png", ".jpeg", ".JPG", ".PNG"]:
        test_path = image_base_name + ext
        if os.path.exists(test_path):
            image_path = test_path
            break
            
    if image_path:
        with open(image_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
            
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = "image/png" if ext == ".png" else "image/jpeg"

        css_code = f"""
        <style>
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-image: url("data:{mime_type};base64,{encoded_string}");
            background-size: cover;      /* Covers the whole screen */
            background-repeat: no-repeat;
            background-position: center;
            filter: blur(10px);          /* Glass blur effect */
            opacity: 0.12;               /* Keeps it subtle and sharp for text reading */
            z-index: 0;
            pointer-events: none;
        }}
        </style>
        """
        st.markdown(css_code, unsafe_allow_html=True)

# Apply the background blur graphic
set_blurred_background("jemag logo back")


# --- 2. SIDEBAR LOGO DISPLAY ---
def get_sidebar_logo_path(image_base_name):
    for ext in ["", ".png", ".jpg", ".jpeg", ".PNG", ".JPG"]:
        test_path = image_base_name + ext
        if os.path.exists(test_path):
            return test_path
    return None

logo_path = get_sidebar_logo_path("logo")
# --- AFTER ---
if logo_path:
    st.sidebar.image(logo_path, width=120)

# 2. Custom CSS for larger text AND vertical spacing
st.markdown("""
    <style>
    /* Increases the font size of the radio button options */
    [data-testid="stSidebar"] .stRadio p {
        font-size: 22px !important;
    }
    /* Increases the font size of the "Go to" label */
    [data-testid="stSidebar"] .stRadio label {
        font-size: 24px !important;
        font-weight: bold !important;
    }
    /* Adds vertical space between the options */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 20px !important; 
    }
    </style>
""", unsafe_allow_html=True)

# 3. Initialize Session State for Login Authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# 4. The Login Screen (Blocks access to the rest of the app)
if not st.session_state.logged_in:
    st.title("🔒 Jemag Renewable Energy - Staff Portal")
    st.write("Please enter your assigned passkey to access the system.")
    
    # Input field that hides the text as dots
    passkey = st.text_input("Enter Passkey", type="password")
    
    if st.button("Login"):
        # 👉 IMPORTANT: Change these passwords to whatever you want!
        if passkey == "5464": 
            st.session_state.logged_in = True
            st.session_state.role = "admin"
            st.rerun()  # Refreshes the page to log them in
        elif passkey == "1234": 
            st.session_state.logged_in = True
            st.session_state.role = "staff"
            st.rerun()
        else:
            st.error("❌ Invalid passkey. Please try again.")
            
    # Stop the code here so the rest of the app doesn't load without a login
    st.stop()

# ---------------------------------------------------------
# EVERYTHING BELOW THIS LINE ONLY RUNS IF LOGGED IN
# ---------------------------------------------------------

# Database connection function
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
    except Exception as e:
        st.error(f"❌ Could not connect to database: {e}")
        return None
# --- MAIN HEADER & LOGO (Side-by-side) ---
logo_path = get_sidebar_logo_path("logo")

# Create two columns (1 part for logo, 5 parts for title) vertically centered
col_logo, col_title = st.columns([1, 5], vertical_alignment="center")

with col_logo:
    if logo_path:
        st.image(logo_path, width=130)  # Sized down slightly so it fits neatly beside text
if st.session_state.role == "admin":
    with col_title:
        st.title("Jemag Renewable Energy - Management Portal")
else:
    with col_title:
      st.title("Jemag Renewable Energy - Production Portal")  
# Sidebar navigation logic based on Role
st.sidebar.title("Navigation Menu")

if st.session_state.role == "admin":
    # Admin sees everything including Analytics
    menu_options = [
        "🏢 View Master Directory",  
        "🔋 Battery Production",
        "📈 Analytics & Insights",
        "👨‍🎓 Student Evaluation",
        "📍 Field Service & Map",
        "📝 Register New Profile"   # <--- NEW TAB
    ]
else:
    # Staff ONLY sees the battery production option
    menu_options = ["🔋 Battery Production"]
    
choice = st.sidebar.radio("Go to", menu_options)

# Add a clean Logout button at the bottom of the sidebar
st.sidebar.divider()
if st.sidebar.button("🚪 Log Out"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.rerun()

st.divider()

# --- TAB 1: VIEW MASTER DIRECTORY (ADMIN ONLY) ---
if choice == "🏢 View Master Directory":
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

# --- TAB 2: LOG STUDENT EVALUATION (ADMIN ONLY) ---
elif choice == "👨‍🎓 Student Evaluation":
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

# --- TAB 3: REGISTER NEW PROFILE (ADMIN ONLY) ---
elif choice == "📝 Register New Profile":
    st.header("👤 Add New Staff or Student Profile")
    
    # 1. Base Information
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

    # 2. Dynamic Inputs based on selected Role
    if role_type == "Staff":
        st.subheader("💼 Staff Information")
        staff_role = st.text_input("Staff Role / Job Title", placeholder="e.g., Senior Technician, QC Lead, Administrator")
        school, focus_area, supervisor = None, None, None
    else:
        st.subheader("🎓 IT Student Information")
        col3, col4 = st.columns(2)
        with col3:
            school = st.text_input("School / Institution", placeholder="e.g., UNIJOS, PLAPOLY")
            focus_area = st.text_input("Focus Area / Department", placeholder="e.g., Electrical Installation, Software Tech")
        with col4:
            supervisor = st.text_input("Assigned Supervisor", placeholder="e.g., Engr. Joshua")
        staff_role = None

    st.divider()

    # 3. Save Button Logic
    if st.button("💾 Save Profile"):
        if first_name and last_name and email:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    
                    # Insert into primary People table
                    query_people = """INSERT INTO People (FirstName, LastName, Email, RegularPhone, WhatsappPhone, RoleType) 
                                       VALUES (%s, %s, %s, %s, %s, %s)"""
                    cursor.execute(query_people, (first_name, last_name, email, regular_phone, whatsapp_phone, role_type))
                    person_id = cursor.lastrowid

                    # Insert role-specific data into child tables
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
            st.warning("⚠️ Please fill out all required fields marked with * (First Name, Last Name, Email).")
        
    elif choice == "📍 Field Service & Map":
         st.subheader("📍 Field Service, Installations & Maintenance Hub")
         st.markdown("Track solar/battery installations across Nigeria, drop interactive GPS pins, and record maintenance service tickets.")
         tab_map, tab_new_install, tab_maintenance = st.tabs([
             "🗺️ Live Site Map & Directory", 
             "⚡ Register New Installation", 
             "🔧 Record Maintenance Visit"
         ])

    # -------------------------------------------------------------------------
    # TAB 1: LIVE MAP & SITE DIRECTORY
    # -------------------------------------------------------------------------
    with tab_map:
        st.markdown("### 🗺️ Live Interactive Installation Map")
        conn = get_db_connection()
        if conn:
            try:
                df_inst = pd.read_sql("SELECT * FROM Installations", conn)
                df_maint = pd.read_sql("SELECT * FROM MaintenanceLogs ORDER BY VisitDate DESC", conn)
                conn.close()
            except Exception as e:
                st.error(f"Error reading records: {e}")
                df_inst, df_maint = pd.DataFrame(), pd.DataFrame()
        else:
            df_inst, df_maint = pd.DataFrame(), pd.DataFrame()

        if not df_inst.empty:
            # Prepare map data (filter out missing Lat/Lon)
            map_data = df_inst.dropna(subset=['Latitude', 'Longitude']).copy()
            map_data['Latitude'] = pd.to_numeric(map_data['Latitude'], errors='coerce')
            map_data['Longitude'] = pd.to_numeric(map_data['Longitude'], errors='coerce')
            map_data = map_data.dropna(subset=['Latitude', 'Longitude'])

            if not map_data.empty:
                # Color map based on site status
                color_map = {
                    "Operational": "#00C853",        # Green
                    "Maintenance Required": "#FFB300", # Yellow
                    "System Down": "#D32F2F"          # Red
                }

                fig_map = px.scatter_mapbox(
                    map_data,
                    lat="Latitude",
                    lon="Longitude",
                    hover_name="ClientName",
                    hover_data={
                        "CityTown": True,
                        "SystemCapacityKW": True,
                        "BatteryCapacityKWh": True,
                        "InverterBrandModel": True,
                        "CurrentStatus": True,
                        "Latitude": False,
                        "Longitude": False
                    },
                    color="CurrentStatus",
                    color_discrete_map=color_map,
                    zoom=5,
                    center={"lat": 9.0820, "lon": 8.6753}, # Centered on Nigeria
                    size_max=15
                )
                fig_map.update_layout(
                    mapbox_style="open-street-map",
                    margin={"r":0, "t":0, "l":0, "b":0},
                    height=450
                )
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("No installations have valid GPS Latitude/Longitude values yet. Add coordinates to view pins!")

            st.divider()

            # Display Data Tables
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown("### 📋 Installed Sites Directory")
                st.dataframe(df_inst, use_container_width=True)
            with col_t2:
                st.markdown("### 🛠️ Maintenance History Logs")
                st.dataframe(df_maint, use_container_width=True)
        else:
            st.info("No installation sites recorded yet. Click on 'Register New Installation' to add your first site!")

    # -------------------------------------------------------------------------
    # TAB 2: REGISTER NEW INSTALLATION
    # -------------------------------------------------------------------------
    with tab_new_install:
        st.markdown("### ⚡ Register Installed System & Set Map Pin")
        with st.form("new_installation_form"):
            c1, c2 = st.columns(2)
            with c1:
                client_name = st.text_input("Client Name *")
                phone_no = st.text_input("Phone Number")
                city_town = st.text_input("City / Town *")
                full_address = st.text_area("Full Site Address")
                installer_name = st.text_input("Lead Installer Name")

            with c2:
                sys_kw = st.number_input("System Capacity (kW)", min_value=0.0, step=0.5, value=5.0)
                batt_kwh = st.number_input("Battery Capacity (kWh)", min_value=0.0, step=0.5, value=10.0)
                inverter_model = st.text_input("Inverter Brand / Model", value="Felicity 5kVA")
                batt_sn = st.text_input("Battery Serial Number (Optional)")
                install_date = st.date_input("Installation Date", value=datetime.date.today())
                current_status = st.selectbox("Current System Status", ["Operational", "Maintenance Required", "System Down"])

            st.markdown("#### 📍 Map Pin & GPS Coordinates")
            cg1, cg2, cg3 = st.columns(3)
            with cg1:
                lat = st.number_input("Latitude (e.g. 9.8965)", format="%.6f", value=9.8965)
            with cg2:
                lon = st.number_input("Longitude (e.g. 8.8583)", format="%.6f", value=8.8583)
            with cg3:
                gmaps_link = st.text_input("Google Maps Location Link")

            submit_install = st.form_submit_button("💾 Save Installation & Drop Pin")

            if submit_install:
                if not client_name or not city_town:
                    st.error("Please fill in the required fields (Client Name & City/Town).")
                else:
                    conn = get_db_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            query = """
                                INSERT INTO Installations 
                                (ClientName, PhoneNumber, CityTown, FullAddress, Latitude, Longitude, 
                                 GoogleMapsLink, SystemCapacityKW, BatteryCapacityKWh, InverterBrandModel, 
                                 BatterySerialNumber, InstallerName, InstallationDate, CurrentStatus)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """
                            cursor.execute(query, (
                                client_name, phone_no, city_town, full_address, lat, lon,
                                gmaps_link, sys_kw, batt_kwh, inverter_model,
                                batt_sn, installer_name, install_date, current_status
                            ))
                            conn.commit()
                            cursor.close()
                            conn.close()
                            st.success(f"✅ Installation for '{client_name}' registered successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving installation: {e}")

    # -------------------------------------------------------------------------
    # TAB 3: RECORD MAINTENANCE VISIT
    # -------------------------------------------------------------------------
    with tab_maintenance:
        st.markdown("### 🔧 Record Service / Maintenance Visit")
        
        conn = get_db_connection()
        inst_options = {}
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT InstallationID, ClientName, CityTown, BatterySerialNumber, SystemCapacityKW, BatteryCapacityKWh, InverterBrandModel, PhoneNumber, FullAddress, GoogleMapsLink FROM Installations")
                sites = cursor.fetchall()
                cursor.close()
                conn.close()
                for s in sites:
                    label = f"{s['ClientName']} ({s['CityTown']}) - SN: {s['BatterySerialNumber'] or 'N/A'}"
                    inst_options[label] = s
            except Exception as e:
                st.error(f"Error fetching sites: {e}")

        if not inst_options:
            st.warning("No installation sites found. Please register an installation first.")
        else:
            selected_site_label = st.selectbox("Select Installation Site *", list(inst_options.keys()))
            site = inst_options[selected_site_label]

            with st.form("maintenance_form"):
                mc1, mc2 = st.columns(2)
                with mc1:
                    m_client = st.text_input("Client Name", value=site['ClientName'], disabled=True)
                    m_phone = st.text_input("Phone Number", value=site['PhoneNumber'] or "")
                    m_city = st.text_input("City / Town", value=site['CityTown'] or "")
                    m_address = st.text_area("Full Site Address", value=site['FullAddress'] or "")
                    m_gmaps = st.text_input("Google Maps Location Link", value=site['GoogleMapsLink'] or "")
                    m_tech = st.text_input("Technician Name *")

                with mc2:
                    m_sn = st.text_input("Battery Serial Number", value=site['BatterySerialNumber'] or "")
                    m_kw = st.number_input("System Capacity (kW)", value=float(site['SystemCapacityKW'] or 0.0))
                    m_kwh = st.number_input("Battery Capacity (kWh)", value=float(site['BatteryCapacityKWh'] or 0.0))
                    m_inverter = st.text_input("Inverter Brand / Model", value=site['InverterBrandModel'] or "")
                    m_date = st.date_input("Date of Visit", value=datetime.date.today())
                    m_status = st.selectbox("Current System Status", ["Operational", "Maintenance Required", "System Down"])

                m_purpose = st.selectbox("Purpose of Visit", ["Routine Inspection", "Emergency Repair", "Capacity Upgrade", "Firmware / BMS Calibration", "Warranty Return"])
                m_issues = st.text_area("Issues Observed", placeholder="Describe any problems found on site...")
                m_action = st.text_area("Action Taken", placeholder="Describe repairs, replaced parts, or adjustments made...")

                submit_maint = st.form_submit_button("💾 Save Maintenance Log")

                if submit_maint:
                    if not m_tech:
                        st.error("Please enter the Technician Name.")
                    else:
                        conn = get_db_connection()
                        if conn:
                            try:
                                cursor = conn.cursor()
                                # 1. Insert into MaintenanceLogs
                                m_query = """
                                    INSERT INTO MaintenanceLogs 
                                    (InstallationID, BatterySerialNumber, ClientName, PhoneNumber, CityTown, 
                                     FullAddress, GoogleMapsLink, SystemCapacityKW, BatteryCapacityKWh, 
                                     InverterBrandModel, PurposeOfVisit, CurrentStatus, IssuesObserved, 
                                     ActionTaken, TechnicianName, VisitDate)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """
                                cursor.execute(m_query, (
                                    site['InstallationID'], m_sn, site['ClientName'], m_phone, m_city,
                                    m_address, m_gmaps, m_kw, m_kwh,
                                    m_inverter, m_purpose, m_status, m_issues,
                                    m_action, m_tech, m_date
                                ))
                                
                                # 2. Update site status in Installations table
                                cursor.execute("UPDATE Installations SET CurrentStatus = %s WHERE InstallationID = %s", (m_status, site['InstallationID']))
                                
                                conn.commit()
                                cursor.close()
                                conn.close()
                                st.success(f"✅ Maintenance visit logged for '{site['ClientName']}'!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error saving maintenance record: {e}")

# --- TAB 4: BATTERY PRODUCTION LOGS (EVERYONE) ---
    elif choice == "🔋 Battery Production":
        st.header("🔋 Comprehensive Battery QC & Production Log")
    
        tab1, tab2 = st.tabs(["📝 Log New Battery", "📊 View Production History"])
    
    with tab1:
        with st.form("battery_pro_form", clear_on_submit=True):
            
            # SECTION 1
            st.subheader("1. Battery & Client Identification")
            col1, col2 = st.columns(2)
            with col1:
                serial_no = st.text_input("Battery Serial Number *", placeholder="e.g., JBYD2654...")
                batch_no = st.text_input("Batch Number *")
                prod_date = st.date_input("Production Date *", datetime.date.today())
                client_name = st.text_input("Client Name *")
            with col2:
                contact_details = st.text_input("Contact Details")
                req_date = st.date_input("Battery Request Date *", datetime.date.today())
                final_location = st.text_input("Battery Final Location *", placeholder="e.g., Jos")
            
            st.divider()

            # SECTION 2
            st.subheader("2. Cell Information")
            col3, col4 = st.columns(2)
            with col3:
                capacity_ah = st.number_input("Cell capacity (Ah)", min_value=0, value=120)
                cell_chem = st.selectbox("Cell chemistry *", ["LiFePO4", "NMC", "BYD", "CTL", "EVE", "Other"])
                num_cells = st.text_input("Number of cells (series / parallel) *", placeholder="e.g., 16S 1P")
            with col4:
                cell_supplier = st.text_input("Cell supplier / source *")
                cell_matching = st.radio("Cell matching confirmation *", ["Yes", "No"], horizontal=True)

            st.divider()

            # SECTION 3
            st.subheader("3. BMS Configuration")
            col5, col6 = st.columns(2)
            with col5:
                bms_brand = st.text_input("BMS brand *", placeholder="e.g., JK")
                bms_model = st.text_input("BMS model *", placeholder="e.g., JK_PB2A16S15P")
                firmware_version = st.text_input("Firmware version (if applicable)", placeholder="e.g., V19.30")
                comm_type = st.selectbox("Communication type *", ["CAN", "RS485", "Other"])
            with col6:
                charge_cutoff = st.text_input("Charge cutoff voltage *", placeholder="e.g., 52.6 V")
                discharge_cutoff = st.text_input("Discharge cutoff voltage *", placeholder="e.g., 52.6 V")
                balancing_enabled = st.radio("Balancing enabled *", ["Yes", "No", "Maybe"], horizontal=True)

            st.divider()

            # SECTION 4
            st.subheader("4. Assembly Checklist")
            st.write("Checks:")
            chk_busbars = st.checkbox("Bus bars tightened")
            chk_temp = st.checkbox("Temperature sensors placed")
            chk_insulation = st.checkbox("Insulation installed")
            chk_case = st.checkbox("Case grounded")
            chk_cable = st.checkbox("Correct cable gauge used")
            chk_polarity = st.checkbox("Polarity checked")
            chk_other = st.text_input("Other (specify)", placeholder="e.g., Battery Inspection Completed")

            st.divider()

            # SECTION 5
            st.subheader("5. Electrical Test Results")
            col7, col8 = st.columns(2)
            with col7:
                ind_cell_voltages = st.text_input("Individual cell voltages (or range) *", placeholder="e.g., 3.2 V")
                pack_volt_before = st.text_input("Pack voltage before charge *", placeholder="e.g., 52.6 V")
                pack_volt_after = st.text_input("Pack voltage after full charge *", placeholder="e.g., 52.6 V")
            with col8:
                initial_discharge = st.text_input("Initial discharge test result *", placeholder="e.g., Good")
                load_test = st.radio("Load test passed *", ["Yes", "No"], horizontal=True)

            st.divider()

            # SECTION 6
            st.subheader("6. Quality Control & Approval")
            col9, col10 = st.columns(2)
            with col9:
                vis_inspect = st.radio("Visual inspection passed *", ["Yes", "No"], horizontal=True)
                elec_inspect = st.radio("Electrical inspection passed *", ["Yes", "No"], horizontal=True)
                qc_approval = st.selectbox("QC approval *", ["Pass", "Fail", "Other"])
            with col10:
                qc_officer = st.text_input("QC officer name")
                remarks = st.text_area("Remarks / fault notes", placeholder="e.g., BATTERY IS FIT FOR USE")

            submit_battery = st.form_submit_button("💾 Submit Final QC Report")
            
            # SUBMIT LOGIC
            if submit_battery:
                if serial_no and client_name:
                    conn = get_db_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            query = """INSERT INTO BatteryLogs (
                                BatterySerialNumber, BatchNumber, ProductionDate, ClientName, ContactDetails, 
                                BatteryRequestDate, BatteryFinalLocation, CellCapacityAh, CellChemistry, 
                                NumberOfCells, CellSupplier, CellMatching, BMSBrand, BMSModel, FirmwareVersion, 
                                ChargeCutoffVoltage, DischargeCutoffVoltage, BalancingEnabled, CommunicationType, 
                                CheckBusBars, CheckTempSensors, CheckInsulation, CheckCaseGrounded, CheckCableGauge, 
                                CheckPolarity, CheckOther, IndCellVoltages, PackVoltageBefore, PackVoltageAfter, 
                                InitialDischargeResult, LoadTestPassed, VisualInspectionPassed, ElectricalInspectionPassed, 
                                QCApproval, QCOfficerName, Remarks
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            )"""
                            
                            # Tuples to pass into database
                            values = (
                                serial_no, batch_no, prod_date, client_name, contact_details, 
                                req_date, final_location, capacity_ah, cell_chem, 
                                num_cells, cell_supplier, cell_matching, bms_brand, bms_model, firmware_version, 
                                charge_cutoff, discharge_cutoff, balancing_enabled, comm_type, 
                                chk_busbars, chk_temp, chk_insulation, chk_case, chk_cable, 
                                chk_polarity, chk_other, ind_cell_voltages, pack_volt_before, pack_volt_after, 
                                initial_discharge, load_test, vis_inspect, elec_inspect, 
                                qc_approval, qc_officer, remarks
                            )
                            
                            cursor.execute(query, values)
                            conn.commit()
                            cursor.close()
                            st.success(f"✅ Battery {serial_no} logged and passed securely into the database!")
                        except mysql.connector.Error as err:
                            if err.errno == 1062: 
                                st.error(f"⚠️ Serial Number '{serial_no}' already exists in the database.")
                            else:
                                st.error(f"❌ Error saving battery log: {err}")
                        finally:
                            conn.close()
                else:
                    st.warning("⚠️ Please fill out at least the Battery Serial Number and Client Name to submit.")
                    
   # View Directory Tab (Upgraded Dashboard)
    with tab2:
        st.subheader("📊 Live Battery Production Dashboard")
        conn = get_db_connection()
        if conn:
            try:
                query = "SELECT * FROM BatteryLogs ORDER BY LogDate DESC"
                df_battery = pd.read_sql(query, conn)
                
                if not df_battery.empty:
                    # --- KPI METRIC CARDS ---
                    total_logged = len(df_battery)
                    total_passed = len(df_battery[df_battery['QCApproval'] == 'Pass'])
                    total_failed = len(df_battery[df_battery['QCApproval'] == 'Fail'])
                    pass_rate = round((total_passed / total_logged) * 100, 1) if total_logged > 0 else 0

                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                    col_m1.metric("Total Assembled", f"{total_logged} Units")
                    col_m2.metric("Passed QC", f"✅ {total_passed}")
                    col_m3.metric("Failed/Pending", f"⚠️ {total_failed}")
                    col_m4.metric("Pass Rate", f"{pass_rate}%")
                    
                    st.divider()
                    
                    # --- COLOR-CODED TABLE ---
                    st.write("**Recent Production Logs**")
                    
                    # Function to color code the QC Approval column
                    def highlight_qc(val):
                        if val == 'Pass':
                            return 'background-color: rgba(0, 200, 83, 0.2); color: #00C853; font-weight: bold'
                        elif val == 'Fail':
                            return 'background-color: rgba(255, 61, 0, 0.2); color: #FF3D00; font-weight: bold'
                        return ''
                    
                    # Apply the styling
                    styled_df = df_battery.style.map(highlight_qc, subset=['QCApproval'])
                    
                    # Display the styled dataframe
                    st.dataframe(styled_df, use_container_width=True)
                else:
                    st.info("No battery logs found. Submit your first QC report to see data here!")
            except Exception as e:
                st.error(f"Error fetching battery logs: {e}")
            finally:
                conn.close()
                
                # --- TAB 5: ANALYTICS & INSIGHTS (ADMIN ONLY) ---

elif choice == "📈 Analytics & Insights":
    st.subheader("📈 Battery Production Analytics & Operational Insights")
    st.markdown("Real-time manufacturing trends and inventory metrics derived from your database.")

    # 1. Fetch All Battery Data from MySQL
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql("SELECT * FROM BatteryLogs", conn)
            conn.close()
        except Exception as e:
            st.error(f"Error fetching analytics data: {e}")
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    if df.empty:
        st.info("No battery logs found in the database to generate analytics.")
    else:
        # Data Preprocessing
        df['ProductionDate'] = pd.to_datetime(df['ProductionDate'], errors='coerce')
        df['CellCapacityAh'] = pd.to_numeric(df['CellCapacityAh'], errors='coerce').fillna(120)

        # Approximate Energy (kWh) calculation assuming 51.2V nominal for 16S LiFePO4 packs
        df['Estimated_kWh'] = (df['CellCapacityAh'] * 51.2) / 1000

        # --- KPI SUMMARY CARDS ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        with kpi1:
            st.metric(label="🔋 Total Packs Built", value=f"{len(df)} Units")
        with kpi2:
            total_kwh = df['Estimated_kWh'].sum()
            st.metric(label="⚡ Total Storage Deployed", value=f"{total_kwh:.1f} kWh")
        with kpi3:
            top_bms = df['BMSBrand'].mode()[0] if not df['BMSBrand'].dropna().empty else "N/A"
            st.metric(label="⚙️ Primary BMS Brand", value=f"{top_bms}")
        with kpi4:
            most_common_cap = int(df['CellCapacityAh'].mode()[0]) if not df['CellCapacityAh'].dropna().empty else 120
            st.metric(label="📦 Main Pack Size", value=f"{most_common_cap} Ah")

        st.divider()

        # --- ROW 1: PRODUCTION TRENDS & CHEMISTRY ---
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📅 Monthly Production Volume")
            df['YearMonth'] = df['ProductionDate'].dt.to_period('M').astype(str)
            monthly_counts = df.groupby('YearMonth').size().reset_index(name='Packs Produced')
            
            fig_monthly = px.bar(
                monthly_counts, 
                x='YearMonth', 
                y='Packs Produced',
                text='Packs Produced',
                labels={'YearMonth': 'Month', 'Packs Produced': 'Packs Built'},
                color_discrete_sequence=['#0F4C81'] # Royal Blue theme
            )
            fig_monthly.update_traces(textposition='outside')
            fig_monthly.update_layout(xaxis_title="Month", yaxis_title="Units Built", height=350)
            st.plotly_chart(fig_monthly, use_container_width=True)

        with col2:
            st.markdown("### 🧪 Cell Chemistry Share")
            chem_counts = df['CellChemistry'].value_counts().reset_index()
            chem_counts.columns = ['Chemistry', 'Count']
            
            fig_chem = px.pie(
                chem_counts, 
                names='Chemistry', 
                values='Count', 
                hole=0.4,
                color_discrete_sequence=['#0F4C81', '#00C853', '#E2E8F0', '#0F172A']
            )
            fig_chem.update_layout(height=350)
            st.plotly_chart(fig_chem, use_container_width=True)

        st.divider()

        # --- ROW 2: BMS BRANDS & CAPACITY CLASSES ---
        col3, col4 = st.columns(2)

        with col3:
            st.markdown("### ⚙️ BMS Brand Distribution")
            bms_counts = df['BMSBrand'].value_counts().reset_index()
            bms_counts.columns = ['BMS Brand', 'Units Installed']

            fig_bms = px.bar(
                bms_counts, 
                x='BMS Brand', 
                y='Units Installed',
                color='BMS Brand',
                text='Units Installed',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_bms.update_traces(textposition='outside')
            fig_bms.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_bms, use_container_width=True)

        with col4:
            st.markdown("### 🔋 Capacity Distribution (Ah)")
            cap_counts = df['CellCapacityAh'].astype(str) + " Ah"
            cap_df = cap_counts.value_counts().reset_index()
            cap_df.columns = ['Capacity Class', 'Count']

            fig_cap = px.pie(
                cap_df, 
                names='Capacity Class', 
                values='Count',
                color_discrete_sequence=['#00C853', '#0F4C81', '#64748B']
            )
            fig_cap.update_layout(height=350)
            st.plotly_chart(fig_cap, use_container_width=True)

        st.divider()

        # --- ROW 3: CLIENT DISTRIBUTION ---
        st.markdown("### 👥 Top Clients & Order Volume")
        client_counts = df['ClientName'].value_counts().head(10).reset_index()
        client_counts.columns = ['Client Name', 'Packs Delivered']

        fig_client = px.bar(
            client_counts, 
            x='Packs Delivered', 
            y='Client Name',
            orientation='h',
            text='Packs Delivered',
            color_discrete_sequence=['#0F4C81']
        )
        fig_client.update_traces(textposition='outside')
        fig_client.update_layout(yaxis=dict(autorange="reversed"), height=300)
        st.plotly_chart(fig_client, use_container_width=True)
