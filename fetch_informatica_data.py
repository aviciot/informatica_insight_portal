
import logging
import os

from config.config import Config
from pathlib import Path
from db.db_utils import get_db_session, get_db_engine,initialize_database

from datetime import datetime, timezone

# Initialize app configuration
config_file = Path("config", "config.yaml")
config = Config(config_file)

engine = get_db_engine(config)
session = get_db_session(config)

db_preference = config.get("insight_db.work_with", "Unknown")
db_display_name = db_colors.get(db_preference, "⚠️ Unknown")


