import streamlit as st
from datetime import datetime
from components.home import hero_section, journey_step, feature_card, roadmap_card, footer_section
from components.sidebar import render_language_toggle
from utils.home_utils import load_model_metadata, check_database_status, check_weather_api_status, get_last_prediction_info
from utils.translations_utils import get_translations   


# Page configuration
st.set_page_config(
    page_title="Küchenkompass - Meal Demand Forecasting",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

render_language_toggle()
t = get_translations("home")
status = t["system_status"]
howto = t["how_to_use"]
features = t["features"]
help_t = t["help"]
pred = t["prediction_factors"]




# Load external CSS
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles/css/main.css")

logo = "styles/images/kitchencopilot_logo_transparent.png"
st.logo(logo, size="medium", link=None, icon_image=None)


# Hero Section
st.markdown(hero_section(t), unsafe_allow_html=True)

# System Status
st.header(status["header"])
st.caption(status["subtitle"])

col1, col2, col3, col4 = st.columns(4)

# Fetch status with error handling
@st.cache_data(ttl=60)
def get_all_status():
    """Fetch all status checks with error handling"""
    statuses = {}
    try:
        statuses['model'] = load_model_metadata()
    except Exception as e:
        st.error(f"t['errors']['loading_data']: {e}")
        statuses['model'] = None
    
    try:
        statuses['prediction'] = get_last_prediction_info()
    except Exception as e:
        st.error(f"t['errors']['loading_data']: {e}")
        statuses['prediction'] = None
    
    try:
        statuses['api'] = check_weather_api_status()
    except Exception as e:
        st.error(f"t['errors']['connecting_weather']: {e}")
        statuses['api'] = False
    
    try:
        statuses['db'] = check_database_status()
    except Exception as e:
        st.error(f"t['errors']['connecting_database']: {e}")
        statuses['db'] = False
    
    return statuses

statuses = get_all_status()

with col1:
    with st.container(border=True):
        model_timestamp = statuses['model']
        if model_timestamp:
            st.metric(
                label=status['model_label'],
                value=status['model_active'],
                delta=status['model_last_trained'] + f" {model_timestamp.strftime('%d %b %Y')}"
            )
        else:
            st.metric(
                label=status['model_label'],
                value=status['model_not_trained'],
                delta=status['model_train_delta'], delta_color="inverse"
            )

with col2:
    with st.container(border=True):
        last_prediction = statuses['prediction']
        if last_prediction: 
            st.metric(
                label=status["prediction_label"],
                value=last_prediction['timestamp'].strftime('%b, %d'),
                delta=f"for: {last_prediction['start_date'].strftime('%b, %d')} - {last_prediction['end_date'].strftime('%b, %d')}"
            )
        else:
            st.metric(
                label=status["prediction_label"],
                value=status["prediction_failed"],
                delta=status["prediction_date_missing"], delta_color="inverse"
            ) 

with col3:
    with st.container(border=True):
        api_status = statuses['api']
        if api_status: 
            st.metric(
                label=status["weather_label"],
                value=status["weather_connected"],
                delta=status["weather_active"]
            )
        else: 
            st.metric(
                label=status["weather_label"],
                value=status["weather_failed"],
                delta=status["weather_not_active"], delta_color="inverse"
            )   

with col4:
    with st.container(border=True):
        db_status = statuses['db']
        if db_status: 
            st.metric(
                label=status["database_label"],
                value=status["database_ready"],
                delta=status["database_operational"]
            )
        else: 
            st.metric(
                label=status["database_label"],
                value=status["database_not_ready"],
                delta=status["database_not_operational"], delta_color="inverse"
            )

st.divider()

# What is KitchenCopilot
st.info(f"""
**{t["what_is"]["title"]}**

{t["what_is"]["text"]}
""")

st.divider()


# How to Use the System
st.header(howto["header"])
st.caption(howto["subtitle"])

tab1, tab2, tab3, tab4 = st.tabs(list(howto["tabs"].values())
)

with tab1:
    st.subheader(howto["step1_title"])
    st.write(f"""{howto["step1_text"]}""")

with tab2:
    st.subheader(howto["step2_title"])
    st.write(f"""{howto["step2_text"]}""")

with tab3:
    st.subheader(howto["step3_title"])
    st.write(f"""{howto["step3_text"]}""")

with tab4:
    st.subheader(howto["step4_title"])
    st.write(f"""{howto["step4_text"]}""")

st.divider()

# Key Features
st.header(features["header"])
st.caption(features["subtitle"])    
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        feature_card(
            "bi-robot",
            features["automated_title"],
            features["automated_text"]
        ),
        unsafe_allow_html=True
    ) 
    
    st.markdown(
        feature_card(
            "bi-speedometer",
            features["performance_title"],
            features["performance_text"]
        ),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        feature_card(
            "bi-clipboard-pulse",
            features["dashboard_title"],
            features["dashboard_text"]
        ),
        unsafe_allow_html=True
    )
    
    st.markdown(
        feature_card(
            "bi-database",
            features["persistence_title"],
            features["persistence_text"]
        ),
        unsafe_allow_html=True
    )

st.divider()

# Prediction Factors
st.header(pred["header"])
st.caption(pred["subtitle"])

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f'<i class="bi bi-calendar-week"></i> <b>{pred["calendar_title"]}</b>', unsafe_allow_html=True)
    st.markdown("\n".join(f"- {item}" for item in pred["calendar_items"]))

with col2:
    st.markdown(f'<i class="bi bi-cloud-sun"></i> <b>{pred["weather_title"]}</b>', unsafe_allow_html=True)
    st.markdown("\n".join(f"- {item}" for item in pred["weather_items"]))   
with col3:
    st.markdown(f'<i class="bi bi-gear-wide"></i> <b>{pred["operational_title"]}</b>', unsafe_allow_html=True)
    st.markdown("\n".join(f"- {item}" for item in pred["operational_items"]))

st.divider()

# Roadmap
st.header(t["roadmap"]["header"])
st.caption(t["roadmap"]["subtitle"])

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        roadmap_card(
            t["roadmap"]["coming_soon"], 
            "primary",
            "bi bi-cup-hot", 
            t["roadmap"]["menu_title"],
            t["roadmap"]["menu_text"]
        ), 
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        roadmap_card(
            t["roadmap"]["planned"], 
            "success",
            "bi bi-bicycle", 
            t["roadmap"]["scheduling_title"],
            t["roadmap"]["scheduling_text"]
        ), 
        unsafe_allow_html=True
    )


st.divider()

# Help Section
st.header(help_t["header"])

with st.expander(help_t["faq_title"]):
    st.markdown(f"#### {help_t['workflow_title']}")
    lines = [f"- **{item['label']}:** {item['text']}" for item in help_t["workflow_items"]]
    st.markdown("\n".join(lines))


    st.markdown(f"#### {help_t['exclusions_title']}")
    st.markdown("\n".join(f"- {item}" for item in help_t["exclusions_items"]))

    st.markdown(f"#### {help_t['data_title']}")
    st.markdown("\n".join(f"- {item}" for item in help_t["data_items"]))

    st.markdown(f"#### {help_t['troubleshooting_title']}")
    st.markdown("\n".join(f"- {item}" for item in help_t["troubleshooting_items"])) 
 
st.divider()

# Footer
st.markdown(footer_section(), unsafe_allow_html=True)