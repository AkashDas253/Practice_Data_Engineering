from abc import ABC, abstractmethod
from collections.abc import Iterator

from models.record import Record


class Output(ABC):
    """
    Base contract for output implementations.
    """

    @abstractmethod
    def write(
        self,
        records: Iterator[Record],
    ) -> int:
        """
        Persist records and return the number written.
        """
        raise NotImplementedError
