import streamlit as st
import pandas as pd
from utils import get_weather, get_prediction, save_dataframe, get_holidays, find_table

st.title("Prepare your data")
st.set_page_config(layout="wide")

# Form for user input
with st.form("date_form"):
   start_date = st.date_input('Pick a start date')
   number_of_days = st.number_input('Number of days to predict', min_value=1, max_value=7, value=5, step=1)
   submit_button = st.form_submit_button('Prepare Data')

# Initialize session state for form submission
if 'form_submitted' not in st.session_state:
    st.session_state['form_submitted'] = False

# If button clicked, set flag to True
if submit_button:
    st.session_state['form_submitted'] = True
    st.session_state['start_date'] = start_date
    st.session_state['number_of_days'] = number_of_days

if st.session_state['form_submitted']:
    # Only create DataFrame if it doesn't exist yet
    if 'forecast_df' not in st.session_state:

        business_days = pd.date_range(start=start_date, periods=number_of_days, freq='B')

        # Calculate start and end dates from business_days
        start_date_str = business_days.min().strftime('%Y-%m-%d')
        end_date_str = business_days.max().strftime('%Y-%m-%d')

        # NOW fetch weather data using those dates
       # weather_df = get_weather(start_date=start_date_str, end_date=end_date_str, type='forecast')

        # Create base DataFrame with date features
        df = pd.DataFrame({'date': business_days})
        df['weekday'] = df['date'].dt.day_name()
        df['month'] = df['date'].dt.month_name() 

        # Merge weather data
       # df = df.merge(
       #      weather_df[['date', 'temperature_max', 'weather_condition']], 
        #     how='left',
        #     left_on='date',
        #     right_on='date'
       #  )

        # Fetch holidays from the database
        holidays = get_holidays(start_date_str, end_date_str)
        
        # Prepare Holidays Data
        holidays['date'] = pd.to_datetime(holidays['date'])

        # Convert integer columns to boolean
        holidays['is_semesterBreak'] = holidays['is_semesterBreak'].astype(bool)
        holidays['is_bridgeDay'] = holidays['is_bridgeDay'].astype(bool)
    
        # Merge holiday data
        df = df.merge(
            holidays[['date', 'description', 'is_bankHoliday', 'is_semesterBreak', 'is_bridgeDay']],
            how='left',
            on='date'
        ).rename(columns={'description': 'holiday_desc'})

        # Remove bank holidays - ADD THIS LINE
        df = df[(df['is_bankHoliday'] != 1) | (df['is_bankHoliday'].isna())]
        # Drop the column if you don't need it anymore
        df = df.drop('is_bankHoliday', axis=1)

        # Handle missing values
        df['is_semesterBreak'] = df['is_semesterBreak'].fillna(False)
        df['is_bridgeDay'] = df['is_bridgeDay'].fillna(False)
        df['holiday_desc'] = df['holiday_desc'].fillna('')
        df['expected_capacity'] = None

        # Format date as string for display
        df['date'] = df['date'].dt.strftime('%d-%m-%Y')

        st.session_state['forecast_df'] = df

    edited_df = st.data_editor(
        st.session_state['forecast_df'],
        column_config={ 
        "date": "Date",
        "weekday": "Weekday",
        "month": "Month",
        "holiday_desc": "Description",
        "is_semesterBreak": "Semester Break",
        "is_bridgeDay": "Bridge Day",
        "expected_capacity": st.column_config.NumberColumn(
            "Expected Capacity",
            help="How many people are you expecting?",
            min_value=10,
            max_value=400,
            step=10,
            format="%d",
        ),
        "temperature_max": "Temp (°C)",
        "weather_condition": "Weather Condition"
    },

    disabled=["date", "weekday", "weekday", "month", "holiday_desc","is_semesterBreak",
                "is_bridgeDay", "temperature_max", "weather_condition"],
    hide_index=True,
    
    )
    st.session_state['forecast_df'] = edited_df
    submit = st.button("Generate Prediction")

    if submit:
        if st.session_state['forecast_df']['expected_capacity'].isnull().any():
            st.error("Please fill in all expected capacity values before submitting.")
        else: 
            updated_df = get_prediction(st.session_state['forecast_df'])
            save_dataframe(updated_df)
            st.success("Data saved and prediction generated! Navigate to the Prediction page to view predictions.")
            st.session_state['form_submitted'] = True  
      