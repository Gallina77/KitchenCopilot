# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

KitchenCopilot is a Streamlit app that forecasts daily meal demand for a cafeteria. A scikit-learn
model (trained offline in a notebook / `scripts/train_model.py`) predicts total meals for upcoming
business days from weekday/month, weather (Open Meteo), and holiday/school-break data; the total is
then split into veg/non-veg/salad using empirically observed ratios per "day theme". Predictions and
actuals are persisted to Postgres (Supabase) and compared on an actuals-vs-predicted page, with an
LLM (Claude, via the Anthropic API) generating plain-language insights on both the planning and
actuals pages.

Note: `README.md` describes an earlier SQLite-based version of this app (different page filenames, a
`.streamlit/secrets.toml` prod/test split that doesn't exist, capacity input that has since been
removed). Treat the README as outdated background, not ground truth — this file and the code are
current.

## Commands

```bash
# Run the app
streamlit run Home.py

# Run the full test suite
pytest

# Fast suite only (what CI runs on every push/PR) — no real DB, no real Anthropic calls
pytest -m "not db and not llm" --cov=utils --cov=components

# Real-DB integration tests (hits the Supabase *test*-tier DB — see Environments below)
APP_ENV=test pytest -m db

# A single test file / test
pytest tests/unit/test_data_preparation.py
pytest tests/unit/test_data_preparation.py::test_build_data_features_adds_day_theme

# Train/retrain the model (writes data/models/*.pkl)
python scripts/train_model.py
```

There is no lint/format command configured in this repo (no ruff/black/flake8 config found) —
don't invent one.

### Pytest markers (declared in `pyproject.toml`, `--strict-markers` enforced)

- `unit` — pure-logic, no I/O, no external dependencies.
- `db` — hits the real Supabase **test**-tier database. Requires `APP_ENV=test` and a
  `[connections.kitchencopilot_db_test]` block in `.streamlit/secrets.toml`.
- `llm` — hits the real Anthropic API.
- `slow` — notably slower than the rest of the suite (AppTest page runs, model-artifact loading).

Every new test file needs one of these markers; unmarked tests fail collection under
`--strict-markers`.

## Architecture

### Environment / database switching

`utils/db_conn.py` picks a Postgres connection block from `.streamlit/secrets.toml` based on the
`APP_ENV` env var: `prod` → `kitchencopilot_db_prod`, anything else (including unset) → the **test**
DB. This defaults to safe, but `tests/conftest.py` forces `APP_ENV=test` in `pytest_configure`
regardless of the developer's shell/`.env`, so the test suite can never accidentally hit prod even if
a `.env` sets `APP_ENV=prod` locally. `secrets.toml` itself is gitignored and is the sole source of
DB URLs and the `ANTHROPIC_API_KEY` — never expect it to exist in CI except where the workflow writes
it (see `.github/workflows/tests.yml`, which materializes only the test-tier block from
`secrets.SUPABASE_TEST_DB_URL`).

`utils/db_utils.get_connection()` wraps `st.connection(..., type="sql")` in `@st.cache_resource`.
Tests never hit this directly — use the `mock_st_connection` fixture (`tests/conftest.py`), which
patches `get_connection` everywhere it's already been imported (including the re-export from
`utils/__init__.py`) and clears the cache so mocks can't leak between tests.

### Data flow (prediction pipeline)

1. **`utils/data_preparation_utils.prepare_data(start_date, number_of_days)`** builds a business-day
   (`freq='B'`) date range, derives `weekday`/`month`/`day_theme` (via `utils/day_themes.DAY_THEMES`,
   a hardcoded weekday→theme lookup), merges in weather (`utils/weather_utils.get_weather`, Open
   Meteo — "forecast" vs "past" endpoint chosen automatically based on whether the range is in the
   future) and holiday data (`utils/db_utils.get_holidays`), and filters out bank holidays.
2. **`utils/prediction_utils.get_prediction(df)`** loads the trained model + `feature_columns` list
   from `data/models/*.pkl` (paths in `utils/paths.py`), one-hot encodes `month`/`weather_condition`/
   `day_theme` (`weekday` is deliberately dropped — it's collinear with `day_theme`, one weekday maps
   to exactly one theme), reindexes to the training-time `feature_columns`, predicts, then splits the
   total into veg/non-veg via `split_veg_non_veg()` using **empirical per-theme ratios pulled from
   `actual_sales` history** (`utils/db_utils.get_empirical_veg_ratio`), falling back to the hardcoded
   `THEME_VEG_RATIO` in `utils/day_themes.py` when no history exists yet for that theme.
3. **`utils/db_utils.save_prediction(df)`** upserts into `predictions` (Postgres `ON CONFLICT (date)
   DO UPDATE`) — `date` is the primary key, so re-running a forecast for an already-predicted date
   overwrites rather than duplicates.
4. Actuals are entered/imported (`pages/4_Import Actuals.py`, `utils/import_utils.csv_validation`)
   and saved via `save_actuals()`, upserted the same way into `actual_sales`.
