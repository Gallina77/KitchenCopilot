import streamlit as st
import pandas as pd
from io import StringIO
from babel.dates import format_date
from utils import csv_validation, get_translations, get_missing_actuals, save_actuals
from components.sidebar import render_language_toggle



# ============================================
# PAGE CONFIG (must be first)
# ============================================

st.set_page_config(page_title="Import Actuals", layout="wide")
#
# ============================================
# 2. RENDER SIDEBAR WIDGETS FIRST
# ============================================
logo = "styles/images/kitchencopilot_logo_transparent.png"
st.logo(logo, size="medium", link=None, icon_image=None) 

# CRITICAL FIX STEP A: Run the toggle first so it can process user clicks
# and save the new active language into st.session_state before we read it.
render_language_toggle() 


# ============================================
# 3. GET TRANSLATIONS (Must be after the toggle)
# ============================================
# CRITICAL FIX STEP B: Now we safely capture the updated language selection 
locale = st.session_state.lang.lower()
t = get_translations("import")
labels = t["display_columns_short"]


# ============================================
# HELPER: load + cast the "missing actuals" dataframe
# ============================================
# Pulled out into its own function so both page-init AND post-save
# refreshes use the exact same casting logic (previously duplicated).
def load_missing_actuals():
    raw_df = get_missing_actuals()

    if raw_df is not None and not raw_df.empty:
        raw_df['date'] = pd.to_datetime(raw_df['date'])
        for col in ['final_prediction', 'predicted_meals_veg', 'predicted_meals_non_veg']:
            if col in raw_df.columns:
                raw_df[col] = raw_df[col].fillna(0).astype(int)
        for col in ['actual_meals', 'actual_meals_veg', 'actual_meals_non_veg']:
            if col in raw_df.columns:
                raw_df[col] = raw_df[col].astype('Int64')

    return raw_df


# ============================================
# INITIALIZE SESSION STATE
# ============================================

if "meals_df" not in st.session_state:
    st.session_state["meals_df"] = load_missing_actuals()


# ============================================
# PAGE TITLE 
# ============================================
st.title(t["page_title"])


# ============================================
# IMPORT AREA
# ============================================

"""
- Accept CSV with columns: `date` (YYYY-MM-DD), `actual_meals` (integer)
- Validate: correct columns present, dates parseable, meals > 0
- Show a preview table before committing
- On confirm: upsert into `actual_sales` (INSERT OR REPLACE)
- Show success count and any skipped/errored rows
"""

st.caption(t["upload_description"])
uploaded_file = st.file_uploader("Browse Files", type="csv")

if uploaded_file is not None:

    dataframe = pd.read_csv(uploaded_file, sep=None, engine='python')

    # FIX: call csv_validation ONCE (previously called twice, and the first
    # call's result was thrown into an `if` check where a tuple is always
    # truthy, so it never actually gated anything).
    result, message, df = csv_validation(dataframe)

    if result:
        # FIX: display and save the RENAMED df returned by csv_validation,
        # not the raw upload (which may still have original/aliased column names).
        st.table(df)
        if st.button(t["save_label"], type="primary", key="upload"):
            is_success, message = save_actuals(df)
            if is_success:
                st.session_state['actuals_saved'] = True

                # FIX: refresh meals_df so newly-imported dates drop out of
                # the "still missing actuals" list below, instead of the
                # manual-edit table silently showing stale data.
                st.session_state["meals_df"] = load_missing_actuals()

                st.rerun()
            else:
                st.error(message)
    else:
        st.error(message)
# success message shown right here, near the CSV upload section
if st.session_state.get('csv_saved', False):
    st.success("Changes saved!")
    st.session_state['csv_saved'] = False


# ============================================
# QUICK SCREEN ENTRY & DETAILED DATA TABLE
# ============================================

st.subheader(t["update_manually"])

