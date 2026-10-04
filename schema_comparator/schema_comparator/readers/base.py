from abc import ABC, abstractmethod
import pyarrow as pa
import duckdb

class BaseReader(ABC):
    """Abstract interface for dataset readers."""

    def __init__(self, source_path: str):
        self.source_path = source_path

    @abstractmethod
    def get_schema(self) -> pa.Schema:
        """Extracts PyArrow schema metadata without scanning row bodies."""
        pass

    @abstractmethod
    def get_relation(self, conn: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyRelation:
        """Registers source with DuckDB connection and returns a DuckDB relation."""
        pass