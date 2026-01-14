import json
import streamlit as st


def get_translations():
    with open("utils/translations.json", "r", encoding="utf-8") as f:
        translations = json.load(f)

    lang = st.session_state.get("lang", "DE")
    return translations[lang]


