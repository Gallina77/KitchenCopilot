import streamlit as st

@st.cache_resource
def get_connection():
    # Create the SQL connection to kitchencopilot_db as specified in your secrets file.
    return st.connection('kitchencopilot_db', type='sql')

# Weekday (English, as returned by dt.day_name()) → theme name
DAY_THEMES = {
    "Monday":    "Sausage",
    "Tuesday":   "Vital",      # likely a "health/light meal" category, common in German canteens
    "Wednesday": "Chicken",
    "Thursday":  "Schnitzel",  # could also translate as "Breaded Cutlet"
    "Friday":    "Fish",
}

# Veg/non-veg split ratio per theme (veg_ratio, non_veg_ratio) — must sum to 1.0
# Source: confirmed portions Mon 30:30, Tue 30:40, Wed 30:40, Thu 30:50, Fri 30:30
THEME_VEG_RATIO = {
    "Sausage":   (0.50, 0.50),  # 30 veg : 30 non-veg
    "Vital":     (0.43, 0.57),  # 30 veg : 40 non-veg
    "Chicken":   (0.43, 0.57),  # 30 veg : 40 non-veg
    "Schnitzel": (0.37, 0.63),  # 30 veg : 50 non-veg
    "Fish":      (0.50, 0.50),  # 30 veg : 30 non-veg
}

def get_empirical_veg_ratio(theme: str) -> tuple[float, float]:
    """Query actual_sales joined to predictions for this theme's historical
    actual_meals_veg/actual_meals_non_veg. Returns (veg_ratio, non_veg_ratio).
    Falls back to THEME_VEG_RATIO[theme] if zero historical rows exist for this theme."""

    sql_query = " SELECT AVG(actual_meals_veg), AVG(actual_meals_non_veg) FROM actual_sales " \
    "JOIN predictions ON actual_sales.date = predictions.date WHERE predictions.day_theme = :theme"

     #If no rows: return THEME_VEG_RATIO.get(theme, (0.5, 0.5))