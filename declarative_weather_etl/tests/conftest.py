from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch
import pytest

CONFIGS_DIR = Path(__file__).parent / "configs"


def get_config_files(pattern: str = "valid_*.yaml") -> list[Path]:
    return sorted(list(CONFIGS_DIR.glob(pattern)))


@pytest.fixture
def config_paths() -> dict[str, Path]:
    return {
        "valid_archive": CONFIGS_DIR / "valid_archive.yaml",
        "valid_forecast": CONFIGS_DIR / "valid_forecast.yaml",
        "invalid_schema": CONFIGS_DIR / "invalid_schema.yaml",
    }


@pytest.fixture
def sample_config():
    config = MagicMock()
    config.database.table_name = "weather_metrics"
    config.database.filepath = ":memory:"

    config.execution.export_csv_on_complete = False
    config.execution.csv_output_path = "output.csv"

    config.requested_metrics = ["air_temp"]

    mock_metric = MagicMock()
    mock_metric.target_column = "air_temp"
    mock_metric.data_type = "DOUBLE"
    config.metrics = [mock_metric]

    return config


@pytest.fixture
def mock_open_meteo_payload() -> Dict[str, Any]:
    return {
        "hourly": {
            "time": ["2023-01-01T00:00", "2023-01-01T01:00"],
            "temperature_2m": [15.2, 14.8],
            "relative_humidity_2m": [80.0, 82.0],
            "wind_speed_10m": [5.1, 4.9],
        }
    }


@pytest.fixture(autouse=True)
def mock_api_client(request, mock_open_meteo_payload):
    if "test_api_client" in request.node.nodeid:
        yield None
        return

    with patch(
        "api_client.WeatherAPIClient.fetch_location_metrics",
        return_value=mock_open_meteo_payload,
    ) as mock_fetch:
        yield mock_fetch