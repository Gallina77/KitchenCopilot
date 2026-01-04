import pandas as pd
import joblib
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from utils.paths import MODEL_PATH, FEATURES_PATH

def get_prediction(new_data):
    # 1. Load model and features
    loaded_model = joblib.load(MODEL_PATH)
    expected_features = joblib.load(FEATURES_PATH)
    
    # 2. Prepare data
    df_prepared = new_data.copy()
    
    # 3. One-hot encode
    df_prepared = pd.get_dummies(
        df_prepared,
        columns=['weekday', 'month', 'weather_condition']
    )

    # Define the desired column order
    expected_features = ['is_semester_break','is_bridge_day', 'expected_capacity', 'temperature_max',
                     'weekday_Friday','weekday_Monday','weekday_Thursday','weekday_Tuesday',
                     'weekday_Wednesday','month_April','month_August','month_December','month_February',
                     'month_January','month_July','month_June','month_March','month_May','month_November',
                     'month_October','month_September','weather_condition_Clear','weather_condition_Cloudy',
                     'weather_condition_Rainy','weather_condition_Snowy']
   
    # 4. Add missing columns (using the feature list!)
    for col in expected_features:
        if col not in df_prepared.columns:
            df_prepared[col] = 0

    # 5. Select and order columns (using the feature list!)
    df_prepared = df_prepared[expected_features]
    
    # 6. Predict (using the model!)
    predictions = loaded_model.predict(df_prepared)
    
    # 7. Return results
    #Add predictions to the original DataFrame
    new_data['predicted_meals'] = np.ceil(predictions)
    new_data['prediction_timestamp'] = datetime.now(timezone.utc)

    #Return the updated DataFrame
    return new_data