import streamlit as st
import pandas as pd
import json
from babel.dates import format_date
import plotly.graph_objects as go
from datetime import timedelta, datetime, date 
from utils import get_actuals_and_predictions, apply_custom_styling, calculate_metrics
from utils.llm_insights import get_llm_insights_for_actuals_vs_predicted
from utils.translations_utils import get_translations
from components.sidebar import render_language_toggle

logo = "styles/images/kitchencopilot_logo_transparent.png"
st.logo(logo, size="medium", link=None, icon_image=None)

st.set_page_config(page_title="Actuals vs. Predicted", layout="wide")
render_language_toggle()
t = get_translations("actuals")
daily_comparison_columns = t["daily_comparison_columns"]
st.title(t["actuals_title"])
st.write(t["actuals_subtitle"])

# Calculated default dates: Last full week (Mon-Fri) 
weekday = date.today().weekday()
default_start = date.today() - timedelta(days=weekday+7)
default_end = default_start + timedelta(days=4)

# Initialize session state for dates
if 'start_date' not in st.session_state:
    st.session_state['start_date'] = default_start
if 'end_date' not in st.session_state:
    st.session_state['end_date'] = default_end

# Initialize session state for form submission
if 'form_submitted' not in st.session_state:
    st.session_state['form_submitted'] = False

# Form for user input
with st.form("date_form"):
    cols = st.columns([1,1])
    start_date = cols[0].date_input(t["start_date_label"], value=st.session_state['start_date'])
    end_date = cols[1].date_input(t["end_date_label"], value=st.session_state['end_date']) 
    submit_button = st.form_submit_button(t["analyze_period_button"], type="primary")

# Handle form submission
if submit_button:
    # Clear old data first
    if 'analysis_df' in st.session_state:
        del st.session_state['analysis_df']
    if 'previous_df' in st.session_state:
        del st.session_state['previous_df']
    if 'current_metrics' in st.session_state:
        del st.session_state['current_metrics']
    if 'previous_metrics' in st.session_state:
        del st.session_state['previous_metrics']
    
    st.session_state['form_submitted'] = True
    st.session_state['start_date'] = start_date
    st.session_state['end_date'] = end_date

