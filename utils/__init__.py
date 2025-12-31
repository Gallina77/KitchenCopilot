# utils/__init__.py
from .weather_utils import get_weather, categorize_weather
from .db_utils import get_holidays, save_prediction
from .prediction_utils import get_prediction
from .data_preparation_utils import prepare_data

# This allows: from utils import get_weather
