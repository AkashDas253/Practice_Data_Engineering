from collections.abc import Iterator

from models.input_unit import InputUnit
from stages.reader.base import Reader
from stages.reader.registry import ReaderRegistry


class TextReader(Reader):
    """
    Reads a text file line by line.
    """

    def read(
        self,
        input_unit: InputUnit,
    ) -> Iterator[str]:

        with open(
            input_unit.location,
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:
                yield line.rstrip("\n")


ReaderRegistry.register(
    "text",
    TextReader,
)
