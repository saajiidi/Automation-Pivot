import os
from datetime import date


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}

APP_TITLE = "DEEN Business Intelligence"
APP_VERSION = "v10.0"
APP_DATA_START_DATE = date(2021, 8, 1)

MORE_TOOLS = [
    "System Logs",
    "Dev Lab",
]

INVENTORY_LOCATIONS = ["Ecom", "Mirpur", "Wari", "Cumilla", "Sylhet"]

STATUS_COLORS = {
    "success": "#15803d",
    "warning": "#b45309",
    "error": "#b91c1c",
    "info": "#1d4ed8",
}

# Performance & Memory Optimization
# Community Cloud should default to the baked snapshot unless explicitly turned off.
USE_STATIC_SNAPSHOT = _env_bool("USE_STATIC_SNAPSHOT", True)

# Components that ALWAYS use snapshot to save memory (like complex maps)
MAP_FORCE_SNAPSHOT = _env_bool("MAP_FORCE_SNAPSHOT", True)

SNAPSHOT_DATE = "2026-04-08"
SNAPSHOT_LABEL = "April 2026 Operational Snapshot"
