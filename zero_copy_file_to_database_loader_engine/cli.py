import argparse
import sys
from core import PluginRegistry, IngestionEngine
from readers import register_readers
from writers import register_writers


def main():
    parser = argparse.ArgumentParser(
        description="Zero-Copy File-to-Database Loader Engine (db-ingestor)"
    )
    parser.add_argument(
        "--reader",
        required=True,
        choices=["parquet", "csv", "ndjson"],
        help="Source file reader type",
    )
    parser.add_argument(
        "--writer",
        required=True,
        choices=["postgres", "duckdb", "clickhouse"],
        help="Target database writer type",
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Path to input source file",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Target database connection string or database path",
    )
    parser.add_argument(
        "--table",
        required=True,
        help="Target database table name",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50000,
        help="Batch row size limit (default: 50000)",
    )

    args = parser.parse_args()

    # 1. Initialize Registry & Register Components
    registry = PluginRegistry()
    register_readers(registry)
    register_writers(registry)

    # 2. Initialize Engine & Execute Pipeline
    engine = IngestionEngine(registry)
    print(f"Starting ingestion: {args.source} -> {args.writer}:{args.table}")

    try:
        metrics = engine.run(
            reader_type=args.reader,
            writer_type=args.writer,
            file_path=args.source,
            connection_string=args.target,
            table_name=args.table,
            batch_size=args.batch_size,
        )

        print("\nIngestion completed successfully!")
        print(f"Total Rows Ingested : {metrics['total_rows']:,}")
        print(f"Total Batches       : {metrics['total_batches']}")
        print(f"Elapsed Time        : {metrics['elapsed_seconds']}s")
        print(f"Throughput          : {metrics['rows_per_second']:,} rows/sec")

    except Exception as e:
        print(f"\nIngestion failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()