from pathlib import Path

import pytest

from config.loader import ConfigLoader


def test_load_valid_yaml():
    path = Path("tests/configs/valid.yaml")

    data = ConfigLoader().load(path)

    assert isinstance(data, dict)
    assert "scans" in data
    assert "application_logs" in data["scans"]
    assert "audit_logs" in data["scans"]


def test_load_empty_yaml(tmp_path):
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")

    data = ConfigLoader().load(path)

    assert data == {}


def test_load_missing_file():
    loader = ConfigLoader()

    with pytest.raises(FileNotFoundError):
        loader.load("does-not-exist.yaml")


def test_load_non_mapping_root(tmp_path):
    path = tmp_path / "invalid.yaml"
    path.write_text("- item1\n- item2\n", encoding="utf-8")

    with pytest.raises(ValueError, match="root must be a mapping"):
        ConfigLoader().load(path)
