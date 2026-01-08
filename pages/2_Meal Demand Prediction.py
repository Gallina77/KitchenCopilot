import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils import get_todays_prediction
import plotly.graph_objects as go

logo = "styles/images/kitchencopilot_logo_transparent.png"
st.logo(logo, size="medium", link=None, icon_image=None)

st.set_page_config(page_title="Meal Predictions", layout="wide")

st.title("Meal Demand Predictions")

# Get predictions from the last 7 days
data = get_todays_prediction()

# === TOP METRICS SECTION ===
st.subheader("Key Insights")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_meals = data['predicted_meals'].sum()
    st.metric(
        label="Total Predicted Meals",
        value=f"{int(total_meals):,}",
        delta=None
    )

with col2:
    avg_meals = data['predicted_meals'].mean()
    st.metric(
        label="Daily Average",
        value=f"{int(avg_meals)}",
        delta=None
    )

with col3:
    peak_day = data.loc[data['predicted_meals'].idxmax()]
    st.metric(
        label="Peak Demand Day",
        value=peak_day['date'].strftime('%a, %b %d'),
        delta=f"{int(peak_day['predicted_meals'])} meals"
    )

with col4:
    # Calculate capacity utilization
    avg_utilization = (data['predicted_meals'] / data['expected_capacity']).mean() * 100
    st.metric(
        label="Avg Capacity Usage",
        value=f"{avg_utilization:.1f}%",
        delta=f"{avg_utilization - 85:.1f}%" if avg_utilization < 85 else f"+{avg_utilization - 85:.1f}%",
        delta_color="inverse"  # Red if over 85%, green if under
    )

st.divider()

# === MAIN CHART SECTION ===
st.subheader("Demand Forecast")

# Prepare data for chart
chart_data = data[['date', 'predicted_meals', 'expected_capacity']].copy()
chart_data['date'] = chart_data['date'].dt.strftime('%a %m/%d')
chart_data = chart_data.set_index('date')

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=chart_data.index,
    y=chart_data['predicted_meals'],
    mode='lines+markers',
    name='Predicted Meals',
    line=dict(color='#1f77b4', width=3)  # Blue
))

fig.add_trace(go.Scatter(
    x=chart_data.index,
    y=chart_data['expected_capacity'],
    mode='lines+markers',
    name='Expected Capacity',
    line=dict(color='#ff7f0e', width=3)  # Orange
))

st.plotly_chart(fig, use_container_width=True)


# Add explanation text
st.caption("📈 Blue line shows predicted meal demand, orange line shows expected capacity")

st.divider()

# === DETAILED DATA TABLE ===
st.subheader("Detailed Predictions")

# Format the display dataframe
display_df = data.copy()
display_df['date'] = display_df['date'].dt.strftime('%a, %B %d, %Y')
display_df['predicted_meals'] = display_df['predicted_meals'].astype(int)
display_df['utilization_%'] = ((display_df['predicted_meals'] / display_df['expected_capacity']) * 100).round(1)
display_df['prediction_timestamp'] = display_df['prediction_timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    # Convert integer columns to boolean
display_df['is_semester_break'] = display_df['is_semester_break'].astype(bool)
display_df['is_bridge_day'] = display_df['is_bridge_day'].astype(bool)

# Select and rename columns for display
display_columns = {
    'date': 'Date',
    'predicted_meals': 'Predicted Meals',
    'expected_capacity': 'Capacity',
    'utilization_%': 'Utilization %',
    'temperature_max': 'Temp (°C)',
    'weather_condition': 'Weather',
    'holiday_desc': 'Holiday',
    'is_semester_break': 'Semester Break',
    'is_bridge_day': 'Bridge Day',
    'prediction_timestamp': 'Last Updated'
}

display_df_final = display_df[list(display_columns.keys())].rename(columns=display_columns)

st.dataframe(
    display_df_final,
    width = 'stretch',
    hide_index=True,
    column_config={
        "Utilization %": st.column_config.ProgressColumn(
            "Utilization %",
            help="Predicted demand as % of capacity",
            min_value=0,
            max_value=100,
            format="%.1f%%"
        )
    }
)

# === FOOTER INSIGHTS ===
st.divider()
st.subheader("Planning Notes")

# Identify high-demand days
high_demand = data[data['predicted_meals'] > data['expected_capacity'] * 0.9]

if len(high_demand) > 0:
    st.warning(f"⚠️ **High demand alert**: {len(high_demand)} day(s) with utilization above 90%. Consider increasing capacity or adjusting menu.")
    for idx, row in high_demand.iterrows():
        st.write(f"• {row['date'].strftime('%A, %B %d')}: {int(row['predicted_meals'])} meals predicted ({int((row['predicted_meals']/row['expected_capacity'])*100)}% capacity)")
else:
    st.success("✅ All days within comfortable capacity limits")

# Weather considerations
rainy_days = data[data['weather_condition'] == 'Rainy']
if len(rainy_days) > 0:
    st.info(f"🌧️ {len(rainy_days)} rainy day(s) in forecast - may affect demand patterns")