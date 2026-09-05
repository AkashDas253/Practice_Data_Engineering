from pathlib import Path
from typing import Any, Dict, List
import duckdb
import pyarrow as pa

from config_parser import ResearchConfig
from metrics import METRIC_REGISTRY


class DuckDBLoader:
    """Manages dynamic table creation, idempotent batch upserts, and flat-file exports in DuckDB."""

    def __init__(self, config: ResearchConfig):
        self.config = config
        self.db_path = str(config.database.filepath)
        self.table_name = config.database.table_name

    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        """Establishes connection to local DuckDB file."""
        return duckdb.connect(self.db_path)

    def build_schema_ddl(self) -> str:
        """Generates dynamic CREATE TABLE statement based on requested metrics."""
        column_definitions = [
            "location_id VARCHAR NOT NULL",
            "observation_timestamp TIMESTAMPTZ NOT NULL",
        ]

        for alias in self.config.requested_metrics:
            if alias in METRIC_REGISTRY:
                metric_def = METRIC_REGISTRY[alias]
                column_definitions.append(f"{metric_def.alias} {metric_def.duckdb_type}")

        # Primary Key ensures idempotency for ON CONFLICT operations
        column_definitions.append("PRIMARY KEY (location_id, observation_timestamp)")

        columns_sql = ",\n    ".join(column_definitions)
        return f"CREATE TABLE IF NOT EXISTS {self.table_name} (\n    {columns_sql}\n);"

    def initialize_table(self) -> None:
        """Executes the dynamic DDL query to prepare destination table."""
        ddl = self.build_schema_ddl()
        with self._get_connection() as conn:
            conn.execute(ddl)

    def load_records(self, records: List[Dict[str, Any]]) -> None:
        """Idempotently upserts flattened observation records into DuckDB using PyArrow table registration."""
        if not records:
            return

        arrow_table = pa.Table.from_pylist(records)

        update_assignments = [
            f"{alias} = EXCLUDED.{alias}"
            for alias in self.config.requested_metrics
            if alias in METRIC_REGISTRY
        ]

        # Prevent SQL syntax errors if no metric assignments exist
        if update_assignments:
            update_sql = ",\n                ".join(update_assignments)
            conflict_action = f"DO UPDATE SET\n                {update_sql}"
        else:
            conflict_action = "DO NOTHING"

        upsert_query = f"""
            INSERT INTO {self.table_name}
            BY NAME
            SELECT * FROM staging_batch
            ON CONFLICT (location_id, observation_timestamp) {conflict_action};
        """

        with self._get_connection() as conn:
            conn.register("staging_batch", arrow_table)
            try:
                conn.execute("BEGIN TRANSACTION;")
                conn.execute(upsert_query)
                conn.execute("COMMIT;")
            except Exception:
                conn.execute("ROLLBACK;")
                raise
            finally:
                conn.unregister("staging_batch")

    def export_to_csv(self) -> None:
        """Exports the gold-layer analytical table to a CSV file if enabled in config."""
        if not self.config.execution.export_csv_on_complete:
            return

        csv_path = Path(self.config.execution.csv_output_path)
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        with self._get_connection() as conn:
            export_query = f"""
                COPY (SELECT * FROM {self.table_name} ORDER BY location_id, observation_timestamp) 
                TO '{csv_path}' (HEADER, DELIMITER ',');
            """
            conn.execute(export_query)


if __name__ == "__main__":
    from api_client import WeatherAPIClient
    from ingestor import WeatherIngestor

    config = ResearchConfig.load_from_yaml(Path("exampl.yaml"))
    api_client = WeatherAPIClient()
    ingestor = WeatherIngestor(config=config, api_client=api_client)
    records = ingestor.fetch_all()

    loader = DuckDBLoader(config)
    loader.initialize_table()
    loader.load_records(records)
    loader.export_to_csv()