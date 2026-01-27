import streamlit as st
import pandas as pd
from utils import prepare_data, render_badges, get_prediction, save_prediction, get_translations
from datetime import date
from babel.dates import format_date
from components.sidebar import render_language_toggle

# ============================================
# PAGE CONFIG (must be first)
# ============================================
st.set_page_config(layout="wide")

# ============================================
# SIDEBAR
# ============================================
logo = "styles/images/kitchencopilot_logo_transparent.png"
st.logo(logo, size="medium", link=None, icon_image=None) #shows the kitchencopilot logo in Sidebar
render_language_toggle() #displays the language toggle

# ============================================
# INJECT CSS
# ============================================
def inject_custom_css():
    """Inject custom CSS for badges and other styling."""
    st.markdown("""
    <style>
        /* Badge base styles */
        .badge {
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
            display: inline-block;
            margin: 2px 4px 2px 0;
        }
        
        /* Badge variants */
        .badge-weather {
            background-color: rgb(255, 241, 203);
            color: #111111;
            border: 1px solid rgba(255, 241, 203, 0.3);
        }
        
        .badge-break {
            background-color: rgb(255, 143, 143);
            color: #111111;
            border: 1px solid rgba(255, 143, 143, 0.3);
        }
        
        .badge-bridge {
            background-color: rgb(194, 226, 250);
            color: #1c83e1;
            border: 1px solid rgba(28, 131, 225, 0.3);
        }
        
        .badge-holiday {
            background-color: rgb(255, 143, 143);
            color: #ffffff;
            border: 1px solid rgba(255, 75, 75, 0.3);
        }
        
        /* Day row container styling */
        .day-row-container {
            background-color: #262730;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 8px;
        }
        
        /* Prediction value styling */
        .prediction-value {
            font-size: 24px;
            font-weight: 600;
            color: #21c354;
        }
        
        .prediction-value.overridden {
            color: #ffbd45;
        }
        
        .prediction-original {
            font-size: 12px;
            color: #a3a8b8;
            text-decoration: line-through;
        }
    </style>
    """, unsafe_allow_html=True)

# Call this once at the top of your app
inject_custom_css()


# ============================================
# GET TRANSLATIONS
# ============================================
t = get_translations("forecast")

# ============================================
# INITIALIZE SESSION STATE
# ============================================

if 'form_submitted' not in st.session_state:
    st.session_state['form_submitted'] = False
    
if 'predictions_generated' not in st.session_state:
    st.session_state['predictions_generated'] = False
    
if 'forecast_df' not in st.session_state:
    st.session_state['forecast_df'] = None

if 'forecast_saved' not in st.session_state:
    st.session_state['forecast_saved'] = False

# ============================================
# THE SWITCH - Check predictions first
# ============================================

