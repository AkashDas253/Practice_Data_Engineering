
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

from .core import Component, registry

def infer_type(value):
    if value is None:
        return "null"

    if isinstance(value, bool):
        return "boolean"

    if isinstance(value, int):
        return "int64"

    if isinstance(value, float):
        return "float64"

    text = str(value).strip()

    if not text:
        return "null"

    if text.lower() in {"true", "false"}:
        return "boolean"

    try:
        int(text)
        return "int64"
    except ValueError:
        pass

    try:
        float(text)
        return "float64"
    except ValueError:
        return "string"

def promote_types(types):
    types = set(types)

    if not types:
        return "null"

    if "null" in types and len(types) > 1:
        types.remove("null")

    if len(types) == 1:
        return next(iter(types))

    if types <= {"int64", "float64"}:
        return "float64"

    return "union[" + ",".join(sorted(types)) + "]"

def infer_fields(headers, rows):
    fields = []

    for index, header in enumerate(headers):
        values = [
            row[index] if index < len(row) else ""
            for row in rows
        ]

        types = [infer_type(value) for value in values]
        non_null_count = sum(value.strip() != "" for value in values)

        fields.append({
            "name": str(header).strip(),
            "type": promote_types(types),
            "observed_types": sorted(set(types)),
            "nullable": non_null_count < len(rows),
        })

    return fields

def detect_delimiter(text):
    candidates = [",", "\t", ";", "|"]

    lines = [
        line for line in text.splitlines()
        if line.strip()
    ][:20]

    if len(lines) < 2:
        return None

    scores = {}

    for delimiter in candidates:
        try:
            rows = list(csv.reader(lines, delimiter=delimiter))
            widths = [len(row) for row in rows]

            if widths and widths[0] > 1 and len(set(widths)) == 1:
                scores[delimiter] = widths[0]
        except csv.Error:
            continue

    if not scores:
        return None

    return max(scores, key=scores.get)

