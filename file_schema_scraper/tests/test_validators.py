from file_schema_scraper.validators import (
    CSVValidator,
    JSONValidator,
    NDJSONValidator,
    SchemaStructureValidator,
    TXTValidator,
)

def test_schema_validator_detects_duplicate_fields():
    result = SchemaStructureValidator().execute({
        "format": "csv",
        "structure_type": "delimited",
        "fields": [
            {"name": "id", "type": "int64"},
            {"name": "id", "type": "string"},
        ],
    })

    assert result["status"] == "failed"
    assert any(
        issue["rule"] == "SCHEMA_DUPLICATE_FIELDS"
        for issue in result["issues"]
    )

def test_csv_validator_detects_inconsistent_rows():
    result = CSVValidator().execute({
        "num_rows": 2,
        "structure": {
            "row_width_errors": 1,
            "duplicate_headers": False,
        },
    })

    assert result["status"] == "warning"

def test_json_validator_accepts_object_records():
    result = JSONValidator().execute({
        "num_rows": 2,
        "structure": {"root_kind": "array"},
    })

    assert result["status"] == "passed"

def test_ndjson_validator_detects_invalid_lines():
    result = NDJSONValidator().execute({
        "structure": {
            "invalid_lines": [{"line": 2, "message": "Invalid JSON"}],
            "non_object_records": 0,
        },
    })

    assert result["status"] == "failed"

def test_txt_validator_reports_unresolved_structure(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("Plain text\n", encoding="utf-8")

    result = TXTValidator().execute({
        "file_path": str(path),
        "structure_type": "plain_text",
        "structure": {},
    })

    assert any(
        issue["rule"] == "TXT_SCHEMA_UNRESOLVED"
        for issue in result["issues"]
    )