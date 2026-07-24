"""Phase 3 example: DB-touching functions tested against a mocked
connection instead of a real database — fast and credential-free, verifies
the SQL/params the code constructs without proving the SQL is valid against
real Postgres (that's what the small db-marked suite in
test_db_utils_integration.py is for).
"""
import pytest

from utils.db_utils import save_prediction
from tests.fixtures.dataframes import build_predictions_df, build_prediction_row

pytestmark = pytest.mark.unit


def test_save_prediction_upserts_and_commits(mock_st_connection):
    df = build_predictions_df()

    ok, err = save_prediction(df)

    assert ok is True
    assert err is None
    mock_st_connection.session.execute.assert_called_once()
    mock_st_connection.session.commit.assert_called_once()

    sql_text, records = mock_st_connection.session.execute.call_args.args
    assert "INSERT INTO predictions" in str(sql_text)
    assert "ON CONFLICT (date) DO UPDATE" in str(sql_text)
    assert records[0]["day_theme"] == "Sausage"


def test_save_prediction_uses_override_as_final_prediction_when_present(mock_st_connection):
    df = build_predictions_df(
        [build_prediction_row(predicted_meals=60, override_meal_prediction=45, override_reason="Staff shortage")]
    )

    save_prediction(df)

    _, records = mock_st_connection.session.execute.call_args.args
    assert records[0]["final_prediction"] == 45


def test_save_prediction_returns_error_tuple_on_db_failure(mock_st_connection):
    mock_st_connection.session.execute.side_effect = Exception("connection reset")

    ok, err = save_prediction(build_predictions_df())

    assert ok is False
    assert err == "connection reset"
