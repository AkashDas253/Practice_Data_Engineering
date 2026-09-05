from datetime import date, datetime, timedelta
from typing import Any, Dict, List

from api_client import WeatherAPIClient
from config_parser import ResearchConfig
from metrics import METRIC_REGISTRY


class WeatherIngestor:
    """Orchestrates chunked API fetching and transforms nested time-series responses into flat records."""

    def __init__(self, config: ResearchConfig, api_client: WeatherAPIClient | None = None):
        self.config = config
        self.api_client = api_client or WeatherAPIClient()

    @staticmethod
    def _normalize_date(val: Any) -> date:
        """Safely coerces strings, datetime, or date objects to standard datetime.date."""
        if isinstance(val, datetime):
            return val.date()
        if isinstance(val, date):
            return val
        return datetime.strptime(str(val), "%Y-%m-%d").date()

    def fetch_all(self) -> List[Dict[str, Any]]:
        """Iterates through locations, executes chunked API calls, and flattens hourly payloads."""
        metric_defs = [
            METRIC_REGISTRY[alias]
            for alias in self.config.requested_metrics
            if alias in METRIC_REGISTRY
        ]
        api_params = [m.api_param for m in metric_defs]
        batch_days = self.config.execution.batch_size_days

        start_dt = self._normalize_date(self.config.time_window.start_date)
        end_dt = self._normalize_date(self.config.time_window.end_date)

        all_records: List[Dict[str, Any]] = []

        for loc in self.config.locations:
            curr_start = start_dt
            while curr_start <= end_dt:
                curr_end = min(curr_start + timedelta(days=batch_days - 1), end_dt)

                raw_data = self.api_client.fetch_location_metrics(
                    latitude=loc.latitude,
                    longitude=loc.longitude,
                    start_date=curr_start,
                    end_date=curr_end,
                    api_params=api_params,
                )

                hourly = raw_data.get("hourly", {})
                timestamps = hourly.get("time", [])

                for idx, timestamp in enumerate(timestamps):
                    record: Dict[str, Any] = {
                        "location_id": loc.id,
                        "observation_timestamp": timestamp,
                    }
                    for m in metric_defs:
                        values = hourly.get(m.api_param, [])
                        record[m.alias] = values[idx] if idx < len(values) else None

                    all_records.append(record)

                curr_start = curr_end + timedelta(days=1)

        return all_records