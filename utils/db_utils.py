import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from utils.day_themes import DAY_THEMES, THEME_VEG_RATIO
from utils.db_conn import get_active_connection_name
from sqlalchemy import text


@st.cache_resource
def get_connection():
    # Connects to the prod or test Postgres DB, selected via APP_ENV (see utils/db_conn.py).
    return st.connection(get_active_connection_name(), type='sql')

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

            # Upsert: `date` is the primary key, and re-saving a forecast for
            # an already-predicted date used to fail outright (to_sql append
            # raised a UniqueViolation, dropping the whole batch). This
            # replaces that date's row instead, so re-generating/overriding a
            # forecast for the same week works - at the cost of losing older
            # predictions for that date.
            columns = [
                'date', 'weekday', 'month', 'day_theme', 'temperature_max', 'weather_condition',
                'is_bridge_day', 'is_school_break', 'holiday_desc',
                'predicted_meals', 'predicted_meals_veg', 'predicted_meals_non_veg',
                'prediction_timestamp', 'override_meal_prediction', 'override_reason', 'final_prediction'
            ]
            columns_sql = ", ".join(columns)
            placeholders_sql = ", ".join(f":{col}" for col in columns)
            update_sql = ", ".join(f"{col} = excluded.{col}" for col in columns if col != 'date')

            sql_query = text(f"""
                INSERT INTO predictions ({columns_sql})
                VALUES ({placeholders_sql})
                ON CONFLICT (date) DO UPDATE SET {update_sql}
            """)

            records_df = df[columns].astype(object).where(pd.notnull(df[columns]), None)
            session.execute(sql_query, records_df.to_dict('records'))
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

    # predictions.date is upserted (one row per date - see save_prediction),
    # so no dedup is needed here anymore.
    sql_query = "SELECT * FROM predictions WHERE date >= :today ORDER BY date"

    params = {"today": monday}
    result = conn.query(sql_query, params=params, ttl=0)

    if result.empty:
        return result

    result['date'] = pd.to_datetime(result['date'], format="ISO8601")
    result['prediction_timestamp'] = pd.to_datetime(result['prediction_timestamp'], format="ISO8601")

    return result

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

    # predictions.date is upserted (one row per date - see save_prediction),
    # so no "keep latest prediction_timestamp per date" filtering is needed.
    sql_query = "SELECT p.date, p.final_prediction, p.prediction_timestamp, p.day_theme, " \
    "p.predicted_meals_veg, p.predicted_meals_non_veg, " \
    "a.actual_meals, a.actual_meals_veg, a.actual_meals_non_veg  " \
    "FROM predictions p INNER JOIN actual_sales a ON p.date = a.date " \
    "WHERE a.date >= :start_date AND a.date <= :end_date " \
    "ORDER BY p.date ASC"

    params={"start_date": start_date, "end_date": end_date}
    df = conn.query(sql_query, params=params,ttl=0)

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




