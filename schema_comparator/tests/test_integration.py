from click.testing import CliRunner
from schema_comparator.cli import main
from pathlib import Path

def test_cli_integration(sample_datasets, tmp_path):
    path_a, path_b = sample_datasets
    out_delta = str(tmp_path / "delta.parquet")
    out_report = str(tmp_path / "report.md")

    runner = CliRunner()
    result = runner.invoke(main, [
        "--source-a", path_a,
        "--source-b", path_b,
        "--keys", "id",
        "--output-delta", out_delta,
        "--report-md", out_report
    ])

    assert result.exit_code == 0
    assert Path(out_delta).exists()
    assert Path(out_report).exists()