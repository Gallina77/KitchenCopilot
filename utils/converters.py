from datetime import datetime

def normalize_datetime(date):
    if isinstance(date, datetime):
        print(date.type())
        return date
    else:
        print(date.type())
        return datetime.fromisoformat(date)