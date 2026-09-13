import re

from modules.base import Component


class RegexParser(Component):
    stage = "parser"
    type = "regex"

    def execute(self, data):
        pattern = self.config["pattern"]
        regex = re.compile(pattern)

        records = []

        for document in data:
            source = document.get("source")
            content = document.get("content", "")

            for match in regex.finditer(content):
                record = match.groupdict()
                record["source"] = source
                records.append(record)

        return records
