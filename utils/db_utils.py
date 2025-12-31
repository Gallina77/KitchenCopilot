import streamlit as st
from sqlalchemy import create_engine, text

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
    
    conn = get_connection()
    result = conn.query(query)
    
    return result
    
def save_prediction(df): 
    conn = get_connection()
        # Get the underlying SQLAlchemy engine
    with conn.session as session:
        
        # Use the connection from the session
        df.to_sql(
            'predictions', 
            session.connection(),
            if_exists='append', 
            index=False
        )
        session.commit()
    return len(df)
