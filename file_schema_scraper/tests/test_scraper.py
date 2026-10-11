import json

from file_schema_scraper.core import SchemaScraperEngine

def test_multi_variant_scan_and_aggregation(tmp_path):
    input_dir = tmp_path / "raw_data"
    output_dir = tmp_path / "intermediate"
    input_dir.mkdir()

    (input_dir / "users_v1.csv").write_text(
        "user_id,username,score\n"
        "1,alice,95.5\n",
        encoding="utf-8",
    )

    (input_dir / "users_v2.csv").write_text(
        "user_id,username,score,country\n"
        "2,bob,82.0,USA\n",
        encoding="utf-8",
    )

    engine = SchemaScraperEngine(
        str(input_dir),
        str(output_dir),
    )

    intermediate_files = engine.run_scan()

    assert len(intermediate_files) == 2

    aggregated_outputs = engine.run_aggregation()

    assert len(aggregated_outputs) == 2

    for output_file in aggregated_outputs:
        assert output_file.exists()

        contract = json.loads(
            output_file.read_text(encoding="utf-8")
        )

        assert contract["total_source_files"] >= 1
        assert "fields" in contract
        assert contract["format"] == "csv"