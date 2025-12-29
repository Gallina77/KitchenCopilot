from pathlib import Path
from sqlalchemy import create_engine, text
import pandas as pd


# Check if data already exists (optional)
print("Starting data seeding...")

# Database connection
data_dir = Path('data')
db_path = data_dir / 'kitchencopilot.db'
engine = create_engine(f'sqlite:///{db_path}')

# Load CSV files
holidays_df = pd.read_csv('data/raw/holidays/holidays_2025_2027.csv')

# Insert into tables
with engine.begin() as conn:
     # Drop existing data
    conn.execute(text('DELETE FROM holidays;'))
    print("✓ Cleared existing holidays data")

    for index, row in holidays_df.iterrows():
        # Convert boolean values to 1/0 for SQLite
        bank_holiday = 1 if row['is_bank_holiday'] else 0
        semester_break = 1 if row['is_semester_break'] else 0
        bridge_day = 1 if row['is_bridge_day'] else 0
    
        conn.execute(text("INSERT INTO holidays (date, description, is_bankHoliday, is_semesterBreak, is_bridgeDay) "
                  f"VALUES ('{row['date']}', '{row['description']}', {bank_holiday}, {semester_break}, {bridge_day});"))

    print("✓ Seeded holidays table")

# Print confirmation messages
print("✓ Data seeding complete!")