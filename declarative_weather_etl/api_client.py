from datetime import date, datetime
from typing import Any, Dict, List, Union
import requests


class WeatherAPIClient:
    """Handles HTTP requests and dynamic endpoint routing for Open-Meteo APIs."""

    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    @staticmethod
    def _normalize_date(val: Union[str, date, datetime]) -> date:
        """Safely converts string, datetime, or date objects to standard datetime.date."""
        if isinstance(val, datetime):
            return val.date()
        if isinstance(val, date):
            return val
        return datetime.strptime(str(val), "%Y-%m-%d").date()

    def fetch_location_metrics(
        self,
        latitude: float,
        longitude: float,
        start_date: Union[str, date, datetime],
        end_date: Union[str, date, datetime],
        api_params: List[str],
    ) -> Dict[str, Any]:
        """Routes request to Archive API if end_date is historical, otherwise Forecast API."""
        start_dt = self._normalize_date(start_date)
        end_dt = self._normalize_date(end_date)

        endpoint = self.ARCHIVE_URL if end_dt < date.today() else self.FORECAST_URL

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "hourly": ",".join(api_params),
            "timezone": "UTC",
        }

        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"Open-Meteo API request failed: {exc}") from exc