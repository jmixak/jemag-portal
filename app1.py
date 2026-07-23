import streamlit as st
import mysql.connector
import pandas as pd

# Page configuration
st.set_page_config(page_title="Jemag Portal", page_icon="⚡", layout="wide")

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

# Sidebar navigation
st.sidebar.title("Navigation Menu")
choice = st.sidebar.radio(
    "Go to", 
    ["View Master Directory", "Log Student Evaluation", "Register New Profile", "🔋 Battery Production"]
)

st.divider()

# --- TAB 1: VIEW MASTER DIRECTORY ---
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

# --- TAB 2: LOG STUDENT EVALUATION ---
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

# --- TAB 3: REGISTER NEW PROFILE ---
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

# --- TAB 4: BATTERY PRODUCTION LOGS ---
elif choice == "🔋 Battery Production":
    st.header("🔋 Battery Production & Quality Control")
    
    # Create two sub-tabs for organizing the workflow!
    tab1, tab2 = st.tabs(["📝 Log New Battery", "📊 View Production History"])
    
    # Sub-Tab 1: The Input Form
    with tab1:
        st.subheader("Record a New Battery Unit")
        with st.form("battery_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                serial_number = st.text_input("Battery Serial Number (e.g., JEM-12V-001)")
                battery_model = st.selectbox("Battery Chemistry/Model", ["LiFePO4", "Lithium-Ion", "Lead-Acid (Deep Cycle)", "Tubular Gel"])
                voltage = st.selectbox("System Voltage", [12, 24, 48])
            with col2:
                capacity = st.number_input("Capacity (Ah)", min_value=10, step=10, value=100)
                assembled_by = st.text_input("Assembled By (Staff Name)")
                qc_status = st.selectbox("QC Status", ["Pending", "Passed", "Failed"])
            
            notes = st.text_area("Production Notes / Test Results")
            submit_battery = st.form_submit_button("Save Battery Log")
            
            if submit_battery:
                if serial_number and assembled_by:
                    conn = get_db_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            query = """INSERT INTO BatteryLogs 
                                       (SerialNumber, BatteryModel, Voltage, CapacityAh, AssembledBy, QC_Status, ProductionNotes) 
                                       VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                            cursor.execute(query, (serial_number, battery_model, voltage, capacity, assembled_by, qc_status, notes))
                            conn.commit()
                            cursor.close()
                            st.success(f"✅ Battery {serial_number} logged successfully!")
                        except mysql.connector.Error as err:
                            # Handle duplicate serial numbers gracefully
                            if err.errno == 1062: 
                                st.error(f"⚠️ Serial Number '{serial_number}' already exists in the database.")
                            else:
                                st.error(f"❌ Error saving battery log: {err}")
                        finally:
                            conn.close()
                else:
                    st.warning("Please enter at least the Serial Number and Assembler's Name.")
                    
    # Sub-Tab 2: The View Directory
    with tab2:
        st.subheader("Live Production History")
        conn = get_db_connection()
        if conn:
            try:
                query = "SELECT * FROM BatteryLogs ORDER BY LogDate DESC"
                df_battery = pd.read_sql(query, conn)
                if not df_battery.empty:
                    st.dataframe(df_battery, use_container_width=True)
                else:
                    st.info("No battery logs found in the database yet.")
            except Exception as e:
                st.error(f"Error fetching battery logs: {e}")
            finally:
                conn.close()
