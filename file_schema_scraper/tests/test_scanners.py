from file_schema_scraper.scanners import (
    CSVScanner,
    JSONScanner,
    NDJSONScanner,
    TXTScanner,
    UniversalScanner,
)

def test_universal_scanner_detects_csv(sample_data_dir):
    result = UniversalScanner().execute(
        str(sample_data_dir / "test.csv")
    )

    assert result["format"] == "csv"
    assert len(result["fields"]) == 3
    assert result["num_rows"] == 2
    assert result["fields"][0]["name"] == "id"

def test_universal_scanner_detects_json(sample_data_dir):
    result = UniversalScanner().execute(
        str(sample_data_dir / "test.json")
    )

    assert result["format"] == "json"
    assert result["num_rows"] == 2

    field_names = {field["name"] for field in result["fields"]}
    assert {"item_id", "status", "extra"} <= field_names

def test_csv_type_inference(sample_data_dir):
    result = CSVScanner().execute(
        str(sample_data_dir / "test.csv")
    )

    fields = {field["name"]: field for field in result["fields"]}

    assert fields["id"]["type"] == "int64"
    assert fields["amount"]["type"] == "float64"

def test_json_optional_fields(sample_data_dir):
    result = JSONScanner().execute(
        str(sample_data_dir / "test.json")
    )

    fields = {field["name"]: field for field in result["fields"]}

    assert "extra" in fields
    assert fields["extra"]["nullable"] is True

def test_ndjson_scanner(sample_data_dir):
    result = NDJSONScanner().execute(
        str(sample_data_dir / "test.ndjson")
    )

    assert result["format"] == "ndjson"
    assert result["num_rows"] == 2

    field_names = {field["name"] for field in result["fields"]}
    assert "item_id" in field_names
    assert "extra" in field_names

def test_ndjson_invalid_lines_are_reported(sample_data_dir):
    result = NDJSONScanner().execute(
        str(sample_data_dir / "test_invalid.ndjson")
    )

    assert result["num_rows"] == 2
    assert len(result["structure"]["invalid_lines"]) == 1

def test_pipe_delimited_txt(sample_data_dir):
    result = UniversalScanner().execute(
        str(sample_data_dir / "test_pipe.txt")
    )

    assert result["format"] == "txt"
    assert result["structure_type"] == "delimited"
    assert result["structure"]["delimiter"] == "|"

def test_semicolon_delimited_txt(sample_data_dir):
    result = UniversalScanner().execute(
        str(sample_data_dir / "test_semicolon.txt")
    )

    assert result["structure_type"] == "delimited"
    assert result["structure"]["delimiter"] == ";"

def test_key_value_txt(sample_data_dir):
    result = UniversalScanner().execute(
        str(sample_data_dir / "test_key_value.txt")
    )

    assert result["structure_type"] == "key_value"

    field_names = {field["name"] for field in result["fields"]}
    assert {"id", "name", "active"} <= field_names

def test_plain_txt_has_no_structured_fields(sample_data_dir):
    result = UniversalScanner().execute(
        str(sample_data_dir / "test_plain.txt")
    )

    assert result["format"] == "txt"
    assert result["structure_type"] == "plain_text"
    assert result["fields"] == []