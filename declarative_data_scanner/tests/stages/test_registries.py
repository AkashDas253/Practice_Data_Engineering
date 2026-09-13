from models.record import Record

import stages.discovery
import stages.reader
import stages.parser
import stages.processing
import stages.output

from stages.discovery.registry import DiscoveryRegistry
from stages.reader.registry import ReaderRegistry
from stages.parser.registry import ParserRegistry
from stages.processing.registry import ProcessingRegistry
from stages.output.registry import OutputRegistry


def test_discovery_registry():
    implementation = DiscoveryRegistry.get("glob")

    assert implementation.__name__ == "GlobDiscovery"

    assert "glob" in DiscoveryRegistry.registered_types()


def test_reader_registry():
    implementation = ReaderRegistry.get("text")

    assert implementation.__name__ == "TextReader"

    assert "text" in ReaderRegistry.registered_types()


def test_parser_registry():
    implementation = ParserRegistry.get("regex_matcher")

    assert implementation.__name__ == "RegexMatcher"

    assert "regex_matcher" in ParserRegistry.registered_types()


def test_processing_registry():
    implementation = ProcessingRegistry.get("filter")

    assert implementation.__name__ == "Filter"

    assert "filter" in ProcessingRegistry.registered_types()


def test_output_registry():
    implementation = OutputRegistry.get("duckdb")

    assert implementation.__name__ == "DuckDBOutput"

    assert "duckdb" in OutputRegistry.registered_types()


def test_unknown_type_fails():
    try:
        ParserRegistry.get("does_not_exist")
    except KeyError as exc:
        assert "Unknown parser type" in str(exc)
    else:
        raise AssertionError("Expected KeyError")


def test_registry_creates_implementation():
    processor = ProcessingRegistry.create(
        "filter",
        field="level",
        equals="ERROR",
    )

    records = iter(
        [
            Record(
                fields={
                    "level": "INFO",
                }
            ),
            Record(
                fields={
                    "level": "ERROR",
                }
            ),
        ]
    )

    result = list(processor.process(records))

    assert len(result) == 1
    assert result[0].get("level") == "ERROR"
