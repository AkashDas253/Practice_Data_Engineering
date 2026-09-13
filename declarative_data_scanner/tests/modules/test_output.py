import csv

from modules.output.csv import CSVOutput


def test_csv_output_creates_parent_directory(tmp_path):
    output = tmp_path / "nested" / "data" / "results.csv"

    component = CSVOutput({
        "path": str(output),
    })

    data = [
        {
            "level": "ERROR",
            "status_code": "500",
            "message": "Database failed",
        },
        {
            "level": "ERROR",
            "status_code": "503",
            "message": "Service unavailable",
        },
    ]

    result = component.execute(data)

    assert output.exists()
    assert result == str(output)

    with output.open(
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2
    assert rows[0]["level"] == "ERROR"
    assert rows[0]["status_code"] == "500"
    assert rows[1]["status_code"] == "503"


def test_csv_output_handles_empty_data(tmp_path):
    output = tmp_path / "results.csv"

    component = CSVOutput({
        "path": str(output),
    })

    result = component.execute([])

    assert result is None
    assert not output.exists()
