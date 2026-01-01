import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
from datetime import datetime

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
        #session.execute(text('DELETE FROM predictions;'))
        # Use the connection from the session
        df.to_sql(
            'predictions', 
            session.connection(),
            if_exists='append', 
            index=False
        )
        session.commit()
    return len(df)

def get_predictions():
    #Take Todays timestamp
    today = datetime.now().date()
    
    query = f"""
        SELECT * FROM predictions 
        WHERE date >= '{today}'
    """
    
    conn = get_connection()
    result = conn.query(query)
    
    if result.empty:
        return result
    
    # Convert to datetime
    result['date'] = pd.to_datetime(result['date'])
    result['prediction_timestamp'] = pd.to_datetime(result['prediction_timestamp'])
    
    # Keep only the row with the latest prediction_timestamp for each date
    latest_predictions = result.sort_values('prediction_timestamp', ascending=False).drop_duplicates('date', keep='first')
    
    # Sort by date for display
    latest_predictions = latest_predictions.sort_values('date')
    
    return latest_predictions

