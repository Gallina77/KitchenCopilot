import pandas as pd
from datetime import datetime
from utils import get_holidays, get_weather

def prepare_data(start_date, number_of_days):

    business_days = pd.date_range(start=start_date, periods=number_of_days, freq='B')

    # Calculate start and end dates from business_days
    start_date_str = business_days.min().strftime('%Y-%m-%d')
    end_date_str = business_days.max().strftime('%Y-%m-%d')

    #Determine if we need to go back in history or if we shall get a forecast 
    this_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    now = datetime.today().date()
    if this_date < now: 
        weather_type = "past"
    else: 
        weather_type = "forecast"

     # NOW fetch weather data using those dates
    weather_df = get_weather(start_date=start_date_str, end_date=end_date_str, type=weather_type)

    # Create base DataFrame with date features
    df = pd.DataFrame({'date': business_days})
    df['weekday'] = df['date'].dt.day_name()      # Add back
    df['month'] = df['date'].dt.month_name() 

    # Merge weather data
    df = df.merge(
            weather_df[['date', 'weather_icon', 'temperature_max', 'weather_condition']], 
            how='left',
            left_on='date',
            right_on='date'
    )

    # Fetch holidays from the database
    holidays = get_holidays(start_date_str, end_date_str)
    
    # Prepare Holidays Data
    holidays['date'] = pd.to_datetime(holidays['date'])

    # Convert integer columns to boolean
    holidays['is_semester_break'] = holidays['is_semester_break'].astype(bool)
    holidays['is_bridge_day'] = holidays['is_bridge_day'].astype(bool)

    # Merge holiday data
    df = df.merge(
        holidays[['date', 'description', 'is_bank_holiday', 'is_semester_break', 'is_bridge_day']],
        how='left',
        on='date'
    ).rename(columns={'description': 'holiday_desc'})

    # Remove bank holidays - ADD THIS LINE
    df = df[(df['is_bank_holiday'] != 1) | (df['is_bank_holiday'].isna())]
    # Drop the column if you don't need it anymore
    df = df.drop('is_bank_holiday', axis=1)

    df = df.infer_objects(copy=False)

    # Handle missing values
    df['is_semester_break'] = df['is_semester_break'].astype('boolean').fillna(False)
    df['is_bridge_day'] = df['is_bridge_day'].astype('boolean').fillna(False)
    df['holiday_desc'] = df['holiday_desc'].fillna('').astype(str)
    df['expected_capacity'] = None

    return df


def render_badges(row,t):
    badges = []
    if row.get('temperature_max'):
        badges.append(f'<span class="badge badge-weather">{row["weather_icon"]} {row["temperature_max"]}°C {row["weather_condition"]}</span>')
    if row.get('is_semester_break'):
        badges.append(f'<span class="badge badge-break">{t['semester_break']}</span>')
    if row.get('is_bridge_day'):
        badges.append(f'<span class="badge badge-bridge">{t['bridge_day']}</span>')
    if row.get('holiday_desc'):
        badges.append(f'<span class="badge badge-holiday">{row["holiday_desc"]}</span>')
    return " ".join(badges) if badges else ""