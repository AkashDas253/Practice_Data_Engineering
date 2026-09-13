from pathlib import Path

from modules.discovery.glob import GlobDiscovery


def test_glob_discovers_matching_files(tmp_path):
    (tmp_path / "app.log").write_text(
        "hello",
        encoding="utf-8",
    )

    (tmp_path / "error.log").write_text(
        "error",
        encoding="utf-8",
    )

    (tmp_path / "readme.txt").write_text(
        "ignore",
        encoding="utf-8",
    )

    component = GlobDiscovery({
        "path": str(tmp_path / "*.log"),
    })

    result = component.execute()

    assert len(result) == 2
    assert str(tmp_path / "app.log") in result
    assert str(tmp_path / "error.log") in result
    assert str(tmp_path / "readme.txt") not in result
