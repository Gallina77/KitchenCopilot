import pandas as pd
from pathlib import Path
import_csv_path = Path("data/raw/sales_data/sales_pp.csv")
export_csv_path = Path("data/raw/sales_data/actual_sales_export.csv")
df = pd.read_csv(import_csv_path, sep=None, engine='python')

# Convert to proper date format
df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y').dt.strftime('%Y-%m-%d')

df.to_csv(export_csv_path, index=False)
