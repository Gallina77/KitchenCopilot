"""
Train the meal-demand Random Forest model on real historical sales data.

This is the first training run on actual sales (data/raw/sales_data/sales_pp.csv,
49 usable business days, Apr 1 - Jun 15 2026) rather than the synthetic data the
previous model was trained on. Predicts TOTAL meals only - the veg/non-veg split
is a separate, non-model concern (see utils/db_utils.get_empirical_veg_ratio).

Run from the project root: python scripts/train_model.py
"""
import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from utils.day_themes import DAY_THEMES
from utils.weather_utils import get_weather
from utils.paths import MODEL_PATH, FEATURES_PATH, METADATA_PATH, PROJECT_ROOT

SALES_CSV = PROJECT_ROOT / "data" / "raw" / "sales_data" / "sales_pp.csv"
HOLIDAYS_CSV = PROJECT_ROOT / "data" / "raw" / "holidays" / "holidays_2025_2027.csv"
HOLDOUT_DAYS = 10  # temporal holdout, never random - see Phase 4 design notes


def load_sales_data() -> pd.DataFrame:
    df = pd.read_csv(SALES_CSV, sep=";")
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%y")
    df["total_meals"] = df["total_day"]
    df["weekday"] = df["date"].dt.day_name()
    df["month"] = df["date"].dt.month_name()
    df["day_theme"] = df["weekday"].map(DAY_THEMES)
    return df[["date", "weekday", "month", "day_theme", "total_meals"]]


def attach_weather(df: pd.DataFrame) -> pd.DataFrame:
    start = df["date"].min().strftime("%Y-%m-%d")
    end = df["date"].max().strftime("%Y-%m-%d")
    weather_df = get_weather(start_date=start, end_date=end, type="past")
    weather_df["date"] = pd.to_datetime(weather_df["date"])
    return df.merge(weather_df[["date", "temperature_max", "weather_condition"]], on="date", how="left")


def attach_holidays(df: pd.DataFrame) -> pd.DataFrame:
    holidays = pd.read_csv(HOLIDAYS_CSV)
    holidays["date"] = pd.to_datetime(holidays["date"])
    holidays = holidays.rename(columns={"is_school_break": "is_semester_break"})
    df = df.merge(
        holidays[["date", "is_semester_break", "is_bridge_day"]],
        on="date",
        how="left",
    )
    df["is_semester_break"] = df["is_semester_break"].fillna(False).astype(bool)
    df["is_bridge_day"] = df["is_bridge_day"].fillna(False).astype(bool)
    return df


def build_training_frame() -> pd.DataFrame:
    df = load_sales_data()
    df = attach_weather(df)
    df = attach_holidays(df)
    if df["temperature_max"].isna().any() or df["weather_condition"].isna().any():
        missing = df[df["temperature_max"].isna() | df["weather_condition"].isna()]["date"].tolist()
        raise ValueError(f"Missing weather data for dates: {missing}")
    return df


def main():
    print("Loading and enriching training data...")
    df = build_training_frame()
    print(f"Training rows: {len(df)}")

    # Temporal split - last HOLDOUT_DAYS rows are the test set, never shuffled
    df = df.sort_values("date").reset_index(drop=True)
    train_df = df.iloc[:-HOLDOUT_DAYS]
    test_df = df.iloc[-HOLDOUT_DAYS:]

    # weekday and day_theme are perfectly collinear (each weekday maps to exactly one theme) -
    # encoding both would add 10 redundant columns for the same 5 categories of information.
    # Keep day_theme only - more business-meaningful, and halves the redundant feature count
    # which matters a lot with only ~40 training rows.
    encoded = pd.get_dummies(df.drop(columns=["weekday"]), columns=["month", "weather_condition", "day_theme"])
    feature_columns = [c for c in encoded.columns if c not in ("date", "total_meals")]

    X_train = encoded.loc[train_df.index, feature_columns]
    y_train = train_df["total_meals"]
    X_test = encoded.loc[test_df.index, feature_columns]
    y_test = test_df["total_meals"]

    print(f"Train: {len(X_train)} rows, Test (holdout, most recent {HOLDOUT_DAYS} days): {len(X_test)} rows")

    # Naive baseline for context: predicting the training mean for every holdout row
    baseline_pred = np.full(len(y_test), y_train.mean())
    baseline_mae = mean_absolute_error(y_test, baseline_pred)
    print(f"Naive baseline (predict train mean) MAE: {baseline_mae:.2f}")

    # Conservative hyperparameters for ~40 rows: unconstrained RF (max_depth=None) will
    # essentially memorize individual training rows rather than learn generalizable patterns.
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=4,
        min_samples_leaf=3,
        random_state=0,
        oob_score=True,
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)
    mape = float(np.mean(np.abs((y_test - predictions) / y_test.replace(0, np.nan))))

    print(f"OOB score: {model.oob_score_:.3f}")
    print(f"Holdout MAE:  {mae:.2f}  (vs. naive baseline {baseline_mae:.2f})")
    print(f"Holdout RMSE: {rmse:.2f}")
    print(f"Holdout MAPE: {mape:.1%}")
    print(f"Holdout R^2:  {r2:.3f}")
    print("Note: metrics computed on only 10 holdout rows - expect high variance, "
          "treat as a rough signal, not a precise benchmark.")

    # Atomic write - write to .tmp, then rename, so a crash mid-write never corrupts the live model
    model_tmp = MODEL_PATH.with_suffix(".pkl.tmp")
    features_tmp = FEATURES_PATH.with_suffix(".pkl.tmp")
    joblib.dump(model, model_tmp)
    joblib.dump(feature_columns, features_tmp)
    model_tmp.replace(MODEL_PATH)
    features_tmp.replace(FEATURES_PATH)
    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved feature columns to {FEATURES_PATH}")

    metadata = {
        "number_of_features": len(feature_columns),
        "training_timestamp": datetime.now().isoformat(),
        "training_row_count": len(df),
        "holdout_row_count": len(test_df),
        "baseline_mae": mae,
        "baseline_rmse": rmse,
        "baseline_mape": mape,
        "feature_columns": feature_columns,
        "data_source": str(SALES_CSV.relative_to(PROJECT_ROOT)),
        "trained_on_real_data": True,
    }
    metadata_tmp = METADATA_PATH.with_suffix(".json.tmp")
    with open(metadata_tmp, "w") as f:
        json.dump(metadata, f, indent=4)
    metadata_tmp.replace(METADATA_PATH)
    print(f"Saved metadata to {METADATA_PATH}")


if __name__ == "__main__":
    main()
