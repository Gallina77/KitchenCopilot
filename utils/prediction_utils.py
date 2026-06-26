import pandas as pd
import joblib
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from utils.paths import MODEL_PATH, FEATURES_PATH
from utils.db_utils import get_empirical_veg_ratio
import math

def get_prediction(new_data):
    # 1. Load model and features from disk
    loaded_model = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(FEATURES_PATH)
    
    # 2. Prepare data
    df_prepared = new_data.copy()
    
    # 3. One-hot encode
    # weekday is dropped: it's perfectly collinear with day_theme (each weekday maps to
    # exactly one theme), so encoding both is redundant - see scripts/train_model.py
    df_prepared = pd.get_dummies(
        df_prepared.drop(columns=['weekday']),
        columns=['month', 'weather_condition', 'day_theme']
    )

    # 4. Add missing columns (ensure all expected features are present)
    for col in feature_columns:
        if col not in df_prepared.columns:
            df_prepared[col] = 0

    # 5. Select and order columns to match training data
    df_prepared = df_prepared[feature_columns]
    
    # 6. Predict (using the model!)
    predictions = loaded_model.predict(df_prepared)
    
    # 7. Return results
    #Add predictions to the original DataFrame
    new_data['predicted_meals'] = np.ceil(predictions)
    new_data['prediction_timestamp'] = datetime.now(timezone.utc)

    # 8. Split total into veg / non-veg using the empirical ratio per theme
    splits = new_data.apply(_split_veg, axis=1, result_type='expand')
    new_data['predicted_meals_veg'] = splits[0]
    new_data['predicted_meals_non_veg'] = splits[1]

    #Return the updated DataFrame
    return new_data


def _split_veg(row):
    theme = row.get('day_theme', 'Unknown')
    veg_r, nonveg_r = get_empirical_veg_ratio(theme)
    total = row['predicted_meals']
    veg = math.ceil(total * veg_r)
    non_veg = int(total) - veg  # ensure sum == total
    return veg, non_veg