# Only show content if form has been submitted
if st.session_state['form_submitted']:
    
    # DATA LOADING SECTION - only runs if data not already loaded
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

        # Calculate metrics for both periods
        st.session_state['current_metrics'] = calculate_metrics(df)
        if len(prev_df) > 0:
            st.session_state['previous_metrics'] = calculate_metrics(prev_df)
        else:
            st.session_state['previous_metrics'] = None
    
    # DISPLAY SECTION - runs every time, reads from session state
    df = st.session_state['analysis_df']
    prev_df = st.session_state['previous_df']
    current = st.session_state['current_metrics']
    previous = st.session_state['previous_metrics']

    # === TOP METRICS SECTION ===
    st.subheader("Performance Metrics")
    st.write("Compare prediction accuracy over the selected period with the previous period.") 

    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        with st.container(border=True):
            if previous:
                mae_delta = current['mae'] - previous['mae']
                st.metric(
                    label=t["metrics"]["mae_label"],
                    value=f"{current['mae']:.1f}",
                    delta=f"{mae_delta:+.1f} {t['metrics']['delta_description']}",
                    delta_color="inverse"
                )
            else:
                st.metric(
                    label=t["metrics"]["mae_label"],
                    value=f"{current['mae']:.1f}",
                    help=t["metrics"]["metrics_error"]
                )
    with col2: 
        with st.container(border=True):
            if previous:
                accuracy_delta = current['accuracy_rate'] - previous['accuracy_rate']
                st.metric(
                    label=t["metrics"]["accuracy_label"],
                    value=f"{current['accuracy_rate']:.1f}%",
                    delta=f"{accuracy_delta:+.1f} {t['metrics']['delta_description']}"
                )
            else: 
                st.metric(
                    label=t["metrics"]["accuracy_label"],
                    value=f"{current['accuracy_rate']:.1f}%",
                    help=t["metrics"]["metrics_error"]  
                )
    with col3: 
        with st.container(border=True):
            if previous: 
                overpred_delta = current['over_predicted'] - previous['over_predicted']
                st.metric(
                    label=t["metrics"]["overprediction_label"],
                    value=f"{current['over_predicted']}",
                    delta=f"{overpred_delta:+} {t['metrics']['delta_description']}",
                    delta_color="inverse"
                )
            else:
                st.metric(
                    label=t["metrics"]["overprediction_label"],
                    value=f"{current['over_predicted']}",
                    help=t["metrics"]["metrics_error"]
                )

    with col4: 
        with st.container(border=True):
            if previous:
                underpred_delta = current['under_predicted'] - previous['under_predicted']
                st.metric(
                    label=t["metrics"]["underprediction_label"],
                    value=f"{current['under_predicted']}",
                    delta=f"{underpred_delta:+} {t['metrics']['delta_description']}",
                    delta_color="inverse"
                )
            else:
                st.metric(
                    label=t["metrics"]["underprediction_label"],
                    value=f"{current['under_predicted']}",
                    help=t["metrics"]["metrics_error"]
                )
    st.divider()

    st.subheader(t["chart_title"])
    if not df.empty:

        chart_data = df[['date', 'final_prediction', 'actual_meals',
                          'predicted_meals_veg', 'actual_meals_veg',
                          'predicted_meals_non_veg', 'actual_meals_non_veg']].copy()
        locale = st.session_state.lang.lower()

        chart_data['date'] = chart_data['date'].apply(
            lambda d: format_date(d, format='EEE MM/dd', locale=locale)
        )
        chart_data = chart_data.set_index('date')

        fig = go.Figure()

        # --- Total ---
        fig.add_trace(go.Scatter(
            x=chart_data.index, y=chart_data['final_prediction'],
            mode='lines+markers', name=t["chart_label_predicted"],
            line=dict(color='#1f77b4', width=3, dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=chart_data.index, y=chart_data['actual_meals'],
            mode='lines+markers', name=t["chart_label_actuals"],
            line=dict(color='#1f77b4', width=3)
        ))

        # --- Veg ---
        fig.add_trace(go.Scatter(
            x=chart_data.index, y=chart_data['predicted_meals_veg'],
            mode='lines+markers', name=t["chart_label_predicted_veg"],
            line=dict(color='#2ca02c', width=2, dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=chart_data.index, y=chart_data['actual_meals_veg'],
            mode='lines+markers', name=t["chart_label_actuals_veg"],
            line=dict(color='#2ca02c', width=2)
        ))

        # --- Non-Veg ---
        fig.add_trace(go.Scatter(
            x=chart_data.index, y=chart_data['predicted_meals_non_veg'],
            mode='lines+markers', name=t["chart_label_predicted_non_veg"],
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=chart_data.index, y=chart_data['actual_meals_non_veg'],
            mode='lines+markers', name=t["chart_label_actuals_non_veg"],
            line=dict(color='#ff7f0e', width=2)
        ))

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error(t["no_data"])

    st.subheader(t["error_chart_title"])
    if not df.empty:
        error_data = df[['date', 'difference', 'difference_veg', 'difference_non_veg']].copy()
        locale = st.session_state.lang.lower()
        error_data['date'] = error_data['date'].apply(
            lambda d: format_date(d, format='EEE MM/dd', locale=locale)
        )

        fig_error = go.Figure()
        fig_error.add_trace(go.Bar(
            x=error_data['date'], y=error_data['difference'],
            name=t["error_chart_label_total"], marker_color='#1f77b4'
        ))
        fig_error.add_trace(go.Bar(
            x=error_data['date'], y=error_data['difference_veg'],
            name=t["error_chart_label_veg"], marker_color='#2ca02c'
        ))
        fig_error.add_trace(go.Bar(
            x=error_data['date'], y=error_data['difference_non_veg'],
            name=t["error_chart_label_non_veg"], marker_color='#ff7f0e'
        ))

        fig_error.update_layout(
            barmode='group',
            yaxis_title=t["error_chart_y_axis"]
        )
        fig_error.add_hline(y=0, line_width=1, line_color='gray')

        st.plotly_chart(fig_error, use_container_width=True)

    else:
        st.error(t["no_data"])
    st.divider()
    

    # Format the display dataframe
    st.subheader(t["daily_comparison_title"])
    df = st.session_state['analysis_df'].copy()

    # An empty result comes back with object-dtype columns (nothing to infer
    # a numeric type from), and .round() below rejects object dtype outright
    # - guard the same way the two charts above already do for empty ranges.
    if not df.empty:
        locale = st.session_state.lang.lower()
        df['date'] = df['date'].apply(
            lambda d: format_date(d, format='EE, dd.MMMM', locale=locale)
        )

        table_columns = [
            'date', 'final_prediction', 'actual_meals', 'pct_error',
            'predicted_meals_veg', 'actual_meals_veg', 'pct_error_veg',
            'predicted_meals_non_veg', 'actual_meals_non_veg', 'pct_error_non_veg'
        ]
        table_df = df[table_columns].copy()
        for col in ['pct_error', 'pct_error_veg', 'pct_error_non_veg']:
            table_df[col] = (table_df[col] * 100).round(0)

        styled_df = apply_custom_styling(table_df)

        st.dataframe(
            styled_df,
            column_config={
                "date": st.column_config.TextColumn(label=daily_comparison_columns["date"], width="medium"),
                "final_prediction": st.column_config.NumberColumn(label=daily_comparison_columns["final_prediction"], width="small"),
                "actual_meals": st.column_config.NumberColumn(label=daily_comparison_columns["actual_meals"], width="small"),
                "pct_error": st.column_config.NumberColumn(label=daily_comparison_columns["pct_error"], width="small"),
                "predicted_meals_veg": st.column_config.NumberColumn(label=daily_comparison_columns["predicted_meals_veg"], width="small"),
                "actual_meals_veg": st.column_config.NumberColumn(label=daily_comparison_columns["actual_meals_veg"], width="small"),
                "pct_error_veg": st.column_config.NumberColumn(label=daily_comparison_columns["pct_error_veg"], width="small"),
                "predicted_meals_non_veg": st.column_config.NumberColumn(label=daily_comparison_columns["predicted_meals_non_veg"], width="small"),
                "actual_meals_non_veg": st.column_config.NumberColumn(label=daily_comparison_columns["actual_meals_non_veg"], width="small"),
                "pct_error_non_veg": st.column_config.NumberColumn(label=daily_comparison_columns["pct_error_non_veg"], width="small"),
            },
            width='stretch',
            hide_index=True
        )
    else:
        st.error(t["no_data"])


    st.divider()

    st.subheader(t["llm_title"])
    with st.spinner(t["spinner_message"]):
        response = get_llm_insights_for_actuals_vs_predicted(df.to_json(),st.session_state.lang)

    # Strip code fences
    response = response.strip()
    if response.startswith("```"):
        lines = response.split("\n")
        response = "\n".join(lines[1:-1])

    try:
        insights = json.loads(response)
        for insight in insights:
            if insight['type'] == 'success':
                st.success(f"**{insight['title']}** — {insight['message']}")
            elif insight['type'] == 'info':
                st.info(f"**{insight['title']}** — {insight['message']}")
            elif insight['type'] == 'warning':
                st.warning(f"**{insight['title']}** — {insight['message']}")
            elif insight['type'] == 'error':
                st.error(f"**{insight['title']}** — {insight['message']}")
    except json.JSONDecodeError:
        st.warning(t["json_error"])
        st.markdown(response)