"""utils/weather_utils.py — spans three phases of the roadmap in one file,
since the module is small and each phase applies naturally to it:

- Phase 0: characterization tests pinning down two known bugs (no fix yet,
  per team decision — these tests exist to document current behavior so a
  future fix has a clear "before" to diff against).
- Phase 1: pure boundary-value tests for categorize_weather.
- Phase 3: mocked-HTTP happy-path test for get_weather (via `responses`).
"""
import pytest
import responses

from utils.weather_utils import categorize_weather, get_weather
from tests.fixtures.weather_responses import (
    response_missing_daily_key,
    valid_daily_response,
)

pytestmark = pytest.mark.unit


# --- Phase 0: characterization tests for known bugs ---------------------

def test_get_weather_raises_on_unrecognized_type():
    # BUG (characterized, not yet fixed): `type` is only handled for
    # "forecast"/"past" in weather_utils.get_weather — anything else leaves
    # `url` unassigned before it's used in requests.get(), raising
    # UnboundLocalError instead of a clear validation error.
    with pytest.raises(UnboundLocalError):
        get_weather(start_date="2026-07-13", end_date="2026-07-14", type="bogus")


@responses.activate
def test_get_weather_raises_when_response_missing_daily_key():
    # BUG (characterized, not yet fixed): if the Open-Meteo response has no
    # "daily" key (e.g. an out-of-range date request), `weather_df` is never
    # assigned but is still referenced two lines later, raising
    # UnboundLocalError instead of a clear error about the bad response.
    responses.add(
        responses.GET,
        "https://api.open-meteo.com/v1/forecast",
        json=response_missing_daily_key(),
        status=200,
    )

    with pytest.raises(UnboundLocalError):
        get_weather(start_date="2026-07-13", end_date="2026-07-14", type="forecast")


# --- Phase 1: pure boundary-value tests ----------------------------------

@pytest.mark.parametrize(
    "code,expected_label",
    [
        (0, "Sunny"),
        (1, "Cloudy"),
        (3, "Cloudy"),
        (4, "Cloudy"),      # falls through to the unknown-code fallback
        (51, "Rainy"),
        (67, "Rainy"),
        (68, "Cloudy"),     # gap between the rainy ranges -> fallback
        (80, "Rainy"),
        (84, "Rainy"),
        (71, "Snowy"),
        (77, "Snowy"),
        (85, "Snowy"),
        (86, "Snowy"),
        (95, "Stormy"),
        (99, "Stormy"),
        (100, "Cloudy"),    # out of all known ranges -> fallback
        (-1, "Cloudy"),     # negative/unknown -> fallback
    ],
)
def test_categorize_weather_boundaries(code, expected_label):
    _, label = categorize_weather(code)
    assert label == expected_label


# --- Phase 3: mocked-HTTP happy path --------------------------------------

@responses.activate
def test_get_weather_forecast_happy_path():
    responses.add(
        responses.GET,
        "https://api.open-meteo.com/v1/forecast",
        json=valid_daily_response(),
        status=200,
    )

    df = get_weather(start_date="2026-07-13", end_date="2026-07-14", type="forecast")

    assert list(df["weather_condition"]) == ["Sunny", "Rainy"]
    assert list(df["temperature_max"]) == [22.5, 19.0]
    assert df["date"].dt.strftime("%Y-%m-%d").tolist() == ["2026-07-13", "2026-07-14"]


@responses.activate
def test_get_weather_past_hits_archive_endpoint():
    responses.add(
        responses.GET,
        "https://archive-api.open-meteo.com/v1/archive",
        json=valid_daily_response(),
        status=200,
    )

    df = get_weather(start_date="2026-01-01", end_date="2026-01-02", type="past")

    assert len(df) == 2
