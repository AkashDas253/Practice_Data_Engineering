from collections.abc import Iterator
from typing import Any

from models.record import Record
from stages.processing.base import Processing
from stages.processing.registry import ProcessingRegistry


class Filter(Processing):
    """
    Keeps records where a field equals a configured value.
    """

    def __init__(
        self,
        field: str,
        equals: Any,
    ):
        self.field = field
        self.equals = equals

    def process(
        self,
        records: Iterator[Record],
    ) -> Iterator[Record]:

        for record in records:
            if record.get(self.field) == self.equals:
                yield record


ProcessingRegistry.register(
    "filter",
    Filter,
)
