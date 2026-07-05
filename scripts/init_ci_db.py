import os
from sqlalchemy import text
from utils.db_conn import get_engine

# ============================================
# INIT CI DATABASE
# One-time schema bootstrap for the Postgres database dedicated to automated
# test runs (tests/conftest.py). Run manually once against a freshly
# provisioned, empty database - never invoked by pytest itself.
#
# Column set mirrors what the app actually reads/writes today
# (utils/db_utils.py, scripts/seed_holidays.py) rather than the retired
# scripts/init_db.py SQLite schema.
# ============================================

os.environ["APP_ENV"] = "ci"

print("Starting CI database initialization...")

engine = get_engine()

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS holidays (
            date DATE,
            description TEXT,
            is_bank_holiday BOOLEAN,
            is_school_break BOOLEAN,
            is_bridge_day BOOLEAN
        )
    """))
    print("Created 'holidays' table")

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS actual_sales (
            date DATE PRIMARY KEY,
            actual_meals INTEGER,
            actual_meals_veg INTEGER,
            actual_meals_non_veg INTEGER
        )
    """))
    print("Created 'actual_sales' table")

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS predictions (
            date DATE PRIMARY KEY,
            weekday TEXT,
            month TEXT,
            day_theme TEXT,
            temperature_max FLOAT,
            weather_condition TEXT,
            is_bridge_day BOOLEAN,
            is_school_break BOOLEAN,
            holiday_desc TEXT,
            predicted_meals INTEGER,
            predicted_meals_veg INTEGER,
            predicted_meals_non_veg INTEGER,
            prediction_timestamp TIMESTAMP,
            override_meal_prediction INTEGER,
            override_reason TEXT,
            final_prediction INTEGER
        )
    """))
    print("Created 'predictions' table")

print("CI database initialization complete.")
