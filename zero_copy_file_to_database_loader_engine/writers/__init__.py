from core.registry import PluginRegistry
from writers.postgres import PostgresCopyWriter
from writers.duckdb import DuckDBWriter
from writers.clickhouse import ClickHouseArrowWriter

__all__ = [
    "PostgresCopyWriter",
    "DuckDBWriter",
    "ClickHouseArrowWriter",
    "register_writers",
]


def register_writers(registry: PluginRegistry) -> None:
    """Helper method to register all writer modules into the plugin registry."""
    registry.register(PostgresCopyWriter)
    registry.register(DuckDBWriter)
    registry.register(ClickHouseArrowWriter)