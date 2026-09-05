from pathlib import Path
import duckdb
import pytest

from duckdb_loader import DuckDBLoader


def test_duckdb_loader_export_to_csv(tmp_path: Path, sample_config):
    db_file_path = (tmp_path / "test.duckdb").as_posix()
    csv_file_path = (tmp_path / "output.csv").as_posix()

    sample_config.database.table_name = "weather_metrics"
    sample_config.database.filepath = db_file_path

    sample_config.execution.export_csv_on_complete = True
    sample_config.execution.csv_output_path = csv_file_path

    loader = DuckDBLoader(sample_config)
    loader.initialize_table()

    records = [
        {
            "location_id": "loc_1",
            "observation_timestamp": "2023-01-01T00:00",
            "air_temp": 15.5,
        }
    ]
    loader.load_records(records)
    loader.export_to_csv()

    export_file = Path(csv_file_path)
    assert export_file.exists()
    assert "loc_1" in export_file.read_text()