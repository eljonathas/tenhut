from __future__ import annotations

from typing import ClassVar

import pygame

from tenhut.core import Phase, Theme

from ..geometry import Point
from ..painting import Rgb
from .climbing_wall import ClimbingWall
from .compass import Compass
from .desk import Desk
from .field_palette import FieldPalette
from .flag import Flag
from .flag_pole import FlagPole
from .map_sheet import MapSheet
from .mountain_range import MountainRange
from .mug import Mug
from .outdoor_scene import OutdoorScene
from .perspective_grid import PerspectiveGrid
from .radio import Radio
from .scene_anchors import SceneAnchors
from .scene_canvas import SceneCanvas
from .scene_context import SceneContext
from .side import Side
from .tent import Tent
from .tire import Tire
from .wood_fence import WoodFence


class FieldScene(OutdoorScene):
    """The training field: fences, tyres and an obstacle wall under a big sky; a map table up front."""

    theme: ClassVar[Theme] = Theme.FIELD

    TABLE_TOP: ClassVar[Rgb] = Rgb(92, 112, 70)
    TABLE_GRAIN: ClassVar[Rgb] = Rgb(70, 86, 52)
    TABLE_EDGE: ClassVar[Rgb] = Rgb(122, 142, 92)
    FAR_HILLS_SHADE: ClassVar[float] = 0.62
    FAR_HILLS_AMPLITUDE: ClassVar[int] = 12
    NEAR_HILLS_AMPLITUDE: ClassVar[int] = 5
    NEAR_HILLS_FREQUENCY: ClassVar[float] = 0.08
    NEAR_HILLS_OFFSET: ClassVar[int] = 2
    HORIZON_DROP: ClassVar[int] = 2
    ROAD_FAR_HALF_WIDTH: ClassVar[int] = 2
    ROAD_NEAR_HALF_WIDTH: ClassVar[int] = 46
    FENCE_POSTS: ClassVar[int] = 7
    FENCE_SPREAD: ClassVar[float] = 0.55
    TIRE_COUNT: ClassVar[int] = 5
    TIRES_SHOWN: ClassVar[int] = 4
    TIRE_SPREAD: ClassVar[float] = 0.28
    CLIMBING_WALL_X: ClassVar[float] = 0.16
    CLIMBING_WALL_WIDTH: ClassVar[int] = 12
    TENT_X: ClassVar[float] = 0.2
    TENT_MIN_X: ClassVar[int] = 12
    FLAG_X: ClassVar[float] = 0.3
    FLAG_POLE_HEIGHT: ClassVar[int] = 30
    FLAG_POLE_FOOT: ClassVar[int] = 4
    FLAG_SIZE: ClassVar[tuple[int, int]] = (14, 9)
    FLAG_OFFSET: ClassVar[Point] = Point(3, -29)
    FLAG_REACH: ClassVar[int] = 16
    MUG_DESK_OFFSET: ClassVar[int] = 5
    MAP_MIN_WIDTH: ClassVar[int] = 40
    MAP_SPAN_FACTOR: ClassVar[float] = 1.1
    COMPASS_OFFSET: ClassVar[Point] = Point(10, 10)
    RADIO_GAP: ClassVar[int] = 20
    RADIO_MIN_X: ClassVar[int] = 2
    MUG_GAP: ClassVar[int] = 6
    MUG_REACH: ClassVar[int] = 12

    def _paint_background(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None:
        viewport = context.viewport
        horizon_y, width = viewport.horizon_y, viewport.width
        sky = self._ambience.sky(self.theme, context.phase)
        palette = FieldPalette.NIGHT if context.phase is Phase.IDLE else FieldPalette.DAY
        sky.paint_gradient(canvas, pygame.Rect(0, 0, width, horizon_y))
        sky.paint_body(canvas, viewport)
        MountainRange(sky.horizon_color.shaded(self.FAR_HILLS_SHADE), self.FAR_HILLS_AMPLITUDE).paint(
            canvas, width, horizon_y
        )
        near_hills = MountainRange(
            palette.hills, self.NEAR_HILLS_AMPLITUDE, frequency=self.NEAR_HILLS_FREQUENCY, offset=self.NEAR_HILLS_OFFSET
        )
        near_hills.paint(canvas, width, horizon_y + self.HORIZON_DROP)
        grid = PerspectiveGrid(viewport, self.HORIZON_DROP)
        grid.paint_ground(canvas, palette.grass, palette.grass_alt)
        self._paint_road(canvas, grid, palette)
        self._paint_fences_and_tires(canvas, grid, palette.grass)
        self._paint_landmarks(canvas, context, anchors)

    def _paint_road(self, canvas: SceneCanvas, grid: PerspectiveGrid, palette: FieldPalette) -> None:
        x, y, height = grid.vanishing_x, grid.horizon_y, grid.horizon_y + grid.ground_height
        far, near = self.ROAD_FAR_HALF_WIDTH, self.ROAD_NEAR_HALF_WIDTH
        canvas.polygon(palette.dirt, [(x - far, y), (x + far, y), (x + near, height), (x - near, height)])

    def _paint_fences_and_tires(self, canvas: SceneCanvas, grid: PerspectiveGrid, grass: Rgb) -> None:
        for side in Side:
            WoodFence(grid.depth_points(side, grid.width * self.FENCE_SPREAD, self.FENCE_POSTS)).draw(canvas)
        for spot in grid.depth_points(Side.LEFT, grid.width * self.TIRE_SPREAD, self.TIRE_COUNT)[: self.TIRES_SHOWN]:
            Tire(spot, grass).draw(canvas)

    def _paint_landmarks(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None:
        viewport = context.viewport
        width, horizon_y, center = viewport.width, viewport.horizon_y, viewport.vanishing_x
        wall_x = center + int(width * self.CLIMBING_WALL_X)
        if wall_x + self.CLIMBING_WALL_WIDTH < width:
            ClimbingWall(wall_x, horizon_y).draw(canvas)
        tent_x = center - int(width * self.TENT_X)
        if tent_x > self.TENT_MIN_X:
            Tent(tent_x, horizon_y).draw(canvas)
        pole_x = center + int(width * self.FLAG_X)
        if pole_x + self.FLAG_REACH < width:
            FlagPole(pole_x, horizon_y - self.FLAG_POLE_HEIGHT, horizon_y + self.FLAG_POLE_FOOT).draw(canvas)
            flag_corner = (pole_x + self.FLAG_OFFSET.x, horizon_y + self.FLAG_OFFSET.y)
            anchors.flag = Flag(pygame.Rect(flag_corner, self.FLAG_SIZE))

    def _paint_foreground(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None:
        viewport = context.viewport
        Desk(self.TABLE_TOP, self.TABLE_GRAIN, self.TABLE_EDGE).draw(canvas, viewport)
        desk_y = viewport.desk_y
        map_width = max(self.MAP_MIN_WIDTH, int(viewport.span * self.MAP_SPAN_FACTOR))
        map_x = viewport.vanishing_x - map_width // 2
        MapSheet(pygame.Rect(map_x, desk_y, map_width, viewport.height - desk_y), viewport.vanishing_x).draw(canvas)
        Compass((map_x + int(self.COMPASS_OFFSET.x), desk_y + int(self.COMPASS_OFFSET.y))).draw(canvas)
        radio_x = map_x - self.RADIO_GAP
        if radio_x > self.RADIO_MIN_X:
            Radio(radio_x, desk_y).draw(canvas)
        mug_x = map_x + map_width + self.MUG_GAP
        if mug_x + self.MUG_REACH < viewport.width:
            anchors.mug = Mug(Point(mug_x, desk_y + self.MUG_DESK_OFFSET))

    def _draw_scenery(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None:
        if anchors.flag is not None:
            anchors.flag.draw(canvas, self._ambience.elapsed)
