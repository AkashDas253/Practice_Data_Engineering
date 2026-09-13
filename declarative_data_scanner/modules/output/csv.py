import csv
from pathlib import Path

from modules.base import Component


class CSVOutput(Component):
    stage = "output"
    type = "csv"

    def execute(self, data):
        path = Path(self.config["path"])

        # Create the parent directory when necessary.
        path.parent.mkdir(parents=True, exist_ok=True)

        if not data:
            return None

        fields = sorted({
            field
            for record in data
            for field in record.keys()
        })

        with path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=fields,
                extrasaction="ignore",
            )

            writer.writeheader()
            writer.writerows(data)

        return str(path)
