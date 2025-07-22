import yaml
from pathlib import Path
import os

class Config:
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.data = self._load_config()
        self.last_modified_time = self._get_last_modified_time()

    def _load_config(self):
        """Load the YAML configuration file."""
        with self.config_file.open("r") as file:
            return yaml.safe_load(file)

    def _get_last_modified_time(self):
        """Get the last modified time of the configuration file."""
        return self.config_file.stat().st_mtime

    def get(self, key: str, default=None):
        """
        Retrieve a value from the config data using a dotted path for nested keys.
        Example:
            config.get('db_details.pci.user') -> Returns the user under pci in db_details.
        """
        keys = key.split(".")
        value = self.data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def check_for_updates(self):
        """Check if the config file has been updated and reload it if necessary."""
        current_modified_time = self.config_file.stat().st_mtime
        if current_modified_time != self.last_modified_time:
            self.data = self._load_config()
            self.last_modified_time = current_modified_time
            return True  # Indicate that the config has been reloaded
        return False

    @property
    def test_mode(self):
        """Return the test_mode flag."""
        return self.data.get("test_mode", False)