from modules.discovery.glob import GlobDiscovery
from modules.reader.text import TextReader
from modules.parser.regex import RegexParser
from modules.processing.filter import FilterProcessor
from modules.output.csv import CSVOutput

from validators.config import ConfigValidator
from validators.component import ComponentValidator
from validators.pipeline import PipelineValidator


class Registry:
    def __init__(self):
        self._components = {}
        self._validators = {}

    def register(self, component):
        key = (component.stage, component.type)
        self._components[key] = component

    def resolve(self, stage, component_type):
        key = (stage, component_type)

        try:
            return self._components[key]
        except KeyError:
            raise ValueError(
                f"Unknown component: stage={stage!r}, "
                f"type={component_type!r}"
            )

    def register_validator(self, name, validator):
        self._validators[name] = validator

    def resolve_validator(self, name):
        try:
            return self._validators[name]
        except KeyError:
            raise ValueError(f"Unknown validator: {name!r}")


registry = Registry()

registry.register(GlobDiscovery)
registry.register(TextReader)
registry.register(RegexParser)
registry.register(FilterProcessor)
registry.register(CSVOutput)

registry.register_validator("config", ConfigValidator)
registry.register_validator("component", ComponentValidator)
registry.register_validator("pipeline", PipelineValidator)
