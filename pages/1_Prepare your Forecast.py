import streamlit as st
import pandas as pd
from utils import prepare_data, get_prediction, save_prediction
from datetime import date

# Must be first Streamlit command
st.set_page_config(layout="wide")

logo = "styles/images/kitchencopilot_logo_transparent.png"
st.logo(logo, size="medium", link=None, icon_image=None)

st.title("Prepare your data")

# Initialize session state
def initialize_session_state():
    """Consolidate all session state initialization"""
    if 'number_of_days' not in st.session_state:
        st.session_state['number_of_days'] = 5
    if 'start_date' not in st.session_state:
        st.session_state['start_date'] = date.today()
    if 'form_submitted' not in st.session_state:
        st.session_state['form_submitted'] = False
    if 'forecast_df' not in st.session_state:
        st.session_state['forecast_df'] = None

initialize_session_state()

# Form for user input
with st.form("date_form"):
    start_date = st.date_input('Pick a start date')
    number_of_days = st.number_input('Number of days to predict', min_value=1, max_value=7, value=5, step=1)
    submit_button = st.form_submit_button('Prepare Data')

# Handle form submission
if submit_button:
    # Clear old forecast when form is resubmitted
    if 'forecast_df' in st.session_state:
        del st.session_state['forecast_df']
    
    st.session_state['form_submitted'] = True
    st.session_state['start_date'] = start_date
    st.session_state['number_of_days'] = number_of_days

# Only show content if form has been submitted
if st.session_state['form_submitted']:
    
    # DATA LOADING - only runs if data not already loaded
    if 'forecast_df' not in st.session_state:
        df = prepare_data(
            st.session_state['start_date'], 
            st.session_state['number_of_days']
        )
        st.session_state['forecast_df'] = df

    # DISPLAY SECTION - runs every time
    edited_df = st.data_editor(
        st.session_state['forecast_df'],
        column_config={ 
            "date": st.column_config.DateColumn(
                "Date",
                format="DD-MM-YYYY"
            ),
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
        disabled=[
            "date", "weekday", "month", "holiday_desc",
            "is_semester_break", "is_bridge_day", 
            "temperature_max", "weather_condition"
        ],
        hide_index=True,
    )
    
    # Save edits back to session state
    st.session_state['forecast_df'] = edited_df
    
    # Generate prediction button
    submit = st.button("Generate Prediction")

    if submit:
        if st.session_state['forecast_df']['expected_capacity'].isnull().any():
            st.error("Please fill in all expected capacity values before submitting.")
        else: 
            updated_df = get_prediction(st.session_state['forecast_df'])
            is_success, message = save_prediction(updated_df)
            if is_success:
                st.success(message)         
            else:
                st.error(message)