# utils/__init__.py
from .weather_utils import get_weather, categorize_weather
from .db_utils import find_table, get_holidays
from .prediction_utils import get_prediction, save_dataframe

# This allows: from utils import get_weather
