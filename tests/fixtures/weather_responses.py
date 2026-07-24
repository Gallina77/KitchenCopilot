"""Sample Open-Meteo JSON payloads for mocking utils/weather_utils.get_weather."""


def valid_daily_response(dates=None, temps=None, codes=None):
    """A well-formed response containing the 'daily' key get_weather expects."""
    dates = dates or ["2026-07-13", "2026-07-14"]
    temps = temps if temps is not None else [22.5, 19.0]
    codes = codes if codes is not None else [0, 61]
    return {
        "latitude": 50.13,
        "longitude": 8.68,
        "daily": {
            "time": dates,
            "temperature_2m_max": temps,
            "weather_code": codes,
        },
    }


def response_missing_daily_key():
    """What Open-Meteo returns on a malformed/out-of-range request: no 'daily'
    key at all. Reproduces the UnboundLocalError characterized in
    tests/unit/test_weather_utils.py.
    """
    return {
        "latitude": 50.13,
        "longitude": 8.68,
        "reason": "Parameter 'start_date' is out of allowed range",
    }
