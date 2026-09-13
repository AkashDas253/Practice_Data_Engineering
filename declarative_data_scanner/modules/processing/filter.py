from modules.base import Component


class FilterProcessor(Component):
    stage = "processing"
    type = "filter"

    def execute(self, data):
        field = self.config["field"]
        expected = self.config["equals"]

        return [
            record
            for record in data
            if record.get(field) == expected
        ]
