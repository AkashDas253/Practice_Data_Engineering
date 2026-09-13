from dataclasses import dataclass, field
from typing import Any


@dataclass
class Record:
    """
    Common structured representation passed through
    parser, processing, and output stages.
    """

    fields: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get(
        self,
        field: str,
        default: Any = None,
    ) -> Any:
        return self.fields.get(field, default)

    def set(
        self,
        field: str,
        value: Any,
    ) -> None:
        self.fields[field] = value
