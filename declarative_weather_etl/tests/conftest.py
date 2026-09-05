from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch
import pytest

CONFIGS_DIR = Path(__file__).parent / "configs"


def get_config_files(pattern: str = "valid_*.yaml") -> list[Path]:
    """Returns a list of YAML test fixture paths matching the glob pattern."""
    return sorted(list(CONFIGS_DIR.glob(pattern)))


@pytest.fixture
def config_paths() -> dict[str, Path]:
    """Pytest fixture providing key-value map of configuration file paths."""
    return {
        "valid_archive": CONFIGS_DIR / "valid_archive.yaml",
        "valid_forecast": CONFIGS_DIR / "valid_forecast.yaml",
        "invalid_schema": CONFIGS_DIR / "invalid_schema.yaml",
    }


@pytest.fixture
def mock_open_meteo_payload() -> Dict[str, Any]:
    """Fixture supplying a deterministic Open-Meteo API response."""
    return {
        "hourly": {
            "time": ["2023-01-01T00:00", "2023-01-01T01:00"],
            "temperature_2m": [15.2, 14.8],
            "relative_humidity_2m": [80.0, 82.0],
            "wind_speed_10m": [5.1, 4.9],
        }
    }


@pytest.fixture(autouse=True)
def mock_api_client(mock_open_meteo_payload):
    """Automatically mocks API requests across all test modules to prevent network calls."""
    with patch(
        "api_client.WeatherAPIClient.fetch_location_metrics",
        return_value=mock_open_meteo_payload,
    ) as mock_fetch:
        yield mock_fetch