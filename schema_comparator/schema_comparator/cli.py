import click
from schema_comparator.inspector import inspect_schema_drift
from schema_comparator.cdc_engine import compute_cdc
from schema_comparator.reporter import export_results

@click.command()
@click.option("--source-a", required=True, help="Path to baseline source (file/table)")
@click.option("--source-b", required=True, help="Path to target source (file/table)")
@click.option("--keys", required=True, help="Comma-separated primary keys")
@click.option("--output-delta", required=True, help="Output Parquet path for CDC deltas")
@click.option("--report-md", required=True, help="Output Markdown path for summary report")
def main(source_a: str, source_b: str, keys: str, output_delta: str, report_md: str):
    pk_list = [k.strip() for k in keys.split(",")]
    
    click.echo("[1/3] Inspecting Schema Drift...")
    drift = inspect_schema_drift(source_a, source_b)

    click.echo("[2/3] Executing Zero-Copy CDC Engine...")
    cdc = compute_cdc(source_a, source_b, pk_list)

    click.echo("[3/3] Exporting Results...")
    export_results(drift, cdc, output_delta, report_md)

    click.echo("✓ Pipeline execution complete.")

if __name__ == "__main__":
    main()