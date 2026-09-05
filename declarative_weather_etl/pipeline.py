from pathlib import Path
from typing import Any, Dict, List, Union

from api_client import WeatherAPIClient
from config_parser import ResearchConfig
from duckdb_loader import DuckDBLoader
from ingestor import WeatherIngestor


class WeatherPipeline:
    """Programmatic API interface for executing declarative-weather-etl."""

    def __init__(
        self,
        config: Union[str, Path, ResearchConfig],
        api_client: WeatherAPIClient | None = None,
        loader: DuckDBLoader | None = None,
    ):
        if isinstance(config, (str, Path)):
            self.config = ResearchConfig.load_from_yaml(Path(config))
        else:
            self.config = config

        self.api_client = api_client or WeatherAPIClient()
        self.ingestor = WeatherIngestor(config=self.config, api_client=self.api_client)
        self.loader = loader or DuckDBLoader(self.config)

    def run(self) -> List[Dict[str, Any]]:
        """Executes full ETL flow: Extraction -> DuckDB Upsert -> CSV Export."""
        records = self.ingestor.fetch_all()
        self.loader.initialize_table()
        self.loader.load_records(records)
        self.loader.export_to_csv()
        return records


def run_pipeline(config: Union[str, Path, ResearchConfig]) -> List[Dict[str, Any]]:
    """Convenience functional API to run the pipeline with a YAML file path or pre-parsed config."""
    pipeline = WeatherPipeline(config)
    return pipeline.run()