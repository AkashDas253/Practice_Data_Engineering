from typing import Optional
import pyarrow as pa
import pyarrow.compute as pc


class SchemaAligner:
    """Inspects Arrow batch schemas and aligns/casts types to match target schema signatures."""

    def __init__(self, target_schema: Optional[pa.Schema] = None):
        self.target_schema = target_schema

    def align_batch(self, batch: pa.RecordBatch) -> pa.RecordBatch:
        """Casts columns in C++ memory space if source types mismatch the target table schema."""
        if not self.target_schema:
            return batch

        aligned_arrays = []
        aligned_fields = []

        for target_field in self.target_schema:
            field_name = target_field.name
            target_type = target_field.type

            if field_name not in batch.schema.names:
                raise ValueError(f"Schema mismatch: Required target column '{field_name}' missing from source batch.")

            source_array = batch.column(field_name)

            # Perform zero-copy / optimized C++ level array casting if types differ
            if source_array.type != target_type:
                source_array = pc.cast(source_array, target_type)

            aligned_arrays.append(source_array)
            aligned_fields.append(target_field)

        return pa.RecordBatch.from_arrays(aligned_arrays, schema=pa.schema(aligned_fields))