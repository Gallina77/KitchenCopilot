"""Phase 1 example: pure-logic tests for utils/day_themes.py — zero
dependencies (no I/O, no Streamlit, no DB), so these are the fastest,
lowest-risk tests to write and a good template for similar pure-dict/
pure-function modules.
"""
import pytest

from utils.day_themes import DAY_THEMES, THEME_VEG_RATIO

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("theme", THEME_VEG_RATIO.keys())
def test_veg_non_veg_ratio_sums_to_one(theme):
    veg_ratio, non_veg_ratio = THEME_VEG_RATIO[theme]
    assert veg_ratio + non_veg_ratio == pytest.approx(1.0, abs=0.01)


def test_every_day_theme_has_a_veg_ratio_entry():
    # Guards against drift if a new weekday/theme is ever added to one dict
    # but not the other.
    for theme in DAY_THEMES.values():
        assert theme in THEME_VEG_RATIO, f"{theme!r} has no THEME_VEG_RATIO entry"


@pytest.mark.parametrize(
    "theme,expected_veg_ratio",
    [
        ("Sausage", 0.50),    # 30 veg : 30 non-veg
        ("Vital", 0.43),      # 30 veg : 40 non-veg
        ("Chicken", 0.43),    # 30 veg : 40 non-veg
        ("Schnitzel", 0.37),  # 30 veg : 50 non-veg
        ("Fish", 0.50),       # 30 veg : 30 non-veg
    ],
)
def test_ratio_matches_documented_portions(theme, expected_veg_ratio):
    veg_ratio, _ = THEME_VEG_RATIO[theme]
    assert veg_ratio == pytest.approx(expected_veg_ratio, abs=0.01)


def test_day_themes_covers_every_weekday():
    assert set(DAY_THEMES.keys()) == {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
