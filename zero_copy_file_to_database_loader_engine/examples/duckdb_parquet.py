import sys
from pathlib import Path

# Add project root directory to sys.path for module resolution
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
sys.path.append(str(ROOT_DIR))

from core import PluginRegistry, IngestionEngine
from readers import register_readers
from writers import register_writers

# Initialize Registry & Ingestion Engine
registry = PluginRegistry()
register_readers(registry)
register_writers(registry)

engine = IngestionEngine(registry)

# Resolve data paths relative to examples/data/
data_dir = BASE_DIR / "data"
db_path = str(data_dir / "analytics.duckdb")
source_parquet = str(data_dir / "users.parquet")

# Ingest Parquet data via SDK
metrics = engine.run(
    reader_type="parquet",
    writer_type="duckdb",
    file_path=source_parquet,
    connection_string=db_path,
    table_name="users",
    batch_size=25_000,
)

# Output Metrics
print("\nDuckDB Ingestion Metrics:")
print(f"  Total Rows Ingested : {metrics.get('total_rows', 0):,}")
print(f"  Duration (seconds)  : {metrics.get('duration_seconds', 0.0):.2f}s")
print(f"  Rows Per Second     : {metrics.get('rows_per_second', 0):,.2f} rows/sec")