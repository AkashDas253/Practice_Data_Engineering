from typing import Dict, Tuple, Type, Any


class PluginRegistry:
    """Central lookup catalog for dynamically resolving readers and writers."""

    def __init__(self):
        self._registry: Dict[Tuple[str, str], Type[Any]] = {}

    def register(self, cls: Type[Any]) -> Type[Any]:
        """Registers a reader or writer component class into the registry."""
        if not hasattr(cls, "stage") or not hasattr(cls, "type"):
            raise ValueError(f"Class '{cls.__name__}' must define both 'stage' and 'type' class attributes.")

        key = (cls.stage.lower(), cls.type.lower())
        self._registry[key] = cls
        return cls

    def resolve(self, stage: str, plugin_type: str) -> Type[Any]:
        """Resolves a component class by stage ('reader'/'writer') and type name."""
        key = (stage.lower(), plugin_type.lower())
        if key not in self._registry:
            available = [f"{s}:{t}" for s, t in self._registry.keys()]
            raise ValueError(
                f"No component registered for stage='{stage}' and type='{plugin_type}'. "
                f"Available registered plugins: {available}"
            )
        return self._registry[key]