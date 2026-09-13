from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any

from models.input_unit import InputUnit


class Discovery(ABC):
    """
    Base contract for input discovery implementations.
    """

    @abstractmethod
    def discover(
        self,
        source: dict[str, Any],
    ) -> Iterator[InputUnit]:
        """
        Discover input units from the configured source.
        """
        raise NotImplementedError
