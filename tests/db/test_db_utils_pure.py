"""Phase 2 example: DB-adjacent functions in utils/db_utils.py that don't
actually need a connection — they operate purely on a DataFrame already
shaped like a DB query result. Test these with plain fixture DataFrames,
no mocking required at all.
"""
import pytest

from utils.db_utils import calculate_metrics, style_difference
from tests.fixtures.dataframes import build_actuals_vs_predictions_df

pytestmark = pytest.mark.unit


def test_calculate_metrics_basic():
    df = build_actuals_vs_predictions_df(
        [
            {"actual_meals": 100, "final_prediction": 100},  # exact match
            {"actual_meals": 103, "final_prediction": 100},  # under-predicted by 3
            {"actual_meals": 130, "final_prediction": 100},  # under-predicted by 30
        ]
    )

    metrics = calculate_metrics(df)

    assert metrics["mae"] == pytest.approx((0 + 3 + 30) / 3)
    assert metrics["over_predicted"] == 0
    assert metrics["under_predicted"] == 2


def test_calculate_metrics_over_predicted_counts_correctly():
    df = build_actuals_vs_predictions_df(
        [
            {"actual_meals": 80, "final_prediction": 100},
            {"actual_meals": 90, "final_prediction": 100},
        ]
    )
    metrics = calculate_metrics(df)
    assert metrics["over_predicted"] == 2
    assert metrics["under_predicted"] == 0


def test_calculate_metrics_handles_zero_prediction_without_raising():
    # final_prediction == 0 would divide-by-zero in a naive implementation;
    # the real function guards this with `.replace(0, np.nan)`.
    df = build_actuals_vs_predictions_df(
        [{"actual_meals": 5, "final_prediction": 0}]
    )
    metrics = calculate_metrics(df)
    assert metrics["mae"] == 5
    # pct_error is NaN for this row (NaN denominator), and NaN <= anything
    # is always False, so it can't count toward accuracy_rate.
    assert metrics["accuracy_rate"] == 0


def test_calculate_metrics_accuracy_rate_tolerance_is_percentage_points_not_fraction():
    # BUG (characterized, not yet fixed — found while writing this test, not
    # part of the originally-scoped known bugs): `pct_error` inside
    # calculate_metrics is computed on a 0-100 scale (`... * 100`), but
    # `tolerance_pct` defaults to 0.05 and is compared directly against it
    # (`pct_error <= tolerance_pct`) with no rescaling. A "5% tolerance"
    # documented in the docstring actually requires the error to be within
    # 0.05 *percentage points* (i.e. ~0.05% relative error) to count as
    # accurate — an unrealistically tight bar in production. This test
    # pins down the current (buggy) behavior: a 3% real-world error does
    # NOT count as "accurate" under the default tolerance_pct=0.05.
    df = build_actuals_vs_predictions_df(
        [{"actual_meals": 103, "final_prediction": 100}]  # a real 3% error
    )
    metrics = calculate_metrics(df, tolerance_pct=0.05)
    assert metrics["accuracy_rate"] == 0  # would be 100 if the scales matched


@pytest.mark.parametrize("val,expected_color", [(5, "green"), (-5, "red"), (0, "red")])
def test_style_difference(val, expected_color):
    assert style_difference(val) == f"color: {expected_color}"
