from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pyarrow as pa


class BaseReader(ABC):
    """Abstract interface for file readers producing zero-copy Arrow RecordBatch streams."""

    stage: str = "reader"
    type: str

    def __init__(self, file_path: str, config: Optional[Dict[str, Any]] = None):
        self.file_path = file_path
        self.config = config or {}

    @abstractmethod
    def read_batches(self, batch_size: int) -> pa.RecordBatchReader:
        """Returns a PyArrow RecordBatchReader iterator over the source file."""
        pass


class BaseWriter(ABC):
    """Abstract interface for database writers consuming Arrow RecordBatches via bulk protocols."""

    stage: str = "writer"
    type: str

    def __init__(self, connection_string: str, table_name: str, config: Optional[Dict[str, Any]] = None):
        self.connection_string = connection_string
        self.table_name = table_name
        self.config = config or {}

    @abstractmethod
    def write_batch(self, batch: pa.RecordBatch) -> int:
        """Writes a single PyArrow RecordBatch using native bulk protocols."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Flushes remaining buffers and safely closes database connections."""
        pass