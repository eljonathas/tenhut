from __future__ import annotations

from abc import ABC
from typing import ClassVar

from tenhut.core import Phase

from ..painting import Rgb
from .scene import Scene
from .scene_canvas import SceneCanvas
from .scene_context import SceneContext


class OutdoorScene(Scene, ABC):
    """A scene under the open sky: it shows the shared clouds and birds, except at night."""

    CLOUD_COLOR: ClassVar[Rgb | None] = Rgb(250, 250, 252)

    def _draw_weather(self, canvas: SceneCanvas, context: SceneContext) -> None:
        if context.phase is Phase.IDLE:
            return
        horizon_y = context.viewport.horizon_y
        if self.CLOUD_COLOR is not None:
            self._ambience.clouds.draw(canvas, horizon_y, self.CLOUD_COLOR)
        self._ambience.birds.draw(canvas, horizon_y, self._ambience.elapsed)
