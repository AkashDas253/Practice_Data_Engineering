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
source_ndjson = str(data_dir / "events.json")

# Execute NDJSON Ingestion via SDK (Auto-DDL creates table if missing)
metrics = engine.run(
    reader_type="ndjson",
    writer_type="clickhouse",
    file_path=source_ndjson,
    connection_string="http://localhost:8123",
    table_name="app_events",
    batch_size=100_000,
    writer_config={
        "host": "localhost",
        "port": 8123,
        "database": "default",
    },
)

# Output Metrics
print("\nClickHouse Ingestion Metrics:")
print(f"  Total Rows Ingested : {metrics.get('total_rows', 0):,}")
print(f"  Duration (seconds)  : {metrics.get('duration_seconds', 0.0):.2f}s")
print(f"  Rows Per Second     : {metrics.get('rows_per_second', 0):,.2f} rows/sec")