5. `utils/db_utils.get_actuals_and_predictions()` / `get_missing_actuals()` join the two tables for
   the review pages; `calculate_metrics()` computes MAE / over-/under-prediction counts / accuracy
   rate (all divisions guarded with `.replace(0, np.nan)` to avoid `ZeroDivisionError`/`inf`).

### Pages (Streamlit auto-discovers `pages/*.py`; filenames include spaces)

- `Home.py` — landing page, system status tiles (model/prediction/weather API/DB), all wrapped in
  individual try/except so one failing check doesn't take down the others.
- `pages/1_Prepare your Forecast.py` — date range input → calls `prepare_data` → `get_prediction`.
- `pages/2_Meal Demand Prediction.py` — review/override predictions, save.
- `pages/3_Actuals vs. Predicted.py` — performance comparison + LLM insights.
- `pages/4_Import Actuals.py` — CSV upload of actual sales.

### Day themes and veg ratios (`utils/day_themes.py`)

`DAY_THEMES` maps English weekday names (as returned by `dt.day_name()`) to a fixed theme per
weekday (e.g. Thursday → "Schnitzel") — themes are calendar-fixed, not date-specific.
`THEME_VEG_RATIO` is the fallback split used until enough `actual_sales` history accumulates for
`get_empirical_veg_ratio` to compute a real one per theme. `THEME_CARD_COLORS` is UI-only (card
accent colors on page 2). Any weekday→theme or ratio change here has a direct, cross-cutting effect
on data prep, prediction splitting, and badge rendering — check all three when editing this file.

### Translations (`utils/translations_utils.py`, `utils/translations/*.json`)

`get_translations(page)` reads the current language from `st.session_state["lang"]` (default `"DE"`),
loads `common.json`, and merges in `{page}.json` if given (e.g. `home.json`, `forecast.json`,
`actuals.json`, `predictions.json`). Adding a UI string means adding the key to **both** the `EN` and
`DE` blocks of the relevant JSON file — nothing falls back automatically across languages.

### LLM insights (`utils/llm_insights.py`)

Two `@st.cache_data`-memoized functions call the Anthropic API (model pinned in the `MODEL` constant)
with `thinking={"type": "disabled"}` (a short summarization task — leaving thinking on could eat the
tight `max_tokens` budget and truncate the JSON output). Both wrap the call in `try/except APIError`
and return a language-keyed fallback string/JSON on failure so the actuals/planning pages degrade
gracefully instead of crashing. When testing code that touches these, use the (autouse)
`_clear_llm_insights_cache` fixture in `tests/conftest.py` so one test's mocked response can't leak
into another's assertion via the cache.

## Testing conventions

Tests are organized by layer, and new tests should follow the existing pattern in the directory they
land in rather than introducing a new style:

- `tests/unit/` — pure-logic tests (marker `unit`), no I/O.
- `tests/db/` — three sub-styles side by side, illustrating a spectrum: `test_db_utils_pure.py` (no
  mocking — DataFrame-in-DataFrame-out functions like `calculate_metrics`), `test_db_utils_mocked.py`
  (uses `mock_st_connection`), `test_db_utils_integration.py` (marker `db`, hits the real test-tier
  Postgres DB).
- `tests/apptest/` — `streamlit.testing.v1.AppTest` page-flow tests that run a real page script
  headlessly and inspect output/`session_state`, with DB calls mocked at the `utils.*` boundary
  (that boundary already has its own coverage in `tests/db/`, so these only verify page wiring).
- `tests/fixtures/` — shared fixture builders: `dataframes.py` (DataFrame builders like
  `build_actuals_vs_predictions_df`), `weather_responses.py`, `model_artifact.py` (a tiny synthetic
  `LinearRegression` + matching `feature_columns`, standing in for the real `data/models/*.pkl` so
  prediction-logic tests don't depend on — or break when someone retrains — the actual model).

Key fixtures from `tests/conftest.py`:
- `frozen_today(date_str)` — freezes "now" for code branching on `datetime.now()`/`.today()` (e.g.
  the past-vs-forecast decision in `compute_date_range_and_weather_type`).
- `mock_st_connection` — a `MagicMock` shaped like `st.connection(..., type='sql')` (`.query()` for
  reads, `.session` context manager for writes); patches `get_connection` everywhere and clears its
  cache_resource cache.

CI (`.github/workflows/tests.yml`) runs `not db and not llm` on every push/PR to `main`; the `db` job
only runs when `secrets.SUPABASE_TEST_DB_URL` is set, and writes a `.streamlit/secrets.toml`
containing only the test-tier connection block.

## Working notes

- `scripts/` contains one-off/maintenance scripts (`train_model.py`, `seed_holidays.py`,
  `seed_actuals.py`, `transform_actuals.py`, `delete_actuals.py`); `scripts/old/` is retired SQLite-era
  seeding code — don't build on it. `scripts/init_db.py` also still targets SQLite and predates the
  Postgres migration; the live schema is Postgres/Supabase, created/altered directly there rather
  than through this script.
- `docs/AUDIT.md` and `docs/FEATURE_PLAN.md` are living project logs (bug audit + phased refactor
  plan) — useful for *why* something looks the way it does, but check the code before trusting a
  status marker in either doc, since they're updated manually and can lag.
