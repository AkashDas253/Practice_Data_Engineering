import json
from collections import defaultdict

from .core import write_json

def write_scan_reports(output_dir, variants, results, failures):
    reports = defaultdict(list)

    for result in results:
        reports[result["format"]].append(result)

    for failure in failures:
        reports["unclassified"].append(failure)

    for fmt, entries in reports.items():
        failed = sum(
            entry.get("validation_status", entry.get("status"))
            == "failed"
            for entry in entries
        )

        write_json(
            output_dir / fmt / "reports" / "validation_report.json",
            {
                "schema_version": "1.0",
                "format": fmt,
                "total_files": len(entries),
                "failed_files": failed,
                "files": entries,
            },
        )

    variant_entries = []

    for path in variants:
        payload = json.loads(path.read_text(encoding="utf-8"))
        variant_entries.append({
            "format": payload["format"],
            "structure_type": payload["structure_type"],
            "variant_id": payload["variant_id"],
            "schema_signature": payload["schema_signature"],
            "total_files": payload["total_files"],
            "path": str(path),
        })

    write_json(output_dir / "manifest.schema.json", {
        "schema_version": "1.0",
        "variant_count": len(variant_entries),
        "formats": sorted({
            item["format"] for item in variant_entries
        }),
        "variants": variant_entries,
        "failed_files": failures,
    })

def write_master_manifest(output_dir, paths):
    masters = []

    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        masters.append({
            "format": payload["format"],
            "structure_type": payload["structure_type"],
            "variant_id": payload["variant_id"],
            "total_source_files": payload["total_source_files"],
            "path": str(path),
        })

    write_json(output_dir / "master_manifest.schema.json", {
        "schema_version": "1.0",
        "master_schema_count": len(masters),
        "master_schemas": masters,
    })
