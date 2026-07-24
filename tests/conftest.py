import os
from unittest.mock import MagicMock

import pytest


def pytest_configure(config):
    # Force the test suite onto the test Postgres DB, regardless of the
    # developer's local .env APP_ENV setting, so tests can never touch prod.
    os.environ["APP_ENV"] = "test"


@pytest.fixture
def frozen_today():
    """Freeze "today" for tests that branch on datetime.now()/.today(), e.g.
    utils.data_preparation_utils.prepare_data's past-vs-forecast decision.
    Usage: `def test_x(frozen_today): frozen_today("2026-07-13")`.
    """
    from freezegun import freeze_time

    frozen = None

    def _freeze(date_str):
        nonlocal frozen
        frozen = freeze_time(date_str)
        return frozen.start()

    yield _freeze

    if frozen is not None:
        frozen.stop()


@pytest.fixture
def mock_st_connection(mocker):
    """A MagicMock shaped like the object utils.db_utils.get_connection()
    returns (st.connection(..., type='sql')): `.query()` for reads,
    `.session` as a context manager for writes. Patches get_connection in
    every place it's already been imported (utils.db_utils, and re-exported
    from utils/__init__.py), and clears its @st.cache_resource cache so no
    mock leaks into a later test.
    """
    conn = MagicMock()
    conn.session.__enter__.return_value = conn.session

    from utils import db_utils

    # Clear any real connection a previous (non-mocked) test may have cached,
    # then patch it — mocker restores the original get_connection, cache and
    # all, when this test tears down.
    db_utils.get_connection.clear()
    mocker.patch("utils.db_utils.get_connection", return_value=conn)

    yield conn


@pytest.fixture(autouse=True)
def _clear_llm_insights_cache():
    """utils.llm_insights' two public functions are @st.cache_data-decorated
    (keyed on their arguments) — clear between tests so one test's mocked
    Anthropic response can't leak into another's assertion.
    """
    from utils import llm_insights

    yield

    llm_insights.get_llm_insights_for_actuals_vs_predicted.clear()
    llm_insights.get_llm_planning_insights.clear()
