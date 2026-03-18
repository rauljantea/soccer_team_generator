from domain.interfaces.interfaces import UniverseInterface
from domain.models.models import Universe


class UnknownUniverseError(Exception):
    pass


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[Universe, UniverseInterface] = {}

    def register(self, universe: Universe, adapter: UniverseInterface) -> None:
        self._adapters[universe] = adapter

    def get(self, universe: Universe) -> UniverseInterface:
        adapter = self._adapters.get(universe)
        if adapter is None:
            raise UnknownUniverseError(
                f"No adapter registered for universe '{universe.value}'. "
                f"Registered: {[u.value for u in self._adapters]}"
            )
        return adapter

    def available(self) -> list[Universe]:
        return list(self._adapters.keys())


registry = AdapterRegistry()
