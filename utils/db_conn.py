# utils/db.py
import tomllib
from pathlib import Path
from sqlalchemy import create_engine as real_create_engine

# Find the root by locating the main KitchenCopilot directory name securely
current_path = Path(__file__).resolve()
PROJECT_ROOT = next(p for p in current_path.parents if p.name == "KitchenCopilot")

def get_engine():
    """Extracts the database URL from secrets.toml and returns a valid SQLAlchemy Engine."""
    secrets_file = PROJECT_ROOT / ".streamlit" / "secrets.toml"
    if not secrets_file.exists():
        raise FileNotFoundError(f"❌ Error: secrets.toml file missing at: {secrets_file.resolve()}")
        
    with open(secrets_file, "rb") as f:
        config = tomllib.load(f)
        
    try:
        # Safely pull the database URL string from the TOML structure
        database_url = config["connections"]["kitchencopilot_db"]["url"]
    except KeyError:
        raise KeyError("❌ Error: Could not find [connections.kitchencopilot_db] configuration in TOML.")
    
    # Dynamically resolve relative SQLite paths so execution works from any folder
    if database_url.startswith("sqlite:///"):
        relative_db_path = database_url.replace("sqlite:///", "")
        absolute_db_path = PROJECT_ROOT / relative_db_path
        database_url = f"sqlite:///{absolute_db_path}"
        
    # Use SQLAlchemy's real engine creator and return it explicitly
    return real_create_engine(database_url)
