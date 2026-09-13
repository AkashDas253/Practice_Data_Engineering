from typing import Type

from stages.output.base import Output


class OutputRegistry:
    """
    Registry for output implementations.
    """

    _implementations: dict[str, Type[Output]] = {}

    @classmethod
    def register(
        cls,
        name: str,
        implementation: Type[Output],
    ) -> None:
        if name in cls._implementations:
            raise ValueError(
                f"Output implementation already registered: {name}"
            )

        cls._implementations[name] = implementation

    @classmethod
    def get(cls, name: str) -> Type[Output]:
        try:
            return cls._implementations[name]
        except KeyError:
            raise KeyError(
                f"Unknown output type: {name}"
            ) from None

    @classmethod
    def create(
        cls,
        name: str,
        **kwargs,
    ) -> Output:
        implementation = cls.get(name)
        return implementation(**kwargs)

    @classmethod
    def registered_types(cls) -> list[str]:
        return sorted(cls._implementations)
