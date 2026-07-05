# utils/db.py
import os
import tomllib
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine as real_create_engine

# utils/db_conn.py lives one level below the project root (utils/db_conn.py),
# so parent.parent is the root regardless of what the checkout directory is
# named - searching for a parent literally named "KitchenCopilot" broke on
# Streamlit Cloud, which mounts the repo at /mount/src/kitchencopilot (lowercase).
PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


def get_active_connection_name():
    """Selects the secrets.toml connection block based on APP_ENV (defaults to 'test').

    'ci' is a third, deliberate-only option for automated test runs against a
    database dedicated to them - unrecognized/unset values still fall back to
    'test', so a typo can never land on prod or the CI-only database.
    """
    app_env = os.getenv("APP_ENV", "test").strip().lower()
    if app_env == "prod":
        return "kitchencopilot_db_prod"
    if app_env == "ci":
        return "kitchencopilot_db_ci"
    return "kitchencopilot_db_test"


def get_engine():
    """Extracts the active (prod/test) database URL from secrets.toml and returns a SQLAlchemy Engine."""
    secrets_file = PROJECT_ROOT / ".streamlit" / "secrets.toml"
    if not secrets_file.exists():
        raise FileNotFoundError(f"❌ Error: secrets.toml file missing at: {secrets_file.resolve()}")

    with open(secrets_file, "rb") as f:
        config = tomllib.load(f)

    connection_name = get_active_connection_name()
    try:
        # Safely pull the database URL string from the TOML structure
        database_url = config["connections"][connection_name]["url"]
    except KeyError:
        raise KeyError(f"❌ Error: Could not find [connections.{connection_name}] configuration in TOML.")

    # Use SQLAlchemy's real engine creator and return it explicitly
    return real_create_engine(database_url)
