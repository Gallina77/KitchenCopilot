from pathlib import Path
from sqlalchemy import create_engine, text
data_dir = Path('data')
data_dir.mkdir(exist_ok=True)  # Creates dir if it doesn't exist

print("Starting database initialization...")

# Creates database and tables
db_path = data_dir / 'kitchencopilot.db'
engine = create_engine(f'sqlite:///{db_path}')

#print(f"✓ Data directory ready at: {data_dir}")

with engine.begin() as conn:
    conn.execute(text('CREATE TABLE IF NOT EXISTS holidays '
    '(date DATE, description TEXT, is_bank_holiday BOOLEAN, ' \
    'is_school_break BOOLEAN, is_bridge_day BOOLEAN);'))

    print("✓ Created 'holidays' table")
 
    conn.execute(text('CREATE TABLE IF NOT EXISTS predictions (date DATE PRIMARY KEY, weekday TEXT, month TEXT, ' \
    'day_theme TEXT, temperature_max FLOAT, weather_condition TEXT, is_bank_holiday BOOLEAN, is_bridge_day BOOLEAN, is_school_break BOOLEAN, ' \
    'holiday_desc TEXT, predicted_meals INTEGER, predicted_meals_veg INTEGER, predicted_meals_non_veg INTEGER, prediction_timestamp TIMESTAMP);'))

    print("✓ Created 'predictions' table")

    conn.execute(text('CREATE TABLE IF NOT EXISTS actual_sales(date DATE PRIMARY KEY, actual_meals INTEGER, ' \
    'actual_meals_veg INTEGER, actual_meals_non_veg INTEGER)'))

    print("✓ Created 'actual_sales' table")

    conn.execute(text('ALTER TABLE predictions ADD COLUMN override_meal_prediction INTEGER;'))
    conn.execute(text('ALTER TABLE predictions ADD COLUMN override_reason TEXT;'))
    conn.execute(text('ALTER TABLE predictions ADD COLUMN final_prediction INTEGER'))

print(f"✓ Database initialization complete: {db_path}")