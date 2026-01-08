import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta, datetime  
from utils import get_actuals_and_predictions, apply_custom_styling, calculate_metrics


logo = "styles/images/kitchencopilot_logo_transparent.png"
st.logo(logo, size="medium", link=None, icon_image=None)

st.set_page_config(page_title="Actuals vs. Predicted", layout="wide")
st.title("Actual vs. Predicted Analysis")
st.write("Evaluate prediction accuracy and model performance")


# Form for user input
with st.form("date_form"):
   cols = st.columns([1,1])
   start_date = cols[0].date_input("Pick a start date")
   end_date = cols[1].date_input("Pick an end date") 
   submit_button = st.form_submit_button("Analyze Period")

# Initialize session state for form submission
if 'form_submitted' not in st.session_state:
    st.session_state['form_submitted'] = False

if submit_button:
    # Clear old data first
    if 'analysis_df' in st.session_state:
        del st.session_state['analysis_df']
    
    st.session_state['form_submitted'] = True
    st.session_state['start_date'] = start_date
    st.session_state['end_date'] = end_date

if st.session_state['form_submitted']:
    if 'analysis_df' not in st.session_state:
        start_date = st.session_state['start_date']
        end_date = st.session_state['end_date']

        # Current period
        df = get_actuals_and_predictions(start_date, end_date)
        st.session_state['analysis_df'] = df

                # Previous period for comparison
        period_length = (end_date - start_date).days
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=period_length)
        
        prev_df = get_actuals_and_predictions(prev_start, prev_end)
        st.session_state['previous_df'] = prev_df
        

        # === TOP METRICS SECTION ===
        st.subheader("Performance Metrics")
        st.write("Compare prediction accuracy over the selected period with the previous period.") 

        # Calculate metrics for both
        st.session_state['current_metrics'] = calculate_metrics(df)
        if len(prev_df) > 0:
            st.session_state['previous_metrics'] = calculate_metrics(prev_df)
        else:
            st.session_state['previous_metrics'] = None    

        current = st.session_state['current_metrics']
        previous = st.session_state['previous_metrics']

        col1, col2, col3, col4 = st.columns(4)
        with col1: 
          with st.container(border=True):
              if previous:
                  mae_delta = current['mae'] - previous['mae']
                  st.metric(
                      label="Mean Absolute Error",
                      value=f"{current['mae']:.1f}",
                      delta=f"{mae_delta:+.1f} vs. last period",
                      delta_color="inverse"
                  )
              else:
                  st.metric(
                      label="Mean Absolute Error",
                      value=f"{current['mae']:.1f}",
                      help="No previous period data available"
                  )
        with col2: 
          with st.container(border=True):
              if previous:
                  accuracy_delta = current['accuracy_rate'] - previous['accuracy_rate']
                  st.metric(
                      label="Accuracy Rate",
                      value=f"{current['accuracy_rate']:.1f}%",
                      delta=f"{accuracy_delta:+.1f} vs. last period"
                  )
              else: 
                  st.metric(
                      label="Accuracy Rate",
                      value=f"{current['accuracy_rate']:.1f}%",
                      help="No previous period data available"
                  )
        with col3: 
          with st.container(border=True):
              if previous: 
                  overpred_delta = current['over_predicted'] - previous['over_predicted']
                  st.metric(
                      label="Total Overpredicted",
                      value= f"{current['over_predicted']}",
                      delta=f"{overpred_delta:+} vs. last period",
                      delta_color="inverse"
                  )
              else:
                  st.metric(
                      label="Total Overpredicted",
                      value= f"{current['over_predicted']}",
                      help ="No previous period data available"
                  )

        with col4: 
          with st.container(border=True):
              if previous:
                  underpred_delta = current['under_predicted'] - previous['under_predicted']
                  st.metric(
                      label="Total Underpredicted",
                      value= f"{current['under_predicted']}",
                      delta=f"{underpred_delta:+} vs. last period",
                      delta_color="inverse"
                  )
              else:
                  st.metric(
                      label="Total Underpredicted",
                      value= f"{current['under_predicted']}",
                      help ="No previous period data available"
                  )
        st.divider()

        st.subheader("Actual vs. Predicted Trend")
        # Prepare data for chart
        chart_data = df[['date', 'predicted_meals', 'actual_meals']].copy()
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
            y=chart_data['actual_meals'],
            mode='lines+markers',
            name='Actual Meals',
            line=dict(color='#ff7f0e', width=3)  # Orange
        ))

        st.plotly_chart(fig, use_container_width=True)

        
        st.divider()

        # Format the display dataframe
        st.subheader("Daily Comparison")
        styled_df = apply_custom_styling(df)
        st.dataframe(
            styled_df,
            column_config={
                "date": st.column_config.DateColumn(
                "Date",
                format="DD-MM-YY"
                ),
                "weekday": "Weekday",
                "predicted_meals": "Predicted Meal Count", 
                "actual_meals": "Actual Meal Count",
                "difference": "Waste/Shortage", 
                "pct_error_actual": "% deviation from actual"
            },
            hide_index=True,
            column_order=("date", "weekday", "predicted_meals", "actual_meals", "difference", "pct_error_actual")
        )

        st.divider()


        st.subheader("Model Insights")