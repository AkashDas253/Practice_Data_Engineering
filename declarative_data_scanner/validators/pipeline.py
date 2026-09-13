class PipelineValidator:

    EXPECTED_ORDER = [
        "discovery",
        "reader",
        "parser",
        "processing",
        "output",
    ]

    def validate(self, pipeline):
        stages = [stage for stage, _ in pipeline]

        # Every stage must be a known stage.
        for stage in stages:
            if stage not in self.EXPECTED_ORDER:
                raise ValueError(
                    f"Unknown pipeline stage: {stage}"
                )

        # Stages must appear in the configured order,
        # but optional stages may be omitted.
        positions = [
            self.EXPECTED_ORDER.index(stage)
            for stage in stages
        ]

        if positions != sorted(positions):
            raise ValueError(
                f"Invalid pipeline order: {stages}"
            )

        # A pipeline must start with discovery and
        # end with output.
        if not stages or stages[0] != "discovery":
            raise ValueError(
                "Pipeline must start with discovery."
            )

        if stages[-1] != "output":
            raise ValueError(
                "Pipeline must end with output."
            )
