class ComponentValidator:

    def validate(self, stage, component_config):
        if not isinstance(component_config, dict):
            raise ValueError(
                f"{stage} component must be a mapping."
            )

        if "type" not in component_config:
            raise ValueError(
                f"{stage} component requires 'type'."
            )

        if "config" not in component_config:
            component_config["config"] = {}
