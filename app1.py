import streamlit as st
import mysql.connector
import pandas as pd
import datetime

# 1. Page configuration (Must be the very first Streamlit command)
st.set_page_config(page_title="Jemag Portal", page_icon="⚡", layout="wide")

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

# App Title
st.title("⚡ Jemag Renewable Energy - Management Portal")

# Sidebar navigation logic based on Role
st.sidebar.title("Navigation Menu")

if st.session_state.role == "admin":
    # Admin sees everything
    menu_options = ["View Master Directory", "Log Student Evaluation", "Register New Profile", "🔋 Battery Production"]
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
if choice == "View Master Directory":
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
elif choice == "Log Student Evaluation":
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
elif choice == "Register New Profile":
    st.header("👤 Add New Staff or Student Profile")
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email Address")
    with col2:
        regular_phone = st.text_input("Regular Phone Number")
        whatsapp_phone = st.text_input("WhatsApp Number")
        role_type = st.selectbox("Role Type", ["Staff", "IT Student"])
        
    if st.button("Save Profile"):
        if first_name and last_name and email:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    query = """INSERT INTO People (FirstName, LastName, Email, RegularPhone, WhatsappPhone, RoleType) 
                               VALUES (%s, %s, %s, %s, %s, %s)"""
                    cursor.execute(query, (first_name, last_name, email, regular_phone, whatsapp_phone, role_type))
                    conn.commit()
                    new_id = cursor.lastrowid
                    cursor.close()
                    st.success(f"Profile created successfully! Assigned System ID: {new_id}")
                except Exception as e:
                    st.error(f"Error saving profile: {e}")
                finally:
                    conn.close()
        else:
            st.warning("Please fill out all required fields (First Name, Last Name, and Email).")

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
                    
    # View Directory Tab
    with tab2:
        st.subheader("Live Battery Production History")
        conn = get_db_connection()
        if conn:
            try:
                query = "SELECT * FROM BatteryLogs ORDER BY LogDate DESC"
                df_battery = pd.read_sql(query, conn)
                if not df_battery.empty:
                    st.dataframe(df_battery, use_container_width=True)
                else:
                    st.info("No battery logs found. Submit your first QC report to see data here!")
            except Exception as e:
                st.error(f"Error fetching battery logs: {e}")
            finally:
                conn.close()
