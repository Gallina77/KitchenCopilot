import pandas as pd
import joblib
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from utils.paths import MODEL_PATH, FEATURES_PATH

def get_prediction(new_data):
    # 1. Load model and features from disk
    loaded_model = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(FEATURES_PATH)
    
    # 2. Prepare data
    df_prepared = new_data.copy()
    
    # 3. One-hot encode
    df_prepared = pd.get_dummies(
        df_prepared,
        columns=['weekday', 'month', 'weather_condition']
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

    #Return the updated DataFrame
    return new_data