from typing import Dict, Any, Optional
import pyarrow as pa
import pyarrow.parquet as pq

from core.base import BaseReader


class ParquetReader(BaseReader):
    """Zero-copy reader for Apache Parquet files using memory-mapped buffers."""

    stage = "reader"
    type = "parquet"

    def read_batches(self, batch_size: int) -> pa.RecordBatchReader:
        """Opens Parquet file and returns a streaming RecordBatchReader."""
        parquet_file = pq.ParquetFile(self.file_path, memory_map=True)
        schema = parquet_file.schema.to_arrow_schema()

        # Generator yielding RecordBatches across row groups
        batch_iter = parquet_file.iter_batches(
            batch_size=batch_size,
            columns=self.config.get("columns", None),
            use_threads=self.config.get("use_threads", True),
        )

        return pa.RecordBatchReader.from_batches(schema, batch_iter)