if st.session_state["meals_df"] is not None and not st.session_state["meals_df"].empty:
    
    # 1. Generate a completely new temporary copy every single rerun
    display_df = st.session_state["meals_df"].copy()
    
    # 2. This transforms '2026-06-30' -> 'Dienstag, 30. Juni' if current_lang == 'de'
    display_df['date_display'] = pd.to_datetime(display_df['date']).apply(
        lambda d: format_date(d, format='EEEE, dd. MMMM', locale=locale)
    )

    # 2.2. Get the theme translations 
    display_df['day_theme'] = display_df['day_theme'].map(t['day_themes'])

    # 3. Dynamic Column Headers Mapping (using your localized labels object)
    column_configuration = {
        "date_display": st.column_config.TextColumn(  
            label=labels.get("date", "Date"),               
            disabled=True                     
        ),
        "day_theme": st.column_config.TextColumn(label=labels.get("day_theme", "Theme")),
        "final_prediction": st.column_config.NumberColumn(label=labels.get("final_prediction", 
                                                                           "Forecast Total"), format="%d"),
        "predicted_meals_veg": st.column_config.NumberColumn(label=labels.get("predicted_meals_veg", 
                                                                              "Forecast Veg"), format="%d"),
        "predicted_meals_non_veg": st.column_config.NumberColumn(label=labels.get("predicted_meals_non_veg", "Forecast Non-Veg"), format="%d"),
        "actual_meals": st.column_config.NumberColumn(label=labels.get("actual_meals", "Actual Total"), format="%d"),
        "actual_meals_veg": st.column_config.NumberColumn(label=labels.get("actual_meals_veg", "Actual Veg"), format="%d"),
        "actual_meals_non_veg": st.column_config.NumberColumn(label=labels.get("actual_meals_non_veg", "Actual Non-Veg"), format="%d"), 
        "date": None,  # hide the raw datetime column from the editor
    }

    # 4. FIX: The language code inside the key forces Streamlit to blow away the 
    # English cached UI and draw a fresh German one immediately when toggled.
    edited_df = st.data_editor(
        display_df, 
        key=f"meals_editor_v2_{locale}", # Changed name to completely clear old cache
        column_config=column_configuration, 
        column_order=["date_display", "day_theme", "final_prediction", 
                      "predicted_meals_veg", "predicted_meals_non_veg",
                      "actual_meals", "actual_meals_veg", "actual_meals_non_veg"],
        hide_index=True
    )
    #Success message for manual edits shown right here, near the table
    if st.session_state.get('manual_saved', False):
        st.success("Changes saved!")
        st.session_state['manual_saved'] = False
    
    # 5. Save Button logic
    if st.button(t["save_label"], type="primary"):
        # Validate: actual_meals should equal actual_meals_veg + actual_meals_non_veg
        mismatch_mask = edited_df['actual_meals'] != (
            edited_df['actual_meals_veg'] + edited_df['actual_meals_non_veg']
        )

        if mismatch_mask.any():
            bad_rows = edited_df.loc[mismatch_mask, ['date', 'actual_meals', 'actual_meals_veg', 'actual_meals_non_veg']]
            st.error(t["error_msg_validation_meals_count"])
            st.dataframe(bad_rows)
        else:
            original_df = st.session_state["meals_df"]
            cols_to_check = ['actual_meals', 'actual_meals_veg', 'actual_meals_non_veg']

            # Use a sentinel so NA-vs-NA compares as "unchanged" instead of "unknown"
            SENTINEL = -9999
            orig_filled = original_df[cols_to_check].fillna(SENTINEL)
            edited_filled = edited_df[cols_to_check].fillna(SENTINEL)

            changed_mask = (edited_filled != orig_filled).any(axis=1)
            changed_rows = edited_df.loc[changed_mask, ['date'] + cols_to_check]

            for col in cols_to_check:
                if col in edited_df.columns:
                    st.session_state["meals_df"][col] = edited_df[col]

            is_success, message = save_actuals(changed_rows)
            if is_success:
                st.session_state['actuals_saved'] = True

                # FIX: refresh here too, for consistency with the CSV path above.
                st.session_state["meals_df"] = load_missing_actuals()

                st.rerun()
            else:
                st.error(message)

else:
    st.error(t["error_message_no_data"])