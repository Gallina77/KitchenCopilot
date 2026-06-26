import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from babel.dates import format_date
from utils import get_future_predictions, get_llm_planning_insights
from components.sidebar import render_language_toggle
from utils.translations_utils import get_translations
import plotly.graph_objects as go

# Must be first Streamlit command
st.set_page_config(page_title="Meal Predictions", layout="wide")

render_language_toggle()
t = get_translations("predictions")
display_columns = t["display_columns"]
chart_data_labels = t["chart_data"]

logo = "styles/images/kitchencopilot_logo_transparent.png"
st.logo(logo, size="medium", link=None, icon_image=None)

st.title(t["predictions_page_title"])

# Get predictions from the last 7 days
data = get_future_predictions()
# === TOP METRICS SECTION ===
st.subheader(t["metrics_subheader"])

col1, col2, col3, col4 = st.columns(4)

if not data.empty:
    with col1:
        with st.container(border=True):
            total_meals = data['final_prediction'].sum()
            total_veg = data['predicted_meals_veg'].sum()
            total_non_veg = data['predicted_meals_non_veg'].sum()
            st.metric(
                label=t["metrics_label_total_predicted_meals"],
                value=f"{int(total_meals):,}"
            )
            st.caption(f"🥦 {int(total_veg)} {t['veg_label']}  |  🍗 {int(total_non_veg)} {t['non_veg_label']}")

    with col2:
        with st.container(border=True):
            avg_meals = data['final_prediction'].mean()
            st.metric(
                label=t["metrics_label_daily_average_predicted_meals"],
                value=f"{int(avg_meals)}"
            )

    with col3:
        with st.container(border=True):
            peak_day = data.loc[data['final_prediction'].idxmax()]
            st.metric(
                label=t["metrics_label_peak_demand_day"],
                value = format_date(peak_day['date'], format='EEE, MMM dd',
                                    locale=st.session_state.lang.lower()),
                delta=f"{int(peak_day['final_prediction'])} {t['metrics_meals_label']}"
            )
            st.caption(
                f"🥦 {int(peak_day['predicted_meals_veg'])} {t['veg_label']}  |  "
                f"🍗 {int(peak_day['predicted_meals_non_veg'])} {t['non_veg_label']}"
            )

else:
    st.error(t["error_message_no_data"])

st.divider()

# === MAIN CHART SECTION ===
st.subheader(t["chart_subheader"])


if not data.empty:
    # Prepare data for chart
    chart_data = data[['date', 'final_prediction', 'predicted_meals_veg', 'predicted_meals_non_veg']].copy()
    locale = st.session_state.lang.lower()

    chart_data['date'] = chart_data['date'].apply(
    lambda d: format_date(d, format='EEE MM/dd', locale=locale)
    )
    chart_data = chart_data.set_index('date')
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=chart_data.index,
        y=chart_data['final_prediction'],
        mode='lines+markers',
        name=chart_data_labels['predicted_meals'],
        line=dict(color='#1f77b4', width=3)
    ))

    fig.add_trace(go.Scatter(
        x=chart_data.index,
        y=chart_data['predicted_meals_veg'],
        mode='lines+markers',
        name=chart_data_labels['predicted_meals_veg'],
        line=dict(color='#27ae60', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=chart_data.index,
        y=chart_data['predicted_meals_non_veg'],
        mode='lines+markers',
        name=chart_data_labels['predicted_meals_non_veg'],
        line=dict(color='#e67e22', width=2)
    ))

    st.plotly_chart(fig, use_container_width=True)

    st.caption(t["chart_caption"])  

else:
    st.error(t["error_message_no_data"])

st.divider()

# === DETAILED DATA TABLE ===
st.subheader(t["detailed_data_subheader"])

if not data.empty:
    # Format the display dataframe
    display_df = data.copy()
    display_df['date'] = display_df['date'].apply(
        lambda d: format_date(d, format='EEEE, dd. MMMM', locale=locale)
    )

    display_df['final_prediction'] = display_df['final_prediction'].astype(int)
    display_df['predicted_meals_veg'] = display_df['predicted_meals_veg'].astype(int)
    display_df['predicted_meals_non_veg'] = display_df['predicted_meals_non_veg'].astype(int)
    display_df['prediction_timestamp'] = display_df['prediction_timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    condition = display_df['weather_condition'].apply(lambda x: x.lower())
    display_df['weather_condition'] = condition.map(t['weather_condition'])

    # Convert integer columns to boolean
    display_df['is_school_break'] = display_df['is_school_break'].astype(bool)
    display_df['is_bridge_day'] = display_df['is_bridge_day'].astype(bool)

    display_df_final = display_df[list(display_columns.keys())].rename(columns=display_columns)

    st.dataframe(
        display_df_final,
        width='stretch',
        hide_index=True
    )
else:
    st.error(t["error_message_no_data"])

     
# === FOOTER INSIGHTS ===
st.divider()
st.subheader(t["insights_subheader"])
if not data.empty:
    with st.spinner(t["spinner_message"]):
            response = get_llm_planning_insights(data.to_json(),st.session_state.lang)
        
    st.info(response)
else:
    st.error(t["insights_no_data"])