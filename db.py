import mysql.connector
import streamlit as st

def get_db_connection():
    """Establishes and returns a connection to the MySQL database using Streamlit secrets."""
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