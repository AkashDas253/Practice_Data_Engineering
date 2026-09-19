from core.registry import PluginRegistry
from readers.parquet import ParquetReader
from readers.csv import CSVReader
from readers.ndjson import NDJSONReader

__all__ = ["ParquetReader", "CSVReader", "NDJSONReader", "register_readers"]


def register_readers(registry: PluginRegistry) -> None:
    """Helper method to register all reader modules into the plugin registry."""
    registry.register(ParquetReader)
    registry.register(CSVReader)
    registry.register(NDJSONReader)