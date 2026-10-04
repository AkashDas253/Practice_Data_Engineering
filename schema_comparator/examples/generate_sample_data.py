from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq

def generate_datasets():
    data_dir = Path("examples/data")
    data_dir.mkdir(parents=True, exist_ok=True)

    path_a = data_dir / "baseline.parquet"
    path_b = data_dir / "target.parquet"

    # Baseline (Source A)
    schema_a = pa.schema([
        ("user_id", pa.int64()),
        ("email", pa.string()),
        ("legacy_code", pa.string()),
        ("score", pa.int32())
    ])
    table_a = pa.Table.from_arrays([
        [101, 102, 103, 104],
        ["alice@example.com", "bob@example.com", "charlie@example.com", "david@example.com"],
        ["OLD_A", "OLD_B", "OLD_C", "OLD_D"],
        [85, 90, 78, 92]
    ], schema=schema_a)
    pq.write_table(table_a, path_a)

    # Target (Source B)
    # Drift: Added 'department', Dropped 'legacy_code'
    # Mutations: 101 updated, 102 unchanged, 103 deleted, 105 inserted
    schema_b = pa.schema([
        ("user_id", pa.int64()),
        ("email", pa.string()),
        ("score", pa.int32()),
        ("department", pa.string())
    ])
    table_b = pa.Table.from_arrays([
        [101, 102, 105],
        ["alice_new@example.com", "bob@example.com", "eve@example.com"],
        [95, 90, 88],
        ["Engineering", "Marketing", "Finance"]
    ], schema=schema_b)
    pq.write_table(table_b, path_b)

    print(f"Generated sample datasets:\n - Baseline: {path_a}\n - Target:   {path_b}")

if __name__ == "__main__":
    generate_datasets()