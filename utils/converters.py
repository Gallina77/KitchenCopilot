from datetime import datetime

def normalize_datetime(date):
    if isinstance(date, datetime):
        return date
    else:
        return datetime.fromisoformat(date)