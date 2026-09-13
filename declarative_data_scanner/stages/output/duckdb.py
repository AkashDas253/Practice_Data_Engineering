from collections.abc import Iterator

from models.record import Record
from stages.output.base import Output
from stages.output.registry import OutputRegistry


class DuckDBOutput(Output):
    """
    Placeholder DuckDB output.

    Full database persistence will be implemented
    in the pipeline phase.
    """

    def __init__(
        self,
        path: str,
        table: str,
    ):
        self.path = path
        self.table = table

    def write(
        self,
        records: Iterator[Record],
    ) -> int:

        count = 0

        for _record in records:
            count += 1

        return count


OutputRegistry.register(
    "duckdb",
    DuckDBOutput,
)
