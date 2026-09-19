# Examples, SDK Demos & CLI Workflows

This directory contains standalone SDK usage scripts, equivalent CLI commands across OS environments, and a mock data generator for testing the **Zero-Copy Loader Engine**.

---

## Directory Layout

```text
examples/
├── data/                   # Target folder for generated mock datasets
├── generate_data.py        # Mock dataset generator script
├── duckdb_parquet.py       # SDK Example: Parquet -> DuckDB
├── postgres_csv.py         # SDK Example: CSV -> PostgreSQL
└── clickhouse_ndjson.py    # SDK Example: NDJSON -> ClickHouse

```

---

## 1. Generate Sample Datasets

Run `generate_data.py` from the project root directory to populate `examples/data/` with sample Parquet, CSV, and NDJSON files:

```bash
python examples/generate_data.py

```

---

## 2. Run SDK Demos

Execute any of the Python SDK example scripts from the **project root directory**:

### Stream Parquet to DuckDB

```bash
python examples/duckdb_parquet.py

```

### Stream CSV to PostgreSQL (`COPY FROM STDIN`)

```bash
python examples/postgres_csv.py

```

### Stream NDJSON to ClickHouse (Native Arrow)

```bash
python examples/clickhouse_ndjson.py

```

---

## 3. Run Equivalent CLI Workflows

You can perform the exact same ingestion tasks using `cli.py` from the **project root directory**.

#### Parquet -> DuckDB

```cmd
python cli.py ^
  --reader parquet ^
  --writer duckdb ^
  --source examples/data/users.parquet ^
  --target examples/data/analytics.duckdb ^
  --table users ^
  --batch-size 25000

```

```bash
python cli.py \
  --reader parquet \
  --writer duckdb \
  --source examples/data/users.parquet \
  --target examples/data/analytics.duckdb \
  --table users \
  --batch-size 25000

```

#### CSV -> PostgreSQL (`COPY FROM STDIN`)

```cmd
python cli.py ^
  --reader csv ^
  --writer postgres ^
  --source examples/data/transactions.csv ^
  --target "postgresql://postgres:password@localhost:5432/mydb" ^
  --table transactions ^
  --batch-size 50000

```

```bash
python cli.py \
  --reader csv \
  --writer postgres \
  --source examples/data/transactions.csv \
  --target "postgresql://postgres:password@localhost:5432/mydb" \
  --table transactions \
  --batch-size 50000

```


#### NDJSON -> ClickHouse (Native Arrow)

```cmd
python cli.py ^
  --reader ndjson ^
  --writer clickhouse ^
  --source examples/data/events.json ^
  --target "http://localhost:8123" ^
  --table app_events ^
  --batch-size 100000

```

```bash
python cli.py \
  --reader ndjson \
  --writer clickhouse \
  --source examples/data/events.json \
  --target "http://localhost:8123" \
  --table app_events \
  --batch-size 100000

```

---
