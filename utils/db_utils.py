import streamlit as st
import pandas as pd
from datetime import datetime

@st.cache_resource
def get_connection():
    # Create the SQL connection to kitchencopilot_db as specified in your secrets file.
    return st.connection('kitchencopilot_db', type='sql')

def style_difference(val):
    # Highlighting max and min values
    if val > 0:
        color = 'green'
    else:
        color = 'red'
    return 'color: %s' % color

def apply_custom_styling(df):
    styled_df = (
    df.style
    .format({'pct_error': '{:.0%}'})
    .map(style_difference, subset=['difference', 'pct_error'])
    )
    return styled_df

def get_holidays(start_date, end_date): 
    conn = get_connection()

    sql_query = "SELECT * FROM holidays WHERE date >= :start_date AND date <= :end_date"
    params = {"start_date": start_date, "end_date": end_date}
    result = conn.query(sql_query, params=params)
    
    return result
    
def save_prediction(df): 
    conn = get_connection()
    with conn.session as session:
        try:
            df['date'] = pd.to_datetime(df['date']).dt.date
            # Ensure override columns exist
            if 'override_meal_prediction' not in df.columns:
                df['override_meal_prediction'] = None
            if 'override_reason' not in df.columns:
                df['override_reason'] = None
            
            df['final_prediction'] = df.apply(
                lambda row: row['override_meal_prediction'] if pd.notna(row['override_meal_prediction']) else row['predicted_meals'],
                axis=1
                )

            df.to_sql('predictions', session.connection(), if_exists='append',index=False)
            session.commit()
            return (True, None)
        
        except Exception as e:
            # what to do when it fails
            return (False, str(e))


def get_future_predictions():
    conn = get_connection()
    #Take Todays timestamp
    today = datetime.now().date()
    
    sql_query = "SELECT * FROM predictions WHERE date >= :today " \
    "ORDER BY prediction_timestamp DESC"
    
    params = {"today": today}
    result = conn.query(sql_query, params=params, ttl=0)

    if result.empty:
        return result
    
    # Convert to datetime
    result['date'] = pd.to_datetime(result['date'])
    result['prediction_timestamp'] = pd.to_datetime(result['prediction_timestamp'])
    
    # Keep only the row with the latest prediction_timestamp for each date
    latest_predictions = result.sort_values('prediction_timestamp', ascending=False).drop_duplicates('date', keep='first')

    # Sort by date for display
    latest_predictions = latest_predictions.sort_values('date')
    all_predictions = pd.DataFrame(latest_predictions)

    return all_predictions

def get_actuals_and_predictions(start_date, end_date):
    conn = get_connection()

    sql_query = "SELECT p.date, p.final_prediction, p.prediction_timestamp, a.actual_meals " \
    "FROM predictions p INNER JOIN actual_sales a ON p.date = a.date " \
    "WHERE p.prediction_timestamp = (SELECT MAX(prediction_timestamp) FROM predictions " \
    "WHERE date = p.date) AND a.date >= :start_date AND a.date <= :end_date " \
    "ORDER BY p.date ASC"


    params={"start_date": start_date, "end_date": end_date} 
    df = conn.query(sql_query, params=params,ttl=0)
    # Final safety check: keeps the latest prediction for every unique date
    df = df.sort_values('prediction_timestamp', ascending=False).drop_duplicates('date')

    df['date'] = pd.to_datetime(df['date'])
    df['weekday'] = df['date'].dt.strftime('%A')
    df['difference'] = df['actual_meals'] - df['final_prediction']
    df['pct_error'] = (df['actual_meals'] - df['final_prediction'])/df['final_prediction']

    return df

def calculate_metrics(df, tolerance_pct=0.05):
    """Calculate prediction metrics.
    
    Args:
        df: DataFrame with actual_meals and final_prediction columns
        tolerance_pct: Percentage tolerance (0.05 = within 5%)
    """
    pct_error = ((df['actual_meals'] - df['final_prediction']) / df['actual_meals']).abs()
    
    return {
        'mae': (df['actual_meals'] - df['final_prediction']).abs().mean(),
        'over_predicted': (df['final_prediction'] > df['actual_meals']).sum(),
        'under_predicted': (df['final_prediction'] < df['actual_meals']).sum(),
        'accuracy_rate': (pct_error <= tolerance_pct).mean() * 100
    }



