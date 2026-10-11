from pathlib import Path

from .core import Component, registry

def make_result(issues):
    status = (
        "failed" if any(i["severity"] == "error" for i in issues)
        else "warning" if any(i["severity"] == "warning" for i in issues)
        else "passed"
    )
    return {"status": status, "issues": issues}

def add(issues, rule, severity, message):
    issues.append({
        "rule": rule,
        "severity": severity,
        "message": message,
    })

class SchemaStructureValidator(Component):
    stage = "validator"
    type = "schema_structure"

    def execute(self, data):
        issues = []
        names = [f.get("name") for f in data.get("fields", [])]

        if len(names) != len(set(names)):
            add(
                issues, "SCHEMA_DUPLICATE_FIELDS", "error",
                "Field names are not unique.",
            )

        for field in data.get("fields", []):
            if not field.get("name") or not field.get("type"):
                add(
                    issues, "SCHEMA_INVALID_FIELD", "error",
                    "Every field requires a name and type.",
                )

        if data.get("structure_type") == "plain_text" and names:
            add(
                issues, "SCHEMA_TEXT_FIELDS", "warning",
                "Plain text unexpectedly contains structured fields.",
            )

        return make_result(issues)

class CSVValidator(Component):
    stage = "validator"
    type = "csv_validation"

    def execute(self, data):
        issues = []
        structure = data.get("structure", {})

        if structure.get("duplicate_headers"):
            add(
                issues, "CSV_DUPLICATE_HEADERS", "error",
                "CSV headers contain duplicate names.",
            )

        if structure.get("row_width_errors", 0):
            add(
                issues, "CSV_ROW_WIDTH", "warning",
                f"{structure['row_width_errors']} rows have inconsistent widths.",
            )

        if data.get("num_rows", 0) == 0:
            add(
                issues, "CSV_NO_RECORDS", "warning",
                "No data records were found.",
            )

        return make_result(issues)

class JSONValidator(Component):
    stage = "validator"
    type = "json_validation"

    def execute(self, data):
        issues = []
        if data.get("num_rows", 0) == 0:
            add(
                issues, "JSON_NO_OBJECT_RECORDS", "info",
                "No object records were found.",
            )

        if data.get("structure", {}).get("root_kind") == "scalar":
            add(
                issues, "JSON_SCALAR_ROOT", "info",
                "The document contains a scalar JSON value.",
            )

        return make_result(issues)

class NDJSONValidator(Component):
    stage = "validator"
    type = "ndjson_validation"

    def execute(self, data):
        issues = []
        structure = data.get("structure", {})

        if structure.get("invalid_lines"):
            add(
                issues, "NDJSON_INVALID_LINES", "error",
                f"{len(structure['invalid_lines'])} lines contain invalid JSON.",
            )

        if structure.get("non_object_records", 0):
            add(
                issues, "NDJSON_NON_OBJECT_RECORDS", "warning",
                "Some records are not JSON objects.",
            )

        return make_result(issues)

class TXTValidator(Component):
    stage = "validator"
    type = "txt_validation"

    def execute(self, data):
        issues = []
        path = Path(data["file_path"])

        if path.stat().st_size == 0:
            add(
                issues, "TXT_EMPTY_FILE", "warning",
                "The text file is empty.",
            )

        if data.get("structure_type") == "plain_text":
            add(
                issues, "TXT_SCHEMA_UNRESOLVED", "info",
                "No reliable record structure was detected.",
            )

        if data.get("structure", {}).get("row_width_errors", 0):
            add(
                issues, "TXT_ROW_WIDTH", "warning",
                "Some delimited records have inconsistent widths.",
            )

        return make_result(issues)

for validator in (
    SchemaStructureValidator,
    CSVValidator,
    JSONValidator,
    NDJSONValidator,
    TXTValidator,
):
    registry.register(validator)
