import streamlit as st

# Create the SQL connection to kitchencopilot_db as specified in your secrets file.
conn = st.connection('kitchencopilot_db', type='sql')

def find_table(table_name: str):
    with conn.session as s:
        return conn.query(f"SELECT * FROM {table_name}")
