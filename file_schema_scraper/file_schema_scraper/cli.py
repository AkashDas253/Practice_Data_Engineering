
import click

from .core import SchemaScraperEngine, registry

@click.group()
def cli():
    """Discover and validate schemas across heterogeneous file formats."""

@cli.command()
@click.option("--input-dir", required=True, type=click.Path(exists=True))
@click.option("--output-dir", required=True, type=click.Path())
def scan(input_dir, output_dir):
    """Discover file structures and generate schema variants."""
    SchemaScraperEngine(input_dir, output_dir).run_scan()

@cli.command()
@click.option("--output-dir", required=True, type=click.Path(exists=True))
def aggregate(output_dir):
    """Generate master schema contracts from discovered variants."""
    SchemaScraperEngine(output_dir, output_dir).run_aggregation()

@cli.command()
@click.option("--input-dir", required=True, type=click.Path(exists=True))
@click.option("--output-dir", required=True, type=click.Path())
def run(input_dir, output_dir):
    """Run discovery, validation, and aggregation."""
    engine = SchemaScraperEngine(input_dir, output_dir)
    engine.run_scan()
    engine.run_aggregation()

@cli.command("components")
def list_components():
    """Display registered pipeline components."""
    from . import scanners, validators, aggregators  # noqa: F401

    for component in registry.available():
        click.echo(component)

if __name__ == "__main__":
    cli()