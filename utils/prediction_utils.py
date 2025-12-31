import pandas as pd
import joblib
from pathlib import Path

def get_prediction(new_data):
    # Get absolute path to model
    current_file = Path(__file__)  # /path/to/utils/prediction_utils.py
    project_root = current_file.parent.parent  # /path/to/KüchenKompass
    model_path = project_root / 'data' / 'models' / 'random_forest_model.pkl'

    # Load the model
    loaded_model = joblib.load(model_path)

    #Prepare the input data (feature engineering)
    df_prepared = new_data.copy()

    #One Hot Encode
    weekday_dummies = pd.get_dummies(df_prepared['weekday'], prefix='weekday')
    month_dummies = pd.get_dummies(df_prepared['month'], prefix='month')
    weather_dummies = pd.get_dummies(df_prepared['weather_condition'], prefix='weather_condition')
    
    df_prepared = pd.concat([df_prepared, weekday_dummies, month_dummies, weather_dummies], axis=1)
    df_prepared = df_prepared.drop(['date', 'holiday_desc', 'weekday', 'month', 'weather_condition'], axis=1)

    # But the model expects ALL 12 months
    all_months = ['month_January', 'month_February', 'month_March', 'month_April', 
              'month_May', 'month_June', 'month_July', 'month_August',
              'month_September', 'month_October', 'month_November', 'month_December']

    # Add missing columns with zeros
    for month in all_months:
        if month not in df_prepared.columns:
            df_prepared[month] = 0

    all_weather_conditions = ["Clear", "Cloudy", "Rainy", "Snowy"]

    for condition in all_weather_conditions
        if condition not in df_prepared.columns: 
            df_prepared[condition] = 0

    # Define the desired column order
    desired_order = ['is_semester_break','is_bridge_day', 'expected_capacity', 'temperature_max',
                     'meal_count','weekday_Friday','weekday_Monday','weekday_Thursday','weekday_Tuesday',
                     'weekday_Wednesday','month_April','month_August','month_December','month_February',
                     'month_January','month_July','month_June','month_March','month_May','month_November',
                     'month_October','month_September','weather_condition_Clear','weather_condition_Cloudy',
                     'weather_condition_Rainy','weather_condition_Snowy']

    # Use the loaded model to make predictions with the re-ordered dataframe
    predictions = loaded_model.predict(df_prepared[desired_order])
    

    #Add predictions to the original DataFrame
    new_data['predicted_meals'] = predictions

    #Return the updated DataFrame
    return new_data
 
    


