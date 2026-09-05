from datetime import date, datetime
from unittest.mock import MagicMock, patch
import pytest
import requests

from api_client import WeatherAPIClient


class TestWeatherAPIClient:

    def test_normalize_date_variants(self):
        client = WeatherAPIClient()
        
        # Test string input
        assert client._normalize_date("2023-01-01") == date(2023, 1, 1)
        # Test date input
        assert client._normalize_date(date(2023, 1, 1)) == date(2023, 1, 1)
        # Test datetime input
        assert client._normalize_date(datetime(2023, 1, 1, 12, 0)) == date(2023, 1, 1)

    @patch("api_client.requests.get")
    def test_fetch_location_metrics_archive_endpoint(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"hourly": {"time": ["2023-01-01T00:00"]}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = WeatherAPIClient()
        res = client.fetch_location_metrics(
            latitude=40.7128,
            longitude=-74.0060,
            start_date="2020-01-01",
            end_date="2020-01-02",  # Historical date -> ARCHIVE_URL
            api_params=["temperature_2m"],
        )

        assert mock_get.called, "requests.get was not invoked by fetch_location_metrics"
        assert mock_get.call_args[0][0] == WeatherAPIClient.ARCHIVE_URL
        assert res == {"hourly": {"time": ["2023-01-01T00:00"]}}

    @patch("api_client.requests.get")
    def test_fetch_location_metrics_forecast_endpoint(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"hourly": {"time": []}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = WeatherAPIClient()
        future_date = date(2099, 1, 1)
        res = client.fetch_location_metrics(
            latitude=40.7128,
            longitude=-74.0060,
            start_date=future_date,
            end_date=future_date,  # Future date -> FORECAST_URL
            api_params=["temperature_2m"],
        )

        assert mock_get.called, "requests.get was not invoked by fetch_location_metrics"
        assert mock_get.call_args[0][0] == WeatherAPIClient.FORECAST_URL

    @patch("api_client.requests.get")
    def test_fetch_location_metrics_http_error_raises_runtime_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("API Down")

        client = WeatherAPIClient()
        with pytest.raises((RuntimeError, requests.exceptions.RequestException)):
            client.fetch_location_metrics(
                latitude=40.7128,
                longitude=-74.0060,
                start_date="2023-01-01",
                end_date="2023-01-02",
                api_params=["temperature_2m"],
            )