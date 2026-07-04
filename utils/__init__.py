# utils/__init__.py
from .weather_utils import get_weather, categorize_weather
from .db_utils import get_holidays, save_prediction, get_future_predictions, get_actuals_and_predictions, apply_custom_styling, calculate_metrics, get_missing_actuals, save_actuals
from .prediction_utils import get_prediction, split_veg_non_veg
from .data_preparation_utils import prepare_data, render_badges
from .home_utils import load_model_metadata, check_database_status, check_weather_api_status, get_last_prediction_info
from .converters import normalize_datetime  
from .llm_insights import get_llm_insights_for_actuals_vs_predicted, get_llm_planning_insights
from .translations_utils import get_translations
from .import_utils import csv_validation
# This allows: from utils import get_weather


