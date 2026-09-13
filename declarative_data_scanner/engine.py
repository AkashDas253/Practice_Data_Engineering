from registry import registry


class Engine:

    def __init__(self, config):
        self.config = config

    def validate(self):
        validator = registry.resolve_validator("config")
        validator().validate(self.config)

    def _create_component(self, stage, definition):
        validator = registry.resolve_validator("component")
        validator().validate(stage, definition)

        component_cls = registry.resolve(
            stage,
            definition["type"],
        )

        return component_cls(definition["config"])

    def build_pipeline(self):
        scan = self.config["scan"]

        pipeline = []

        for stage in ("discovery", "reader"):
            component = self._create_component(
                stage,
                scan[stage],
            )

            pipeline.append((stage, component))

        parsers = scan["parser"]

        if not isinstance(parsers, list):
            parsers = [parsers]

        for parser in parsers:
            component = self._create_component(
                "parser",
                parser,
            )

            pipeline.append(("parser", component))

        for processor in scan.get("processing", []):
            component = self._create_component(
                "processing",
                processor,
            )

            pipeline.append(("processing", component))

        output = self._create_component(
            "output",
            scan["output"],
        )

        pipeline.append(("output", output))

        return pipeline

    def run(self):
        self.validate()

        pipeline = self.build_pipeline()

        validator = registry.resolve_validator("pipeline")
        validator().validate(pipeline)

        data = None

        for stage, component in pipeline:
            data = component.execute(data)

        return data
