from datetime import datetime
import pandas as pd

def normalize_datetime(date):
    date = pd.to_datetime(date)
    if isinstance(date, datetime):
        print("no change")
        return date
    else:
        print("Change")
        return datetime.fromisoformat(date)