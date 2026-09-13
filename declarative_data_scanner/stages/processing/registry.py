from typing import Type

from stages.processing.base import Processing


class ProcessingRegistry:
    """
    Registry for processing implementations.
    """

    _implementations: dict[str, Type[Processing]] = {}

    @classmethod
    def register(
        cls,
        name: str,
        implementation: Type[Processing],
    ) -> None:
        if name in cls._implementations:
            raise ValueError(
                f"Processing implementation already registered: {name}"
            )

        cls._implementations[name] = implementation

    @classmethod
    def get(cls, name: str) -> Type[Processing]:
        try:
            return cls._implementations[name]
        except KeyError:
            raise KeyError(
                f"Unknown processing type: {name}"
            ) from None

    @classmethod
    def create(
        cls,
        name: str,
        **kwargs,
    ) -> Processing:
        implementation = cls.get(name)
        return implementation(**kwargs)

    @classmethod
    def registered_types(cls) -> list[str]:
        return sorted(cls._implementations)
