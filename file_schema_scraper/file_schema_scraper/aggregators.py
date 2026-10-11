from .core import Component, registry
from .scanners import promote_types

class BaseAggregator(Component):
    stage = "aggregator"

    def execute(self, payload):
        files = payload.get("file_schemas", [])
        total_files = len(files)
        observed = {}
        coverage = {}
        total_rows = sum(
            file.get("num_rows", 0) for file in files
        )

        for file_schema in files:
            for field in file_schema.get("fields", []):
                name = field["name"]
                observed.setdefault(name, set()).update(
                    field.get("observed_types", [field["type"]])
                )
                coverage[name] = coverage.get(name, 0) + 1

        fields = []

        for name in sorted(observed):
            types = observed[name]
            count = coverage[name]

            fields.append({
                "name": name,
                "type": promote_types(types),
                "observed_types": sorted(types),
                "nullable": count < total_files or "null" in types,
                "file_coverage_count": count,
                "file_coverage_ratio": (
                    round(count / total_files, 4)
                    if total_files else 0
                ),
            })

        return {
            "schema_version": "1.0",
            "format": self.type,
            "structure_type": payload["structure_type"],
            "variant_id": payload["variant_id"],
            "schema_signature": payload["schema_signature"],
            "total_source_files": total_files,
            "total_rows": total_rows,
            "fields": fields,
            "files": [
                {
                    "file_name": item["file_name"],
                    "file_path": item["file_path"],
                    "validation_status": item.get(
                        "validation_status", "unknown"
                    ),
                }
                for item in files
            ],
        }

class CSVAggregator(BaseAggregator):
    type = "csv"

class JSONAggregator(BaseAggregator):
    type = "json"

class NDJSONAggregator(BaseAggregator):
    type = "ndjson"

class TXTAggregator(BaseAggregator):
    type = "txt"

    def execute(self, payload):
        master = super().execute(payload)
        master["structure_metadata"] = [
            {
                "file_name": item["file_name"],
                "structure": item.get("structure", {}),
            }
            for item in payload.get("file_schemas", [])
        ]
        return master

for aggregator in (
    CSVAggregator,
    JSONAggregator,
    NDJSONAggregator,
    TXTAggregator,
):
    registry.register(aggregator)
