from __future__ import annotations

import pygame

from tenhut.ui.painting import UiCanvas, UiPalette

from .layout_frame import LayoutFrame
from .layout_mode import LayoutMode
from .layout_strategy import LayoutStrategy
from .size import Size


class TallLayout(LayoutStrategy):
    """A window standing up: the scene on top, the chalkboard and the buttons below it."""

    MIN_HEIGHT = 460
    MIN_WIDTH = 300
    SCENE_MIN_HEIGHT = 200
    SCENE_SHARE = 0.5
    BOARD_RESERVE = 290
    MARGIN = 8
    BUTTONS_BELOW_BOARD = 28
    GENERAL_SHARE = 0.42
    DOUBLING_HEIGHT = 250
    GROUND_EDGE = 2

    @property
    def mode(self) -> LayoutMode:
        return LayoutMode.TALL

    @property
    def doubling_height(self) -> int:
        return self.DOUBLING_HEIGHT

    def accepts(self, size: Size) -> bool:
        return size.height >= self.MIN_HEIGHT and size.width >= self.MIN_WIDTH

    def frame(self, size: Size) -> LayoutFrame:
        scene_height = max(
            self.SCENE_MIN_HEIGHT, min(int(size.height * self.SCENE_SHARE), size.height - self.BOARD_RESERVE)
        )
        scene = pygame.Rect(0, 0, size.width, scene_height)
        board = pygame.Rect(
            self.MARGIN,
            scene_height + self.MARGIN,
            size.width - 2 * self.MARGIN,
            size.height - scene_height - self.BUTTON_HEIGHT - self.BUTTONS_BELOW_BOARD,
        )
        buttons = pygame.Rect(self.MARGIN, board.bottom + self.MARGIN, size.width - 2 * self.MARGIN, self.BUTTON_HEIGHT)
        return LayoutFrame(scene, board, buttons, int(size.width * self.GENERAL_SHARE))

    def balloon_area(self, frame: LayoutFrame, size: Size, board_shown: bool) -> pygame.Rect:
        return pygame.Rect(self.SIDE_MARGIN, self.TOP_MARGIN, size.width - 2 * self.SIDE_MARGIN, frame.scene.h)

    def paint_ground(self, canvas: UiCanvas, frame: LayoutFrame, size: Size) -> None:
        top = frame.scene.bottom
        canvas.shapes.rect(UiPalette.GROUND, (0, top, size.width, size.height - top))
        canvas.shapes.rect(UiPalette.INK, (0, top, size.width, self.GROUND_EDGE))
