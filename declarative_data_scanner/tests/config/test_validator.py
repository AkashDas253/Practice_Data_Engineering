import pytest
from pydantic import ValidationError

from config.loader import ConfigLoader
from config.schema import ApplicationConfig
from config.validator import ConfigValidator


def test_validate_valid_configuration():
    data = ConfigLoader().load("tests/configs/valid.yaml")

    config = ConfigValidator().validate(data)

    assert isinstance(config, ApplicationConfig)

    assert len(config.scans) == 2

    application = config.scans["application_logs"]

    assert application.source.type == "file"
    assert application.source.path == "./logs/application/*.log"

    assert application.discovery.type == "glob"
    assert application.reader.type == "text"

    assert len(application.parser.modules) == 2

    assert (
        application.parser.modules[0].type
        == "regex_matcher"
    )

    assert (
        application.parser.modules[1].type
        == "timestamp_normalizer"
    )

    assert len(application.processing.modules) == 2

    assert (
        application.processing.modules[0].type
        == "filter"
    )

    assert application.output.type == "duckdb"
    assert application.state.enabled is True


def test_multiple_scans_are_preserved():
    data = ConfigLoader().load("tests/configs/valid.yaml")

    config = ConfigValidator().validate(data)

    assert list(config.scans.keys()) == [
        "application_logs",
        "audit_logs",
    ]


def test_parser_module_order_is_preserved():
    data = ConfigLoader().load("tests/configs/valid.yaml")

    config = ConfigValidator().validate(data)

    modules = config.scans["application_logs"].parser.modules

    assert modules[0].type == "regex_matcher"
    assert modules[1].type == "timestamp_normalizer"


def test_processing_module_order_is_preserved():
    data = ConfigLoader().load("tests/configs/valid.yaml")

    config = ConfigValidator().validate(data)

    modules = config.scans["application_logs"].processing.modules

    assert modules[0].type == "filter"
    assert modules[1].type == "select"


def test_invalid_configuration():
    data = ConfigLoader().load("tests/configs/invalid.yaml")

    with pytest.raises(ValidationError):
        ConfigValidator().validate(data)


def test_unknown_field_is_rejected():
    data = {
        "scans": {
            "test": {
                "source": {
                    "type": "file",
                    "path": "./test.log",
                    "unknown_field": True,
                },
                "discovery": {
                    "type": "glob",
                },
                "reader": {
                    "type": "text",
                },
                "parser": {
                    "modules": [],
                },
                "output": {
                    "type": "csv",
                },
            }
        }
    }

    with pytest.raises(ValidationError):
        ConfigValidator().validate(data)
