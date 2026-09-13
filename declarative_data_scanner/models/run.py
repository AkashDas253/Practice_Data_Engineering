from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Run:
    """
    Represents one execution of a configured scan.
    """

    run_id: UUID
    scan_id: str
    started_at: datetime
