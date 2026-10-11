
from file_schema_scraper.aggregators import (
    CSVAggregator,
    JSONAggregator,
    NDJSONAggregator,
    TXTAggregator,
)

def make_payload(fmt, variant_id, file_schemas, structure_type="tabular"):
    return {
        "format": fmt,
        "structure_type": structure_type,
        "variant_id": variant_id,
        "schema_signature": "test-signature",
        "total_files": len(file_schemas),
        "file_schemas": file_schemas,
    }

def test_aggregator_tracks_subset_fields():
    payload = make_payload(
        "csv",
        "csv_variant_1",
        [
            {
                "file_name": "f1.csv",
                "file_path": "f1.csv",
                "fields": [
                    {"name": "id", "type": "int64"},
                    {"name": "name", "type": "string"},
                ],
                "num_rows": 2,
            },
            {
                "file_name": "f2.csv",
                "file_path": "f2.csv",
                "fields": [
                    {"name": "id", "type": "int64"},
                    {"name": "name", "type": "string"},
                    {"name": "country", "type": "string"},
                ],
                "num_rows": 2,
            },
        ],
    )

    master = CSVAggregator().execute(payload)

    assert master["total_source_files"] == 2
    assert master["total_rows"] == 4

    fields = {field["name"]: field for field in master["fields"]}

    assert fields["id"]["file_coverage_count"] == 2
    assert fields["country"]["file_coverage_count"] == 1
    assert fields["country"]["nullable"] is True
    assert fields["country"]["file_coverage_ratio"] == 0.5

def test_aggregator_promotes_numeric_types():
    payload = make_payload(
        "csv",
        "csv_variant_2",
        [
            {
                "file_name": "f1.csv",
                "file_path": "f1.csv",
                "fields": [{"name": "amount", "type": "int64"}],
                "num_rows": 1,
            },
            {
                "file_name": "f2.csv",
                "file_path": "f2.csv",
                "fields": [{"name": "amount", "type": "float64"}],
                "num_rows": 1,
            },
        ],
    )

    master = CSVAggregator().execute(payload)

    amount = next(
        field for field in master["fields"]
        if field["name"] == "amount"
    )

    assert amount["type"] == "float64"

def test_aggregator_preserves_incompatible_types():
    payload = make_payload(
        "json",
        "json_variant_1",
        [
            {
                "file_name": "a.json",
                "file_path": "a.json",
                "fields": [{"name": "value", "type": "int64"}],
                "num_rows": 1,
            },
            {
                "file_name": "b.json",
                "file_path": "b.json",
                "fields": [{"name": "value", "type": "boolean"}],
                "num_rows": 1,
            },
        ],
        structure_type="json_document",
    )

    master = JSONAggregator().execute(payload)

    value = next(
        field for field in master["fields"]
        if field["name"] == "value"
    )

    assert value["type"] == "union[boolean,int64]"

def test_format_specific_aggregators():
    assert NDJSONAggregator().type == "ndjson"
    assert TXTAggregator().type == "txt"