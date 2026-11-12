from __future__ import annotations

from tenhut.game.scenes import SceneRegistry

from .celebration import Celebration


class SceneCelebration(Celebration):
    """Sets the fireworks off in the sky of the scenes."""

    def __init__(self, scenes: SceneRegistry) -> None:
        self._scenes = scenes

    def fireworks(self, center_x: float | None = None) -> None:
        self._scenes.burst(center_x)
