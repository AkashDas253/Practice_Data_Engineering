from typing import Dict, Any, Optional
import duckdb
import pyarrow as pa

from core.base import BaseWriter


class DuckDBWriter(BaseWriter):
    """Zero-copy writer for DuckDB using direct PyArrow table binding."""

    stage = "writer"
    type = "duckdb"

    def __init__(self, connection_string: str, table_name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(connection_string, table_name, config)
        # connection_string can be a file path like 'analytics.duckdb' or ':memory:'
        self.conn = duckdb.connect(self.connection_string)
        self._table_initialized = False

    def write_batch(self, batch: pa.RecordBatch) -> int:
        """Registers the Arrow batch as a virtual DuckDB view and inserts rows directly."""
        if batch.num_rows == 0:
            return 0

        # Convert Arrow batch to Arrow Table for DuckDB registration
        arrow_table = pa.Table.from_batches([batch])

        # Zero-copy registration of Arrow data into DuckDB process memory
        self.conn.register("_temp_arrow_batch", arrow_table)

        # Automatically create table matching Arrow schema on first batch if it does not exist
        if not self._table_initialized:
            self.conn.execute(
                f'CREATE TABLE IF NOT EXISTS "{self.table_name}" AS SELECT * FROM _temp_arrow_batch WHERE 1=0'
            )
            self._table_initialized = True

        # Execute batch insert
        self.conn.execute(f'INSERT INTO "{self.table_name}" SELECT * FROM _temp_arrow_batch')
        self.conn.unregister("_temp_arrow_batch")

        return batch.num_rows

    def close(self) -> None:
        """Flushes and closes DuckDB connection."""
        if hasattr(self, "conn") and self.conn:
            self.conn.close()