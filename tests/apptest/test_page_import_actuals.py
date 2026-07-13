"""Phase 5 example: a Streamlit AppTest page-flow test — the newest kind of
test in this suite (no prior usage of streamlit.testing.v1.AppTest existed
in the repo). Runs the real page script headlessly and inspects its output/
session_state, with the DB call mocked at the utils.* boundary (that
boundary is already covered independently by tests/db/test_db_utils_*.py,
so this test only needs to verify the page's own wiring).

Start from this pattern for the remaining pages (see the plan's Phase 5
notes for a suggested order: pages/3, then sidebar.render_language_toggle,
then Home.py / pages 1-2 last since those need the most mocking).
"""
import pytest
from streamlit.testing.v1 import AppTest

pytestmark = pytest.mark.unit

PAGE_PATH = "pages/4_Import Actuals.py"


def test_shows_no_data_message_when_nothing_to_import(mocker):
    # No file uploaded (default AppTest state) and no missing-actuals rows
    # in the DB -> the page should hit its "nothing to do" branch, not crash.
    mocker.patch("utils.get_missing_actuals", return_value=None)

    at = AppTest.from_file(PAGE_PATH)
    at.run()

    assert not at.exception
    assert len(at.error) == 1
    assert "no" in at.error[0].value.lower() or "keine" in at.error[0].value.lower()
