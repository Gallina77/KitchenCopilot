from utils.db_conn import get_engine 
from sqlalchemy import text

engine = get_engine() 
sql_query="DELETE FROM actual_sales;"
try:
    with engine.begin() as connection:  # Now engine is valid and has .begin()
        connection.execute(text(sql_query))
        print(f"Success: All data in actuals sales database deleted.")
except Exception as e:
    print(f"Database operation failed: {e}")