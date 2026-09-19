from typing import Dict, Any, Optional
import clickhouse_connect
import pyarrow as pa

from core.base import BaseWriter


def arrow_to_clickhouse_type(arrow_type: pa.DataType) -> str:
    """Helper to map PyArrow data types to ClickHouse data types."""
    if pa.types.is_int64(arrow_type):
        return "Int64"
    elif pa.types.is_int32(arrow_type):
        return "Int32"
    elif pa.types.is_float64(arrow_type):
        return "Float64"
    elif pa.types.is_float32(arrow_type):
        return "Float32"
    elif pa.types.is_boolean(arrow_type):
        return "Bool"
    elif pa.types.is_timestamp(arrow_type) or pa.types.is_date(arrow_type):
        return "DateTime"
    else:
        return "String"


class ClickHouseArrowWriter(BaseWriter):
    """Native bulk writer for ClickHouse using binary Arrow streaming format."""

    stage = "writer"
    type = "clickhouse"

    def __init__(self, connection_string: str, table_name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(connection_string, table_name, config)

        # Parse connection params from config or connection_string
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 8123)
        username = self.config.get("username", "default")
        password = self.config.get("password", "")
        database = self.config.get("database", "default")

        self.client = clickhouse_connect.get_client(
            host=host,
            port=port,
            username=username,
            password=password,
            database=database,
        )
        self._table_initialized = False

    def write_batch(self, batch: pa.RecordBatch) -> int:
        """Pushes an Arrow RecordBatch directly into ClickHouse."""
        if batch.num_rows == 0:
            return 0

        # Auto-create target ClickHouse table from Arrow schema if missing
        if not self._table_initialized:
            col_defs = [f"`{field.name}` {arrow_to_clickhouse_type(field.type)}" for field in batch.schema]
            create_sql = (
                f"CREATE TABLE IF NOT EXISTS `{self.table_name}` ({', '.join(col_defs)}) "
                f"ENGINE = MergeTree() ORDER BY tuple()"
            )
            self.client.command(create_sql)
            self._table_initialized = True

        arrow_table = pa.Table.from_batches([batch])
        self.client.insert_arrow(self.table_name, arrow_table)
        return batch.num_rows

    def close(self) -> None:
        """Closes ClickHouse client connection."""
        if hasattr(self, "client") and self.client:
            self.client.close()