def detect_text_structure(text):
    lines = [
        line for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return {"structure_type": "plain_text"}

    # Detect records containing key-value pairs first.
    key_value_lines = 0

    for line in lines:
        parts = re.split(r"[;,]\s*", line.strip())

        if parts and all(
            re.match(r"^[\w.-]+\s*[:=]\s*.*$", part)
            for part in parts
        ):
            key_value_lines += 1

    if key_value_lines >= max(1, len(lines) // 2):
        return {"structure_type": "key_value"}

    # Detect delimiter-separated tabular records.
    delimiter = detect_delimiter(text)

    if delimiter:
        return {
            "structure_type": "delimited",
            "delimiter": delimiter,
        }

    return {"structure_type": "plain_text"}

def extract_json_fields(records):
    observed = defaultdict(set)
    counts = defaultdict(int)

    for record in records:
        if not isinstance(record, dict):
            continue

        for name, value in record.items():
            observed[name].add(infer_type(value))
            counts[name] += 1

    total = len(records)
    fields = []

    for name in sorted(observed):
        types = observed[name]

        fields.append({
            "name": name,
            "type": promote_types(types),
            "observed_types": sorted(types),
            "nullable": counts[name] < total or "null" in types,
        })

    return fields

class CSVScanner(Component):
    stage = "scanner"
    type = "csv"

    def execute(self, data, detection=None):
        path = Path(data)
        text = path.read_text(encoding="utf-8-sig")

        delimiter = (detection or {}).get(
            "text_structure", {}
        ).get("delimiter", ",")

        rows = list(csv.reader(text.splitlines(), delimiter=delimiter))

        if not rows:
            raise ValueError(f"Empty CSV file: {path}")

        headers = rows[0]
        data_rows = rows[1:]

        return {
            "format": "csv",
            "structure_type": "delimited",
            "file_name": path.name,
            "file_path": str(path),
            "fields": infer_fields(headers, data_rows),
            "num_rows": len(data_rows),
            "structure": {
                "delimiter": delimiter,
                "header_present": True,
                "duplicate_headers": len(headers) != len(set(headers)),
                "row_width_errors": sum(
                    len(row) != len(headers) for row in data_rows
                ),
            },
        }

class JSONScanner(Component):
    stage = "scanner"
    type = "json"

    def execute(self, data, detection=None):
        path = Path(data)
        parsed = json.loads(path.read_text(encoding="utf-8-sig"))

        if isinstance(parsed, list):
            records = parsed
            root_kind = "array"
        elif isinstance(parsed, dict):
            records = [parsed]
            root_kind = "object"
        else:
            records = []
            root_kind = "scalar"

        return {
            "format": "json",
            "structure_type": "json_document",
            "file_name": path.name,
            "file_path": str(path),
            "fields": extract_json_fields(records),
            "num_rows": len(records),
            "structure": {"root_kind": root_kind},
        }

class NDJSONScanner(Component):
    stage = "scanner"
    type = "ndjson"

    def execute(self, data, detection=None):
        path = Path(data)
        records = []
        invalid_lines = []

        for line_number, line in enumerate(
            path.read_text(encoding="utf-8-sig").splitlines(), 1
        ):
            if not line.strip():
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                invalid_lines.append({
                    "line": line_number,
                    "message": str(exc),
                })

        objects = [item for item in records if isinstance(item, dict)]

        return {
            "format": "ndjson",
            "structure_type": "json_lines",
            "file_name": path.name,
            "file_path": str(path),
            "fields": extract_json_fields(objects),
            "num_rows": len(records),
            "structure": {
                "invalid_lines": invalid_lines,
                "non_object_records": len(records) - len(objects),
            },
        }

class TXTScanner(Component):
    stage = "scanner"
    type = "txt"

    def execute(self, data, detection=None):
        path = Path(data)
        text = path.read_text(encoding="utf-8-sig")
        lines = [line for line in text.splitlines() if line.strip()]

        structure = (detection or {}).get(
            "text_structure",
            detect_text_structure(text),
        )

        kind = structure["structure_type"]
        fields = []

        if kind == "delimited":
            delimiter = structure["delimiter"]
            rows = list(csv.reader(lines, delimiter=delimiter))

            headers = rows[0]
            data_rows = rows[1:]

            fields = infer_fields(headers, data_rows)

            metadata = {
                "delimiter": delimiter,
                "header_present": True,
                "row_width_errors": sum(
                    len(row) != len(headers) for row in data_rows
                ),
            }

        elif kind == "key_value":
            records = []

            for line in lines:
                record = {}

                for part in re.split(r"[;,]\s*", line):
                    match = re.match(
                        r"\s*([\w.-]+)\s*[:=]\s*(.*?)\s*$",
                        part,
                    )

                    if match:
                        record[match.group(1)] = match.group(2)

                if record:
                    records.append(record)

            fields = extract_json_fields(records)
            metadata = {"record_count": len(records)}

        else:
            metadata = {
                "line_count": len(text.splitlines()),
                "blank_line_count": sum(
                    not line.strip() for line in text.splitlines()
                ),
            }

        return {
            "format": "txt",
            "structure_type": kind,
            "file_name": path.name,
            "file_path": str(path),
            "fields": fields,
            "num_rows": len(lines),
            "structure": metadata,
        }

class UniversalScanner(Component):
    stage = "scanner"
    type = "universal"

    def execute(self, data):
        path = Path(data)

        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        text = path.read_text(encoding="utf-8-sig")
        stripped = text.strip()
        extension = path.suffix.lower()

        if extension in {".ndjson", ".jsonl"}:
            fmt = "ndjson"

        elif extension == ".json":
            fmt = "json"

        elif extension == ".csv":
            fmt = "csv"

        elif extension == ".tsv":
            fmt = "csv"

        elif extension == ".txt":
            fmt = "txt"

        elif stripped.startswith("{") or stripped.startswith("["):
            try:
                json.loads(stripped)
                fmt = "json"
            except json.JSONDecodeError:
                fmt = "ndjson"

        else:
            structure = detect_text_structure(text)
            fmt = (
                "csv"
                if structure.get("delimiter") == ","
                else "txt"
            )

        if fmt == "csv" and extension == ".tsv":
            detection = {
                "text_structure": {
                    "structure_type": "delimited",
                    "delimiter": "\t",
                }
            }
        else:
            detection = {
                "text_structure": detect_text_structure(text)
            }

        scanner_cls = registry.get("scanner", fmt)
        result = scanner_cls().execute(str(path), detection=detection)

        result["format"] = fmt
        result["detected_extension"] = extension

        return result

for scanner in (
    CSVScanner,
    JSONScanner,
    NDJSONScanner,
    TXTScanner,
    UniversalScanner,
):
    registry.register(scanner)