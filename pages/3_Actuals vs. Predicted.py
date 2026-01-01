import streamlit as st


logo = "styles/images/kitchencopilot_logo_transparent.png"
st.logo(logo, size="medium", link=None, icon_image=None)

st.set_page_config(page_title="Actuals vs. Predicted", layout="wide")
st.title("Actual vs. Predicted Analysis")
st.write("Evaluate prediction accuracy and model performance")

# Form for user input
with st.form("date_form"):
   cols = st.columns([1, 1, 2])
   minimum = cols[1].date_input("Pick a start date")
   maximum = cols[1].date_input("Pick an end date") 
   submit_button = cols[2].form_submit_button("Analyze Period")
  # start_date = st.date_input('Pick a start date')
  # end_date = st.date_input('Pick an end date')
  # submit_button = st.form_submit_button('Analyze Period')

# === TOP METRICS SECTION ===
st.subheader("Performance Metrics")

col1, col2, col3, col4 = st.columns(4)

#with col1:


st.subheader("Actual vs. Predicted Trend")

st.subheader("Daily Comparison")

st.subheader("Model Insights")