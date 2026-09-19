import io
from typing import Dict, Any, Optional
import pyarrow as pa
import pyarrow.csv as pa_csv
import psycopg

from core.base import BaseWriter


def arrow_to_pg_type(arrow_type: pa.DataType) -> str:
    """Helper to map PyArrow data types to PostgreSQL data types."""
    if pa.types.is_int64(arrow_type):
        return "BIGINT"
    elif pa.types.is_int32(arrow_type) or pa.types.is_int16(arrow_type) or pa.types.is_int8(arrow_type):
        return "INTEGER"
    elif pa.types.is_float64(arrow_type):
        return "DOUBLE PRECISION"
    elif pa.types.is_float32(arrow_type):
        return "REAL"
    elif pa.types.is_boolean(arrow_type):
        return "BOOLEAN"
    elif pa.types.is_timestamp(arrow_type) or pa.types.is_date(arrow_type):
        return "TIMESTAMP"
    else:
        return "TEXT"


class PostgresCopyWriter(BaseWriter):
    """High-throughput PostgreSQL writer utilizing native COPY FROM STDIN binary/CSV streaming."""

    stage = "writer"
    type = "postgres"

    def __init__(self, connection_string: str, table_name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(connection_string, table_name, config)
        self.conn = psycopg.connect(self.connection_string)
        self.conn.autocommit = False
        self._table_initialized = False

    def write_batch(self, batch: pa.RecordBatch) -> int:
        """Converts RecordBatch into a memory stream and issues COPY FROM STDIN."""
        if batch.num_rows == 0:
            return 0

        # Auto-create target PostgreSQL table from Arrow schema if missing
        if not self._table_initialized:
            col_defs = [f'"{field.name}" {arrow_to_pg_type(field.type)}' for field in batch.schema]
            create_sql = f'CREATE TABLE IF NOT EXISTS "{self.table_name}" ({", ".join(col_defs)})'
            
            with self.conn.cursor() as cursor:
                cursor.execute(create_sql)
            self.conn.commit()
            self._table_initialized = True

        # Convert Arrow batch to in-memory CSV buffer
        sink = io.BytesIO()
        write_options = pa_csv.WriteOptions(include_header=False)
        pa_csv.write_csv(batch, sink, write_options=write_options)
        sink.seek(0)

        # Build SQL COPY statement
        columns = ", ".join([f'"{name}"' for name in batch.schema.names])
        copy_sql = f'COPY "{self.table_name}" ({columns}) FROM STDIN WITH (FORMAT csv, HEADER false)'

        with self.conn.cursor() as cursor:
            with cursor.copy(copy_sql) as copy:
                while chunk := sink.read(64 * 1024):  # Stream 64KB chunks
                    copy.write(chunk)

        self.conn.commit()
        return batch.num_rows

    def close(self) -> None:
        """Closes PostgreSQL database connection."""
        if hasattr(self, "conn") and self.conn:
            self.conn.close()