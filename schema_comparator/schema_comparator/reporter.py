from pathlib import Path
import pyarrow.parquet as pq
from schema_comparator.inspector import SchemaDriftResult
from schema_comparator.cdc_engine import CDCResult

def export_results(
    drift: SchemaDriftResult, 
    cdc: CDCResult, 
    delta_output_path: str, 
    report_md_path: str
):
    # 1. Write Delta Parquet
    delta_path = Path(delta_output_path)
    delta_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(cdc.delta_table, delta_path)

    # 2. Write Markdown Report
    report_path = Path(report_md_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    md_content = f"""# SchemaComparator Audit Report

## 1. Schema Drift Evaluation
* **Added Columns**: {len(drift.added_columns)}
* **Dropped Columns**: {len(drift.dropped_columns)}
* **Type Mismatches**: {len(drift.type_mismatches)}

### Added Columns Detail
{_format_list(drift.added_columns)}

### Dropped Columns Detail
{_format_list(drift.dropped_columns)}

### Type Mismatches Detail
{_format_list(drift.type_mismatches)}

---

## 2. Row-Level CDC Summary
* **INSERTS**: {cdc.count_inserts}
* **UPDATES**: {cdc.count_updates}
* **DELETES**: {cdc.count_deletes}
* **UNCHANGED**: {cdc.count_unchanged}
"""
    report_path.write_text(md_content, encoding="utf-8")

def _format_list(items) -> str:
    if not items:
        return "_None_"
    return "\n".join([f"* `{item}`" for item in items])