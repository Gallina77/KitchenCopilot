from datetime import date, datetime
import pandas as pd
from pandas.testing import assert_frame_equal
import pytest
from utils.data_preparation_utils import prepare_data, merge_and_clean_holidays, compute_date_range_and_weather_type, build_data_features, merge_weather, clean_holidays_data

#Run only tests with a particular label: pytest -m unit
pytestmark = pytest.mark.unit

@pytest.fixture
def fixed_start_and_days():
    return "2026-02-06", 7

@pytest.fixture
def dataframe(): 
    data = {'date': pd.to_datetime(['2026-02-06','2026-02-09']), 
        'weekday': ['Friday', 'Monday'],
        'month':['February', 'February'],
        'day_theme':['Fish', 'Sausage']
        }
    return pd.DataFrame(data)


def test_calculate_end_date_without_weekends(fixed_start_and_days):
    start_date, number_of_days = fixed_start_and_days
    today = datetime.strptime("2026-02-06", '%Y-%m-%d').date()
    start, end, weather_type,business_days = compute_date_range_and_weather_type(start_date, number_of_days, today)
    assert end == "2026-02-16"

def test_start_date_on_weekend():
    start_date = "2026-07-11"
    number_of_days = 2
    today = datetime.strptime("2026-02-06", '%Y-%m-%d').date()
    start, end, weather_type,business_days = compute_date_range_and_weather_type(start_date, number_of_days, today)
    assert start == "2026-07-13"
    assert end == "2026-07-14"

def test_today_is_none(mocker, fixed_start_and_days): 
    start_date, number_of_days = fixed_start_and_days
    mock_datetime = mocker.patch("utils.data_preparation_utils.datetime")
    mock_datetime.today.return_value.date.return_value = date(2026, 3, 1)
    mock_datetime.strptime.side_effect = datetime.strptime  # needed again, same reason as before

    start, end, weather_type,business_days = compute_date_range_and_weather_type(start_date, number_of_days, today=None)
    assert weather_type == "past"

def test_weather_type_is_forecast_for_future_end_date(fixed_start_and_days):
    start_date, number_of_days = fixed_start_and_days
    today = datetime.strptime("2026-02-06", '%Y-%m-%d').date()
    start, end, weather_type,business_days = compute_date_range_and_weather_type(start_date, number_of_days, today)
    assert weather_type == "forecast"

def test_weather_type_is_past_for_past_end_date(fixed_start_and_days):
    start_date, number_of_days = fixed_start_and_days
    today = datetime.strptime("2026-03-03", '%Y-%m-%d').date()
    start, end, weather_type,business_days = compute_date_range_and_weather_type(start_date, number_of_days, today)
    assert weather_type == "past"

def test_weather_type_is_forecast_for_end_date_is_today(fixed_start_and_days):
    start_date, number_of_days = fixed_start_and_days
    today = datetime.strptime("2026-02-16", '%Y-%m-%d').date()
    start, end, weather_type,business_days = compute_date_range_and_weather_type(start_date, number_of_days, today)
    assert weather_type == "forecast"

def test_business_days_with_one_day():
    start_date = "2026-02-16"
    number_of_days = 1
    today = datetime.strptime("2026-02-16", '%Y-%m-%d').date()
    start, end, weather_type, business_days = compute_date_range_and_weather_type(start_date, number_of_days, today)
    assert business_days == ['2026-02-16 00:00:00']

def test_build_data_features_adds_weekday_month_and_theme_columns(dataframe):
    business_days = (['2026-02-06', '2026-02-09'])
    df = build_data_features(business_days)
    df_mock = dataframe
    #Check that left and right DataFrame are equal.
    assert_frame_equal(df_mock, df)

def test_build_data_features_raises_on_invalid_date_string():
    business_days = ['not-a-date']
    with pytest.raises(ValueError):
        build_data_features(business_days)

def test_build_data_features_raises_on_weekend_date():
    with pytest.raises(ValueError, match="Mon–Fri"):
        build_data_features(['2026-02-08'])  # Sunday

def test_merge_weather_left_join_keeps_all_original_rows_and_fills_missing():
    df = pd.DataFrame({'date': ['2026-02-06', '2026-02-07']})
    weather_df = pd.DataFrame({
        'date': ['2026-02-06'],
        'weather_icon': ['sun'],
        'temperature_max': [10],
        'weather_condition': ['clear']
    })
    result = merge_weather(df, weather_df)

    assert len(result) == 2  # left join keeps both rows
    assert result.loc[result['date'] == '2026-02-07', 'weather_icon'].isna().all()

def test_clean_holidays_data_normalizes_date_and_keeps_bool_flags():
    holidays = pd.DataFrame({
        'date': ['2026-06-04', '2026-06-05'],  # as Supabase might return before parsing
        'is_school_break': [False, False],
        'is_bridge_day': [0, 1]
    })
    result = clean_holidays_data(holidays)

    assert pd.api.types.is_datetime64_any_dtype(result['date'])
    assert result['is_bridge_day'].tolist() == [False, True]

