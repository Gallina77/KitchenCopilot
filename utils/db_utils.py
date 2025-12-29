import streamlit as st

@st.cache_resource
def get_connection():
    # Create the SQL connection to kitchencopilot_db as specified in your secrets file.
    return st.connection('kitchencopilot_db', type='sql')

def find_table(table_name: str):
    conn = get_connection()
    with conn.session as s:
        return conn.query(f"SELECT * FROM {table_name}")
