import pytest

from validators.config import ConfigValidator


def test_valid_config():
    config = {
        "scan": {
            "discovery": {
                "type": "glob",
                "config": {},
            },
            "reader": {
                "type": "text",
                "config": {},
            },
            "parser": [
                {
                    "type": "regex",
                    "config": {},
                }
            ],
            "output": {
                "type": "csv",
                "config": {},
            },
        }
    }

    ConfigValidator().validate(config)


def test_missing_scan_fails():
    with pytest.raises(ValueError, match="Missing 'scan'"):
        ConfigValidator().validate({})


def test_missing_required_stage_fails():
    config = {
        "scan": {
            "discovery": {},
        }
    }

    with pytest.raises(ValueError, match="Missing required stage"):
        ConfigValidator().validate(config)


def test_processing_is_optional():
    config = {
        "scan": {
            "discovery": {},
            "reader": {},
            "parser": [],
            "output": {},
        }
    }

    ConfigValidator().validate(config)

    assert config["scan"]["processing"] == []
