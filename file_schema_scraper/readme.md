# File Schema Scraper

A lightweight, modular, plugin-based Python engine for discovering, inspecting, validating, and aggregating schemas across heterogeneous datasets.

File Schema Scraper is designed for situations where data arrives in multiple file formats, file structures change over time, and no single schema describes the entire dataset. It detects supported formats, extracts structural information, groups files into schema variants, validates discovered schemas, and generates independent schema contracts and reports.

## Key Features

- **Content-Aware Format Detection:** Identifies supported data formats using file extensions and content inspection.
- **Format-Specific Scanning:** Supports CSV, JSON, NDJSON, and TXT, with separate handling for structured documents, delimited text, key-value records, and plain text.
- **Schema Fingerprinting:** Generates stable fingerprints from structural information to identify distinct schema variants.
- **Multi-Variant Discovery:** Groups files with compatible structures while preserving differences such as additional fields, changed types, and different delimiters.
- **Subset-Aware Aggregation:** Tracks field coverage, field presence, and nullability across source files.
- **Type Inference and Promotion:** Infers common data types and promotes compatible types, such as integers and floating-point values.
- **Format-Specific Validation:** Supports independent validation rules for different formats and structures.
- **Independent Schema Contracts:** Generates separate schema outputs for individual formats and detected structural variants.
- **Plugin-Based Architecture:** Uses a central component registry to connect scanners, validators, and aggregators.
- **Automated Testing:** Includes unit and integration tests for scanning, validation, aggregation, and end-to-end workflows.

## Supported Formats

The project distinguishes between a file format and the structure of the data stored inside it. This is particularly important for TXT files, which may contain structured records or unstructured text.

| File format | Supported structures | Schema discovery |
| --- | --- | --- |
| CSV | Comma-separated tabular records | Headers, columns, inferred types, row-width checks |
| JSON | JSON objects and arrays | Keys, nested structures, observed types, optional fields |
| NDJSON / JSONL | One JSON value per line | Record fields, type variations, invalid-line detection |
| TXT | Delimiter-separated records, key-value records, plain text | Structure-dependent field extraction and validation |
| TSV | Tab-separated records | Tabular field extraction through the CSV scanner |

### TXT Structure Detection

TXT files do not necessarily have a conventional schema. Their structure must be identified before schema extraction can be performed.

Examples include:

**Delimiter-separated records**

```
id|name|amount
1|alpha|10.5
2|beta|20.0
```

**Key-value records**

```
id=1;name=alpha;active=true
id=2;name=beta;active=false
```

**Plain text**

```
Application started.
Loading configuration.
Application ready.
```

Delimited records can expose fields and inferred types. Key-value records can expose recurring keys. Plain text may have no meaningful field-level schema, so the appropriate output is structural metadata rather than an invented tabular schema.

Detection is heuristic. Ambiguous or irregular files should be validated, and unsupported structures should be reported explicitly.

## Architecture

The engine follows a modular pipeline.

1. **Scan:** Discover input files, detect their formats and structures, extract fields, infer types, and calculate schema fingerprints.
2. **Validate:** Check discovered schemas and format-specific structural rules, reporting errors and warnings.
3. **Aggregate:** Combine compatible file schemas, calculate field coverage, track optional fields, and promote compatible types.
4. **Report:** Write machine-readable schema contracts and supporting metadata for downstream inspection.

The implementation uses a registry-based component model so format-specific handlers can be added without placing all parsing and validation logic inside one universal scanner.

### Schema Variants

Files should not automatically be merged merely because they share an extension.

For example, these CSV files have different structures:

```
# users_v1.csv
user_id,username,score
1,alice,95.5
```

```
# users_v2.csv
user_id,username,score,country
2,bob,82.0,USA
```

The engine can fingerprint their structures and maintain separate variants. Each variant can have its own intermediate schema and master contract.

Field coverage can then distinguish between fields present in every source file and fields found in only a subset.

For example:

```
{
  "name": "country",
  "type": "string",
  "nullable": true,
  "file_coverage_count": 1,
  "file_coverage_ratio": 0.5
}
```

The example represents a field present in one of two source files. Actual output properties depend on the generated contract.

## Project Structure

