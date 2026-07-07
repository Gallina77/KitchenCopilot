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
# Pulled into its own function so page-init AND post-save refreshes
# share the exact same casting logic (previously duplicated inline).
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

st.caption(t["upload_description"])
st.markdown(t["csv_import_instructions"])
uploaded_file = st.file_uploader(t["browse_files_label"], type="csv")

if uploaded_file is not None:

    try:
        dataframe = pd.read_csv(uploaded_file, sep=None, engine='python')
    except Exception as e:
        print(f"CSV read failed: {e}")
        dataframe = None
        st.error(t["error_csv_unreadable"])

    if dataframe is not None:
        # FIX: call csv_validation ONCE. Previously it was called twice, and the
        # first call's 3-tuple result was used in an `if` check — a non-empty
        # tuple is always truthy in Python, so that check never actually gated
        # anything; it just wasted a redundant validation call.
        result, message, df = csv_validation(dataframe)

        if result:
            # FIX: display and save the RENAMED df returned by csv_validation,
            # not the raw upload — `dataframe` may still have original/aliased
            # column names (e.g. "Datum", "Gesamt") that downstream code
            # (save_actuals, etc.) doesn't expect.
            st.table(df)
            if st.button(t["save_label"], type="primary", key="upload"):
                is_success, message = save_actuals(df)
                if is_success:
                    # FIX: refresh meals_df so newly-imported dates drop out of
                    # the "still missing actuals" list below, instead of the
                    # manual-edit table silently showing stale data.
                    st.session_state["meals_df"] = load_missing_actuals()

                    # Dedicated flag for THIS section's success message. It is
                    # intentionally NOT cleared here — per your preference, it
                    # should stay visible until the next CSV save overwrites it
                    # (which happens naturally, since this line runs again on
                    # the next successful save).
                    st.session_state["csv_saved"] = True
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.error(message)

# Shown right here, near the upload section — stays visible across reruns
# until the next successful CSV save (no auto-clear).
if st.session_state.get("csv_saved", False):
    st.success(t["csv_save_success"])

# ============================================
# QUICK SCREEN ENTRY & DETAILED DATA TABLE
# ============================================

st.subheader(t["update_manually"])
st.caption(t["manual_update_instructions"])

if st.session_state["meals_df"] is not None and not st.session_state["meals_df"].empty:
    
    # 1. Generate a completely new temporary copy every single rerun
    display_df = st.session_state["meals_df"].copy()
    
    # 2. This transforms '2026-06-30' -> 'Dienstag, 30. Juni' if current_lang == 'de'
    display_df['date_display'] = pd.to_datetime(display_df['date']).apply(
        lambda d: format_date(d, format='EE, dd. MMMM', locale=locale)
    )

    # 2.2. Get the theme translations 
    display_df['day_theme'] = display_df['day_theme'].map(t['day_themes'])

    # 3. Dynamic Column Headers Mapping (using your localized labels object)
    # Only the actual_* columns are editable - date/theme/forecast columns
    # are read-only context, not something a manual entry should change.
    column_configuration = {
        "date_display": st.column_config.TextColumn(
            label=labels.get("date", "Date"),
            disabled=True
        ),
        "day_theme": st.column_config.TextColumn(label=labels.get("day_theme", "Theme"), disabled=True),
        "final_prediction": st.column_config.NumberColumn(label=labels.get("final_prediction",
                                                                           "Forecast Total"), format="%d", disabled=True),
        "predicted_meals_veg": st.column_config.NumberColumn(label=labels.get("predicted_meals_veg",
                                                                              "Forecast Veg"), format="%d", disabled=True),
        "predicted_meals_non_veg": st.column_config.NumberColumn(label=labels.get("predicted_meals_non_veg", "Forecast Non-Veg"), format="%d", disabled=True),
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

    # Shown right here, near the manual-edit table — stays visible across
    # reruns until the next successful manual save (no auto-clear).
    if st.session_state.get("manual_saved", False):
        st.success(t["manual_save_success"])

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

            is_success, message = save_actuals(changed_rows)
            if is_success:
                # FIX: refresh meals_df from the database, same as the CSV
                # path above, so both save flows behave consistently.
                st.session_state["meals_df"] = load_missing_actuals()

                # Dedicated flag for THIS section — not auto-cleared, stays
                # until the next successful manual save.
                st.session_state["manual_saved"] = True
                st.rerun()
            else:
                st.error(message)

else:
    st.error(t["error_message_no_data"])