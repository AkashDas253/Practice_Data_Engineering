from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

class Component:
    stage = "component"
    type = "default"

    def __init__(self, config: dict | None = None):
        self.config = config or {}

    def execute(self, data: Any) -> Any:
        raise NotImplementedError

class ComponentRegistry:
    def __init__(self):
        self._items = {}

    def register(self, cls):
        self._items[(cls.stage, cls.type)] = cls
        return cls

    def get(self, stage: str, type_name: str):
        try:
            return self._items[(stage, type_name)]
        except KeyError as exc:
            raise ValueError(
                f"Component not registered: {stage}:{type_name}"
            ) from exc

    def available(self):
        return [
            f"{stage}:{name}"
            for stage, name in sorted(self._items)
        ]

registry = ComponentRegistry()

def stable_hash(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

def schema_fingerprint(schema: dict) -> str:
    fields = [
        {"name": f["name"], "type": f["type"]}
        for f in schema.get("fields", [])
    ]
    fields.sort(key=lambda item: item["name"])

    identity = {
        "format": schema["format"],
        "structure_type": schema.get("structure_type", "unknown"),
        "structure": schema.get("structure", {}),
        "fields": fields,
    }
    return stable_hash(identity)[:16]

def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temporary.replace(path)

class SchemaScraperEngine:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir).resolve()
        self.output_dir = Path(output_dir).resolve()

        if not self.input_dir.is_dir():
            raise NotADirectoryError(str(self.input_dir))

        self.output_dir.mkdir(parents=True, exist_ok=True)

        from . import scanners, validators, aggregators  # noqa: F401

    def _files(self):
        for path in sorted(self.input_dir.rglob("*")):
            if not path.is_file() or path.name.startswith("."):
                continue

            resolved = path.resolve()

            if (
                resolved == self.output_dir
                or self.output_dir in resolved.parents
            ):
                continue

            yield path

    def run_scan(self) -> list[Path]:
        from .detection import FormatDetector
        from .reporting import write_scan_reports

        detector = FormatDetector()
        groups = defaultdict(list)
        file_results = []
        failures = []

        for path in self._files():
            try:
                detection = detector.execute(str(path))
                fmt = detection["format"]

                scanner = registry.get("scanner", fmt)()
                schema = scanner.execute(str(path), detection=detection)

                checks = {}
                for validator_type in (
                    "schema_structure",
                    f"{fmt}_validation",
                ):
                    validator = registry.get(
                        "validator", validator_type
                    )()
                    checks[validator_type] = validator.execute(schema)

                schema["validation"] = checks

                failed = any(
                    check["status"] == "failed"
                    for check in checks.values()
                )
                warned = any(
                    check["status"] == "warning"
                    for check in checks.values()
                )

                schema["validation_status"] = (
                    "failed" if failed
                    else "warning" if warned
                    else "passed"
                )

                schema["schema_signature"] = schema_fingerprint(schema)

                groups[
                    (fmt, schema["schema_signature"])
                ].append(schema)

                file_results.append({
                    "file_name": path.name,
                    "file_path": str(path),
                    "format": fmt,
                    "structure_type": schema["structure_type"],
                    "schema_signature": schema["schema_signature"],
                    "validation_status": schema["validation_status"],
                    "validation": checks,
                })

                print(
                    f"[SCANNED] {path.name}: "
                    f"{fmt}/{schema['structure_type']}"
                )

            except Exception as exc:
                failures.append({
                    "file_name": path.name,
                    "file_path": str(path),
                    "status": "failed",
                    "error": str(exc),
                })
                print(f"[ERROR] {path}: {exc}")

        outputs = []
        counters = defaultdict(int)

        for (fmt, signature), schemas in sorted(groups.items()):
            structure = schemas[0]["structure_type"]
            counters[(fmt, structure)] += 1
            number = counters[(fmt, structure)]

            variant_id = (
                f"{fmt}_{structure}_variant_{number:03d}"
            )

            payload = {
                "schema_version": "1.0",
                "format": fmt,
                "structure_type": structure,
                "variant_id": variant_id,
                "schema_signature": signature,
                "total_files": len(schemas),
                "file_schemas": schemas,
            }

            output = (
                self.output_dir / fmt / "variants"
                / f"{variant_id}.schema.json"
            )
            write_json(output, payload)
            outputs.append(output)

        write_scan_reports(
            self.output_dir, outputs, file_results, failures
        )

        print(
            f"[COMPLETE] {len(outputs)} variants; "
            f"{len(file_results)} scanned; {len(failures)} failed."
        )
        return outputs

    def run_aggregation(self) -> list[Path]:
        from .reporting import write_master_manifest

        outputs = []
        variants_dir = self.output_dir

        for path in sorted(
            variants_dir.glob("*/variants/*.schema.json")
        ):
            payload = json.loads(path.read_text(encoding="utf-8"))
            fmt = payload["format"]

            aggregator = registry.get("aggregator", fmt)()
            master = aggregator.execute(payload)

            output = (
                self.output_dir / fmt / "master"
                / f"master_{payload['variant_id']}.schema.json"
            )
            write_json(output, master)
            outputs.append(output)

            print(f"[MASTER] {output}")

        write_master_manifest(self.output_dir, outputs)
        return outputs