if st.session_state['predictions_generated']:
    # ========== STATE 2: Review & Save ==========
    st.success(t["success_message_prediction"])
    st.title(t["step_2_title"])
    st.caption(t["step_2_subtitle"])
    
    df = st.session_state['forecast_df']
    locale = st.session_state.lang.lower()
    
    # Create formatted date display if not already there
    if 'date_display' not in df.columns:
        df['date_display'] = df['date'].apply(
            lambda d: format_date(d, format='EEEE, dd. MMMM', locale=locale)
        )
    
    
    for i, (idx, row) in enumerate(df.iterrows()):
        if i % 2 == 0:
            left_col, right_col = st.columns(2)
        
        col = left_col if i % 2 == 0 else right_col

        with col:
            with st.container(border=True):
                
                st.markdown(f"**{row['date_display']}**")
                st.markdown(render_badges(row, t), unsafe_allow_html=True)
                
                
                # Row 2: Capacity | Prediction + Toggle
                left_part, right_part = st.columns([1, 1])
                
                with left_part:
                       st.markdown(f"{t['expected_capacity_label']}:  "
                            f"<strong style='color: #6082B6; font-size: 18px;'>{int(row['expected_capacity'])}</strong>",
                            unsafe_allow_html=True
                        )
                     
                with right_part:
                    pred_col, toggle_col = st.columns([3, 1])
            
                    with pred_col:
                        st.markdown(
                            f"{t['prediction_label']}:  "
                            f"<strong style='color: #21c354; font-size: 18px;'>{int(row['predicted_meals'])}</strong>",
                            unsafe_allow_html=True
                        )
            
                    with toggle_col:
                        override_on = st.toggle(
                            "✏️",
                            key=f"override_{row['date']}",
                            label_visibility="collapsed"
                        )
        
                    # Row 3: Override (only when toggle ON)
                if override_on:
                    st.markdown(
                        "<hr style='margin: 4px 0; border: none; border-top: 1px solid #3d4251;'>",
                        unsafe_allow_html=True
                    )
                    override_col1, override_col2 = st.columns([1, 2])
                    
                    with override_col1:
                        st.number_input(
                            label=t["override_value_label"],
                            key=f"override_value_{row['date']}",
                            value=int(row['predicted_meals']),
                            step=25
                        )
                    
                    with override_col2:
                        st.text_input(
                            label=t["override_reason_label"],
                            key=f"override_reason_{row['date']}",
                            placeholder=t["override_reason_placeholder"]
                        )
    # Action buttons
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← " + t["start_over_button"]):
            st.session_state['predictions_generated'] = False
            st.session_state['form_submitted'] = False
            st.rerun()
    
    with col2:
        if not st.session_state.get('forecast_saved', False):
            if st.button("✓ " + t["save_forecast_button"], type="primary"):
                df = st.session_state['forecast_df'].copy()
    
                # Collect overrides from session state
                for idx, row in df.iterrows():
                    date_key = row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date'])
                    
                    # Check if override toggle is ON for this day
                    if st.session_state.get(f"override_{date_key}", False):
                        df.at[idx, 'override_meal_prediction'] = st.session_state.get(f"override_value_{date_key}")
                        df.at[idx, 'override_reason'] = st.session_state.get(f"override_reason_{date_key}")
                    else:
                        df.at[idx, 'override_meal_prediction'] = None
                        df.at[idx, 'override_reason'] = None
                        
                clean_df = df.drop(columns=['date_display', 'weather_icon'], errors='ignore')
                is_success, message = save_prediction(clean_df)
                if is_success:
                    st.session_state['forecast_saved'] = True
                    st.rerun()
                else:
                    st.error(message)

        # Success + Dashboard button (only after successful save)
        if st.session_state.get('forecast_saved', False):
            st.success(t["save_success"])
            if st.button(t["view_dashboard"]):
                st.session_state['forecast_saved'] = False
                st.session_state['predictions_generated'] = False
                st.session_state['form_submitted'] = False
                st.switch_page("pages/2_Meal Demand Prediction.py")

else:
    # ========== STATE 0 & 1: Form always visible ==========
    
    st.title(t["prepare_your_forecast_title"])
    st.caption(t["prepare_your_forecast_subtitle"])
    
    # Form (shows in both State 0 and State 1)
    with st.form("date_form"):
        cols = st.columns([1, 1])
        start_date = cols[0].date_input(t["start_date_label"])
        number_of_days = cols[1].selectbox(
            t["number_of_days_label"],
            [3, 5, 7],
            index=1, #shows 5 as a standard
            accept_new_options=True,
            placeholder=t["number_of_days_placeholder"]
        )
        submit = st.form_submit_button(t["load_days_button"], type="primary")
    
    if submit:
        st.session_state['form_submitted'] = True
        st.session_state['forecast_df'] = prepare_data(start_date, int(number_of_days))
        st.rerun()
    
    # Capacity inputs (only shows in State 1)
    if st.session_state['form_submitted']:
        df = st.session_state['forecast_df']
        locale = st.session_state.lang.lower()

        #Create a formatted display column (only if date is still datetime)
        if pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date_display'] = df['date'].apply(lambda d: format_date(d, format='EEEE, dd. MMMM', locale=locale))
        
        for i, (idx, row) in enumerate(df.iterrows()):
            if i % 2 == 0:
                left_col, right_col = st.columns(2)
            
            col = left_col if i % 2 == 0 else right_col
            
            with col:
                with st.container(border=True):
                    st.markdown(f"**{row['date_display']}**")
                    st.markdown(render_badges(row, t), unsafe_allow_html=True)
                    st.number_input(
                        label=t["expected_capacity_label"],
                        key=f"cap_{row['date']}",
                        label_visibility="visible",
                        min_value=50,
                        max_value=400,
                        step=25
                    )
        
        if st.button(t["generate_prediction_button"], type="primary"):
        # Collect capacity values
            for idx, row in df.iterrows():
                df.at[idx, 'expected_capacity'] = st.session_state[f"cap_{row['date']}"]
        
            # Check for missing values
            if df['expected_capacity'].isnull().any():
                st.error(t["error_missing_capacity"])
            else:
                # Run prediction
                df_pred = get_prediction(df)
                st.session_state['forecast_df'] = df_pred
                st.session_state['predictions_generated'] = True
                st.rerun()  # Success message will show in State 2




