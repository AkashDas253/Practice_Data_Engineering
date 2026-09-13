from typing import Type

from stages.parser.base import Parser


class ParserRegistry:
    """
    Registry for parser implementations.
    """

    _implementations: dict[str, Type[Parser]] = {}

    @classmethod
    def register(
        cls,
        name: str,
        implementation: Type[Parser],
    ) -> None:
        if name in cls._implementations:
            raise ValueError(
                f"Parser implementation already registered: {name}"
            )

        cls._implementations[name] = implementation

    @classmethod
    def get(cls, name: str) -> Type[Parser]:
        try:
            return cls._implementations[name]
        except KeyError:
            raise KeyError(
                f"Unknown parser type: {name}"
            ) from None

    @classmethod
    def create(
        cls,
        name: str,
        **kwargs,
    ) -> Parser:
        implementation = cls.get(name)
        return implementation(**kwargs)

    @classmethod
    def registered_types(cls) -> list[str]:
        return sorted(cls._implementations)
