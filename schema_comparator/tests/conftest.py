import pytest
import pyarrow as pa
import pyarrow.parquet as pq

@pytest.fixture
def sample_datasets(tmp_path):
    path_a = tmp_path / "source_a.parquet"
    path_b = tmp_path / "source_b.parquet"

    # Source A (Baseline)
    schema_a = pa.schema([("id", pa.int64()), ("value", pa.string())])
    table_a = pa.Table.from_arrays([[1, 2, 3], ["A", "B", "C"]], schema=schema_a)
    pq.write_table(table_a, path_a)

    # Source B (Modified): ID 1 updated, ID 2 unchanged, ID 3 deleted, ID 4 inserted, col added
    schema_b = pa.schema([("id", pa.int64()), ("value", pa.string()), ("new_col", pa.int32())])
    table_b = pa.Table.from_arrays([[1, 2, 4], ["UPDATED", "B", "NEW"], [10, 20, 40]], schema=schema_b)
    pq.write_table(table_b, path_b)

    return str(path_a), str(path_b)