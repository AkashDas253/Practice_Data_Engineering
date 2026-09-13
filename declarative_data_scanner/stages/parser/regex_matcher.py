import re
from collections.abc import Iterator

from models.record import Record
from stages.parser.base import Parser
from stages.parser.registry import ParserRegistry


class RegexMatcher(Parser):
    """
    Parses text using a regular expression.

    Named regex groups become Record fields.
    """

    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)

    def parse(
        self,
        raw_data: Iterator[str],
    ) -> Iterator[Record]:

        for line in raw_data:
            match = self.pattern.match(line)

            if match is None:
                continue

            yield Record(
                fields=match.groupdict()
            )


ParserRegistry.register(
    "regex_matcher",
    RegexMatcher,
)
