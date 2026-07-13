"""A tiny synthetic model + feature list, standing in for the real
data/models/*.pkl artifacts so utils/prediction_utils.py tests don't depend
on the actual trained model (which can change independently of this logic).
"""
import numpy as np
from sklearn.linear_model import LinearRegression


def build_synthetic_model_and_features():
    """A model fit on a handful of synthetic rows, plus the feature_columns
    list get_prediction() expects to align its one-hot-encoded input against.
    """
    feature_columns = [
        "temperature_max",
        "month_July",
        "weather_condition_Sunny",
        "day_theme_Sausage",
    ]
    X = np.array(
        [
            [22.0, 1, 1, 1],
            [18.0, 0, 0, 0],
            [25.0, 1, 1, 1],
            [15.0, 0, 0, 0],
        ]
    )
    y = np.array([60, 40, 65, 35])

    model = LinearRegression().fit(X, y)
    return model, feature_columns
