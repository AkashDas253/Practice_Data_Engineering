from typing import Iterator, Optional
import pyarrow as pa


class BatchController:
    """Enforces batch size limits and memory constraints across streaming Arrow batches."""

    def __init__(self, default_batch_size: int = 50000):
        self.default_batch_size = default_batch_size

    def process_stream(self, batch_reader: pa.RecordBatchReader) -> Iterator[pa.RecordBatch]:
        """Yields RecordBatches ensuring row counts conform to configured thresholds."""
        for batch in batch_reader:
            if batch.num_rows == 0:
                continue

            # Slice oversized batches to enforce strict maximum batch boundaries
            if batch.num_rows > self.default_batch_size:
                offset = 0
                while offset < batch.num_rows:
                    length = min(self.default_batch_size, batch.num_rows - offset)
                    yield batch.slice(offset, length)
                    offset += length
            else:
                yield batch