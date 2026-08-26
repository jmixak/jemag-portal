import streamlit as st
import os

# Import View Modules
from views.master_directory import render_master_directory, render_student_evaluation, render_register_profile
from views.battery_production import render_battery_production
from views.travel_log import render_travel_log
from views.analytics import render_analytics

# Page Configuration
st.set_page_config(page_title="Jemag Portal", page_icon="⚡", layout="wide")

# Apply CSS
if os.path.exists("style.css"):
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Top Brand Header
col_logo, col_title = st.columns([1, 5])
with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=110)
with col_title:
    st.title("JEMAG Solar & Battery Operations Portal")

st.divider()

# Session State Role Setup
if "role" not in st.session_state:
    st.session_state.role = "admin"

# Sidebar Branding & Navigation
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.title("Navigation")

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
    menu_options = ["🧳 Travel Log"]

choice = st.sidebar.radio("Select Page", menu_options)

# Router Logic
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