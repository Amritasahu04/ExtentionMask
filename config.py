from pathlib import Path

# Application information
APP_NAME = "ExtensionMask"
APP_VERSION = "1.0.0"

# Project directories
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
QUARANTINE_DIR = DATA_DIR / "quarantine"
ASSETS_DIR = BASE_DIR / "assets"

# Database location
DB_PATH = DATA_DIR / "extensionmask.db"

# Create required directories
def initialize_directories():
    for directory in [
        DATA_DIR,
        LOG_DIR,
        QUARANTINE_DIR,
        ASSETS_DIR
    ]:
        directory.mkdir(parents=True, exist_ok=True)
