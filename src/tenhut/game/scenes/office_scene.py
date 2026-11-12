from __future__ import annotations

from typing import ClassVar

import pygame

from tenhut.core import Clock, Theme

from ..geometry import Point
from ..painting import Rgb
from .ambience import Ambience
from .clipboard import Clipboard
from .desk import Desk
from .desk_plaque import DeskPlaque
from .file_cabinet import FileCabinet
from .flag import Flag
from .flag_pole import FlagPole
from .lamp import Lamp
from .layer_cache import LayerCache
from .map_board import MapBoard
from .mug import Mug
from .note_pad import NotePad
from .office_room import OfficeRoom
from .scene import Scene
from .scene_anchors import SceneAnchors
from .scene_canvas import SceneCanvas
from .scene_context import SceneContext
from .wall_clock import WallClock
from .window import Window


class OfficeScene(Scene):
    """Headquarters: a room with a window, a map, a flag and a desk with the mission checklist."""

    theme: ClassVar[Theme] = Theme.OFFICE

    DESK_TOP: ClassVar[Rgb] = Rgb(150, 100, 58)
    DESK_GRAIN: ClassVar[Rgb] = Rgb(120, 78, 44)
    DESK_EDGE: ClassVar[Rgb] = Rgb(178, 126, 78)
    WINDOW_GAP: ClassVar[int] = 26
    WINDOW_MAX_WIDTH: ClassVar[int] = 46
    WINDOW_MIN_WIDTH: ClassVar[int] = 18
    WINDOW_MARGIN: ClassVar[int] = 6
    WINDOW_TOP_SHARE: ClassVar[float] = 0.14
    WINDOW_HEIGHT_SHARE: ClassVar[float] = 0.46
    WINDOW_MIN_HEIGHT: ClassVar[int] = 14
    CLOCK_RISE: ClassVar[int] = 9
    CLOCK_MIN_DROP: ClassVar[int] = 7
    MAP_MAX_WIDTH: ClassVar[int] = 52
    MAP_MIN_WIDTH: ClassVar[int] = 20
    MAP_TOP_SHARE: ClassVar[float] = 0.12
    MAP_HEIGHT_SHARE: ClassVar[float] = 0.44
    CABINET_CLEARANCE: ClassVar[int] = 22
    CABINET_GAP: ClassVar[int] = 30
    CABINET_INSET: ClassVar[int] = 18
    CABINET_HEIGHT_SHARE: ClassVar[float] = 0.5
    FLAG_MIN_WALL_X: ClassVar[int] = 14
    FLAG_SIZE: ClassVar[tuple[int, int]] = (18, 11)
    FLAG_OFFSET: ClassVar[Point] = Point(-8, 6)
    POLE_OFFSET_X: ClassVar[int] = -9
    POLE_TOP_OFFSET: ClassVar[int] = 4
    POLE_FOOT_OFFSET: ClassVar[int] = 6
    LAMP_MIN_CEILING: ClassVar[int] = 14
    LAMP_DEFAULT_DROP: ClassVar[int] = 12
    CLIPBOARD_MIN_WIDTH: ClassVar[int] = 30
    CLIPBOARD_MAX_WIDTH: ClassVar[int] = 64
    CLIPBOARD_SPAN_SHARE: ClassVar[float] = 0.8
    NOTE_PAD_GAP: ClassVar[int] = 22
    NOTE_PAD_MIN_X: ClassVar[int] = 4
    MUG_GAP: ClassVar[int] = 8
    MUG_REACH: ClassVar[int] = 12
    MUG_DESK_OFFSET: ClassVar[int] = 6
    CLIPBOARD_DESK_OFFSET: ClassVar[int] = 3
    CLIPBOARD_EXTRA_HEIGHT: ClassVar[int] = 2

    def __init__(self, ambience: Ambience, cache: LayerCache, clock: Clock) -> None:
        super().__init__(ambience, cache)
        self._clock = clock

    def _paint_background(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None:
        viewport = context.viewport
        room = OfficeRoom(viewport)
        room.paint(canvas)
        anchors.clock = self._hang_window(canvas, context, room)
        self._hang_map(canvas, viewport.vanishing_x, room)
        self._stand_cabinet(canvas, viewport.vanishing_x, room)
        self._raise_flag(canvas, room, anchors)
        wall = room.back_wall
        drop = wall.top - 2 if wall.top > self.LAMP_MIN_CEILING else self.LAMP_DEFAULT_DROP
        anchors.lamp = Lamp(viewport.vanishing_x, 0, drop)

    def _hang_window(self, canvas: SceneCanvas, context: SceneContext, room: OfficeRoom) -> WallClock | None:
        """Paint the window if the wall has room for it, and return the clock hung above it."""
        wall = room.back_wall
        right = context.viewport.vanishing_x - self.WINDOW_GAP
        width = min(self.WINDOW_MAX_WIDTH, right - wall.left - self.WINDOW_MARGIN)
        if width < self.WINDOW_MIN_WIDTH:
            return None
        top = wall.top + room.height_share(self.WINDOW_TOP_SHARE)
        height = max(self.WINDOW_MIN_HEIGHT, room.height_share(self.WINDOW_HEIGHT_SHARE))
        view = pygame.Rect(right - width, top, width, height)
        Window(view, self._ambience.sky(self.theme, context.phase)).draw(canvas)
        clock_y = max(wall.top + self.CLOCK_MIN_DROP, top - self.CLOCK_RISE)
        return WallClock((view.centerx, clock_y), self._clock)

    def _hang_map(self, canvas: SceneCanvas, vanishing_x: int, room: OfficeRoom) -> None:
        wall = room.back_wall
        left = vanishing_x + self.WINDOW_GAP
        width = min(self.MAP_MAX_WIDTH, wall.right - left - self.WINDOW_MARGIN)
        if width < self.MAP_MIN_WIDTH:
            return
        top = wall.top + room.height_share(self.MAP_TOP_SHARE)
        height = max(self.WINDOW_MIN_HEIGHT, room.height_share(self.MAP_HEIGHT_SHARE))
        MapBoard(pygame.Rect(left, top, width, height)).draw(canvas)

    def _stand_cabinet(self, canvas: SceneCanvas, vanishing_x: int, room: OfficeRoom) -> None:
        wall = room.back_wall
        if wall.right - self.CABINET_CLEARANCE > vanishing_x + self.CABINET_GAP:
            FileCabinet(
                wall.right - self.CABINET_INSET, wall.bottom, room.height_share(self.CABINET_HEIGHT_SHARE)
            ).draw(canvas)

    def _raise_flag(self, canvas: SceneCanvas, room: OfficeRoom, anchors: SceneAnchors) -> None:
        wall = room.back_wall
        if wall.left > self.FLAG_MIN_WALL_X:
            corner = Point(wall.left, wall.top)
            anchors.flag = Flag(
                pygame.Rect((corner.x + self.FLAG_OFFSET.x, corner.y + self.FLAG_OFFSET.y), self.FLAG_SIZE)
            )
            pole_top, pole_foot = wall.top + self.POLE_TOP_OFFSET, wall.bottom + self.POLE_FOOT_OFFSET
            FlagPole(wall.left + self.POLE_OFFSET_X, pole_top, pole_foot).draw(canvas)

    def _paint_foreground(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None:
        viewport = context.viewport
        Desk(self.DESK_TOP, self.DESK_GRAIN, self.DESK_EDGE).draw(canvas, viewport)
        desk_y, center = viewport.desk_y, viewport.vanishing_x
        clipboard_width = max(
            self.CLIPBOARD_MIN_WIDTH, min(self.CLIPBOARD_MAX_WIDTH, int(viewport.span * self.CLIPBOARD_SPAN_SHARE))
        )
        clipboard_top = desk_y + self.CLIPBOARD_DESK_OFFSET
        clipboard_height = viewport.height - desk_y + self.CLIPBOARD_EXTRA_HEIGHT
        anchors.clipboard = Clipboard(
            pygame.Rect(center - clipboard_width // 2, clipboard_top, clipboard_width, clipboard_height)
        )
        note_pad_x = center - clipboard_width // 2 - self.NOTE_PAD_GAP
        if note_pad_x > self.NOTE_PAD_MIN_X:
            NotePad(note_pad_x, desk_y).draw(canvas)
        mug_x = center + clipboard_width // 2 + self.MUG_GAP
        if mug_x + self.MUG_REACH < viewport.width:
            anchors.mug = Mug(Point(mug_x, desk_y + self.MUG_DESK_OFFSET))
        DeskPlaque(center, desk_y).draw(canvas)

    def _draw_weather(self, canvas: SceneCanvas, context: SceneContext) -> None:
        """Indoors there are no clouds or birds."""

    def _draw_scenery(self, canvas: SceneCanvas, context: SceneContext, anchors: SceneAnchors) -> None:
        elapsed = self._ambience.elapsed
        if anchors.lamp is not None:
            anchors.lamp.draw(canvas, elapsed)
        if anchors.clock is not None:
            anchors.clock.draw(canvas)
        if anchors.flag is not None:
            anchors.flag.draw(canvas, elapsed)
