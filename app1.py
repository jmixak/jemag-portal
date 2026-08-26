import streamlit as st

# Import custom view modules
from views.master_directory import render_master_directory, render_student_evaluation, render_register_profile
from views.travel_log import render_travel_log
from views.analytics import render_analytics

# Page Configuration
st.set_page_config(page_title="Jemag Portal", page_icon="⚡", layout="wide")

# Load CSS Styles
try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

# User Role Session State Setup
if "role" not in st.session_state:
    st.session_state.role = "admin"

# Navigation Menu Router
st.sidebar.title("Navigation Menu")

if st.session_state.role == "admin":
    menu_options = [
        "🏢 View Master Directory",  
        "👨‍🎓 Student Evaluation",
        "📝 Register New Profile",
        "🧳 Travel Log",
        "📈 Analytics & Insights"
    ]
else:
    menu_options = ["🧳 Travel Log"]

choice = st.sidebar.radio("Go to", menu_options)

# Route to corresponding View Page
if choice == "🏢 View Master Directory":
    render_master_directory()
elif choice == "👨‍🎓 Student Evaluation":
    render_student_evaluation()
elif choice == "📝 Register New Profile":
    render_register_profile()
elif choice == "🧳 Travel Log":
    render_travel_log()
elif choice == "📈 Analytics & Insights":
    render_analytics()