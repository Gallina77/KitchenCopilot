import streamlit as st
from sqlalchemy import text
import pandas as pd

# ============================================
# SEED HISTORICAL SALES DATA
# ============================================

# 1. Load CSV

path = "data/raw/sales_data/sales_pp.csv"
df = pd.read_csv(path, sep=";")
print(df.head())

# Clean date format to YYYY-MM-DD string
df['date'] = pd.to_datetime(df['date']).dt.strftime("%Y-%m-%d")

# 2. Build the SQL rows
sql_rows = []
for _, row in df.iterrows():
    # Formats exactly as: ('2025-01-03', 126)
    sql_rows.append(f"('{row['date']}', '{int(row['total_day'])}', '{int(row['veg'])}', '{int(row['non_veg'])}')")

# Join rows with commas for a clean bulk insert
values_string = ",\n".join(sql_rows)


# 3. Create the full INSERT statement
table_name = "actual_sales"
columns = "(date, actual_meals,actual_meals_veg, actual_meals_non_veg)"
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