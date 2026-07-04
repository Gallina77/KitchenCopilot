import streamlit as st
from utils.db_conn import get_active_connection_name
# Initialize session state for the toggle if it doesn't exist


#def render_env_badge():
    # Visible reminder of which DB (prod/test) this session is connected to,
    # since switching requires an app restart and is otherwise invisible.
   # is_prod = get_active_connection_name() == "kitchencopilot_db_prod"
  #  if is_prod:
   #     st.sidebar.error("🔴 Connected to PROD database")
  #  else:
     #   st.sidebar.info("🟢 Connected to TEST database")


def render_language_toggle():
  #  render_env_badge()

    # 1. Check URL param first (only on initial load)
    if 'lang' not in st.session_state:
        params = st.query_params
        if "lang" in params:
            url_lang = params["lang"].upper()
            if url_lang in ["EN", "DE"]:
                st.session_state.lang = url_lang
            else:
                st.session_state.lang = "DE"
        else:
            st.session_state.lang = "DE"

    # 2. Render toggle
    is_english = st.sidebar.toggle(
        label="EN" if st.session_state.lang == "EN" else "DE",
        value=(st.session_state.lang == "EN")
    )
    
    
    # 3. Update state and URL if changed
    new_lang = "EN" if is_english else "DE"
    
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.query_params["lang"] = new_lang.lower()
        st.rerun()