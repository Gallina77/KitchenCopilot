import requests 
import pandas as pd 


def categorize_weather(code):
    if code == 0:
        return "Clear"
    elif 1 <= code <= 3:
        return "Cloudy"
    elif code in range(51, 68) or code in range(80, 83):
        return "Rainy"
    elif code in range(71, 78) or code in range(85, 87):
        return "Snowy"
    elif code in range(95, 100):
        return "Stormy"
    else:
        return "Cloudy"  # Default fallback for any edge cases


def get_weather(start_date: str, end_date: str, type: str):
    params = {
        "latitude": 50.1330,
        "longitude": 8.6807,
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "Europe/Berlin",
        "daily": ["temperature_2m_max", "weather_code"]
     }
    
    if type == "forecast":
        url = "https://api.open-meteo.com/v1/forecast"
    elif type == "past":
        url =  "https://archive-api.open-meteo.com/v1/archive"
    else: 
        url = "unkown"
    r = requests.get(url, params=params)
    weather_data = r.json()

    # Extract the actual weather data
    if 'daily' in weather_data:
        daily_data = weather_data['daily']
        dates = daily_data['time']
        temperature_max = daily_data['temperature_2m_max']
        weather_conditions = [categorize_weather(code) for code in daily_data['weather_code']]

        # Create a dataframe with the weather data
        weather_df = pd.DataFrame({
            'dates': pd.to_datetime(dates),
            'temperature_max': temperature_max,
            'weather_conditions': weather_conditions
        })

        return weather_df