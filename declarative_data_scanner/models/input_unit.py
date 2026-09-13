from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class InputUnit:
    """
    Represents one discovered input independently of
    how it was discovered.
    """

    identity: str
    location: str
    size: int | None = None
    modified_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
