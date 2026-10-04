from schema_comparator.inspector import inspect_schema_drift
from schema_comparator.cdc_engine import compute_cdc
from schema_comparator.reporter import export_results

# 1. Inspect schema drift between two datasets
drift = inspect_schema_drift("data/source_a.parquet", "data/source_b.parquet")
print("Added Columns:", drift.added_columns)

# 2. Run CDC engine
cdc = compute_cdc("data/source_a.parquet", "data/source_b.parquet", primary_keys=["id"])
print(f"Inserts: {cdc.count_inserts}, Updates: {cdc.count_updates}, Deletes: {cdc.count_deletes}")

# 3. Export outputs
export_results(drift, cdc, "output/delta.parquet", "output/report.md")