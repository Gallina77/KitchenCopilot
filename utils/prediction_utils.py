import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
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
    
    # But the model expects ALL 12 months
    all_months = ['month_January', 'month_February', 'month_March', 'month_April', 
              'month_May', 'month_June', 'month_July', 'month_August',
              'month_September', 'month_October', 'month_November', 'month_December']


    df_prepared = pd.concat([df_prepared, weekday_dummies, month_dummies, weather_dummies], axis=1)
    df_prepared = df_prepared.drop(['date', 'holiday_desc', 'weekday', 'month', 'weather_condition'], axis=1)
    
    # Add missing columns with zeros
    for month in all_months:
        if month not in df_prepared.columns:
            df_prepared[month] = 0


    print(df_prepared.head(20))

    # Use the loaded model to make predictions
    result = loaded_model.predict(df_prepared)
    

    #Add predictions to the DataFrame
    #Return the updated DataFrame
 

def save_dataframe(updated_df):
    pass
    


get_prediction
