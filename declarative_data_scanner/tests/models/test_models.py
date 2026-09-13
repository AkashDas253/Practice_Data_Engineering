from datetime import datetime
from uuid import uuid4

from models.input_unit import InputUnit
from models.record import Record
from models.result import RunResult
from models.run import Run


def test_input_unit():
    modified_at = datetime.now()

    input_unit = InputUnit(
        identity="file-1",
        location="./data/file.log",
        size=100,
        modified_at=modified_at,
        metadata={"source": "test"},
    )

    assert input_unit.identity == "file-1"
    assert input_unit.location == "./data/file.log"
    assert input_unit.size == 100
    assert input_unit.modified_at == modified_at
    assert input_unit.metadata["source"] == "test"


def test_record():
    record = Record(
        fields={
            "level": "ERROR",
        }
    )

    assert record.get("level") == "ERROR"

    record.set("message", "failure")

    assert record.get("message") == "failure"


def test_run():
    run_id = uuid4()

    run = Run(
        run_id=run_id,
        scan_id="application_logs",
        started_at=datetime.now(),
    )

    assert run.run_id == run_id
    assert run.scan_id == "application_logs"


def test_run_result_defaults():
    result = RunResult(status="SUCCESS")

    assert result.status == "SUCCESS"
    assert result.records_read == 0
    assert result.records_written == 0
    assert result.records_failed == 0
