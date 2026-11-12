from __future__ import annotations

from dataclasses import dataclass

import pygame

from tenhut.game.animations import SlamPlacement, StampPlacement, TitleCardPlacement
from tenhut.game.geometry import Point

from .layout_frame import LayoutFrame
from .layout_mode import LayoutMode
from .layout_strategy import LayoutStrategy
from .size import Size


@dataclass(frozen=True, slots=True)
class Layout:
    """Where everything goes for the current logical screen size.

    ``world_scale`` is the number of logical pixels per world pixel and ``general_scale`` the same for the
    general's sprite: he stands on the other side of the desk, so he is drawn bigger than the scenery.
    """

    size: Size
    strategy: LayoutStrategy
    frame: LayoutFrame
    world_scale: int
    world: Size
    vanishing_x: int
    horizon_y: int
    desk_top: int
    general_scale: int
    general_top: int

    HEAD_OFFSET = 4
    SHOULDER_OFFSET = (19, 48)
    GENERAL_HALF_WIDTH = 30
    GENERAL_WIDTH = 60

    @property
    def mode(self) -> LayoutMode:
        return self.strategy.mode

    @property
    def compact(self) -> bool:
        return self.strategy.compact

    @property
    def scene(self) -> pygame.Rect:
        return self.frame.scene

    @property
    def board(self) -> pygame.Rect:
        return self.frame.board

    @property
    def buttons(self) -> pygame.Rect:
        return self.frame.buttons

    @property
    def general_x(self) -> int:
        return self.frame.general_x

    @property
    def board_visible(self) -> bool:
        return not self.compact

    @property
    def head(self) -> Point:
        return Point(self.general_x, self.general_top + self.HEAD_OFFSET * self.general_scale)

    @property
    def shoulder(self) -> Point:
        back, down = self.SHOULDER_OFFSET
        return Point(self.general_x - back * self.general_scale, self.general_top + down * self.general_scale)

    @property
    def general_rect(self) -> pygame.Rect:
        scale = self.general_scale
        desk_edge = self.scene.y + self.desk_top * self.world_scale
        return pygame.Rect(
            self.general_x - self.GENERAL_HALF_WIDTH * scale,
            self.general_top,
            self.GENERAL_WIDTH * scale,
            desk_edge - self.general_top,
        )

    def balloon_area(self, board_shown: bool) -> pygame.Rect:
        return self.strategy.balloon_area(self.frame, self.size, board_shown)

    def slam_placement(self) -> SlamPlacement:
        return SlamPlacement(
            self.desk_top * self.world_scale, self.world_scale, self.general_scale, self.general_x - self.scene.x
        )

    def title_card_placement(self) -> TitleCardPlacement:
        return TitleCardPlacement(self.scene, self.strategy.title_region(self.frame))

    def stamp_placement(self, board_shown: bool) -> StampPlacement:
        center = self.board.center if board_shown else self.scene.center
        return StampPlacement(self.size.width, Point(*center))
