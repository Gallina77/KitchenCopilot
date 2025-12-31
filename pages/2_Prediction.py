import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Meal Predictions", layout="wide")

st.title("Meal Demand Predictions")

# Generate mock data to show the layout
dates = pd.date_range(start=datetime.now().date(), periods=7, freq='B')
mock_data = pd.DataFrame({
    'date': dates,
    'predicted_meals': [145, 167, 189, 156, 142, 178, 163],
    'expected_capacity': [150, 180, 200, 160, 150, 180, 170],
    'temperature_max': [22, 24, 26, 23, 21, 25, 24],
    'weather_condition': ['Clear', 'Cloudy', 'Clear', 'Rainy', 'Clear', 'Cloudy', 'Clear'],
    'is_semester_break': [False, False, False, False, False, False, False],
    'is_bridge_day': [False, False, False, False, False, False, False],
    'holiday_desc': ['', '', '', '', '', '', ''],
    'prediction_timestamp': [datetime.now()] * 7
})

# === TOP METRICS SECTION ===
st.subheader("Key Insights")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_meals = mock_data['predicted_meals'].sum()
    st.metric(
        label="Total Predicted Meals",
        value=f"{int(total_meals):,}",
        delta=None
    )

with col2:
    avg_meals = mock_data['predicted_meals'].mean()
    st.metric(
        label="Daily Average",
        value=f"{int(avg_meals)}",
        delta=None
    )

with col3:
    peak_day = mock_data.loc[mock_data['predicted_meals'].idxmax()]
    st.metric(
        label="Peak Demand Day",
        value=peak_day['date'].strftime('%a, %b %d'),
        delta=f"{int(peak_day['predicted_meals'])} meals"
    )

with col4:
    # Calculate capacity utilization
    avg_utilization = (mock_data['predicted_meals'] / mock_data['expected_capacity']).mean() * 100
    st.metric(
        label="Avg Capacity Usage",
        value=f"{avg_utilization:.1f}%",
        delta=f"{avg_utilization - 85:.1f}%" if avg_utilization < 85 else f"+{avg_utilization - 85:.1f}%",
        delta_color="inverse"  # Red if over 85%, green if under
    )

st.divider()

# === MAIN CHART SECTION ===
st.subheader("7-Day Demand Forecast")

# Prepare data for chart
chart_data = mock_data[['date', 'predicted_meals', 'expected_capacity']].copy()
chart_data['date'] = chart_data['date'].dt.strftime('%a %m/%d')
chart_data = chart_data.set_index('date')

st.line_chart(
    chart_data,
    height=400,
    use_container_width=True
)

# Add explanation text
st.caption("📈 Blue line shows predicted meal demand, orange line shows expected capacity")

st.divider()

# === DETAILED DATA TABLE ===
st.subheader("Detailed Predictions")

# Format the display dataframe
display_df = mock_data.copy()
display_df['date'] = display_df['date'].dt.strftime('%a, %B %d, %Y')
display_df['predicted_meals'] = display_df['predicted_meals'].astype(int)
display_df['utilization_%'] = ((display_df['predicted_meals'] / display_df['expected_capacity']) * 100).round(1)
display_df['prediction_timestamp'] = display_df['prediction_timestamp'].dt.strftime('%Y-%m-%d %H:%M')

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
    use_container_width=True,
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
st.subheader("📝 Planning Notes")

# Identify high-demand days
high_demand = mock_data[mock_data['predicted_meals'] > mock_data['expected_capacity'] * 0.9]

if len(high_demand) > 0:
    st.warning(f"⚠️ **High demand alert**: {len(high_demand)} day(s) with utilization above 90%. Consider increasing capacity or adjusting menu.")
    for idx, row in high_demand.iterrows():
        st.write(f"• {row['date'].strftime('%A, %B %d')}: {int(row['predicted_meals'])} meals predicted ({int((row['predicted_meals']/row['expected_capacity'])*100)}% capacity)")
else:
    st.success("✅ All days within comfortable capacity limits")

# Weather considerations
rainy_days = mock_data[mock_data['weather_condition'] == 'Rainy']
if len(rainy_days) > 0:
    st.info(f"🌧️ {len(rainy_days)} rainy day(s) in forecast - may affect demand patterns")