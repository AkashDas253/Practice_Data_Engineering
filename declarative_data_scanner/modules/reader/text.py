from pathlib import Path

from modules.base import Component


class TextReader(Component):
    stage = "reader"
    type = "text"

    def execute(self, data):
        encoding = self.config.get("encoding", "utf-8")

        records = []

        for filename in data:
            content = Path(filename).read_text(encoding=encoding)

            records.append({
                "source": filename,
                "content": content,
            })

        return records
