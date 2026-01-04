from pathlib import Path

# Calculate once, use everywhere
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / 'data' / 'models'
MODEL_PATH = MODELS_DIR / 'random_forest_model.pkl'
FEATURES_PATH = MODELS_DIR / 'feature_columns.pkl'
METADATA_PATH = MODELS_DIR / 'model_metadata.json'