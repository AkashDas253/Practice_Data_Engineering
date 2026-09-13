from abc import ABC, abstractmethod
from collections.abc import Iterator

from models.record import Record


class Processing(ABC):
    """
    Base contract for record processing implementations.
    """

    @abstractmethod
    def process(
        self,
        records: Iterator[Record],
    ) -> Iterator[Record]:
        """
        Transform a stream of records.
        """
        raise NotImplementedError
