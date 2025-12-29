# KitchenCopilot

A machine learning-powered meal demand forecasting system for cafeterias, built with Python and Streamlit.

## Overview

KitchenCopilot helps cafeteria managers predict daily meal demand by combining historical sales data with real-time environmental factors. The system integrates weather forecasts, holiday calendars, and capacity planning to generate accurate meal demand predictions, reducing food waste and improving operational efficiency.

This project demonstrates end-to-end machine learning operations including data pipeline design, feature engineering with external APIs, model training and deployment, and interactive web-based visualization.

## Key Features

- **Automated Feature Engineering**: Automatically enriches forecasts with weather data (OpenWeatherMap API) and German holidays (Hessen)
- **Interactive Forecasting Interface**: Streamlit-based dashboard for generating predictions with custom date ranges
- **Performance Tracking**: Compare actual vs predicted meals with exportable Excel reports
- **SQLite Data Persistence**: Stores predictions and actual sales for historical analysis
- **Modular ML Pipeline**: Separate model training workflow using Jupyter notebooks

## Technology Stack

### Core Technologies
- **Python 3.9.6**: Core programming language
- **Streamlit 1.5**: Interactive web application framework
- **scikit-learn 1.6.1**: Machine learning model training and prediction
- **SQLAlchemy 2.0.45**: Database ORM and connection management
- **SQLite**: Lightweight database for predictions and historical data

### Data Processing
- **Pandas 2.3.3**: Data manipulation and analysis
- **NumPy 2.0.2**: Numerical computing
- **requests 2.32.5**: HTTP client for API integration

### External APIs
- **OpenWeatherMap API**: 7-day weather forecasts (free tier)

## Project Structure

```
kitchencopilot/
├── data/
│   ├── models/             # trained models 
│   ├── processed/          # Processed training data
│   ├── raw/                # raw data
│   └── kitchencopilot.db   # SQLite database (created by init script)
├── notebooks/
│   └── extract_data.ipynb  # Data extraction and model training
├── scripts/
│   └── init_db.py          # Database initialization script
├── pages                   # Streamlit pages (auto-discovered)
│   └── 1_Prepare.py        # Configure prediction timeframe and fetch weather
│   └── 2_Prediction.py     # Display Predicted Meal Demand
│   └── 3_Actuals.py        # Actuals vs. Predictions
│   └── 4_Import.py         # Import Page for actual sales data        
├── utils
│   └── __init__.py         # Streamlit application
│   └── db_utils.py         # Database operations
│   └── prediction_utils.py # ML Prediction logic
│   └── weather_utils.py    # API Integration
├── .streamlit/
│   └── secrets.toml        # Streamlit configuration (not in Git)
├── Home.py                 # Streamlit Landing Page
├── requirements.txt        # Python dependencies
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.9 or higher
- OpenWeatherMap API key (free tier: https://openweathermap.org/api)

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd kitchencopilot
```

2. **Create and activate virtual environment**

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

4. **Set up OpenWeatherMap API key**

Create a `.streamlit/secrets.toml` file:
```toml
[connections.kitchencopilot_db]
url = "sqlite:///data/kitchencopilot.db"

[api]
openweathermap_key = "your_api_key_here"
```

5. **Initialize the database**
```bash
python scripts/init_db.py
```

You should see:
```
Starting database initialization...
✓ Data directory ready at: data
✓ Created 'holidays' table
✓ Created 'predictions' table
✓ Created 'actual_sales' table
✓ Database initialization complete: data/kitchencopilot.db
```

### Running the Application

**Start the Streamlit app:**
```bash
streamlit run Home.py
```

The application will open in your browser at `http://localhost:8501`

### Working with Notebooks

For model training and data exploration:

```bash
jupyter notebook notebooks/extract_data.ipynb
```

The notebook includes:
- PDF sales report extraction using pdfplumber
- Data preprocessing and feature engineering
- Model training with scikit-learn
- Model persistence for production use

## Usage Guide

### Generating Predictions

1. Navigate to the Predictions page in the Streamlit app
2. Select a start date and forecast period (up to 7 days)
3. Input expected daily capacity
4. Click "Fetch Weather & Generate Predictions"
5. Review the forecast table and visualizations

### Exporting Results

- Use the "Export to Excel" button to download predictions
- Compare actual vs predicted meals for performance analysis
- Reports include all features used in the prediction

## Architecture

The system follows a modular architecture separating concerns:

- **Offline Process**: Historical data training using Jupyter notebooks
- **Feature Engineering**: Automated enrichment with weather and holiday data
- **Prediction Engine**: Trained scikit-learn model for demand forecasting
- **Web Interface**: Streamlit dashboard for user interaction
- **Data Persistence**: SQLite database for predictions and actuals

For detailed architecture documentation, see `architektur_beschreibung_deutsch.md`

## Future Enhancements

- Automated daily scheduling for predictions
- Enhanced model features (menu item analysis, historical trends)
- Multi-location support for cafeteria chains
- Real-time model retraining pipeline
- Advanced visualization with confidence intervals
- Mobile-responsive interface improvements

## Technical Notes

**Database Schema:**
- `holidays`: Holiday calendar with bank holidays, semester breaks, and bridge days
- `predictions`: Forecast results with all feature data and timestamps
- `actual_sales`: Actual meal counts for model validation

**Model Details:**
- Algorithm: Scikit-learn regression (specific model TBD based on training results)
- Features: Weekday, month, expected capacity, temperature, weather conditions, holiday flags
- Training data: Historical cafeteria sales with weather and calendar features

## License

This project is a portfolio demonstration piece. Contact for usage inquiries.

## Contact

For questions or collaboration opportunities, please reach out via GitHub.