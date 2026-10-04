from schema_comparator.readers.base import BaseReader
from schema_comparator.readers.arrow import ArrowFileReader
from schema_comparator.readers.duckdb import DuckDBTableReader

def get_reader(source: str) -> BaseReader:
    if source.endswith((".parquet", ".csv", ".json", ".ndjson")):
        return ArrowFileReader(source)
    return DuckDBTableReader(source)