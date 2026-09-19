import csv
import json
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq

# Dynamically resolve 'examples/data' directory relative to this script file
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def generate_data(row_count: int = 50_000):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating sample datasets ({row_count:,} rows each) in '{DATA_DIR}'...\n")

    # 1. Parquet File
    parquet_path = DATA_DIR / "users.parquet"
    print(f"  -> Creating {parquet_path}...")
    parquet_table = pa.Table.from_pydict({
        "user_id": list(range(1, row_count + 1)),
        "username": [f"user_{i}" for i in range(1, row_count + 1)],
        "score": [float(i * 1.25) for i in range(1, row_count + 1)],
        "is_active": [i % 2 == 0 for i in range(1, row_count + 1)],
    })
    pq.write_table(parquet_table, parquet_path)

    # 2. CSV File
    csv_path = DATA_DIR / "transactions.csv"
    print(f"  -> Creating {csv_path}...")
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["txn_id", "user_id", "amount", "status"])
        for i in range(1, row_count + 1):
            writer.writerow([i, (i % 1000) + 1, round(i * 0.99, 2), "COMPLETED" if i % 3 != 0 else "PENDING"])

    # 3. NDJSON File
    ndjson_path = DATA_DIR / "events.json"
    print(f"  -> Creating {ndjson_path}...")
    with open(ndjson_path, mode="w", encoding="utf-8") as f:
        for i in range(1, row_count + 1):
            record = {
                "event_id": i,
                "event_type": "CLICK" if i % 2 == 0 else "VIEW",
                "page_url": f"/products/item_{i % 100}",
                "timestamp_ms": 1700000000000 + i,
            }
            f.write(json.dumps(record) + "\n")

    print("\nDataset generation complete!")


if __name__ == "__main__":
    generate_data()