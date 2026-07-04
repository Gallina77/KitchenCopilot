from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from utils.db_conn import get_engine 


# ============================================
# SEED HOLIDAYS
# ============================================

# 1. File Path and Data Loading
csv_path = Path("data/raw/holidays/holidays_2025_2027.csv")

if not csv_path.exists():
    print(f"Error: CSV file not found at {csv_path.resolve()}")
    exit(1)

# Read CSV
df = pd.read_csv(csv_path)


# 2. Securely Package Data into Parameters
# This maps dataframe rows to a dictionary, isolating it from the SQL text
data_to_insert = [
    {
        "date_val": pd.to_datetime(row['date']).strftime("%Y-%m-%d"), 
        "desc_val": row["description"], 
        "is_bank_hol_val": row["is_bank_holiday"], 
        "is_school_break_val": row["is_school_break"], 
        "is_bridge_day_val": row["is_bridge_day"], 

    }
    for _, row in df.iterrows()
]

# 3. Pure Parameterized SQL Statement (100% Injection Proof)
secure_query = text("""
    INSERT INTO holidays (date, description,is_bank_holiday, is_school_break, is_bridge_day) 
    VALUES (:date_val, :desc_val, :is_bank_hol_val, :is_school_break_val, :is_bridge_day_val);
""")

# 4. Execute directly via Engine Context Manager

#Spin up the database connection engine
engine = get_engine() 
try:
    with engine.begin() as connection:  # Now engine is valid and has .begin()
        connection.execute(secure_query, data_to_insert)
    print(f"Success: Securely inserted {len(data_to_insert)} rows into the holidays database.")
except Exception as e:
    print(f"Database operation failed: {e}")
