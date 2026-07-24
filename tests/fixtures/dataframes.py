"""Builder functions for the DataFrame shapes utils/db_utils.py works with.

Each builder takes optional overrides so a test only has to spell out the
columns it actually cares about; everything else gets a sane default.
"""
import pandas as pd


def build_actuals_vs_predictions_df(rows=None):
    """Rows shaped like utils.db_utils.get_actuals_and_predictions()'s output
    (post-JOIN, pre-derived-columns) — just actual_meals/final_prediction,
    which is all utils.db_utils.calculate_metrics needs.
    """
    if rows is None:
        rows = [
            {"actual_meals": 100, "final_prediction": 100},
            {"actual_meals": 120, "final_prediction": 100},
            {"actual_meals": 80, "final_prediction": 100},
        ]
    return pd.DataFrame(rows)


def build_prediction_row(**overrides):
    """A single row shaped like the DataFrame utils.db_utils.save_prediction
    expects (one row per date, matching its `columns` list)."""
    row = {
        "date": "2026-07-13",
        "weekday": "Monday",
        "month": "July",
        "day_theme": "Sausage",
        "temperature_max": 22.5,
        "weather_condition": "Sunny",
        "is_bridge_day": False,
        "is_school_break": False,
        "holiday_desc": "",
        "predicted_meals": 60,
        "predicted_meals_veg": 30,
        "predicted_meals_non_veg": 30,
        "predicted_meals_salad": 0,
        "prediction_timestamp": "2026-07-06T08:00:00",
        "override_meal_prediction": None,
        "override_reason": None,
    }
    row.update(overrides)
    return row


def build_predictions_df(rows=None):
    if rows is None:
        rows = [build_prediction_row()]
    return pd.DataFrame(rows)


def build_actual_sales_row(**overrides):
    row = {
        "date": "2026-07-13",
        "actual_meals": 58,
        "actual_meals_veg": 28,
        "actual_meals_non_veg": 30,
        "actual_meals_salad": 4.5,
    }
    row.update(overrides)
    return row


def build_actual_sales_df(rows=None):
    if rows is None:
        rows = [build_actual_sales_row()]
    return pd.DataFrame(rows)
