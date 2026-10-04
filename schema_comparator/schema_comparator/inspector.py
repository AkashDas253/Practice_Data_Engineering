from dataclasses import dataclass, field
from typing import List, Tuple
import pyarrow as pa
from schema_comparator.readers import get_reader

@dataclass
class SchemaDriftResult:
    added_columns: List[Tuple[str, str]] = field(default_factory=list)
    dropped_columns: List[Tuple[str, str]] = field(default_factory=list)
    type_mismatches: List[Tuple[str, str, str]] = field(default_factory=list)
    unified_schema: pa.Schema = None

def inspect_schema_drift(source_a_path: str, source_b_path: str) -> SchemaDriftResult:
    reader_a = get_reader(source_a_path)
    reader_b = get_reader(source_b_path)

    schema_a = reader_a.get_schema()
    schema_b = reader_b.get_schema()

    fields_a = {field.name: field.type for field in schema_a}
    fields_b = {field.name: field.type for field in schema_b}

    result = SchemaDriftResult()

    # Identify added & dropped columns
    for name, dtype in fields_b.items():
        if name not in fields_a:
            result.added_columns.append((name, str(dtype)))
            
    for name, dtype in fields_a.items():
        if name not in fields_b:
            result.dropped_columns.append((name, str(dtype)))

    # Identify type mismatches
    common_cols = set(fields_a.keys()).intersection(set(fields_b.keys()))
    unified_fields = []

    for field_a in schema_a:
        name = field_a.name
        if name in common_cols:
            type_a = fields_a[name]
            type_b = fields_b[name]
            if type_a != type_b:
                result.type_mismatches.append((name, str(type_a), str(type_b)))
            unified_fields.append(field_a)
        else:
            unified_fields.append(field_a)

    for field_b in schema_b:
        if field_b.name not in fields_a:
            unified_fields.append(field_b)

    result.unified_schema = pa.schema(unified_fields)
    return result