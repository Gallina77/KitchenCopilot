import requests 
import pandas as pd 


def categorize_weather(code):
    if code == 0: return "☀️", "Clear"
    if 1 <= code <= 3: return "⛅", "Cloudy"
    if 51 <= code <= 67 or 80 <= code <= 84: return "🌧️", "Rainy"
    if 71 <= code <= 77 or 85 <= code <= 86: return "❄️", "Snowy"
    if 95 <= code <= 99: return "⛈️", "Stormy"
    return "☁️", "Cloudy" # If code is unknown, show cloudy


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

    # --- Main Processing ---
    if 'daily' in weather_data:
    # 1. Create DataFrame directly from the daily JSON
        weather_df = pd.DataFrame(weather_data['daily'])
    
    # 2. Map icons and text into two new columns
    # .apply(pd.Series) splits the (icon, condition) tuple into columns
    weather_df[['weather_icon', 'weather_condition']] = weather_df['weather_code'].apply(lambda x: pd.Series(categorize_weather(x)))

    # 3. Optional: Convert time to actual datetime objects
    weather_df['date'] = pd.to_datetime(weather_df['time'])
    weather_df["temperature_max"] = weather_df["temperature_2m_max"]

    return weather_df