import streamlit as st

# Title of the app
pages = {
    "Home": [
        st.Page("home.py", title="Home", icon="🏠")],

    "Prediction": [
        st.Page("prepare.py", title="Prepare your data", icon="📅"),
        st.Page("prediction.py", title="Get Prediction", icon="🔮"),
    ],
    "Actual vs Prediction": [
        st.Page("history.py", title="View History", icon="📊"),
        st.Page("import.py", title="Import Data", icon="⬆️"),
    ],
}

pg = st.navigation(pages)
pg.run()