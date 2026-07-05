import os
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import text

from utils.day_themes import DAY_THEMES


def pytest_configure(config):
    # Force the test suite onto the dedicated CI-only Postgres DB, regardless
    # of the developer's local .env APP_ENV setting, so automated runs never
    # touch prod or the manual dev/QA test DB (see utils/db_conn.py).
    os.environ["APP_ENV"] = "ci"


# Monday-Friday of the current week, matching get_future_predictions()'s own
# definition of "future" (date >= start of this week), so seeded predictions
# always show up as future regardless of which day of the week the suite runs.
_TODAY = date.today()
_MONDAY = _TODAY - timedelta(days=_TODAY.weekday())
SEED_DATES = [_MONDAY + timedelta(days=i) for i in range(5)]
SEED_WEEKDAYS = list(DAY_THEMES.keys())  # Monday..Friday
SEED_THEMES = list(DAY_THEMES.values())


@pytest.fixture(scope="session", autouse=True)
def seed_test_data():
    """Seed the CI-only DB with a known dataset once per test session, and
    empty it again afterwards - this database is dedicated to automated runs,
    so owning the tables outright (rather than juggling sentinel rows) is
    simplest and safe."""
    from utils.db_conn import get_engine  # deferred so APP_ENV=ci (set above) is honored

    engine = get_engine()

    def _clear(conn):
        conn.execute(text("DELETE FROM predictions"))
        conn.execute(text("DELETE FROM actual_sales"))
        conn.execute(text("DELETE FROM holidays"))

    holiday_rows = [
        {
            "date": SEED_DATES[0],
            "description": "Seed Holiday",
            "is_bank_holiday": True,
            "is_school_break": False,
            "is_bridge_day": False,
        }
    ]

    actual_sales_rows = []
    prediction_rows = []
    for i, (d, weekday, theme) in enumerate(zip(SEED_DATES, SEED_WEEKDAYS, SEED_THEMES)):
        veg = 40 + i
        non_veg = 60 + i
        actual_sales_rows.append({
            "date": d,
            "actual_meals": veg + non_veg,
            "actual_meals_veg": veg,
            "actual_meals_non_veg": non_veg,
        })

        predicted_veg = 38 + i
        predicted_non_veg = 57 + i
        prediction_rows.append({
            "date": d,
            "weekday": weekday,
            "month": d.strftime("%B"),
            "day_theme": theme,
            "temperature_max": 20.0,
            "weather_condition": "Clear",
            "is_bridge_day": False,
            "is_school_break": False,
            "holiday_desc": "Seed Holiday" if i == 0 else None,
            "predicted_meals": predicted_veg + predicted_non_veg,
            "predicted_meals_veg": predicted_veg,
            "predicted_meals_non_veg": predicted_non_veg,
            "prediction_timestamp": datetime.now(timezone.utc),
            "override_meal_prediction": None,
            "override_reason": None,
            "final_prediction": predicted_veg + predicted_non_veg,
        })

    holiday_insert = text("""
        INSERT INTO holidays (date, description, is_bank_holiday, is_school_break, is_bridge_day)
        VALUES (:date, :description, :is_bank_holiday, :is_school_break, :is_bridge_day)
    """)
    actual_sales_insert = text("""
        INSERT INTO actual_sales (date, actual_meals, actual_meals_veg, actual_meals_non_veg)
        VALUES (:date, :actual_meals, :actual_meals_veg, :actual_meals_non_veg)
    """)
    prediction_insert = text("""
        INSERT INTO predictions (
            date, weekday, month, day_theme, temperature_max, weather_condition,
            is_bridge_day, is_school_break, holiday_desc, predicted_meals,
            predicted_meals_veg, predicted_meals_non_veg, prediction_timestamp,
            override_meal_prediction, override_reason, final_prediction
        ) VALUES (
            :date, :weekday, :month, :day_theme, :temperature_max, :weather_condition,
            :is_bridge_day, :is_school_break, :holiday_desc, :predicted_meals,
            :predicted_meals_veg, :predicted_meals_non_veg, :prediction_timestamp,
            :override_meal_prediction, :override_reason, :final_prediction
        )
    """)

    with engine.begin() as conn:
        # Self-healing: clears out anything left behind by a previous run that
        # crashed before its teardown ran, before seeding fresh data.
        _clear(conn)
        conn.execute(holiday_insert, holiday_rows)
        conn.execute(actual_sales_insert, actual_sales_rows)
        conn.execute(prediction_insert, prediction_rows)

    try:
        yield
    finally:
        with engine.begin() as conn:
            _clear(conn)
