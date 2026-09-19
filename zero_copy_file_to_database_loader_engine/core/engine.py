import time
from typing import Dict, Any, Optional
import pyarrow as pa

from core.registry import PluginRegistry
from core.aligner import SchemaAligner
from core.controller import BatchController


class IngestionEngine:
    """Main orchestrator for zero-copy file-to-database ingestion pipelines."""

    def __init__(self, registry: PluginRegistry):
        self.registry = registry

    def run(
        self,
        reader_type: str,
        writer_type: str,
        file_path: str,
        connection_string: str,
        table_name: str,
        batch_size: int = 50000,
        reader_config: Optional[Dict[str, Any]] = None,
        writer_config: Optional[Dict[str, Any]] = None,
        target_schema: Optional[pa.Schema] = None,
    ) -> Dict[str, Any]:
        """Executes the ingestion pipeline end-to-end."""
        start_time = time.perf_counter()

        # 1. Resolve components from registry
        ReaderClass = self.registry.resolve("reader", reader_type)
        WriterClass = self.registry.resolve("writer", writer_type)

        # 2. Instantiate components
        reader = ReaderClass(file_path=file_path, config=reader_config)
        writer = WriterClass(connection_string=connection_string, table_name=table_name, config=writer_config)

        aligner = SchemaAligner(target_schema=target_schema)
        controller = BatchController(default_batch_size=batch_size)

        total_rows = 0
        total_batches = 0

        try:
            # 3. Stream zero-copy Arrow batches
            batch_stream = reader.read_batches(batch_size=batch_size)

            # 4. Align, control, and write batches
            for raw_batch in controller.process_stream(batch_stream):
                aligned_batch = aligner.align_batch(raw_batch)
                rows_written = writer.write_batch(aligned_batch)
                
                total_rows += rows_written if rows_written is not None else aligned_batch.num_rows
                total_batches += 1

        finally:
            writer.close()

        elapsed_seconds = time.perf_counter() - start_time
        rows_per_second = total_rows / elapsed_seconds if elapsed_seconds > 0 else 0.0

        return {
            "status": "SUCCESS",
            "total_rows": total_rows,
            "total_batches": total_batches,
            "elapsed_seconds": round(elapsed_seconds, 4),
            "rows_per_second": round(rows_per_second, 2),
        }