import csv

import yaml

from engine import Engine


def test_yaml_pipeline_end_to_end(tmp_path):
    input_dir = tmp_path / "logs"
    input_dir.mkdir()

    output_file = tmp_path / "output" / "errors.csv"

    log_file = input_dir / "application.log"

    log_file.write_text(
        "\n".join([
            "2026-09-13 INFO 200 GET /api/users",
            "2026-09-13 ERROR 500 GET /api/orders Database failed",
            "2026-09-13 INFO 200 POST /api/login",
            "2026-09-13 ERROR 503 GET /api/payments Payment unavailable",
        ]),
        encoding="utf-8",
    )

    config = {
        "scan": {
            "discovery": {
                "type": "glob",
                "config": {
                    "path": str(input_dir / "*.log"),
                },
            },
            "reader": {
                "type": "text",
                "config": {
                    "encoding": "utf-8",
                },
            },
            "parser": [
                {
                    "type": "regex",
                    "config": {
                        "pattern": (
                            r"(?P<date>\S+)[ \t]+"
                            r"(?P<level>\w+)[ \t]+"
                            r"(?P<status_code>\d+)[ \t]+"
                            r"(?P<method>\w+)[ \t]+"
                            r"(?P<path>\S+)"
                            r"(?:[ \t]+(?P<message>[^\r\n]*))?"
                        ),
                    },
                }
            ],
            "processing": [
                {
                    "type": "filter",
                    "config": {
                        "field": "level",
                        "equals": "ERROR",
                    },
                }
            ],
            "output": {
                "type": "csv",
                "config": {
                    "path": str(output_file),
                },
            },
        }
    }

    # Serialize and load the configuration through YAML.
    # This verifies that the configuration is YAML-compatible
    # without manually constructing YAML containing Windows paths.
    yaml_config = yaml.safe_dump(config)

    loaded_config = yaml.safe_load(yaml_config)

    Engine(loaded_config).run()

    assert output_file.exists()

    with output_file.open(
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2

    assert rows[0]["level"] == "ERROR"
    assert rows[0]["status_code"] == "500"
    assert rows[0]["message"] == "Database failed"

    assert rows[1]["level"] == "ERROR"
    assert rows[1]["status_code"] == "503"
    assert rows[1]["message"] == "Payment unavailable"
