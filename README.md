# KitchenCopilot

A machine learning-powered meal demand forecasting system for cafeterias, built with Python and Streamlit.

## Overview

KitchenCopilot helps cafeteria managers predict daily meal demand by combining historical sales data with real-time environmental factors. The system integrates weather forecasts, holiday calendars, and a weekday-based "day theme" system to generate meal demand predictions split into vegetarian, non-vegetarian, and salad portions — reducing food waste and improving operational efficiency.

This project demonstrates end-to-end machine learning operations including data pipeline design, feature engineering with external APIs, model training and deployment, cloud database persistence, and interactive web-based visualization.

## Key Features

- **Automated Feature Engineering**: Enriches forecasts with weather data (Open Meteo API) and holiday/school-break/bridge-day data
- **Day Theme System**: Each weekday maps to a fixed meal concept (e.g. "Schnitzel" on Thursday); themes drive both the prediction feature set and the veg/non-veg split
- **Veg / Non-Veg / Salad Split**: Total predicted meals are split into categories using empirically observed ratios per day theme, learned from actual sales history (with a hardcoded fallback until enough history exists)
- **Interactive Forecasting Interface**: Streamlit-based dashboard for generating predictions over a date range, with manual override support
- **AI-powered Insights**: The app sends prediction/actuals data to Claude (Anthropic API), which identifies actionable patterns — like systematic weekday biases or veg/non-veg split errors — in plain language for kitchen staff
- **Performance Tracking**: Compare actual vs. predicted meals, with per-category error breakdowns and exportable PDF reports
- **CSV Actuals Import**: Upload actual sales data via CSV, with column-alias detection and schema/sum validation
- **Cloud Data Persistence**: Predictions and actuals are stored in Postgres (Supabase), with separate prod/test databases selected via an environment variable
- **Modular ML Pipeline**: Model training happens offline via `scripts/train_model.py` / notebooks, decoupled from the app
- **Bilingual UI**: Full English/German translation support with a sidebar language toggle

## Technology Stack

### Core Technologies
- **Python 3.12**
- **Streamlit 1.50**: Interactive web application framework
- **scikit-learn 1.6.1**: Machine learning model training and prediction
- **SQLAlchemy 2.0.45**: Database ORM and connection management
- **Postgres (Supabase)**: Cloud-hosted database for predictions and actuals

### Data Processing
- **Pandas 2.3.3**: Data manipulation and analysis
- **NumPy 2.0.2**: Numerical computing
- **Pydantic / Pandantic**: Schema validation for imported CSV data
- **fpdf2**: PDF report export
- **Plotly 6.5.0**: Charting
- **Babel 2.17.0**: Locale-aware formatting

### External APIs
- **Open Meteo API**: Weather forecasts and historical weather (free tier, no API key required)
- **Claude API (Anthropic)**: Prediction/actuals data is serialized to JSON and sent to the Anthropic API for natural-language insights; responses are cached (`st.cache_data`) to avoid redundant calls, with a translated fallback message if the API is unreachable

