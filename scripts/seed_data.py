from pathlib import Path
from sqlalchemy import create_engine, text
import pandas as pd

print("Starting data seeding...")

# Database connection
data_dir = Path('data')
db_path = data_dir / 'kitchencopilot.db'
engine = create_engine(f'sqlite:///{db_path}')

# Load CSV file
holidays_df = pd.read_csv(
    'data/raw/holidays/holidays_2025_2027.csv',
    dtype={
        'is_bank_holiday': str,
        'is_semester_break': str,
        'is_bridge_day': str
    }
)

# Then convert strings to int
holidays_df['is_bankHoliday'] = holidays_df['is_bank_holiday'].str.strip().eq('TRUE').astype(int)
holidays_df['is_semesterBreak'] = holidays_df['is_semester_break'].str.strip().eq('TRUE').astype(int)
holidays_df['is_bridgeDay'] = holidays_df['is_bridge_day'].str.strip().eq('TRUE').astype(int)

# Insert into database
with engine.begin() as conn:
    # Clear existing data
    conn.execute(text('DELETE FROM holidays;'))
    print("✓ Cleared existing holidays data")
    
    # Insert all rows at once using pandas to_sql
    holidays_df[['date', 'description', 'is_bankHoliday', 'is_semesterBreak', 'is_bridgeDay']].to_sql(
        'holidays',
        conn,
        if_exists='append',
        index=False
    )
    print(f"✓ Seeded {len(holidays_df)} rows into holidays table")

print("✓ Data seeding complete!")