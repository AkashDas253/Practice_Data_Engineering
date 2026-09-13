from typing import Any

from config.schema import ApplicationConfig


class ConfigValidator:
    """Validate raw configuration against the application schema."""

    def validate(
        self,
        data: dict[str, Any],
    ) -> ApplicationConfig:
        return ApplicationConfig.model_validate(data)
