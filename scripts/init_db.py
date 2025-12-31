from pathlib import Path
from sqlalchemy import create_engine, text
data_dir = Path('data')
data_dir.mkdir(exist_ok=True)  # Creates dir if it doesn't exist

print("Starting database initialization...")

# Creates database and tables
db_path = data_dir / 'kitchencopilot.db'
engine = create_engine(f'sqlite:///{db_path}')

print(f"✓ Data directory ready at: {data_dir}")

with engine.begin() as conn:
    conn.execute(text('CREATE TABLE IF NOT EXISTS holidays '
    '(date DATE, description TEXT, is_bank_holiday BOOLEAN, ' \
    'is_semester_break BOOLEAN, is_bridge_day BOOLEAN);'))

    print("✓ Created 'holidays' table")
 
    conn.execute(text('CREATE TABLE IF NOT EXISTS predictions (date DATE, weekday TEXT, expected_capacity INTEGER, ' \
    'temperature_max FLOAT, weather_condition TEXT, is_bank_holiday BOOLEAN, is_bridge_day BOOLEAN, is_semester_break BOOLEAN, ' \
    'holiday_desc TEXT, predicted_meals INTEGER, prediction_timestamp DATETIME);'))

    print("✓ Created 'predictions' table")

    conn.execute(text('CREATE TABLE IF NOT EXISTS actual_sales(date DATE, actual_meals INTEGER)'))

    print("✓ Created 'actual_sales' table")

print(f"✓ Database initialization complete: {db_path}")