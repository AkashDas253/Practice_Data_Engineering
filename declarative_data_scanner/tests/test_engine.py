import pytest

from engine import Engine


def valid_config():
    return {
        "scan": {
            "discovery": {
                "type": "glob",
                "config": {
                    "path": "./data/*.log",
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
                            r"(?P<date>\S+)\s+"
                            r"(?P<level>\w+)\s+"
                            r"(?P<status_code>\d+)\s+"
                            r"(?P<method>\w+)\s+"
                            r"(?P<path>\S+)"
                            r"(?:\s+(?P<message>.*))?"
                        ),
                    },
                }
            ],
            "processing": [],
            "output": {
                "type": "csv",
                "config": {
                    "path": "./data/output.csv",
                },
            },
        }
    }


def test_valid_config():
    engine = Engine(valid_config())

    assert engine.validate() is None


def test_missing_scan():
    engine = Engine({})

    with pytest.raises(
        ValueError,
        match="Missing 'scan' configuration",
    ):
        engine.validate()


def test_missing_stage():
    config = valid_config()

    del config["scan"]["reader"]

    engine = Engine(config)

    with pytest.raises(
        ValueError,
        match="Missing required stage: reader",
    ):
        engine.validate()


def test_build_pipeline():
    engine = Engine(valid_config())

    pipeline = engine.build_pipeline()

    stages = [stage for stage, _ in pipeline]

    assert stages == [
        "discovery",
        "reader",
        "parser",
        "output",
    ]


def test_build_pipeline_with_processing():
    config = valid_config()

    config["scan"]["processing"] = [
        {
            "type": "filter",
            "config": {
                "field": "level",
                "equals": "ERROR",
            },
        }
    ]

    engine = Engine(config)

    pipeline = engine.build_pipeline()

    stages = [stage for stage, _ in pipeline]

    assert stages == [
        "discovery",
        "reader",
        "parser",
        "processing",
        "output",
    ]


def test_multiple_processing_components():
    config = valid_config()

    config["scan"]["processing"] = [
        {
            "type": "filter",
            "config": {
                "field": "level",
                "equals": "ERROR",
            },
        },
        {
            "type": "filter",
            "config": {
                "field": "status_code",
                "equals": "500",
            },
        },
    ]

    engine = Engine(config)

    pipeline = engine.build_pipeline()

    processing_components = [
        component
        for stage, component in pipeline
        if stage == "processing"
    ]

    assert len(processing_components) == 2


def test_run_end_to_end(tmp_path):
    log_file = tmp_path / "app.log"

    log_file.write_text(
        "2026-09-13 ERROR 500 GET /api/test Failed",
        encoding="utf-8",
    )

    output_file = tmp_path / "output" / "result.csv"

    config = valid_config()

    config["scan"]["discovery"]["config"]["path"] = str(
        tmp_path / "*.log"
    )

    config["scan"]["output"]["config"]["path"] = str(
        output_file
    )

    engine = Engine(config)

    result = engine.run()

    assert output_file.exists()
    assert result == str(output_file)
