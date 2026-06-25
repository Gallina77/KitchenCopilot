from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from utils.db_conn import get_engine 


# ============================================
# SEED HOLIDAYS
# ============================================

# 1. File Path and Data Loading
csv_path = Path("data/raw/sales_data/sales_pp.csv")

if not csv_path.exists():
    print(f"Error: CSV file not found at {csv_path.resolve()}")
    exit(1)

# Read CSV
df = pd.read_csv(csv_path, sep=";")


# 2. Securely Package Data into Parameters
# This maps dataframe rows to a dictionary, isolating it from the SQL text
data_to_insert = [
    {
        "date_val": pd.to_datetime(row['date']).strftime("%Y-%m-%d"), 
        "actual_meals_qty": int(row["total_day"]),
        "actual_meals_veg_qty": int(row["veg"]), 
        "actual_meals_non_veg_qty": int(row["non_veg"])

    }
    for _, row in df.iterrows()
]

# 3. Pure Parameterized SQL Statement (100% Injection Proof)
secure_query = text("""
    INSERT INTO actual_sales (date, actual_meals,actual_meals_veg, actual_meals_non_veg) 
    VALUES (:date_val, :actual_meals_qty, :actual_meals_veg_qty, :actual_meals_non_veg_qty);
""")

# 4. Execute directly via Engine Context Manager

#Spin up the database connection engine
engine = get_engine() 
try:
    with engine.begin() as connection:  # Now engine is valid and has .begin()
        connection.execute(secure_query, data_to_insert)
    print(f"Success: Securely inserted {len(data_to_insert)} rows into the actuals sales database.")
except Exception as e:
    print(f"Database operation failed: {e}")