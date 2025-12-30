import streamlit as st

@st.cache_resource
def get_connection():
    # Create the SQL connection to kitchencopilot_db as specified in your secrets file.
    return st.connection('kitchencopilot_db', type='sql')

def get_holidays(start_date, end_date): 
    # Create your SQL query with date filtering

    query = f"""
        SELECT * FROM holidays 
        WHERE date >= '{start_date}' 
        AND date <= '{end_date}'
    """
    print("SQL Query:", query)
    
    conn = get_connection()
    result = conn.query(query)
    
    return result
    
def find_table(table_name: str):
    conn = get_connection()
    return conn.query(f"SELECT * FROM {table_name}")
