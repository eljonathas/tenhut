from __future__ import annotations

import pygame

from .layout_frame import LayoutFrame
from .layout_mode import LayoutMode
from .layout_strategy import LayoutStrategy
from .size import Size


class WideLayout(LayoutStrategy):
    """A window lying down: the scene fills it and the chalkboard stands on the right."""

    MIN_WIDTH = 480
    MIN_HEIGHT = 290
    MIN_ASPECT = 1.15
    BOARD_SHARE = 0.46
    BOARD_MIN_WIDTH = 240
    BOARD_MAX_WIDTH = 330
    BOARD_MARGIN = 8
    BUTTONS_BELOW_BOARD = 26
    GENERAL_MIN_X = 80

    @property
    def mode(self) -> LayoutMode:
        return LayoutMode.WIDE

    def accepts(self, size: Size) -> bool:
        return (
            size.width >= self.MIN_WIDTH
            and size.height >= self.MIN_HEIGHT
            and size.width >= size.height * self.MIN_ASPECT
        )

    def frame(self, size: Size) -> LayoutFrame:
        width = max(self.BOARD_MIN_WIDTH, min(self.BOARD_MAX_WIDTH, int(size.width * self.BOARD_SHARE)))
        board = pygame.Rect(
            size.width - width - self.BOARD_MARGIN,
            self.BOARD_MARGIN,
            width,
            size.height - self.BUTTON_HEIGHT - self.BUTTONS_BELOW_BOARD,
        )
        buttons = pygame.Rect(board.x, board.bottom + self.BOARD_MARGIN, width, self.BUTTON_HEIGHT)
        scene = pygame.Rect(0, 0, size.width, size.height)
        return LayoutFrame(scene, board, buttons, max(self.GENERAL_MIN_X, board.x // 2))

    def balloon_area(self, frame: LayoutFrame, size: Size, board_shown: bool) -> pygame.Rect:
        return pygame.Rect(self.SIDE_MARGIN, self.TOP_MARGIN, frame.board.x - 2 * self.SIDE_MARGIN, size.height)

    def title_region(self, frame: LayoutFrame) -> pygame.Rect:
        return pygame.Rect(0, 0, frame.board.x, frame.scene.h)