### Testing
- **pytest**, **pytest-mock**, **pytest-cov**, **freezegun**, **responses**: Unit, mocked, and integration test tooling (see [Testing](#testing) below)

## Project Structure

```
kitchencopilot/
├── components/
│   ├── home.py                 # HTML component builders for the Home page
│   └── sidebar.py               # Language toggle (EN/DE) rendered in the sidebar
├── data/
│   ├── models/                  # Trained model artifacts (.pkl) + metadata
│   ├── processed/                # Processed training data
│   └── raw/                     # Raw data (holidays, sales data)
├── docs/
│   ├── AUDIT.md                 # Project audit / issue register (historical log)
│   └── FEATURE_PLAN.md          # Phased refactor/feature plan (historical log)
├── pages/                        # Streamlit pages (auto-discovered, filenames include spaces)
│   ├── 1_Prepare your Forecast.py   # Choose a date range, fetch weather/holidays, generate predictions
│   ├── 2_Meal Demand Prediction.py  # Review predictions, override values, save to DB
│   ├── 3_Actuals vs. Predicted.py   # Compare actuals vs. predictions, error breakdowns, LLM insights
│   └── 4_Import Actuals.py          # CSV upload of actual sales data
├── scripts/
│   ├── train_model.py            # Offline model training, writes data/models/*.pkl
│   ├── seed_holidays.py           # Seed the holidays table
│   ├── seed_actuals.py            # Seed the actual_sales table
│   ├── transform_actuals.py       # Data transformation helpers
│   ├── delete_actuals.py          # Maintenance script
│   └── old/                      # Retired SQLite-era scripts, not used by the current app
├── styles/
│   ├── css/main.css              # App styling
│   └── images/                   # Logo assets
├── tests/
│   ├── unit/                     # Pure-logic tests, no I/O
│   ├── db/                       # DB-adjacent tests (pure / mocked / real integration)
│   ├── apptest/                  # streamlit.testing.v1.AppTest page-flow tests
│   └── fixtures/                 # Shared fixture builders (DataFrames, weather responses, model artifact)
├── utils/
│   ├── db_conn.py                # Builds the SQLAlchemy engine; selects prod/test DB via APP_ENV
│   ├── db_utils.py               # Postgres queries/upserts for holidays, predictions, actual_sales
│   ├── data_preparation_utils.py # Feature engineering, badge rendering
│   ├── prediction_utils.py       # Model inference + veg/non-veg/salad split
│   ├── day_themes.py             # Weekday → day theme mapping, veg-ratio fallback, UI colors
│   ├── weather_utils.py          # Open Meteo API client
│   ├── llm_insights.py           # Anthropic API integration for insights (with caching + fallback)
│   ├── home_utils.py             # System status checks for the Home page
│   ├── import_utils.py           # CSV column-alias detection + schema/sum validation
│   ├── export_pdf.py             # PDF report generation
│   ├── translations_utils.py     # Loads/merges EN/DE translation JSON
│   └── translations/             # Per-page + common EN/DE translation JSON files
├── .streamlit/
│   └── secrets.toml               # DB connection URLs + ANTHROPIC_API_KEY (not in Git)
├── Home.py                        # Streamlit landing page / system status dashboard
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # pytest configuration (markers, test paths)
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.12 or higher
- A Supabase (or other Postgres) project — one database is enough to start; prod/test separation is optional but recommended
- Anthropic API key (https://console.anthropic.com)

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd kitchencopilot
```

2. **Create and activate a virtual environment**

On macOS/Linux:
```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure secrets**

Create `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "your-key-here"

[connections.kitchencopilot_db_test]
url = "postgresql://user:password@host:5432/dbname"

[connections.kitchencopilot_db_prod]
url = "postgresql://user:password@host:5432/dbname"
```

The app selects between these two blocks at runtime via the `APP_ENV` environment variable
(`prod` → `kitchencopilot_db_prod`, anything else, including unset → `kitchencopilot_db_test`).
If you only have one database, point both blocks at it.

5. **Create the database schema**

The `holidays`, `predictions`, and `actual_sales` tables are created directly in Postgres (e.g. via
the Supabase SQL editor) rather than through a setup script. See `scripts/seed_holidays.py` and
`scripts/seed_actuals.py` for the expected column shapes, and `docs/FEATURE_PLAN.md` for schema
history.

### Running the Application

**Start the Streamlit app:**
```bash
streamlit run Home.py
```

The application will open in your browser at `http://localhost:8501`

### Working with Notebooks / Retraining the Model

```bash
python scripts/train_model.py
```

Training uses historical sales data plus weather/calendar features, and writes the model, its
feature-column list, and metadata to `data/models/`.

## Usage Guide

### Generating Predictions

1. Navigate to **"Prepare your Forecast"** and choose a start date and number of business days
2. The app fetches weather and holiday data automatically and generates predictions
3. Navigate to **"Meal Demand Prediction"** to review the forecast (total, veg, non-veg, salad), override values if needed, and save
4. Navigate to **"Actuals vs. Predicted"** once actuals are available to compare performance, view AI-generated insights, and export results

### Importing Actuals

- Use **"Import Actuals"** to upload a CSV of actual sales
- Column names are matched against known aliases (e.g. `date`/`datum`, `total`/`gesamt`) and validated for type and internal consistency (veg + non-veg must sum to the total) before saving

### Exporting Results

- Use the PDF export on the Actuals/Predictions pages to download a report of the current table

## Testing

```bash
# Full suite
pytest

# Fast suite (what CI runs on every push/PR) — no real DB, no real Anthropic calls
pytest -m "not db and not llm" --cov=utils --cov=components

# Real-DB integration tests (hits the Supabase test-tier database)
APP_ENV=test pytest -m db
```

Tests are layered by marker (`unit`, `db`, `llm`, `slow`) and organized by directory
(`tests/unit`, `tests/db`, `tests/apptest`, `tests/fixtures`). See `CLAUDE.md` for details on the
fixtures and conventions used.

## Architecture

The system follows a modular architecture separating concerns:

- **Offline Process**: Model training via `scripts/train_model.py`, independent of the running app
- **Feature Engineering**: Automated enrichment with weather, holiday, and day-theme data
- **Prediction Engine**: Trained scikit-learn model for total demand, followed by a rule-based veg/non-veg/salad split using empirical per-theme ratios
- **Web Interface**: Multi-page Streamlit dashboard for forecast generation, review, and performance tracking
- **AI Insights**: Claude (Anthropic API) summarizes prediction/actuals patterns for kitchen staff
- **Data Persistence**: Postgres (Supabase) for predictions, actuals, and holidays, with an environment-based prod/test switch

## Database Schema

- `holidays`: Holiday calendar with bank holidays, semester breaks, and bridge days
- `predictions`: Forecast results (date, weekday, month, day theme, weather, holiday flags, predicted totals and veg/non-veg/salad splits, override fields, timestamps) — `date` is the primary key, upserted on regeneration
- `actual_sales`: Actual meal counts (total, veg, non-veg, salad) for model validation — `date` is the primary key, upserted on re-import

## License

This project is a portfolio demonstration piece. Contact for usage inquiries.

## Contact

For questions or collaboration opportunities, please reach out via GitHub.
