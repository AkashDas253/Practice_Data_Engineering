from typing import Type

from stages.reader.base import Reader


class ReaderRegistry:
    """
    Registry for reader implementations.
    """

    _implementations: dict[str, Type[Reader]] = {}

    @classmethod
    def register(
        cls,
        name: str,
        implementation: Type[Reader],
    ) -> None:
        if name in cls._implementations:
            raise ValueError(
                f"Reader implementation already registered: {name}"
            )

        cls._implementations[name] = implementation

    @classmethod
    def get(cls, name: str) -> Type[Reader]:
        try:
            return cls._implementations[name]
        except KeyError:
            raise KeyError(
                f"Unknown reader type: {name}"
            ) from None

    @classmethod
    def create(
        cls,
        name: str,
        **kwargs,
    ) -> Reader:
        implementation = cls.get(name)
        return implementation(**kwargs)

    @classmethod
    def registered_types(cls) -> list[str]:
        return sorted(cls._implementations)
