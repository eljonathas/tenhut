from __future__ import annotations

from dataclasses import dataclass

from tenhut.core import Phase, Theme

from .scene_context import SceneContext


@dataclass(frozen=True, slots=True)
class SceneKey:
    """Identifies one cached pair of static layers."""

    theme: Theme
    phase: Phase
    width: int
    height: int
    vanishing_x: int
    horizon_y: int

    @classmethod
    def of(cls, theme: Theme, context: SceneContext) -> SceneKey:
        viewport = context.viewport
        return cls(theme, context.phase, viewport.width, viewport.height, viewport.vanishing_x, viewport.horizon_y)
