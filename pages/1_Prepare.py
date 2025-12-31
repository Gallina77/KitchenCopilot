import streamlit as st
import pandas as pd
from utils import prepare_data, get_prediction, save_prediction

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

# Clear old forecast when form is resubmitted
if 'forecast_df' in st.session_state:
    del st.session_state['forecast_df']

# If button clicked, set flag to True
if submit_button:
    st.session_state['form_submitted'] = True
    st.session_state['start_date'] = start_date
    st.session_state['number_of_days'] = number_of_days

if st.session_state['form_submitted']:
    # Only create DataFrame if it doesn't exist yet
    if 'forecast_df' not in st.session_state:

        df = prepare_data(start_date, number_of_days)

        st.session_state['forecast_df'] = df

    edited_df = st.data_editor(
        st.session_state['forecast_df'],
        column_config={ 
        "date": "Date",
        "weekday": "Weekday",
        "month": "Month",
        "holiday_desc": "Description",
        "is_semester_break": "Semester Break",
        "is_bridge_day": "Bridge Day",
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

    disabled=["date", "weekday", "weekday", "month", "holiday_desc","is_semester_break",
            "is_bridge_day", "temperature_max", "weather_condition"],
    hide_index=True,
    
    )
    st.session_state['forecast_df'] = edited_df
    submit = st.button("Generate Prediction")

    if submit:
        if st.session_state['forecast_df']['expected_capacity'].isnull().any():
            st.error("Please fill in all expected capacity values before submitting.")
        else: 
            updated_df = get_prediction(st.session_state['forecast_df'])
            save_prediction(updated_df)
            st.success("Data saved and prediction generated! Navigate to the Prediction page to view predictions.")
            st.session_state['form_submitted'] = True  
      