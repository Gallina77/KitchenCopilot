import requests 
import pandas as pd 

url = "https://api.open-meteo.com/v1/forecast"

def get_weather(start_date: str, end_date: str):
    params = {
        "latitude": 50.1330,
        "longitude": 8.6807,
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "Europe/Berlin",
        "daily": ["temperature_2m_max", "weather_code"]
     }
  
    r = requests.get(url, params=params)
    weather_data = r.json()

    # Extract the actual weather data
    if 'daily' in weather_data:
        daily_data = weather_data['daily']
        dates = daily_data['time']
        temperatures = daily_data['temperature_2m_max']
        #WMO codes for conditions (e.g., 0 = Clear, 1-3 = Mostly Clear/Partly Cloudy, 51-65 = Drizzle/Rain).
        weather_codes = ["Clear" if code == 0 else "Partly Cloudy" if 1 <= code <= 3 else "Rainy" for code in daily_data['weather_code']]
        
        # Create a dataframe with the weather data
        weather_df = pd.DataFrame({
            'dates': pd.to_datetime(dates),
            'temperature_max': temperatures,
            'weather_code': weather_codes
        })

        return weather_df