import streamlit as st
import pandas as pd
import db_utils as db
import weather_utils as weather
import prediction_utils as prediction


st.title("Prepare your data")

# Fetch holidays from the database
holidays = db.find("holidays")

# Form for user input
with st.form("date_form"):
   start_date = st.date_input('Pick a start date')
   number_of_days = st.number_input('Number of days to predict', min_value=1, max_value=14, value=7, step=1)
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
        data = []
        business_days = pd.date_range(start=start_date, periods=number_of_days, freq='B')
        start_date = business_days.min().strftime('%Y-%m-%d')
        end_date = business_days.max().strftime('%Y-%m-%d')
        weather_df = weather.get_weather(start_date=start_date, end_date=end_date)
        for day in business_days:
            data.append({
                    "date": f"{day.strftime('%d-%m-%Y')}", 
                    "weekday": f"{day.strftime('%A')}",
                    "weather_temp": weather_df[weather_df['dates'] == day]['temperature_max'].values[0] if any(weather_df['dates'] == day) else None, 
                    "weather_condition": weather_df[weather_df['dates'] == day]['weather_code'].values[0] if any(weather_df['dates'] == day) else None,
                    "is_holiday": True if any(holidays['date'] == day.strftime('%Y-%m-%d')) else False, 
                    "holiday_desc": holidays[holidays['date'] == day.strftime('%Y-%m-%d')]['description'].values[0] if any(holidays['date'] == day.strftime('%Y-%m-%d')) else "",
                    "expected_capacity":None})
        
        df = pd.DataFrame(data)
        st.session_state['forecast_df'] = df


    edited_df = st.data_editor(
        st.session_state['forecast_df'],
        column_config={
            "date": "date",
            "weekday": "Weekday",
            "weather_temp": "Temp (°C)",
            "weather_condition": "Weather Condition",
            "is_holiday": "Holiday ?",
            "holiday_desc": "Description",
            "expected_capacity": st.column_config.NumberColumn(
                "Expected Capacity",
                help="How many people are you expecting?",
                min_value=10,
                max_value=400,
                step=10,
                format="%d",
            ),
        
        },
        disabled=["date", "weekday","weather_temp", "weather_condition", "is_holiday", "holiday_desc"],
        hide_index=True,
    )
    st.session_state['forecast_df'] = edited_df

    submit = st.button("Save & Generate Prediction")

    if submit:
        if st.session_state['forecast_df']['expected_capacity'].isnull().any():
            st.error("Please fill in all expected capacity values before submitting.")
        else: 
            updated_df = prediction.get_prediction(st.session_state['forecast_df'])
            prediction.save_dataframe(updated_df)
            st.success("Data saved and prediction generated! Navigate to the Prediction page to view predictions.")
            st.session_state['form_submitted'] = True  
      