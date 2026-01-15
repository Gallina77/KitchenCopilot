import os
from pathlib import Path
import pandas as pd
import streamlit as st
from anthropic import Anthropic
    
@st.cache_data
def get_llm_insights_for_actuals_vs_predicted(data_json: str, lang: str):

    client = Anthropic(
        api_key=st.secrets["ANTHROPIC_API_KEY"],
    )

    response_language = "German" if st.session_state.lang == "DE" else "English"


    message = client.messages.create(
        max_tokens=800,
        messages=[
            {
                "role": "user",
                "content": "You help kitchen teams review how well their meal predictions performed. "
                    "This data compares past predictions against actual results. "
                    "The data contains dates, weekdays, predicted meals, actual meals, difference, and percentage error. "
                    "Look for meaningful patterns: Are certain weekdays consistently off? "
                    "Do holidays or low-volume days cause problems? Is there a bias in the predictions? "
                    "Only report patterns that are significant and actionable. "
                    "Return your response as a JSON array only. No other text, no markdown, no explanation. "
                    "Each insight should be an object with three fields: "
                    "type (one of: success, info, warning, error), "
                    "title (short label for the insight), "
                    "message (one sentence explanation and one sentence recommendation). "
                    "Use these types: "
                    "success = predictions working well, no action needed. "
                    "info = general observation worth noting. "
                    "warning = 3-5% error or a pattern to watch. "
                    "error = over 5% error, needs attention. "
                    "Return at most 3 insights. Fewer is fine."
                    "If the predictions are working well and there are no clear issues, say so briefly. "
                    "Use simple language for kitchen managers. No jargon."
                    "Return raw JSON only. DO NOT wrap in code fences or markdown."
                    f"Respond in {response_language}."
                    f"Here is the data: {data_json}"
        
            }
        ],
        model="claude-sonnet-4-5-20250929",
    )
    return message.content[0].text

@st.cache_data
def get_llm_planning_insights(data_json: str, lang: str):

    client = Anthropic(
        api_key=st.secrets["ANTHROPIC_API_KEY"],
    )

    response_language = "German" if st.session_state.lang == "DE" else "English"

    message = client.messages.create(
        max_tokens=800,
        messages=[
            {
                "role": "user",
                "content": "You help kitchen teams plan based on meal demand forecasts. "
                    "This data contains future dates, predicted meals, expected capacity, "
                    "utilization percentage, temperature, weather condition, holiday description, "
                    "semester break flag, bridge day flag, and prediction timestamp. "
                    "List ONLY 2-3 inconsistencies or unusual patterns — "
                    "things that don't match expected conditions (weather, holiday, day of week) "
                    "or seem worth verifying. "
                    "Do NOT include daily summaries, recommendations, or risk ratings. "
                    "Keep it brief and simple, no jargon. Use bullet points."
                    f"Respond in {response_language}."
                    f"Here is the data: {data_json}"
        
            }
        ],
        model="claude-sonnet-4-5-20250929",
    )
    return message.content[0].text