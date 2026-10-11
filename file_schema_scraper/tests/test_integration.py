import json

from file_schema_scraper.core import SchemaScraperEngine

def test_end_to_end_engine_pipeline(sample_data_dir, tmp_path):
    output_dir = tmp_path / "schemas"

    engine = SchemaScraperEngine(
        str(sample_data_dir),
        str(output_dir),
    )

    intermediate_files = engine.run_scan()

    assert intermediate_files

    aggregated_outputs = engine.run_aggregation()

    assert aggregated_outputs

    formats_found = set()

    for path in aggregated_outputs:
        contract = json.loads(
            path.read_text(encoding="utf-8")
        )

        formats_found.add(contract["format"])

        assert contract["total_source_files"] >= 1
        assert isinstance(contract["fields"], list)

    assert {"csv", "json", "ndjson", "txt"} <= formats_found