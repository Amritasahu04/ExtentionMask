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


import json


SETTINGS_PATH = DATA_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "monitor_duration": "Continuous",
    "scan_delay": 2.0,
    "notifications_enabled": True,
    "notification_min_severity": "Medium",
    "notification_cooldown": 30
}

NOTIFICATION_SEVERITIES = [
    "Low",
    "Medium",
    "High",
    "Critical"
]

MIN_NOTIFICATION_COOLDOWN = 10
MAX_NOTIFICATION_COOLDOWN = 120

LOG_FILE = LOG_DIR / "extensionmask.log"

MONITOR_DURATIONS = {
    "Continuous": None,
    "15 Minutes": 900,
    "30 Minutes": 1800,
    "1 Hour": 3600,
    "2 Hours": 7200
}


def load_settings():

    settings = DEFAULT_SETTINGS.copy()

    try:

        if SETTINGS_PATH.exists():

            with open(
                SETTINGS_PATH,
                "r",
                encoding="utf-8"
            ) as file:

                saved = json.load(file)

            if isinstance(saved, dict):
                settings.update(saved)

    except (OSError, ValueError):
        pass

    if settings["monitor_duration"] not in (
        MONITOR_DURATIONS.keys()
    ):
        settings["monitor_duration"] = "Continuous"

    try:

        delay = float(settings["scan_delay"])

        if not 1 <= delay <= 10:
            delay = 2.0

        settings["scan_delay"] = delay

    except (ValueError, TypeError):
        settings["scan_delay"] = 2.0

    if not isinstance(
        settings.get("notifications_enabled"), bool
    ):
        settings["notifications_enabled"] = True

    if settings.get(
        "notification_min_severity"
    ) not in NOTIFICATION_SEVERITIES:

        settings["notification_min_severity"] = "Medium"

    try:

        cooldown = int(
            settings.get("notification_cooldown", 30)
        )

        settings["notification_cooldown"] = max(
            MIN_NOTIFICATION_COOLDOWN,
            min(MAX_NOTIFICATION_COOLDOWN, cooldown)
        )

    except (ValueError, TypeError, OverflowError):

        settings["notification_cooldown"] = 30

    return settings



def save_settings(settings):

    initialize_directories()

    temporary_path = SETTINGS_PATH.with_suffix(
        ".tmp"
    )

    with open(
        temporary_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(settings, file, indent=4)

    temporary_path.replace(SETTINGS_PATH)
