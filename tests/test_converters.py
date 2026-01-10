import pytest
from utils.converters import normalize_datetime

def test_always_passes():
    assert True

def test_normalize_datetime_isoformat():
    date_str = "2024-06-15T12:30:00"
    normalized = normalize_datetime(date_str)
    assert normalized.year == 2024
    assert normalized.month == 6
    assert normalized.day == 15
    assert normalized.hour == 12
    assert normalized.minute == 30  