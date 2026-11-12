from __future__ import annotations

from typing import ClassVar

import pygame

from tenhut.core import Phase, Theme

from ..geometry import Point
from ..painting import Rgb
from .barbed_wire_fence import BarbedWireFence
from .binoculars import Binoculars
from .crater_field import CraterField
from .dead_tree import DeadTree
from .helmet import Helmet
from .mountain_range import MountainRange
from .mug import Mug
from .outdoor_scene import OutdoorScene
from .perspective_grid import PerspectiveGrid
from .sandbag_wall import SandbagWall
from .scene_anchors import SceneAnchors
from .scene_canvas import SceneCanvas
from .scene_context import SceneContext
from .side import Side
from .trench_palette import TrenchPalette


class TrenchScene(OutdoorScene):
    """The front line: mud, craters, barbed wire and smoke beyond a sandbag parapet."""

    theme: ClassVar[Theme] = Theme.TRENCH
    CLOUD_COLOR: ClassVar[Rgb | None] = Rgb(150, 150, 160)

    HILLS_SHADE: ClassVar[float] = 0.5
    HILLS_AMPLITUDE: ClassVar[int] = 7
    HILLS_FREQUENCY: ClassVar[float] = 0.03
    HORIZON_DROP: ClassVar[int] = 1
    TREE_POSITIONS: ClassVar[tuple[float, ...]] = (0.08, 0.27, 0.71, 0.9)
    FENCE_POSTS: ClassVar[int] = 6
    FENCE_SPREAD: ClassVar[float] = 0.5
    HELMET_X: ClassVar[float] = 0.45
    BINOCULARS_X: ClassVar[float] = 0.7
    MUG_X: ClassVar[float] = 0.35
    MUG_RISE: ClassVar[int] = 9
    PARAPET_INSET: ClassVar[int] = 1
    MIN_X: ClassVar[int] = 4

    def _paint_background(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None:
        viewport = context.viewport
        horizon_y, width = viewport.horizon_y, viewport.width
        sky = self._ambience.sky(self.theme, context.phase)
        palette = TrenchPalette.NIGHT if context.phase is Phase.IDLE else TrenchPalette.DAY
        sky.paint_gradient(canvas, pygame.Rect(0, 0, width, horizon_y))
        sky.paint_body(canvas, viewport, dimmed=True)
        hills = MountainRange(
            sky.horizon_color.shaded(self.HILLS_SHADE), self.HILLS_AMPLITUDE, frequency=self.HILLS_FREQUENCY
        )
        hills.paint(canvas, width, horizon_y)
        grid = PerspectiveGrid(viewport, self.HORIZON_DROP)
        grid.paint_ground(canvas, palette.mud, palette.mud_alt)
        CraterField(PerspectiveGrid(viewport), palette.mud, width).draw(canvas)
        for share in self.TREE_POSITIONS:
            DeadTree(int(width * share), horizon_y).draw(canvas)
        for side in Side:
            BarbedWireFence(grid.depth_points(side, width * self.FENCE_SPREAD, self.FENCE_POSTS)).draw(canvas)
        anchors.smoke_source_y = horizon_y

    def _paint_foreground(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None:
        viewport = context.viewport
        SandbagWall().draw(canvas, viewport)
        span, center = viewport.span, viewport.vanishing_x
        parapet_y = viewport.desk_y - self.PARAPET_INSET
        helmet_x = center + int(span * self.HELMET_X)
        if helmet_x + Helmet.REACH < viewport.width:
            Helmet(helmet_x, parapet_y).draw(canvas)
        binoculars_x = center - int(span * self.BINOCULARS_X)
        if binoculars_x > self.MIN_X:
            Binoculars(binoculars_x, parapet_y).draw(canvas)
        mug_x = center - int(span * self.MUG_X)
        if mug_x > self.MIN_X:
            anchors.mug = Mug(Point(mug_x, parapet_y - self.MUG_RISE), Mug.TIN)

    def _draw_scenery(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None:
        horizon_y = anchors.smoke_source_y if anchors.smoke_source_y is not None else context.viewport.horizon_y
        smoke = self._ambience.smoke
        smoke.emit_if_due(self._ambience.frame(), horizon_y)
        smoke.draw(canvas)
