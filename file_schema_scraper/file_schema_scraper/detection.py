import csv
import json
import re
from io import StringIO
from pathlib import Path

from .core import Component, registry

DELIMITERS = [",", "\t", "|", ";"]

def detect_text_structure(text: str) -> dict:
    lines = [
        line for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return {
            "structure_type": "plain_text",
            "confidence": 0.0,
            "evidence": ["No non-empty lines found"],
        }

    sample = lines[:50]

    best = None
    for delimiter in DELIMITERS:
        try:
            rows = list(csv.reader(
                sample,
                delimiter=delimiter,
                strict=True,
            ))
        except csv.Error:
            continue

        widths = [len(row) for row in rows]
        if not widths or widths[0] < 2:
            continue

        consistent = sum(
            width == widths[0] for width in widths
        ) / len(widths)

        score = consistent * min(widths[0] / 4, 1.0)

        if consistent >= 0.8 and (
            best is None or score > best["score"]
        ):
            best = {
                "structure_type": "delimited",
                "delimiter": delimiter,
                "score": score,
                "confidence": round(consistent, 3),
                "evidence": [
                    f"{widths[0]} fields per first sampled row",
                    f"{consistent:.0%} consistent row widths",
                ],
            }

    if best is not None:
        best.pop("score")
        return best

    key_value_lines = 0
    for line in sample:
        if re.search(r"[\w.-]+\s*[:=]\s*\S+", line):
            key_value_lines += 1

    if key_value_lines / len(sample) >= 0.7:
        return {
            "structure_type": "key_value",
            "confidence": round(key_value_lines / len(sample), 3),
            "evidence": ["Repeated key-value patterns"],
        }

    if len(sample) >= 2:
        candidates = []

        for line in sample:
            boundaries = [
                match.start()
                for match in re.finditer(r"\S+", line)
            ]
            candidates.append(boundaries)

        shared = set(candidates[0])
        for boundaries in candidates[1:]:
            shared &= set(boundaries)

        if len(shared) >= 2:
            return {
                "structure_type": "fixed_width",
                "confidence": 0.5,
                "evidence": [
                    "Repeated character positions across lines"
                ],
            }

    return {
        "structure_type": "plain_text",
        "confidence": 0.4,
        "evidence": ["No reliable structured layout detected"],
    }

class FormatDetector(Component):
    stage = "detector"
    type = "universal"

    def execute(self, data: str) -> dict:
        path = Path(data)
        raw = path.read_bytes()

        if raw.startswith(b"PAR1"):
            return {
                "format": "parquet",
                "confidence": 1.0,
                "evidence": ["Parquet magic bytes"],
            }

        if raw.startswith(b"PK\x03\x04") and path.suffix.lower() in {
            ".xlsx", ".xlsm"
        }:
            return {
                "format": "excel",
                "confidence": 1.0,
                "evidence": ["Excel ZIP container and extension"],
            }

        text = raw.decode("utf-8-sig", errors="strict")
        stripped = text.strip()
        ext = path.suffix.lower()

        if ext in {".ndjson", ".jsonl"}:
            return {
                "format": "ndjson",
                "confidence": 1.0,
                "evidence": ["Line-delimited JSON extension"],
            }

        try:
            json.loads(stripped)
            return {
                "format": "json",
                "confidence": 1.0,
                "evidence": ["Valid JSON document"],
            }
        except json.JSONDecodeError:
            pass

        lines = [line for line in stripped.splitlines() if line.strip()]
        if len(lines) > 1:
            parsed_count = 0

            for line in lines[:20]:
                try:
                    json.loads(line)
                    parsed_count += 1
                except json.JSONDecodeError:
                    break

            if parsed_count == min(len(lines), 20):
                return {
                    "format": "ndjson",
                    "confidence": 0.95,
                    "evidence": [
                        "Multiple independently valid JSON records"
                    ],
                }

        structure = detect_text_structure(text)

        if ext == ".csv":
            fmt = "csv"
        elif ext in {".txt", ".dat", ".tsv", ".psv"}:
            fmt = "txt"
        elif ext in {".xml"} or stripped.startswith("<?xml"):
            fmt = "xml"
        elif ext in {".avro"}:
            fmt = "avro"
        elif ext in {".parquet"}:
            fmt = "parquet"
        elif ext in {".xlsx", ".xlsm", ".xls"}:
            fmt = "excel"
        elif structure["structure_type"] == "delimited":
            fmt = "txt"
        else:
            fmt = "txt"

        return {
            "format": fmt,
            "confidence": structure["confidence"],
            "evidence": structure["evidence"],
            "text_structure": structure,
        }

registry.register(FormatDetector)
