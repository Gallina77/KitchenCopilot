import pandas as pd
from pathlib import Path
from utils import get_translations
from pydantic import BaseModel
from pandantic import Pandantic
import datetime


COLUMN_ALIASES = {
    "date": ["date", "datum"],
    "actual_meals": ["actual_meals", "total", "gesamt"],
    "actual_meals_veg": ["actual_meals_veg", "veg", "vegetarisch"],
    "actual_meals_non_veg": ["actual_meals_non_veg", "non-veg"],
}

# Define your schema using Pydantic BaseModel
class DataFrameSchema(BaseModel):
    """"""
    date: datetime.date
    actual_meals: int
    actual_meals_veg: int
    actual_meals_non_veg: int


def csv_validation(df):
    ok, message, df = column_validation(df)
    if not ok:
        return False, message, None
    
    ok, message = value_validation(df)
    if not ok:
        return False, message, None
    
    ok, message = sum_validation(df)
    if not ok:
        return False, message, None
    
    return True, None, df

def column_validation(df):
    t = get_translations("import")
    
    original_columns = list(df.columns)
    lowercase_columns = list(df.columns.str.lower())
    
    rename_map = {}
    missing = []
    
    for internal_name in COLUMN_ALIASES:
        accepted_aliases = COLUMN_ALIASES[internal_name]
        found = False
        
        for alias in accepted_aliases:
            if alias in lowercase_columns:
                # Find WHERE it matched, so we can grab the ORIGINAL-cased name
                position = lowercase_columns.index(alias)
                original_name = original_columns[position]
                
                rename_map[original_name] = internal_name
                found = True
        
        if found == False:
            missing.append(internal_name)
    
    if missing:
        message = t["error_csv_missing_columns"] + ": " + ", ".join(missing)
        ok = False
    else:
        df = df.rename(columns=rename_map)
        df = df[list(COLUMN_ALIASES.keys())]
        message = None
        ok = True
    return ok, message, df

    
def value_validation(df):
    #Validation 2: Date and Integers
    validator = Pandantic(schema=DataFrameSchema)

    # Validate with error raising
    try:
        validator.validate(dataframe=df, errors="raise")
        ok=True
        message = None
    except ValueError as e:
        ok = False
        message = e
    
    return ok, message

def sum_validation(df):
    t = get_translations("import")
    
    expected_sum = df["actual_meals_veg"] + df["actual_meals_non_veg"]
    mismatches = df[df["actual_meals"] != expected_sum]
    
    if not mismatches.empty:
        # Report which rows are off, using their original row position
        bad_rows = [str(i) for i in mismatches.index]
        message = t["error_sum_mismatch"] + ": " + ", ".join(bad_rows)
        return False, message
    
    return True, None

