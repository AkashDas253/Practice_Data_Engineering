from pathlib import Path
from typing import Any

import yaml


class ConfigLoader:
    """Load YAML configuration files."""

    def load(self, path: str | Path) -> dict[str, Any]:
        config_path = Path(path)

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}"
            )

        if not config_path.is_file():
            raise ValueError(
                f"Configuration path is not a file: {config_path}"
            )

        with config_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if data is None:
            return {}

        if not isinstance(data, dict):
            raise ValueError(
                "Configuration root must be a mapping."
            )

        return data
