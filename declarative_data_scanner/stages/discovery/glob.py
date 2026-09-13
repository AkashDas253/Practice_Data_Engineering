from collections.abc import Iterator
from pathlib import Path

from models.input_unit import InputUnit
from stages.discovery.base import Discovery
from stages.discovery.registry import DiscoveryRegistry


class GlobDiscovery(Discovery):
    """
    Discovers files using a glob pattern.
    """

    def discover(self, source):
        pattern = source["path"]

        for path in Path().glob(pattern):
            if path.is_file():
                stat = path.stat()

                yield InputUnit(
                    identity=str(path.resolve()),
                    location=str(path),
                    size=stat.st_size,
                )


DiscoveryRegistry.register(
    "glob",
    GlobDiscovery,
)
