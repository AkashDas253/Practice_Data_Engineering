from pathlib import Path
from unittest.mock import patch
import pytest
import yaml

from cli import main
from config_parser import ResearchConfig


def test_cli_successful_run(tmp_path: Path):
    """Tests CLI entrypoint execution with valid configuration argument."""
    config_path = Path(__file__).parent / "configs" / "valid_archive.yaml"
    config = ResearchConfig.load_from_yaml(config_path)
    config.database.filepath = tmp_path / "cli_test.duckdb"
    config.execution.export_csv_on_complete = False

    temp_yaml = tmp_path / "cli_config.yaml"
    with open(temp_yaml, "w", encoding="utf-8") as f:
        yaml.dump(config.model_dump(mode="json"), f)

    test_args = ["cli.py", "--config", str(temp_yaml)]
    with patch("sys.argv", test_args):
        # Successful run exits cleanly without raising SystemExit
        main()


def test_cli_missing_config_file_raises_exit():
    """Ensures CLI gracefully exits with non-zero code when config file is missing."""
    test_args = ["cli.py", "--config", "non_existent_config.yaml"]
    with patch("sys.argv", test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1