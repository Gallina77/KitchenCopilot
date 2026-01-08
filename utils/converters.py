from datetime import datetime
import pandas as pd

def normalize_datetime(date):
    date = pd.to_datetime(date)
    if isinstance(date, datetime):
        return date
    else:
        return datetime.fromisoformat(date)