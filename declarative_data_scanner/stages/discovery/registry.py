from typing import Type

from stages.discovery.base import Discovery


class DiscoveryRegistry:
    """
    Registry for discovery implementations.
    """

    _implementations: dict[str, Type[Discovery]] = {}

    @classmethod
    def register(
        cls,
        name: str,
        implementation: Type[Discovery],
    ) -> None:
        if name in cls._implementations:
            raise ValueError(
                f"Discovery implementation already registered: {name}"
            )

        cls._implementations[name] = implementation

    @classmethod
    def get(cls, name: str) -> Type[Discovery]:
        try:
            return cls._implementations[name]
        except KeyError:
            raise KeyError(
                f"Unknown discovery type: {name}"
            ) from None

    @classmethod
    def create(
        cls,
        name: str,
        **kwargs,
    ) -> Discovery:
        implementation = cls.get(name)
        return implementation(**kwargs)

    @classmethod
    def registered_types(cls) -> list[str]:
        return sorted(cls._implementations)
