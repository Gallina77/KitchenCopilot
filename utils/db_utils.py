import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from utils.day_themes import DAY_THEMES, THEME_VEG_RATIO
from sqlalchemy import text


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
        df.style.format({
            'pct_error': '{:.0f}%',
            'pct_error_veg': '{:.0f}%',
            'pct_error_non_veg': '{:.0f}%'
        }).map(style_difference, subset=[
            'pct_error', 'pct_error_veg', 'pct_error_non_veg'
        ])
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
                lambda row: row['override_meal_prediction'] if pd.notna(row['override_meal_prediction']) 
                else row['predicted_meals'],
                axis=1
                )

            df.to_sql('predictions', session.connection(), if_exists='append',index=False)
            session.commit()
            return (True, None)
        
        except Exception as e:
            # what to do when it fails
            return (False, str(e))
        
def save_actuals(df): 
    conn = get_connection()

    with conn.session as session:
        try:
            df['date'] = pd.to_datetime(df['date']).dt.date
            sql_query = text("""
                INSERT INTO actual_sales (date, actual_meals, actual_meals_veg, actual_meals_non_veg)
                VALUES (:date, :actual_meals, :actual_meals_veg, :actual_meals_non_veg)
                ON CONFLICT(date) DO UPDATE SET
                    actual_meals = excluded.actual_meals,
                    actual_meals_veg = excluded.actual_meals_veg,
                    actual_meals_non_veg = excluded.actual_meals_non_veg
            """)

            for _, row in df.iterrows():
                session.execute(sql_query,
                    {
                        "date": row["date"],
                        "actual_meals": row["actual_meals"],
                        "actual_meals_veg": row["actual_meals_veg"],
                        "actual_meals_non_veg": row["actual_meals_non_veg"],
                    }
                )
            session.commit()
            return (True, None)
        
        except Exception as e:
            # what to do when it fails
            return (False, str(e))


def get_future_predictions():
    conn = get_connection()
    #Take Todays timestamp
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    
    sql_query = "SELECT * FROM predictions WHERE date >= :today " \
    "ORDER BY prediction_timestamp DESC"
    
    params = {"today": monday}
    result = conn.query(sql_query, params=params, ttl=0)

    if result.empty:
        return result
    
    # Convert to datetime

    result['date'] = pd.to_datetime(result['date'],format="ISO8601")
    result['prediction_timestamp'] = pd.to_datetime(result['prediction_timestamp'],format="ISO8601")
    
    # Keep only the row with the latest prediction_timestamp for each date
    latest_predictions = result.sort_values('prediction_timestamp', ascending=False).drop_duplicates('date', keep='first')

    # Sort by date for display
    latest_predictions = latest_predictions.sort_values('date')
    all_predictions = pd.DataFrame(latest_predictions)

    return all_predictions

def get_missing_actuals():
    conn = get_connection()
    sql_query = "SELECT p.date, p.final_prediction, p.day_theme, p.predicted_meals_veg, p.predicted_meals_non_veg, "\
    "a.actual_meals, a.actual_meals_veg, a.actual_meals_non_veg FROM predictions p LEFT JOIN actual_sales a ON p.date = a.date  "\
    "WHERE a.date IS NULL ORDER BY p.date ASC"
    df = conn.query(sql_query, ttl=0)
    df['date'] = pd.to_datetime(df['date'])
    print(df)
    return df


def get_actuals_and_predictions(start_date, end_date):
    conn = get_connection()

    sql_query = "SELECT p.date, p.final_prediction, p.prediction_timestamp, p.day_theme, " \
    "p.predicted_meals_veg, p.predicted_meals_non_veg, " \
    "a.actual_meals, a.actual_meals_veg, a.actual_meals_non_veg  " \
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
    df['pct_error'] = (df['actual_meals'] - df['final_prediction'])/df['final_prediction'].replace(0, np.nan)
  
    # New: per-category differences for the error breakdown chart
    df['difference_veg'] = df['actual_meals_veg'] - df['predicted_meals_veg']
    df['difference_non_veg'] = df['actual_meals_non_veg'] - df['predicted_meals_non_veg']
    df['difference_veg'] = df['actual_meals_veg'] - df['predicted_meals_veg']
    df['difference_non_veg'] = df['actual_meals_non_veg'] - df['predicted_meals_non_veg']
    df['pct_error_veg'] = (df['actual_meals_veg'] - df['predicted_meals_veg']) / df['predicted_meals_veg'].replace(0, np.nan)
    df['pct_error_non_veg'] = (df['actual_meals_non_veg'] - df['predicted_meals_non_veg']) / df['predicted_meals_non_veg'].replace(0, np.nan)


    return df

def calculate_metrics(df, tolerance_pct=0.05):
    """Calculate prediction metrics.
    
    Args:
        df: DataFrame with actual_meals and final_prediction columns
        tolerance_pct: Percentage tolerance (0.05 = within 5%)
    """

    numerator = (df['actual_meals'] - df['final_prediction']).abs()
    denominator = df['final_prediction'].replace(0, np.nan)
    pct_error= (numerator / denominator) * 100
  
    return {
        'mae': (df['actual_meals'] - df['final_prediction']).abs().mean(),
        'over_predicted': (df['final_prediction'] > df['actual_meals']).sum(),
        'under_predicted': (df['final_prediction'] < df['actual_meals']).sum(),
        'accuracy_rate': (pct_error <= tolerance_pct).mean() * 100
    }

def get_empirical_veg_ratio(theme: str) -> tuple[float, float]:
    """Compute the empirical veg/non-veg ratio for a theme from actual_sales history.
    Derives day_theme from each row's date directly 
    Falls back to THEME_VEG_RATIO[theme] if zero historical rows exist for this theme."""
   

    fallback = THEME_VEG_RATIO.get(theme, (0.5, 0.5))
    conn = get_connection()

    sql_query = "SELECT date, actual_meals_veg, actual_meals_non_veg FROM actual_sales " \
    "WHERE actual_meals_veg IS NOT NULL AND actual_meals_non_veg IS NOT NULL"

    try:
        result = conn.query(sql_query, ttl=0)
    except Exception as e:
        print(f"get_empirical_veg_ratio query failed: {e}")
        return fallback

    if result.empty:
        return fallback

    result['date'] = pd.to_datetime(result['date'])
    result['day_theme'] = result['date'].dt.day_name().map(DAY_THEMES)
    theme_rows = result[result['day_theme'] == theme]

    if theme_rows.empty:
        return fallback

    avg_veg = theme_rows['actual_meals_veg'].mean()
    avg_non_veg = theme_rows['actual_meals_non_veg'].mean()
    total = avg_veg + avg_non_veg

    if total == 0:
        return fallback

    return (avg_veg / total, avg_non_veg / total)




