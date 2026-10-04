# SchemaComparator

`schema_comparator` is a local, schema-agnostic Data Engineering utility that evaluates structural schema drift and computes row-level Change Data Capture (CDC) mutation vectors (`INSERT`, `UPDATE`, `DELETE`, `UNCHANGED`) between any two tabular datasets without pre-defined schema constraints.

---

## Key Features

- **100% Schema-Agnostic:** Dynamically inspects and compares resolved schemas of supported tabular datasets.
- **Schema Drift Detection:** Automatically flags added columns, dropped columns, and data type mismatches.
- **Vectorized CDC Engine:** Leverages PyArrow and DuckDB for low-memory, vectorized set-based comparisons and row-level CDC classification.
- **Actionable Outputs:** Exports tagged `.parquet` delta logs (`_change_type`) and human-readable Markdown audit summaries.
- **Extensible Reader Architecture:** Datasource-specific logic is isolated behind the `BaseReader` interface, allowing new datasources to be added through new reader implementations without changing the core comparison engine.

---

## Supported Readers

The reader layer decouples datasource ingestion from the core comparison engine. All readers implement `BaseReader` and provide a resolved PyArrow schema and a DuckDB relation.

| Reader Class | Module Path | Supported Data Sources | Base Contract | Key Responsibility |
| --- | --- | --- | --- | --- |
| `BaseReader` | `schema_comparator/readers/base.py` | N/A (Abstract Interface) | N/A | Defines `get_schema()` and `get_relation()` |
| `ArrowFileReader` | `schema_comparator/readers/arrow.py` | Parquet, CSV, NDJSON | `BaseReader` | Reads supported tabular files and exposes their schema and relation |
| `DuckDBTableReader` | `schema_comparator/readers/duckdb.py` | DuckDB Tables, Views, Queries | `BaseReader` | Exposes relational sources through the common reader interface |
| `Custom Reader` | `schema_comparator/readers/...` | Additional datasources | `BaseReader` | Adds support for new datasources without changing the core engine |

---

## Project Structure

```
schema_comparator/               # Root repository directory
├── schema_comparator/           # Core Python package engine
│   ├── __init__.py              # Package initialization & version info
│   ├── cli.py                   # Terminal CLI entrypoint & argument parser
│   ├── inspector.py             # Schema drift evaluation & field alignment
│   ├── cdc_engine.py            # CDC comparison & mutation classifier
│   ├── reporter.py              # Parquet delta exporter & Markdown report generator
│   └── readers/                 # Reader implementations
│       ├── __init__.py          # Reader resolver
│       ├── base.py              # Abstract BaseReader interface
│       └── ...                  # Additional readers
├── tests/                       # Test suite
│   ├── conftest.py              # Pytest fixtures & synthetic dataset generators
│   ├── test_inspector.py        # Schema drift tests
│   ├── test_cdc.py              # CDC tests
│   └── test_integration.py      # End-to-end CLI tests
├── examples/                    # Sample scripts & workflows
│   ├── generate_sample_data.py  # Synthetic dataset generator
│   └── quickstart.py            # Programmatic Python API example
├── pyproject.toml               # Packaging metadata & dependencies
├── requirements.txt             # Development & runtime dependencies
└── README.md                    # Project documentation
```

---

## Installation

```
# Clone this repo and navigate to this folder

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install package in editable mode
pip install -e .
```

---

## Quickstart

### 1. Generate Sample Data

Generate synthetic baseline (`source_a`) and target (`source_b`) Parquet files exhibiting schema drift and CDC mutations:

```
python examples/generate_sample_data.py
```

### 2. Run CLI Tool

You can run the engine using the package entrypoint:

```
schema_comparator \
  --source-a examples/data/baseline.parquet \
  --source-b examples/data/target.parquet \
  --keys user_id \
  --output-delta output/deltas.parquet \
  --report-md output/drift_report.md
```

Alternative Python module invocation:

```
python -m schema_comparator.cli \
  --source-a examples/data/baseline.parquet \
  --source-b examples/data/target.parquet \
  --keys user_id \
  --output-delta output/deltas.parquet \
  --report-md output/drift_report.md
```

### 3. Generated Audit Report

The tool generates a Parquet delta log and a Markdown audit report.

Example:

```
# SchemaComparator Audit Report

## 1. Schema Drift Evaluation
* **Added Columns**: 1
* **Dropped Columns**: 1
* **Type Mismatches**: 0

### Added Columns Detail
* `('department', 'string')`

### Dropped Columns Detail
* `('legacy_code', 'string')`

### Type Mismatches Detail
_None_

---

## 2. Row-Level CDC Summary
* **INSERTS**: 1
* **UPDATES**: 1
* **DELETES**: 2
* **UNCHANGED**: 1
```

---

## Python API Usage

```
from schema_comparator.inspector import inspect_schema_drift
from schema_comparator.cdc_engine import compute_cdc
from schema_comparator.reporter import export_results

# 1. Evaluate structural schema drift
drift = inspect_schema_drift(
    "examples/data/baseline.parquet",
    "examples/data/target.parquet"
)

# 2. Compute CDC row mutation vectors
cdc = compute_cdc(
    "examples/data/baseline.parquet",
    "examples/data/target.parquet",
    primary_keys=["user_id"]
)

# 3. Export Parquet deltas and Markdown audit summary
export_results(
    drift,
    cdc,
    "output/deltas.parquet",
    "output/drift_report.md"
)
```

---

## Testing

Run the automated test suite:

```
python -m pytest tests/ -v
```

Run with coverage:

```
python -m pytest --cov=schema_comparator tests/
```