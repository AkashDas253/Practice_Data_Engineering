from abc import ABC, abstractmethod
from collections.abc import Iterator

from models.record import Record


class Parser(ABC):
    """
    Base contract for parser implementations.
    """

    @abstractmethod
    def parse(
        self,
        raw_data: Iterator[str],
    ) -> Iterator[Record]:
        """
        Convert raw input into structured records.
        """
        raise NotImplementedError