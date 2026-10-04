import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.csv as pa_csv
import pyarrow.json as pa_json
import duckdb
from schema_comparator.readers.base import BaseReader

class ArrowFileReader(BaseReader):
    """Universal reader for Parquet, CSV, and NDJSON files."""

    def get_schema(self) -> pa.Schema:
        if self.source_path.endswith(".parquet"):
            return pq.read_schema(self.source_path)
        elif self.source_path.endswith(".csv"):
            return pa_csv.open_csv(self.source_path).schema
        elif self.source_path.endswith((".json", ".ndjson")):
            return pa_json.read_json(self.source_path).schema
        else:
            # Fallback to DuckDB scan for schema inference
            conn = duckdb.connect()
            return conn.read_parquet(self.source_path).arrow().schema

    def get_relation(self, conn: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyRelation:
        if self.source_path.endswith(".parquet"):
            return conn.read_parquet(self.source_path)
        elif self.source_path.endswith(".csv"):
            return conn.read_csv(self.source_path)
        elif self.source_path.endswith((".json", ".ndjson")):
            return conn.read_json(self.source_path)
        else:
            return conn.read_parquet(self.source_path)