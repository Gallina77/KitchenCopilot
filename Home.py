import streamlit as st
from components.components import hero_section, journey_step, feature_card, roadmap_card, footer_section


# Page configuration
st.set_page_config(
    page_title="KitchenCopilot - Meal Demand Forecasting",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load external CSS
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles/css/main.css")

logo = "styles/images/kitchencopilot_logo_transparent.png"
st.logo(logo, size="medium", link=None, icon_image=None)


# Hero Section
st.markdown(hero_section(), unsafe_allow_html=True)


# System Status
st.header("System Status")
st.caption("Real-time overview of your forecasting system")

col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.metric(
            label="Model Status",
            value="Active",
            delta="Last trained: Dec 28, 2025"
        )

with col2:
    with st.container(border=True):
        st.metric(
            label="Last Prediction",
            value="Today, 06:00",
            delta="Jan 1 - Jan 7, 2026"
        )

with col3:
    with st.container(border=True):
        st.metric(
            label="Weather API",
            value="Connected",
            delta="OpenWeatherMap active"
        )

with col4:
    with st.container(border=True):
        st.metric(
            label="Database",
            value="Ready",
            delta="SQLite operational"
        )

st.divider()

# What is KitchenCopilot
st.info("""
**What is KitchenCopilot?**

KitchenCopilot helps cafeteria managers predict daily meal demand by combining historical 
sales data with real-time environmental factors. The system reduces food waste and improves 
operational efficiency by providing accurate forecasts based on weather conditions, holidays, 
and capacity planning.
""")

st.divider()


# How to Use the System
st.header("How to Use the System")
st.caption("Detailed walkthrough for each step of the process")

tab1, tab2, tab3, tab4 = st.tabs(["PREPARE", "PREDICT", "TRACK", "IMPORT"])

with tab1:
    st.subheader("Step 1: Prepare Your Forecast")
    st.write("""
    Navigate to the Prepare page and select your forecast start date and period (up to 7 days). 
    The system automatically fetches weather forecasts and checks for holidays in Hessen. Then 
    enter expected daily capacity. The ML model combines this with weather data, weekday patterns, 
    and holiday information to forecast meal demand.
    """)

with tab2:
    st.subheader("Step 2: Generate Predictions")
    st.write("""
    On the Prediction page, review the prepared forecast data including dates, weather conditions, 
    and holiday information. The system displays your predictions with interactive visualizations 
    showing expected meal demand for each working day. You can export the results to Excel for 
    further analysis or sharing with your team.
    """)

with tab3:
    st.subheader("Step 3: Track Performance")
    st.write("""
    Use the Actuals page to compare predicted vs actual meal counts. This helps validate model 
    accuracy and identify improvement opportunities. Review performance metrics, analyze trends 
    over time, and download comparison reports that show how well the forecasts matched reality.
    """)

with tab4:
    st.subheader("Step 4: Import Actual Sales")
    st.write("""
    Upload actual sales data through the Import page to build your historical database and enable 
    performance tracking. This data is stored in the SQLite database and used to calculate 
    accuracy metrics, identify patterns, and can be used for future model retraining to improve 
    forecast quality over time.
    """)

st.divider()

# Key Features
st.header("Key Features")
st.caption("Everything you need for accurate meal demand forecasting")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        feature_card(
            "bi-robot",
            "Automated Feature Engineering",
            "The system automatically enriches your predictions with weather forecasts from OpenWeatherMap and holiday information for Hessen. Weekends and bank holidays are excluded from predictions."
        ),
        unsafe_allow_html=True
    ) 
    
    st.markdown(
        feature_card(
            "bi-speedometer",
            "Performance Tracking",
            "Compare actual vs predicted meals with exportable Excel reports. Track model accuracy over time and identify patterns in forecast performance."
        ),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        feature_card(
            "bi-clipboard-pulse",
            "Interactive Dashboard",
            "Streamlit-based interface for generating predictions with custom date ranges. Visualize forecasts with interactive charts and export results for further analysis."
        ),
        unsafe_allow_html=True
    )
    
    st.markdown(
        feature_card(
            "bi-database",
            "Data Persistence",
            "SQLite database stores all predictions and actual sales data for historical analysis. Build a comprehensive record of forecasting performance over time."
        ),
        unsafe_allow_html=True
    )

st.divider()

# Prediction Factors
st.header("Prediction Factors")
st.caption("The machine learning model considers multiple factors when generating forecasts")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<i class="bi bi-calendar-week"></i> <b>Calendar Information</b>', unsafe_allow_html=True)
    st.markdown("""
    - Day of the week
    - Month of the year
    - Public holidays in Hessen
    - Semester breaks and bridge days
    """)

with col2:
    st.markdown('<i class="bi bi-cloud-sun"></i> <b>Weather Conditions</b>', unsafe_allow_html=True)
    st.markdown("""
    - Temperature
    - Weather description
    - Precipitation likelihood
    - 7-day forecasts
    """)

with col3:
    st.markdown('<i class="bi bi-gear-wide"></i> <b>Operational Data</b>', unsafe_allow_html=True)
    st.markdown("""
    - Expected daily capacity
    - Historical sales patterns
    - Weekday trends
    """)

st.divider()

# Roadmap
st.header("What's Next for KitchenCopilot")
st.caption("Exciting features currently in development")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        roadmap_card(
            "Coming Soon", 
            "#856404", 
            "#fff3cd", 
            "bi-fork-knife", 
            "Menu Planning Integration",
            "Learn how different meal offerings affect demand. Optimize your menu strategy based on historical preferences and patterns."
        ), 
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        roadmap_card(
            "Planned", 
            "#004085", 
            "#e7f3ff", 
            "bi-bicycle", 
            "Automated Scheduling",
            "Hands-free daily forecasts delivered automatically. Integrate seamlessly with your workflow and save valuable time."
        ), 
        unsafe_allow_html=True
    )

st.divider()

# Help Section
st.header("Need Help?")

with st.expander("Frequently Asked Questions"):
    st.markdown("#### Understanding the Workflow")
    st.markdown("""
    - **Prepare:** Set your forecast timeframe and let the system fetch weather data
    - **Predict:** Enter capacity and generate demand forecasts for working days only
    - **Track:** Import actual sales to compare against predictions
    - **Improve:** Use performance insights to refine capacity planning
    """)
    
    st.markdown("#### What Gets Excluded")
    st.markdown("""
    - Weekends (Saturday and Sunday) are automatically filtered out
    - Public holidays in Hessen are excluded from predictions
    - Semester breaks and bridge days are marked in the holiday calendar
    """)
    
    st.markdown("#### Understanding Your Data")
    st.markdown("""
    - Predictions are stored in the SQLite database with timestamps
    - Actual sales can be imported through the Import page
    - Excel exports include all features used for each prediction
    """)
    
    st.markdown("#### Troubleshooting")
    st.markdown("""
    - If weather data fails to load, check your OpenWeatherMap API key in secrets.toml
    - Ensure your start date is within the 7-day forecast window
    - Database issues? Try reinitializing with scripts/init_db.py
    - Contact support if the model status shows as inactive
    """)

st.divider()

# Footer
st.markdown(footer_section(), unsafe_allow_html=True)