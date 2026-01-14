import streamlit as st  
# Initialize session state for the toggle if it doesn't exist

import streamlit as st

def render_language_toggle():
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