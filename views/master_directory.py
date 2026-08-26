import streamlit as st
import pandas as pd
from db import get_db_connection

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
                    st.cache_data.clear()
                    st.success(f"✅ Profile created successfully for {first_name} {last_name}! (ID: {person_id})")
                except Exception as e:
                    st.error(f"❌ Error saving profile: {e}")
                finally:
                    conn.close()
        else:
            st.warning("⚠️ Please fill out required fields (First Name, Last Name, Email).")