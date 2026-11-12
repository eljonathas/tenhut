from __future__ import annotations

from .scene_key import SceneKey
from .scene_layers import SceneLayers


class LayerCache:
    """Remembers the static layers of the last few views; a resize storm cannot grow it without bound."""

    MAX_ENTRIES = 6

    def __init__(self) -> None:
        self._layers: dict[SceneKey, SceneLayers] = {}

    def __len__(self) -> int:
        return len(self._layers)

    def get(self, key: SceneKey) -> SceneLayers | None:
        return self._layers.get(key)

    def put(self, key: SceneKey, layers: SceneLayers) -> None:
        if len(self._layers) > self.MAX_ENTRIES:
            self._layers.clear()
        self._layers[key] = layers
