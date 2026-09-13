from dataclasses import dataclass


@dataclass
class RunResult:
    """
    Represents the result and metrics of a scan execution.
    """

    status: str

    inputs_discovered: int = 0
    inputs_processed: int = 0

    records_read: int = 0
    records_parsed: int = 0
    records_processed: int = 0
    records_written: int = 0
    records_failed: int = 0
