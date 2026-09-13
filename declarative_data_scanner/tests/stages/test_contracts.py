from models.input_unit import InputUnit
from models.record import Record
from stages.discovery.base import Discovery
from stages.reader.base import Reader
from stages.parser.base import Parser
from stages.processing.base import Processing
from stages.output.base import Output


class FakeDiscovery(Discovery):

    def discover(self, source):
        yield InputUnit(
            identity="test-input",
            location="test.log",
        )


class FakeReader(Reader):

    def read(self, input_unit):
        yield "INFO hello"
        yield "ERROR something failed"


class FakeParser(Parser):

    def parse(self, raw_data):
        for line in raw_data:
            level, message = line.split(" ", 1)

            yield Record(
                fields={
                    "level": level,
                    "message": message,
                }
            )


class FakeProcessing(Processing):

    def process(self, records):
        for record in records:
            if record.get("level") == "ERROR":
                yield record


class FakeOutput(Output):

    def __init__(self):
        self.records = []

    def write(self, records):
        for record in records:
            self.records.append(record)

        return len(self.records)


def test_stage_contracts_can_be_composed():
    discovery = FakeDiscovery()
    reader = FakeReader()
    parser = FakeParser()
    processing = FakeProcessing()
    output = FakeOutput()

    inputs = discovery.discover({})

    input_unit = next(inputs)

    raw_data = reader.read(input_unit)
    records = parser.parse(raw_data)
    processed = processing.process(records)

    written = output.write(processed)

    assert written == 1

    assert output.records[0].get("level") == "ERROR"
    assert (
        output.records[0].get("message")
        == "something failed"
    )
