from __future__ import annotations

from dataclasses import dataclass

from tenhut.core import Phase

from .viewport import Viewport


@dataclass(frozen=True, slots=True)
class SceneContext:
    """What a scene needs to know to draw one frame: the session phase and the viewport."""

    phase: Phase
    viewport: Viewport

    def fitted_to(self, size: tuple[int, int]) -> SceneContext:
        return SceneContext(self.phase, self.viewport.fitted_to(size))
