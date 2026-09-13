from abc import ABC, abstractmethod
from typing import Any


class Component(ABC):
    stage: str
    type: str

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    @abstractmethod
    def execute(self, data: Any) -> Any:
        """Execute the component."""
        raise NotImplementedError
