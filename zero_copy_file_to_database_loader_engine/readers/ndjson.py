from typing import Dict, Any, Optional
import pyarrow as pa
import pyarrow.dataset as ds

from core.base import BaseReader


class NDJSONReader(BaseReader):
    """Zero-copy reader for newline-delimited JSON (NDJSON) files."""

    stage = "reader"
    type = "ndjson"

    def read_batches(self, batch_size: int) -> pa.RecordBatchReader:
        """Constructs a Arrow Dataset scanner to stream JSON batches."""
        json_format = ds.JsonFileFormat(
            read_options=ds.JsonReadOptions(
                block_size=self.config.get("block_size", 16 * 1024 * 1024)
            )
        )

        dataset = ds.dataset(
            self.file_path,
            format=json_format,
            schema=self.config.get("explicit_schema", None),
        )

        scanner = dataset.scanner(
            batch_size=batch_size,
            use_threads=self.config.get("use_threads", True),
        )

        return scanner.to_reader()