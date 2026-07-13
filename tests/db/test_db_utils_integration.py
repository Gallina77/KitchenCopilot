"""Phase 4 example: a small, deliberately minimal suite of tests that hit
the REAL test-tier Supabase database (mjhequkrufsslyjjofhq). Everything
here is marked `db` and excluded from the default run
(`pytest -m "not db and not llm"`); run explicitly with `pytest -m db`.

Safety: tests/conftest.py forces APP_ENV=test before any test runs, and
utils.db_conn.get_active_connection_name() defaults to the test connection
name — both are exercised directly in tests/unit/test_db_conn.py. These
tests never touch the prod database as a result.

Requires .streamlit/secrets.toml with a working
[connections.kitchencopilot_db_test] block; skips cleanly (not a failure)
when that file isn't present, e.g. on a contributor's machine or a CI run
without the DB secret configured.
"""
import pandas as pd
import pytest
from sqlalchemy import text

from utils import db_conn
from utils.db_utils import get_connection, get_future_predictions, save_prediction

SECRETS_FILE = db_conn.PROJECT_ROOT / ".streamlit" / "secrets.toml"

pytestmark = [
    pytest.mark.db,
    pytest.mark.skipif(
        not SECRETS_FILE.exists(),
        reason="No .streamlit/secrets.toml — test-tier Supabase credentials not configured here.",
    ),
]

# Far-future date reserved for this test only, so it can never collide with
# a real forecast and is trivially identifiable for cleanup.
TEST_DATE = "2099-01-01"


def _delete_test_row(conn):
    with conn.session as session:
        session.execute(text("DELETE FROM predictions WHERE date = :date"), {"date": TEST_DATE})
        session.commit()


@pytest.fixture
def clean_test_prediction_row():
    conn = get_connection()
    _delete_test_row(conn)  # in case a previously-failed run left a row behind
    yield conn
    _delete_test_row(conn)


def test_save_prediction_round_trips_through_get_future_predictions(clean_test_prediction_row):
    df = pd.DataFrame(
        [
            {
                "date": TEST_DATE,
                "weekday": "Thursday",
                "month": "January",
                "day_theme": "Schnitzel",
                "temperature_max": 10.0,
                "weather_condition": "Cloudy",
                "is_bridge_day": False,
                "is_school_break": False,
                "holiday_desc": "",
                "predicted_meals": 80,
                "predicted_meals_veg": 30,
                "predicted_meals_non_veg": 50,
                "predicted_meals_salad": 0,
                "prediction_timestamp": "2026-07-13T08:00:00",
                "override_meal_prediction": None,
                "override_reason": None,
            }
        ]
    )

    ok, err = save_prediction(df)
    assert ok, err

    result = get_future_predictions()
    matching = result[result["date"] == pd.Timestamp(TEST_DATE)]
    assert len(matching) == 1
    assert matching.iloc[0]["final_prediction"] == 80
