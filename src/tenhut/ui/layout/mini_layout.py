from __future__ import annotations

from typing import ClassVar

import pygame

from .layout_frame import LayoutFrame
from .layout_mode import LayoutMode
from .layout_strategy import LayoutStrategy
from .size import Size


class MiniLayout(LayoutStrategy):
    """A small window: a compact widget; the chalkboard opens over the scene only when needed."""

    MARGIN = 6
    BUTTONS_FROM_BOTTOM = 8
    BOARD_BELOW_BUTTONS = 22
    GENERAL_SHARE = 0.3
    GENERAL_MIN_X = 60
    HUD_RESERVE = 140
    compact: ClassVar[bool] = True

    @property
    def mode(self) -> LayoutMode:
        return LayoutMode.MINI

    def accepts(self, size: Size) -> bool:
        return True

    def frame(self, size: Size) -> LayoutFrame:
        scene = pygame.Rect(0, 0, size.width, size.height)
        buttons = pygame.Rect(
            self.MARGIN,
            size.height - self.BUTTON_HEIGHT - self.BUTTONS_FROM_BOTTOM,
            size.width - 2 * self.MARGIN,
            self.BUTTON_HEIGHT,
        )
        board = pygame.Rect(
            self.MARGIN,
            self.MARGIN,
            size.width - 2 * self.MARGIN,
            size.height - self.BUTTON_HEIGHT - self.BOARD_BELOW_BUTTONS,
        )
        return LayoutFrame(scene, board, buttons, max(self.GENERAL_MIN_X, int(size.width * self.GENERAL_SHARE)))

    def balloon_area(self, frame: LayoutFrame, size: Size, board_shown: bool) -> pygame.Rect:
        reserve = 2 * self.SIDE_MARGIN if board_shown else self.HUD_RESERVE
        return pygame.Rect(self.SIDE_MARGIN, self.TOP_MARGIN, size.width - reserve, size.height)