```
file_schema_scraper/
├── file_schema_scraper/
│   ├── __init__.py
│   ├── core.py
│   ├── detection.py
│   ├── scanners.py
│   ├── validators.py
│   ├── aggregators.py
│   ├── reporting.py
│   └── cli.py
├── examples/
│   └── generate_files.py
├── tests/
│   ├── conftest.py
│   ├── test_scanners.py
│   ├── test_validators.py
│   ├── test_aggregators.py
│   ├── test_scraper.py
│   └── test_integration.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Main Components

| Stage | Component | Responsibility |
| --- | --- | --- |
| Detection | Format and structure detection | Identifies likely formats and text structures |
| Scanner | `UniversalScanner` | Routes files to the appropriate scanner |
| Scanner | `CSVScanner` | Extracts tabular fields and infers column types |
| Scanner | `JSONScanner` | Extracts fields from JSON documents |
| Scanner | `NDJSONScanner` | Processes line-delimited JSON records |
| Scanner | `TXTScanner` | Handles delimited, key-value, and plain-text structures |
| Validator | Schema and format-specific validators | Checks schema integrity and format-specific rules |
| Aggregator | Format-specific aggregators | Combines compatible schemas and tracks field coverage |
| Reporting | Reporting utilities | Produces machine-readable schema and validation reports |
| Core | `ComponentRegistry` | Registers and resolves pipeline components |
| Core | `SchemaScraperEngine` | Coordinates scanning, validation, and aggregation |
| CLI | Click command interface | Exposes pipeline operations through the command line |

Component availability and exact class names should match the installed implementation.

## Installation

Python 3.12 or a compatible supported Python version is recommended.

Create and activate a virtual environment on Windows PowerShell:

```
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the project and development dependencies:

```
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Quickstart

Run the following commands from the project root.

### 1. Generate sample files

Generate files covering multiple formats and structural scenarios:

```
python examples/generate_files.py
```

The generator creates examples such as CSV variants, JSON documents, NDJSON records, delimiter-separated TXT files, key-value TXT files, and plain-text logs.

### 2. Scan input files

Discover formats, extract schemas, and group compatible files into intermediate variants:

```
python -m file_schema_scraper.cli scan --input-dir examples/data --output-dir schemas/intermediate
```

### 3. Aggregate schemas

Use the aggregation command supported by the installed CLI implementation.

For a CLI that accepts `--schemas-dir` and `--output`:

```
python -m file_schema_scraper.cli aggregate --schemas-dir schemas/intermediate --output schemas/master.schema.json
```

The engine should generate master contracts independently for the discovered variants. The actual output paths depend on the implementation.

### 4. Inspect generated schemas

Open the generated JSON files and review:

- Detected format and structure type
- Schema fingerprint and variant identifier
- Field names and inferred data types
- Nullability and field coverage
- Source-file and row counts
- Validation warnings and errors, where reported

## Validation

Validation should be format-aware rather than relying on a single set of rules for every file.

Examples of useful checks include:

| Format or structure | Validation checks |
| --- | --- |
| CSV | Missing headers, duplicate headers, inconsistent row widths |
| JSON | Malformed JSON, unsupported root structures, inconsistent record shapes |
| NDJSON | Invalid lines, non-object records, inconsistent fields |
| Delimited TXT | Delimiter consistency, header quality, irregular row widths |
| Key-value TXT | Missing keys, malformed pairs, inconsistent record structure |
| Plain TXT | Encoding and readability checks, line statistics, unresolved schema status |
| Shared schema | Duplicate fields, invalid field definitions, missing required metadata |

A validation result should distinguish errors from warnings. Plain text without a field-level schema is not automatically invalid; it may simply be unsuitable for tabular schema inference.

## Testing

Run the complete test suite:

```
pytest -v
```

Run tests with coverage:

```
pytest --cov=file_schema_scraper --cov-report=term-missing -v
```

Run individual test modules:

```
pytest -v tests/test_scanners.py
pytest -v tests/test_validators.py
pytest -v tests/test_aggregators.py
pytest -v tests/test_scraper.py tests/test_integration.py
```

The test suite covers format detection, field extraction, type inference, schema variants, subset-aware aggregation, validation rules, and integration behavior.

CLI tests can be added separately to verify command invocation, invalid arguments, and error handling.

## Design Principles

- **Format-aware:** Different formats receive appropriate parsing and validation.
- **Structure-aware:** Files with the same extension can contain different data structures.
- **Variant-preserving:** Structural differences are retained rather than silently discarded.
- **Auditable:** Intermediate schemas and validation results can be inspected independently.
- **Extensible:** New scanners, validators, and aggregators can be registered as components.
- **Conservative:** When a reliable field-level schema cannot be inferred, the engine should report that limitation rather than fabricate a schema.

## Current Scope and Limitations

- Format detection is heuristic and may be ambiguous for files with misleading extensions or irregular content.
- Type inference depends on the values observed during scanning; a sample may not represent every possible value.
- Nested JSON objects and arrays may require recursive schema inference for comprehensive nested contracts.
- Fixed-width text, binary formats, XML, Parquet, Excel, and other specialized formats require dedicated detection and parsing support.
- Schema fingerprints depend on which structural properties are included. Changes to delimiter, header interpretation, field types, or nested structure may affect variant grouping.
- Successful unit tests demonstrate the tested behavior, not universal correctness across all possible datasets.

## Future Enhancements

Potential improvements include:

- Recursive nested-schema inference
- Configurable required fields and validation policies
- Additional format plugins for XML, Parquet, and Excel
- Configurable encoding detection
- Confidence scores for format and structure detection
- Schema evolution comparisons between runs
- Machine-readable validation summaries
- CLI integration tests and broader edge-case coverage

