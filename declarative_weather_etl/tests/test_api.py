from pathlib import Path
import duckdb
from pydantic import ValidationError
import pytest
import yaml

from config_parser import ResearchConfig
from pipeline import WeatherPipeline, run_pipeline

CONFIGS_DIR = Path(__file__).parent / "configs"
VALID_CONFIG_PATHS = sorted(list(CONFIGS_DIR.glob("valid_*.yaml")))


@pytest.mark.parametrize(
    "config_path",
    VALID_CONFIG_PATHS if VALID_CONFIG_PATHS else [pytest.param(None, marks=pytest.mark.skip("No test configs found"))],
    ids=lambda p: p.stem if isinstance(p, Path) else "skipped",
)
def test_weather_pipeline_execution(config_path: Path, tmp_path: Path):
    """Tests WeatherPipeline instantiation and execution for valid YAML test configs."""
    config = ResearchConfig.load_from_yaml(config_path)
    config.database.filepath = tmp_path / "test.duckdb"
    config.execution.csv_output_path = tmp_path / "test.csv"

    pipeline = WeatherPipeline(config)
    records = pipeline.run()

    # Assertions on returned record payload
    assert len(records) > 0
    assert "location_id" in records[0]
    assert "observation_timestamp" in records[0]

    # Verify DuckDB persistence and table schema
    conn = duckdb.connect(str(config.database.filepath))
    count = conn.execute(
        f"SELECT COUNT(*) FROM {config.database.table_name}"
    ).fetchone()[0]
    assert count == len(records)
    conn.close()

    # Verify CSV Export
    if config.execution.export_csv_on_complete:
        assert config.execution.csv_output_path.exists()


def test_run_pipeline_functional_api(tmp_path: Path):
    """Tests convenience functional wrapper run_pipeline()."""
    config_path = CONFIGS_DIR / "valid_archive.yaml"
    config = ResearchConfig.load_from_yaml(config_path)
    config.database.filepath = tmp_path / "func_test.duckdb"
    config.execution.export_csv_on_complete = False

    temp_yaml = tmp_path / "temp_config.yaml"
    with open(temp_yaml, "w", encoding="utf-8") as f:
        yaml.dump(config.model_dump(mode="json"), f)

    records = run_pipeline(temp_yaml)
    assert isinstance(records, list)
    assert len(records) > 0


def test_invalid_yaml_schema_raises_validation_error():
    """Ensures invalid coordinate or schema values fail early in Pydantic parser."""
    invalid_path = CONFIGS_DIR / "invalid_schema.yaml"
    with pytest.raises(ValidationError):
        ResearchConfig.load_from_yaml(invalid_path)