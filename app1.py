import streamlit as st
import mysql.connector
import pandas as pd

# Database connection function reading from cloud secrets
def get_db_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        port=int(st.secrets["mysql"]["port"]),
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"]
    )

# Page configuration
st.set_page_config(page_title="Jemag Portal", page_icon="⚡", layout="wide")
st.title("⚡ Jemag Renewable Energy - Management Portal")

# Sidebar navigation
st.sidebar.title("Navigation Menu")
choice = st.sidebar.radio("Go to", ["View Master Directory", "Log Student Evaluation", "Register New Profile"])