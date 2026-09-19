import sys
from pathlib import Path

# Add project root directory to sys.path for module resolution
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
sys.path.append(str(ROOT_DIR))

from core import PluginRegistry, IngestionEngine
from readers import register_readers
from writers import register_writers

# Initialize Registry & Core Engine
registry = PluginRegistry()
register_readers(registry)
register_writers(registry)

engine = IngestionEngine(registry)

# Resolve data paths relative to examples/data/
data_dir = BASE_DIR / "data"
source_csv = str(data_dir / "transactions.csv")
pg_uri = "postgresql://postgres:password@localhost:5432/mydb"

# Execute CSV Ingestion via SDK (Auto-DDL creates table if missing)
metrics = engine.run(
    reader_type="csv",
    writer_type="postgres",
    file_path=source_csv,
    connection_string=pg_uri,
    table_name="transactions",
    batch_size=50_000,
)

# Output Metrics
print("\nPostgreSQL Ingestion Metrics:")
print(f"  Total Rows Ingested : {metrics.get('total_rows', 0):,}")
print(f"  Duration (seconds)  : {metrics.get('duration_seconds', 0.0):.2f}s")
print(f"  Rows Per Second     : {metrics.get('rows_per_second', 0):,.2f} rows/sec")