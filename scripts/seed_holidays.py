import streamlit as st
from sqlalchemy import text
import pandas as pd

# ============================================
# SEED HOLIDAYS
# ============================================

# 1. Load CSV

path = "data/raw/holidays/holidays_2025_2027.csv"
df = pd.read_csv(path)

# Clean date format to YYYY-MM-DD string
df['date'] = pd.to_datetime(df['date']).dt.strftime("%Y-%m-%d")

# 2. Build the SQL rows
sql_rows = []
for _, row in df.iterrows():
    # Formats exactly as: ('2025-01-03', 126)
    sql_rows.append(f"('{row['date']}', '{row['description']}', '{row['is_bank_holiday']}','{row['is_school_break']}', '{row['is_bridge_day']}')")

# Join rows with commas for a clean bulk insert
values_string = ",\n".join(sql_rows)


# 3. Create the full INSERT statement
table_name = "holidays"
columns = "(date, description,is_bank_holiday, is_school_break, is_bridge_day)"
    # Construct complete SQL Statement
insert_query = f"""
    INSERT INTO {table_name} {columns} 
    VALUES 
    {values_string};
    """

conn = st.connection('kitchencopilot_db', type='sql')
with conn.session as session:
        session.execute(text(insert_query))
        session.commit()

print("Load complete")