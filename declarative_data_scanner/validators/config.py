class ConfigValidator:

    REQUIRED_STAGES = [
        "discovery",
        "reader",
        "parser",
        "output",
    ]

    def validate(self, config):
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a mapping.")

        if "scan" not in config:
            raise ValueError("Missing 'scan' configuration.")

        scan = config["scan"]

        for stage in self.REQUIRED_STAGES:
            if stage not in scan:
                raise ValueError(
                    f"Missing required stage: {stage}"
                )

        if "processing" not in scan:
            scan["processing"] = []
