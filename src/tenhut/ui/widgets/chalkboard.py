from __future__ import annotations

import pygame

from tenhut.ui.painting import UiCanvas, UiPalette


class Chalkboard:
    """The wooden frame and green surface the pages write on."""

    FRAME_WIDTH = 5
    OUTLINE_GROW = 4
    SHADE_GROW = 2
    NAIL_INSET = 4
    NAIL_SIZE = 2

    @classmethod
    def writing_area(cls, board: pygame.Rect) -> pygame.Rect:
        return board.inflate(-2 * cls.FRAME_WIDTH, -2 * cls.FRAME_WIDTH)

    def draw(self, canvas: UiCanvas, board: pygame.Rect) -> None:
        shapes = canvas.shapes
        shapes.rect(UiPalette.INK, board.inflate(self.OUTLINE_GROW, self.OUTLINE_GROW))
        shapes.rect(UiPalette.WOOD_DARK, board.inflate(self.SHADE_GROW, self.SHADE_GROW))
        shapes.rect(UiPalette.WOOD, board)
        shapes.line(UiPalette.WOOD_LIGHT, (board.x + 1, board.y + 1), (board.right - 2, board.y + 1))
        surface = self.writing_area(board)
        shapes.rect(UiPalette.BOARD_DARK, surface.inflate(self.SHADE_GROW, self.SHADE_GROW))
        shapes.rect(UiPalette.BOARD, surface)
        self._draw_nails(canvas, board)

    def _draw_nails(self, canvas: UiCanvas, board: pygame.Rect) -> None:
        inset = self.NAIL_INSET
        corners = (
            board.topleft,
            (board.right - inset, board.y),
            (board.x, board.bottom - inset),
            (board.right - inset, board.bottom - inset),
        )
        for x, y in corners:
            canvas.shapes.rect(UiPalette.NAIL, (x + 1, y + 1, self.NAIL_SIZE, self.NAIL_SIZE))
