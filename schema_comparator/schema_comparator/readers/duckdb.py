import pyarrow as pa
import duckdb
from schema_comparator.readers.base import BaseReader

class DuckDBTableReader(BaseReader):
    """Reader for DuckDB database tables, views, or queries."""

    def __init__(self, source_path: str, db_path: str = ":memory:"):
        super().__init__(source_path)
        self.db_path = db_path

    def get_schema(self) -> pa.Schema:
        conn = duckdb.connect(self.db_path)
        rel = conn.table(self.source_path)
        return rel.arrow().schema

    def get_relation(self, conn: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyRelation:
        if self.db_path != ":memory:":
            conn.execute(f"ATTACH '{self.db_path}' AS external_db;")
            return conn.table(f"external_db.{self.source_path}")
        return conn.table(self.source_path)