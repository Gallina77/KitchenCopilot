import json
import streamlit as st


def get_translations(page: str = None):
    lang = st.session_state.get("lang", "DE")
    
    # Always load common
    with open("utils/translations/common.json", "r", encoding="utf-8") as f:
        translations = json.load(f)[lang]
    
    # Merge page-specific if provided
    if page:
        with open(f"utils/translations/{page}.json", "r", encoding="utf-8") as f:
            page_translations = json.load(f)[lang]
        translations.update(page_translations)
    
    return translations


