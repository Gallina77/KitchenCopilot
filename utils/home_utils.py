import json
from datetime import datetime
from utils.paths import METADATA_PATH
import streamlit as st
import requests

def load_model_metadata():
    try:
        #Loading model metadata
        with open(METADATA_PATH, 'r') as file:
            data = json.load(file)
            timestamp_string = data['training_timestamp']
            return datetime.fromisoformat(timestamp_string)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, KeyError):
        return None
    
#Retrieving last prediction information
def get_last_prediction_info():
    try:
        conn = st.connection("kitchencopilot_db", type="sql")
        results = conn.query("""
            SELECT prediction_timestamp, date 
            FROM predictions 
            WHERE prediction_timestamp = (
                SELECT MAX(prediction_timestamp) 
                FROM predictions
            )
            ORDER BY date
        """)
        
        if results.empty:
            return None
        
        # Get the timestamp (same for all rows)
        timestamp = results.iloc[0]['prediction_timestamp']
        
        # Get first and last dates
        start_date = results.iloc[0]['date']
        end_date = results.iloc[-1]['date']  # -1 means last row
        
        return {
            'timestamp': timestamp,
            'start_date': start_date,
            'end_date': end_date
        }
        
    except Exception as e:
        #print(f"Error: {e}")
        return None


#Testing weather API connectivity  
def check_weather_api_status():
    url = "https://api.open-meteo.com/v1/forecast"
    today = datetime.now().strftime("%Y-%m-%d")
    params = {"latitude": 50.1330,"longitude": 8.6807,"start_date": today,"end_date": today,
    "timezone": "Europe/Berlin","daily": ["temperature_2m_max", "weather_code"]}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as errh:
        return False  

#Checking database connection status
def check_database_status():
    try:
        conn = st.connection("kitchencopilot_db", type="sql")
        # Test the connection with a simple query
        conn.query("SELECT 1")
        return True
    except Exception:
        return False

