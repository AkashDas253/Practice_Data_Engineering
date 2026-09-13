from abc import ABC, abstractmethod
from collections.abc import Iterator

from models.input_unit import InputUnit


class Reader(ABC):
    """
    Base contract for input readers.
    """

    @abstractmethod
    def read(
        self,
        input_unit: InputUnit,
    ) -> Iterator[str]:
        """
        Read raw input incrementally.
        """
        raise NotImplementedError
