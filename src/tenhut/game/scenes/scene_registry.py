from __future__ import annotations

from tenhut.core import Clock, SystemClock, Theme

from ..global_random import GlobalRandom
from ..random_source import RandomSource
from .ambience import Ambience
from .field_scene import FieldScene
from .layer_cache import LayerCache
from .office_scene import OfficeScene
from .parade_scene import ParadeScene
from .scene import Scene
from .trench_scene import TrenchScene


class SceneRegistry:
    """Owns the four scenes and the ambience they share, and hands out the scene for a theme."""

    def __init__(self, clock: Clock | None = None, randomness: RandomSource | None = None) -> None:
        # Building the ambience draws the clouds and stars first: that fixes the order of the shared random stream.
        self._ambience = Ambience(randomness or GlobalRandom())
        cache = LayerCache()
        scenes: tuple[Scene, ...] = (
            OfficeScene(self._ambience, cache, clock or SystemClock()),
            FieldScene(self._ambience, cache),
            TrenchScene(self._ambience, cache),
            ParadeScene(self._ambience, cache),
        )
        self._scenes = {scene.theme: scene for scene in scenes}

    @property
    def ambience(self) -> Ambience:
        return self._ambience

    @property
    def fireworks(self) -> bool:
        return self._ambience.fireworks.launching

    @fireworks.setter
    def fireworks(self, launching: bool) -> None:
        self._ambience.fireworks.launching = launching

    def scene_for(self, theme: Theme) -> Scene:
        return self._scenes[theme]

    def update(self, dt: float) -> None:
        self._ambience.update(dt)

    def burst(self, center_x: float | None = None) -> None:
        self._ambience.burst(center_x)
