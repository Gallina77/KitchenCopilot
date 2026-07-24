from datetime import datetime
import pytest
from utils.converters import normalize_datetime

#Run only tests with a particular label: pytest -m unit
pytestmark = pytest.mark.unit


def test_normalize_datetime_isoformat():
    date_str = "2024-06-15T12:30:00"
    normalized = normalize_datetime(date_str)
    assert normalized.year == 2024
    assert normalized.month == 6
    assert normalized.day == 15
    assert normalized.hour == 12
    assert normalized.minute == 30


def test_normalize_datetime_date_only_string():
    normalized = normalize_datetime("2024-06-15")
    assert normalized == datetime(2024, 6, 15)


def test_normalize_datetime_passthrough_datetime_object():
    dt = datetime(2024, 6, 15, 8, 0)
    assert normalize_datetime(dt) == dt


def test_normalize_datetime_unparseable_string_raises():
    with pytest.raises(Exception):
        normalize_datetime("not a date")
